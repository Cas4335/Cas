"""Tests for authentication flow."""

import pytest
from app.core.security import hash_password, verify_password, create_access_token, decode_token
from app.models.user import User


class TestPasswordHashing:
    def test_hash_and_verify(self):
        password = "secure_password_123"
        hashed = hash_password(password)
        assert hashed != password
        assert verify_password(password, hashed)

    def test_wrong_password_fails(self):
        hashed = hash_password("correct_password")
        assert not verify_password("wrong_password", hashed)

    def test_hash_is_not_plaintext(self):
        password = "my_secret"
        hashed = hash_password(password)
        assert password not in hashed


class TestJWT:
    def test_create_and_decode_token(self):
        token = create_access_token(subject="42", extra_claims={"email": "test@example.com"})
        payload = decode_token(token)
        assert payload["sub"] == "42"
        assert payload["email"] == "test@example.com"
        assert "exp" in payload

    def test_token_has_expiry(self):
        from jose import jwt
        token = create_access_token(subject="1")
        payload = decode_token(token)
        assert "exp" in payload
        assert payload["exp"] is not None


class TestLoginEndpoint:
    def test_login_success(self, client, admin_user):
        res = client.post("/auth/login", json={
            "email": "testadmin@example.com",
            "password": "testpass123",
        })
        assert res.status_code == 200
        data = res.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client, admin_user):
        res = client.post("/auth/login", json={
            "email": "testadmin@example.com",
            "password": "wrongpassword",
        })
        assert res.status_code == 401

    def test_login_unknown_email(self, client):
        res = client.post("/auth/login", json={
            "email": "nobody@example.com",
            "password": "anypassword",
        })
        assert res.status_code == 401

    def test_me_endpoint(self, client, admin_user):
        # First login
        res = client.post("/auth/login", json={
            "email": "testadmin@example.com",
            "password": "testpass123",
        })
        token = res.json()["access_token"]

        # Then get profile
        res = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 200
        data = res.json()
        assert data["email"] == "testadmin@example.com"
        assert "admin" in data["roles"]

    def test_me_requires_auth(self, client):
        res = client.get("/auth/me")
        assert res.status_code == 403  # No Authorization header

    def test_me_invalid_token(self, client):
        res = client.get("/auth/me", headers={"Authorization": "Bearer invalid_token"})
        assert res.status_code == 401
