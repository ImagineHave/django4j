release: python manage.py migrate  --run-syncdb
web: gunicorn --worker-class=gthread --workers=4 --threads=12 --timeout=1200 s4j.wsgi --config gunicorn.conf

