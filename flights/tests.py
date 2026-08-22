from django.test import TestCase, Client
from django.utils import timezone
from datetime import timedelta, date
from decimal import Decimal
import json
from .models import Airline, Airport, Aircraft, Flight, Seat, Booking, Passenger, Coupon

class PassengerDetailsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.airline = Airline.objects.create(name="FlyEase Airways", code="FE")
        self.origin = Airport.objects.create(code="BOM", name="Chhatrapati Shivaji Maharaj Intl", city="Mumbai", country="India")
        self.dest = Airport.objects.create(code="DEL", name="Indira Gandhi Intl", city="Delhi", country="India")
        self.aircraft = Aircraft.objects.create(model_name="Airbus A320", economy_seats=150)
        
        now = timezone.now()
        self.flight = Flight.objects.create(
            flight_number="FE-1024",
            airline=self.airline,
            aircraft=self.aircraft,
            origin=self.origin,
            destination=self.dest,
            departure_time=now + timedelta(days=2),
            arrival_time=now + timedelta(days=2, hours=2),
            base_price=Decimal("5000.00"),
            total_seats=100,
            available_seats=100
        )
        
        # Create seats
        self.seat_12a = Seat.objects.create(flight=self.flight, seat_number="12A", seat_class="ECONOMY", status="AVAILABLE")
        self.seat_12b = Seat.objects.create(flight=self.flight, seat_number="12B", seat_class="ECONOMY", status="AVAILABLE")
        
        # Create coupon
        self.coupon = Coupon.objects.create(
            code="FLYEASE10",
            discount_percent=10.0,
            valid_until=now + timedelta(days=10),
            is_active=True
        )

    def test_flight_search(self):
        date_str = (timezone.now() + timedelta(days=2)).strftime('%Y-%m-%d')
        response = self.client.get(f'/flights/search/?origin=BOM&destination=DEL&departure_date={date_str}&passengers=2')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('offers', data)
        self.assertTrue(len(data['offers']) > 0)

    def test_seat_map(self):
        response = self.client.get(f'/flights/seats/{self.flight.id}/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['flight_id'], self.flight.id)
        self.assertTrue(len(data['seats']) >= 2)

    from unittest.mock import patch

    @patch('flights.views.simulate_payment')
    def test_confirm_booking_with_multiple_passengers_and_services(self, mock_payment):
        mock_payment.return_value = {"success": True, "transaction_id": "TXN123456789"}
        payload = {
            "itinerary": [{
                "flight_id": self.flight.id,
                "class": "ECONOMY",
                "extra_fees": 0,
                "seats_list": ["12A", "12B"]
            }],
            "passengers": [
                {
                    "first_name": "Aryan",
                    "last_name": "Sharma",
                    "email": "aryan@example.com",
                    "phone": "+919876543210",
                    "dob": "1995-05-15",
                    "gender": "MALE",
                    "passport_id": "P1234567",
                    "nationality": "Indian"
                },
                {
                    "first_name": "Rohan",
                    "last_name": "Sharma",
                    "email": "",
                    "phone": "",
                    "dob": "2000-08-20",
                    "gender": "MALE",
                    "passport_id": "P7654321",
                    "nationality": "Indian"
                }
            ],
            "services": ["baggage", "insurance"],
            "coupon": "FLYEASE10"
        }
        
        response = self.client.post(
            '/flights/book/confirm/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIn('pnr', data)
        
        # Verify database models
        booking = Booking.objects.get(pnr=data['pnr'])
        self.assertEqual(booking.booked_seats, 2)
        self.assertEqual(booking.status, 'CONFIRMED')
        
        # Verify passengers created with extended fields
        passengers = Passenger.objects.filter(first_name__in=["Aryan", "Rohan"])
        self.assertEqual(passengers.count(), 2)
        
        aryan = Passenger.objects.get(first_name="Aryan")
        self.assertEqual(aryan.gender, "MALE")
        self.assertEqual(aryan.passport_id, "P1234567")
        self.assertEqual(aryan.nationality, "Indian")
        self.assertEqual(str(aryan.dob), "1995-05-15")
        
        # Verify seats reserved
        self.seat_12a.refresh_from_db()
        self.seat_12b.refresh_from_db()
        self.assertEqual(self.seat_12a.status, 'OCCUPIED')
        self.assertEqual(self.seat_12b.status, 'OCCUPIED')
