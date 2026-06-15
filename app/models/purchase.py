from sqlalchemy import Column, Integer, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.database import Base


class PurchasedGame(Base):
    __tablename__ = "purchased_games"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    game_id = Column(Integer, ForeignKey("games.id"), nullable=False)
    purchase_date = Column(DateTime(timezone=False), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="purchased_games")
    game = relationship("Game", back_populates="purchased_games")
