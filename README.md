
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
