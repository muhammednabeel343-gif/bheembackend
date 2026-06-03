from sqlalchemy import Column, Integer, String, DateTime, func
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)

    password_hash = Column(String(255), nullable=True)
    hashed_password = Column(String(255), nullable=True)

    created_at = Column(
        DateTime(timezone=False),
        server_default=func.now()
    )