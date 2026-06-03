from sqlalchemy import Column, Integer, String, Date, DateTime, func
from sqlalchemy.orm import relationship
from app.database import Base


class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(255), nullable=False)
    genre = Column(String(100))
    publisher = Column(String(255))
    release_date = Column(Date)
    image_url = Column(String(1000))

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
