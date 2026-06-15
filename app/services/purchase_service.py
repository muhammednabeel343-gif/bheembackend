from sqlalchemy.orm import Session
from app.models.purchase import PurchasedGame
from app.models.game import Game
from app.models.user import User
from typing import List, Optional


class PurchaseService:
    """Service for managing purchased games."""

    @staticmethod
    def get_purchased_games(db: Session, user_id: int) -> List[PurchasedGame]:
        """Get all games purchased by a user."""
        return db.query(PurchasedGame).filter(
            PurchasedGame.user_id == user_id
        ).order_by(PurchasedGame.purchase_date.desc()).all()

    @staticmethod
    def is_game_purchased(db: Session, user_id: int, game_id: int) -> bool:
        """Check if user has purchased a specific game."""
        purchased = db.query(PurchasedGame).filter(
            PurchasedGame.user_id == user_id,
            PurchasedGame.game_id == game_id
        ).first()
        return purchased is not None

    @staticmethod
    def add_purchased_game(
        db: Session,
        user_id: int,
        game_id: int
    ) -> PurchasedGame:
        """Add a game to user's purchased games."""
        # Check if already purchased
        if PurchaseService.is_game_purchased(db, user_id, game_id):
            return db.query(PurchasedGame).filter(
                PurchasedGame.user_id == user_id,
                PurchasedGame.game_id == game_id
            ).first()
        
        purchased_game = PurchasedGame(
            user_id=user_id,
            game_id=game_id
        )
        db.add(purchased_game)
        db.commit()
        db.refresh(purchased_game)
        return purchased_game

    @staticmethod
    def get_purchase_count(db: Session, user_id: int) -> int:
        """Get total number of games purchased by user."""
        return db.query(PurchasedGame).filter(
            PurchasedGame.user_id == user_id
        ).count()

    @staticmethod
    def get_user_library(db: Session, user_id: int) -> List[dict]:
        """Get user's game library with details."""
        purchased = PurchaseService.get_purchased_games(db, user_id)
        library = []
        
        for purchase in purchased:
            game = db.query(Game).filter(Game.id == purchase.game_id).first()
            if game:
                library.append({
                    "id": game.id,
                    "name": game.name,
                    "image_url": game.image_url,
                    "purchase_date": purchase.purchase_date,
                    "genre": game.genre,
                    "description": game.description
                })
        
        return library
