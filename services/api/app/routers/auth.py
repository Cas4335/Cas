"""
Authentication router: login and user profile.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import verify_password, create_access_token
from app.core.config import settings
from app.middleware.auth import get_current_user
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse, UserMeResponse

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate with email and password, return a JWT access token.
    Does NOT expose whether the email exists (prevents enumeration).
    """
    user = db.query(User).filter(User.email == request.email.lower().strip()).first()

    # Always run verify_password even if user is None to prevent timing attacks
    password_ok = verify_password(
        request.password,
        user.hashed_password if user else "$2b$12$placeholder_hash_to_prevent_timing",
    )

    if not user or not password_ok or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(
        subject=str(user.id),
        extra_claims={"email": user.email, "roles": user.get_role_names()},
    )

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in_hours=settings.JWT_EXPIRE_HOURS,
    )


@router.get("/me", response_model=UserMeResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Return the authenticated user's profile and roles."""
    return UserMeResponse(
        id=current_user.id,
        email=current_user.email,
        display_name=current_user.display_name,
        roles=current_user.get_role_names(),
        is_active=current_user.is_active,
        created_at=current_user.created_at,
    )
