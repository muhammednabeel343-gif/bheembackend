from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.database import Base


class Requirement(Base):
    __tablename__ = "requirements"

    id = Column(Integer, primary_key=True, index=True)

    game_id = Column(Integer, ForeignKey("games.id"))

    cpu = Column(String(100))
    gpu = Column(String(100))

    ram = Column(Integer)
    storage = Column(Integer)

    directx = Column(String(20))
    operating_system = Column("os", String(50))

    created_at = Column(DateTime(timezone=False), server_default=func.now())

    game = relationship("Game", back_populates="requirements")

    @property
    def ram_gb(self):
        return self.ram

    @property
    def storage_gb(self):
        return self.storage
