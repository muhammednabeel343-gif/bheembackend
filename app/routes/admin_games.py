from datetime import date
from typing import Optional, Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.game import Game
from app.models.requirement import Requirement
from app.schemas.game import GameListItem, GameDetail
from app.schemas.game_admin import GameCreate, GameUpdate, GameResponse
from app.services.game_service import list_games, get_game_by_id, load_favorite_map
from app.authentication.admin_jwt import get_current_admin
from app.models.user import User
from app.utils.image_url import normalize_image_url

router = APIRouter(prefix="/admin/games", tags=["Game Management"])


@router.get("")
def get_games(
    page: int = 1,
    limit: int = 50,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    games, total, favorite_map = list_games(db, current_user.id, search=None, category=None, page=page, limit=limit)

    items: List[GameResponse] = []
    for g in games:
        req = g.requirements[0] if g.requirements else None
        items.append(
            GameResponse(
                id=g.id,
                name=g.title,
                genre=g.genre or "",
                publisher=g.publisher,
                release_date=g.release_date.isoformat() if g.release_date else None,
                image_url=normalize_image_url(g.thumbnail_url),
                cpu=req.cpu if req else None,
                gpu=req.gpu if req else None,
                ram_gb=req.ram_gb if req else None,
                storage=req.storage_gb if req else None,
                directx=req.directx if req else None,
                operating_system=req.operating_system if req else None,
            )
        )

    return {"games": items, "total": total, "page": page, "limit": limit}


@router.get("/{game_id}")
def get_game(game_id: int, current_user: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    game = get_game_by_id(db, game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    favorite_map = load_favorite_map(db, current_user.id)
    req = game.requirements[0] if game.requirements else None
    return {
        "id": game.id,
        "name": game.title,
        "genre": game.genre,
        "publisher": game.publisher,
        "release_date": game.release_date.isoformat() if game.release_date else None,
        "image_url": normalize_image_url(game.thumbnail_url),
        "cpu": req.cpu if req else None,
        "gpu": req.gpu if req else None,
        "ram_gb": req.ram_gb if req else None,
        "storage": req.storage_gb if req else None,
        "directx": req.directx if req else None,
        "operating_system": req.operating_system if req else None,
        "is_favorite": favorite_map.get(game.id, False),
    }


@router.post("")
def create_game(payload: GameCreate, current_user: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    game = Game(
        name=payload.name,
        description=payload.description,
        genre=payload.genre,
        publisher=payload.publisher,
        release_date=payload.release_date,
        image_url=payload.image_url,
    )
    db.add(game)
    db.commit()
    db.refresh(game)

    req = Requirement(
        game_id=game.id,
        cpu=payload.cpu or "",
        gpu=payload.gpu or "",
        ram=payload.ram_gb or 0,
        storage=payload.storage or 0,
        directx=payload.directx,
        operating_system=payload.operating_system,
    )
    db.add(req)
    db.commit()
    db.refresh(req)

    return {
        "id": game.id,
        "name": game.name,
        "genre": game.genre,
        "publisher": game.publisher,
        "release_date": game.release_date,
        "image_url": game.image_url,
        "cpu": req.cpu,
        "gpu": req.gpu,
        "ram_gb": req.ram_gb,
        "storage": req.storage_gb,
        "directx": req.directx,
        "operating_system": req.operating_system,
    }


@router.put("/{game_id}")
def update_game(game_id: int, payload: GameUpdate, current_user: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    game = db.query(Game).filter(Game.id == game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    if payload.name is not None:
        game.name = payload.name
    if payload.description is not None:
        game.description = payload.description
    if payload.genre is not None:
        game.genre = payload.genre
    if payload.publisher is not None:
        game.publisher = payload.publisher
    if payload.release_date is not None:
        game.release_date = payload.release_date
    if payload.image_url is not None:
        game.image_url = payload.image_url

    req = db.query(Requirement).filter(Requirement.game_id == game_id).first()
    if not req:
        req = Requirement(game_id=game_id)
        db.add(req)

    if payload.cpu is not None:
        req.cpu = payload.cpu
    if payload.gpu is not None:
        req.gpu = payload.gpu
    if payload.ram_gb is not None:
        req.ram = payload.ram_gb
    if payload.storage is not None:
        req.storage = payload.storage
    if payload.directx is not None:
        req.directx = payload.directx
    if payload.operating_system is not None:
        req.operating_system = payload.operating_system

    db.commit()
    db.refresh(game)
    db.refresh(req)

    return {
        "id": game.id,
        "name": game.name,
        "genre": game.genre,
        "publisher": game.publisher,
        "release_date": game.release_date,
        "image_url": game.image_url,
        "cpu": req.cpu,
        "gpu": req.gpu,
        "ram_gb": req.ram_gb,
        "storage": req.storage_gb,
        "directx": req.directx,
        "operating_system": req.operating_system,
    }


@router.delete("/{game_id}")
def delete_game(game_id: int, current_user: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    game = db.query(Game).filter(Game.id == game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    db.delete(game)
    db.commit()
    return {"message": "Game deleted"}
