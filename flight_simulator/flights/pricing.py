
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime
from django.utils import timezone

def compute_dynamic_fare(base_fare: Decimal,
                         total_seats: int,
                         seats_available: int,
                         departure: datetime,
                         demand_level: float) -> Decimal:
    

    
    if total_seats <= 0:
        total_seats = 1
    if seats_available < 0:
        seats_available = 0
    if demand_level < 0:
        demand_level = 0.0
    if demand_level > 1:
        demand_level = 1.0

    
    now = timezone.now()
    if departure.tzinfo:
        now = now.astimezone(departure.tzinfo)
    hours_to_departure = max((departure - now).total_seconds() / 3600.0, 0.0)

    remaining_pct = seats_available / float(total_seats)

    
    if hours_to_departure > 168:      
        time_mult = 1.0
    elif hours_to_departure > 72:     
        time_mult = 1.05
    elif hours_to_departure > 24:     
        time_mult = 1.20
    elif hours_to_departure > 6:     
        time_mult = 1.5
    else:                             
        time_mult = 2.0

    
    availability_mult = 1.0 + (1.0 - remaining_pct) ** 2 * 2.0

    
    demand_mult = 0.9 + demand_level * 1.1

    multiplier = time_mult * availability_mult * demand_mult

    if remaining_pct < 0.05:
        multiplier *= 1.25

    fare = (Decimal(base_fare) * Decimal(str(multiplier))).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    base = Decimal(base_fare).quantize(Decimal('0.01'))
    if fare < base:
        fare = base

    return fare
