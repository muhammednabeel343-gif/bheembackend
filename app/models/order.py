from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, func, Enum
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    total_amount = Column(Float, nullable=False)
    payment_method = Column(String(50), nullable=False)  # UPI, Credit Card, Debit Card, Net Banking
    status = Column(String(20), default=OrderStatus.PENDING.value, nullable=False)
    created_at = Column(DateTime(timezone=False), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="orders")
    items = relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan"
    )


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    game_id = Column(Integer, ForeignKey("games.id"), nullable=False)
    price = Column(Float, nullable=False)

    # Relationships
    order = relationship("Order", back_populates="items")
    game = relationship("Game", back_populates="order_items")
