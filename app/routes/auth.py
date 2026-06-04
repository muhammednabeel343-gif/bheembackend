from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.schemas.auth import UserCreate, LoginRequest, Token, UserResponse
from app.authentication.jwt import (
    hash_password,
    create_access_token,
    authenticate_user,
    get_current_user,
)
from app.database import get_db
from app.models.user import User
from app.models.admin import Admin
from app.config import settings
from app.schemas.admin import AdminResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=Token)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter((User.email == user.email) | (User.username == user.username)).first()
    if existing:
        detail = "Email or username already registered"
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail)

    hashed_password = hash_password(user.password)
    db_user = User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password,
    )
    db.add(db_user)
    try:
        db.commit()
        db.refresh(db_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email or username already registered")

    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(data={"sub": db_user.email}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login", response_model=Token)
async def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, credentials.email, credentials.password)
    if not user:
        admin = db.query(Admin).filter(Admin.email == credentials.email).first()
        if admin:
            from app.authentication.jwt import verify_password
            if verify_password(credentials.password, admin.hashed_password):
                access_token = create_access_token(
                    data={"sub": admin.email, "role": "admin"},
                    expires_delta=timedelta(minutes=settings.access_token_expire_minutes)
                )
                return {
                    "access_token": access_token,
                    "token_type": "bearer",
                    "role": "admin",
                    "admin": {
                        "id": admin.id,
                        "username": admin.username,
                        "email": admin.email
                    }
                }
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user.last_login_at = datetime.utcnow()
    db.add(user)
    db.commit()
    db.refresh(user)

    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer", "role": "user"}


@router.get("/me", response_model=UserResponse)
async def get_profile(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    return {"message": f"User {current_user.username} logged out successfully"}
