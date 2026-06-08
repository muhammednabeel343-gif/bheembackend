from app.database import SessionLocal
from app.models.game import Game
from app.models.requirement import Requirement
from app.models.user_scan import UserScan
from app.data.os_benchmarks import OS_BENCHMARKS
from app.services.compatibility_service import get_os_score, check_os_compatibility

db = SessionLocal()

# Get exact values from database
game = db.query(Game).filter(Game.name.ilike("%lies of p%")).first()
req = db.query(Requirement).filter(Requirement.game_id == game.id).first()
latest_scan = db.query(UserScan).filter(UserScan.game_id.is_(None)).order_by(UserScan.scan_time.desc()).first()

game_os = req.operating_system
user_os = latest_scan.operating_system

print("=" * 60)
print("DEBUGGING OS COMPATIBILITY")
print("=" * 60)

print(f"\nGame Minimum OS: '{game_os}'")
print(f"User OS:        '{user_os}'")

print(f"\n--- OS Benchmark Scores ---")
print(f"Available OS_BENCHMARKS keys:")
for key in sorted(OS_BENCHMARKS.keys()):
    print(f"  '{key}': {OS_BENCHMARKS[key]}")

print(f"\n--- Score Matching ---")
game_score = get_os_score(game_os)
user_score = get_os_score(user_os)
print(f"Game OS score: {game_score}")
print(f"User OS score: {user_score}")

print(f"\n--- String Matching Debug ---")
game_os_lower = (game_os or "").lower()
user_os_lower = (user_os or "").lower()
print(f"Game OS (lowercase): '{game_os_lower}'")
print(f"User OS (lowercase): '{user_os_lower}'")

print(f"\nChecking matches for game OS '{game_os_lower}':")
for key in OS_BENCHMARKS.keys():
    if key in game_os_lower:
        print(f"  ✓ Found match: '{key}'")

print(f"\nChecking matches for user OS '{user_os_lower}':")
for key in OS_BENCHMARKS.keys():
    if key in user_os_lower:
        print(f"  ✓ Found match: '{key}'")

print(f"\n--- OS Compatibility Check ---")
result = check_os_compatibility(game_os, user_os)
print(f"check_os_compatibility('{game_os}', '{user_os}')")
print(f"Result: {result}")

if not result:
    print("\n❌ FAILED - Analyzing why...")
    
    def get_os_family(os_str):
        if "windows" in os_str:
            return "windows"
        elif "ubuntu" in os_str or "linux" in os_str:
            return "linux"
        elif "mac" in os_str:
            return "macos"
        return None
    
    game_family = get_os_family(game_os_lower)
    user_family = get_os_family(user_os_lower)
    
    print(f"  Game OS family: {game_family}")
    print(f"  User OS family: {user_family}")
    print(f"  Game score: {game_score}")
    print(f"  User score: {user_score}")
    
    if game_family != user_family and game_family is not None and user_family is not None:
        print(f"  → Different OS families!")
    elif user_score < game_score:
        print(f"  → User OS score ({user_score}) < Game score ({game_score})")
else:
    print("\n✅ PASS - Compatibility check successful")

db.close()
