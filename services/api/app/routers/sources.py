"""Sources router — list configured data sources."""

from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.middleware.auth import get_current_user
from app.models.user import User
from app.models.source import Source
from app.schemas.source import SourceResponse

router = APIRouter()


@router.get("/", response_model=List[SourceResponse])
async def list_sources(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all configured data sources. Any authenticated user can view the list."""
    sources = db.query(Source).all()
    return sources
