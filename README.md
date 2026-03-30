# Prescription Manager & OAuth Identity Provider

A sophisticated Django-based healthcare management system that demonstrates an advanced integration of **NoSQL databases**, **GraphQL APIs**, and a custom-built **OAuth 2.0 Identity Provider**.

## 📌 Project Overview
This project serves as a comprehensive administrative tool for medical environments. It is split into two primary domains:
1.  **Prescription Manager App:** An administrative CRUD interface and GraphQL API for managing users, medications, facilities, appointments, and prescriptions.
2.  **OAuth Service:** A custom implementation of the OAuth 2.0 protocol, allowing the system to act as an identity provider to authorize internal and external applications.

## 🚀 Key Skills Demonstrated
*   **Advanced NoSQL Integration (MongoDB + PyMongo):** Developed custom wrapper classes for BSON serialization and ObjectId management, bypassing the standard Django ORM.
*   **Custom OAuth 2.0 Implementation:** Ground-up implementation of `authorization_code` and `refresh_token` flows, including custom consent screens and token management.
*   **Modern API Design (GraphQL):** Flexible data-fetching layer using **Graphene-Django** to resolve complex connections between NoSQL documents.
*   **Security & Authentication:** Industry-standard password hashing using `bcrypt` and custom Python decorators (`@oauth_token_required`) to protect resources.

---

## 📂 Folder Structure

```plaintext
manage.py
global_utils/               # Shared security and auth utilities
├── auth.py                 # Bcrypt hashing and verification
oauth_service/              # Custom OAuth 2.0 Identity Provider App
├── auth/                   # Session helpers and backends
├── db/                     # MongoDB connection handles
├── management/commands/    # Seed scripts for OAuth clients
├── models/                 # PyMongo wrappers for Clients, Codes, and Tokens
├── templates/              # Login, Register, and Authorisation UI
└── views/                  # Core OAuth protocol logic
prescription_manager_app/   # Healthcare Management App
├── db/                     # MongoDB connection handles
├── management/commands/    # Seed scripts for medical content
├── models/                 # PyMongo wrappers for medical entities
├── schema/                 # GraphQL Queries, Mutations, and Types
├── templates/              # CRUD Admin UI for healthcare entities
└── views/                  # Traditional Django views for CRUD
prescription_project/       # Project configuration
├── settings.py             # App, Auth, and OAuth settings
└── urls.py                 # Main routing (GraphQL, OAuth, and App)
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