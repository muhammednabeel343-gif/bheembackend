from app.database import SessionLocal
from app.models.game import Game
from app.models.requirement import Requirement

db = SessionLocal()

print("=" * 80)
print("CHECKING ALL GAMES' MINIMUM OS REQUIREMENTS")
print("=" * 80)

games = db.query(Game).all()

for game in games:
    req = db.query(Requirement).filter(Requirement.game_id == game.id).first()
    
    print(f"\n{game.id}. {game.name}")
    if req:
        print(f"   OS Requirement: {repr(req.operating_system)}")
        print(f"   Type: {type(req.operating_system)}")
    else:
        print(f"   No requirements found")

db.close()
