# flights/pricing.py
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime
from django.utils import timezone

def compute_dynamic_fare(base_fare: Decimal,
                         total_seats: int,
                         seats_available: int,
                         departure: datetime,
                         demand_level: float) -> Decimal:
    """
    Compute dynamic fare from:
      - remaining seats (seats_available / total_seats)
      - time until departure (hours)
      - demand_level (0.0 .. 1.0)
      - base_fare (Decimal)
    Returns Decimal price rounded to 2 decimals.
    """

    # Safety guards
    if total_seats <= 0:
        total_seats = 1
    if seats_available < 0:
        seats_available = 0
    if demand_level < 0:
        demand_level = 0.0
    if demand_level > 1:
        demand_level = 1.0

    # Time to departure in hours (use timezone-aware now)
    now = timezone.now()
    if departure.tzinfo:
        now = now.astimezone(departure.tzinfo)
    hours_to_departure = max((departure - now).total_seconds() / 3600.0, 0.0)

    remaining_pct = seats_available / float(total_seats)

    # Time multiplier (tunable)
    if hours_to_departure > 168:      # >7 days
        time_mult = 1.0
    elif hours_to_departure > 72:     # 3-7 days
        time_mult = 1.05
    elif hours_to_departure > 24:     # 1-3 days
        time_mult = 1.20
    elif hours_to_departure > 6:      # 6-24 hours
        time_mult = 1.5
    else:                             # <6 hours
        time_mult = 2.0

    # Availability multiplier (exponential-ish)
    availability_mult = 1.0 + (1.0 - remaining_pct) ** 2 * 2.0

    # Demand multiplier maps 0..1 -> 0.9..2.0
    demand_mult = 0.9 + demand_level * 1.1

    # Combine
    multiplier = time_mult * availability_mult * demand_mult

    # Low-seat tier bump
    if remaining_pct < 0.05:
        multiplier *= 1.25

    # Compute fare
    fare = (Decimal(base_fare) * Decimal(str(multiplier))).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    # Ensure at least base fare
    base = Decimal(base_fare).quantize(Decimal('0.01'))
    if fare < base:
        fare = base

    return fare
