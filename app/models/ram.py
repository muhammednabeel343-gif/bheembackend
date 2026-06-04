from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.sql import func

from app.database import Base


class RAM(Base):
    __tablename__ = "rams"

    id = Column(Integer, primary_key=True, index=True)

    size = Column(Integer, nullable=False, unique=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )