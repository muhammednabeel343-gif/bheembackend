from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime


class OrderItemResponse(BaseModel):
    id: int
    game_id: int
    game_name: str
    price: float
    image_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class OrderResponse(BaseModel):
    id: int
    user_id: int
    total_amount: float
    payment_method: str
    status: str
    created_at: datetime
    items: List[OrderItemResponse] = []

    model_config = ConfigDict(from_attributes=True)


class CreateOrderRequest(BaseModel):
    game_ids: List[int]
    total_amount: float
    payment_method: str  # UPI, Credit Card, Debit Card, Net Banking


class ProcessPaymentRequest(BaseModel):
    order_id: int
    payment_method: str
    amount: float


class PaymentSimulationRequest(BaseModel):
    order_id: Optional[int] = None
    success: bool = True  # For mock payment simulation (body may omit order_id)
