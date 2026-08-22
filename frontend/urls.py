from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('destinations/', views.destinations_view, name='destinations'),
    path('deals/', views.deals_view, name='deals'),
    path('about/', views.about_view, name='about'),
    path('verify/<str:pnr>/', views.verify_ticket_view, name='ticket_verify'),
    
    # Company Pages
    path('careers/', views.careers_view, name='careers'),
    path('press/', views.press_view, name='press'),
    path('contact/', views.contact_view, name='contact'),
    
    # Support Pages
    path('help/', views.help_view, name='help'),
    path('faqs/', views.faqs_view, name='faqs'),
    path('booking-support/', views.booking_support_view, name='booking_support'),
    path('baggage-info/', views.baggage_info_view, name='baggage_info'),
    
    # Explore Pages
    path('airlines/', views.airlines_view, name='airlines'),
    path('flight-status/', views.flight_status_view, name='flight_status'),
    
    # Legal Pages
    path('privacy/', views.privacy_view, name='privacy'),
    path('terms/', views.terms_view, name='terms'),
    path('refund/', views.refund_view, name='refund'),
    path('security/', views.security_view, name='security'),
    
    # Auth & Dashboard
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('my-trips/', views.dashboard_view, name='my_trips'),
    
    # Direct admin route aliases
    path('admin/login/', lambda r: redirect('/admin-portal/login/'), name='admin_login_alias'),
    path('admin/logout/', lambda r: redirect('/admin-portal/logout/'), name='admin_logout_alias'),
    path('admin/dashboard/', lambda r: redirect('/admin-portal/dashboard/')),
    path('admin/flights/', lambda r: redirect('/admin-portal/flights/')),
    path('admin/pricing/', lambda r: redirect('/admin-portal/pricing/')),
    path('admin/bookings/', lambda r: redirect('/admin-portal/bookings/')),
    path('admin/users/', lambda r: redirect('/admin-portal/users/')),
    path('admin/deals/', lambda r: redirect('/admin-portal/deals/')),
    path('admin/analytics/', lambda r: redirect('/admin-portal/dashboard/')),
]
