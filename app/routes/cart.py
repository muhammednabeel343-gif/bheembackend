from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.authentication.jwt import get_current_user
from app.models.user import User
from app.models.game import Game
from app.services.cart_service import CartService
from app.services.purchase_service import PurchaseService
from app.schemas.cart import (
    AddToCartRequest,
    RemoveFromCartRequest,
    CartResponse,
    CartItemWithGame
)

router = APIRouter(prefix="/cart", tags=["cart"])


@router.post("/add")
async def add_to_cart(
    request: AddToCartRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a game to user's cart."""
    # Verify game exists
    game = db.query(Game).filter(Game.id == request.game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    # Check if already purchased
    if PurchaseService.is_game_purchased(db, current_user.id, request.game_id):
        raise HTTPException(status_code=400, detail="Game already purchased")
    
    cart_item = CartService.add_to_cart(db, current_user.id, request.game_id)
    return {"message": "Added to cart", "cart_item_id": cart_item.id}


@router.post("/remove")
async def remove_from_cart(
    request: RemoveFromCartRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove a game from user's cart."""
    success = CartService.remove_from_cart(db, current_user.id, request.game_id)
    if not success:
        raise HTTPException(status_code=404, detail="Item not found in cart")
    return {"message": "Removed from cart"}


@router.get("", response_model=CartResponse)
async def get_cart(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's cart."""
    cart_items = CartService.get_user_cart(db, current_user.id)
    
    items_with_game = []
    total = 0.0
    
    for item in cart_items:
        game = db.query(Game).filter(Game.id == item.game_id).first()
        if game:
            items_with_game.append(CartItemWithGame(
                id=item.id,
                game_id=game.id,
                game_name=game.name,
                price=game.price or 0.0,
                image_url=game.image_url,
                created_at=item.created_at
            ))
            total += game.price or 0.0
    
    return CartResponse(
        items=items_with_game,
        count=len(items_with_game),
        total_amount=total
    )


@router.get("/count")
async def get_cart_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get number of items in cart."""
    count = CartService.get_cart_count(db, current_user.id)
    return {"count": count}


@router.delete("/clear")
async def clear_cart(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Clear all items from cart."""
    CartService.clear_cart(db, current_user.id)
    return {"message": "Cart cleared"}
