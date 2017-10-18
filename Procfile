release: python manage.py migrate
web: gunicorn --workers=2 s4j.wsgi --timeout 600

