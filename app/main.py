from app.models.user_scan import UserScan
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
print("PROJECT BHEEM MAIN LOADED")
from app.config import settings
from app.database import engine, Base, SessionLocal
from app.routes.auth import router as auth_router
from app.routes.games import router as games_router
from app.routes.favorites import router as favorites_router
from app.routes.system import router as system_router
from app.data.seed import seed_sample_games

Base.metadata.create_all(bind=engine)
with SessionLocal() as db:
    seed_sample_games(db)

app = FastAPI(title=settings.app_name, version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth_router)
app.include_router(games_router)
app.include_router(favorites_router)
app.include_router(system_router)


@app.get("/")
async def root():
    return {"message": "Welcome to Project Bheem API"}
