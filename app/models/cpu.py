from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func

from app.database import Base


class CPU(Base):
    __tablename__ = "cpus"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(150), nullable=False, unique=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )