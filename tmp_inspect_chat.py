from app.config import settings
from sqlalchemy import create_engine, text

def main():
    engine = create_engine(settings.database_url)
    with engine.connect() as conn:
        for sid in [10, 11]:
            print('session', sid)
            rows = conn.execute(text('select id,user_id,title,created_at,updated_at from chat_sessions where id=:id'), {'id': sid}).fetchall()
            print(rows)
            msgs = conn.execute(text('select id,role,content,created_at from chat_messages where session_id=:id order by id'), {'id': sid}).fetchall()
            print(msgs)

if __name__ == '__main__':
    main()
