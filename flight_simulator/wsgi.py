"""
WSGI config for flight_simulator project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flight_simulator.settings')

application = get_wsgi_application()
app = application

# Auto-initialize SQLite database & seed data on Vercel cold starts
if os.environ.get('VERCEL'):
    try:
        from django.core.management import call_command
        from flights.models import Airport
        
        # Check if database tables exist and are populated
        if not Airport.objects.exists():
            call_command('migrate', interactive=False)
            try:
                from seed_db import seed
                seed()
            except Exception as se:
                print(f"[Vercel] Seed error: {se}")
    except Exception as e:
        try:
            from django.core.management import call_command
            call_command('migrate', interactive=False)
            try:
                from seed_db import seed
                seed()
            except Exception as se:
                print(f"[Vercel] Seed fallback error: {se}")
        except Exception as ex:
            print(f"[Vercel] DB auto-migration error: {ex}")
