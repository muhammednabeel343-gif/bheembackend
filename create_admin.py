import bcrypt
from sqlalchemy import create_engine, text

url = "postgresql://neondb_owner:npg_pbCMLEd6At1k@ep-divine-silence-ap52ue96-pooler.c-7.us-east-1.aws.neon.tech/neondb?channel_binding=require&sslmode=require"
engine = create_engine(url)

email = "admin@gmail.com"
password = "admin123"
hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

with engine.begin() as conn:
    row = conn.execute(text("SELECT id FROM admins WHERE username = :username"), {"username": "admin"}).fetchone()
    if not row:
        conn.execute(
            text("INSERT INTO admins (username, email, hashed_password) VALUES (:username, :email, :hashed_password)"),
            {"username": "admin", "email": email, "hashed_password": hashed},
        )
        print(f"Created admin: {email} / {password}")
    else:
        conn.execute(
            text("UPDATE admins SET email = :email, hashed_password = :hashed_password WHERE username = :username"),
            {"email": email, "hashed_password": hashed, "username": "admin"},
        )
        print(f"Updated admin to: {email} / {password}")
