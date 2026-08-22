import os
import django
import random
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flight_simulator.settings')
django.setup()

from django.utils import timezone
from flights.models import Airline, Airport, Aircraft, Flight, Seat
from flights.flight_generator import calculate_flight_duration_and_base_fare, generate_seats_for_flight

def seed_worldwide_network_flights():
    print("Starting worldwide network flights generation for 324 airports...")
    
    airlines_by_code = {a.code: a for a in Airline.objects.all()}
    aircraft_list = list(Aircraft.objects.all())
    base_date = timezone.now().date()
    
    # Hub connect lists
    indian_intl_hubs = ['DEL', 'BOM', 'BLR', 'HYD', 'MAA', 'CCU', 'COK']
    
    # All international destinations currently in DB
    intl_airports = list(Airport.objects.filter(is_international=True).exclude(country="India"))
    
    print(f"Found {len(intl_airports)} international destination airports.")
    
    # Major regional partners
    airline_pool = [
        'AI', '6E', 'EK', 'SQ', 'BA', 'LH', 'QR', 'TG', 'EY',
        'AF', 'KL', 'DL', 'UA', 'JL', 'NH', 'CX', 'QF',
        'TK', 'VS', 'LX', 'SV', 'GF', 'WY', 'FZ', 'G9', 'NZ'
    ]
    
    created_count = 0
    flight_seq = 2000
    
    # For each international airport, generate connection to at least 1-2 major hubs across 7 days
    for ap in intl_airports:
        # Choose 2 closest or major Indian hubs
        hubs = random.sample(indian_intl_hubs, 2)
        air_code = random.choice(airline_pool)
        airline = airlines_by_code.get(air_code) or airlines_by_code.get('AI')
        
        for hub_code in hubs:
            hub_ap = Airport.objects.get(code=hub_code)
            
            # Create outbound and return
            routes = [(hub_ap, ap), (ap, hub_ap)]
            
            for orig, dest in routes:
                for day_offset in range(0, 7):
                    target_d = base_date + timedelta(days=day_offset)
                    dep_hour = random.choice(['01:15', '06:45', '11:30', '15:20', '20:10', '23:45'])
                    
                    flight_seq += 1
                    f_num = f"{airline.code}-{flight_seq}"
                    while Flight.objects.filter(flight_number=f_num).exists():
                        flight_seq += 1
                        f_num = f"{airline.code}-{flight_seq}"
                        
                    dep_dt = timezone.make_aware(datetime.combine(target_d, datetime.strptime(dep_hour, '%H:%M').time()))
                    dur_hours, base_fare = calculate_flight_duration_and_base_fare(orig.code, dest.code)
                    arr_dt = dep_dt + timedelta(hours=dur_hours)
                    
                    aircraft = random.choice(aircraft_list) if aircraft_list else None
                    tot_seats = aircraft.total_capacity if aircraft else 180
                    avail_seats = random.randint(int(tot_seats * 0.20), tot_seats)
                    
                    fl = Flight.objects.create(
                        flight_number=f_num,
                        airline=airline,
                        aircraft=aircraft,
                        origin=orig,
                        destination=dest,
                        departure_time=dep_dt,
                        arrival_time=arr_dt,
                        base_price=base_fare,
                        total_seats=tot_seats,
                        available_seats=avail_seats,
                        demand_factor=round(random.uniform(0.9, 1.45), 2),
                        status='SCHEDULED'
                    )
                    
                    if aircraft:
                        generate_seats_for_flight(fl, aircraft)
                    created_count += 1
                    
                    if created_count % 500 == 0:
                        print(f"Generated {created_count} worldwide flights...")

    print(f"Worldwide flight seeding complete! Generated {created_count} new flights.")
    print(f"Total flights in system: {Flight.objects.count()}")

if __name__ == '__main__':
    seed_worldwide_network_flights()
