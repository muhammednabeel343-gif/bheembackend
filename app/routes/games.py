from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.schemas.game import GameListResponse, GameListItem, GameDetail
from app.schemas.compatibility import CompatibilityResponse
from app.services.game_service import list_games, get_game_by_id, get_similar_games, load_favorite_map
from app.services.compatibility_service import build_game_compatibility
from app.database import get_db
from app.authentication.jwt import get_current_user
from app.models.user import User
from app.utils.image_url import normalize_image_url

router = APIRouter(prefix="/games", tags=["games"])


@router.get("", response_model=GameListResponse)
async def read_games(
    search: Optional[str] = Query(None, description="Search game titles"),
    category: Optional[str] = Query(None, description="Filter by category"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    games, total, favorite_map = list_games(db, current_user.id, search, category, page, limit)

    items = [
        GameListItem(
            id=game.id,
            name=game.title,
            genre=game.genre or "",
            image_url=normalize_image_url(game.thumbnail_url),
            is_favorite=favorite_map.get(game.id, False),
        )
        for game in games
    ]
    return {"games": items, "total": total, "page": page, "limit": limit}


@router.get("/{game_id}", response_model=GameDetail)
async def read_game(game_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    game = get_game_by_id(db, game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    favorite_map = load_favorite_map(db, current_user.id)
    return GameDetail(
        id=game.id,
        name=game.title,
        description=game.description,
        price=game.price,
        genre=game.genre,
        publisher=game.publisher,
        release_date=game.release_date,
        image_url=normalize_image_url(game.thumbnail_url),
        requirements=game.requirements,
        is_favorite=favorite_map.get(game.id, False),
    )


@router.post("/{game_id}/compatibility")
async def game_compatibility(
    game_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        print("COMPATIBILITY REQUEST:", game_id)

        report = build_game_compatibility(
            db,
            current_user.id,
            game_id
        )

        print("REPORT GENERATED")

        return report

    except Exception as e:
        import traceback
        traceback.print_exc()
        print("COMPATIBILITY ERROR:", repr(e))
        raise


@router.get("/{game_id}/similar", response_model=list[GameListItem])
async def read_similar_games(game_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    similar = get_similar_games(db, game_id)
    favorite_map = load_favorite_map(db, current_user.id)
    return [
        GameListItem(
            id=game.id,
            name=game.title,
            genre=game.genre or "",
            image_url=game.thumbnail_url,
            is_favorite=favorite_map.get(game.id, False),
        )
        for game in similar
    ]
