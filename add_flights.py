import os
import sys
import django
from django.utils import timezone
from datetime import timedelta, datetime
import decimal

# Assuming this script is run via `python manage.py shell < add_flights.py`
from flights.models import Flight

# Delete existing dummy flights
# Flight.objects.all().delete() # Optional: keeping the existing ones is fine

# Create some flights for 2026-08-15
date_str = '2026-08-15'
base_date = timezone.make_aware(datetime.strptime(date_str, '%Y-%m-%d'))

flights = [
    {
        'origin': 'BOM',
        'destination': 'CCU',
        'departure_time': base_date + timedelta(hours=10, minutes=30),
        'arrival_time': base_date + timedelta(hours=13, minutes=0),
        'base_price': decimal.Decimal('5500.00'),
        'total_seats': 180,
        'available_seats': 150,
        'demand_factor': 1.2
    },
    {
        'origin': 'BOM',
        'destination': 'CCU',
        'departure_time': base_date + timedelta(hours=16, minutes=45),
        'arrival_time': base_date + timedelta(hours=19, minutes=15),
        'base_price': decimal.Decimal('6200.00'),
        'total_seats': 180,
        'available_seats': 20,
        'demand_factor': 1.5
    },
    {
        'origin': 'BOM',
        'destination': 'LHR',
        'departure_time': base_date + timedelta(hours=2, minutes=0),
        'arrival_time': base_date + timedelta(hours=7, minutes=30),
        'base_price': decimal.Decimal('35000.00'),
        'total_seats': 300,
        'available_seats': 100,
        'demand_factor': 1.1
    },
    {
        'origin': 'DEL',
        'destination': 'BOM',
        'departure_time': base_date + timedelta(hours=8, minutes=0),
        'arrival_time': base_date + timedelta(hours=10, minutes=15),
        'base_price': decimal.Decimal('4500.00'),
        'total_seats': 180,
        'available_seats': 180,
        'demand_factor': 1.0
    }
]

created = 0
for data in flights:
    Flight.objects.create(**data)
    created += 1

print(f"Successfully added {created} flights to the database!")
