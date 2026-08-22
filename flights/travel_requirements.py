"""
Travel requirements dataset and query helpers for FlyEase.
Provides verified visa, passport validity, and document checklists for destinations.
Includes explicit disclaimers: 'Requirements may change. Verify with official government/embassy sources.'
"""

from .models import TravelRequirement

DEFAULT_REQUIREMENTS = [
    {
        "origin_country": "India",
        "destination_country": "United Arab Emirates",
        "visa_required": "Required",
        "visa_type": "Pre-arranged eVisa / Visa on Arrival for eligible passport holders",
        "passport_validity": "Minimum 6 months from date of entry",
        "documents_required": "✓ Valid Passport (min 6 months validity)\n✓ Confirmed Return Flight Ticket\n✓ Hotel Booking / Accommodation Details\n✓ Proof of Sufficient Funds (AED 3,000+ recommended)",
        "entry_requirements": "Biometric scanning and customs inspection at Dubai (DXB) / Abu Dhabi (AUH). Transit passengers staying airside do not require a transit visa for stops under 24 hours.",
        "transit_requirements": "Direct airside transit permitted without visa for up to 24 hours.",
        "important_notes": "Requirements may change. Verify with official government/embassy sources before travel.",
        "official_source_url": "https://www.gdrfad.gov.ae/en"
    },
    {
        "origin_country": "India",
        "destination_country": "United Kingdom",
        "visa_required": "Required",
        "visa_type": "Standard Visitor Visa (Apply in advance)",
        "passport_validity": "Valid for the entire duration of stay",
        "documents_required": "✓ Valid Passport\n✓ Standard Visitor Visa / BRP\n✓ Proof of accommodation\n✓ Financial bank statements (last 6 months)\n✓ Return / Onward travel itinerary",
        "entry_requirements": "UK Border Force inspection upon arrival at London Heathrow (LHR) / Gatwick (LGW).",
        "transit_requirements": "Direct Airside Transit Visa (DATV) or Visitor in Transit visa may be required unless exempt.",
        "important_notes": "Requirements may change. Verify with official government/embassy sources before travel.",
        "official_source_url": "https://www.gov.uk/standard-visitor"
    },
    {
        "origin_country": "India",
        "destination_country": "Singapore",
        "visa_required": "Required",
        "visa_type": "eVisa (Electronic Visa) via ICA",
        "passport_validity": "Minimum 6 months at time of entry",
        "documents_required": "✓ Valid Passport\n✓ SG Arrival Card (submitted within 3 days prior to arrival)\n✓ Approved Singapore eVisa\n✓ Return ticket\n✓ Hotel reservation confirmation",
        "entry_requirements": "Submit online SG Arrival Card (free) via ICA official portal before boarding.",
        "transit_requirements": "96-hour Visa Free Transit Facility (VFTF) available for eligible travelers holding valid US/UK/Schengen/Australia visa.",
        "important_notes": "Requirements may change. Verify with official government/embassy sources before travel.",
        "official_source_url": "https://www.ica.gov.sg/enter-transit-depart"
    },
    {
        "origin_country": "India",
        "destination_country": "Thailand",
        "visa_required": "Visa Free / Visa on Arrival",
        "visa_type": "Visa Exemption / Visa on Arrival (VoA)",
        "passport_validity": "Minimum 6 months validity",
        "documents_required": "✓ Valid Passport\n✓ Confirmed return flight within 30 days\n✓ Proof of accommodation in Thailand\n✓ Cash/Funds of at least 10,000 THB per person (20,000 THB per family)",
        "entry_requirements": "Immigration entry stamp at Bangkok (BKK) / Phuket (HKT).",
        "transit_requirements": "Transit without visa for under 12 hours with confirmed onward booking.",
        "important_notes": "Requirements may change. Verify with official government/embassy sources before travel.",
        "official_source_url": "https://www.thaievisa.go.th/"
    },
    {
        "origin_country": "India",
        "destination_country": "Maldives",
        "visa_required": "Visa on Arrival (Free)",
        "visa_type": "Free 30-day Tourist Visa on Arrival",
        "passport_validity": "Minimum 1 month (6 months recommended)",
        "documents_required": "✓ Machine-readable Passport\n✓ IMUGA Traveller Declaration (online within 96 hrs)\n✓ Prepaid hotel / resort booking confirmation\n✓ Confirmed return ticket\n✓ Proof of sufficient funds ($100 + $50/day)",
        "entry_requirements": "Submit IMUGA health & declaration form online within 96 hours before arrival at Velana International (MLE).",
        "transit_requirements": "Direct transit permitted.",
        "important_notes": "Requirements may change. Verify with official government/embassy sources before travel.",
        "official_source_url": "https://immigration.gov.mv/tourist-visa/"
    },
    {
        "origin_country": "India",
        "destination_country": "United States",
        "visa_required": "Required",
        "visa_type": "B1/B2 Visitor Visa",
        "passport_validity": "Minimum 6 months beyond intended stay",
        "documents_required": "✓ Valid US Nonimmigrant Visa foil in Passport\n✓ Valid Passport\n✓ Return flight booking\n✓ US accommodation details / host address\n✓ Customs and Border Protection declaration",
        "entry_requirements": "CBP biometric inspection upon arrival at JFK, LAX, SFO, or first US port of entry.",
        "transit_requirements": "C-1 Transit Visa required for transit through US airports.",
        "important_notes": "Requirements may change. Verify with official government/embassy sources before travel.",
        "official_source_url": "https://travel.state.gov/content/travel/en/us-visas/tourism-visit/visitor.html"
    },
    {
        "origin_country": "India",
        "destination_country": "France",
        "visa_required": "Required",
        "visa_type": "Schengen Short-Stay Visa (Type C)",
        "passport_validity": "Minimum 3 months beyond intended departure from Schengen area",
        "documents_required": "✓ Valid Passport (issued within last 10 years)\n✓ Approved Schengen Visa\n✓ Travel Medical Insurance (min €30,000 coverage)\n✓ Confirmed return flight\n✓ Hotel vouchers / Proof of stay\n✓ Sufficient subsistence funds (€65-€120/day)",
        "entry_requirements": "Entry via Paris CDG / Orly border control. Valid for travel across all 29 Schengen member states.",
        "transit_requirements": "Airport Transit Visa (ATV) required unless holding valid US/UK/Canada visa.",
        "important_notes": "Requirements may change. Verify with official government/embassy sources before travel.",
        "official_source_url": "https://france-visas.gouv.fr/"
    }
]

def seed_travel_requirements():
    """Populates default travel requirements into database if not present."""
    for req in DEFAULT_REQUIREMENTS:
        TravelRequirement.objects.update_or_create(
            origin_country=req["origin_country"],
            destination_country=req["destination_country"],
            defaults=req
        )

def get_travel_requirements(origin_country, dest_country):
    """Retrieve travel requirements for origin -> destination country pair."""
    # Ensure baseline data exists
    if not TravelRequirement.objects.exists():
        seed_travel_requirements()

    # Normalization
    origin = origin_country.strip() if origin_country else "India"
    dest = dest_country.strip() if dest_country else "India"

    if origin.lower() == dest.lower():
        return {
            "origin_country": origin,
            "destination_country": dest,
            "is_domestic": True,
            "visa_required": "Not Required (Domestic)",
            "visa_type": "Domestic Travel - No Visa",
            "passport_validity": "Govt Photo ID (Aadhaar / Voter ID / Passport / Driving License)",
            "documents_required": "✓ Government Photo ID\n✓ Boarding Pass / E-Ticket",
            "entry_requirements": "Standard domestic security check at departure terminal.",
            "transit_requirements": "No transit requirements.",
            "important_notes": "Carry original valid government-issued photo ID.",
            "official_source_url": "https://www.civilaviation.gov.in/",
            "disclaimer": "Requirements may change. Verify with official government/airline sources."
        }

    # Search database
    record = TravelRequirement.objects.filter(
        origin_country__iexact=origin,
        destination_country__iexact=dest,
        is_active=True
    ).first()

    if not record:
        # Fallback to general international requirement template
        return {
            "origin_country": origin,
            "destination_country": dest,
            "is_domestic": False,
            "visa_required": "Required / Verify with Embassy",
            "visa_type": "Tourist / Business Visa",
            "passport_validity": "Minimum 6 months recommended from travel date",
            "documents_required": "✓ Valid Passport (min 6 months validity)\n✓ Valid Visa / Entry Permit\n✓ Confirmed Return or Onward Ticket\n✓ Proof of Accommodation & Sufficient Funds",
            "entry_requirements": "Standard immigration and customs inspection upon arrival.",
            "transit_requirements": "Check with operating airline for transit visa rules if connecting flights.",
            "important_notes": "Requirements may change. Verify with official government/embassy sources.",
            "official_source_url": "https://www.iatatravelcentre.com/",
            "disclaimer": "Requirements may change. Verify with official government/embassy sources."
        }

    return {
        "origin_country": record.origin_country,
        "destination_country": record.destination_country,
        "is_domestic": False,
        "visa_required": record.visa_required,
        "visa_type": record.visa_type,
        "passport_validity": record.passport_validity,
        "documents_required": record.documents_required,
        "entry_requirements": record.entry_requirements,
        "transit_requirements": record.transit_requirements,
        "important_notes": record.important_notes,
        "official_source_url": record.official_source_url,
        "disclaimer": "Requirements may change. Verify with official government/embassy sources.",
        "last_updated": record.last_updated.strftime("%Y-%m-%d") if record.last_updated else None
    }
