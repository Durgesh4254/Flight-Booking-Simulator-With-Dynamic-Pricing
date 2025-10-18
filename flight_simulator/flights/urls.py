
from django.urls import path
from .views import (
    BeginBookingView,
    ConfirmBookingView,
    CancelBookingView,
    BookingHistoryView,
)

urlpatterns = [
    path('book/begin/', BeginBookingView.as_view(), name='begin-booking'),
    path('book/confirm/', ConfirmBookingView.as_view(), name='confirm-booking'),
    path('book/cancel/', CancelBookingView.as_view(), name='cancel-booking'),
    path('book/history/', BookingHistoryView.as_view(), name='booking-history'),
]
