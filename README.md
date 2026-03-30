# 💊 Prescription Manager & OAuth Identity Provider

This project is a sophisticated healthcare management system built with **Django** and **MongoDB**. It serves as a comprehensive administrative tool for medical environments, demonstrating how to integrate NoSQL databases and modern API protocols into a unified healthcare stack.

---

## 🚀 Key Skills Demonstrated
*   **Advanced NoSQL Integration (MongoDB + PyMongo):** Developed custom wrapper classes for BSON serialisation and ObjectId management, bypassing the standard Django ORM.
*   **Custom OAuth 2.0 Implementation:** Ground-up implementation of `authorization_code` and `refresh_token` flows, including custom consent screens and token management.
*   **Modern API Design (GraphQL):** Flexible data-fetching layer using **Graphene-Django** to resolve complex connections between NoSQL documents.
*   **Security & Authentication:** Industry-standard password hashing using `bcrypt` and custom Python decorators (`@oauth_token_required`) to protect resources.

---

## 📌 Functional Overview
The system is split into two primary functional domains:
*   **Prescription Manager App:** An administrative CRUD interface and GraphQL API used to manage the lifecycle of healthcare data, including users, medications, facilities, appointments, and prescriptions.
*   **OAuth Identity Service:** A custom-built implementation of the OAuth 2.0 protocol that allows the system to act as a central identity provider, authorising both internal modules and external applications via `authorization_code` and `refresh_token` flows.

---

## 📂 Folder Structure

```plaintext
├── manage.py                       # Project entry point
├── global_utils/                   # Shared Security
│   └── auth.py                     # Bcrypt hashing and verification logic
├── oauth_service/                  # OAuth 2.0 Identity Provider
│   ├── models/                     # PyMongo wrappers for Clients, Codes, and Tokens
│   ├── templates/                  # UI for Auth (Login, Register, Consent, Manage Apps)
│   ├── views/                      # Protocol logic (Token, Authorise, User Management)
│   ├── auth/                       # MongoDB session and backend helpers
│   ├── forms.py                    # Validation for OAuth flows and registration
│   └── urls.py                     # Routing for /oauth/ endpoints
├── prescription_manager_app/       # Healthcare Management App
│   ├── models/                     # PyMongo wrappers (User, Med, Facility, Appt, Rx)
│   ├── views/                      # CRUD logic for all medical entities
│   ├── templates/                  # Standard Admin UI (List, Detail, Form, Delete)
│   │                                 for all core healthcare entities
│   ├── schema/                     # GraphQL (Graphene) implementation:
│   │   ├── types.py                # Type definitions for all entities
│   │   ├── queries/                # Fetching logic for all entities
│   │   ├── mutations/              # Create/Update/Delete for all entities
│   │   └── schema.py               # Root Query/Mutation assembly
│   ├── management/commands/        # Database seed scripts (Medical Content)
│   └── urls.py                     # Routing for Admin/CRUD interfaces
└── prescription_project/           # Project Configuration
    ├── settings.py                 # App/Auth/OAuth config and MongoDB settings
    └── urls.py                     # Main dispatcher (GraphQL, OAuth, and App URLs)
```

---

## 🚦 Getting Started

### Step 1: Create a virtual environment
```bash
python -m venv .venv
```

### Step 2: Activate the virtual environment
**macOS/Linux:**
```bash
source .venv/bin/activate
```
**Windows:**
```bash
.\.venv\Scripts\activate
```

### Step 3: Install Dependencies
Ensure you have MongoDB running on `localhost:27017`, then install the requirements:
```bash
pip install -r requirements.txt
```
*(Note: If you do not have a requirements.txt, install the core packages: `pip install django pymongo graphene-django bcrypt`)*

### Step 4: Database Seeding
Unlike standard Django projects, this NoSQL project uses custom management commands to populate MongoDB:
```bash
# Seed the OAuth Client (Internal App credentials)
python manage.py seed_oauth

# Seed the Healthcare Data (Users, Meds, Facilities, etc.)
python manage.py seed_content
```

### Step 5: Run the development server
```bash
python manage.py runserver
```

---

## 🛠 Tech Stack
*   **Framework:** Django (Python)
*   **Database:** MongoDB (via PyMongo)
*   **API:** GraphQL (Graphene-Django)
*   **Authentication:** Custom OAuth 2.0 & Bcrypt
*   **Frontend:** Django Templates (Server-Side Rendering)

---

## 📝 Usage Note
Access the **OAuth Service** at `http://localhost:8000/oauth/` to register or login. Once authenticated, you can access the **Prescription Admin** dashboard at `http://localhost:8000/admin` and the **GraphQL Playground** at `http://localhost:8000/graphql/`.