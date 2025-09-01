
---

## Folder Structure

```plaintext
manage.py
prescription_manager_app/
├── admin.py
├── apps.py
├── backends.py
├── db.py
├── models.py
├── tests.py
├── urls.py
├── views.py
├── __init__.py
├── migrations/
│   └── __init__.py
├── models/
│   ├── appointment.py
│   ├── facility.py
│   ├── medication.py
│   ├── prescription.py
│   ├── user.py
│   └── __init__.py
├── oauth/
│   ├── setup.py
│   └── storage.py
├── scripts/
│   └── seed.py
└── templates/
    └── prescription_manager_app/
        ├── base.html
        ├── appointment/
        │   ├── confirm_delete.html
        │   ├── detail.html
        │   ├── form.html
        │   └── list.html
        ├── auth/
        │   ├── authorise.html
        │   ├── login.html
        │   └── register.html
        ├── facility/
        │   ├── confirm_delete.html
        │   ├── detail.html
        │   ├── form.html
        │   └── list.html
        ├── medication/
        │   ├── confirm_delete.html
        │   ├── detail.html
        │   ├── form.html
        │   └── list.html
        ├── prescription/
        │   ├── confirm_delete.html
        │   ├── detail.html
        │   ├── form.html
        │   └── list.html
        └── user/
            ├── confirm_delete.html
            ├── detail.html
            ├── form.html
            └── list.html
prescription_project/
├── asgi.py
├── settings.py
├── urls.py
├── wsgi.py
└── __init__.py
```

---

## Getting Started
### Step 1: Create a virtual environment
```bash
python -m venv .venv
```
### Step 2: Activate the virtual environment
On macOS/Linux:
```bash
source .venv/bin/activate
```
On Windows:
```bash
.\venv\Scripts\activate
```
### Step 3: Install Django
```bash
pip install django
```
### Step 4: Create a new Django project named 'prescription_project'
```bash
django-admin startproject prescription_project .
```
### Step 5: Create a new Django app called 'prescription_manager_app'
```bash
python manage.py startapp prescription_manager_app
```
### Step 6: Run the development server
```bash
python manage.py runserver
```

---
