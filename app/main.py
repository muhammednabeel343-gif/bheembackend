from pathlib import Path
from app.database import engine, Base, SessionLocal
from app.routes.auth import router as auth_router
from app.routes.games import router as games_router
from app.routes.favorites import router as favorites_router
from app.routes.system import router as system_router
from app.routes.admin_auth import router as admin_auth_router
from app.routes.admin_dashboard import router as admin_dashboard_router
from app.routes.admin_games import router as admin_games_router
from app.routes.cpus import router as cpu_router
from app.routes.gpus import router as gpu_router
from app.routes.rams import router as ram_router
from app.routes.storages import router as storage_router
from app.data.seed import seed_sample_games
from contextlib import contextmanager
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.config import settings
import shutil, os, uuid

# Safe path calculation: main.py is at backend/app/main.py
# parent = backend/app, parent.parent = backend/ (the project root)
BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

app = FastAPI(title=settings.app_name, version="1.0.0")

app.include_router(auth_router)
app.include_router(games_router)
app.include_router(admin_auth_router)
app.include_router(admin_dashboard_router)
app.include_router(admin_games_router)
app.include_router(favorites_router)
app.include_router(system_router)
app.include_router(cpu_router)
app.include_router(gpu_router)
app.include_router(ram_router)
app.include_router(storage_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="game-images")

@app.post("/admin/upload-image")
async def upload_image(file: UploadFile = File(...), token: str = ""):
    ext = os.path.splitext(file.filename)[1] or ".png"
    filename = f"{uuid.uuid4().hex}{ext}"
    file_location = UPLOAD_DIR / filename
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    api_url = f"{settings.api_base_url}/uploads/{filename}"
    return {"url": api_url}


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
