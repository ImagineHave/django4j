release: python manage.py migrate  --run-syncdb
web: gunicorn --worker-class=gthread --workers=2 --threads=2 --timeout=1200 s4j.wsgi --config gunicorn.conf

