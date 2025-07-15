python -m venv .venv
source .venv/bin/activate
python -m pip install django
django-admin startproject prescription_project .
python manage.py startapp prescription_lifecycle_app
python manage.py runserver

