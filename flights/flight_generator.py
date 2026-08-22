import os
import sys
import django
from datetime import datetime, timedelta
import decimal
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flight_simulator.settings')
django.setup()

from django.utils import timezone
from django.db import transaction
from flights.models import Airline, Airport, Aircraft, Flight, Seat
from flights.utils import compute_dynamic_fare

from flights.destinations_dataset import AIRPORT_MAP

AIRPORT_COORDS = AIRPORT_MAP

import math

def calculate_flight_duration_and_base_fare(orig_code, dest_code):
    """Calculate approximate distance, flight duration in hours, and base fare."""
    c1 = AIRPORT_COORDS.get(orig_code)
    c2 = AIRPORT_COORDS.get(dest_code)

    if not c1:
        ap1 = Airport.objects.filter(code=orig_code).first()
        if ap1:
            c1 = {'lat': ap1.latitude, 'lon': ap1.longitude, 'country': ap1.country, 'city': ap1.city}
        else:
            c1 = {'lat': 20.0, 'lon': 77.0, 'country': 'India', 'city': orig_code}

    if not c2:
        ap2 = Airport.objects.filter(code=dest_code).first()
        if ap2:
            c2 = {'lat': ap2.latitude, 'lon': ap2.longitude, 'country': ap2.country, 'city': ap2.city}
        else:
            c2 = {'lat': 28.0, 'lon': 77.0, 'country': 'India', 'city': dest_code}

    lat1, lon1 = math.radians(c1['lat']), math.radians(c1['lon'])
    lat2, lon2 = math.radians(c2['lat']), math.radians(c2['lon'])

    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    dist_km = max(350, 6371 * c)

    is_international = (c1.get('country') != c2.get('country'))

    # Approx 750-850 km/h cruising speed + 30 mins taxi/takeoff/landing
    duration_hours = round(max(1.0, (dist_km / 780.0) + 0.5), 1)

    # Base pricing logic based on distance and route type
    if not is_international:
        # Domestic India: ~ ₹2,200 to ₹8,500 base
        base_fare = round(2200 + (dist_km * 2.1), -1)
        base_fare = max(2400, min(base_fare, 9500))
    else:
        # International: base ₹12,000 - ₹68,000
        base_fare = round(11000 + (dist_km * 3.6), -2)
        base_fare = max(11500, min(base_fare, 72000))

    return duration_hours, decimal.Decimal(str(base_fare))


def get_airline_for_route(orig_code, dest_code, index):
    """Pick realistic airline for given route based on all global and domestic partners."""
    c1 = AIRPORT_COORDS.get(orig_code, {})
    c2 = AIRPORT_COORDS.get(dest_code, {})
    is_intl = (c1.get('country') != c2.get('country'))

    if is_intl:
        intl_airlines = [
            'EK', 'AI', 'BA', 'SQ', 'LH', 'QR', 'TG', 'EY',
            'AF', 'KL', 'CX', 'DL', 'UA', 'JL', 'NH', 'QF',
            'TK', 'VS', 'LX', 'SV', 'GF', 'WY', 'FZ', 'G9'
        ]
        return intl_airlines[index % len(intl_airlines)]
    else:
        dom_airlines = ['6E', 'AI', 'UK', 'SG', 'QP', 'I5', '9I']
        return dom_airlines[index % len(dom_airlines)]


def create_dynamic_schedule_flights(origin_code, dest_code, target_date):
    """
    Dynamically generates realistic simulated flights between any 2 supported airports
    for the requested date if none exist in the database.
    """
    try:
        orig = Airport.objects.get(code=origin_code)
        dest = Airport.objects.get(code=dest_code)
    except Airport.DoesNotExist:
        return []

    # Check if flights already exist
    existing = Flight.objects.filter(
        origin=orig,
        destination=dest,
        departure_time__date=target_date
    )
    if existing.exists():
        return list(existing)

    duration_hours, base_fare = calculate_flight_duration_and_base_fare(origin_code, dest_code)
    all_aircraft = list(Aircraft.objects.all())
    if not all_aircraft:
        return []

    all_airlines = {a.code: a for a in Airline.objects.all()}

    # Flight schedule templates (times throughout the day)
    is_intl = (orig.country != dest.country)
    if is_intl:
        times = ['02:15', '08:30', '14:45', '21:00', '23:30']
    else:
        times = ['06:00', '08:30', '11:15', '14:00', '16:45', '19:30', '21:45']

    created_flights = []
    base_dt = timezone.make_aware(datetime.combine(target_date, datetime.min.time()))

    for i, t_str in enumerate(times):
        h, m = map(int, t_str.split(':'))
        dep_time = base_dt + timedelta(hours=h, minutes=m)
        arr_time = dep_time + timedelta(hours=duration_hours)

        al_code = get_airline_for_route(origin_code, dest_code, i)
        airline = all_airlines.get(al_code) or list(all_airlines.values())[0]

        # Choose wide-body for long international or high density for domestic
        if duration_hours > 5:
            ac = next((a for a in all_aircraft if a.business_seats > 20), all_aircraft[0])
        else:
            ac = next((a for a in all_aircraft if a.business_seats <= 20), all_aircraft[0])

        # Randomize price slightly ±10%
        factor = decimal.Decimal(str(random.uniform(0.92, 1.12)))
        flight_price = (base_fare * factor).quantize(decimal.Decimal('0.01'))

        # Code FE / Airline prefix
        f_num = f"{airline.code}-{random.randint(100, 999)}"
        # Ensure unique flight number
        while Flight.objects.filter(flight_number=f_num).exists():
            f_num = f"{airline.code}-{random.randint(100, 9999)}"

        total_seats = ac.total_capacity
        available_seats = max(10, int(total_seats * random.uniform(0.3, 0.85)))

        f = Flight.objects.create(
            flight_number=f_num,
            airline=airline,
            aircraft=ac,
            origin=orig,
            destination=dest,
            departure_time=dep_time,
            arrival_time=arr_time,
            base_price=flight_price,
            total_seats=total_seats,
            available_seats=available_seats,
            demand_factor=round(random.uniform(0.9, 1.4), 2)
        )

        # Generate seats for seat map
        generate_seats_for_flight(f, ac)
        created_flights.append(f)

    return created_flights


def generate_seats_for_flight(flight, aircraft):
    """Generate seat rows for the flight."""
    seats_to_create = []
    eco_rows = aircraft.economy_seats // 6
    for row in range(1, eco_rows + 1):
        for idx, letter in enumerate(['A', 'B', 'C', 'D', 'E', 'F']):
            is_window = letter in ['A', 'F']
            is_aisle = letter in ['C', 'D']
            is_extra = row in [1, 12, 13]
            status = 'AVAILABLE' if random.random() > 0.25 else 'OCCUPIED'
            seats_to_create.append(Seat(
                flight=flight,
                seat_number=f"{row}{letter}",
                seat_class='ECONOMY',
                status=status,
                is_window=is_window,
                is_aisle=is_aisle,
                extra_legroom=is_extra
            ))

    if aircraft.business_seats > 0:
        biz_rows = aircraft.business_seats // 4
        for row in range(1, biz_rows + 1):
            for letter in ['A', 'C', 'D', 'F']:
                seats_to_create.append(Seat(
                    flight=flight,
                    seat_number=f"B{row}{letter}",
                    seat_class='BUSINESS',
                    status='AVAILABLE' if random.random() > 0.2 else 'OCCUPIED',
                    is_window=letter in ['A', 'F'],
                    is_aisle=letter in ['C', 'D'],
                    extra_legroom=False
                ))

    if aircraft.first_class_seats > 0:
        fc_rows = aircraft.first_class_seats // 2
        for row in range(1, fc_rows + 1):
            for letter in ['A', 'D']:
                seats_to_create.append(Seat(
                    flight=flight,
                    seat_number=f"F{row}{letter}",
                    seat_class='FIRST',
                    status='AVAILABLE' if random.random() > 0.15 else 'OCCUPIED',
                    is_window=True,
                    is_aisle=False,
                    extra_legroom=True
                ))

    Seat.objects.bulk_create(seats_to_create, batch_size=250)
