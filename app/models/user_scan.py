from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    ForeignKey,
    DateTime,
    func,
)
from sqlalchemy.orm import relationship

from app.database import Base


class UserScan(Base):
    __tablename__ = "user_scans"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    game_id = Column(Integer, ForeignKey("games.id"), nullable=True)

    cpu = Column(String(255), nullable=False)
    gpu = Column(String(255), nullable=False)

    ram_gb = Column(Integer, nullable=False)
    storage_gb = Column(Integer, nullable=False)

    operating_system = Column(String(100), nullable=True)

    compatibility_score = Column(Float, nullable=False)

    fps_estimate = Column(Integer, nullable=True)

    status = Column(String(50), nullable=False)

    scan_time = Column(DateTime(timezone=False),
                       server_default=func.now())

    user = relationship("User")
    game = relationship("Game")