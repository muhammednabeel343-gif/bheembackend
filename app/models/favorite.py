from sqlalchemy import Column, Integer, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.database import Base


class Favorite(Base):
    __tablename__ = "favourites"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"))
    game_id = Column(Integer, ForeignKey("games.id"))

    created_at = Column(
        DateTime(timezone=False),
        server_default=func.now()
    )

    user = relationship("User")
    game = relationship("Game", back_populates="favorites")