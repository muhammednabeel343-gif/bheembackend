from app.database import SessionLocal
from app.models.game import Game
from app.models.requirement import Requirement
from app.models.user_scan import UserScan
from app.services.compatibility_service import compute_compatibility_report, check_os_compatibility

db = SessionLocal()

print("=" * 80)
print("FINAL VERIFICATION - LIES OF P COMPATIBILITY CHECK")
print("=" * 80)

# Get game and requirements
game = db.query(Game).filter(Game.name.ilike("%lies of p%")).first()
req = db.query(Requirement).filter(Requirement.game_id == game.id).first()
user_scan = db.query(UserScan).filter(UserScan.game_id.is_(None)).order_by(UserScan.scan_time.desc()).first()

print(f"\n📋 GAME: {game.name}")
print(f"   ID: {game.id}")

print(f"\n🎮 GAME REQUIREMENTS:")
print(f"   OS: '{req.operating_system}'")
print(f"   CPU: {req.cpu}")
print(f"   GPU: {req.gpu}")
print(f"   RAM: {req.ram_gb} GB")
print(f"   Storage: {req.storage_gb} GB")

print(f"\n👤 YOUR SYSTEM:")
print(f"   OS: '{user_scan.operating_system}'")
print(f"   CPU: {user_scan.cpu}")
print(f"   GPU: {user_scan.gpu}")
print(f"   RAM: {user_scan.ram_gb} GB")
print(f"   Storage: {user_scan.storage_gb} GB")

print(f"\n" + "=" * 80)
print("RUNNING COMPATIBILITY REPORT")
print("=" * 80)

report = compute_compatibility_report(req, user_scan)

print(f"\n✅ CHECKS:")
for key, value in report["checks"].items():
    symbol = "✓" if value else "✗"
    print(f"   {symbol} {key}: {value}")

print(f"\n📊 OVERALL:")
print(f"   Score: {report['compatibility_percentage']}%")
print(f"   Status: {report['status']}")

print(f"\n" + "=" * 80)
print("JSON RESPONSE (what frontend receives):")
print("=" * 80)

import json
print(json.dumps({
    "checks": report["checks"],
    "minimum_requirements": {
        "operating_system": report["minimum_requirements"]["operating_system"]
    },
    "user_specs": {
        "operating_system": report["user_specs"]["operating_system"]
    },
    "compatibility_percentage": report["compatibility_percentage"],
    "status": report["status"]
}, indent=2))

print(f"\n" + "=" * 80)
if report["checks"]["os_pass"]:
    print("✅ OS CHECK PASSED - Should display green checkmark")
else:
    print("❌ OS CHECK FAILED - Something is still wrong!")
print("=" * 80)

db.close()
