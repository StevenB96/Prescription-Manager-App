python -m venv .venv
source .venv/bin/activate
python -m pip install django
django-admin startproject django_test_project .
python manage.py startapp prescription_lifecycle_app

