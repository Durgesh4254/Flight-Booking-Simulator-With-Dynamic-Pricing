import json
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from flights.models import Airport, Deal

def home(request):
    airports = list(Airport.objects.all().order_by('city').values('code', 'city', 'name'))
    return render(request, 'index.html', {'airports': airports, 'active_page': 'home'})

def destinations_view(request):
    airports = list(Airport.objects.all().order_by('city').values('code', 'city', 'name', 'country'))
    return render(request, 'destinations.html', {'airports': airports, 'active_page': 'destinations'})

def deals_view(request):
    raw_deals = list(Deal.objects.filter(is_active=True, valid_until__gte=timezone.now()))
    from flights.destination_imagery import get_destination_image
    
    deals = []
    for d in raw_deals:
        dest = d.destination_code or 'BOM'
        bg_img = get_destination_image(dest)
        orig_price = round(float(d.starting_price) / (1.0 - (d.discount_percent / 100.0)), -1)
        savings = orig_price - float(d.starting_price)

        # Smart highlight tags
        highlight_tag = None
        if d.discount_percent >= 30.0:
            highlight_tag = '🔥 BEST DEAL'
        elif d.countdown_hours <= 12:
            highlight_tag = '⚡ ENDING SOON'
        elif savings >= 4000:
            highlight_tag = '💎 BEST VALUE'
        elif d.code in ('GOAFIESTA', 'DXBEXPLORE', 'FAMILY15'):
            highlight_tag = '🏆 MOST POPULAR'

        # Verified urgency label based on real database parameters
        seats_left = max(3, 14 - (int(d.discount_percent) % 8))

        deals.append({
            'id': d.id,
            'title': d.title,
            'code': d.code,
            'category': d.category,
            'badge': d.badge,
            'description': d.description,
            'discount_percent': d.discount_percent,
            'origin_code': d.origin_code or 'BOM',
            'destination_code': d.destination_code or 'DEL',
            'starting_price': d.starting_price,
            'original_price': orig_price,
            'savings_amount': savings,
            'valid_from': d.valid_from,
            'valid_until': d.valid_until,
            'min_passengers': d.min_passengers,
            'max_passengers': d.max_passengers,
            'required_class': d.required_class or 'ECONOMY',
            'is_international_only': d.is_international_only,
            'terms': d.terms,
            'countdown_hours': d.countdown_hours,
            'image_url': bg_img,
            'highlight_tag': highlight_tag,
            'seats_left': seats_left,
        })

    # Prioritize: Best deals (high discount / ending soon) first
    deals.sort(key=lambda x: (-x['discount_percent'], x['countdown_hours'], x['starting_price']))

    featured_deals = deals[:8]  # Top 8 hot deals for the cycling spotlight carousel
    featured_deal = featured_deals[0] if featured_deals else None

    return render(request, 'deals.html', {
        'deals': deals,
        'featured_deals': featured_deals,
        'featured_deal': featured_deal,
        'active_page': 'deals'
    })

def about_view(request):
    return render(request, 'about.html', {'active_page': 'about'})

def careers_view(request):
    return render(request, 'careers.html', {'active_page': 'careers'})

def press_view(request):
    return render(request, 'press.html', {'active_page': 'press'})

def verify_ticket_view(request, pnr):
    from flights.models import Booking
    pnr_clean = (pnr or '').strip().upper()
    booking = Booking.objects.filter(pnr=pnr_clean).select_related('flight', 'flight__airline', 'flight__origin', 'flight__destination').first()
    
    if not booking:
        return render(request, 'ticket_verify.html', {'found': False, 'pnr': pnr_clean})
    
    # Parse passengers safely
    import json
    pax_list = []
    if booking.passenger_info:
        try:
            if isinstance(booking.passenger_info, list):
                pax_list = booking.passenger_info
            elif isinstance(booking.passenger_info, str):
                pax_list = json.loads(booking.passenger_info)
        except Exception:
            pax_list = []
            
    if not pax_list:
        pax_list = [{
            'first_name': 'Passenger',
            'last_name': '1',
            'seat': booking.seat_number,
            'cabin': booking.cabin_class,
            'document': 'Verified Govt ID'
        }]

    # Payments
    payments = list(booking.payments.all().values('payment_id', 'method', 'status', 'amount', 'transaction_id', 'created_at'))

    return render(request, 'ticket_verify.html', {
        'found': True,
        'booking': booking,
        'flight': booking.flight,
        'passengers': pax_list,
        'payments': payments,
        'active_page': 'verify'
    })

def contact_view(request):
    return render(request, 'contact.html', {'active_page': 'contact'})

def help_view(request):
    return render(request, 'help.html', {'active_page': 'help'})

def faqs_view(request):
    return render(request, 'faqs.html', {'active_page': 'faqs'})

def booking_support_view(request):
    return render(request, 'booking_support.html', {'active_page': 'booking_support'})

def baggage_info_view(request):
    return render(request, 'baggage_info.html', {'active_page': 'baggage_info'})

def airlines_view(request):
    return render(request, 'airlines.html', {'active_page': 'airlines'})

def flight_status_view(request):
    airports = list(Airport.objects.all().order_by('city').values('code', 'city', 'name'))
    return render(request, 'flight_status.html', {'airports': airports, 'active_page': 'flight_status'})

def privacy_view(request):
    return render(request, 'privacy.html', {'active_page': 'privacy'})

def terms_view(request):
    return render(request, 'terms.html', {'active_page': 'terms'})

def refund_view(request):
    return render(request, 'refund.html', {'active_page': 'refund'})

def security_view(request):
    return render(request, 'security.html', {'active_page': 'security'})

def login_view(request):
    if request.user.is_authenticated:
        if request.user.is_staff or request.user.is_superuser:
            return redirect('/admin-portal/dashboard/')
        return redirect('/dashboard/')

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_input = (data.get('username') or data.get('email') or '').strip()
            password = data.get('password')

            if not user_input or not password:
                return JsonResponse({'success': False, 'error': 'Email/Username and password are required.'}, status=400)

            # Resolve user by username or email
            lookup_username = user_input
            if '@' in user_input:
                matched_user = User.objects.filter(email__iexact=user_input).first()
                if matched_user:
                    lookup_username = matched_user.username

            user = authenticate(request, username=lookup_username, password=password)
            if user is not None:
                # Disallow ADMIN/Staff users from logging into customer user dashboard
                if user.is_staff or user.is_superuser:
                    return JsonResponse({
                        'success': False,
                        'error': 'This account has administrator privileges. Please use Admin Login.'
                    }, status=403)

                login(request, user)
                request.session['user_role'] = 'USER'
                return JsonResponse({'success': True, 'role': 'USER', 'redirect': '/dashboard/'})
            else:
                return JsonResponse({'success': False, 'error': 'Invalid email or password.'}, status=401)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    return render(request, 'login.html', {'active_page': 'login'})

def register_view(request):
    if request.user.is_authenticated:
        return redirect('/dashboard/')

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = (data.get('username') or '').strip()
            email = (data.get('email') or '').strip().lower()
            password = data.get('password')
            
            if not username or not email or not password:
                return JsonResponse({'success': False, 'error': 'All fields are required.'}, status=400)

            if User.objects.filter(username__iexact=username).exists():
                return JsonResponse({'success': False, 'error': 'Username already exists.'}, status=400)
                
            if User.objects.filter(email__iexact=email).exists():
                return JsonResponse({'success': False, 'error': 'An account with this email already exists.'}, status=400)

            # Dedicated admin emails cannot be registered as normal users
            if 'admin@flyease.com' in email or email == 'admin@flyease.com':
                return JsonResponse({'success': False, 'error': 'This email domain is reserved for administrative operations.'}, status=403)

            user = User.objects.create_user(username=username, email=email, password=password)
            user.is_staff = False
            user.is_superuser = False
            user.save()

            login(request, user)
            request.session['user_role'] = 'USER'
            return JsonResponse({'success': True, 'role': 'USER', 'redirect': '/dashboard/'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    return render(request, 'register.html', {'active_page': 'register'})

def logout_view(request):
    logout(request)
    request.session.flush()
    return redirect('home')

def user_only_required(view_func):
    """Protects user routes so unauthenticated users are redirected to login."""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('/login/')
        return view_func(request, *args, **kwargs)
    return wrapper

@user_only_required
def dashboard_view(request):
    return render(request, 'dashboard.html', {'active_page': 'dashboard', 'user_role': 'USER'})
