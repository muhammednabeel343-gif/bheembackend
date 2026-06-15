from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)

    hashed_password = Column(String(255), nullable=False)

    created_at = Column(
        DateTime(timezone=False),
        server_default=func.now()
    )

    chat_sessions = relationship(
        "ChatSession",
        back_populates="user",
        cascade="all, delete-orphan",
        order_by="ChatSession.updated_at.desc()",
    )

    # Cart and Purchase relationships
    cart_items = relationship(
        "CartItem",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    orders = relationship(
        "Order",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    purchased_games = relationship(
        "PurchasedGame",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    # Community relationships
    community_posts = relationship(
        "CommunityPost",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    post_reactions = relationship(
        "PostReaction",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    post_comments = relationship(
        "PostComment",
        back_populates="user",
        cascade="all, delete-orphan"
    )