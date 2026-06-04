from datetime import date
from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base


class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(255), nullable=False)
    description = Column(String(1000), nullable=True)
    genre = Column(String(100), nullable=True)
    publisher = Column(String(255), nullable=True)
    release_date = Column(Date, nullable=True)
    image_url = Column(String(1000), nullable=True)

    created_at = Column(DateTime(timezone=False), server_default=func.now())

    requirements = relationship(
        "Requirement",
        back_populates="game",
        cascade="all, delete-orphan"
    )

    favorites = relationship(
        "Favorite",
        back_populates="game",
        cascade="all, delete-orphan"
    )

    @property
    def title(self):
        return self.name

    @property
    def thumbnail_url(self):
        return self.image_url

    @property
    def slug(self):
        return self.name.lower().replace(' ', '-')

    @property
    def category(self):
        return self.genre