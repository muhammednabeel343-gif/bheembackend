from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.authentication.jwt import get_current_user
from app.models.user import User
from app.models.game import Game
from app.services.purchase_service import PurchaseService
from app.models.purchase import PurchasedGame
from app.schemas.purchase import (
    PurchasedGameResponse,
    UserLibraryResponse,
    IsPurchasedResponse
)

router = APIRouter(prefix="/purchases", tags=["purchases"])


@router.get("/library", response_model=UserLibraryResponse)
async def get_library(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's game library (all purchased games)."""
    library = PurchaseService.get_user_library(db, current_user.id)
    
    return UserLibraryResponse(
        games=library,
        total_count=len(library)
    )


@router.get("/count")
async def get_purchase_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get total number of games purchased."""
    count = PurchaseService.get_purchase_count(db, current_user.id)
    return {"total_purchased": count}


@router.get("/{game_id}/check", response_model=IsPurchasedResponse)
async def check_purchase(
    game_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Check if user has purchased a specific game."""
    # Verify game exists
    game = db.query(Game).filter(Game.id == game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    is_purchased = PurchaseService.is_game_purchased(db, current_user.id, game_id)
    
    if is_purchased:
        purchased = db.query(PurchasedGame).filter(
            PurchasedGame.user_id == current_user.id,
            PurchasedGame.game_id == game_id
        ).first()
        purchase_date = purchased.purchase_date if purchased else None
    else:
        purchase_date = None
    
    return IsPurchasedResponse(
        is_purchased=is_purchased,
        purchase_date=purchase_date
    )
