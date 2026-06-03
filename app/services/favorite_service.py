from typing import List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.favorite import Favorite
from app.models.game import Game


def list_user_favorites(db: Session, user_id: int) -> List[Favorite]:
    return db.query(Favorite).filter(Favorite.user_id == user_id).all()


def get_user_favorite(db: Session, user_id: int, game_id: int) -> Favorite | None:
    return db.query(Favorite).filter(Favorite.user_id == user_id, Favorite.game_id == game_id).first()


def add_favorite(db: Session, user_id: int, game_id: int) -> Favorite:
    existing = get_user_favorite(db, user_id, game_id)
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Game already in favorites")

    game = db.query(Game).filter(Game.id == game_id).first()
    if not game:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Game not found")

    favorite = Favorite(user_id=user_id, game_id=game_id)
    db.add(favorite)
    db.commit()
    db.refresh(favorite)
    return favorite


def remove_favorite(db: Session, user_id: int, game_id: int) -> None:
    favorite = get_user_favorite(db, user_id, game_id)
    if not favorite:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Favorite not found")
    db.delete(favorite)
    db.commit()
