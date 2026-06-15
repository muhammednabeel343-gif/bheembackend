from sqlalchemy import text
from app.database import engine

sql = """
ALTER TABLE games
ADD COLUMN IF NOT EXISTS description TEXT DEFAULT '';
"""

with engine.connect() as conn:
    conn.execute(text(sql))
    conn.commit()

print("description column ensured on games table")
