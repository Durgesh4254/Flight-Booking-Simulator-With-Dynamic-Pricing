"""
Groq AI Travel Assistant Service for FlyEase.
Translates natural-language user queries into context-grounded recommendations
using real application database facts (flights, dynamic prices, deals, seat inventory, baggage, visa requirements).
Strictly prevents hallucinations: never invents fake flights or prices.
Uses GROQ_API_KEY from environment.
"""

import json
import os
import re
from decimal import Decimal
from django.conf import settings
from django.utils import timezone
from .models import Flight, Deal, Airport, Airline, Coupon
from .utils import compute_dynamic_fare
from .travel_requirements import get_travel_requirements
from .flight_generator import create_dynamic_schedule_flights

try:
    from groq import Groq
except ImportError:
    Groq = None

def get_groq_client():
    api_key = getattr(settings, 'GROQ_API_KEY', '') or os.environ.get('GROQ_API_KEY', '')
    if not api_key or not Groq:
        return None
    try:
        return Groq(api_key=api_key)
    except Exception:
        return None

def extract_origin_and_dest(query):
    """
    Intelligently extracts origin and destination airports from natural language phrases like:
    - 'from Mumbai to Amritsar'
    - 'flights from BOM to ATQ'
    - 'Mumbai to Bali'
    - 'flight to Bali'
    - 'flights to London from Delhi'
    """
    q = query.lower()
    all_airports = list(Airport.objects.all())

    # Map name/city/code/aliases to airport object
    airport_lookup = {}
    for a in all_airports:
        airport_lookup[a.code.lower()] = a
        airport_lookup[a.city.lower()] = a
        # Also include sub-city names like 'Amritsar / Golden Temple' -> 'amritsar'
        for part in a.city.lower().split('/'):
            airport_lookup[part.strip()] = a
        for part in a.name.lower().split():
            if len(part) > 3:
                airport_lookup[part] = a

    # Common aliases
    aliases = {
        'bali': 'DPS', 'denpasar': 'DPS',
        'amritsar': 'ATQ',
        'dubai': 'DXB',
        'london': 'LHR', 'heathrow': 'LHR',
        'delhi': 'DEL', 'new delhi': 'DEL',
        'mumbai': 'BOM', 'bombay': 'BOM',
        'bangalore': 'BLR', 'bengaluru': 'BLR',
        'chennai': 'MAA',
        'kolkata': 'CCU',
        'goa': 'GOI',
        'singapore': 'SIN',
        'paris': 'CDG',
        'new york': 'JFK',
        'tokyo': 'HND',
        'srinagar': 'SXR',
        'jaipur': 'JAI',
        'phuket': 'HKT',
        'bangkok': 'BKK'
    }
    for alias, code in aliases.items():
        ap = Airport.objects.filter(code=code).first()
        if ap:
            airport_lookup[alias] = ap

    orig_ap = None
    dest_ap = None

    # Pattern: "from X to Y"
    m_from_to = re.search(r'from\s+([a-zA-Z\s]+?)\s+to\s+([a-zA-Z\s]+?)(?:\s+under|\s+on|\s+in|\s+for|\s+below|\?|\.|$)', q)
    if m_from_to:
        w_orig = m_from_to.group(1).strip()
        w_dest = m_from_to.group(2).strip()
        for k, ap in airport_lookup.items():
            if k in w_orig:
                orig_ap = ap
                break
        for k, ap in airport_lookup.items():
            if k in w_dest:
                dest_ap = ap
                break

    # Pattern: "X to Y"
    if not dest_ap:
        m_x_to_y = re.search(r'([a-zA-Z]+)\s+to\s+([a-zA-Z]+)', q)
        if m_x_to_y:
            w1 = m_x_to_y.group(1).strip()
            w2 = m_x_to_y.group(2).strip()
            if w1 in airport_lookup and w2 in airport_lookup:
                orig_ap = airport_lookup[w1]
                dest_ap = airport_lookup[w2]

    # Pattern: "flights to Y" / "flight for Y"
    if not dest_ap:
        m_to = re.search(r'(?:to|for|in)\s+([a-zA-Z]+)', q)
        if m_to:
            w_dest = m_to.group(1).strip()
            if w_dest in airport_lookup:
                dest_ap = airport_lookup[w_dest]

    # General keyword scan if still not resolved
    if not dest_ap:
        for k, ap in airport_lookup.items():
            if re.search(r'\b' + re.escape(k) + r'\b', q):
                if not dest_ap:
                    dest_ap = ap
                elif not orig_ap and ap != dest_ap:
                    orig_ap = ap

    # Default fallback origin if only destination is asked
    if dest_ap and not orig_ap:
        orig_ap = Airport.objects.filter(code='BOM').first() or Airport.objects.first()

    return orig_ap, dest_ap

def gather_database_context(user_query):
    """
    Scans the database for real flights, deals, coupons, and destination info
    matching keywords in the user query to ground the AI response.
    """
    orig_ap, dest_ap = extract_origin_and_dest(user_query)
    today = timezone.now().date()

    # Query or dynamically generate flights for the requested route
    flights_context = []
    if orig_ap and dest_ap and orig_ap != dest_ap:
        specific_flights = Flight.objects.filter(
            origin=orig_ap,
            destination=dest_ap,
            departure_time__gte=timezone.now()
        ).select_related('airline', 'origin', 'destination', 'aircraft')[:8]

        if not specific_flights.exists():
            create_dynamic_schedule_flights(orig_ap.code, dest_ap.code, today)
            specific_flights = Flight.objects.filter(
                origin=orig_ap,
                destination=dest_ap,
                departure_time__gte=timezone.now()
            ).select_related('airline', 'origin', 'destination', 'aircraft')[:8]

        flights_qs = specific_flights
    else:
        # General top scheduled flights
        flights_qs = Flight.objects.filter(
            is_active=True,
            departure_time__gte=timezone.now()
        ).select_related('airline', 'origin', 'destination', 'aircraft')[:15]

    for f in flights_qs:
        pricing = compute_dynamic_fare(f)
        flights_context.append({
            "flight_number": f.flight_number,
            "airline": f.airline.name if f.airline else "FlyEase",
            "airline_code": f.airline.code if f.airline else "FE",
            "origin": f.origin.code if f.origin else "BOM",
            "origin_city": f.origin.city if f.origin else "Mumbai",
            "destination": f.destination.code if f.destination else "DEL",
            "destination_city": f.destination.city if f.destination else "Delhi",
            "departure": f.departure_time.strftime("%Y-%m-%d %H:%M"),
            "arrival": f.arrival_time.strftime("%Y-%m-%d %H:%M"),
            "price": float(pricing['total']),
            "base_fare": float(pricing['base_fare']),
            "available_seats": f.available_seats,
            "baggage": f.airline.baggage_policy if f.airline and f.airline.baggage_policy else "Cabin: 7kg | Check-in: 15kg",
            "status": f.status
        })

    # 3. Active deals and promotions
    deals = list(Deal.objects.filter(is_active=True, valid_until__gte=timezone.now())[:6])
    deals_context = [{
        "code": d.code,
        "title": d.title,
        "discount_percent": d.discount_percent,
        "starting_price": float(d.starting_price),
        "category": d.category,
        "terms": d.terms
    } for d in deals]

    # 4. Standard baggage rules
    baggage_rules = {
        "Economy Domestic": "Cabin: 1 piece up to 7 kg | Check-in: 1 piece up to 15 kg",
        "Economy International": "Cabin: 1 piece up to 7 kg | Check-in: 1 or 2 pieces up to 25-30 kg",
        "Business Class": "Cabin: 2 pieces up to 10 kg each | Check-in: 2 pieces up to 35-40 kg",
        "Excess Baggage": "Pre-book online at ₹1,200 for +15 kg to save 40% vs airport counter rates."
    }

    return {
        "flights": flights_context,
        "deals": deals_context,
        "baggage_rules": baggage_rules,
        "reference_time": timezone.now().strftime("%Y-%m-%d %H:%M UTC"),
        "orig_airport": orig_ap,
        "dest_airport": dest_ap
    }

def ask_flyease_ai(user_message, conversation_history=None):
    """
    Main assistant pipeline:
    User Message -> Gather DB context -> Groq Llama 3 / Structured synthesis -> Response
    """
    if not user_message or not user_message.strip():
        return {
            "reply": "Hello! I am FlyEase AI ✈️. How can I help you find flights, deals, baggage rules, or travel requirements today?",
            "flights": [],
            "deals": []
        }

    client = get_groq_client()
    context = gather_database_context(user_message)

    # If Groq client is not configured or fails, provide intelligent fact-based deterministic fallback
    if not client:
        return generate_fact_based_reply(user_message, context)

    system_prompt = f"""You are FlyEase AI, the official intelligent travel assistant for the FlyEase flight-booking platform.
You assist travelers with finding flights, comparing fares, explaining baggage allowances, applying deals, dynamic pricing, and travel requirements.

CRITICAL RULES:
1. STRICT ROUTE RELEVANCE: ONLY talk about flights that match the traveler's requested origin and destination. If the traveler asks for Amritsar, ONLY discuss flights to Amritsar. If they ask for Bali, ONLY discuss flights to Bali.
2. NEVER invent flights, prices, flight numbers, or dates that are not provided in the REAL DATABASE CONTEXT below.
3. If no flights match the requested route, state clearly that no direct flights were found for that route.
4. Always format your responses cleanly with emojis (✈️, 🏆, 💰, 🔥, 🛂, 🧳).
5. For flight options, clearly present Flight Number, Route (e.g. BOM → ATQ), Price (in ₹ INR), Duration/Stops, and Baggage.
6. Highlight active promo codes when relevant.

REAL DATABASE CONTEXT (LIVE FACTUAL DATA):
Flights Available: {json.dumps(context['flights'])}
Active Deals: {json.dumps(context['deals'])}
Baggage Rules: {json.dumps(context['baggage_rules'])}
Current Time: {context['reference_time']}
"""

    messages = [{"role": "system", "content": system_prompt}]
    if conversation_history:
        for turn in conversation_history[-4:]:
            messages.append({"role": turn.get('role', 'user'), "content": turn.get('content', '')})
    messages.append({"role": "user", "content": user_message})

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.2,
            max_tokens=600,
        )
        reply = completion.choices[0].message.content

        return {
            "reply": reply,
            "flights": context['flights'][:4],
            "deals": context['deals'][:2],
            "status": "SUCCESS"
        }
    except Exception as e:
        fallback_res = generate_fact_based_reply(user_message, context)
        fallback_res["note"] = "AI assistant connected with localized intelligence."
        return fallback_res

def generate_fact_based_reply(query, context):
    """Deterministic, high-accuracy reply generator when external LLM is offline."""
    q = query.lower()
    flights = context.get('flights', [])
    deals = context.get('deals', [])
    orig_ap = context.get('orig_airport')
    dest_ap = context.get('dest_airport')

    if "baggage" in q or "luggage" in q or "cabin" in q:
        reply = "✈️ **FlyEase Baggage Guidelines**:\n\n" \
                "• **Domestic Economy**: 7 kg Cabin + 15 kg Check-in\n" \
                "• **International Economy**: 7 kg Cabin + 25-30 kg Check-in\n" \
                "• **Business Class**: 2x 10 kg Cabin + 35-40 kg Check-in\n\n" \
                "💡 *Tip: Pre-book extra baggage during checkout to save up to 40% vs airport counter rates.*"
        return {"reply": reply, "flights": [], "deals": deals[:1]}

    if "visa" in q or "document" in q or "passport" in q or ("need" in q and ("dubai" in q or "bali" in q or "london" in q)):
        dest_country = dest_ap.country if dest_ap else "United Arab Emirates"
        req = get_travel_requirements("India", dest_country)
        reply = f"🛂 **Travel & Visa Guidelines for {dest_country}**:\n\n" \
                f"• **Visa Status**: {req.get('visa_required', 'Required')}\n" \
                f"• **Visa Type**: {req.get('visa_type', 'Tourist / Electronic Visa')}\n" \
                f"• **Passport Validity**: {req.get('passport_validity', 'Min 6 months')}\n\n" \
                f"**Mandatory Documents Checklist**:\n{req.get('documents_required', 'Valid Passport, Return Ticket, Accommodation')}\n\n" \
                f"⚠️ *Note: Always verify with official embassy portals before travel.*"
        return {"reply": reply, "flights": [], "deals": []}

    if "deal" in q or "coupon" in q or "discount" in q or "offer" in q:
        if deals:
            d_list = "\n".join([f"• **{d['code']}**: {d['title']} ({d['discount_percent']}% OFF)" for d in deals[:3]])
            reply = f"🔥 **Active FlyEase Deals & Offers**:\n\n{d_list}\n\nApply these promo codes on the booking screen before payment!"
        else:
            reply = "🔥 Check our Special Deals page for active weekend and seasonal promotional fares!"
        return {"reply": reply, "flights": [], "deals": deals}

    # Route Specific Matching
    if dest_ap and flights:
        orig_title = orig_ap.city if orig_ap else "Mumbai"
        dest_title = dest_ap.city
        cheapest = min(flights, key=lambda x: x['price'])
        
        f_list = f"✈️ Yes! I found **{len(flights)} scheduled flights** from **{orig_title}** to **{dest_title}** ({orig_ap.code if orig_ap else 'BOM'} → {dest_ap.code}):\n\n" \
                 f"🏆 **Best Value Option**: `{cheapest['airline_code']}-{cheapest['flight_number']}`\n" \
                 f"💰 **Fare**: **₹{cheapest['price']:,.0f}** ({cheapest['available_seats']} seats left)\n" \
                 f"🧳 **Baggage**: {cheapest['baggage']}\n" \
                 f"📅 **Departure**: {cheapest['departure']}\n"
        if deals:
            f_list += f"\n🔥 **Available Promo**: Use code `{deals[0]['code']}` for {deals[0]['discount_percent']}% instant discount!"
        return {"reply": f_list, "flights": flights[:4], "deals": deals[:2]}

    if dest_ap and not flights:
        return {
            "reply": f"✈️ No direct flights currently scheduled between {orig_ap.city if orig_ap else 'origin'} and {dest_ap.city} for today. Please try searching for upcoming dates on our flight search engine.",
            "flights": [],
            "deals": deals[:2]
        }

    return {
        "reply": "✈️ I can help you search live flights, predict price trends, track price drops, check visa rules, and apply deals! Try asking: *'Flights from Mumbai to Amritsar'* or *'Is there any flight to Bali?'*",
        "flights": flights[:3],
        "deals": deals[:2]
    }
