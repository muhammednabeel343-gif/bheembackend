from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.admin import Admin
from app.schemas.admin import AdminLogin, AdminResponse
from app.authentication.jwt import (
    verify_password,
    create_access_token
)
from app.config import settings
from app.authentication.admin_jwt import get_current_admin

router = APIRouter(
    prefix="/admin",
    tags=["Admin Authentication"]
)


@router.post("/login")
def admin_login(
    credentials: AdminLogin,
    db: Session = Depends(get_db)
):
    admin = (
        db.query(Admin)
        .filter(Admin.email == credentials.email)
        .first()
    )

    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    if not verify_password(
        credentials.password,
        admin.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    access_token = create_access_token(
        data={"sub": admin.email},
        expires_delta=timedelta(
            minutes=settings.access_token_expire_minutes
        )
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "admin": {
            "id": admin.id,
            "username": admin.username,
            "email": admin.email
        }
    }


@router.get("/me", response_model=AdminResponse)
def get_admin_profile(current_admin: Admin = Depends(get_current_admin)):
    return current_admin