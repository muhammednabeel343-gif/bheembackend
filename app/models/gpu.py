from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func

from app.database import Base


class GPU(Base):
    __tablename__ = "gpus"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(150), nullable=False, unique=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )