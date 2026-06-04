from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.favorite import FavoriteListResponse, FavoriteCreate, FavoriteItem
from app.services.favorite_service import list_user_favorites, add_favorite, remove_favorite
from app.database import get_db
from app.authentication.jwt import get_current_user
from app.models.user import User

router = APIRouter(prefix="/favorites", tags=["favorites"])


@router.get("", response_model=FavoriteListResponse)
async def read_favorites(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    favorites = list_user_favorites(db, current_user.id)
    items = [
        FavoriteItem(
            id=fav.id,
            game_id=fav.game.id,
            name=fav.game.title,
            genre=fav.game.genre,
            image_url=fav.game.thumbnail_url,
        )
        for fav in favorites
    ]
    return {"favorites": items}


@router.post("", response_model=FavoriteItem)
async def create_favorite(payload: FavoriteCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    favorite = add_favorite(db, current_user.id, payload.game_id)
    return FavoriteItem(
        id=favorite.id,
        game_id=favorite.game_id,
        name=favorite.game.title,
        genre=favorite.game.genre,
        image_url=favorite.game.thumbnail_url,
    )


@router.delete("/{game_id}")
async def delete_favorite(game_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    remove_favorite(db, current_user.id, game_id)
    return {"message": "Favorite removed"}
