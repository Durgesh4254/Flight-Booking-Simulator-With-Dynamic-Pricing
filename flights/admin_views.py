import json
from decimal import Decimal
from datetime import datetime, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test, login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db.models import Sum, Count, Avg, Q, F
from django.db import transaction

from flights.models import (
    Flight, Airport, Airline, Aircraft, Seat, Booking, BookingPassenger,
    Passenger, Coupon, Deal, PricingRule, FareHistory, Payment,
    AdminActivityLog, AdminAlert
)
from flights.utils import compute_dynamic_fare
from flights.destinations_dataset import DESTINATIONS_DATA

def is_admin_user(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)

def require_admin_api(view_func):
    def wrapper(request, *args, **kwargs):
        if not is_admin_user(request.user):
            return JsonResponse({'error': 'Unauthorized. Administrator privileges required.'}, status=403)
        return view_func(request, *args, **kwargs)
    return wrapper

def log_admin_activity(user, action_type, entity_type, entity_id, description, prev_val="", new_val="", request=None):
    ip = request.META.get('REMOTE_ADDR') if request else None
    AdminActivityLog.objects.create(
        user=user if user.is_authenticated else None,
        action_type=action_type,
        entity_type=entity_type,
        entity_id=str(entity_id) if entity_id else "",
        description=description,
        previous_value=str(prev_val),
        new_value=str(new_val),
        ip_address=ip
    )

# ----------------- ADMIN AUTH -----------------
@csrf_exempt
def admin_login_view(request):
    if is_admin_user(request.user):
        return redirect('/admin-portal/dashboard/')
        
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            admin_input = (data.get('username') or data.get('email') or '').strip()
            password = data.get('password')

            if not admin_input or not password:
                return JsonResponse({'success': False, 'error': 'Administrator email/username and password required.'}, status=400)

            lookup_username = admin_input
            if '@' in admin_input:
                matched_user = User.objects.filter(email__iexact=admin_input).first()
                if matched_user:
                    lookup_username = matched_user.username

            user = authenticate(request, username=lookup_username, password=password)
            if user is not None and (user.is_staff or user.is_superuser):
                login(request, user)
                request.session['user_role'] = 'ADMIN'
                log_admin_activity(user, "USER_STATUS_CHANGE", "AdminSession", user.id, "Admin user logged in successfully", request=request)
                return JsonResponse({'success': True, 'role': 'ADMIN', 'redirect': '/admin-portal/dashboard/'})
            elif user is not None:
                return JsonResponse({'success': False, 'error': 'You do not have administrator access.'}, status=403)
            else:
                return JsonResponse({'success': False, 'error': 'Invalid administrator credentials.'}, status=401)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    return render(request, 'admin/admin_login.html')

def admin_logout_view(request):
    if request.user.is_authenticated:
        log_admin_activity(request.user, "USER_STATUS_CHANGE", "AdminSession", request.user.id, "Admin user logged out", request=request)
    logout(request)
    request.session.flush()
    return redirect('/admin-portal/login/')

# ----------------- ADMIN PAGE VIEWS -----------------
@user_passes_test(is_admin_user, login_url='/admin-portal/login/')
def admin_dashboard_page(request):
    return render(request, 'admin/admin_dashboard.html', {'active_tab': 'dashboard', 'user': request.user})

@user_passes_test(is_admin_user, login_url='/admin-portal/login/')
def admin_flights_page(request):
    return render(request, 'admin/admin_flights.html', {'active_tab': 'flights', 'user': request.user})

@user_passes_test(is_admin_user, login_url='/admin-portal/login/')
def admin_airports_page(request):
    return render(request, 'admin/admin_airports.html', {'active_tab': 'airports', 'user': request.user})

@user_passes_test(is_admin_user, login_url='/admin-portal/login/')
def admin_pricing_page(request):
    return render(request, 'admin/admin_pricing.html', {'active_tab': 'pricing', 'user': request.user})

@user_passes_test(is_admin_user, login_url='/admin-portal/login/')
def admin_seats_page(request):
    return render(request, 'admin/admin_seats.html', {'active_tab': 'seats', 'user': request.user})

@user_passes_test(is_admin_user, login_url='/admin-portal/login/')
def admin_deals_page(request):
    return render(request, 'admin/admin_deals.html', {'active_tab': 'deals', 'user': request.user})

@user_passes_test(is_admin_user, login_url='/admin-portal/login/')
def admin_bookings_page(request):
    return render(request, 'admin/admin_bookings.html', {'active_tab': 'bookings', 'user': request.user})

@user_passes_test(is_admin_user, login_url='/admin-portal/login/')
def admin_refunds_page(request):
    return render(request, 'admin/admin_refunds.html', {'active_tab': 'refunds', 'user': request.user})

@user_passes_test(is_admin_user, login_url='/admin-portal/login/')
def admin_users_page(request):
    return render(request, 'admin/admin_users.html', {'active_tab': 'users', 'user': request.user})

@user_passes_test(is_admin_user, login_url='/admin-portal/login/')
def admin_airlines_page(request):
    airlines = Airline.objects.all()
    return render(request, 'admin/admin_airlines.html', {'active_tab': 'airlines', 'user': request.user, 'airlines': airlines})

@user_passes_test(is_admin_user, login_url='/admin-portal/login/')
def admin_alerts_page(request):
    return render(request, 'admin/admin_alerts.html', {'active_tab': 'alerts', 'user': request.user})

@user_passes_test(is_admin_user, login_url='/admin-portal/login/')
def admin_logs_page(request):
    return render(request, 'admin/admin_logs.html', {'active_tab': 'logs', 'user': request.user})

# ----------------- ADMIN REST APIs -----------------

@require_admin_api
def api_dashboard_kpis(request):
    """Real-time live KPI counters & metrics"""
    total_flights = Flight.objects.count()
    active_flights = Flight.objects.filter(status__in=['SCHEDULED', 'BOARDING', 'IN_FLIGHT'], is_active=True).count()
    total_bookings = Booking.objects.count()
    cancelled_bookings = Booking.objects.filter(status='CANCELLED').count()
    total_users = User.objects.count()
    
    # Revenue aggregation
    revenue_data = Booking.objects.filter(status__in=['CONFIRMED', 'COMPLETED']).aggregate(
        total_rev=Sum('price_paid'),
        avg_fare=Avg('price_paid')
    )
    total_revenue = float(revenue_data['total_rev'] or 0.0)
    avg_ticket_price = float(revenue_data['avg_fare'] or 0.0)

    today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_revenue_data = Booking.objects.filter(
        created_at__gte=today_start,
        status__in=['CONFIRMED', 'COMPLETED']
    ).aggregate(today_rev=Sum('price_paid'))
    today_revenue = float(today_revenue_data['today_rev'] or 0.0)

    # Seat inventory totals
    seat_data = Flight.objects.filter(is_active=True).aggregate(
        avail=Sum('available_seats'),
        total_cap=Sum('total_seats')
    )
    avail_seats = seat_data['avail'] or 0
    total_cap = seat_data['total_cap'] or 1
    occupancy_rate = round(((total_cap - avail_seats) / max(total_cap, 1)) * 100, 1)

    unread_alerts = AdminAlert.objects.filter(is_read=False).count()

    return JsonResponse({
        'total_flights': total_flights,
        'active_flights': active_flights,
        'total_bookings': total_bookings,
        'cancelled_bookings': cancelled_bookings,
        'total_users': total_users,
        'total_revenue': total_revenue,
        'today_revenue': today_revenue,
        'available_seats': avail_seats,
        'occupancy_rate': occupancy_rate,
        'avg_ticket_price': avg_ticket_price,
        'unread_alerts': unread_alerts
    })

@require_admin_api
def api_analytics_charts(request):
    """Interactive analytics charts data based on timeframe filter"""
    timeframe = request.GET.get('timeframe', '30D')
    now = timezone.now()
    
    days_map = {'TODAY': 1, '7D': 7, '30D': 30, '3M': 90, '6M': 180, '1Y': 365}
    days = days_map.get(timeframe, 30)
    start_date = now - timedelta(days=days)

    # 1. Revenue over time (daily/grouped)
    bookings_qs = Booking.objects.filter(created_at__gte=start_date)
    
    labels = []
    revenue_series = []
    bookings_series = []

    step_days = max(1, days // 15)
    cur = start_date
    while cur <= now:
        next_dt = cur + timedelta(days=step_days)
        interval_b = bookings_qs.filter(created_at__gte=cur, created_at__lt=next_dt)
        rev = float(interval_b.filter(status__in=['CONFIRMED', 'COMPLETED']).aggregate(s=Sum('price_paid'))['s'] or 0)
        cnt = interval_b.count()
        
        labels.append(cur.strftime('%d %b'))
        revenue_series.append(rev)
        bookings_series.append(cnt)
        cur = next_dt

    # 2. Revenue by Route (Top 6)
    top_routes_raw = (
        Flight.objects.filter(bookings__status__in=['CONFIRMED', 'COMPLETED'])
        .values('origin__code', 'destination__code')
        .annotate(
            route_revenue=Sum('bookings__price_paid'),
            booking_count=Count('bookings')
        )
        .order_by('-route_revenue')[:6]
    )
    route_labels = [f"{r['origin__code']} → {r['destination__code']}" for r in top_routes_raw]
    route_revenue = [float(r['route_revenue'] or 0) for r in top_routes_raw]

    # 3. Revenue by Airline
    airline_raw = (
        Airline.objects.filter(flight__bookings__status__in=['CONFIRMED', 'COMPLETED'])
        .values('name')
        .annotate(airline_rev=Sum('flight__bookings__price_paid'))
        .order_by('-airline_rev')[:6]
    )
    airline_labels = [a['name'] for a in airline_raw]
    airline_rev = [float(a['airline_rev'] or 0) for a in airline_raw]

    # 4. Cabin Class distribution
    cabin_counts = {
        'Economy': BookingPassenger.objects.filter(seat__seat_class='ECONOMY').count() or 120,
        'Premium Economy': BookingPassenger.objects.filter(seat__seat_class='PREMIUM_ECONOMY').count() or 35,
        'Business': BookingPassenger.objects.filter(seat__seat_class='BUSINESS').count() or 22,
        'First Class': BookingPassenger.objects.filter(seat__seat_class='FIRST').count() or 8,
    }

    # 5. Demand Heatmap (Top busy city pairs)
    demand_heatmap = list(
        Flight.objects.values('origin__code', 'destination__code')
        .annotate(
            avg_demand=Avg('demand_factor'),
            avg_occ=Avg(F('total_seats') - F('available_seats'))
        )
        .order_by('-avg_demand')[:8]
    )
    demand_list = [{
        'route': f"{d['origin__code']} → {d['destination__code']}",
        'demand_score': round(float(d['avg_demand'] or 1.0) * 70, 1),
        'occupancy': round(min(100.0, float(d['avg_occ'] or 60.0) / 1.5), 1)
    } for d in demand_heatmap]

    return JsonResponse({
        'revenue_chart': {'labels': labels, 'revenue': revenue_series, 'bookings': bookings_series},
        'route_chart': {'labels': route_labels, 'data': route_revenue},
        'airline_chart': {'labels': airline_labels, 'data': airline_rev},
        'cabin_chart': {'labels': list(cabin_counts.keys()), 'data': list(cabin_counts.values())},
        'demand_heatmap': demand_list
    })

# ----------------- FLIGHT MANAGEMENT APIs -----------------
@require_admin_api
def api_flights_list(request):
    """Search, filter and paginate flights with live dynamic price inspection"""
    search = request.GET.get('search', '').strip()
    origin = request.GET.get('origin', '').strip().upper()
    destination = request.GET.get('destination', '').strip().upper()
    airline_code = request.GET.get('airline', '').strip().upper()
    status = request.GET.get('status', '').strip().upper()
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 25))

    qs = Flight.objects.select_related('airline', 'aircraft', 'origin', 'destination').all().order_by('-departure_time')

    if search:
        qs = qs.filter(
            Q(flight_number__icontains=search) |
            Q(origin__city__icontains=search) |
            Q(destination__city__icontains=search) |
            Q(airline__name__icontains=search)
        )
    if origin:
        qs = qs.filter(origin__code=origin)
    if destination:
        qs = qs.filter(destination__code=destination)
    if airline_code:
        qs = qs.filter(airline__code=airline_code)
    if status:
        qs = qs.filter(status=status)

    total_count = qs.count()
    start = (page - 1) * page_size
    end = start + page_size
    flights_page = qs[start:end]

    results = []
    for f in flights_page:
        pricing = compute_dynamic_fare(f, requested_class='ECONOMY')
        occ = round(((f.total_seats - f.available_seats) / max(f.total_seats, 1)) * 100, 1)
        
        # Demand tag
        if f.demand_factor >= 1.25 or occ >= 85:
            demand_tag = "🔴 SURGE"
        elif f.demand_factor >= 1.10 or occ >= 70:
            demand_tag = "🟠 HIGH"
        elif f.demand_factor >= 0.95:
            demand_tag = "🟡 NORMAL"
        else:
            demand_tag = "🟢 LOW"

        results.append({
            'id': f.id,
            'flight_number': f.flight_number,
            'airline_name': f.airline.name if f.airline else 'Unknown',
            'airline_code': f.airline.code if f.airline else '',
            'airline_logo': f.airline.logo_url if f.airline else '',
            'aircraft': f.aircraft.model_name if f.aircraft else '',
            'origin_code': f.origin.code if f.origin else '',
            'origin_city': f.origin.city if f.origin else '',
            'destination_code': f.destination.code if f.destination else '',
            'destination_city': f.destination.city if f.destination else '',
            'departure_time': f.departure_time.strftime('%Y-%m-%d %H:%M'),
            'arrival_time': f.arrival_time.strftime('%Y-%m-%d %H:%M'),
            'base_price': float(f.base_price),
            'current_fare': pricing['current_fare_before_tax'],
            'total_fare': pricing['total'],
            'total_seats': f.total_seats,
            'available_seats': f.available_seats,
            'occupancy': occ,
            'demand_factor': round(f.demand_factor, 2),
            'demand_tag': demand_tag,
            'status': f.status,
            'is_active': f.is_active,
            'manual_override': float(f.manual_override_price) if f.manual_override_price else None
        })

    return JsonResponse({
        'total': total_count,
        'page': page,
        'page_size': page_size,
        'flights': results
    })

@csrf_exempt
@require_admin_api
def api_flight_save(request):
    """Add new flight or Edit existing flight with strict validations"""
    if request.method != 'POST':
        return HttpResponseForbidden()
    try:
        data = json.loads(request.body)
        flight_id = data.get('id')
        flight_num = data.get('flight_number', '').strip().upper()
        airline_code = data.get('airline_code', '').strip().upper()
        origin_code = data.get('origin_code', '').strip().upper()
        dest_code = data.get('dest_code', '').strip().upper()
        dep_str = data.get('departure_time')
        arr_str = data.get('arrival_time')
        base_fare = Decimal(str(data.get('base_price', 3500)))
        status = data.get('status', 'SCHEDULED')
        is_active = data.get('is_active', True)
        manual_override = Decimal(str(data.get('manual_override_price'))) if data.get('manual_override_price') else None

        if origin_code == dest_code:
            return JsonResponse({'success': False, 'error': 'Origin and Destination airports cannot be identical.'}, status=400)

        origin = Airport.objects.get(code=origin_code)
        dest = Airport.objects.get(code=dest_code)
        airline = Airline.objects.get(code=airline_code) if airline_code else None
        aircraft = Aircraft.objects.first()

        dep_dt = datetime.fromisoformat(dep_str.replace('Z', '+00:00')) if 'T' in dep_str else datetime.strptime(dep_str, '%Y-%m-%d %H:%M')
        arr_dt = datetime.fromisoformat(arr_str.replace('Z', '+00:00')) if 'T' in arr_str else datetime.strptime(arr_str, '%Y-%m-%d %H:%M')

        if timezone.is_naive(dep_dt):
            dep_dt = timezone.make_aware(dep_dt)
        if timezone.is_naive(arr_dt):
            arr_dt = timezone.make_aware(arr_dt)

        if arr_dt <= dep_dt:
            return JsonResponse({'success': False, 'error': 'Arrival time must be strictly after Departure time.'}, status=400)

        if flight_id:
            flight = Flight.objects.get(id=flight_id)
            prev_fare = flight.base_price
            flight.flight_number = flight_num
            flight.airline = airline
            flight.origin = origin
            flight.destination = dest
            flight.departure_time = dep_dt
            flight.arrival_time = arr_dt
            flight.base_price = base_fare
            flight.status = status
            flight.is_active = is_active
            flight.manual_override_price = manual_override
            flight.save()
            log_admin_activity(request.user, "FLIGHT_UPDATE", "Flight", flight.id, f"Updated flight {flight.flight_number}", prev_val=prev_fare, new_val=base_fare, request=request)
        else:
            if Flight.objects.filter(flight_number=flight_num).exists():
                return JsonResponse({'success': False, 'error': f"Flight number {flight_num} already exists."}, status=400)
            
            flight = Flight.objects.create(
                flight_number=flight_num,
                airline=airline,
                aircraft=aircraft,
                origin=origin,
                destination=dest,
                departure_time=dep_dt,
                arrival_time=arr_dt,
                base_price=base_fare,
                total_seats=aircraft.total_capacity if aircraft else 180,
                available_seats=aircraft.total_capacity if aircraft else 180,
                status=status,
                is_active=is_active,
                manual_override_price=manual_override
            )
            # Create seats for flight
            from flights.flight_generator import generate_seats_for_flight
            if aircraft:
                generate_seats_for_flight(flight, aircraft)
            log_admin_activity(request.user, "FLIGHT_CREATE", "Flight", flight.id, f"Created new flight {flight.flight_number} ({origin.code} → {dest.code})", new_val=base_fare, request=request)

        return JsonResponse({'success': True, 'flight_id': flight.id, 'message': f"Flight {flight.flight_number} saved successfully."})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

# ----------------- DYNAMIC PRICING CONTROL CENTER APIs -----------------

@require_admin_api
def api_flight_pricing_details(request, flight_id):
    """Return granular dynamic pricing mathematical breakdown for the pricing inspector"""
    flight = get_object_or_404(Flight, id=flight_id)
    pricing = compute_dynamic_fare(flight)
    
    # 30-Day Fare History
    history_qs = FareHistory.objects.filter(flight=flight).order_by('timestamp')[:30]
    history_data = [{
        'time': h.timestamp.strftime('%d %b %H:%M'),
        'fare': float(h.fare),
        'seats': h.seats_available,
        'reason': h.reason
    } for h in history_qs]

    rule = PricingRule.objects.filter(is_active=True).first()

    hours_left = max(0.0, round((flight.departure_time - timezone.now()).total_seconds() / 3600, 1))

    return JsonResponse({
        'flight_id': flight.id,
        'flight_number': flight.flight_number,
        'route': f"{flight.origin.code} → {flight.destination.code}",
        'airline': flight.airline.name if flight.airline else '',
        'base_price': float(flight.base_price),
        'current_fare': pricing['current_fare_before_tax'],
        'total_fare': pricing['total'],
        'taxes': pricing['taxes'],
        'multiplier': pricing['multiplier'],
        'breakdown': pricing['breakdown'],
        'is_override': pricing['is_override'],
        'manual_override_price': float(flight.manual_override_price) if flight.manual_override_price else None,
        'min_fare_limit': float(flight.min_fare_limit) if flight.min_fare_limit else (float(rule.min_fare_floor) if rule else 1500),
        'max_fare_limit': float(flight.max_fare_limit) if flight.max_fare_limit else (float(rule.max_fare_cap) if rule else 45000),
        'seats_available': flight.available_seats,
        'total_seats': flight.total_seats,
        'hours_to_departure': hours_left,
        'demand_factor': round(flight.demand_factor, 2),
        'history': history_data
    })

@csrf_exempt
@require_admin_api
def api_simulate_pricing(request):
    """
    Simulation tool: calculates simulated fare without mutating the database.
    Allows real-time price preview across slider factors.
    """
    if request.method != 'POST':
        return HttpResponseForbidden()
    try:
        data = json.loads(request.body)
        flight_id = data.get('flight_id')
        base_price = Decimal(str(data.get('base_price', 4500)))
        total_seats = int(data.get('total_seats', 180))
        avail_seats = int(data.get('seats_remaining', 30))
        demand_pct = float(data.get('demand_pct', 80)) / 100.0 # 0.8
        hours_left = float(data.get('hours_to_departure', 24))
        is_weekend = bool(data.get('is_weekend', False))

        rule = PricingRule.objects.filter(is_active=True).first()
        demand_weight = rule.demand_multiplier_weight if rule else 1.15
        seat_weight = rule.seat_availability_weight if rule else 1.25
        time_weight = rule.time_to_departure_weight if rule else 1.20
        weekend_weight = rule.weekend_multiplier if rule else 1.15

        mult = 1.0
        factors = []

        # Time Factor
        if hours_left < 12:
            t_adj = 0.50 * time_weight
            factors.append({"name": "Imminent Departure (<12h)", "val": f"+{round(t_adj*100)}%", "amount": float(base_price)*t_adj})
            mult += t_adj
        elif hours_left < 24:
            t_adj = 0.35 * time_weight
            factors.append({"name": "Last Minute (<24h)", "val": f"+{round(t_adj*100)}%", "amount": float(base_price)*t_adj})
            mult += t_adj
        elif hours_left < 72:
            t_adj = 0.15 * time_weight
            factors.append({"name": "Near Departure (<3d)", "val": f"+{round(t_adj*100)}%", "amount": float(base_price)*t_adj})
            mult += t_adj
        elif hours_left > 720:
            t_adj = -0.10
            factors.append({"name": "Early Bird (>30d)", "val": "-10%", "amount": float(base_price)*t_adj})
            mult += t_adj

        # Seat Factor
        seat_ratio = avail_seats / max(total_seats, 1)
        if seat_ratio < 0.10:
            s_adj = 0.55 * seat_weight
            factors.append({"name": "Critical Seat Scarcity (<10%)", "val": f"+{round(s_adj*100)}%", "amount": float(base_price)*s_adj})
            mult += s_adj
        elif seat_ratio < 0.25:
            s_adj = 0.30 * seat_weight
            factors.append({"name": "High Occupancy (<25%)", "val": f"+{round(s_adj*100)}%", "amount": float(base_price)*s_adj})
            mult += s_adj
        elif seat_ratio < 0.50:
            s_adj = 0.15 * seat_weight
            factors.append({"name": "Moderate Occupancy (<50%)", "val": f"+{round(s_adj*100)}%", "amount": float(base_price)*s_adj})
            mult += s_adj

        # Demand Factor
        d_adj = (demand_pct - 1.0) * demand_weight
        if abs(d_adj) > 0.02:
            factors.append({"name": "Market Demand", "val": f"{round(d_adj*100):+d}%", "amount": float(base_price)*d_adj})
            mult += d_adj

        if is_weekend:
            w_adj = 0.12 * weekend_weight
            factors.append({"name": "Weekend Surge", "val": f"+{round(w_adj*100)}%", "amount": float(base_price)*w_adj})
            mult += w_adj

        sim_fare = float(base_price) * max(mult, 0.8)
        sim_taxes = sim_fare * 0.18
        sim_total = sim_fare + sim_taxes

        # Current flight price for delta
        current_fare = float(base_price)
        if flight_id:
            try:
                fl = Flight.objects.get(id=flight_id)
                current_p = compute_dynamic_fare(fl)
                current_fare = current_p['current_fare_before_tax']
            except Flight.DoesNotExist:
                pass

        diff = sim_fare - current_fare
        pct_diff = round((diff / max(current_fare, 1)) * 100, 1)

        return JsonResponse({
            'success': True,
            'base_price': float(base_price),
            'simulated_fare': round(sim_fare, 2),
            'simulated_total': round(sim_total, 2),
            'current_fare': round(current_fare, 2),
            'difference': round(diff, 2),
            'percentage_diff': pct_diff,
            'multiplier': round(mult, 2),
            'factors': factors
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

@csrf_exempt
@require_admin_api
def api_apply_flight_pricing(request, flight_id):
    """Apply manual price override, minimum/maximum bounds or base price update"""
    if request.method != 'POST':
        return HttpResponseForbidden()
    try:
        data = json.loads(request.body)
        flight = get_object_or_404(Flight, id=flight_id)
        
        prev_override = flight.manual_override_price
        
        if 'manual_override_price' in data:
            override_val = data['manual_override_price']
            flight.manual_override_price = Decimal(str(override_val)) if override_val else None
            
        if 'base_price' in data and data['base_price']:
            flight.base_price = Decimal(str(data['base_price']))
            
        if 'min_fare_limit' in data:
            flight.min_fare_limit = Decimal(str(data['min_fare_limit'])) if data['min_fare_limit'] else None
            
        if 'max_fare_limit' in data:
            flight.max_fare_limit = Decimal(str(data['max_fare_limit'])) if data['max_fare_limit'] else None

        flight.save()

        # Record in FareHistory
        pricing = compute_dynamic_fare(flight)
        FareHistory.objects.create(
            flight=flight,
            fare=Decimal(str(pricing['total'])),
            seats_available=flight.available_seats,
            reason="Admin Pricing Update / Manual Override"
        )

        log_admin_activity(
            request.user,
            "PRICE_OVERRIDE",
            "Flight",
            flight.id,
            f"Updated pricing controls for {flight.flight_number}",
            prev_val=f"Override: {prev_override}",
            new_val=f"Fare: ₹{pricing['current_fare_before_tax']}",
            request=request
        )

        return JsonResponse({
            'success': True,
            'message': f"Pricing rule updated for flight {flight.flight_number}.",
            'current_fare': pricing['current_fare_before_tax'],
            'total_fare': pricing['total']
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

@csrf_exempt
@require_admin_api
def api_bulk_pricing_adjustment(request):
    """Apply percentage or fixed price adjustments across selected flights / routes"""
    if request.method != 'POST':
        return HttpResponseForbidden()
    try:
        data = json.loads(request.body)
        flight_ids = data.get('flight_ids', [])
        adjustment_type = data.get('adjustment_type', 'PERCENT') # 'PERCENT' or 'FIXED'
        value = float(data.get('value', 0)) # e.g. 10.0 for +10% or -500 for -₹500

        if not flight_ids:
            return JsonResponse({'success': False, 'error': 'No flights selected for bulk update.'}, status=400)

        flights = Flight.objects.filter(id__in=flight_ids)
        updated_count = 0
        
        for f in flights:
            current_base = float(f.base_price)
            if adjustment_type == 'PERCENT':
                new_base = round(current_base * (1.0 + (value / 100.0)), 2)
            else:
                new_base = round(current_base + value, 2)
            
            new_base = max(1200.0, new_base)
            f.base_price = Decimal(str(new_base))
            f.save()

            # Record in FareHistory
            new_p = compute_dynamic_fare(f)
            FareHistory.objects.create(
                flight=f,
                fare=Decimal(str(new_p['total'])),
                seats_available=f.available_seats,
                reason=f"Bulk Price Adjustment ({value:+}{'%' if adjustment_type=='PERCENT' else '₹'})"
            )
            updated_count += 1

        log_admin_activity(
            request.user,
            "BULK_PRICE_CHANGE",
            "FlightGroup",
            f"{updated_count} flights",
            f"Applied bulk {adjustment_type} adjustment of {value} across {updated_count} flights.",
            request=request
        )

        return JsonResponse({'success': True, 'updated_count': updated_count, 'message': f"Successfully updated pricing for {updated_count} flights."})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

@csrf_exempt
@require_admin_api
def api_pricing_rules_get_set(request):
    """Retrieve and update global Dynamic Pricing Engine Configuration"""
    if request.method == 'GET':
        rule = PricingRule.objects.filter(is_active=True).first()
        if not rule:
            rule = PricingRule.objects.create(name="Default Engine Rule")
        
        return JsonResponse({
            'id': rule.id,
            'name': rule.name,
            'min_fare_floor': float(rule.min_fare_floor),
            'max_fare_cap': float(rule.max_fare_cap),
            'demand_multiplier_weight': rule.demand_multiplier_weight,
            'seat_availability_weight': rule.seat_availability_weight,
            'time_to_departure_weight': rule.time_to_departure_weight,
            'peak_season_multiplier': rule.peak_season_multiplier,
            'weekend_multiplier': rule.weekend_multiplier,
            'holiday_multiplier': rule.holiday_multiplier
        })
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            rule = PricingRule.objects.filter(is_active=True).first()
            if not rule:
                rule = PricingRule(name="Engine Rule")

            rule.min_fare_floor = Decimal(str(data.get('min_fare_floor', 1500)))
            rule.max_fare_cap = Decimal(str(data.get('max_fare_cap', 45000)))
            rule.demand_multiplier_weight = float(data.get('demand_multiplier_weight', 1.15))
            rule.seat_availability_weight = float(data.get('seat_availability_weight', 1.25))
            rule.time_to_departure_weight = float(data.get('time_to_departure_weight', 1.20))
            rule.peak_season_multiplier = float(data.get('peak_season_multiplier', 1.20))
            rule.weekend_multiplier = float(data.get('weekend_multiplier', 1.15))
            rule.holiday_multiplier = float(data.get('holiday_multiplier', 1.25))
            rule.created_by = request.user
            rule.save()

            log_admin_activity(
                request.user,
                "PRICING_RULE_CHANGE",
                "PricingRule",
                rule.id,
                "Updated global dynamic pricing engine parameters & weights",
                request=request
            )

            return JsonResponse({'success': True, 'message': 'Dynamic pricing rules updated successfully.'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)

# ----------------- AIRPORTS & DESTINATIONS APIs -----------------

@require_admin_api
def api_airports_list(request):
    """Search 260+ airport directory with pagination and filters"""
    query = request.GET.get('q', '').strip()
    category = request.GET.get('category', '').strip()
    country = request.GET.get('country', '').strip()
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 50))

    qs = Airport.objects.all().order_by('-popularity', 'city')
    if query:
        qs = qs.filter(
            Q(code__icontains=query) |
            Q(name__icontains=query) |
            Q(city__icontains=query) |
            Q(country__icontains=query)
        )
    if category:
        qs = qs.filter(category=category)
    if country:
        qs = qs.filter(country__icontains=country)

    total = qs.count()
    start = (page - 1) * page_size
    items = qs[start:start + page_size]

    data = [{
        'id': a.id,
        'code': a.code,
        'icao_code': a.icao_code,
        'name': a.name,
        'city': a.city,
        'country': a.country,
        'region': a.region,
        'terminal': a.terminal,
        'timezone': a.timezone,
        'is_international': a.is_international,
        'popularity': a.popularity,
        'category': a.category,
        'avg_fare': float(a.avg_fare),
        'best_season': a.best_season,
        'is_active': a.is_active
    } for a in items]

    return JsonResponse({
        'total': total,
        'page': page,
        'page_size': page_size,
        'airports': data
    })

@csrf_exempt
@require_admin_api
def api_airport_save(request):
    """Add or Edit airport in global directory"""
    if request.method != 'POST':
        return HttpResponseForbidden()
    try:
        data = json.loads(request.body)
        airport_id = data.get('id')
        code = data.get('code', '').strip().upper()
        name = data.get('name', '').strip()
        city = data.get('city', '').strip()
        country = data.get('country', '').strip()
        category = data.get('category', 'CITY')
        avg_fare = Decimal(str(data.get('avg_fare', 4500)))

        if airport_id:
            ap = Airport.objects.get(id=airport_id)
            ap.name = name
            ap.city = city
            ap.country = country
            ap.category = category
            ap.avg_fare = avg_fare
            ap.is_international = data.get('is_international', ap.is_international)
            ap.is_active = data.get('is_active', True)
            ap.save()
            log_admin_activity(request.user, "AIRPORT_MODIFY", "Airport", ap.id, f"Edited airport {ap.code} - {ap.city}", request=request)
        else:
            if Airport.objects.filter(code=code).exists():
                return JsonResponse({'success': False, 'error': f"Airport with IATA code {code} already exists."}, status=400)
            ap = Airport.objects.create(
                code=code,
                name=name,
                city=city,
                country=country,
                category=category,
                avg_fare=avg_fare,
                is_international=data.get('is_international', False),
                is_active=data.get('is_active', True)
            )
            log_admin_activity(request.user, "AIRPORT_MODIFY", "Airport", ap.id, f"Created new airport {ap.code} ({ap.city})", request=request)

        return JsonResponse({'success': True, 'message': f"Airport {ap.code} saved."})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

# ----------------- SEAT INVENTORY MANAGEMENT -----------------

@require_admin_api
def api_flight_seat_map(request, flight_id):
    """Return complete aircraft cabin seat inventory for admin blocking/price control"""
    flight = get_object_or_404(Flight, id=flight_id)
    seats = Seat.objects.filter(flight=flight).order_by('seat_number')

    seat_list = []
    counts = {'AVAILABLE': 0, 'OCCUPIED': 0, 'BLOCKED': 0, 'SELECTED': 0}
    for s in seats:
        counts[s.status] = counts.get(s.status, 0) + 1
        seat_list.append({
            'id': s.id,
            'seat_number': s.seat_number,
            'seat_class': s.seat_class,
            'status': s.status,
            'is_window': s.is_window,
            'is_aisle': s.is_aisle,
            'extra_legroom': s.extra_legroom,
            'price_override': float(s.price_override) if s.price_override else None
        })

    return JsonResponse({
        'flight_id': flight.id,
        'flight_number': flight.flight_number,
        'aircraft': flight.aircraft.model_name if flight.aircraft else 'Standard',
        'stats': counts,
        'seats': seat_list
    })

@csrf_exempt
@require_admin_api
def api_toggle_seat_status(request):
    """Toggle or set seat status (AVAILABLE, OCCUPIED, BLOCKED) and instantly update live counters"""
    if request.method != 'POST':
        return HttpResponseForbidden()
    try:
        data = json.loads(request.body)
        seat_id = data.get('seat_id')
        new_status = data.get('status') # 'AVAILABLE', 'OCCUPIED', 'BLOCKED'

        seat = get_object_or_404(Seat, id=seat_id)
        
        # If no explicit status given, cycle through: AVAILABLE -> OCCUPIED -> BLOCKED -> AVAILABLE
        if not new_status:
            cycle = {'AVAILABLE': 'OCCUPIED', 'OCCUPIED': 'BLOCKED', 'BLOCKED': 'AVAILABLE'}
            new_status = cycle.get(seat.status, 'AVAILABLE')

        prev_status = seat.status
        seat.status = new_status
        seat.save()

        # Update available_seats on flight
        avail_count = Seat.objects.filter(flight=seat.flight, status='AVAILABLE').count()
        seat.flight.available_seats = avail_count
        seat.flight.save()

        # Gather fresh stats
        flight_seats = Seat.objects.filter(flight=seat.flight)
        counts = {
            'AVAILABLE': flight_seats.filter(status='AVAILABLE').count(),
            'OCCUPIED': flight_seats.filter(status='OCCUPIED').count(),
            'BLOCKED': flight_seats.filter(status='BLOCKED').count(),
        }

        log_admin_activity(
            request.user,
            "SEAT_BLOCK",
            "Seat",
            seat.id,
            f"Seat {seat.seat_number} changed from {prev_status} to {new_status} on flight {seat.flight.flight_number}",
            prev_val=prev_status,
            new_val=new_status,
            request=request
        )

        return JsonResponse({
            'success': True,
            'message': f"Seat {seat.seat_number} set to {new_status}.",
            'seat_id': seat.id,
            'seat_number': seat.seat_number,
            'new_status': new_status,
            'stats': counts
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

# ----------------- ADVANCED DEALS & BUDGET INTELLIGENCE -----------------

@require_admin_api
def api_deals_list(request):
    """Retrieve all deals with conversion and performance tracking"""
    deals = Deal.objects.all().order_by('-valid_until')
    result = []
    for d in deals:
        conversion = round((d.bookings_count / max(d.applied_count, 1)) * 100, 1)
        result.append({
            'id': d.id,
            'title': d.title,
            'code': d.code,
            'category': d.category,
            'badge': d.badge,
            'description': d.description,
            'discount_type': d.discount_type,
            'discount_percent': d.discount_percent,
            'discount_value': float(d.discount_value),
            'origin_code': d.origin_code or 'Any',
            'destination_code': d.destination_code or 'Any',
            'starting_price': float(d.starting_price),
            'valid_from': d.valid_from.strftime('%Y-%m-%d'),
            'valid_until': d.valid_until.strftime('%Y-%m-%d'),
            'is_active': d.is_active,
            'applied_count': d.applied_count,
            'bookings_count': d.bookings_count,
            'conversion_rate': conversion,
            'total_discount_given': float(d.total_discount_given),
            'revenue_generated': float(d.revenue_generated),
            'usage_limit': d.usage_limit
        })
    return JsonResponse({'deals': result})

@csrf_exempt
@require_admin_api
def api_deal_save(request):
    """Create or Edit a deal targeting destinations, airlines, or flights"""
    if request.method != 'POST':
        return HttpResponseForbidden()
    try:
        data = json.loads(request.body)
        deal_id = data.get('id')
        code = data.get('code', '').strip().upper()
        title = data.get('title', '').strip()
        discount_percent = float(data.get('discount_percent', 10.0))
        starting_price = Decimal(str(data.get('starting_price', 2999)))
        valid_until_str = data.get('valid_until')
        category = data.get('category', 'DOMESTIC')

        valid_until = datetime.fromisoformat(valid_until_str.replace('Z', '+00:00')) if 'T' in valid_until_str else datetime.strptime(valid_until_str, '%Y-%m-%d')
        if timezone.is_naive(valid_until):
            valid_until = timezone.make_aware(valid_until)

        if deal_id:
            deal = Deal.objects.get(id=deal_id)
            deal.title = title
            deal.code = code
            deal.category = category
            deal.description = data.get('description', deal.description)
            deal.discount_percent = discount_percent
            deal.starting_price = starting_price
            deal.origin_code = data.get('origin_code') or None
            deal.destination_code = data.get('destination_code') or None
            deal.valid_until = valid_until
            deal.is_active = data.get('is_active', True)
            deal.save()
            log_admin_activity(request.user, "DEAL_UPDATE", "Deal", deal.id, f"Edited deal {deal.code}", request=request)
        else:
            if Deal.objects.filter(code=code).exists():
                return JsonResponse({'success': False, 'error': f"Deal code {code} already exists."}, status=400)
            deal = Deal.objects.create(
                title=title,
                code=code,
                category=category,
                description=data.get('description', f"Special discount with code {code}"),
                discount_percent=discount_percent,
                starting_price=starting_price,
                origin_code=data.get('origin_code') or None,
                destination_code=data.get('destination_code') or None,
                valid_until=valid_until,
                is_active=data.get('is_active', True)
            )
            log_admin_activity(request.user, "DEAL_CREATE", "Deal", deal.id, f"Created new deal {deal.code}", request=request)

        return JsonResponse({'success': True, 'deal_id': deal.id, 'message': f"Deal {deal.code} saved successfully."})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

@csrf_exempt
@require_admin_api
def api_deal_duplicate(request, deal_id):
    """Duplicate an existing deal for fast promo creation"""
    if request.method != 'POST':
        return HttpResponseForbidden()
    try:
        orig = get_object_or_404(Deal, id=deal_id)
        new_code = f"{orig.code}_COPY"
        count = 1
        while Deal.objects.filter(code=new_code).exists():
            new_code = f"{orig.code}_COPY{count}"
            count += 1

        new_deal = Deal.objects.create(
            title=f"Copy of {orig.title}",
            code=new_code,
            category=orig.category,
            badge=orig.badge,
            description=orig.description,
            discount_percent=orig.discount_percent,
            origin_code=orig.origin_code,
            destination_code=orig.destination_code,
            starting_price=orig.starting_price,
            valid_from=timezone.now(),
            valid_until=orig.valid_until,
            is_active=True
        )

        log_admin_activity(request.user, "DEAL_DUPLICATE", "Deal", new_deal.id, f"Duplicated deal {orig.code} to {new_deal.code}", request=request)

        return JsonResponse({'success': True, 'deal_id': new_deal.id, 'message': f"Deal duplicated as {new_deal.code}."})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

@require_admin_api
def api_deal_budget_finder(request):
    """
    Find matching destinations and flights that fit within the admin's chosen deal budget.
    """
    min_budget = float(request.GET.get('min_budget', 2000))
    max_budget = float(request.GET.get('max_budget', 10000))
    category = request.GET.get('category', '').strip().upper()
    discount_pct = float(request.GET.get('discount', 20.0))

    # Query matching flights
    flights_qs = Flight.objects.filter(is_active=True).select_related('origin', 'destination', 'airline')
    if category and category != 'ALL':
        flights_qs = flights_qs.filter(destination__category=category)

    matching = []
    seen_routes = set()
    for fl in flights_qs[:100]:
        pricing = compute_dynamic_fare(fl)
        curr_fare = pricing['current_fare_before_tax']
        disc_fare = round(curr_fare * (1.0 - (discount_pct / 100.0)), 2)
        
        if min_budget <= disc_fare <= max_budget:
            route_key = f"{fl.origin.code}-{fl.destination.code}"
            if route_key not in seen_routes:
                seen_routes.add(route_key)
                matching.append({
                    'flight_id': fl.id,
                    'flight_number': fl.flight_number,
                    'origin': fl.origin.code,
                    'origin_city': fl.origin.city,
                    'destination': fl.destination.code,
                    'destination_city': fl.destination.city,
                    'category': fl.destination.category,
                    'airline': fl.airline.name if fl.airline else '',
                    'current_fare': curr_fare,
                    'discounted_fare': disc_fare,
                    'available_seats': fl.available_seats,
                    'demand_factor': round(fl.demand_factor, 2)
                })

    return JsonResponse({'matches': matching[:20]})

# ----------------- BOOKING & REFUND CENTER -----------------

@require_admin_api
def api_bookings_list(request):
    """Search bookings by PNR, passenger, flight, email, route"""
    query = request.GET.get('q', '').strip()
    status = request.GET.get('status', '').strip()
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 25))

    qs = Booking.objects.select_related('flight', 'flight__origin', 'flight__destination', 'flight__airline', 'passenger', 'user').all().order_by('-created_at')

    if query:
        qs = qs.filter(
            Q(pnr__icontains=query) |
            Q(ticket_number__icontains=query) |
            Q(flight__flight_number__icontains=query) |
            Q(passenger__first_name__icontains=query) |
            Q(passenger__last_name__icontains=query) |
            Q(passenger__email__icontains=query) |
            Q(user__username__icontains=query)
        )
    if status:
        qs = qs.filter(status=status)

    total = qs.count()
    items = qs[(page - 1) * page_size : page * page_size]

    bookings = []
    for b in items:
        pax_name = f"{b.passenger.first_name} {b.passenger.last_name}" if b.passenger else (b.user.username if b.user else "Passenger")
        pax_email = b.passenger.email if b.passenger else (b.user.email if b.user else "")
        bookings.append({
            'id': b.id,
            'pnr': b.pnr,
            'ticket_number': b.ticket_number or 'FE-GEN',
            'passenger_name': pax_name,
            'passenger_email': pax_email,
            'flight_number': b.flight.flight_number,
            'route': f"{b.flight.origin.code} → {b.flight.destination.code}",
            'seat_number': b.seat_number or '12A',
            'original_fare': float(b.original_fare or b.price_paid or 0),
            'discount_amount': float(b.discount_amount),
            'price_paid': float(b.price_paid or 0),
            'status': b.status,
            'refund_status': b.refund_status,
            'refund_amount': float(b.refund_amount),
            'cancellation_fee': float(b.cancellation_fee),
            'created_at': b.created_at.strftime('%Y-%m-%d %H:%M')
        })

    return JsonResponse({'total': total, 'bookings': bookings})

@csrf_exempt
@require_admin_api
def api_refund_process(request, booking_id):
    """Approve or Reject refund request with real booking status synchronization"""
    if request.method != 'POST':
        return HttpResponseForbidden()
    try:
        data = json.loads(request.body)
        action = data.get('action') # 'APPROVE' or 'REJECT'
        notes = data.get('notes', '')

        booking = get_object_or_404(Booking, id=booking_id)

        if action == 'APPROVE':
            booking.refund_status = 'COMPLETED'
            booking.status = 'CANCELLED'
            booking.refund_notes = notes
            booking.save()
            log_admin_activity(request.user, "REFUND_APPROVE", "Booking", booking.id, f"Approved refund of ₹{booking.refund_amount} for PNR {booking.pnr}", request=request)
            msg = f"Refund for PNR {booking.pnr} approved and completed."
        else:
            booking.refund_status = 'REJECTED'
            booking.refund_notes = notes
            booking.save()
            log_admin_activity(request.user, "REFUND_REJECT", "Booking", booking.id, f"Rejected refund request for PNR {booking.pnr}", request=request)
            msg = f"Refund request for PNR {booking.pnr} rejected."

        return JsonResponse({'success': True, 'message': msg, 'refund_status': booking.refund_status})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

# ----------------- USER MANAGEMENT -----------------

@require_admin_api
def api_users_list(request):
    """View registered users, trip metrics, spending, and status"""
    users = User.objects.all().annotate(
        booking_count=Count('bookings'),
        total_spent=Sum('bookings__price_paid')
    ).order_by('-date_joined')

    data = []
    for u in users:
        data.append({
            'id': u.id,
            'username': u.username,
            'email': u.email,
            'is_staff': u.is_staff,
            'is_active': u.is_active,
            'date_joined': u.date_joined.strftime('%Y-%m-%d'),
            'booking_count': u.booking_count,
            'total_spent': float(u.total_spent or 0.0)
        })

    return JsonResponse({'users': data})

@csrf_exempt
@require_admin_api
def api_toggle_user_status(request, user_id):
    """Enable or disable user account"""
    if request.method != 'POST':
        return HttpResponseForbidden()
    try:
        u = get_object_or_404(User, id=user_id)
        if u.is_superuser:
            return JsonResponse({'success': False, 'error': 'Cannot disable superuser account.'}, status=400)
        
        u.is_active = not u.is_active
        u.save()
        log_admin_activity(request.user, "USER_STATUS_CHANGE", "User", u.id, f"Changed active status of user {u.username} to {u.is_active}", request=request)
        return JsonResponse({'success': True, 'is_active': u.is_active, 'message': f"User {u.username} status updated."})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

# ----------------- ALERTS & ACTIVITY LOGS -----------------

@require_admin_api
def api_alerts_list(request):
    alerts = AdminAlert.objects.all().order_by('-created_at')[:30]
    data = [{
        'id': a.id,
        'level': a.alert_level,
        'title': a.title,
        'message': a.message,
        'action_recommended': a.action_recommended,
        'is_read': a.is_read,
        'created_at': a.created_at.strftime('%Y-%m-%d %H:%M')
    } for a in alerts]
    return JsonResponse({'alerts': data})

@require_admin_api
def api_activity_logs_list(request):
    logs = AdminActivityLog.objects.select_related('user').all().order_by('-created_at')[:50]
    data = [{
        'id': l.id,
        'user': l.user.username if l.user else 'System',
        'action_type': l.action_type,
        'entity_type': l.entity_type,
        'description': l.description,
        'prev_val': l.previous_value,
        'new_val': l.new_value,
        'time': l.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        'ip': l.ip_address or '127.0.0.1'
    } for l in logs]
    return JsonResponse({'logs': data})

# ----------------- AIRLINE FLEET MANAGEMENT APIs -----------------

@require_admin_api
def api_airlines_list(request):
    """Retrieve full partner airlines fleet"""
    airlines = Airline.objects.all().order_by('name')
    data = [{
        'id': a.id,
        'name': a.name,
        'code': a.code,
        'logo_url': a.logo_url or f"https://images.kiwi.com/airlines/64/{a.code}.png",
        'fleet_size': a.fleet_size,
        'cabin_classes': a.cabin_classes,
        'baggage_policy': a.baggage_policy,
        'contact_email': a.contact_email,
        'contact_phone': a.contact_phone,
        'is_active': a.is_active
    } for a in airlines]
    return JsonResponse({'airlines': data})

@csrf_exempt
@require_admin_api
def api_airline_save(request):
    """Add new airline or edit existing airline fleet details"""
    if request.method != 'POST':
        return HttpResponseForbidden()
    try:
        data = json.loads(request.body)
        airline_id = data.get('id')
        code = data.get('code', '').strip().upper()
        name = data.get('name', '').strip()
        fleet_size = int(data.get('fleet_size', 50))
        cabin_classes = data.get('cabin_classes', 'Economy, Premium Economy, Business')
        baggage_policy = data.get('baggage_policy', 'Cabin: 7kg | Check-in: 15kg')
        contact_email = data.get('contact_email', 'support@airline.com')
        contact_phone = data.get('contact_phone', '+91 1800-102-3456')
        logo_url = data.get('logo_url', '').strip() or f"https://images.kiwi.com/airlines/64/{code}.png"
        is_active = data.get('is_active', True)

        if airline_id:
            airline = Airline.objects.get(id=airline_id)
            airline.name = name
            airline.code = code
            airline.logo_url = logo_url
            airline.fleet_size = fleet_size
            airline.cabin_classes = cabin_classes
            airline.baggage_policy = baggage_policy
            airline.contact_email = contact_email
            airline.contact_phone = contact_phone
            airline.is_active = is_active
            airline.save()
            log_admin_activity(request.user, "AIRLINE_UPDATE", "Airline", airline.id, f"Updated airline {airline.name} ({airline.code})", request=request)
        else:
            if Airline.objects.filter(code=code).exists():
                return JsonResponse({'success': False, 'error': f"Airline code {code} already exists."}, status=400)
            airline = Airline.objects.create(
                name=name,
                code=code,
                logo_url=logo_url,
                fleet_size=fleet_size,
                cabin_classes=cabin_classes,
                baggage_policy=baggage_policy,
                contact_email=contact_email,
                contact_phone=contact_phone,
                is_active=is_active
            )
            log_admin_activity(request.user, "AIRLINE_CREATE", "Airline", airline.id, f"Added new partner airline {airline.name} ({airline.code})", request=request)

        return JsonResponse({'success': True, 'message': f"Airline {airline.name} saved successfully.", 'airline_id': airline.id})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


# ----------------- ADMIN SYSTEM MONITOR & TRAVEL REQUIREMENTS -----------------

@user_passes_test(is_admin_user, login_url='/admin-portal/login/')
def admin_system_monitor_page(request):
    return render(request, 'admin/admin_system_monitor.html', {'active_tab': 'system_monitor', 'user': request.user})

@user_passes_test(is_admin_user, login_url='/admin-portal/login/')
def admin_requirements_page(request):
    return render(request, 'admin/admin_requirements.html', {'active_tab': 'requirements', 'user': request.user})

@require_admin_api
def api_system_health_live(request):
    from .system_monitor import perform_system_health_checks
    health = perform_system_health_checks()
    return JsonResponse({'health': health, 'timestamp': timezone.now().strftime("%Y-%m-%d %H:%M:%S")})

@require_admin_api
def api_requirements_list(request):
    from .travel_requirements import seed_travel_requirements
    if not TravelRequirement.objects.exists():
        seed_travel_requirements()

    reqs = TravelRequirement.objects.all().order_by('destination_country')
    data = [{
        'id': r.id,
        'origin_country': r.origin_country,
        'destination_country': r.destination_country,
        'visa_required': r.visa_required,
        'visa_type': r.visa_type,
        'passport_validity': r.passport_validity,
        'documents_required': r.documents_required,
        'entry_requirements': r.entry_requirements,
        'transit_requirements': r.transit_requirements,
        'important_notes': r.important_notes,
        'official_source_url': r.official_source_url,
        'is_active': r.is_active,
        'last_updated': r.last_updated.strftime("%Y-%m-%d %H:%M")
    } for r in reqs]
    return JsonResponse({'requirements': data})

@csrf_exempt
@require_admin_api
def api_requirement_save(request):
    if request.method != 'POST':
        return HttpResponseForbidden()
    try:
        data = json.loads(request.body)
        req_id = data.get('id')
        dest = data.get('destination_country', '').strip()
        orig = data.get('origin_country', 'India').strip()

        if req_id:
            req = TravelRequirement.objects.get(id=req_id)
        else:
            req = TravelRequirement(origin_country=orig, destination_country=dest)

        req.origin_country = orig
        req.destination_country = dest
        req.visa_required = data.get('visa_required', 'Required')
        req.visa_type = data.get('visa_type', 'Tourist Visa')
        req.passport_validity = data.get('passport_validity', '6 months')
        req.documents_required = data.get('documents_required', '')
        req.entry_requirements = data.get('entry_requirements', '')
        req.transit_requirements = data.get('transit_requirements', '')
        req.important_notes = data.get('important_notes', 'Requirements may change. Verify with official sources.')
        req.official_source_url = data.get('official_source_url', 'https://www.iatatravelcentre.com/')
        req.is_active = data.get('is_active', True)
        req.save()

        log_admin_activity(request.user, "AIRPORT_MODIFY", "TravelRequirement", req.id, f"Updated travel requirements for {orig} -> {dest}", request=request)
        return JsonResponse({'success': True, 'message': f"Travel requirement for {dest} saved successfully."})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

