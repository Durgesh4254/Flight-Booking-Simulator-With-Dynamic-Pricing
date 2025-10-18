import uuid
from django.db import models
from django.utils import timezone

class Flight(models.Model):
    origin = models.CharField(max_length=50)
    destination = models.CharField(max_length=50)
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_seats = models.IntegerField(default=100)
    available_seats = models.IntegerField(default=100)
    demand_factor = models.FloatField(default=1.0)  # simulated demand

    def __str__(self):
        return f"{self.origin} → {self.destination} ({self.departure_time.strftime('%Y-%m-%d %H:%M')})"
 ##------------------------------------------------------------   
## Milestone 3 additions
##---------------------------------------------------------------
class Passenger(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Booking(models.Model):
    STATUS_PENDING = 'PENDING'    
    STATUS_CONFIRMED = 'CONFIRMED'
    STATUS_FAILED = 'FAILED'     
    STATUS_CANCELLED = 'CANCELLED'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_CONFIRMED, 'Confirmed'),
        (STATUS_FAILED, 'Failed'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]

    pnr = models.CharField(max_length=12, unique=True, db_index=True)
    flight = models.ForeignKey('Flight', on_delete=models.PROTECT, related_name='bookings')
    passenger = models.ForeignKey(Passenger, on_delete=models.CASCADE, related_name='bookings')
    seat_number = models.CharField(max_length=10, null=True, blank=True)
    booked_seats = models.IntegerField(default=1)   # number of seats held
    price_paid = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"PNR {self.pnr} - {self.flight.origin}->{self.flight.destination} ({self.status})"


class FareHistory(models.Model):
    flight = models.ForeignKey('Flight', on_delete=models.CASCADE, related_name='fare_history')
    timestamp = models.DateTimeField(auto_now_add=True)
    fare = models.DecimalField(max_digits=10, decimal_places=2)
    seats_available = models.IntegerField()

    def __str__(self):
        return f"{self.flight} @ {self.timestamp}: {self.fare}"
