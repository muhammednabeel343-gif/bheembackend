from sqlalchemy import create_engine, text

engine = create_engine('postgresql://neondb_owner:npg_pbCMLEd6At1k@ep-divine-silence-ap52ue96-pooler.c-7.us-east-1.aws.neon.tech/neondb?channel_binding=require&sslmode=require')

with engine.begin() as conn:
    rows = conn.execute(text("SELECT id, name, genre FROM games ORDER BY id ASC")).fetchall()
    print('games count:', len(rows))
    for row in rows:
        print(row)
