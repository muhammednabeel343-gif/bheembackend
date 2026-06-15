from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base


class CommunityPost(Base):
    __tablename__ = "community_posts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    game_id = Column(Integer, ForeignKey("games.id"), nullable=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=False), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="community_posts")
    game = relationship("Game", back_populates="community_posts")
    reactions = relationship(
        "PostReaction",
        back_populates="post",
        cascade="all, delete-orphan"
    )
    comments = relationship(
        "PostComment",
        back_populates="post",
        cascade="all, delete-orphan"
    )


class PostReaction(Base):
    __tablename__ = "post_reactions"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("community_posts.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    emoji = Column(String(10), nullable=False)  # ❤️, 🔥, 🎮, 😎, ⚔️

    # Relationships
    post = relationship("CommunityPost", back_populates="reactions")
    user = relationship("User", back_populates="post_reactions")


class PostComment(Base):
    __tablename__ = "post_comments"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("community_posts.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    comment = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=False), server_default=func.now())

    # Relationships
    post = relationship("CommunityPost", back_populates="comments")
    user = relationship("User", back_populates="post_comments")
