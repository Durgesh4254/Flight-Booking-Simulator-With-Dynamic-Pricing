# flights/views.py (append)
import json
from decimal import Decimal
from django.db import transaction
from django.db.models import F
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseNotAllowed
from django.views import View
from django.utils import timezone

from .models import Flight, Booking, Passenger
from .utils import generate_pnr, simulate_payment
from .pricing import compute_dynamic_fare

# Helper: atomic seat reservation using conditional update
def try_reserve_seats(flight_id: int, seats_to_reserve: int) -> bool:
    """
    Atomically decrement available_seats by seats_to_reserve only if enough seats.
    Returns True if reserved, False otherwise.
    """
    # Use a single update with filter to ensure atomicity
    updated = Flight.objects.filter(id=flight_id, available_seats__gte=seats_to_reserve).update(
        available_seats=F('available_seats') - seats_to_reserve
    )
    return updated == 1

class BeginBookingView(View):
    """
    Step 1: Client picks flight and number of seats.
    POST /flights/book/begin/
    Body JSON: {"flight_id": "<uuid>", "seats": 1}
    Response: temporary hold (in this simple approach we do immediate atomic decrement as hold).
    """
    def post(self, request):
        try:
            payload = json.loads(request.body)
            flight_id = payload.get('flight_id')
            seats = int(payload.get('seats', 1))
        except Exception:
            return HttpResponseBadRequest("Invalid JSON or parameters")

        if seats <= 0:
            return HttpResponseBadRequest("seats must be >= 1")

        try:
            flight = Flight.objects.get(id=flight_id)
        except Flight.DoesNotExist:
            return HttpResponseBadRequest("Flight not found")

        # Attempt to reserve seats atomically
        reserved = False
        with transaction.atomic():
            reserved = try_reserve_seats(flight.id, seats)
            # If reserved False -> not enough seats, no change done.
            if not reserved:
                return JsonResponse({"success": False, "error": "Not enough seats available"}, status=409)

        # Return tentative booking token (we'll require full data next)
        # For simplicity we return flight info and dynamic_price
        dynamic_price = compute_dynamic_fare(Decimal(flight.base_price), flight.total_seats, flight.available_seats, flight.departure_time, float(getattr(flight, 'demand_factor', 1.0)))
        return JsonResponse({
            "success": True,
            "message": "Seats reserved temporarily (atomic decrement)",
            "flight_id": str(flight.id),
            "seats_reserved": seats,
            "dynamic_price_per_seat": str(dynamic_price),
            "total_price": str(dynamic_price * seats)
        })

class ConfirmBookingView(View):
    """
    Step 2: submit passenger info and run payment.
    POST /flights/book/confirm/
    Body JSON:
    {
      "flight_id": "<uuid>",
      "seats": 1,
      "passenger": {"first_name":"A","last_name":"B","email":"x@y.com","phone":"..."},
      "payment": {"method": "card", "details": {...}}  # optional - ignored by simulator
    }
    """
    def post(self, request):
        try:
            payload = json.loads(request.body)
            flight_id = payload.get('flight_id')
            seats = int(payload.get('seats', 1))
            p = payload.get('passenger') or {}
        except Exception:
            return HttpResponseBadRequest("Invalid JSON or parameters")

        if seats <= 0:
            return HttpResponseBadRequest("seats must be >=1")

        try:
            flight = Flight.objects.get(id=flight_id)
        except Flight.DoesNotExist:
            return HttpResponseBadRequest("Flight not found")

        # Price calculation — must recalc at confirmation moment (price may change)
        dynamic_price = compute_dynamic_fare(Decimal(flight.base_price), flight.total_seats, flight.available_seats, flight.departure_time, float(getattr(flight, 'demand_factor', 1.0)))
        total_amount = dynamic_price * seats

        # Simulate payment
        payment_result = simulate_payment(total_amount)
        if not payment_result.get('success'):
            # Payment failed -> revert seat reservation (add seats back) — do it atomically
            with transaction.atomic():
                Flight.objects.filter(id=flight.id).update(available_seats=F('available_seats') + seats)
            return JsonResponse({"success": False, "error": "Payment failed", "detail": payment_result.get('error')}, status=402)

        # Payment success -> create passenger and booking record
        with transaction.atomic():
            passenger = Passenger.objects.create(
                first_name=p.get('first_name',''),
                last_name=p.get('last_name',''),
                email=p.get('email'),
                phone=p.get('phone')
            )
            # allocate simple seat_number(s) — sequential allocation: used_seat_index = total_seats - available_seats + 1
            # Note: available_seats already decremented in BeginBooking, so current available_seats reflects hold.
            used = flight.total_seats - flight.available_seats
            # For multiple seats we assign seat numbers like "12A" -> for simplicity assign numeric seat indexes
            seat_numbers = []
            for i in range(1, seats+1):
                seat_num = f"{used + i}"
                seat_numbers.append(seat_num)

            pnr = generate_pnr(prefix='PN')
            booking = Booking.objects.create(
                pnr=pnr,
                flight=flight,
                passenger=passenger,
                seat_number=",".join(seat_numbers),
                booked_seats=seats,
                price_paid=total_amount,
                status=Booking.STATUS_CONFIRMED
            )

        return JsonResponse({
            "success": True,
            "pnr": booking.pnr,
            "booking_id": booking.id,
            "flight_id": str(flight.id),
            "seat_number": booking.seat_number,
            "price_paid": str(booking.price_paid),
            "transaction_id": payment_result.get('transaction_id')
        }, status=201)

class CancelBookingView(View):
    """
    Cancel a confirmed booking and refund (simulated).
    POST /flights/book/cancel/
    Body JSON: {"pnr":"PNXXXX"}
    """
    def post(self, request):
        try:
            payload = json.loads(request.body)
            pnr = payload.get('pnr')
        except Exception:
            return HttpResponseBadRequest("Invalid JSON")

        if not pnr:
            return HttpResponseBadRequest("pnr required")

        try:
            booking = Booking.objects.select_related('flight').get(pnr=pnr)
        except Booking.DoesNotExist:
            return JsonResponse({"success": False, "error": "Booking not found"}, status=404)

        if booking.status != Booking.STATUS_CONFIRMED:
            return JsonResponse({"success": False, "error": f"Booking not cancellable (status {booking.status})"}, status=409)

        seats = booking.booked_seats
        with transaction.atomic():
            # mark booking cancelled
            booking.status = Booking.STATUS_CANCELLED
            booking.save()
            # add seats back atomically
            booking.flight.refresh_from_db()
            Flight.objects.filter(id=booking.flight.id).update(available_seats=F('available_seats') + seats)

        return JsonResponse({"success": True, "pnr": booking.pnr, "status": booking.status})

class BookingHistoryView(View):
    """
    GET /flights/book/history/?email=...  OR /flights/book/history/?pnr=...
    Returns list of bookings for passenger email or exact PNR.
    """
    def get(self, request):
        pnr = request.GET.get('pnr')
        email = request.GET.get('email')

        if pnr:
            qs = Booking.objects.filter(pnr=pnr).select_related('passenger','flight')
        elif email:
            qs = Booking.objects.filter(passenger__email__iexact=email).select_related('passenger','flight')
        else:
            return HttpResponseBadRequest("Provide either pnr or email")

        results = []
        for b in qs.order_by('-created_at'):
            results.append({
                "pnr": b.pnr,
                "flight_id": str(b.flight.id),
                "route": f"{b.flight.origin}->{b.flight.destination}",
                "departure": b.flight.departure_time.isoformat(),
                "passenger": f"{b.passenger.first_name} {b.passenger.last_name}",
                "seat_number": b.seat_number,
                "price_paid": str(b.price_paid),
                "status": b.status,
                "created_at": b.created_at.isoformat()
            })
        return JsonResponse(results, safe=False)
