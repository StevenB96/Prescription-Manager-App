import hashlib
import secrets
from bson.objectid import ObjectId
from datetime import datetime

from prescription_manager_app.db.connection import user_col

from global_utils.auth import (
    hash_password_bcrypt,
    verify_password
)


class User:
    """
    A PyMongo‑backed wrapper for the 'users' collection.
    """
    ROLE_DOCTOR = 0
    ROLE_PHARMACIST = 1
    ROLE_PATIENT = 2
    ROLE_ADMIN = 3

    STATUS_ACTIVE = 0
    STATUS_INACTIVE = 1

    # Display mappings
    ROLE_DISPLAY = {
        ROLE_DOCTOR: 'Doctor',
        ROLE_PHARMACIST: 'Pharmacist',
        ROLE_PATIENT: 'Patient',
        ROLE_ADMIN: 'Admin',
    }

    STATUS_DISPLAY = {
        STATUS_ACTIVE: 'Active',
        STATUS_INACTIVE: 'Inactive',
    }

    ROLE_CHOICES = list(ROLE_DISPLAY.items())

    STATUS_CHOICES = list(STATUS_DISPLAY.items())

    def __init__(self, data):
        self._data = data

    @property
    def id(self):
        return str(self._data["_id"])

    @property
    def username(self):
        return self._data.get("username")

    @property
    def email(self):
        return self._data.get("email")

    @property
    def password_hash(self):
        return self._data.get("password_hash")

    @property
    def session_salt(self):
        return self._data.get("session_salt")

    @property
    def role(self):
        return self._data.get("role")

    @property
    def status(self):
        return self._data.get("status")

    @property
    def created_at(self):
        return self._data.get("created_at")

    @property
    def updated_at(self):
        return self._data.get("updated_at")

    @property
    def last_logged_in(self):
        return self._data.get("last_logged_in")

    def get_role_display(self):
        return self.ROLE_DISPLAY.get(self.role, 'Unknown')

    def get_status_display(self):
        return self.STATUS_DISPLAY.get(self.status, 'Unknown')

    @classmethod
    def create(
        cls,
        username: str,
        email: str,
        password: str,
        role: int,
        status: int = STATUS_ACTIVE
    ):
        """
        Create a new user in MongoDB.

        Raises:
            ValueError: If a user with the same email or username already exists.

        Returns:
            User: A new instance of the User class representing the inserted user.
        """
        # Check if a user with the same email or username already exists
        if user_col.find_one({"$or": [{"email": email}, {"username": username}]}):
            raise ValueError(
                "A user with this email or username already exists.")

        # Hash the password before saving
        password_hash = hash_password_bcrypt(password)

        # Prepare the user document
        now = datetime.utcnow()
        doc = {
            "username": username,
            "email": email,
            "password_hash": password_hash,
            "role": role,
            "status": status,
            "session_salt": secrets.token_hex(16),
            "created_at": now,
            "updated_at": now,
        }

        # Insert the document into MongoDB
        result = user_col.insert_one(doc)
        doc["_id"] = result.inserted_id

        # Return a User instance
        return cls(doc)

    @classmethod
    def get(cls, id):
        try:
            oid = ObjectId(id)
        except Exception:
            return None
        doc = user_col.find_one({"_id": oid})
        return cls(doc) if doc else None

    @classmethod
    def list_all(cls):
        return [cls(d) for d in user_col.find().sort("created_at", 1)]

    @classmethod
    def update(cls, id: str, **kwargs):
        """
        Update an existing user in MongoDB.

        Args:
            id (str): The ID of the user to update.
            **kwargs: Fields to update (only allowed fields will be updated).

        Raises:
            ValueError: If no valid fields are provided for update.
            ValueError: If the user with the given ID does not exist.

        Returns:
            User: An updated instance of the User class.
        """
        allowed = {"username", "email", "password",
                   "role", "status", "last_logged_in"}
        fields = {k: v for k, v in kwargs.items() if k in allowed}
        if not fields:
            raise ValueError("No valid fields provided for update.")

        if "password" in fields:
            fields["password_hash"] = hash_password_bcrypt(
                fields.pop("password"))

        fields["updated_at"] = datetime.utcnow()

        try:
            oid = ObjectId(id)
        except Exception:
            raise ValueError("Invalid user ID format.")

        result = user_col.update_one({"_id": oid}, {"$set": fields})

        if result.matched_count == 0:
            raise ValueError("User not found.")

    @classmethod
    def delete(cls, id: str) -> bool:
        """
        Delete a user from MongoDB.

        Args:
            id (str): The ID of the user to delete.

        Raises:
            ValueError: If the user ID is invalid.
            ValueError: If the user does not exist.

        Returns:
            bool: True if the user was deleted successfully, False otherwise.
        """
        try:
            oid = ObjectId(id)
        except Exception:
            raise ValueError("Invalid user ID format.")

        result = user_col.delete_one({"_id": oid})

        if result.deleted_count == 0:
            raise ValueError("User not found.")

        return True

    @classmethod
    def get_by_username(cls, username: str):
        doc = user_col.find_one({"username": username})
        return cls(doc) if doc else None

    @classmethod
    def get_by_email(cls, email: str):
        doc = user_col.find_one({"email": email})
        return cls(doc) if doc else None

    def check_password(self, password: str) -> bool:
        """
        Verify that the provided password matches the stored password hash.
        """
        if not self.password_hash:
            return False
        return verify_password(password, self.password_hash)

    def get_session_auth_hash(self) -> str:
        # Hash both password_hash + session_salt for uniqueness
        data = f"{self.password_hash}{self.session_salt}"
        return hashlib.sha256(data.encode("utf-8")).hexdigest()
