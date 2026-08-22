from datetime import datetime
from django.utils import timezone
import random
import string
from decimal import Decimal

def compute_dynamic_fare(flight, base_price=None, requested_class='ECONOMY'):
    """
    Computes dynamic fare based on database PricingRules, manual overrides, and real flight conditions.
    Returns structured pricing payload with transparent itemized breakdown.
    """
    from .models import PricingRule
    
    # Check if manual price override exists for this flight
    if getattr(flight, 'manual_override_price', None):
        base_price = flight.manual_override_price
        is_override = True
    elif base_price is None:
        base_price = flight.base_price
        is_override = False
    else:
        is_override = False

    # Get active pricing rule if configured
    rule = PricingRule.objects.filter(is_active=True).first()
    demand_weight = rule.demand_multiplier_weight if rule else 1.10
    seat_weight = rule.seat_availability_weight if rule else 1.20
    time_weight = rule.time_to_departure_weight if rule else 1.15
    peak_season_weight = rule.peak_season_multiplier if rule else 1.20
    weekend_weight = rule.weekend_multiplier if rule else 1.15
    holiday_weight = rule.holiday_multiplier if rule else 1.25
    min_floor = float(rule.min_fare_floor) if rule else 1500.00
    max_cap = float(rule.max_fare_cap) if rule else 45000.00

    if getattr(flight, 'min_fare_limit', None):
        min_floor = max(min_floor, float(flight.min_fare_limit))
    if getattr(flight, 'max_fare_limit', None):
        max_cap = min(max_cap, float(flight.max_fare_limit))

    time_to_departure = max((flight.departure_time - timezone.now()).total_seconds() / 3600, 0.0)
    seat_ratio = flight.available_seats / max(flight.total_seats, 1)
    demand = flight.demand_factor

    multiplier = 1.0
    breakdown = []
    
    # 1. Time Factor
    time_adj = 0.0
    if time_to_departure < 12:
        time_adj = 0.50 * time_weight
        breakdown.append({"reason": "Imminent Departure (<12 hrs)", "impact": "high", "amount": round(float(base_price) * time_adj, 2), "factor": f"+{round(time_adj*100)}%"})
    elif time_to_departure < 24:
        time_adj = 0.35 * time_weight
        breakdown.append({"reason": "Last Minute Booking (<24 hrs)", "impact": "high", "amount": round(float(base_price) * time_adj, 2), "factor": f"+{round(time_adj*100)}%"})
    elif time_to_departure < 72:
        time_adj = 0.15 * time_weight
        breakdown.append({"reason": "Near Departure (<3 days)", "impact": "medium", "amount": round(float(base_price) * time_adj, 2), "factor": f"+{round(time_adj*100)}%"})
    elif time_to_departure > 30 * 24:
        time_adj = -0.10
        breakdown.append({"reason": "Early Bird Booking (>30 days)", "impact": "low", "amount": round(float(base_price) * time_adj, 2), "factor": f"{round(time_adj*100)}%"})
    multiplier += time_adj

    # 2. Availability Scarcity Factor
    seat_adj = 0.0
    if seat_ratio < 0.10:
        seat_adj = 0.55 * seat_weight
        breakdown.append({"reason": "Critical Seat Scarcity (<10% seats)", "impact": "high", "amount": round(float(base_price) * seat_adj, 2), "factor": f"+{round(seat_adj*100)}%"})
    elif seat_ratio < 0.25:
        seat_adj = 0.30 * seat_weight
        breakdown.append({"reason": "High Seat Occupancy (<25% seats)", "impact": "high", "amount": round(float(base_price) * seat_adj, 2), "factor": f"+{round(seat_adj*100)}%"})
    elif seat_ratio < 0.50:
        seat_adj = 0.15 * seat_weight
        breakdown.append({"reason": "Moderate Occupancy (<50% seats)", "impact": "medium", "amount": round(float(base_price) * seat_adj, 2), "factor": f"+{round(seat_adj*100)}%"})
    multiplier += seat_adj

    # 3. Peak Travel / Weekend
    weekend_adj = 0.0
    if flight.departure_time.weekday() in [4, 5, 6]:
        weekend_adj = 0.12 * weekend_weight
        breakdown.append({"reason": "Weekend Travel Surcharge", "impact": "medium", "amount": round(float(base_price) * weekend_adj, 2), "factor": f"+{round(weekend_adj*100)}%"})
        multiplier += weekend_adj

    # 4. Demand Level Adjustment
    demand_adj = (demand - 1.0) * demand_weight
    if abs(demand_adj) > 0.02:
        tag = "Surge Demand Pressure" if demand_adj > 0 else "Low Demand Discount"
        breakdown.append({"reason": tag, "impact": "high" if demand_adj > 0.2 else "medium", "amount": round(float(base_price) * demand_adj, 2), "factor": f"{round(demand_adj*100):+d}%"})
        multiplier += demand_adj

    # Class Multiplier
    class_multipliers = {
        'ECONOMY': 1.0,
        'PREMIUM_ECONOMY': 1.75,
        'BUSINESS': 3.4,
        'FIRST': 4.8
    }
    class_mult = class_multipliers.get(requested_class.upper(), 1.0)
    
    # Compute Raw Dynamic Fare
    raw_fare = float(base_price) * max(multiplier, 0.8) * class_mult
    
    # Enforce floor and cap
    capped_fare = max(min_floor * class_mult, min(raw_fare, max_cap * class_mult))
    final_base = round(capped_fare, 2)
    
    # Taxes (18% GST standard in aviation)
    taxes = round(final_base * 0.18, 2)
    total_fare = round(final_base + taxes, 2)

    if not breakdown:
        breakdown.append({"reason": "Standard Base Pricing", "impact": "normal", "amount": 0.00, "factor": "0%"})

    if is_override:
        breakdown.insert(0, {"reason": "Manual Price Override Applied", "impact": "high", "amount": 0.00, "factor": "OVERRIDE"})

    return {
        "base_fare": round(float(flight.base_price) * class_mult, 2),
        "dynamic_fare": round(final_base - (float(flight.base_price) * class_mult), 2),
        "current_fare_before_tax": final_base,
        "taxes": taxes,
        "total": total_fare,
        "multiplier": round(multiplier, 2),
        "breakdown": breakdown,
        "is_override": is_override
    }

def generate_pnr(prefix='PN'):
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    return f"{prefix}{code}"

def simulate_payment(amount: Decimal) -> dict:
    chance_fail = min(0.05, 0.02 + (float(amount) / 100000.0))  
    if random.random() < chance_fail:
        return {"success": False, "error": "Simulated payment failure"}
    return {"success": True, "transaction_id": ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))}