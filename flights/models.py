import uuid
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
import string
import random

class Airline(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    logo_url = models.URLField(blank=True, null=True)
    fleet_size = models.IntegerField(default=50)
    cabin_classes = models.CharField(max_length=150, default="Economy, Premium Economy, Business, First")
    baggage_policy = models.TextField(blank=True, default="Cabin: 7kg | Check-in: 15kg (Domestic), 25kg (Intl)")
    contact_email = models.EmailField(blank=True, null=True, default="support@airline.com")
    contact_phone = models.CharField(max_length=30, blank=True, null=True, default="+91 1800-102-3456")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.code})"

class Airport(models.Model):
    CATEGORY_CHOICES = [
        ('CITY', 'Metropolitan / City'),
        ('BEACH', 'Beach & Coastal'),
        ('MOUNTAINS', 'Hills & Mountains'),
        ('HERITAGE', 'Heritage & Culture'),
        ('ADVENTURE', 'Adventure & Nature'),
        ('INTERNATIONAL', 'Global Gateway'),
    ]

    code = models.CharField(max_length=10, unique=True) # IATA
    icao_code = models.CharField(max_length=10, blank=True, null=True)
    name = models.CharField(max_length=150)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    country_code = models.CharField(max_length=10, default="IN")
    region = models.CharField(max_length=100, default="Asia")
    terminal = models.CharField(max_length=50, default="T1/T2")
    timezone = models.CharField(max_length=50, default="UTC+05:30")
    is_international = models.BooleanField(default=False)
    latitude = models.FloatField(default=20.5937)
    longitude = models.FloatField(default=78.9629)
    popularity = models.IntegerField(default=85) # 1-100 score
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='CITY')
    avg_fare = models.DecimalField(max_digits=10, decimal_places=2, default=4500.00)
    best_season = models.CharField(max_length=100, default="Oct - Mar")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.city} ({self.code}) - {self.name}"

class Aircraft(models.Model):
    model_name = models.CharField(max_length=100)
    manufacturer = models.CharField(max_length=100)
    economy_seats = models.IntegerField(default=150)
    business_seats = models.IntegerField(default=30)
    first_class_seats = models.IntegerField(default=10)

    @property
    def total_capacity(self):
        return self.economy_seats + self.business_seats + self.first_class_seats

    def __str__(self):
        return self.model_name

class Flight(models.Model):
    STATUS_CHOICES = [
        ('SCHEDULED', 'Scheduled'),
        ('BOARDING', 'Boarding'),
        ('DEPARTED', 'Departed'),
        ('IN_FLIGHT', 'In Flight'),
        ('LANDED', 'Landed'),
        ('DELAYED', 'Delayed'),
        ('CANCELLED', 'Cancelled'),
        ('COMPLETED', 'Completed'),
    ]

    flight_number = models.CharField(max_length=20, unique=True, default=uuid.uuid4)
    airline = models.ForeignKey(Airline, on_delete=models.CASCADE, null=True)
    aircraft = models.ForeignKey(Aircraft, on_delete=models.SET_NULL, null=True)
    origin = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name='departures', null=True)
    destination = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name='arrivals', null=True)
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Keeping these for backward compatibility in algorithms
    total_seats = models.IntegerField(default=100)
    available_seats = models.IntegerField(default=100)
    demand_factor = models.FloatField(default=1.0)
    
    # Admin controls
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SCHEDULED')
    manual_override_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    min_fare_limit = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    max_fare_limit = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        orig_code = self.origin.code if self.origin else "N/A"
        dest_code = self.destination.code if self.destination else "N/A"
        return f"{self.flight_number}: {orig_code} → {dest_code}"

class Seat(models.Model):
    CLASS_CHOICES = [
        ('ECONOMY', 'Economy'),
        ('PREMIUM_ECONOMY', 'Premium Economy'),
        ('BUSINESS', 'Business'),
        ('FIRST', 'First Class'),
    ]
    STATUS_CHOICES = [
        ('AVAILABLE', 'Available'),
        ('SELECTED', 'Selected'),
        ('OCCUPIED', 'Occupied'),
        ('BLOCKED', 'Blocked'),
    ]
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, related_name='seats')
    seat_number = models.CharField(max_length=5) # e.g. 12A
    seat_class = models.CharField(max_length=20, choices=CLASS_CHOICES, default='ECONOMY')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='AVAILABLE')
    is_window = models.BooleanField(default=False)
    is_aisle = models.BooleanField(default=False)
    extra_legroom = models.BooleanField(default=False)
    price_override = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.flight.flight_number} - {self.seat_number} ({self.status})"

class Passenger(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='saved_passengers')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    dob = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=20, null=True, blank=True)
    passport_id = models.CharField(max_length=50, null=True, blank=True)
    nationality = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Coupon(models.Model):
    code = models.CharField(max_length=20, unique=True)
    discount_percent = models.FloatField(default=0.0) 
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00) 
    valid_until = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.code

class Deal(models.Model):
    CATEGORY_CHOICES = [
        ('WEEKEND', 'Weekend Deals'),
        ('DOMESTIC', 'Domestic Offers'),
        ('INTERNATIONAL', 'International Offers'),
        ('BUSINESS', 'Business Class Deals'),
        ('STUDENT', 'Student Offers'),
        ('FAMILY', 'Family Offers'),
        ('LASTMINUTE', 'Last-Minute Deals'),
        ('BEACH', 'Beach Escapes'),
        ('CITY', 'City Breaks'),
        ('HERITAGE', 'Heritage Tours'),
        ('ADVENTURE', 'Adventure'),
    ]
    DISCOUNT_TYPE_CHOICES = [
        ('PERCENT', 'Percentage (%)'),
        ('FIXED', 'Fixed Amount (₹)'),
    ]
    TRIP_TYPE_CHOICES = [
        ('BOTH', 'One Way & Round Trip'),
        ('ONE_WAY', 'One Way Only'),
        ('ROUND_TRIP', 'Round Trip Only'),
    ]

    title = models.CharField(max_length=150)
    code = models.CharField(max_length=30, unique=True)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='DOMESTIC')
    badge = models.CharField(max_length=50, default='🔥 Special Deal')
    description = models.TextField()
    
    discount_type = models.CharField(max_length=10, choices=DISCOUNT_TYPE_CHOICES, default='PERCENT')
    discount_percent = models.FloatField(default=10.0)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2, default=500.00)
    max_discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=5000.00)
    min_booking_amount = models.DecimalField(max_digits=10, decimal_places=2, default=2000.00)
    
    # Targeting filters
    origin_code = models.CharField(max_length=10, blank=True, null=True, help_text="Specific origin or empty for any")
    destination_code = models.CharField(max_length=10, blank=True, null=True, help_text="Specific destination or empty for any")
    applicable_airlines = models.CharField(max_length=200, blank=True, null=True, help_text="Comma-separated airline codes or blank for all")
    applicable_flights = models.CharField(max_length=300, blank=True, null=True, help_text="Comma-separated flight numbers or blank for all")
    applicable_destinations = models.TextField(blank=True, null=True, help_text="Comma-separated destination codes")
    
    starting_price = models.DecimalField(max_digits=10, decimal_places=2, default=2999.00)
    valid_from = models.DateTimeField(default=timezone.now)
    valid_until = models.DateTimeField()
    travel_start_date = models.DateField(null=True, blank=True)
    travel_end_date = models.DateField(null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    min_passengers = models.IntegerField(default=1)
    max_passengers = models.IntegerField(default=9)
    required_class = models.CharField(max_length=20, blank=True, null=True, help_text="e.g. BUSINESS, FIRST, ECONOMY or null")
    trip_type = models.CharField(max_length=20, choices=TRIP_TYPE_CHOICES, default='BOTH')
    is_international_only = models.BooleanField(default=False)
    usage_limit = models.IntegerField(default=500)
    per_user_limit = models.IntegerField(default=2)
    terms = models.TextField(blank=True, default="Valid for limited time. Applicable on select routes. Subject to seat availability.")
    countdown_hours = models.IntegerField(default=48, help_text="Simulated countdown hours")

    # Performance tracking
    views_count = models.IntegerField(default=0)
    applied_count = models.IntegerField(default=0)
    bookings_count = models.IntegerField(default=0)
    total_discount_given = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    revenue_generated = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.title} ({self.code}) - {self.discount_percent}% OFF"

class PricingRule(models.Model):
    name = models.CharField(max_length=100, default="Standard Dynamic Rule")
    is_active = models.BooleanField(default=True)
    
    min_fare_floor = models.DecimalField(max_digits=10, decimal_places=2, default=1500.00)
    max_fare_cap = models.DecimalField(max_digits=10, decimal_places=2, default=45000.00)
    
    demand_multiplier_weight = models.FloatField(default=1.10, help_text="Weight for demand curve")
    seat_availability_weight = models.FloatField(default=1.20, help_text="Weight for seat scarcity")
    time_to_departure_weight = models.FloatField(default=1.15, help_text="Weight for approaching departure")
    peak_season_multiplier = models.FloatField(default=1.20, help_text="Peak holiday multiplier")
    weekend_multiplier = models.FloatField(default=1.15, help_text="Fri-Sun travel multiplier")
    holiday_multiplier = models.FloatField(default=1.25, help_text="Special festive travel")
    
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.name} (Active: {self.is_active})"

class Booking(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('FAILED', 'Failed'),
        ('CANCELLED', 'Cancelled'),
        ('REFUND_PROCESSING', 'Refund Processing'),
        ('COMPLETED', 'Completed')
    ]

    pnr = models.CharField(max_length=12, unique=True, db_index=True)
    ticket_number = models.CharField(max_length=20, unique=True, null=True, blank=True, db_index=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='bookings')
    flight = models.ForeignKey(Flight, on_delete=models.PROTECT, related_name='bookings')
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)
    deal = models.ForeignKey(Deal, on_delete=models.SET_NULL, null=True, blank=True, related_name='bookings')
    deal_title = models.CharField(max_length=150, blank=True, null=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    original_fare = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Deprecated for new multi-passenger structure, but kept to prevent breaking existing views instantly
    passenger = models.ForeignKey(Passenger, on_delete=models.CASCADE, related_name='old_bookings', null=True) 
    seat_number = models.CharField(max_length=255, null=True, blank=True) 
    
    booked_seats = models.IntegerField(default=1)   
    price_paid = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    # Cancellation & Refund tracking
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancellation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    refund_status = models.CharField(max_length=30, default='NONE', choices=[
        ('NONE', 'None'),
        ('REQUESTED', 'Requested'),
        ('PROCESSING', 'Processing'),
        ('COMPLETED', 'Completed'),
        ('REJECTED', 'Rejected'),
        ('FAILED', 'Failed')
    ])
    refund_method = models.CharField(max_length=50, blank=True, null=True)
    refund_notes = models.TextField(blank=True, null=True)

    # Insurance & Services tracking
    has_insurance = models.BooleanField(default=False)
    insurance_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    terminal = models.CharField(max_length=20, default="T1")
    gate = models.CharField(max_length=20, default="A12")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        orig = self.flight.origin.code if self.flight.origin else "N/A"
        dest = self.flight.destination.code if self.flight.destination else "N/A"
        return f"PNR {self.pnr} - {orig}->{dest} ({self.status})"

class PriceAlert(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='price_alerts')
    email = models.EmailField()
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, null=True, blank=True, related_name='price_alerts')
    origin = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name='departure_alerts')
    destination = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name='arrival_alerts')
    travel_date = models.DateField()
    cabin_class = models.CharField(max_length=20, default='ECONOMY')
    target_price = models.DecimalField(max_digits=10, decimal_places=2)
    initial_price = models.DecimalField(max_digits=10, decimal_places=2)
    current_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_triggered = models.BooleanField(default=False)
    triggered_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Alert for {self.email}: {self.origin.code}→{self.destination.code} @ ₹{self.target_price}"

class TravelRequirement(models.Model):
    origin_country = models.CharField(max_length=100, default="India")
    destination_country = models.CharField(max_length=100)
    visa_required = models.CharField(max_length=50, default="Required") # Required, Visa on Arrival, Visa Free, eVisa
    visa_type = models.CharField(max_length=100, default="Tourist / Electronic Visa")
    passport_validity = models.CharField(max_length=100, default="Minimum 6 months from travel date")
    documents_required = models.TextField(default="Valid Passport, Confirmed Return Ticket, Hotel Booking / Accommodation Proof, Proof of Funds")
    entry_requirements = models.TextField(default="Customs declaration upon entry, health declaration if applicable.")
    transit_requirements = models.TextField(default="Transit visa required if leaving airport international transit area.")
    important_notes = models.TextField(default="Travel requirements may change without prior notice. Verify with official government/embassy sources.")
    official_source_url = models.URLField(blank=True, null=True, default="https://www.iatatravelcentre.com/")
    is_active = models.BooleanField(default=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.origin_country} → {self.destination_country} ({self.visa_required})"

class ServiceHealthLog(models.Model):
    service_name = models.CharField(max_length=100) # Groq AI, Weather API, Email Service, Database, Dynamic Pricing, Flight Tracking, Payment Gateway
    status = models.CharField(max_length=30, default="OPERATIONAL") # OPERATIONAL, DEGRADED, DOWN
    latency_ms = models.FloatField(default=0.0)
    last_successful_request = models.DateTimeField(null=True, blank=True)
    last_error = models.TextField(blank=True, null=True)
    error_count = models.IntegerField(default=0)
    uptime_pct = models.FloatField(default=99.9)
    checked_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.service_name}: {self.status} ({self.latency_ms:.1f}ms)"


class BookingPassenger(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='booking_passengers')
    passenger = models.ForeignKey(Passenger, on_delete=models.PROTECT)
    seat = models.ForeignKey(Seat, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.passenger} on {self.booking.pnr}"

class FareHistory(models.Model):
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, related_name='fare_history')
    timestamp = models.DateTimeField(auto_now_add=True)
    fare = models.DecimalField(max_digits=10, decimal_places=2)
    seats_available = models.IntegerField()
    reason = models.CharField(max_length=200, default="Dynamic Calculation")

    def __str__(self):
        return f"{self.flight} @ {self.timestamp}: {self.fare}"

class Payment(models.Model):
    METHOD_CHOICES = [
        ('UPI', 'UPI'),
        ('CARD', 'Credit/Debit Card'),
        ('NET_BANKING', 'Net Banking'),
        ('WALLET', 'Wallet'),
        ('COUNTER', 'Pay at Counter'),
    ]
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
        ('REFUNDED', 'Refunded'),
    ]
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='payments', null=True, blank=True)
    payment_id = models.CharField(max_length=50, unique=True, db_index=True)
    method = models.CharField(max_length=20, choices=METHOD_CHOICES, default='CARD')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    gateway_response = models.JSONField(blank=True, null=True)
    card_last4 = models.CharField(max_length=4, blank=True, null=True)
    upi_id = models.CharField(max_length=100, blank=True, null=True)
    bank_name = models.CharField(max_length=100, blank=True, null=True)
    wallet_provider = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.payment_id} - {self.method} - {self.status}"

class AdminActivityLog(models.Model):
    ACTION_CHOICES = [
        ('FLIGHT_CREATE', 'Flight Created'),
        ('FLIGHT_UPDATE', 'Flight Updated'),
        ('FLIGHT_DISABLE', 'Flight Disabled'),
        ('PRICE_OVERRIDE', 'Price Override Applied'),
        ('BULK_PRICE_CHANGE', 'Bulk Price Adjustment'),
        ('PRICING_RULE_CHANGE', 'Pricing Rule Modified'),
        ('DEAL_CREATE', 'Deal Created'),
        ('DEAL_UPDATE', 'Deal Updated'),
        ('DEAL_DUPLICATE', 'Deal Duplicated'),
        ('DEAL_DISABLE', 'Deal Disabled'),
        ('SEAT_BLOCK', 'Seat Blocked/Unblocked'),
        ('BOOKING_CANCEL', 'Booking Cancelled by Admin'),
        ('REFUND_APPROVE', 'Refund Approved'),
        ('REFUND_REJECT', 'Refund Rejected'),
        ('AIRPORT_MODIFY', 'Airport Modified'),
        ('AIRLINE_MODIFY', 'Airline Modified'),
        ('USER_STATUS_CHANGE', 'User Status Changed'),
    ]
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action_type = models.CharField(max_length=40, choices=ACTION_CHOICES)
    entity_type = models.CharField(max_length=50, default="General")
    entity_id = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField()
    previous_value = models.TextField(blank=True, null=True)
    new_value = models.TextField(blank=True, null=True)
    ip_address = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.created_at.strftime('%Y-%m-%d %H:%M')}] {self.action_type} by {self.user}"

class AdminAlert(models.Model):
    LEVEL_CHOICES = [
        ('INFO', 'Informational 🟢'),
        ('WARNING', 'Warning 🟡'),
        ('HIGH', 'High Priority 🟠'),
        ('CRITICAL', 'Critical Alert 🔴'),
    ]
    alert_level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='INFO')
    title = models.CharField(max_length=150)
    message = models.TextField()
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, null=True, blank=True)
    deal = models.ForeignKey(Deal, on_delete=models.CASCADE, null=True, blank=True)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, null=True, blank=True)
    action_recommended = models.CharField(max_length=200, blank=True, null=True)
    is_read = models.BooleanField(default=False)
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.alert_level}: {self.title}"

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    rating = models.IntegerField(default=5)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.user} ({self.rating}/5)"

