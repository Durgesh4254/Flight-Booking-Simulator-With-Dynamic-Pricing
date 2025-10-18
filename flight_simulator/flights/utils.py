from datetime import datetime
from django.utils import timezone
import random
import string
from decimal import Decimal

def calculate_dynamic_price(flight):
    time_to_departure = (flight.departure_time - timezone.now()).total_seconds() / 3600
    seat_ratio = flight.available_seats / flight.total_seats
    demand = flight.demand_factor

    # Example dynamic formula
    price_multiplier = 1.0

    # Less time left → higher price
    if time_to_departure < 24:
        price_multiplier += 0.3
    elif time_to_departure < 72:
        price_multiplier += 0.15

    # Fewer seats → higher price
    if seat_ratio < 0.5:
        price_multiplier += 0.2
    elif seat_ratio < 0.2:
        price_multiplier += 0.5

    # High demand → higher price
    price_multiplier *= demand

    return round(float(flight.base_price) * price_multiplier, 2)

def generate_pnr(prefix='PN'):
    # 8 chars alphanumeric (uppercase) prefixed
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    return f"{prefix}{code}"

def simulate_payment(amount: Decimal) -> dict:
    """
    Fake payment processor:
      - returns {"success": True, "transaction_id": "..."} on success
      - or {"success": False, "error":"..."}
    Here we make random success/fail for simulation. In real life integrate gateway.
    """
    # simple deterministic-ish: high amounts slightly more likely to fail
    chance_fail = 0.02 + (float(amount) / 100000.0)  # small base fail + scales with amount
    if random.random() < chance_fail:
        return {"success": False, "error": "Simulated payment failure"}
    return {"success": True, "transaction_id": ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))}