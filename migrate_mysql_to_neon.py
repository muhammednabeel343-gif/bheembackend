import os
from datetime import date, datetime
from typing import Any

import bcrypt
import mysql.connector
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

NEON_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://neondb_owner:npg_pbCMLEd6At1k@ep-divine-silence-ap52ue96-pooler.c-7.us-east-1.aws.neon.tech/neondb?channel_binding=require&sslmode=require",
)

MYSQL_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "admin",
    "database": "projectbheem",
}


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def to_date(val: Any) -> date | None:
    if isinstance(val, (date, datetime)):
        d = val if isinstance(val, date) else val.date()
        if str(d.year) == "0000" or str(d) == "0000-00-00":
            return None
        return d
    if isinstance(val, str) and val.strip() not in {"", "0000-00-00"}:
        try:
            return date.fromisoformat(val)
        except Exception:
            return None
    return None


def migrate():
    mysql_conn = mysql.connector.connect(**MYSQL_CONFIG)
    mysql_cursor = mysql_conn.cursor(dictionary=True)

    mysql_cursor.execute("SELECT COUNT(*) as cnt FROM games")
    game_count = mysql_cursor.fetchone()["cnt"]
    print(f"MySQL game count: {game_count}")

    if game_count == 0:
        print("No games to migrate.")
        mysql_conn.close()
        return

    users = []
    mysql_cursor.execute("SELECT id, username, email, password_hash, hashed_password, created_at FROM users")
    users.extend(mysql_cursor.fetchall())

    mysql_cursor.execute("SELECT id, name, genre, publisher, release_date, image_url, created_at FROM games")
    games = mysql_cursor.fetchall()

    mysql_cursor.execute("SELECT id, game_id, cpu, gpu, ram, storage, directx, os, created_at FROM requirements")
    reqs = mysql_cursor.fetchall()

    mysql_cursor.execute("SELECT id, user_id, game_id, created_at FROM favourites")
    favs = mysql_cursor.fetchall()

    mysql_cursor.execute(
        "SELECT id, user_id, game_id, cpu, gpu, ram_gb, storage_gb, operating_system, compatibility_score, fps_estimate, status, scan_time FROM user_scans"
    )
    scans = mysql_cursor.fetchall()

    mysql_cursor.close()
    mysql_conn.close()
    print(f"Loaded users={len(users)}, games={len(games)}, requirements={len(reqs)}, favorites={len(favs)}, scans={len(scans)}")

    engine = create_engine(NEON_URL, pool_pre_ping=True, pool_recycle=300, pool_size=5, max_overflow=10, pool_timeout=30, echo=False)
    with engine.begin() as conn:
        conn.execute(text("DROP TABLE IF EXISTS user_scans, requirements, favorites, games, users CASCADE"))
    print("Dropped Neon app tables.")

    with engine.begin() as conn:
        conn.execute(
            text(
                """
                CREATE TABLE users (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(50) NOT NULL UNIQUE,
                    email VARCHAR(100) NOT NULL UNIQUE,
                    hashed_password VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
        )
        for row in users:
            conn.execute(
                text(
                    "INSERT INTO users (id, username, email, hashed_password, created_at) "
                    "VALUES (:id, :username, :email, :hashed_password, :created_at)"
                ),
                {
                    "id": row["id"],
                    "username": row["username"],
                    "email": row["email"],
                    "hashed_password": row.get("password_hash") or row.get("hashed_password") or hash_password("default123"),
                    "created_at": to_date(row.get("created_at")),
                },
            )
        print(f"Migrated users: {len(users)}")

        conn.execute(
            text(
                """
                CREATE TABLE games (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    genre VARCHAR(100),
                    publisher VARCHAR(255),
                    release_date DATE,
                    image_url VARCHAR(1000),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
        )
        for row in games:
            conn.execute(
                text(
                    "INSERT INTO games (id, name, genre, publisher, release_date, image_url, created_at) "
                    "VALUES (:id, :name, :genre, :publisher, :release_date, :image_url, :created_at)"
                ),
                {
                    "id": row["id"],
                    "name": row["name"],
                    "genre": row.get("genre"),
                    "publisher": row.get("publisher"),
                    "release_date": to_date(row.get("release_date")),
                    "image_url": row.get("image_url"),
                    "created_at": to_date(row.get("created_at")),
                },
            )
        print(f"Migrated games: {len(games)}")

        conn.execute(
            text(
                """
                CREATE TABLE requirements (
                    id SERIAL PRIMARY KEY,
                    game_id INTEGER NOT NULL REFERENCES games(id),
                    cpu VARCHAR(100),
                    gpu VARCHAR(100),
                    ram INTEGER,
                    storage INTEGER,
                    directx VARCHAR(20),
                    os VARCHAR(50),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
        )
        for row in reqs:
            conn.execute(
                text(
                    "INSERT INTO requirements (id, game_id, cpu, gpu, ram, storage, directx, os, created_at) "
                    "VALUES (:id, :game_id, :cpu, :gpu, :ram, :storage, :directx, :os, :created_at)"
                ),
                {
                    "id": row["id"],
                    "game_id": row["game_id"],
                    "cpu": row.get("cpu"),
                    "gpu": row.get("gpu"),
                    "ram": int(row["ram"]) if row.get("ram") is not None else None,
                    "storage": int(row["storage"]) if row.get("storage") is not None else None,
                    "directx": row.get("directx"),
                    "os": row.get("os"),
                    "created_at": to_date(row.get("created_at")),
                },
            )
        print(f"Migrated requirements: {len(reqs)}")

        conn.execute(
            text(
                """
                CREATE TABLE favorites (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL REFERENCES users(id),
                    game_id INTEGER NOT NULL REFERENCES games(id),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE (user_id, game_id)
                )
                """
            )
        )
        for row in favs:
            conn.execute(
                text(
                    "INSERT INTO favorites (id, user_id, game_id, created_at) "
                    "VALUES (:id, :user_id, :game_id, :created_at)"
                ),
                {
                    "id": row["id"],
                    "user_id": row["user_id"],
                    "game_id": row["game_id"],
                    "created_at": to_date(row.get("created_at")),
                },
            )
        print(f"Migrated favorites: {len(favs)}")

        conn.execute(
            text(
                """
                CREATE TABLE user_scans (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL REFERENCES users(id),
                    game_id INTEGER REFERENCES games(id),
                    cpu VARCHAR(255) NOT NULL,
                    gpu VARCHAR(255) NOT NULL,
                    ram_gb INTEGER NOT NULL,
                    storage_gb INTEGER NOT NULL,
                    operating_system VARCHAR(100),
                    compatibility_score FLOAT NOT NULL,
                    fps_estimate INTEGER,
                    status VARCHAR(50) NOT NULL,
                    scan_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
        )
        for row in scans:
            conn.execute(
                text(
                    "INSERT INTO user_scans (id, user_id, game_id, cpu, gpu, ram_gb, storage_gb, operating_system, compatibility_score, fps_estimate, status, scan_time) "
                    "VALUES (:id, :user_id, :game_id, :cpu, :gpu, :ram_gb, :storage_gb, :operating_system, :compatibility_score, :fps_estimate, :status, :scan_time)"
                ),
                {
                    "id": row["id"],
                    "user_id": row["user_id"],
                    "game_id": row.get("game_id"),
                    "cpu": row.get("cpu"),
                    "gpu": row.get("gpu"),
                    "ram_gb": int(row["ram_gb"]) if row.get("ram_gb") is not None else None,
                    "storage_gb": int(row["storage_gb"]) if row.get("storage_gb") is not None else None,
                    "operating_system": row.get("operating_system"),
                    "compatibility_score": float(row["compatibility_score"]) if row.get("compatibility_score") is not None else None,
                    "fps_estimate": int(row["fps_estimate"]) if row.get("fps_estimate") is not None else None,
                    "status": row.get("status"),
                    "scan_time": to_date(row.get("scan_time")),
                },
            )
        print(f"Migrated user_scans: {len(scans)}")

    print("Migration completed.")


if __name__ == "__main__":
    migrate()
