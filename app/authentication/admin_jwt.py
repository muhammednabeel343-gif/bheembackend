from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.admin import Admin

oauth2_scheme_admin = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)


async def get_current_admin(
    token: str = Depends(oauth2_scheme_admin),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate admin credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )

        email = payload.get("sub")
        role = payload.get("role")

        if email is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    admin = (
        db.query(Admin)
        .filter(Admin.email == email)
        .first()
    )

    if admin is None:
        raise credentials_exception

    return admin