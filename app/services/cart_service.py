from sqlalchemy.orm import Session
from app.models.cart import CartItem
from app.models.game import Game
from app.models.user import User
from typing import List


class CartService:
    """Service for managing shopping cart operations."""

    @staticmethod
    def add_to_cart(db: Session, user_id: int, game_id: int) -> CartItem:
        """Add a game to user's cart."""
        # Check if already in cart
        existing = db.query(CartItem).filter(
            CartItem.user_id == user_id,
            CartItem.game_id == game_id
        ).first()
        
        if existing:
            return existing
        
        cart_item = CartItem(user_id=user_id, game_id=game_id)
        db.add(cart_item)
        db.commit()
        db.refresh(cart_item)
        return cart_item

    @staticmethod
    def remove_from_cart(db: Session, user_id: int, game_id: int) -> bool:
        """Remove a game from user's cart."""
        cart_item = db.query(CartItem).filter(
            CartItem.user_id == user_id,
            CartItem.game_id == game_id
        ).first()
        
        if cart_item:
            db.delete(cart_item)
            db.commit()
            return True
        return False

    @staticmethod
    def get_user_cart(db: Session, user_id: int) -> List[CartItem]:
        """Get all items in user's cart."""
        return db.query(CartItem).filter(CartItem.user_id == user_id).all()

    @staticmethod
    def get_cart_count(db: Session, user_id: int) -> int:
        """Get number of items in user's cart."""
        return db.query(CartItem).filter(CartItem.user_id == user_id).count()

    @staticmethod
    def clear_cart(db: Session, user_id: int) -> None:
        """Clear all items from user's cart."""
        db.query(CartItem).filter(CartItem.user_id == user_id).delete()
        db.commit()

    @staticmethod
    def get_cart_total(db: Session, user_id: int) -> float:
        """Calculate total price of items in cart."""
        cart_items = db.query(CartItem).filter(CartItem.user_id == user_id).all()
        total = 0.0
        for item in cart_items:
            game = db.query(Game).filter(Game.id == item.game_id).first()
            if game and game.price:
                total += game.price
        return total
