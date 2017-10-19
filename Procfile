release: python manage.py migrate
web: gunicorn --worker-class=gthread --workers=2 --threads=4 s4j.wsgi --timeout 600

