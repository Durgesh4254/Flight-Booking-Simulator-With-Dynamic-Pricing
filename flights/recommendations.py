"""
Personalized Recommendations Engine for FlyEase.
Produces contextual destination and route recommendations based on legitimate application data:
- Previous search destinations
- Booked flights and destinations
- Interacted deals and categories
- Preferred budget range
- Popular domestic and global hubs
Users can toggle personalization in settings.
"""

from .models import Booking, Deal, Airport, Flight
from .destinations_dataset import DESTINATIONS_DATA

def get_personalized_recommendations(user=None, recent_search_dest=None, max_budget=45000):
    """
    Computes personalized destination recommendations.
    """
    recommended = []
    
    # 1. Inspect past bookings if authenticated
    past_dest_codes = []
    if user and user.is_authenticated:
        user_bookings = Booking.objects.filter(user=user).select_related('flight', 'flight__destination')[:5]
        for b in user_bookings:
            if b.flight and b.flight.destination:
                past_dest_codes.append(b.flight.destination.code)

    # 2. Add recent search dest
    if recent_search_dest:
        past_dest_codes.append(recent_search_dest.upper())

    # 3. Destination clusters for smart contextual matching
    CLUSTERS = {
        'DXB': ['DOH', 'AUH', 'MCT', 'SIN', 'BKK'],
        'BOM': ['DEL', 'BLR', 'GOI', 'DXB', 'LHR'],
        'DEL': ['BOM', 'BLR', 'SXR', 'DXB', 'SIN'],
        'GOI': ['COK', 'MLE', 'DPS', 'TRV', 'MAA'],
        'LHR': ['CDG', 'FRA', 'AMS', 'ZRH', 'FCO'],
        'SIN': ['BKK', 'KUL', 'DPS', 'HKG', 'HND'],
        'SXR': ['IXB', 'DED', 'IXC', 'GAU', 'ZRH']
    }

    target_related = []
    for code in past_dest_codes:
        target_related.extend(CLUSTERS.get(code, []))

    if not target_related:
        # Default trending global gateways
        target_related = ['DXB', 'SIN', 'GOI', 'LHR', 'DEL', 'SXR', 'BKK', 'MLE']

    # Filter unique codes
    seen = set(past_dest_codes)
    unique_candidates = []
    for code in target_related:
        if code not in seen and code not in unique_candidates:
            unique_candidates.append(code)

    # Fetch airport metadata
    airport_objs = {a.code: a for a in Airport.objects.filter(code__in=unique_candidates[:8])}

    # Fetch active deals
    active_deals = {d.destination_code: d for d in Deal.objects.filter(is_active=True)}

    for code in unique_candidates[:6]:
        ap = airport_objs.get(code)
        if not ap:
            continue

        deal = active_deals.get(code)
        deal_tag = f"{deal.discount_percent}% OFF with {deal.code}" if deal else None

        base_fare = float(ap.avg_fare) if ap.avg_fare else 4500.0
        
        # Estimate duration
        is_intl = ap.is_international or ap.country != "India"
        est_duration = "4h 20m" if is_intl else "2h 10m"

        recommended.append({
            "code": ap.code,
            "city": ap.city,
            "country": ap.country,
            "name": ap.name,
            "category": ap.category,
            "price": int(base_fare),
            "duration": est_duration,
            "deal": deal_tag,
            "rating": 4.8,
            "baggage": "20-30 KG Included",
            "best_season": ap.best_season,
            "is_international": is_intl,
            "reason": f"Popular route based on trending travel to {ap.city}"
        })

    return recommended
