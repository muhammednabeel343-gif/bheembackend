from app.database import SessionLocal
from app.models.game import Game
from app.models.requirement import Requirement

db = SessionLocal()

games = db.query(Game).all()

print("\n=== Games and Their OS Requirements ===\n")
for game in games[:10]:
    req = db.query(Requirement).filter(Requirement.game_id == game.id).first()
    os_req = req.operating_system if req else "None"
    print(f"Game: {game.name:<40} OS: {os_req}")

print("\n=== Total Games: ===\n")
print(f"Total: {len(games)} games")

db.close()
