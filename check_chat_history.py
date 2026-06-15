import sys
sys.path.insert(0, '.')
from dotenv import load_dotenv
from pathlib import Path
load_dotenv(Path('.env'))

from app.database import SessionLocal
from app.models.chat import ChatSession, ChatMessage
from app.models.user import User

db = SessionLocal()

users = db.query(User).all()
for user in users:
    sessions = db.query(ChatSession).filter(ChatSession.user_id == user.id).order_by(ChatSession.updated_at.desc()).all()
    print(f"\nUser: {user.username} (id={user.id}) — {len(sessions)} session(s)")
    for s in sessions:
        msgs = db.query(ChatMessage).filter(ChatMessage.session_id == s.id).order_by(ChatMessage.id).all()
        print(f"  Session #{s.id}: '{s.title}' | {len(msgs)} messages | updated: {s.updated_at}")
        for m in msgs:
            print(f"    [{m.role.upper():9s}] {m.content[:80].strip()}...")

db.close()
