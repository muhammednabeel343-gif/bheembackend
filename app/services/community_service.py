from sqlalchemy.orm import Session
from app.models.community import CommunityPost, PostReaction, PostComment
from app.models.user import User
from app.models.game import Game
from typing import List, Optional, Dict
from datetime import datetime


class CommunityService:
    """Service for managing community posts, reactions, and comments."""

    @staticmethod
    def create_post(
        db: Session,
        user_id: int,
        content: str,
        game_id: Optional[int] = None
    ) -> CommunityPost:
        """Create a new community post."""
        post = CommunityPost(
            user_id=user_id,
            content=content,
            game_id=game_id
        )
        db.add(post)
        db.commit()
        db.refresh(post)
        return post

    @staticmethod
    def get_community_feed(db: Session, limit: int = 50, offset: int = 0) -> List[CommunityPost]:
        """Get community feed posts ordered by newest first."""
        return db.query(CommunityPost).order_by(
            CommunityPost.created_at.desc()
        ).limit(limit).offset(offset).all()

    @staticmethod
    def get_post(db: Session, post_id: int) -> Optional[CommunityPost]:
        """Get a specific post."""
        return db.query(CommunityPost).filter(CommunityPost.id == post_id).first()

    @staticmethod
    def delete_post(db: Session, post_id: int, user_id: int) -> bool:
        """Delete a post (only by author)."""
        post = db.query(CommunityPost).filter(
            CommunityPost.id == post_id,
            CommunityPost.user_id == user_id
        ).first()
        
        if post:
            db.delete(post)
            db.commit()
            return True
        return False

    @staticmethod
    def add_reaction(
        db: Session,
        post_id: int,
        user_id: int,
        emoji: str
    ) -> PostReaction:
        """Add or update a reaction to a post."""
        # Check if reaction already exists
        existing = db.query(PostReaction).filter(
            PostReaction.post_id == post_id,
            PostReaction.user_id == user_id,
            PostReaction.emoji == emoji
        ).first()
        
        if existing:
            return existing
        
        reaction = PostReaction(
            post_id=post_id,
            user_id=user_id,
            emoji=emoji
        )
        db.add(reaction)
        db.commit()
        db.refresh(reaction)
        return reaction

    @staticmethod
    def remove_reaction(
        db: Session,
        post_id: int,
        user_id: int,
        emoji: str
    ) -> bool:
        """Remove a reaction from a post."""
        reaction = db.query(PostReaction).filter(
            PostReaction.post_id == post_id,
            PostReaction.user_id == user_id,
            PostReaction.emoji == emoji
        ).first()
        
        if reaction:
            db.delete(reaction)
            db.commit()
            return True
        return False

    @staticmethod
    def get_reactions(db: Session, post_id: int) -> Dict[str, int]:
        """Get reaction summary for a post."""
        reactions = db.query(PostReaction).filter(
            PostReaction.post_id == post_id
        ).all()
        
        summary = {}
        for reaction in reactions:
            if reaction.emoji not in summary:
                summary[reaction.emoji] = 0
            summary[reaction.emoji] += 1
        
        return summary

    @staticmethod
    def user_has_reacted(db: Session, post_id: int, user_id: int, emoji: str) -> bool:
        """Check if user has reacted with specific emoji."""
        reaction = db.query(PostReaction).filter(
            PostReaction.post_id == post_id,
            PostReaction.user_id == user_id,
            PostReaction.emoji == emoji
        ).first()
        return reaction is not None

    @staticmethod
    def add_comment(
        db: Session,
        post_id: int,
        user_id: int,
        comment: str
    ) -> PostComment:
        """Add a comment to a post."""
        post_comment = PostComment(
            post_id=post_id,
            user_id=user_id,
            comment=comment
        )
        db.add(post_comment)
        db.commit()
        db.refresh(post_comment)
        return post_comment

    @staticmethod
    def get_comments(db: Session, post_id: int) -> List[PostComment]:
        """Get all comments for a post."""
        return db.query(PostComment).filter(
            PostComment.post_id == post_id
        ).order_by(PostComment.created_at.asc()).all()

    @staticmethod
    def delete_comment(db: Session, comment_id: int, user_id: int) -> bool:
        """Delete a comment (only by author)."""
        comment = db.query(PostComment).filter(
            PostComment.id == comment_id,
            PostComment.user_id == user_id
        ).first()
        
        if comment:
            db.delete(comment)
            db.commit()
            return True
        return False

    @staticmethod
    def get_user_posts(db: Session, user_id: int) -> List[CommunityPost]:
        """Get all posts by a specific user."""
        return db.query(CommunityPost).filter(
            CommunityPost.user_id == user_id
        ).order_by(CommunityPost.created_at.desc()).all()
