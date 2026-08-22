from django.contrib import admin
from .models import (
    Airline, Airport, Aircraft, Flight, Seat, Passenger, Coupon,
    Deal, Booking, BookingPassenger, FareHistory, Review, Payment
)

@admin.register(Airline)
class AirlineAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')

@admin.register(Airport)
class AirportAdmin(admin.ModelAdmin):
    list_display = ('code', 'city', 'country')
    search_fields = ('code', 'city')

@admin.register(Aircraft)
class AircraftAdmin(admin.ModelAdmin):
    list_display = ('model_name', 'manufacturer', 'total_capacity')

@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = ('flight_number', 'origin', 'destination', 'departure_time', 'base_price')
    list_filter = ('origin', 'destination', 'departure_time')

@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    list_display = ('flight', 'seat_number', 'seat_class', 'status')
    list_filter = ('seat_class', 'status')

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_percent', 'discount_amount', 'is_active', 'valid_until')

@admin.register(Deal)
class DealAdmin(admin.ModelAdmin):
    list_display = ('title', 'code', 'category', 'discount_percent', 'starting_price', 'is_active', 'valid_until')
    list_filter = ('category', 'is_active', 'is_international_only')
    search_fields = ('title', 'code')

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('pnr', 'user', 'flight', 'status', 'price_paid', 'deal_title', 'discount_amount', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('pnr', 'deal_title')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('payment_id', 'booking', 'method', 'status', 'amount', 'created_at')
    list_filter = ('method', 'status', 'created_at')
    search_fields = ('payment_id', 'transaction_id', 'booking__pnr')
    readonly_fields = ('payment_id',)
    raw_id_fields = ('booking',)

admin.site.register(Passenger)
admin.site.register(BookingPassenger)
admin.site.register(FareHistory)
admin.site.register(Review)
