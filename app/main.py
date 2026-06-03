from app.database import engine, Base, SessionLocal
from app.routes.auth import router as auth_router
from app.routes.games import router as games_router
from app.routes.favorites import router as favorites_router
from app.routes.system import router as system_router
from app.data.seed import seed_sample_games
from contextlib import contextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings

app = FastAPI(title=settings.app_name, version="1.0.0")

app.include_router(auth_router)
app.include_router(games_router)
app.include_router(favorites_router)
app.include_router(system_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Welcome to Project Bheem API"}


@contextmanager
def _seed_once():
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        seed_sample_games(db)
    finally:
        db.close()


@app.post("/seed-db")
async def seed_db():
    _seed_once()
    return {"message": "Database seeded successfully"}
