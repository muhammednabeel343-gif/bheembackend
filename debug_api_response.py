import requests
import json

# Test the actual API endpoint like the frontend would
token = "test_token"  # This will fail, but we can check the backend directly

print("=" * 80)
print("TESTING WHAT FRONTEND RECEIVES FROM API")
print("=" * 80)

# Simulate what the frontend does
from app.database import SessionLocal
from app.models.user import User
from app.models.game import Game
from app.services.compatibility_service import build_game_compatibility

db = SessionLocal()

# Get or create a test user
user = db.query(User).first()
if not user:
    print("❌ No user found in database!")
    db.close()
    exit()

print(f"\n👤 Using User: {user.id}")

# Get Lies of P
game = db.query(Game).filter(Game.name.ilike("%lies of p%")).first()
if not game:
    print("❌ Game not found!")
    db.close()
    exit()

print(f"🎮 Game: {game.name} (ID: {game.id})")

# Build compatibility report like the API does
try:
    report = build_game_compatibility(db, user.id, game.id)
    
    print("\n" + "=" * 80)
    print("FULL API RESPONSE:")
    print("=" * 80)
    
    print(json.dumps(report, indent=2, default=str))
    
    print("\n" + "=" * 80)
    print("CHECKS OBJECT (What Frontend Reads):")
    print("=" * 80)
    
    checks = report.get("checks", {})
    for key, value in checks.items():
        print(f"  {key}: {value}")
    
    print("\n" + "=" * 80)
    if "os_pass" in checks:
        print(f"✅ os_pass found: {checks['os_pass']}")
    else:
        print(f"❌ os_pass NOT FOUND in checks!")
        print(f"Available keys: {list(checks.keys())}")
    print("=" * 80)
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

db.close()
