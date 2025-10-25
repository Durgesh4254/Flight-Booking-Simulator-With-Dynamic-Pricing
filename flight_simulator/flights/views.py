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


def try_reserve_seats(flight_id: int, seats_to_reserve: int) -> bool:
    
    
    updated = Flight.objects.filter(id=flight_id, available_seats__gte=seats_to_reserve).update(
        available_seats=F('available_seats') - seats_to_reserve
    )
    return updated == 1

class BeginBookingView(View):
    
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

        
        reserved = False
        with transaction.atomic():
            reserved = try_reserve_seats(flight.id, seats)
            if not reserved:
                return JsonResponse({"success": False, "error": "Not enough seats available"}, status=409)

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

        
        dynamic_price = compute_dynamic_fare(Decimal(flight.base_price), flight.total_seats, flight.available_seats, flight.departure_time, float(getattr(flight, 'demand_factor', 1.0)))
        total_amount = dynamic_price * seats

        payment_result = simulate_payment(total_amount)
        if not payment_result.get('success'):
            with transaction.atomic():
                Flight.objects.filter(id=flight.id).update(available_seats=F('available_seats') + seats)
            return JsonResponse({"success": False, "error": "Payment failed", "detail": payment_result.get('error')}, status=402)

        with transaction.atomic():
            passenger = Passenger.objects.create(
                first_name=p.get('first_name',''),
                last_name=p.get('last_name',''),
                email=p.get('email'),
                phone=p.get('phone')
            )
            
            used = flight.total_seats - flight.available_seats
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
            booking.status = Booking.STATUS_CANCELLED
            booking.save()
            booking.flight.refresh_from_db()
            Flight.objects.filter(id=booking.flight.id).update(available_seats=F('available_seats') + seats)

        return JsonResponse({"success": True, "pnr": booking.pnr, "status": booking.status})

class BookingHistoryView(View):
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
class FlightSearchView(View):
    def get(self, request):
        origin = request.GET.get('origin')
        destination = request.GET.get('destination')
        departure_date = request.GET.get('departure_date')  
        return_date = request.GET.get('return_date')  
        passengers = int(request.GET.get('passengers', '1'))

        if not origin or not destination or not departure_date:
            return HttpResponseBadRequest("origin, destination, and departure_date are required")

        try:
            departure_dt = timezone.datetime.fromisoformat(departure_date)
            departure_dt = timezone.make_aware(departure_dt)
        except ValueError:
            return HttpResponseBadRequest("Invalid departure_date format. Use ISO format YYYY-MM-DDTHH:MM:SS")

        flights = Flight.objects.filter(
            origin__iexact=origin,
            destination__iexact=destination,
            departure_time__date=departure_dt.date(),
            available_seats__gte=passengers
        )

        results = []
        for flight in flights:
            dynamic_price = compute_dynamic_fare(Decimal(flight.base_price), flight.total_seats, flight.available_seats, flight.departure_time, float(getattr(flight, 'demand_factor', 1.0)))
            results.append({
                "flight_id": str(flight.id),
                "origin": flight.origin,
                "destination": flight.destination,
                "departure_time": flight.departure_time.isoformat(),
                "arrival_time": flight.arrival_time.isoformat(),
                "available_seats": flight.available_seats,
                "dynamic_price_per_seat": str(dynamic_price)
            })

        return JsonResponse(results, safe=False)
