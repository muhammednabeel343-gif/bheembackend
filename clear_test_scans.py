"""Remove all user scans for Nabeel (stale test data)."""
import sys
sys.path.insert(0, '.')

from app.database import SessionLocal
from app.models.user_scan import UserScan
from app.models.user import User

db = SessionLocal()
try:
    user = db.query(User).filter(User.username == "Nabeel").first()
    if not user:
        print("User not found")
        sys.exit(1)

    scans = db.query(UserScan).filter(UserScan.user_id == user.id).all()
    print(f"Found {len(scans)} scan(s):")
    for s in scans:
        print(f"  cpu={s.cpu}  gpu={s.gpu}  ram={s.ram_gb}GB  storage={s.storage_gb}GB")

    db.query(UserScan).filter(UserScan.user_id == user.id).delete()
    db.commit()
    print("All scans deleted for", user.username)
finally:
    db.close()
