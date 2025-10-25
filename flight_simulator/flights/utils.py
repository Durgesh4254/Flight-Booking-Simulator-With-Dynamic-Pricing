from datetime import datetime
from django.utils import timezone
import random
import string
from decimal import Decimal

def calculate_dynamic_price(flight):
    time_to_departure = (flight.departure_time - timezone.now()).total_seconds() / 3600
    seat_ratio = flight.available_seats / flight.total_seats
    demand = flight.demand_factor

    price_multiplier = 1.0

    if time_to_departure < 24:
        price_multiplier += 0.3
    elif time_to_departure < 72:
        price_multiplier += 0.15

    if seat_ratio < 0.5:
        price_multiplier += 0.2
    elif seat_ratio < 0.2:
        price_multiplier += 0.5

    
    price_multiplier *= demand

    return round(float(flight.base_price) * price_multiplier, 2)

def generate_pnr(prefix='PN'):
    
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    return f"{prefix}{code}"

def simulate_payment(amount: Decimal) -> dict:
   
    chance_fail = 0.02 + (float(amount) / 100000.0)  
    if random.random() < chance_fail:
        return {"success": False, "error": "Simulated payment failure"}
    return {"success": True, "transaction_id": ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))}