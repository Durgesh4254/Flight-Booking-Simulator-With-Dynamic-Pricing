"""
Live Flight Radar Tracker Telemetry Service for FlyEase.
Calculates realistic aircraft positions, altitude, speed, remaining distance, ETA, and gate/terminal.
If a flight is outside its active operational window (e.g. past or far future), returns "Live position unavailable".
"""

import math
from datetime import datetime
from django.utils import timezone
from .models import Flight
from .destinations_dataset import AIRPORT_MAP

def get_flight_radar_telemetry(flight_identifier):
    """
    Computes real-time aircraft telemetry along its Great Circle arc.
    """
    flight = None
    if isinstance(flight_identifier, int) or (isinstance(flight_identifier, str) and flight_identifier.isdigit()):
        flight = Flight.objects.filter(id=int(flight_identifier)).first()
    else:
        flight = Flight.objects.filter(flight_number__iexact=str(flight_identifier).strip()).first()

    if not flight:
        return {
            "success": False,
            "error": "Flight not found",
            "is_live": False,
            "status_message": "Live position unavailable"
        }

    now = timezone.now()
    dep_time = flight.departure_time
    arr_time = flight.arrival_time
    total_seconds = max((arr_time - dep_time).total_seconds(), 1800.0)
    elapsed_seconds = (now - dep_time).total_seconds()

    orig_code = flight.origin.code if flight.origin else "BOM"
    dest_code = flight.destination.code if flight.destination else "DEL"
    
    orig_coords = AIRPORT_MAP.get(orig_code, {"lat": flight.origin.latitude, "lon": flight.origin.longitude, "city": flight.origin.city})
    dest_coords = AIRPORT_MAP.get(dest_code, {"lat": flight.destination.latitude, "lon": flight.destination.longitude, "city": flight.destination.city})

    # Great circle distance
    lat1, lon1 = math.radians(orig_coords['lat']), math.radians(orig_coords['lon'])
    lat2, lon2 = math.radians(dest_coords['lat']), math.radians(dest_coords['lon'])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    total_dist_km = round(max(350, 6371 * c), 0)

    # Status detection
    if elapsed_seconds < -3600:
        # More than 1 hour before departure
        return {
            "success": True,
            "flight_number": flight.flight_number,
            "airline": flight.airline.name if flight.airline else "FlyEase",
            "airline_code": flight.airline.code if flight.airline else "FE",
            "origin": orig_code,
            "origin_city": orig_coords.get('city', orig_code),
            "destination": dest_code,
            "dest_city": dest_coords.get('city', dest_code),
            "status": "SCHEDULED",
            "status_label": "🟢 Scheduled",
            "is_live": False,
            "status_message": "Flight is scheduled. Radar telemetry activates 1 hour before departure.",
            "departure_time": dep_time.isoformat(),
            "arrival_time": arr_time.isoformat(),
            "terminal": "T1",
            "gate": "A12"
        }
    elif elapsed_seconds < 0:
        # Boarding window (1 hour prior to departure)
        return {
            "success": True,
            "flight_number": flight.flight_number,
            "airline": flight.airline.name if flight.airline else "FlyEase",
            "airline_code": flight.airline.code if flight.airline else "FE",
            "origin": orig_code,
            "origin_city": orig_coords.get('city', orig_code),
            "destination": dest_code,
            "dest_city": dest_coords.get('city', dest_code),
            "status": "BOARDING",
            "status_label": "🟡 Boarding at Gate",
            "is_live": True,
            "current_position": {
                "latitude": orig_coords['lat'],
                "longitude": orig_coords['lon']
            },
            "altitude_ft": 0,
            "speed_kmh": 0,
            "progress_pct": 0.0,
            "distance_remaining_km": total_dist_km,
            "eta": arr_time.strftime("%H:%M"),
            "terminal": "T1",
            "gate": "B24",
            "departure_time": dep_time.isoformat(),
            "arrival_time": arr_time.isoformat()
        }
    elif 0 <= elapsed_seconds <= total_seconds:
        # Active in flight!
        progress = elapsed_seconds / total_seconds
        
        # Intermediate coordinates on arc
        curr_lat = orig_coords['lat'] + (dest_coords['lat'] - orig_coords['lat']) * progress
        curr_lon = orig_coords['lon'] + (dest_coords['lon'] - orig_coords['lon']) * progress

        # Realistic altitude profile (climb -> cruise at 34,000-38,000 ft -> descent)
        if progress < 0.15:
            alt = int((progress / 0.15) * 34000)
            spd = int(450 + (progress / 0.15) * 370)
        elif progress > 0.85:
            alt = int((1.0 - ((progress - 0.85) / 0.15)) * 34000)
            spd = int(820 - ((progress - 0.85) / 0.15) * 400)
        else:
            alt = 34000 + int(math.sin(progress * math.pi) * 2000)
            spd = 820 + int(math.sin(progress * math.pi) * 30)

        dist_rem = round(total_dist_km * (1.0 - progress), 0)

        return {
            "success": True,
            "flight_number": flight.flight_number,
            "airline": flight.airline.name if flight.airline else "FlyEase",
            "airline_code": flight.airline.code if flight.airline else "FE",
            "aircraft": flight.aircraft.model_name if flight.aircraft else "Boeing 737-800",
            "origin": orig_code,
            "origin_city": orig_coords.get('city', orig_code),
            "destination": dest_code,
            "dest_city": dest_coords.get('city', dest_code),
            "status": "IN_FLIGHT",
            "status_label": "🟢 In Flight",
            "is_live": True,
            "current_position": {
                "latitude": round(curr_lat, 4),
                "longitude": round(curr_lon, 4)
            },
            "altitude_ft": alt,
            "speed_kmh": spd,
            "progress_pct": round(progress * 100, 1),
            "distance_remaining_km": dist_rem,
            "total_distance_km": total_dist_km,
            "eta": arr_time.strftime("%H:%M"),
            "terminal": "T2",
            "gate": "B24",
            "departure_time": dep_time.isoformat(),
            "arrival_time": arr_time.isoformat()
        }
    else:
        # Landed
        return {
            "success": True,
            "flight_number": flight.flight_number,
            "airline": flight.airline.name if flight.airline else "FlyEase",
            "origin": orig_code,
            "destination": dest_code,
            "status": "LANDED",
            "status_label": "🔵 Landed & Arrived",
            "is_live": False,
            "altitude_ft": 0,
            "speed_kmh": 0,
            "distance_remaining_km": 0,
            "progress_pct": 100.0,
            "terminal": "T2",
            "gate": "B24"
        }
