from app.database import SessionLocal
from app.models.game import Game
from app.models.requirement import Requirement
from app.models.user_scan import UserScan
from app.services.compatibility_service import compute_compatibility_report, check_os_compatibility
from datetime import datetime

db = SessionLocal()

# Get Lies of P game
game = db.query(Game).filter(Game.name.ilike("%lies of p%")).first()

if not game:
    print("❌ Lies of P not found!")
    db.close()
    exit()

print(f"✓ Found: {game.name}")

# Get requirements
req = db.query(Requirement).filter(Requirement.game_id == game.id).first()
if req:
    print(f"\n📋 Game Requirements:")
    print(f"  OS: {req.operating_system}")
    print(f"  CPU: {req.cpu}")
    print(f"  GPU: {req.gpu}")
    print(f"  RAM: {req.ram_gb} GB")
    print(f"  Storage: {req.storage_gb} GB")
else:
    print("❌ No requirements found!")

# Get latest user scan
latest_scan = db.query(UserScan).filter(UserScan.game_id.is_(None)).order_by(UserScan.scan_time.desc()).first()

if not latest_scan:
    print("❌ No user system scan found!")
    db.close()
    exit()

print(f"\n👤 User System:")
print(f"  OS: {latest_scan.operating_system}")
print(f"  CPU: {latest_scan.cpu}")
print(f"  GPU: {latest_scan.gpu}")
print(f"  RAM: {latest_scan.ram_gb} GB")
print(f"  Storage: {latest_scan.storage_gb} GB")

# Test OS compatibility
print(f"\n🔍 OS Compatibility Check:")
print(f"  Required: {req.operating_system}")
print(f"  User has: {latest_scan.operating_system}")
os_compat = check_os_compatibility(req.operating_system, latest_scan.operating_system)
print(f"  Result: {'✓ PASS' if os_compat else '✗ FAIL'}")

# Generate full compatibility report
print(f"\n📊 Full Compatibility Report:")
report = compute_compatibility_report(req, latest_scan)

print(f"\nCompatibility Checks:")
for key, value in report["checks"].items():
    status = "✓ Pass" if value else "✗ Fail"
    print(f"  {key}: {status}")

print(f"\nOverall Score: {report['compatibility_percentage']}%")
print(f"Status: {report['status']}")

db.close()
