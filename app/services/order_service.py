from sqlalchemy.orm import Session
from app.models.order import Order, OrderItem, OrderStatus
from app.models.purchase import PurchasedGame
from app.services.purchase_service import PurchaseService
from app.models.game import Game
from typing import List, Optional
from datetime import datetime


class OrderService:
    """Service for managing orders."""

    @staticmethod
    def create_order(
        db: Session,
        user_id: int,
        game_ids: List[int],
        total_amount: float,
        payment_method: str
    ) -> Order:
        """Create a new order with order items."""
        order = Order(
            user_id=user_id,
            total_amount=total_amount,
            payment_method=payment_method,
            status=OrderStatus.PENDING.value
        )
        db.add(order)
        db.flush()  # Flush to get the order ID

        # Add order items
        for game_id in game_ids:
            game = db.query(Game).filter(Game.id == game_id).first()
            if game:
                order_item = OrderItem(
                    order_id=order.id,
                    game_id=game_id,
                    price=game.price or 0.0
                )
                db.add(order_item)

        db.commit()
        db.refresh(order)
        return order

    @staticmethod
    def get_user_orders(db: Session, user_id: int) -> List[Order]:
        """Get all orders for a user."""
        return db.query(Order).filter(Order.user_id == user_id).order_by(Order.created_at.desc()).all()

    @staticmethod
    def get_order(db: Session, order_id: int, user_id: int) -> Optional[Order]:
        """Get a specific order for a user."""
        return db.query(Order).filter(
            Order.id == order_id,
            Order.user_id == user_id
        ).first()

    @staticmethod
    def update_order_status(db: Session, order_id: int, status: str) -> Order:
        """Update order status."""
        order = db.query(Order).filter(Order.id == order_id).first()
        if order:
            order.status = status
            db.commit()
            db.refresh(order)
        return order

    @staticmethod
    def complete_order(db: Session, order_id: int) -> Order:
        """Mark order as completed and create purchased game entries."""
        order = db.query(Order).filter(Order.id == order_id).first()
        if order:
            order.status = OrderStatus.COMPLETED.value
            # Create PurchasedGame entries for each order item (avoid duplicates)
            for order_item in order.items:
                PurchaseService.add_purchased_game(db, order.user_id, order_item.game_id)

            db.commit()
            db.refresh(order)
        return order

    @staticmethod
    def get_order_items(db: Session, order_id: int) -> List[OrderItem]:
        """Get all items in an order."""
        return db.query(OrderItem).filter(OrderItem.order_id == order_id).all()
