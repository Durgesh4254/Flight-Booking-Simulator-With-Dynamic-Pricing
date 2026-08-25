import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flight_simulator.settings')
try:
    from django.apps import apps
    if not apps.ready:
        django.setup()
except Exception:
    django.setup()

from django.utils import timezone
from django.db import transaction
from datetime import timedelta, datetime
import decimal
import random

from django.db import connection
from django.contrib.auth.models import User
from flights.models import (
    Airline, Airport, Aircraft, Flight, Seat, Coupon, Deal,
    PricingRule, AdminActivityLog, AdminAlert, Passenger, Booking, Payment
)
from flights.destinations_dataset import DESTINATIONS_DATA
from flights.flight_generator import AIRPORT_COORDS, create_dynamic_schedule_flights

@transaction.atomic
def seed():
    print("Clearing old data...")
    with connection.cursor() as cursor:
        if connection.vendor == 'sqlite':
            cursor.execute("PRAGMA foreign_keys = OFF;")
        cursor.execute("DELETE FROM flights_bookingpassenger;")
        cursor.execute("DELETE FROM flights_payment;")
        cursor.execute("DELETE FROM flights_adminalert;")
        cursor.execute("DELETE FROM flights_pricealert;")
        cursor.execute("DELETE FROM flights_farehistory;")
        cursor.execute("DELETE FROM flights_adminactivitylog;")
        cursor.execute("DELETE FROM flights_review;")
        cursor.execute("DELETE FROM flights_booking;")
        cursor.execute("DELETE FROM flights_seat;")
        cursor.execute("DELETE FROM flights_flight;")
        cursor.execute("DELETE FROM flights_passenger;")
        cursor.execute("DELETE FROM flights_pricingrule;")
        cursor.execute("DELETE FROM flights_deal;")
        cursor.execute("DELETE FROM flights_coupon;")
        cursor.execute("DELETE FROM flights_aircraft;")
        cursor.execute("DELETE FROM flights_airport;")
        cursor.execute("DELETE FROM flights_airline;")
        cursor.execute("DELETE FROM flights_travelrequirement;")
        cursor.execute("DELETE FROM flights_servicehealthlog;")
        if connection.vendor == 'sqlite':
            cursor.execute("PRAGMA foreign_keys = ON;")

    print("Ensuring Admin User...")
    admin_user, created = User.objects.get_or_create(username='admin', defaults={'email': 'admin@flyease.com', 'is_staff': True, 'is_superuser': True})
    admin_user.set_password('admin123')
    admin_user.is_staff = True
    admin_user.is_superuser = True
    admin_user.save()
    print("Superuser/Admin configured: admin / admin123")

    print("Creating Default Dynamic Pricing Rule...")
    PricingRule.objects.create(
        name="Global Aviation Dynamic Pricing Algorithm",
        is_active=True,
        min_fare_floor=decimal.Decimal('1800.00'),
        max_fare_cap=decimal.Decimal('65000.00'),
        demand_multiplier_weight=1.15,
        seat_availability_weight=1.25,
        time_to_departure_weight=1.20,
        peak_season_multiplier=1.20,
        weekend_multiplier=1.15,
        holiday_multiplier=1.25,
        created_by=admin_user
    )

    print("Creating Airlines Fleet...")
    airlines_data = [
        {'name': 'IndiGo', 'code': '6E', 'logo_url': 'https://images.kiwi.com/airlines/64/6E.png', 'fleet_size': 360, 'cabin_classes': 'Economy'},
        {'name': 'Air India', 'code': 'AI', 'logo_url': 'https://images.kiwi.com/airlines/64/AI.png', 'fleet_size': 140, 'cabin_classes': 'Economy, Premium Economy, Business, First'},
        {'name': 'Vistara', 'code': 'UK', 'logo_url': 'https://images.kiwi.com/airlines/64/UK.png', 'fleet_size': 70, 'cabin_classes': 'Economy, Premium Economy, Business'},
        {'name': 'Emirates', 'code': 'EK', 'logo_url': 'https://images.kiwi.com/airlines/64/EK.png', 'fleet_size': 260, 'cabin_classes': 'Economy, Premium Economy, Business, First'},
        {'name': 'SpiceJet', 'code': 'SG', 'logo_url': 'https://images.kiwi.com/airlines/64/SG.png', 'fleet_size': 58, 'cabin_classes': 'Economy'},
        {'name': 'Akasa Air', 'code': 'QP', 'logo_url': 'https://images.kiwi.com/airlines/64/QP.png', 'fleet_size': 24, 'cabin_classes': 'Economy'},
        {'name': 'Singapore Airlines', 'code': 'SQ', 'logo_url': 'https://images.kiwi.com/airlines/64/SQ.png', 'fleet_size': 150, 'cabin_classes': 'Economy, Premium Economy, Business, First'},
        {'name': 'British Airways', 'code': 'BA', 'logo_url': 'https://images.kiwi.com/airlines/64/BA.png', 'fleet_size': 280, 'cabin_classes': 'Economy, Premium Economy, Business, First'},
        {'name': 'Lufthansa', 'code': 'LH', 'logo_url': 'https://images.kiwi.com/airlines/64/LH.png', 'fleet_size': 310, 'cabin_classes': 'Economy, Premium Economy, Business, First'},
        {'name': 'Qatar Airways', 'code': 'QR', 'logo_url': 'https://images.kiwi.com/airlines/64/QR.png', 'fleet_size': 250, 'cabin_classes': 'Economy, Business, First'},
        {'name': 'Etihad Airways', 'code': 'EY', 'logo_url': 'https://images.kiwi.com/airlines/64/EY.png', 'fleet_size': 90, 'cabin_classes': 'Economy, Business, First'},
        {'name': 'Thai Airways', 'code': 'TG', 'logo_url': 'https://images.kiwi.com/airlines/64/TG.png', 'fleet_size': 75, 'cabin_classes': 'Economy, Premium Economy, Business'},
    ]
    airlines = {a['code']: Airline.objects.create(**a) for a in airlines_data}

    print("Creating Expanded Global Airport Database (200-300+ destinations)...")
    airports_to_create = []
    for d in DESTINATIONS_DATA:
        airports_to_create.append(Airport(
            code=d['code'],
            icao_code=d.get('icao', ''),
            name=d['name'],
            city=d['city'],
            country=d['country'],
            country_code=d.get('country_code', 'IN'),
            region=d.get('region', 'Global'),
            terminal=d.get('terminal', 'T1'),
            timezone=d.get('timezone', 'UTC+00:00'),
            is_international=d.get('is_international', False),
            latitude=d.get('lat', 20.0),
            longitude=d.get('lon', 77.0),
            popularity=d.get('popularity', 80),
            category=d.get('category', 'CITY'),
            avg_fare=decimal.Decimal(str(d.get('avg_fare', 4500))),
            best_season=d.get('best_season', 'Oct - Mar'),
            is_active=True
        ))
    Airport.objects.bulk_create(airports_to_create)
    print(f"Created {len(airports_to_create)} global and domestic airports.")

    print("Creating Aircraft Fleet...")
    aircraft_data = [
        {'model_name': 'Airbus A320neo', 'manufacturer': 'Airbus', 'economy_seats': 150, 'business_seats': 16, 'first_class_seats': 8},
        {'model_name': 'Boeing 777-300ER', 'manufacturer': 'Boeing', 'economy_seats': 228, 'business_seats': 40, 'first_class_seats': 12},
        {'model_name': 'Boeing 737 MAX 8', 'manufacturer': 'Boeing', 'economy_seats': 144, 'business_seats': 16, 'first_class_seats': 6},
        {'model_name': 'Airbus A321neo', 'manufacturer': 'Airbus', 'economy_seats': 174, 'business_seats': 24, 'first_class_seats': 8},
        {'model_name': 'Airbus A380-800', 'manufacturer': 'Airbus', 'economy_seats': 360, 'business_seats': 64, 'first_class_seats': 16},
        {'model_name': 'Boeing 787-9 Dreamliner', 'manufacturer': 'Boeing', 'economy_seats': 210, 'business_seats': 32, 'first_class_seats': 10},
    ]
    for a in aircraft_data:
        Aircraft.objects.create(**a)

    print("Generating scheduled flights for popular domestic and global routes...")
    base_date = timezone.now().date()
    
    # Pre-generate schedules for the next 14 days for top busy routes
    top_routes = [
        ('BOM', 'DEL'), ('DEL', 'BOM'),
        ('BOM', 'BLR'), ('BLR', 'BOM'),
        ('BOM', 'CCU'), ('CCU', 'BOM'),
        ('DEL', 'BLR'), ('BLR', 'DEL'),
        ('BOM', 'HYD'), ('HYD', 'BOM'),
        ('DEL', 'HYD'), ('HYD', 'DEL'),
        ('BOM', 'MAA'), ('MAA', 'BOM'),
        ('DEL', 'CCU'), ('CCU', 'DEL'),
        ('BOM', 'GOI'), ('GOI', 'BOM'),
        ('DEL', 'GOI'), ('GOI', 'DEL'),
        ('BOM', 'PNQ'), ('PNQ', 'DEL'),
        ('BOM', 'LHR'), ('LHR', 'BOM'),
        ('DEL', 'LHR'), ('LHR', 'DEL'),
        ('BOM', 'DXB'), ('DXB', 'BOM'),
        ('DEL', 'DXB'), ('DXB', 'DEL'),
        ('BLR', 'SIN'), ('SIN', 'BLR'),
        ('BOM', 'SIN'), ('SIN', 'BOM'),
        ('MAA', 'SIN'), ('SIN', 'MAA'),
        ('HYD', 'DXB'), ('DXB', 'HYD'),
        ('DEL', 'JFK'), ('JFK', 'DEL'),
        ('BOM', 'CDG'), ('CDG', 'BOM'),
        ('DEL', 'FRA'), ('FRA', 'DEL'),
        ('BOM', 'BKK'), ('BKK', 'BOM'),
        ('DEL', 'DOH'), ('DOH', 'DEL'),
        ('BOM', 'HND'), ('HND', 'BOM'),
    ]

    total_generated = 0
    for day_offset in range(0, 14):
        target_d = base_date + timedelta(days=day_offset)
        for orig, dest in top_routes:
            flights = create_dynamic_schedule_flights(orig, dest, target_d)
            total_generated += len(flights)

    print(f"Pre-seeded {total_generated} flights across top routes for the next 14 days.")

    print("Creating Deals and Coupons...")
    now = timezone.now()
    one_year_later = now + timedelta(days=365)

    # Standard Coupons
    Coupon.objects.create(code='FLYEASE10', discount_percent=10.0, is_active=True, valid_until=one_year_later)
    Coupon.objects.create(code='FIRSTFLY20', discount_percent=20.0, is_active=True, valid_until=one_year_later)
    Coupon.objects.create(code='FLAT500', discount_amount=decimal.Decimal('500.00'), is_active=True, valid_until=one_year_later)

    # Deals matching requirements (20 High-Value, Diverse Deals)
    deals_data = [
        {
            'title': 'Family Travel Special',
            'code': 'FAMILY15',
            'category': 'FAMILY',
            'badge': '👨‍👩‍👧 Family Offer - 15% OFF',
            'description': 'Enjoy special savings when flying together with family. Min 2 passengers, max 6 passengers.',
            'discount_percent': 15.0,
            'origin_code': '',
            'destination_code': '',
            'starting_price': decimal.Decimal('2800.00'),
            'valid_from': now,
            'valid_until': one_year_later,
            'is_active': True,
            'min_passengers': 2,
            'max_passengers': 6,
            'required_class': '',
            'is_international_only': False,
            'terms': 'Valid for 2 to 6 passengers on any domestic or international route. Cannot be combined with other promo codes.',
            'countdown_hours': 36
        },
        {
            'title': 'Weekend Getaway Deal',
            'code': 'WEEKEND20',
            'category': 'WEEKEND',
            'badge': '🔥 Weekend Deal - 20% OFF',
            'description': 'Special weekend escape discounts for quick domestic breaks and spontaneous vacations.',
            'discount_percent': 20.0,
            'origin_code': 'BOM',
            'destination_code': 'BLR',
            'starting_price': decimal.Decimal('2400.00'),
            'valid_from': now,
            'valid_until': one_year_later,
            'is_active': True,
            'min_passengers': 1,
            'max_passengers': 9,
            'required_class': '',
            'is_international_only': False,
            'terms': 'Valid on BOM-BLR flights. Limited seats available on discounted fares.',
            'countdown_hours': 14
        },
        {
            'title': 'Global Explorer Discount',
            'code': 'GLOBAL12',
            'category': 'INTERNATIONAL',
            'badge': '🌎 International Offer - 12% OFF',
            'description': 'Explore top global destinations including Dubai, London, Singapore and Paris at unbelievable fares.',
            'discount_percent': 12.0,
            'origin_code': '',
            'destination_code': '',
            'starting_price': decimal.Decimal('11000.00'),
            'valid_from': now,
            'valid_until': one_year_later,
            'is_active': True,
            'min_passengers': 1,
            'max_passengers': 9,
            'required_class': '',
            'is_international_only': True,
            'terms': 'Valid on all international flights to DXB, LHR, SIN, CDG, JFK. Valid passport required for boarding.',
            'countdown_hours': 48
        },
        {
            'title': 'Business Class Luxury Upgrade',
            'code': 'BIZ10',
            'category': 'BUSINESS',
            'badge': '💎 Business Class Deal - 10% OFF',
            'description': 'Fly in comfort with lie-flat seats, gourmet dining, priority boarding and extra baggage.',
            'discount_percent': 10.0,
            'origin_code': '',
            'destination_code': '',
            'starting_price': decimal.Decimal('14500.00'),
            'valid_from': now,
            'valid_until': one_year_later,
            'is_active': True,
            'min_passengers': 1,
            'max_passengers': 4,
            'required_class': 'BUSINESS',
            'is_international_only': False,
            'terms': 'Applicable only when Business class cabin is selected. Includes lounge access and extra baggage.',
            'countdown_hours': 72
        },
        {
            'title': 'Student Flying Advantage',
            'code': 'STUDENT10',
            'category': 'STUDENT',
            'badge': '🎓 Student Offer - 10% OFF',
            'description': 'Special discounted rates and extra baggage allowances for students traveling for studies.',
            'discount_percent': 10.0,
            'origin_code': '',
            'destination_code': '',
            'starting_price': decimal.Decimal('2200.00'),
            'valid_from': now,
            'valid_until': one_year_later,
            'is_active': True,
            'min_passengers': 1,
            'max_passengers': 2,
            'required_class': 'ECONOMY',
            'is_international_only': False,
            'terms': 'Valid student ID must be presented at airport check-in counter.',
            'countdown_hours': 24
        },
        {
            'title': 'Flash Last-Minute Saver',
            'code': 'LASTMIN25',
            'category': 'LASTMINUTE',
            'badge': '⚡ Last-Minute Deal - 25% OFF',
            'description': 'Grab unsold seats on flights departing within the next 48 hours at rock-bottom prices.',
            'discount_percent': 25.0,
            'origin_code': 'DEL',
            'destination_code': 'BOM',
            'starting_price': decimal.Decimal('3200.00'),
            'valid_from': now,
            'valid_until': one_year_later,
            'is_active': True,
            'min_passengers': 1,
            'max_passengers': 4,
            'required_class': '',
            'is_international_only': False,
            'terms': 'Valid on DEL-BOM departures. Non-refundable and non-changeable fare.',
            'countdown_hours': 8
        },
        {
            'title': 'Metro Express Saver',
            'code': 'METRO15',
            'category': 'DOMESTIC',
            'badge': '✈️ Domestic Offer - 15% OFF',
            'description': 'Heavy discounts between top metro routes connecting Mumbai, Delhi, Bangalore and Hyderabad.',
            'discount_percent': 15.0,
            'origin_code': 'BOM',
            'destination_code': 'DEL',
            'starting_price': decimal.Decimal('3800.00'),
            'valid_from': now,
            'valid_until': one_year_later,
            'is_active': True,
            'min_passengers': 1,
            'max_passengers': 9,
            'required_class': '',
            'is_international_only': False,
            'terms': 'Valid across all major domestic metro connections.',
            'countdown_hours': 28
        },
        {
            'title': 'Goa Beach Party Express',
            'code': 'GOAFIESTA',
            'category': 'WEEKEND',
            'badge': '🏖️ Goa Special - 18% OFF',
            'description': 'Escape to the golden sands, sunset cruises, and beach shacks of Goa with flat 18% savings.',
            'discount_percent': 18.0,
            'origin_code': 'BOM',
            'destination_code': 'GOI',
            'starting_price': decimal.Decimal('2199.00'),
            'valid_from': now,
            'valid_until': one_year_later,
            'is_active': True,
            'min_passengers': 1,
            'max_passengers': 6,
            'required_class': '',
            'is_international_only': False,
            'terms': 'Valid on all inbound flights to Goa (GOI). Subject to seat availability.',
            'countdown_hours': 19
        },
        {
            'title': 'Dubai Shopping & Skyline Escape',
            'code': 'DXBEXPLORE',
            'category': 'INTERNATIONAL',
            'badge': '🏙️ Dubai Mega Deal - 15% OFF',
            'description': 'Witness Burj Khalifa, desert safaris, and luxury malls with direct airline partner discounts.',
            'discount_percent': 15.0,
            'origin_code': 'BOM',
            'destination_code': 'DXB',
            'starting_price': decimal.Decimal('10999.00'),
            'valid_from': now,
            'valid_until': one_year_later,
            'is_active': True,
            'min_passengers': 1,
            'max_passengers': 8,
            'required_class': '',
            'is_international_only': True,
            'terms': 'Valid on Emirates, Air India, and IndiGo flights to Dubai (DXB). Visa assistance included.',
            'countdown_hours': 42
        },
        {
            'title': 'Singapore Lion City Getaway',
            'code': 'SINGASAVER',
            'category': 'INTERNATIONAL',
            'badge': '🦁 Singapore Deal - 14% OFF',
            'description': 'Explore Gardens by the Bay, Marina Bay Sands, and Universal Studios with special companion discounts.',
            'discount_percent': 14.0,
            'origin_code': 'BLR',
            'destination_code': 'SIN',
            'starting_price': decimal.Decimal('13499.00'),
            'valid_from': now,
            'valid_until': one_year_later,
            'is_active': True,
            'min_passengers': 1,
            'max_passengers': 6,
            'required_class': '',
            'is_international_only': True,
            'terms': 'Valid on non-stop Singapore Airlines and Air India flights.',
            'countdown_hours': 31
        },
        {
            'title': 'Kashmir Paradise Valley Special',
            'code': 'HEAVENKASH',
            'category': 'DOMESTIC',
            'badge': '🏔️ Srinagar Offer - 16% OFF',
            'description': 'Glide on Dal Lake shikaras and explore snow-capped peaks in Gulmarg with scenic route savings.',
            'discount_percent': 16.0,
            'origin_code': 'DEL',
            'destination_code': 'SXR',
            'starting_price': decimal.Decimal('3499.00'),
            'valid_from': now,
            'valid_until': one_year_later,
            'is_active': True,
            'min_passengers': 1,
            'max_passengers': 6,
            'required_class': '',
            'is_international_only': False,
            'terms': 'Valid on DEL-SXR and BOM-SXR flights. Complimentary reschedule within 7 days.',
            'countdown_hours': 22
        },
        {
            'title': 'Honeymoon in Maldives Bliss',
            'code': 'MALDIVES20',
            'category': 'INTERNATIONAL',
            'badge': '🏝️ Maldives Romance - 20% OFF',
            'description': 'Stay in overwater villas with clear blue lagoons and romantic beachfront candlelight dinners.',
            'discount_percent': 20.0,
            'origin_code': 'COK',
            'destination_code': 'MLE',
            'starting_price': decimal.Decimal('14999.00'),
            'valid_from': now,
            'valid_until': one_year_later,
            'is_active': True,
            'min_passengers': 2,
            'max_passengers': 4,
            'required_class': '',
            'is_international_only': True,
            'terms': 'Minimum 2 adult passengers. Free 25kg checked baggage allowance included.',
            'countdown_hours': 54
        },
        {
            'title': 'London Royal Heritage Tour',
            'code': 'LONDONEASY',
            'category': 'INTERNATIONAL',
            'badge': '🇬🇧 London Special - 10% OFF',
            'description': 'Direct Dreamliner connections to Heathrow. Free British afternoon tea voucher on confirmed booking.',
            'discount_percent': 10.0,
            'origin_code': 'BOM',
            'destination_code': 'LHR',
            'starting_price': decimal.Decimal('26999.00'),
            'valid_from': now,
            'valid_until': one_year_later,
            'is_active': True,
            'min_passengers': 1,
            'max_passengers': 6,
            'required_class': '',
            'is_international_only': True,
            'terms': 'Valid on British Airways & Air India Boeing 787 flights to LHR.',
            'countdown_hours': 65
        },
        {
            'title': 'Spiritual Varanasi & Ganga Aarti',
            'code': 'HOLIKASHI',
            'category': 'DOMESTIC',
            'badge': '🪔 Holy City Offer - 22% OFF',
            'description': 'Experience serene sunrise boat rides on Ganga and evening Dashashwamedh Aarti in ancient Kashi.',
            'discount_percent': 22.0,
            'origin_code': 'DEL',
            'destination_code': 'VNS',
            'starting_price': decimal.Decimal('2299.00'),
            'valid_from': now,
            'valid_until': one_year_later,
            'is_active': True,
            'min_passengers': 1,
            'max_passengers': 8,
            'required_class': '',
            'is_international_only': False,
            'terms': 'Valid for all travelers. Special priority assistance for senior citizens available.',
            'countdown_hours': 16
        },
        {
            'title': 'First Class Suite Royal Experience',
            'code': 'ROYALSUITE',
            'category': 'BUSINESS',
            'badge': '👑 First Class - 12% OFF',
            'description': 'Private suite cabin, caviar dining, Dom Pérignon service, and luxury chauffeur airport transfers.',
            'discount_percent': 12.0,
            'origin_code': 'BOM',
            'destination_code': 'DXB',
            'starting_price': decimal.Decimal('38999.00'),
            'valid_from': now,
            'valid_until': one_year_later,
            'is_active': True,
            'min_passengers': 1,
            'max_passengers': 2,
            'required_class': 'BUSINESS',
            'is_international_only': False,
            'terms': 'Applies to Premium/Business/First class cabins. Includes free lounge access globally.',
            'countdown_hours': 80
        },
        {
            'title': 'Bangkok Tropical Street & Culture',
            'code': 'THAIDELIGHT',
            'category': 'INTERNATIONAL',
            'badge': '🍜 Bangkok Deal - 16% OFF',
            'description': 'Indulge in floating markets, grand temples, rooftop nightlife, and world-renowned Thai cuisine.',
            'discount_percent': 16.0,
            'origin_code': 'CCU',
            'destination_code': 'BKK',
            'starting_price': decimal.Decimal('11899.00'),
            'valid_from': now,
            'valid_until': one_year_later,
            'is_active': True,
            'min_passengers': 1,
            'max_passengers': 6,
            'required_class': '',
            'is_international_only': True,
            'terms': 'Valid on Thai Airways and IndiGo flights to Bangkok (BKK). Free seat selection included.',
            'countdown_hours': 26
        },
        {
            'title': 'Pink City Royal Rajasthan Holiday',
            'code': 'JAIPURROYAL',
            'category': 'DOMESTIC',
            'badge': '🏰 Jaipur Special - 15% OFF',
            'description': 'Tour magnificent Amer Fort, City Palace, and traditional Rajasthani bazaar handicrafts.',
            'discount_percent': 15.0,
            'origin_code': 'BOM',
            'destination_code': 'JAI',
            'starting_price': decimal.Decimal('2199.00'),
            'valid_from': now,
            'valid_until': one_year_later,
            'is_active': True,
            'min_passengers': 1,
            'max_passengers': 6,
            'required_class': '',
            'is_international_only': False,
            'terms': 'Valid on all routes to Jaipur (JAI). Instant booking discount applied at checkout.',
            'countdown_hours': 33
        },
        {
            'title': 'Global University Scholar Pass',
            'code': 'SCHOLAR15',
            'category': 'STUDENT',
            'badge': '📚 Student Pass - 15% OFF',
            'description': 'Extra 10kg check-in baggage + 15% off for international and interstate student relocations.',
            'discount_percent': 15.0,
            'origin_code': '',
            'destination_code': '',
            'starting_price': decimal.Decimal('2500.00'),
            'valid_from': now,
            'valid_until': one_year_later,
            'is_active': True,
            'min_passengers': 1,
            'max_passengers': 2,
            'required_class': 'ECONOMY',
            'is_international_only': False,
            'terms': 'Valid student ID or admission letter required. Includes 1 free date change.',
            'countdown_hours': 40
        },
        {
            'title': 'Golden Temple Spiritual Pilgrimage',
            'code': 'AMRITSARFLIGHT',
            'category': 'DOMESTIC',
            'badge': '✨ Amritsar - 18% OFF',
            'description': 'Direct non-stop flights to Sri Guru Ram Dass Jee International Airport with complimentary langar guidance.',
            'discount_percent': 18.0,
            'origin_code': 'DEL',
            'destination_code': 'ATQ',
            'starting_price': decimal.Decimal('2399.00'),
            'valid_from': now,
            'valid_until': one_year_later,
            'terms': 'Valid on DEL-ATQ & BOM-ATQ flights. Includes complimentary web check-in.',
            'countdown_hours': 21
        },
        {
            'title': 'Red-Eye Midnight Flash Sale',
            'code': 'MIDNIGHT30',
            'category': 'LASTMINUTE',
            'badge': '🌙 Midnight Flash - 30% OFF',
            'description': 'Save up to 30% on late-night and early-morning flights departing between 11 PM and 6 AM.',
            'discount_percent': 30.0,
            'origin_code': '',
            'destination_code': '',
            'starting_price': decimal.Decimal('1999.00'),
            'valid_from': now,
            'valid_until': one_year_later,
            'is_active': True,
            'min_passengers': 1,
            'max_passengers': 4,
            'required_class': 'ECONOMY',
            'is_international_only': False,
            'terms': 'Valid for departures between 23:00 and 06:00. Non-refundable promotional rate.',
            'countdown_hours': 6
        },
        # --- 12 NEW ATTRACTIVE DEALS ---
        {
            'title': 'Parisian Romance & Eiffel Dreams',
            'code': 'PARISAMOUR',
            'category': 'INTERNATIONAL',
            'badge': '🥐 Paris Romance - 18% OFF',
            'description': 'Stroll along the Seine, visit the Louvre Museum, and experience the dazzling Eiffel Tower illuminated at night.',
            'discount_percent': 18.0,
            'origin_code': 'BOM',
            'destination_code': 'CDG',
            'starting_price': decimal.Decimal('28999.00'),
            'valid_from': now,
            'valid_until': one_year_later,
            'is_active': True,
            'min_passengers': 1,
            'max_passengers': 4,
            'required_class': '',
            'is_international_only': True,
            'terms': 'Valid on non-stop Air France and Air India flights to Paris Charles de Gaulle (CDG).',
            'countdown_hours': 36
        },
        {
            'title': 'Tokyo Cherry Blossom Adventure',
            'code': 'TOKYOSAKURA',
            'category': 'INTERNATIONAL',
            'badge': '🌸 Tokyo Discovery - 15% OFF',
            'description': 'Explore vibrant Shibuya Crossing, Mt. Fuji day trips, and authentic Michelin ramen in buzzing Tokyo.',
            'discount_percent': 15.0,
            'origin_code': 'DEL',
            'destination_code': 'HND',
            'starting_price': decimal.Decimal('32999.00'),
            'valid_from': now,
            'valid_until': one_year_later,
            'is_active': True,
            'min_passengers': 1,
            'max_passengers': 6,
            'required_class': '',
            'is_international_only': True,
            'terms': 'Valid on ANA & Japan Airlines codeshare flights to Haneda (HND). 2 Free check-in bags included.',
            'countdown_hours': 42
        },
        {
            'title': 'Sydney Harbor & Bondi Beach Special',
            'code': 'SYDNEYDOWN',
            'category': 'INTERNATIONAL',
            'badge': '🦘 Sydney Escapes - 14% OFF',
            'description': 'Marvel at the Sydney Opera House, take coastal walks in Bondi, and visit the iconic Blue Mountains.',
            'discount_percent': 14.0,
            'origin_code': 'BOM',
            'destination_code': 'SYD',
            'starting_price': decimal.Decimal('38999.00'),
            'valid_from': now,
            'valid_until': one_year_later,
            'is_active': True,
            'min_passengers': 1,
            'max_passengers': 6,
            'required_class': '',
            'is_international_only': True,
            'terms': 'Valid on Qantas & Singapore Airlines flights to Sydney (SYD). Australian ETA visa required.',
            'countdown_hours': 52
        },
        {
            'title': 'Phuket Beach Resort Fiesta',
            'code': 'PHUKETWAVE',
            'category': 'WEEKEND',
            'badge': '🏖️ Phuket Getaway - 20% OFF',
            'description': 'Crystal clear waters at Phi Phi Islands, luxury beach clubs, and water sports with instant flight discounts.',
            'discount_percent': 20.0,
            'origin_code': 'BOM',
            'destination_code': 'HKT',
            'starting_price': decimal.Decimal('9999.00'),
            'valid_from': now,
            'valid_until': one_year_later,
            'is_active': True,
            'min_passengers': 1,
            'max_passengers': 6,
            'required_class': '',
            'is_international_only': True,
            'terms': 'Valid on non-stop flights to Phuket (HKT). Free rescheduling within 72 hours.',
            'countdown_hours': 18
        },
        {
            'title': 'Andaman Emerald Island Paradise',
            'code': 'ANDAMANISLE',
            'category': 'DOMESTIC',
            'badge': '🏝️ Port Blair - 22% OFF',
            'description': 'Scuba dive in Havelock Island crystal waters, relax at Radhanagar Beach, and explore historic Cellular Jail.',
            'discount_percent': 22.0,
            'origin_code': 'CCU',
            'destination_code': 'IXZ',
            'starting_price': decimal.Decimal('3899.00'),
            'valid_from': now,
            'valid_until': one_year_later,
            'is_active': True,
            'min_passengers': 1,
            'max_passengers': 8,
            'required_class': '',
            'is_international_only': False,
            'terms': 'Valid on CCU-IXZ and MAA-IXZ flights. Special priority boarding for families.',
            'countdown_hours': 24
        },
        {
            'title': 'Udaipur City of Lakes Royalty',
            'code': 'UDAIPURLAKE',
            'category': 'WEEKEND',
            'badge': '👑 Udaipur Luxury - 17% OFF',
            'description': 'Sunset boat cruise on Lake Pichola, luxury heritage palaces, and traditional Mewari royal hospitality.',
            'discount_percent': 17.0,
            'origin_code': 'BOM',
            'destination_code': 'UDR',
            'starting_price': decimal.Decimal('2299.00'),
            'valid_from': now,
            'valid_until': one_year_later,
            'is_active': True,
            'min_passengers': 1,
            'max_passengers': 6,
            'required_class': '',
            'is_international_only': False,
            'terms': 'Valid on BOM-UDR & DEL-UDR flights. Complimentary heritage guide on booking confirmation.',
            'countdown_hours': 15
        },
        {
            'title': 'Dehradun & Rishikesh Yoga Retreat',
            'code': 'RISHIYOGA',
            'category': 'DOMESTIC',
            'badge': '🧘 Rishikesh Soul - 18% OFF',
            'description': 'Fly directly into Jolly Grant Airport for serene Himalayan retreats, river rafting, and evening Ganga arti.',
            'discount_percent': 18.0,
            'origin_code': 'DEL',
            'destination_code': 'DED',
            'starting_price': decimal.Decimal('1899.00'),
            'valid_from': now,
            'valid_until': one_year_later,
            'is_active': True,
            'min_passengers': 1,
            'max_passengers': 6,
            'required_class': '',
            'is_international_only': False,
            'terms': 'Valid on DEL-DED direct express flights. Includes 1 free carry-on yoga mat bag.',
            'countdown_hours': 11
        },
        {
            'title': 'Darjeeling Tea & Toy Train Excursion',
            'code': 'BAGDOGRATEA',
            'category': 'FAMILY',
            'badge': '🫖 Bagdogra Special - 20% OFF',
            'description': 'Gateway to misty Darjeeling hills, panoramic Kanchenjunga sunrises, and aromatic organic tea gardens.',
            'discount_percent': 20.0,
            'origin_code': 'CCU',
            'destination_code': 'IXB',
            'starting_price': decimal.Decimal('2199.00'),
            'valid_from': now,
            'valid_until': one_year_later,
            'is_active': True,
            'min_passengers': 2,
            'max_passengers': 8,
            'required_class': '',
            'is_international_only': False,
            'terms': 'Minimum 2 passengers. Valid on CCU-IXB & DEL-IXB routes.',
            'countdown_hours': 28
        },
        {
            'title': 'Executive Transatlantic Suite Pass',
            'code': 'BIZTRANSAT',
            'category': 'BUSINESS',
            'badge': '💼 New York Biz - 15% OFF',
            'description': 'Direct premium flights to JFK with chauffeur service, private flat-bed suites, and fine dining.',
            'discount_percent': 15.0,
            'origin_code': 'BOM',
            'destination_code': 'JFK',
            'starting_price': decimal.Decimal('64999.00'),
            'valid_from': now,
            'valid_until': one_year_later,
            'is_active': True,
            'min_passengers': 1,
            'max_passengers': 4,
            'required_class': 'BUSINESS',
            'is_international_only': True,
            'terms': 'Valid on Business/First Class cabins to JFK. Includes 3 bags up to 32kg each.',
            'countdown_hours': 72
        },
        {
            'title': 'University Break Flash Fare',
            'code': 'COLLEGEBREAK',
            'category': 'STUDENT',
            'badge': '🎒 Student Break - 20% OFF',
            'description': 'Heavy discounts on semester break travel across domestic tech and education hubs.',
            'discount_percent': 20.0,
            'origin_code': 'DEL',
            'destination_code': 'BLR',
            'starting_price': decimal.Decimal('2150.00'),
            'valid_from': now,
            'valid_until': one_year_later,
            'is_active': True,
            'min_passengers': 1,
            'max_passengers': 3,
            'required_class': 'ECONOMY',
            'is_international_only': False,
            'terms': 'Student ID mandatory at check-in. Extra 5kg baggage allowance free of charge.',
            'countdown_hours': 19
        },
        {
            'title': 'Chandigarh & Shimla Hills Express',
            'code': 'CITYBEAUTIFUL',
            'category': 'WEEKEND',
            'badge': '🌲 Chandigarh Deal - 19% OFF',
            'description': 'Direct flights to the City Beautiful with quick scenic taxi connections to Kasauli and Shimla.',
            'discount_percent': 19.0,
            'origin_code': 'BOM',
            'destination_code': 'IXC',
            'starting_price': decimal.Decimal('2699.00'),
            'valid_from': now,
            'valid_until': one_year_later,
            'is_active': True,
            'min_passengers': 1,
            'max_passengers': 6,
            'required_class': '',
            'is_international_only': False,
            'terms': 'Valid on BOM-IXC and BLR-IXC non-stop flights.',
            'countdown_hours': 13
        },
        {
            'title': 'Kaziranga & Brahmaputra Odyssey',
            'code': 'GUWAHATIWILD',
            'category': 'DOMESTIC',
            'badge': '🦏 Assam Wildlife - 16% OFF',
            'description': 'Fly into Guwahati for thrilling Kaziranga rhino safaris and scenic Brahmaputra river sunset cruises.',
            'discount_percent': 16.0,
            'origin_code': 'DEL',
            'destination_code': 'GAU',
            'starting_price': decimal.Decimal('2899.00'),
            'valid_from': now,
            'valid_until': one_year_later,
            'is_active': True,
            'min_passengers': 1,
            'max_passengers': 6,
            'required_class': '',
            'is_international_only': False,
            'terms': 'Valid on all direct routes to Guwahati (GAU). Instant confirmation.',
            'countdown_hours': 20
        }
    ]

    for data in deals_data:
        Deal.objects.update_or_create(
            code=data['code'],
            defaults=data
        )

    print(f"Created/Updated {len(deals_data)} deals successfully.")

    print("Creating sample bookings & payments...")
    first_flight = Flight.objects.filter(origin__code='BOM', destination__code='DEL').first()
    second_flight = Flight.objects.filter(origin__code='DEL', destination__code='GOI').first()
    
    if first_flight:
        p1 = Passenger.objects.create(first_name="Rahul", last_name="Sharma", email="rahul.sharma@example.com", phone="+91 9876543210")
        b1 = Booking.objects.create(
            pnr="FE849201",
            ticket_number="FE992019482012",
            flight=first_flight,
            passenger=p1,
            booked_seats=1,
            seat_number="12A",
            original_fare=decimal.Decimal('5200.00'),
            price_paid=decimal.Decimal('6136.00'),
            status="CONFIRMED",
        )
        Payment.objects.create(
            booking=b1,
            payment_id="PAY94820194820184",
            method="CARD",
            amount=decimal.Decimal('6136.00'),
            status="SUCCESS",
            transaction_id="TXN9482019482",
            card_last4="4242"
        )
    
    if second_flight:
        p2 = Passenger.objects.create(first_name="Priya", last_name="Patel", email="priya.patel@example.com", phone="+91 9812345678")
        b2 = Booking.objects.create(
            pnr="FE551930",
            ticket_number="FE849201948205",
            flight=second_flight,
            passenger=p2,
            booked_seats=1,
            seat_number="14C",
            original_fare=decimal.Decimal('4500.00'),
            price_paid=decimal.Decimal('5310.00'),
            status="CANCELLED",
            cancelled_at=now,
            cancellation_fee=decimal.Decimal('1000.00'),
            refund_amount=decimal.Decimal('4310.00'),
            refund_status="REQUESTED",
            refund_method="ORIGINAL_PAYMENT",
            refund_notes="Customer requested cancellation due to family emergency."
        )
        Payment.objects.create(
            booking=b2,
            payment_id="PAY84920194820199",
            method="UPI",
            amount=decimal.Decimal('5310.00'),
            status="SUCCESS",
            transaction_id="UPI984201948",
            upi_id="priya@okhdfcbank"
        )

    print("Creating sample Admin Alerts & Activity Logs...")
    if first_flight:
        AdminAlert.objects.create(
            alert_level="CRITICAL",
            title=f"Flight {first_flight.flight_number} Nearly Sold Out",
            message=f"Only {first_flight.available_seats} seats remaining on route {first_flight.origin.code} → {first_flight.destination.code}. High dynamic surge detected.",
            flight=first_flight,
            action_recommended="Review dynamic pricing multipliers or assign larger aircraft."
        )
        AdminActivityLog.objects.create(
            user=admin_user,
            action_type="PRICING_RULE_CHANGE",
            entity_type="PricingRule",
            entity_id="1",
            description="Initialized standard AI Dynamic Pricing algorithm parameters.",
            new_value="Base floor: ₹1800, Cap: ₹65000, Multiplier: 1.15x",
            ip_address="127.0.0.1"
        )
    
    print("Database seeding completed successfully!")

if __name__ == '__main__':
    seed()
