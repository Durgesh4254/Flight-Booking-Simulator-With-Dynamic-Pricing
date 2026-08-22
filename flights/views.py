import json
import random
import string
from datetime import datetime
from decimal import Decimal
from django.db import transaction
from django.db.models import F
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse, Http404
from django.views import View
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from .models import (
    Flight, Booking, Passenger, FareHistory, Seat, Coupon, Deal,
    BookingPassenger, Airport, Airline, Aircraft, Payment
)
from .utils import compute_dynamic_fare, simulate_payment, generate_pnr
from .pdf_generator import build_eticket_pdf


def generate_ticket_number():
    prefix = 'FE'
    digits = ''.join(random.choices(string.digits, k=12))
    return f"{prefix}{digits}"


def generate_payment_id():
    prefix = 'PAY'
    chars = string.ascii_uppercase + string.digits
    body = ''.join(random.choices(chars, k=14))
    return f"{prefix}{body}"

from .ai_service import ask_flyease_ai
from .price_predictor import predict_flight_price
from .flight_scorer import calculate_flight_scores
from .weather_service import get_destination_weather
from .travel_requirements import get_travel_requirements
from .flight_tracker import get_flight_radar_telemetry
from .recommendations import get_personalized_recommendations
from .email_service import (
    send_booking_confirmation_email,
    send_price_drop_email,
    send_cancellation_refund_email
)
from .system_monitor import perform_system_health_checks
from .models import (
    Flight, Booking, Passenger, FareHistory, Seat, Coupon, Deal,
    BookingPassenger, Airport, Airline, Aircraft, Payment, PriceAlert,
    TravelRequirement, ServiceHealthLog, AdminAlert
)

from .flight_generator import create_dynamic_schedule_flights

def resolve_airport(query_str):
    """
    Intelligently resolves an airport object from:
    1. Exact 3-letter IATA code (e.g. 'DEL', 'DXB', 'BOM')
    2. City name (e.g. 'Delhi', 'New Delhi', 'Mumbai', 'Dubai', 'London')
    3. Airport name (e.g. 'Indira Gandhi', 'Heathrow')
    4. Fuzzy / case-insensitive contains match
    """
    if not query_str:
        return None
    q = query_str.strip()
    
    # 1. Exact code match
    ap = Airport.objects.filter(code__iexact=q).first()
    if ap:
        return ap
    
    # 2. Exact city match
    ap = Airport.objects.filter(city__iexact=q).first()
    if ap:
        return ap

    # 3. Common city alias mapping
    CITY_ALIASES = {
        'DELHI': 'DEL', 'NEW DELHI': 'DEL',
        'MUMBAI': 'BOM', 'BOMBAY': 'BOM',
        'BENGALURU': 'BLR', 'BANGALORE': 'BLR',
        'CHENNAI': 'MAA', 'MADRAS': 'MAA',
        'KOLKATA': 'CCU', 'CALCUTTA': 'CCU',
        'HYDERABAD': 'HYD',
        'GOA': 'GOI',
        'DUBAI': 'DXB',
        'LONDON': 'LHR', 'HEATHROW': 'LHR',
        'SINGAPORE': 'SIN',
        'BANGKOK': 'BKK',
        'TOKYO': 'HND',
        'PARIS': 'CDG',
        'NEW YORK': 'JFK',
        'SYDNEY': 'SYD',
        'MALDIVES': 'MLE', 'MALE': 'MLE',
        'BALI': 'DPS',
        'SRINAGAR': 'SXR',
        'JAIPUR': 'JAI',
        'UDAIPUR': 'UDR',
        'VARANASI': 'VNS',
        'AHMEDABAD': 'AMD',
        'PUNE': 'PNQ',
        'KOCHI': 'COK', 'COCHIN': 'COK',
        'DOHA': 'DOH',
        'FRANKFURT': 'FRA',
        'TORONTO': 'YYZ',
        'SAN FRANCISCO': 'SFO',
        'LOS ANGELES': 'LAX',
    }
    alias_code = CITY_ALIASES.get(q.upper())
    if alias_code:
        ap = Airport.objects.filter(code=alias_code).first()
        if ap:
            return ap

    # 4. Partial substring in city or name
    ap = Airport.objects.filter(city__icontains=q).first()
    if ap:
        return ap
    ap = Airport.objects.filter(name__icontains=q).first()
    if ap:
        return ap

    return None

class FlightSearchView(View):
    def get(self, request):
        origin_input = request.GET.get('origin', '').strip()
        dest_input = request.GET.get('destination', '').strip()
        date_str = request.GET.get('departure_date', '').strip()
        
        # New filters
        cabin_class = request.GET.get('class', 'ECONOMY').upper()
        passengers = int(request.GET.get('passengers', 1))

        if not origin_input or not dest_input or not date_str:
            return JsonResponse({'error': 'Missing origin, destination, or departure_date'}, status=400)

        try:
            dep_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return JsonResponse({'error': 'Invalid date format. Use YYYY-MM-DD'}, status=400)

        # Resolve airport objects intelligently from code OR city name
        orig_airport = resolve_airport(origin_input)
        dest_airport = resolve_airport(dest_input)

        if not orig_airport or not dest_airport:
            return JsonResponse({
                'offers': [],
                'message': f"No flights available between '{origin_input}' and '{dest_input}'. Please check city/airport names."
            })

        origin_code = orig_airport.code
        dest_code = dest_airport.code

        if origin_code == dest_code:
            return JsonResponse({'error': 'Origin and destination cannot be the same airport'}, status=400)

        flights = Flight.objects.filter(
            origin=orig_airport,
            destination=dest_airport,
            departure_time__date=dep_date
        )

        # If no flights currently seeded for this date, dynamically generate realistic flight schedules
        if not flights.exists():
            generated_list = create_dynamic_schedule_flights(origin_code, dest_code, dep_date)
            # Fetch as QuerySet for consistent handling
            flights = Flight.objects.filter(
                origin=orig_airport,
                destination=dest_airport,
                departure_time__date=dep_date
            )

        results = []
        for flight in flights:
            if flight.available_seats < passengers:
                continue

            pricing = compute_dynamic_fare(flight, requested_class=cabin_class)
            prediction = predict_flight_price(flight, requested_class=cabin_class, current_pricing=pricing)
            
            results.append({
                'id': flight.id,
                'flight_number': flight.flight_number,
                'airline': {
                    'code': flight.airline.code if flight.airline else 'N/A',
                    'name': flight.airline.name if flight.airline else 'Unknown',
                    'logo': flight.airline.logo_url if flight.airline else ''
                },
                'aircraft': flight.aircraft.model_name if flight.aircraft else 'Unknown',
                'origin': flight.origin.code,
                'destination': flight.destination.code,
                'departure_time': flight.departure_time.isoformat(),
                'arrival_time': flight.arrival_time.isoformat(),
                'duration_hours': round((flight.arrival_time - flight.departure_time).total_seconds() / 3600, 1),
                'pricing': pricing,
                'price_prediction': prediction,
                'available_seats': flight.available_seats,
                'class': cabin_class
            })
            
            # Record fare history for analytics
            FareHistory.objects.create(
                flight=flight,
                fare=pricing['total'],
                seats_available=flight.available_seats
            )

        # Calculate best flight multi-attribute scoring
        results = calculate_flight_scores(results)

        # Sorting logic
        sort_by = request.GET.get('sort', 'cheapest')
        if sort_by == 'cheapest':
            results.sort(key=lambda x: x['pricing']['total'])
        elif sort_by == 'fastest':
            results.sort(key=lambda x: x['duration_hours'])
        elif sort_by == 'best_value':
            results.sort(key=lambda x: -x.get('recommendation_score', 0))

        return JsonResponse({'offers': results})



class FlightSeatMapView(View):
    def get(self, request, flight_id):
        try:
            flight = Flight.objects.get(id=flight_id)
        except Flight.DoesNotExist:
            return JsonResponse({'error': 'Flight not found'}, status=404)
        
        seats = Seat.objects.filter(flight=flight).values(
            'id', 'seat_number', 'seat_class', 'status', 'is_window', 'is_aisle', 'extra_legroom'
        )
        return JsonResponse({'flight_id': flight.id, 'seats': list(seats)})


def check_deal_eligibility(deal, passengers_count, cabin_class, itinerary_flights):
    now = timezone.now()
    if not deal.is_active:
        return False, "This deal is currently inactive."
    if deal.valid_until < now:
        return False, "This deal has expired."
    if deal.valid_from > now:
        return False, "This deal is not yet active."
    if passengers_count < deal.min_passengers:
        return False, f"This deal requires a minimum of {deal.min_passengers} passenger(s)."
    if passengers_count > deal.max_passengers:
        return False, f"This deal is valid for up to {deal.max_passengers} passenger(s)."
    if deal.required_class and cabin_class.upper() != deal.required_class.upper():
        return False, f"This deal is only applicable for {deal.required_class.title()} class bookings."
    
    # Check route criteria if specified
    if deal.origin_code or deal.destination_code or deal.is_international_only:
        for f in itinerary_flights:
            orig = f.origin.code.upper() if f.origin else ""
            dest = f.destination.code.upper() if f.destination else ""
            if deal.origin_code and deal.origin_code.upper() != orig:
                return False, f"This deal is only valid for departures from {deal.origin_code}."
            if deal.destination_code and deal.destination_code.upper() != dest:
                return False, f"This deal is only valid for flights to {deal.destination_code}."
            if deal.is_international_only:
                # international check
                if f.origin and f.destination and f.origin.country == 'India' and f.destination.country == 'India':
                    return False, "This deal is only applicable to international flights."

    return True, "Deal is applicable."


class ConfirmBookingView(View):
    def post(self, request):
        try:
            payload = json.loads(request.body)
            itinerary = payload.get('itinerary', [])
            
            # Backwards compatibility if frontend sends old format
            if not itinerary and payload.get('flight_id'):
                itinerary = [{
                    "flight_id": payload.get('flight_id'),
                    "class": payload.get('class', 'ECONOMY').upper(),
                    "extra_fees": payload.get('extra_fees', 0),
                    "seats_list": payload.get('seats_list', []) # optional
                }]

            passengers_data = payload.get('passengers', [])
            coupon_code = payload.get('coupon', None)
            deal_code = payload.get('deal_code', None) or payload.get('deal_id', None)
        except Exception:
            return JsonResponse({"success": False, "error": "Invalid JSON payload"}, status=400)

        seats_needed = len(passengers_data)
        if seats_needed <= 0:
            return JsonResponse({"success": False, "error": "At least one passenger is required"}, status=400)
            
        if not itinerary:
            return JsonResponse({"success": False, "error": "No flights in itinerary"}, status=400)

        # Optional services fee calculation (server-side authority)
        service_prices = {
            'baggage': Decimal('1200.00'),
            'priority': Decimal('500.00'),
            'meal': Decimal('350.00'),
            'insurance': Decimal('700.00'),
        }
        selected_services = payload.get('services', [])
        services_fee_per_pax = sum(service_prices.get(s, Decimal('0.00')) for s in selected_services)
        services_total = services_fee_per_pax * seats_needed

        # 1. Validate all flights and calculate total
        total_amount = services_total
        flights_to_book = []
        raw_flight_objs = []
        primary_cabin_class = 'ECONOMY'
        
        for leg in itinerary:
            try:
                flight = Flight.objects.get(id=leg.get('flight_id'))
                raw_flight_objs.append(flight)
            except Flight.DoesNotExist:
                return JsonResponse({"success": False, "error": f"Flight {leg.get('flight_id')} not found"}, status=404)
                
            if flight.available_seats < seats_needed:
                return JsonResponse({"success": False, "error": f"Not enough seats available on flight {flight.flight_number}"}, status=400)
                
            cabin_class = leg.get('class', 'ECONOMY').upper()
            primary_cabin_class = cabin_class
            extra_fees = Decimal(str(leg.get('extra_fees', 0)))
            pricing = compute_dynamic_fare(flight, requested_class=cabin_class)
            leg_total = (Decimal(str(pricing['total'])) * seats_needed) + extra_fees
            total_amount += leg_total
            
            flights_to_book.append({
                'flight': flight,
                'class': cabin_class,
                'seats_list': leg.get('seats_list', []),
                'price_paid': leg_total
            })

        original_gross_fare = total_amount

        # 2. Handle Deal or Coupon logic (Server-side validation)
        # Policy: Only one offer/deal or coupon per booking
        applied_deal = None
        applied_coupon = None
        deal_title_saved = None
        discount = Decimal('0.00')

        if deal_code:
            try:
                # Can lookup by code or id
                if str(deal_code).isdigit():
                    deal_obj = Deal.objects.get(id=int(deal_code))
                else:
                    deal_obj = Deal.objects.get(code=str(deal_code).upper())
                
                is_eligible, reason = check_deal_eligibility(
                    deal_obj, seats_needed, primary_cabin_class, raw_flight_objs
                )
                if is_eligible:
                    applied_deal = deal_obj
                    deal_title_saved = f"{deal_obj.title} ({deal_obj.discount_percent}% OFF)"
                    discount = (original_gross_fare * Decimal(str(deal_obj.discount_percent / 100))).quantize(Decimal('0.01'))
                    total_amount = max(Decimal('0.00'), original_gross_fare - discount)
                else:
                    return JsonResponse({"success": False, "error": f"Deal not applicable: {reason}"}, status=400)
            except Deal.DoesNotExist:
                return JsonResponse({"success": False, "error": "Invalid or expired deal code."}, status=404)

        elif coupon_code:
            try:
                coupon_obj = Coupon.objects.get(code=coupon_code.upper(), is_active=True, valid_until__gte=timezone.now())
                applied_coupon = coupon_obj
                deal_title_saved = f"Promo Code {coupon_obj.code}"
                if coupon_obj.discount_percent > 0:
                    discount = (original_gross_fare * Decimal(str(coupon_obj.discount_percent / 100))).quantize(Decimal('0.01'))
                elif coupon_obj.discount_amount > 0:
                    discount = coupon_obj.discount_amount
                total_amount = max(Decimal('0.00'), original_gross_fare - discount)
            except Coupon.DoesNotExist:
                pass 

        # 3. Extract & validate Payment details from payload
        payment_details = payload.get('payment_details', {}) or {}
        payment_method = str(payment_details.get('method', 'CARD')).upper()
        valid_methods = {m[0] for m in Payment.METHOD_CHOICES}
        if payment_method not in valid_methods:
            payment_method = 'CARD'
        card_last4 = payment_details.get('card_last4')
        upi_id = payment_details.get('upi_id')
        bank_name = payment_details.get('bank_name')
        wallet_provider = payment_details.get('wallet_provider')

        # 4. Simulate Payment Gateway (deterministic chance of failure)
        payment_result = simulate_payment(total_amount)
        payment_status = 'SUCCESS' if payment_result.get('success') else 'FAILED'
        transaction_id = payment_result.get('transaction_id')

        # 5. Create Bookings and Passengers
        generated_pnrs = []
        generated_ticket_numbers = []
        payment_records = []
        user = request.user if request.user.is_authenticated else None

        try:
            with transaction.atomic():
                # Lock the flights
                flight_ids = [f['flight'].id for f in flights_to_book]
                locked_flights = Flight.objects.select_for_update().filter(id__in=flight_ids)

                # Check availability again after locking
                for lf in locked_flights:
                    if lf.available_seats < seats_needed:
                        raise ValueError(f"Seat availability changed for flight {lf.flight_number}. Please try again.")

                # If payment failed, we still create a Payment record with FAILED status
                # but do NOT confirm the booking.
                num_legs = len(flights_to_book)
                leg_discount = (discount / num_legs).quantize(Decimal('0.01')) if num_legs else Decimal('0.00')

                for leg_data in flights_to_book:
                    flight = Flight.objects.get(id=leg_data['flight'].id)
                    pnr = generate_pnr()
                    generated_pnrs.append(pnr)

                    booking_status = 'CONFIRMED' if payment_status == 'SUCCESS' else 'FAILED'
                    ticket_num = generate_ticket_number() if payment_status == 'SUCCESS' else None
                    leg_paid = max(Decimal('0.00'), leg_data['price_paid'] - leg_discount)

                    # Insurance calculation
                    has_ins = 'insurance' in selected_services or payload.get('has_insurance', False)
                    ins_fee = Decimal('499.00') * seats_needed if has_ins else Decimal('0.00')

                    booking = Booking.objects.create(
                        pnr=pnr,
                        ticket_number=ticket_num,
                        user=user,
                        flight=flight,
                        coupon=applied_coupon,
                        deal=applied_deal,
                        deal_title=deal_title_saved,
                        discount_amount=leg_discount,
                        original_fare=leg_data['price_paid'],
                        booked_seats=seats_needed,
                        price_paid=leg_paid if payment_status == 'SUCCESS' else None,
                        status=booking_status,
                        has_insurance=has_ins,
                        insurance_fee=ins_fee,
                        terminal=f"T{(flight.id % 3) + 1}",
                        gate=f"{['A','B','C','D'][flight.id % 4]}{(flight.id % 20) + 1}"
                    )
                    if ticket_num:
                        generated_ticket_numbers.append(ticket_num)

                    seat_list = []
                    # Create passengers for this booking
                    for idx, pd in enumerate(passengers_data):
                        dob_val = pd.get('dob') if pd.get('dob') else None
                        passenger, _ = Passenger.objects.get_or_create(
                            first_name=pd.get('first_name', ''),
                            last_name=pd.get('last_name', ''),
                            email=pd.get('email', '') or None,
                            defaults={
                                'phone': pd.get('phone', ''),
                                'dob': dob_val,
                                'gender': pd.get('gender', ''),
                                'passport_id': pd.get('passport_id', ''),
                                'nationality': pd.get('nationality', '')
                            }
                        )
                        # Update passenger details if provided
                        updated_fields = False
                        if pd.get('phone') and passenger.phone != pd.get('phone'):
                            passenger.phone = pd.get('phone')
                            updated_fields = True
                        if dob_val and passenger.dob != dob_val:
                            passenger.dob = dob_val
                            updated_fields = True
                        if pd.get('gender') and passenger.gender != pd.get('gender'):
                            passenger.gender = pd.get('gender')
                            updated_fields = True
                        if pd.get('passport_id') and passenger.passport_id != pd.get('passport_id'):
                            passenger.passport_id = pd.get('passport_id')
                            updated_fields = True
                        if pd.get('nationality') and passenger.nationality != pd.get('nationality'):
                            passenger.nationality = pd.get('nationality')
                            updated_fields = True
                        if updated_fields:
                            passenger.save()

                        seat_num = None
                        if idx < len(leg_data['seats_list']):
                            seat_num = leg_data['seats_list'][idx]
                        
                        seat_obj = None
                        if seat_num:
                            try:
                                seat_obj = Seat.objects.get(flight=flight, seat_number=seat_num)
                                if seat_obj.status == 'AVAILABLE':
                                    seat_obj.status = 'OCCUPIED'
                                    seat_obj.save()
                                    seat_list.append(seat_obj.seat_number)
                                else:
                                    seat_obj = None
                            except Seat.DoesNotExist:
                                pass
                        
                        BookingPassenger.objects.create(
                            booking=booking,
                            passenger=passenger,
                            seat=seat_obj
                        )
                        
                    booking.seat_number = ",".join(seat_list) if seat_list else "UNASSIGNED"
                    booking.save()

                    # Create Payment record tied to this booking leg
                    pay_id = generate_payment_id()
                    payment_record = Payment.objects.create(
                        booking=booking,
                        payment_id=pay_id,
                        method=payment_method,
                        amount=leg_paid if payment_status == 'SUCCESS' else total_amount,
                        status=payment_status,
                        transaction_id=transaction_id,
                        card_last4=card_last4 if payment_method == 'CARD' else None,
                        upi_id=upi_id if payment_method == 'UPI' else None,
                        bank_name=bank_name if payment_method == 'NET_BANKING' else None,
                        wallet_provider=wallet_provider if payment_method == 'WALLET' else None,
                    )
                    payment_records.append({
                        'payment_id': pay_id,
                        'method': payment_method,
                        'status': payment_status,
                        'transaction_id': transaction_id,
                    })

                    flight.available_seats = F('available_seats') - seats_needed
                    flight.save()

                    # Trigger Booking Confirmation Email with PDF Attachment non-blockingly
                    if payment_status == 'SUCCESS':
                        try:
                            send_booking_confirmation_email(booking, passengers_data)
                        except Exception:
                            pass

            if payment_status != 'SUCCESS':
                return JsonResponse({
                    "success": False,
                    "error": "Payment failed",
                    "detail": payment_result.get('error', 'Payment gateway declined the transaction.'),
                    "payment_status": payment_status,
                    "payment_ids": [p['payment_id'] for p in payment_records],
                }, status=402)

            return JsonResponse({
                "success": True,
                "pnr": generated_pnrs[0],
                "pnrs": generated_pnrs,
                "ticket_numbers": generated_ticket_numbers,
                "message": "Booking Confirmed",
                "transaction_id": transaction_id,
                "payment_status": payment_status,
                "payments": payment_records,
                "deal_applied": deal_title_saved,
                "discount_amount": float(discount),
                "original_fare": float(original_gross_fare),
                "final_amount": float(total_amount),
                "has_insurance": 'insurance' in selected_services or payload.get('has_insurance', False),
            })

        except ValueError as ve:
            return JsonResponse({"success": False, "error": str(ve)}, status=400)
        except Exception as e:
            return JsonResponse({"success": False, "error": "An error occurred during booking.", "detail": str(e)}, status=500)


class DealsListView(View):
    def get(self, request):
        category = request.GET.get('category')
        qs = Deal.objects.filter(is_active=True, valid_until__gte=timezone.now()).order_by('starting_price')
        if category and category.upper() != 'ALL':
            qs = qs.filter(category=category.upper())

        deals_data = []
        for d in qs:
            deals_data.append({
                'id': d.id,
                'title': d.title,
                'code': d.code,
                'category': d.category,
                'badge': d.badge,
                'description': d.description,
                'discount_percent': d.discount_percent,
                'origin_code': d.origin_code or '',
                'destination_code': d.destination_code or '',
                'starting_price': float(d.starting_price),
                'valid_until': d.valid_until.isoformat(),
                'min_passengers': d.min_passengers,
                'max_passengers': d.max_passengers,
                'required_class': d.required_class or '',
                'is_international_only': d.is_international_only,
                'terms': d.terms,
                'countdown_hours': d.countdown_hours,
            })
        return JsonResponse({'deals': deals_data})


class DealValidateView(View):
    def post(self, request):
        try:
            payload = json.loads(request.body)
            code = payload.get('code', '').upper()
            passengers = int(payload.get('passengers', 1))
            cabin_class = payload.get('class', 'ECONOMY').upper()
            amount = Decimal(str(payload.get('amount', 0)))
            flight_id = payload.get('flight_id')
        except Exception:
            return JsonResponse({"success": False, "error": "Invalid payload"}, status=400)

        try:
            deal = Deal.objects.get(code=code)
        except Deal.DoesNotExist:
            return JsonResponse({"success": False, "error": "Invalid deal code"}, status=404)

        flight_objs = []
        if flight_id:
            try:
                flight_objs.append(Flight.objects.get(id=flight_id))
            except Flight.DoesNotExist:
                pass

        is_eligible, reason = check_deal_eligibility(deal, passengers, cabin_class, flight_objs)
        if not is_eligible:
            return JsonResponse({"success": False, "error": reason}, status=400)

        discount = (amount * Decimal(str(deal.discount_percent / 100))).quantize(Decimal('0.01'))
        final_amount = max(Decimal('0.00'), amount - discount)

        return JsonResponse({
            "success": True,
            "deal_id": deal.id,
            "deal_title": deal.title,
            "code": deal.code,
            "discount_percent": deal.discount_percent,
            "discount_amount": float(discount),
            "original_amount": float(amount),
            "final_amount": float(final_amount),
            "message": f"✓ {deal.title} applied! {deal.discount_percent}% OFF (-₹{discount:,.2f})"
        })


class ApplyCouponView(View):
    def post(self, request):
        try:
            payload = json.loads(request.body)
            code = payload.get('coupon_code', '').upper()
            amount = Decimal(str(payload.get('amount', 0)))
        except Exception:
            return JsonResponse({"success": False, "error": "Invalid payload"}, status=400)
            
        try:
            coupon = Coupon.objects.get(code=code, is_active=True, valid_until__gte=timezone.now())
            discount = Decimal('0.00')
            if coupon.discount_percent > 0:
                discount = amount * Decimal(str(coupon.discount_percent / 100))
            elif coupon.discount_amount > 0:
                discount = coupon.discount_amount
                
            return JsonResponse({
                "success": True,
                "discount": float(discount),
                "final_amount": float(max(Decimal('0.00'), amount - discount))
            })
        except Coupon.DoesNotExist:
            return JsonResponse({"success": False, "error": "Invalid or expired coupon"}, status=404)


class BookingHistoryView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Authentication required"}, status=401)

        bookings = Booking.objects.filter(user=request.user).select_related(
            'flight', 'flight__origin', 'flight__destination', 'flight__airline'
        ).prefetch_related('booking_passengers', 'booking_passengers__seat').order_by('-created_at')
        
        results = []
        now = timezone.now()

        for b in bookings:
            dep = b.flight.departure_time
            arr = b.flight.arrival_time
            
            # Realistic flight progress / status simulation engine
            if b.status == 'CANCELLED':
                live_flight_status = 'CANCELLED'
                timeline_step = 0
            elif now < dep - timezone.timedelta(hours=24):
                live_flight_status = 'SCHEDULED'
                timeline_step = 1
            elif now < dep - timezone.timedelta(hours=2):
                live_flight_status = 'CHECKIN_OPEN'
                timeline_step = 2
            elif now < dep:
                live_flight_status = 'BOARDING'
                timeline_step = 3
            elif now < arr:
                live_flight_status = 'IN_FLIGHT'
                timeline_step = 4
            else:
                live_flight_status = 'ARRIVED'
                timeline_step = 5

            seats_list = [
                bp.seat.seat_number for bp in b.booking_passengers.all() if bp.seat
            ]

            results.append({
                'pnr': b.pnr,
                'flight': f"{b.flight.origin.code} to {b.flight.destination.code}",
                'origin_code': b.flight.origin.code,
                'dest_code': b.flight.destination.code,
                'origin_city': b.flight.origin.city,
                'dest_city': b.flight.destination.city,
                'airline_name': b.flight.airline.name if b.flight.airline else 'FlyEase',
                'airline_code': b.flight.airline.code if b.flight.airline else 'FE',
                'flight_number': b.flight.flight_number,
                'date': b.flight.departure_time.isoformat(),
                'arrival_date': b.flight.arrival_time.isoformat(),
                'status': b.status,
                'live_flight_status': live_flight_status,
                'timeline_step': timeline_step,
                'terminal': f"T{(b.id % 3) + 1}",
                'gate': f"{['A','B','C','D'][b.id % 4]}{(b.id % 20) + 1}",
                'price_paid': float(b.price_paid) if b.price_paid else 0,
                'original_fare': float(b.original_fare) if b.original_fare else (float(b.price_paid) if b.price_paid else 0),
                'discount_amount': float(b.discount_amount or 0),
                'cancellation_fee': float(b.cancellation_fee or 0),
                'refund_amount': float(b.refund_amount or 0),
                'refund_status': b.refund_status,
                'refund_method': b.refund_method,
                'cancelled_at': b.cancelled_at.isoformat() if b.cancelled_at else None,
                'deal_applied': b.deal_title or (f"Coupon: {b.coupon.code}" if b.coupon else None),
                'seats': b.booked_seats,
                'seats_list': seats_list
            })
        return JsonResponse({'bookings': results})


class BookingDetailView(View):
    def get(self, request, pnr):
        try:
            booking = Booking.objects.select_related(
                'flight', 'flight__origin', 'flight__destination',
                'flight__airline', 'flight__aircraft', 'coupon', 'user'
            ).prefetch_related(
                'booking_passengers', 'booking_passengers__passenger',
                'booking_passengers__seat', 'payments'
            ).get(pnr=pnr.upper())
        except Booking.DoesNotExist:
            return JsonResponse({"success": False, "error": "Booking not found"}, status=404)

        if booking.user and request.user.is_authenticated and booking.user_id != request.user.id:
            return JsonResponse({"success": False, "error": "Unauthorized"}, status=403)

        passengers = []
        for bp in booking.booking_passengers.all():
            pax = bp.passenger
            seat_obj = bp.seat
            passengers.append({
                'first_name': pax.first_name,
                'last_name': pax.last_name,
                'email': pax.email,
                'phone': pax.phone,
                'dob': pax.dob.isoformat() if pax.dob else None,
                'gender': pax.gender,
                'nationality': pax.nationality,
                'passport_id': pax.passport_id,
                'seat': seat_obj.seat_number if seat_obj else 'Unassigned',
                'seat_class': seat_obj.seat_class if seat_obj else 'ECONOMY',
                'is_window': seat_obj.is_window if seat_obj else False,
                'is_aisle': seat_obj.is_aisle if seat_obj else False,
                'extra_legroom': seat_obj.extra_legroom if seat_obj else False,
            })

        payments = []
        for pay in booking.payments.all():
            payments.append({
                'payment_id': pay.payment_id,
                'method': pay.method,
                'method_label': dict(Payment.METHOD_CHOICES).get(pay.method, pay.method),
                'amount': float(pay.amount),
                'status': pay.status,
                'transaction_id': pay.transaction_id,
                'card_last4': pay.card_last4,
                'upi_id': pay.upi_id,
                'bank_name': pay.bank_name,
                'wallet_provider': pay.wallet_provider,
                'created_at': pay.created_at.isoformat(),
            })

        flight = booking.flight
        now = timezone.now()
        dep = flight.departure_time
        arr = flight.arrival_time

        if booking.status == 'CANCELLED':
            live_flight_status = 'CANCELLED'
            timeline_step = 0
        elif now < dep - timezone.timedelta(hours=24):
            live_flight_status = 'SCHEDULED'
            timeline_step = 1
        elif now < dep - timezone.timedelta(hours=2):
            live_flight_status = 'CHECKIN_OPEN'
            timeline_step = 2
        elif now < dep:
            live_flight_status = 'BOARDING'
            timeline_step = 3
        elif now < arr:
            live_flight_status = 'IN_FLIGHT'
            timeline_step = 4
        else:
            live_flight_status = 'ARRIVED'
            timeline_step = 5

        data = {
            'success': True,
            'pnr': booking.pnr,
            'ticket_number': booking.ticket_number,
            'status': booking.status,
            'live_flight_status': live_flight_status,
            'timeline_step': timeline_step,
            'terminal': f"T{(booking.id % 3) + 1}",
            'gate': f"{['A','B','C','D'][booking.id % 4]}{(booking.id % 20) + 1}",
            'created_at': booking.created_at.isoformat(),
            'updated_at': booking.updated_at.isoformat(),
            'cancelled_at': booking.cancelled_at.isoformat() if booking.cancelled_at else None,
            'cancellation_fee': float(booking.cancellation_fee or 0),
            'refund_amount': float(booking.refund_amount or 0),
            'refund_status': booking.refund_status,
            'refund_method': booking.refund_method,
            'booked_seats': booking.booked_seats,
            'price_paid': float(booking.price_paid) if booking.price_paid else 0,
            'original_fare': float(booking.original_fare) if booking.original_fare else (float(booking.price_paid) if booking.price_paid else 0),
            'discount_amount': float(booking.discount_amount or 0),
            'coupon': {
                'code': booking.coupon.code,
                'discount_percent': booking.coupon.discount_percent,
                'discount_amount': float(booking.coupon.discount_amount),
            } if booking.coupon else None,
            'flight': {
                'id': flight.id,
                'flight_number': flight.flight_number,
                'airline': {
                    'code': flight.airline.code if flight.airline else 'FE',
                    'name': flight.airline.name if flight.airline else 'FlyEase',
                    'logo': flight.airline.logo_url if flight.airline else '',
                },
                'aircraft': flight.aircraft.model_name if flight.aircraft else 'Boeing 737-800',
                'origin': {
                    'code': flight.origin.code,
                    'city': flight.origin.city,
                    'name': flight.origin.name,
                    'country': flight.origin.country,
                },
                'destination': {
                    'code': flight.destination.code,
                    'city': flight.destination.city,
                    'name': flight.destination.name,
                    'country': flight.destination.country,
                },
                'departure_time': flight.departure_time.isoformat(),
                'arrival_time': flight.arrival_time.isoformat(),
                'duration_min': int((flight.arrival_time - flight.departure_time).total_seconds() // 60),
            },
            'passengers': passengers,
            'payments': payments,
        }
        return JsonResponse(data)


class CancelBookingView(View):
    def post(self, request, pnr):
        if not request.user.is_authenticated:
            # Allow cancellation with valid PNR in simulator environment
            pass

        try:
            booking = Booking.objects.select_related(
                'flight', 'flight__origin', 'flight__destination'
            ).prefetch_related('booking_passengers', 'booking_passengers__seat', 'payments').get(pnr=pnr.upper())
        except Booking.DoesNotExist:
            return JsonResponse({"success": False, "error": "Booking not found"}, status=404)

        if booking.status == 'CANCELLED':
            return JsonResponse({"success": False, "error": "This booking has already been cancelled."}, status=400)

        now = timezone.now()
        dep = booking.flight.departure_time
        total_paid = booking.price_paid or Decimal('0.00')

        # Cancellation rules based on departure time remaining
        hours_before = (dep - now).total_seconds() / 3600.0
        if hours_before > 48:
            # Flat nominal fee of 500 per passenger
            pax_count = max(1, booking.booked_seats)
            fee = Decimal(str(pax_count * 500.00))
        elif hours_before > 24:
            # 20% cancellation fee
            fee = (total_paid * Decimal('0.20')).quantize(Decimal('0.01'))
        elif hours_before > 0:
            # 40% cancellation fee
            fee = (total_paid * Decimal('0.40')).quantize(Decimal('0.01'))
        else:
            # Flight already departed
            fee = total_paid

        fee = min(fee, total_paid)
        refund_amount = max(Decimal('0.00'), total_paid - fee)

        # Release reserved seats back to available
        for bp in booking.booking_passengers.all():
            if bp.seat:
                bp.seat.status = 'AVAILABLE'
                bp.seat.save()

        # Update flight available seats count
        booking.flight.available_seats = min(
            booking.flight.total_seats,
            booking.flight.available_seats + booking.booked_seats
        )
        booking.flight.save()

        # Determine refund method from payment record
        last_payment = booking.payments.filter(status='SUCCESS').last()
        refund_method = "Original Payment Method"
        if last_payment:
            last_payment.status = 'REFUNDED'
            last_payment.save()
            refund_method = dict(Payment.METHOD_CHOICES).get(last_payment.method, last_payment.method)

        # Update booking in database (do NOT delete)
        booking.status = 'CANCELLED'
        booking.cancelled_at = now
        booking.cancellation_fee = fee
        booking.refund_amount = refund_amount
        booking.refund_status = 'COMPLETED' if refund_amount > 0 else 'NONE'
        booking.refund_method = refund_method
        booking.save()

        # Send cancellation & refund transactional email non-blockingly
        try:
            send_cancellation_refund_email(booking)
        except Exception:
            pass

        return JsonResponse({
            "success": True,
            "pnr": booking.pnr,
            "status": "CANCELLED",
            "price_paid": float(total_paid),
            "cancellation_fee": float(fee),
            "refund_amount": float(refund_amount),
            "refund_status": booking.refund_status,
            "refund_method": refund_method,
            "cancelled_at": now.isoformat(),
            "message": f"Booking {booking.pnr} successfully cancelled. Refund of ₹{refund_amount:,.2f} processed to {refund_method}."
        })


class ExploreDestinationsView(View):
    def get(self, request):
        category = request.GET.get('category', 'all').lower()
        max_budget = float(request.GET.get('max_budget', 100000))
        origin_code = request.GET.get('origin', 'BOM').upper()
        date_window = request.GET.get('date_window', 'this-weekend').lower()

        airports = list(Airport.objects.exclude(code=origin_code).order_by('city'))

        CATEGORY_MAP = {
            'beaches': ['GOI', 'MLE', 'DPS', 'COK', 'MAA', 'TRV', 'SYD', 'MEL', 'BKK', 'BCN'],
            'mountains': ['SXR', 'IXB', 'IXC', 'DED', 'GAU', 'ZRH'],
            'cities': ['DEL', 'BLR', 'DXB', 'LHR', 'SIN', 'HND', 'JFK', 'CDG', 'BKK', 'HYD', 'CCU', 'FRA', 'KUL', 'DOH', 'IST', 'ICN', 'YYZ', 'LAX', 'SFO', 'AMS', 'SVO', 'FCO', 'BCN', 'HKG', 'CPH', 'PNQ', 'AMD', 'LKO', 'PAT', 'BHO', 'IDR', 'NAG', 'RPR'],
            'heritage': ['JAI', 'UDR', 'VNS', 'ATQ', 'FCO', 'IST', 'ATH', 'BBI', 'IXM', 'DEL', 'LKO'],
            'nature': ['SXR', 'IXZ', 'COK', 'IXB', 'GAU', 'MLE', 'DPS', 'ZRH', 'TRV'],
            'adventure': ['DED', 'SXR', 'IXZ', 'SYD', 'MEL', 'DPS', 'GOI', 'ZRH', 'LAX', 'SFO']
        }

        DEST_SEASONS = {
            'GOI': 'Nov – Mar', 'DXB': 'Oct – Apr', 'SIN': 'All Year', 'SXR': 'Apr – Oct',
            'MLE': 'Dec – Apr', 'LHR': 'May – Sep', 'VNS': 'Oct – Mar', 'BKK': 'Nov – Feb',
            'JAI': 'Oct – Mar', 'DEL': 'Oct – Mar', 'BLR': 'Sep – Mar', 'HND': 'Mar – May & Sep – Nov',
            'JFK': 'May – Oct', 'CDG': 'Apr – Oct', 'SYD': 'Sep – Apr', 'DPS': 'Apr – Oct',
            'IXZ': 'Oct – May', 'UDR': 'Sep – Mar', 'DED': 'Mar – Jun & Sep – Nov', 'IXB': 'Mar – May',
            'FRA': 'May – Sep', 'KUL': 'All Year', 'DOH': 'Nov – Mar', 'IST': 'Apr – Oct',
            'ICN': 'Mar – May & Sep – Nov', 'YYZ': 'Jun – Sep', 'LAX': 'All Year', 'SFO': 'Sep – Nov',
            'AMS': 'Apr – Sep', 'MEL': 'Nov – Mar', 'SVO': 'Jun – Aug', 'FCO': 'Apr – Oct',
            'BCN': 'May – Oct', 'ZRH': 'Jun – Sep & Dec – Mar', 'HKG': 'Oct – Dec', 'CPH': 'May – Aug',
            'MAA': 'Nov – Feb', 'COK': 'Sep – Mar', 'TRV': 'Oct – Mar', 'HYD': 'Oct – Mar',
            'CCU': 'Oct – Mar', 'AMD': 'Nov – Feb', 'PNQ': 'Jul – Feb', 'GAU': 'Oct – Apr',
            'IXC': 'Oct – Mar', 'ATQ': 'Oct – Mar', 'LKO': 'Oct – Mar', 'PAT': 'Nov – Feb',
            'BBI': 'Oct – Mar', 'IXM': 'Oct – Mar', 'NAG': 'Nov – Feb', 'IDR': 'Oct – Mar',
            'BHO': 'Oct – Mar', 'RPR': 'Oct – Mar'
        }

        # Date window dynamic multiplier and tag
        WINDOW_CONFIG = {
            'this-weekend': {'mult': 1.15, 'tag': 'This Weekend Express', 'days_ahead': 2},
            'next-weekend': {'mult': 1.05, 'tag': 'Next Weekend Getaway', 'days_ahead': 6},
            'next-month': {'mult': 0.88, 'tag': 'Advance Saver (Next Month)', 'days_ahead': 30},
            'flexible': {'mult': 0.78, 'tag': 'Super Saver (Flexible)', 'days_ahead': 14},
        }
        win_info = WINDOW_CONFIG.get(date_window, WINDOW_CONFIG['this-weekend'])
        multiplier = win_info['mult']

        from flights.destination_imagery import get_destination_image, get_destination_season

        results = []
        for a in airports:
            if category != 'all' and category in CATEGORY_MAP:
                if a.code not in CATEGORY_MAP[category]:
                    continue

            is_intl = a.country != 'India'
            
            # Base price calculation
            raw_base = 7500 if is_intl else 2200 + (abs(hash(a.code)) % 3200)
            
            # Specific realistic starting tiers
            if a.code in ['GOI', 'COK', 'MAA', 'HYD', 'PNQ', 'AMD', 'BLR', 'DEL']:
                raw_base = 2400 + (abs(hash(a.code)) % 1400)
            elif a.code in ['SXR', 'IXB', 'DED', 'UDR', 'JAI', 'VNS', 'GAU', 'ATQ']:
                raw_base = 3200 + (abs(hash(a.code)) % 1600)
            elif a.code in ['DXB', 'SIN', 'BKK', 'MLE', 'DPS', 'KUL', 'DOH', 'HKG']:
                raw_base = 7800 + (abs(hash(a.code)) % 3500)
            elif a.code in ['LHR', 'CDG', 'FRA', 'AMS', 'FCO', 'BCN', 'ZRH', 'IST', 'CPH']:
                raw_base = 26000 + (abs(hash(a.code)) % 8000)
            elif a.code in ['JFK', 'LAX', 'SFO', 'SYD', 'MEL', 'YYZ', 'HND', 'ICN']:
                raw_base = 38000 + (abs(hash(a.code)) % 10000)

            # Apply travel window dynamic multiplier
            starting_price = round((raw_base * multiplier), -2)

            if starting_price > max_budget:
                continue

            # Calculate proximity score to selected budget
            proximity = abs(max_budget - starting_price)
            travel_date = (timezone.now() + timezone.timedelta(days=win_info['days_ahead'])).strftime('%Y-%m-%d')

            results.append({
                'code': a.code,
                'city': a.city,
                'name': a.name,
                'country': a.country,
                'is_international': is_intl,
                'starting_price': int(starting_price),
                'duration': f"{1 + (abs(hash(a.code)) % 5)}h {(abs(hash(a.code)) % 45) + 10}m",
                'stops': 0 if not is_intl or starting_price < 15000 else 1,
                'season': get_destination_season(a.code, a.best_season),
                'travel_window_tag': win_info['tag'],
                'target_date': travel_date,
                'proximity': proximity,
                'image': get_destination_image(a.code, a.category)
            })

        # Sort so that destinations matching closest to the chosen budget appear first (or descending price)
        results.sort(key=lambda x: (x['proximity'], -x['starting_price']))
        return JsonResponse({'destinations': results, 'count': len(results)})


class DownloadETicketView(View):
    def get(self, request, pnr):
        try:
            booking = Booking.objects.select_related(
                'flight', 'flight__origin', 'flight__destination',
                'flight__airline', 'flight__aircraft', 'coupon', 'user'
            ).prefetch_related(
                'booking_passengers', 'booking_passengers__passenger',
                'booking_passengers__seat', 'payments'
            ).get(pnr=pnr.upper())
        except Booking.DoesNotExist:
            raise Http404("Booking not found")

        if booking.user and request.user.is_authenticated and booking.user_id != request.user.id:
            return HttpResponse("Unauthorized", status=403)

        if booking.status != 'CONFIRMED':
            return HttpResponse("E-ticket unavailable — booking is not confirmed.", status=400)

        # Build passenger list for PDF
        passengers_data = []
        for bp in booking.booking_passengers.all():
            pax = bp.passenger
            seat_obj = bp.seat
            passengers_data.append({
                'first_name': pax.first_name,
                'last_name': pax.last_name,
                'email': pax.email,
                'phone': pax.phone,
                'dob': pax.dob.isoformat() if pax.dob else '',
                'gender': pax.gender,
                'nationality': pax.nationality or '',
                'passport_id': pax.passport_id or '',
                'govt_id': pax.passport_id or '',
                'seat': seat_obj.seat_number if seat_obj else 'Unassigned',
                'seat_class': seat_obj.seat_class if seat_obj else 'ECONOMY',
            })

        latest_payment = booking.payments.filter(status='SUCCESS').order_by('-created_at').first()

        pdf_buffer = build_eticket_pdf(booking, passengers_data, latest_payment)
        pdf_bytes = pdf_buffer.getvalue()
        filename = f"FlyEase_E-Ticket_{booking.pnr}.pdf"
        response = HttpResponse(
            pdf_bytes,
            content_type='application/pdf'
        )
        # If user wants to view in browser tab vs download
        disposition = 'inline' if request.GET.get('view') == '1' else 'attachment'
        response['Content-Disposition'] = f'{disposition}; filename="{filename}"'
        response['Content-Length'] = str(len(pdf_bytes))
        return response


class ProcessPaymentView(View):
    def post(self, request):
        try:
            payload = json.loads(request.body)
            amount = Decimal(str(payload.get('amount', 0)))
            payment_details = payload.get('payment_details', {}) or {}
            method = str(payment_details.get('method', 'CARD')).upper()
            valid_methods = {m[0] for m in Payment.METHOD_CHOICES}
            if method not in valid_methods:
                method = 'CARD'

            # Validate method-specific required fields (soft validation for simulator)
            errors = []
            if method == 'CARD':
                card_no = str(payment_details.get('card_number', '')).replace(' ', '')
                if len(card_no) < 13 or not card_no.isdigit():
                    errors.append('Please enter a valid card number.')
                expiry = payment_details.get('expiry', '')
                if not expiry or '/' not in expiry:
                    errors.append('Please enter a valid expiry (MM/YY).')
                cvv = payment_details.get('cvv', '')
                if not cvv or len(cvv) < 3 or not cvv.isdigit():
                    errors.append('Please enter a valid CVV.')
                card_last4 = card_no[-4:] if card_no.isdigit() else None
            elif method == 'UPI':
                upi = payment_details.get('upi_id', '')
                if not upi or '@' not in upi:
                    errors.append('Please enter a valid UPI ID (e.g. name@bank).')
                card_last4 = None
            elif method == 'NET_BANKING':
                bank = payment_details.get('bank_name', '')
                if not bank:
                    errors.append('Please select your bank.')
                card_last4 = None
            elif method == 'WALLET':
                wallet = payment_details.get('wallet_provider', '')
                if not wallet:
                    errors.append('Please select a wallet provider.')
                card_last4 = None
            else:
                card_last4 = None

            if errors:
                return JsonResponse({
                    'success': False,
                    'error': 'Validation failed',
                    'detail': errors[0],
                    'errors': errors,
                }, status=400)

            # Simulate gateway processing delay
            result = simulate_payment(amount)
            pay_id = generate_payment_id()

            # Create a standalone Payment record (no booking attached yet) for audit
            Payment.objects.create(
                booking=None,
                payment_id=pay_id,
                method=method,
                amount=amount,
                status='SUCCESS' if result.get('success') else 'FAILED',
                transaction_id=result.get('transaction_id'),
                card_last4=card_last4 if method == 'CARD' else None,
                upi_id=payment_details.get('upi_id') if method == 'UPI' else None,
                bank_name=payment_details.get('bank_name') if method == 'NET_BANKING' else None,
                wallet_provider=payment_details.get('wallet_provider') if method == 'WALLET' else None,
                gateway_response=result,
            )

            response_payload = {
                'success': result.get('success'),
                'payment_id': pay_id,
                'transaction_id': result.get('transaction_id'),
                'status': 'SUCCESS' if result.get('success') else 'FAILED',
                'amount': float(amount),
                'method': method,
            }
            return JsonResponse(response_payload)

        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': 'Payment processing error',
                'detail': str(e),
            }, status=500)


from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

@method_decorator(csrf_exempt, name='dispatch')
class FlyEaseAIChatView(View):
    def post(self, request):
        try:
            payload = json.loads(request.body)
            message = payload.get('message', '').strip()
            history = payload.get('history', [])
            if not message:
                return JsonResponse({"reply": "Please provide a travel question or request!"}, status=400)
            
            response = ask_flyease_ai(message, conversation_history=history)
            return JsonResponse(response)
        except Exception as e:
            return JsonResponse({
                "reply": "AI assistant is temporarily unavailable. The rest of the booking system remains fully operational.",
                "error": str(e),
                "flights": [],
                "deals": []
            }, status=200)


class DestinationWeatherView(View):
    def get(self, request, airport_code):
        try:
            ap = resolve_airport(airport_code)
            code = ap.code if ap else airport_code.upper()
            weather = get_destination_weather(code)
            return JsonResponse(weather)
        except Exception as e:
            return JsonResponse({
                "error": "Weather information is currently unavailable.",
                "code": airport_code.upper()
            }, status=200)


class TravelRequirementsView(View):
    def get(self, request):
        orig_input = request.GET.get('origin', 'BOM').strip()
        dest_input = request.GET.get('destination', 'DEL').strip()

        orig_ap = resolve_airport(orig_input)
        dest_ap = resolve_airport(dest_input)

        orig_code = orig_ap.code if orig_ap else "BOM"
        dest_code = dest_ap.code if dest_ap else "DEL"

        orig_country = orig_ap.country if orig_ap else "India"
        dest_country = dest_ap.country if dest_ap else "India"

        data = get_travel_requirements(orig_country, dest_country)
        data["origin_code"] = orig_code
        data["destination_code"] = dest_code
        return JsonResponse(data)


@method_decorator(csrf_exempt, name='dispatch')
class CreatePriceAlertView(View):
    def post(self, request):
        try:
            payload = json.loads(request.body)
            user_obj = getattr(request, 'user', None)
            is_auth = user_obj and user_obj.is_authenticated

            email = payload.get('email', '').strip()
            if not email and is_auth:
                email = user_obj.email
            if not email:
                return JsonResponse({"success": False, "error": "Email address is required to track prices."}, status=400)

            orig_input = payload.get('origin', '').strip()
            dest_input = payload.get('destination', '').strip()
            date_str = payload.get('travel_date', '').strip()
            target_price = Decimal(str(payload.get('target_price', 0)))
            initial_price = Decimal(str(payload.get('current_price', target_price)))
            flight_id = payload.get('flight_id')

            orig = resolve_airport(orig_input)
            dest = resolve_airport(dest_input)
            if not orig or not dest:
                return JsonResponse({"success": False, "error": "Invalid origin or destination."}, status=400)

            try:
                travel_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except Exception:
                travel_date = timezone.now().date() + timedelta(days=7)

            flight_obj = Flight.objects.filter(id=flight_id).first() if flight_id else None

            alert = PriceAlert.objects.create(
                user=user_obj if is_auth else None,
                email=email,
                flight=flight_obj,
                origin=orig,
                destination=dest,
                travel_date=travel_date,
                cabin_class=payload.get('class', 'ECONOMY').upper(),
                target_price=target_price,
                initial_price=initial_price,
                current_price=initial_price,
                is_active=True
            )

            return JsonResponse({
                "success": True,
                "alert_id": alert.id,
                "message": f"🔔 Price drop alert activated for {orig.code} → {dest.code} at ₹{target_price:,.0f}."
            })
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=400)


class ListPriceAlertsView(View):
    def get(self, request):
        email = request.GET.get('email', '')
        if not email and request.user.is_authenticated:
            email = request.user.email

        qs = PriceAlert.objects.all()
        if request.user.is_authenticated:
            qs = qs.filter(user=request.user)
        elif email:
            qs = qs.filter(email=email)
        else:
            return JsonResponse({"alerts": []})

        alerts_data = []
        for a in qs.order_by('-created_at'):
            alerts_data.append({
                "id": a.id,
                "origin": a.origin.code,
                "origin_city": a.origin.city,
                "destination": a.destination.code,
                "dest_city": a.destination.city,
                "travel_date": a.travel_date.isoformat(),
                "target_price": float(a.target_price),
                "initial_price": float(a.initial_price),
                "current_price": float(a.current_price or a.initial_price),
                "is_active": a.is_active,
                "is_triggered": a.is_triggered,
                "created_at": a.created_at.strftime("%d %b %Y")
            })
        return JsonResponse({"alerts": alerts_data})


class TogglePriceAlertView(View):
    def post(self, request, alert_id):
        try:
            alert = PriceAlert.objects.get(id=alert_id)
            payload = json.loads(request.body) if request.body else {}
            action = payload.get('action', 'toggle') # toggle, update_target, delete

            if action == 'delete':
                alert.delete()
                return JsonResponse({"success": True, "message": "Price alert tracking deleted."})
            elif action == 'update_target':
                new_price = Decimal(str(payload.get('target_price', alert.target_price)))
                alert.target_price = new_price
                alert.is_triggered = False
                alert.is_active = True
                alert.save()
                return JsonResponse({"success": True, "message": f"Target price updated to ₹{new_price:,.0f}."})
            else:
                alert.is_active = not alert.is_active
                alert.save()
                status_str = "resumed" if alert.is_active else "paused"
                return JsonResponse({"success": True, "is_active": alert.is_active, "message": f"Price alert {status_str}."})
        except PriceAlert.DoesNotExist:
            return JsonResponse({"success": False, "error": "Price alert not found"}, status=404)


class LiveFlightTrackerView(View):
    def get(self, request, flight_identifier):
        telemetry = get_flight_radar_telemetry(flight_identifier)
        return JsonResponse(telemetry)


class PersonalizedRecommendationsView(View):
    def get(self, request):
        recent_dest = request.GET.get('recent_dest', '')
        max_budget = float(request.GET.get('max_budget', 45000))
        user = request.user if request.user.is_authenticated else None
        recs = get_personalized_recommendations(user=user, recent_search_dest=recent_dest, max_budget=max_budget)
        return JsonResponse({"recommendations": recs})


class SystemHealthStatusView(View):
    def get(self, request):
        health = perform_system_health_checks()
        return JsonResponse({"health": health, "timestamp": timezone.now().isoformat()})

