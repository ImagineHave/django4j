release: python manage.py migrate
web: gunicorn s4j.wsgi --timeout 600
ps: web=2 worker=2

