release: python manage.py migrate
web: gunicorn s4j.wsgi --timeout 600
ps: scale web=2 worker=2

