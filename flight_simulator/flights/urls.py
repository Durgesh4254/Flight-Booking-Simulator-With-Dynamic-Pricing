
from django.urls import path
from .views import (
    FlightSearchView,
    BeginBookingView,
    ConfirmBookingView,
    CancelBookingView,
    BookingHistoryView
)

urlpatterns = [
    path('search/', FlightSearchView.as_view(), name='flight-search'),
    path('book/begin/', BeginBookingView.as_view(), name='begin-booking'),
    path('book/confirm/', ConfirmBookingView.as_view(), name='confirm-booking'),
    path('book/cancel/', CancelBookingView.as_view(), name='cancel-booking'),
    path('bookings/', BookingHistoryView.as_view(), name='booking-history'),
]
