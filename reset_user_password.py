import bcrypt
from sqlalchemy import create_engine, text

url = "postgresql://neondb_owner:npg_pbCMLEd6At1k@ep-divine-silence-ap52ue96-pooler.c-7.us-east-1.aws.neon.tech/neondb?channel_binding=require&sslmode=require"
engine = create_engine(url)

password = "123"
hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

with engine.begin() as conn:
    conn.execute(
        text("UPDATE users SET hashed_password = :hashed_password WHERE email = :email"),
        {"hashed_password": hashed, "email": "nabeel@gmail.com"},
    )
    print("Reset nabeel@gmail.com password to: 123")
