from sqlalchemy import text
from app.database import engine

sql = """
ALTER TABLE games
ADD COLUMN IF NOT EXISTS price double precision DEFAULT 0.0;
"""

with engine.connect() as conn:
    conn.execute(text(sql))
    conn.commit()

print("price column ensured on games table")
