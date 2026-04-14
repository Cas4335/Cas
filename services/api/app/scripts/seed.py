"""
Seed script: creates demo users and roles for local development.

Run with: python -m app.scripts.seed

IMPORTANT: Change all passwords before connecting real data.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models.user import User, Role, user_roles_table


DEMO_ROLES = [
    {"name": "admin", "description": "Full access to all content and admin functions"},
    {"name": "management", "description": "Access to management and shared content"},
    {"name": "operations", "description": "Access to operations and shared content"},
    {"name": "hr", "description": "Access to HR and shared content"},
    {"name": "shared_user", "description": "Access to shared content only"},
]

DEMO_USERS = [
    {
        "email": "admin@example.com",
        "display_name": "Admin User",
        "password": "changeme123",
        "roles": ["admin"],
    },
    {
        "email": "ops@example.com",
        "display_name": "Operations User",
        "password": "changeme123",
        "roles": ["operations"],
    },
    {
        "email": "hr@example.com",
        "display_name": "HR User",
        "password": "changeme123",
        "roles": ["hr"],
    },
    {
        "email": "mgmt@example.com",
        "display_name": "Management User",
        "password": "changeme123",
        "roles": ["management"],
    },
    {
        "email": "shared@example.com",
        "display_name": "Shared User",
        "password": "changeme123",
        "roles": ["shared_user"],
    },
]


def seed():
    db = SessionLocal()
    try:
        print("Seeding roles...")
        role_map = {}
        for role_data in DEMO_ROLES:
            existing = db.query(Role).filter_by(name=role_data["name"]).first()
            if not existing:
                role = Role(**role_data)
                db.add(role)
                db.flush()
                role_map[role_data["name"]] = role
                print(f"  Created role: {role_data['name']}")
            else:
                role_map[role_data["name"]] = existing
                print(f"  Role exists: {role_data['name']}")

        print("Seeding users...")
        for user_data in DEMO_USERS:
            existing = db.query(User).filter_by(email=user_data["email"]).first()
            if not existing:
                user = User(
                    email=user_data["email"],
                    display_name=user_data["display_name"],
                    hashed_password=hash_password(user_data["password"]),
                )
                db.add(user)
                db.flush()
                for role_name in user_data["roles"]:
                    role = role_map.get(role_name)
                    if role:
                        user.roles.append(role)
                print(f"  Created user: {user_data['email']} ({', '.join(user_data['roles'])})")
            else:
                print(f"  User exists: {user_data['email']}")

        db.commit()
        print("Seed complete.")
    except Exception as e:
        db.rollback()
        print(f"Seed failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
