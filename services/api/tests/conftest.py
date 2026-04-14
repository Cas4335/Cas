"""
Test fixtures and configuration.
Uses SQLite for unit tests (no Postgres needed).
"""
import os

# Set env vars BEFORE importing any app modules
os.environ.setdefault("POSTGRES_PASSWORD", "test")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-for-testing-only-never-use-in-prod")
os.environ.setdefault("POSTGRES_HOST", "localhost")
os.environ.setdefault("POSTGRES_DB", "phx_test")
os.environ.setdefault("POSTGRES_USER", "phx")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Override the DB engine before importing app modules that use it
from app.core import database as db_module

TEST_DB_URL = "sqlite:///./test_phx.db"

test_engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestSessionFactory = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# Patch the lazy engine factory to return the test engine
db_module._engine = test_engine
db_module._SessionLocal = TestSessionFactory

from app.core.database import Base, get_db
from app.main import app
from app.models.user import User, Role
from app.core.security import hash_password


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)
    if os.path.exists("./test_phx.db"):
        os.remove("./test_phx.db")


@pytest.fixture
def db():
    session = TestSessionFactory()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def admin_user(db):
    role = db.query(Role).filter_by(name="admin").first()
    if not role:
        role = Role(name="admin", description="Admin role")
        db.add(role)
        db.flush()

    user = db.query(User).filter_by(email="testadmin@example.com").first()
    if not user:
        user = User(
            email="testadmin@example.com",
            display_name="Test Admin",
            hashed_password=hash_password("testpass123"),
        )
        db.add(user)
        db.flush()
        user.roles.append(role)
        db.commit()
    return user


@pytest.fixture
def ops_user(db):
    role = db.query(Role).filter_by(name="operations").first()
    if not role:
        role = Role(name="operations", description="Ops role")
        db.add(role)
        db.flush()

    user = db.query(User).filter_by(email="testops@example.com").first()
    if not user:
        user = User(
            email="testops@example.com",
            display_name="Test Ops",
            hashed_password=hash_password("testpass123"),
        )
        db.add(user)
        db.flush()
        user.roles.append(role)
        db.commit()
    return user
