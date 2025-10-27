# Flight Simulator

This is a Django-based flight simulator application.

## Project Structure

- `flight_simulator/`: The main Django project directory.
- `flights/`: A Django app to manage flight data and logic.
- `frontend/`: A Django app to serve the user interface.
- `manage.py`: The Django management script.


## File Structure

```
├── README.md
├── db.sqlite3
├── flight_simulator/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── flights/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── migrations/
│   ├── models.py
│   ├── pricing.py
│   ├── tests.py
│   ├── urls.py
│   ├── utils.py
│   └── views.py
├── frontend/
│   ├── static/
│   │   ├── script.js
│   │   └── style.css
│   ├── templates/
│   │   └── index.html
│   ├── urls.py
│   └── views.py
├── manage.py
└── requirements.txt
```
## Features

- Search for flights between two airports on a given date.
- Real-time pricing simulation that adjusts based on demand.
- Book flights and view booking history.
- Cancel bookings.

## API Endpoints

The following API endpoints are available:

- `GET /flights/search/`: Search for flights.
- `POST /flights/book/begin/`: Begin the booking process.
- `POST /flights/book/confirm/`: Confirm a booking.
- `POST /flights/book/cancel/`: Cancel a booking.
- `GET /flights/bookings/`: View booking history.

## Models

The application uses the following models:

- Flight: Represents a flight with an origin, destination, departure/arrival times, price, and seat availability.
- Passenger: Represents a passenger with their contact information.
- Booking: Represents a booking made by a passenger for a specific flight.
- FareHistory: Tracks the fare changes for a flight over time.

## Middleware

The application uses the following middleware:

- `django.middleware.security.SecurityMiddleware`: Provides several security enhancements to the request/response cycle.
- `django.contrib.sessions.middleware.SessionMiddleware`: Enables session functionality.
- `django.middleware.common.CommonMiddleware`: Provides various conveniences, including forbidding access to user agents in the `DISALLOWED_USER_AGENTS` setting, and performing URL rewriting based on the `APPEND_SLASH` and `PREPEND_WWW` settings.
- `django.middleware.csrf.CsrfViewMiddleware`: Adds protection against Cross-Site Request Forgeries.
- `django.contrib.auth.middleware.AuthenticationMiddleware`: Adds the `user` attribute, representing the currently-logged-in user, to every incoming `HttpRequest` object.
- `django.contrib.messages.middleware.MessageMiddleware`: Enables cookie- and session-based messaging.
- `django.middleware.clickjacking.XFrameOptionsMiddleware`: Provides clickjacking protection via the `X-Frame-Options` header.

## Templates

The application uses a single template, `index.html`, which serves as the main user interface for searching, booking, and managing flights.

## Static Files

The application uses the following static files:

- `style.css`: The main stylesheet for the application.
- `script.js`: The main JavaScript file for the application.

## Deployment

To deploy the application in a production environment, follow these steps:

1.  Disable debug mode:In `flight_simulator/settings.py`, set `DEBUG = False`.
2.  Configure allowed hosts: In `flight_simulator/settings.py`, set `ALLOWED_HOSTS` to a list of the domains that will host the application.
3.  ##Set a secret key:## In `flight_simulator/settings.py`, replace the default `SECRET_KEY` with a unique, randomly generated key.
4.  ##Collect static files:## Run `python manage.py collectstatic` to collect all static files into a single directory.
5.  ##Use a production web server:## Use a production-ready web server such as Gunicorn or uWSGI to serve the application.

## Testing

To run the test suite, use the following command:
python manage.py runserver


## Getting Started

1. **Install dependencies:**

   pip install -r requirements.txt

2. **Run migrations:**

   python manage.py migrate
 
3. **Start the development server:**

   python manage.py runserver
