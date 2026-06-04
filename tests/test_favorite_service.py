import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi import HTTPException

from app.database import Base
from app.models.user import User
from app.models.game import Game
from app.services.favorite_service import add_favorite, get_user_favorite, remove_favorite


def create_test_session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    return sessionmaker(bind=engine)()


def test_add_and_remove_favorite():
    db = create_test_session()

    user = User(username="testuser", email="test@example.com", hashed_password="hash")
    game = Game(name="Test Game", genre="Adventure", publisher="Pub")
    db.add(user)
    db.add(game)
    db.commit()
    db.refresh(user)
    db.refresh(game)

    fav = add_favorite(db, user.id, game.id)
    assert fav.user_id == user.id and fav.game_id == game.id

    with pytest.raises(HTTPException) as exc:
        add_favorite(db, user.id, game.id)
    assert exc.value.status_code == 409

    remove_favorite(db, user.id, game.id)
    assert get_user_favorite(db, user.id, game.id) is None

    with pytest.raises(HTTPException) as exc2:
        remove_favorite(db, user.id, game.id)
    assert exc2.value.status_code == 404
