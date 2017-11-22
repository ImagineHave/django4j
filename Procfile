release: python manage.py migrate
web: gunicorn --worker-class=gthread --workers=4 --threads=8 s4j.wsgi --timeout 600 --config gunicorn.conf

