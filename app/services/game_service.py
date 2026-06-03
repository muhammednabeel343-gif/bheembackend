from typing import List, Optional, Tuple, Dict
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.game import Game
from app.models.favorite import Favorite


def list_games(
    db: Session,
    user_id: int,
    search: Optional[str] = None,
    category: Optional[str] = None,
    page: int = 1,
    limit: int = 20,
) -> Tuple[List[Game], int, Dict[int, bool]]:

    query = db.query(Game)

    if search:
        search_value = f"%{search.lower()}%"
        query = query.filter(func.lower(Game.name).like(search_value))

    if category:
        query = query.filter(Game.genre == category)

    total = query.count()

    items = (
        query
        .order_by(Game.name.asc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    favorite_map = load_favorite_map(db, user_id)

    return items, total, favorite_map


def get_game_by_id(db: Session, game_id: int) -> Optional[Game]:
    return db.query(Game).filter(Game.id == game_id).first()


def get_similar_games(
    db: Session,
    game_id: int,
    limit: int = 5
) -> List[Game]:

    base_game = get_game_by_id(db, game_id)

    if not base_game:
        return []

    return (
        db.query(Game)
        .filter(
            Game.genre == base_game.genre,
            Game.id != game_id
        )
        .order_by(Game.name.asc())
        .limit(limit)
        .all()
    )


def load_favorite_map(
    db: Session,
    user_id: int
) -> dict[int, bool]:

    favorite_rows = (
        db.query(Favorite.game_id)
        .filter(Favorite.user_id == user_id)
        .all()
    )

    return {
        game_id: True
        for (game_id,) in favorite_rows
    }