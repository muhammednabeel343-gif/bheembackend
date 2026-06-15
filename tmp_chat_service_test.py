from app.database import engine
from sqlalchemy.orm import Session
from app.models.user import User
from app.services.chat_service import ChatService

with Session(engine) as db:
    user = db.query(User).filter(User.id == 1).first()
    print('user', user.id, user.email if user else None)
    svc = ChatService(db, user)
    for sid in [10, 11]:
        try:
            msgs = svc.get_messages(sid)
            print('session', sid, 'msgs', len(msgs), [m.id for m in msgs])
        except Exception as e:
            print('session', sid, 'error', type(e).__name__, e)
