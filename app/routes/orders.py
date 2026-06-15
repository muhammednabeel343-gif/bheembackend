from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.authentication.jwt import get_current_user
from app.models.user import User
from app.models.game import Game
from app.services.cart_service import CartService
from app.services.order_service import OrderService
from app.services.purchase_service import PurchaseService
from app.schemas.order import (
    CreateOrderRequest,
    OrderResponse,
    PaymentSimulationRequest,
    ProcessPaymentRequest,
    OrderItemResponse
)

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("/create", response_model=OrderResponse)
async def create_order(
    request: CreateOrderRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new order from cart items."""
    
    # Verify all games exist
    games = db.query(Game).filter(Game.id.in_(request.game_ids)).all()
    if len(games) != len(request.game_ids):
        raise HTTPException(status_code=404, detail="One or more games not found")
    
    # Compute server-side total and create order (do not trust client total)
    total_amount = sum([g.price or 0.0 for g in games])

    # Create order using server-calculated total
    order = OrderService.create_order(
        db,
        current_user.id,
        request.game_ids,
        total_amount,
        request.payment_method
    )
    
    # Build response with game details
    items_response = []
    for item in order.items:
        game = db.query(Game).filter(Game.id == item.game_id).first()
        items_response.append(OrderItemResponse(
            id=item.id,
            game_id=item.game_id,
            game_name=game.name if game else "Unknown",
            price=item.price,
            image_url=game.image_url if game else None
        ))
    
    return OrderResponse(
        id=order.id,
        user_id=order.user_id,
        total_amount=order.total_amount,
        payment_method=order.payment_method,
        status=order.status,
        created_at=order.created_at,
        items=items_response
    )


@router.get("/", response_model=List[OrderResponse])
async def get_orders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all orders for current user."""
    orders = OrderService.get_user_orders(db, current_user.id)
    
    responses = []
    for order in orders:
        items_response = []
        for item in order.items:
            game = db.query(Game).filter(Game.id == item.game_id).first()
            items_response.append(OrderItemResponse(
                id=item.id,
                game_id=item.game_id,
                game_name=game.name if game else "Unknown",
                price=item.price,
                image_url=game.image_url if game else None
            ))
        
        responses.append(OrderResponse(
            id=order.id,
            user_id=order.user_id,
            total_amount=order.total_amount,
            payment_method=order.payment_method,
            status=order.status,
            created_at=order.created_at,
            items=items_response
        ))
    
    return responses


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific order."""
    order = OrderService.get_order(db, order_id, current_user.id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    items_response = []
    for item in order.items:
        game = db.query(Game).filter(Game.id == item.game_id).first()
        items_response.append(OrderItemResponse(
            id=item.id,
            game_id=item.game_id,
            game_name=game.name if game else "Unknown",
            price=item.price,
            image_url=game.image_url if game else None
        ))
    
    return OrderResponse(
        id=order.id,
        user_id=order.user_id,
        total_amount=order.total_amount,
        payment_method=order.payment_method,
        status=order.status,
        created_at=order.created_at,
        items=items_response
    )


@router.post("/{order_id}/simulate-payment")
async def simulate_payment(
    order_id: int,
    request: PaymentSimulationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Simulate payment processing (mock)."""
    order = OrderService.get_order(db, order_id, current_user.id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if request.success:
        # Mark order as completed and create purchased games
        order = OrderService.complete_order(db, order_id)
        # Clear cart after successful purchase
        CartService.clear_cart(db, current_user.id)
        
        return {
            "success": True,
            "message": "Payment successful",
            "order_id": order.id,
            "status": order.status
        }
    else:
        # Mark order as failed
        order = OrderService.update_order_status(db, order_id, "failed")
        return {
            "success": False,
            "message": "Payment failed",
            "order_id": order.id,
            "status": order.status
        }


@router.post("/{order_id}/complete")
async def complete_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Complete an order and create purchased games."""
    order = OrderService.get_order(db, order_id, current_user.id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order = OrderService.complete_order(db, order_id)
    CartService.clear_cart(db, current_user.id)
    
    return {
        "success": True,
        "message": "Order completed",
        "order_id": order.id
    }
