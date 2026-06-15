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
from app.routes.os import router as os_router
from app.routes.ai_features import router as ai_features_router
from app.routes.chatbot import router as chatbot_router
from app.routes.recommendations import router as recommendations_router
from app.routes.chat import router as chat_router
from app.routes.cart import router as cart_router
from app.routes.orders import router as orders_router
from app.routes.purchases import router as purchases_router
from app.routes.community import router as community_router
from app.data.seed import seed_sample_games
from contextlib import asynccontextmanager, contextmanager
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.config import settings
import shutil, os, uuid
import logging
import asyncio

# Safe path calculation: main.py is at backend/app/main.py
# parent = backend/app, parent.parent = backend/ (the project root)
BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan handler: create any missing tables, then validate AI on startup."""
    # Ensure chat tables (and any other new models) exist without requiring
    # a manual migration step in development / first deploy.
    try:
        from app.models import chat as _chat_models  # noqa: F401 – registers models on Base
        Base.metadata.create_all(bind=engine, checkfirst=True)
    except Exception as e:
        logging.warning("create_all failed (non-fatal): %s", e)

    app.state.ai_validation = {"checked": False, "result": None}
    
    # AI validation with timeout to prevent startup hang
    try:
        if settings.ai_enabled and settings.ai_api_key:
            try:
                from app.services.google_ai_client import GoogleAIClient
                client = GoogleAIClient(
                    api_key=settings.ai_api_key,
                    project_id=settings.google_project_id,
                    enable=True,
                    model=settings.gemini_model,
                )
                # Wrap in timeout to prevent indefinite hanging
                result = await asyncio.wait_for(
                    asyncio.to_thread(client.validate),
                    timeout=5.0
                )
                app.state.ai_validation = {"checked": True, "result": result}
                if not result.get("ok"):
                    logging.warning("AI validation failed at startup: %s", result)
                    if settings.ai_fail_fast:
                        raise RuntimeError(f"AI validation failed: {result}")
            except asyncio.TimeoutError:
                logging.warning("AI validation timed out after 5 seconds - continuing without validation")
                app.state.ai_validation = {"checked": True, "result": {"ok": False, "detail": "Validation timeout"}}
        else:
            app.state.ai_validation = {"checked": True, "result": {"ok": True, "mode": "disabled"}}
    except Exception as e:
        app.state.ai_validation = {"checked": True, "result": {"ok": False, "detail": str(e)}}
        logging.exception("Exception during AI validation at startup")
        if settings.ai_fail_fast:
            raise

    yield


app = FastAPI(title=settings.app_name, version="1.0.0", lifespan=lifespan)

# Add CORS middleware FIRST, before routers
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
app.include_router(os_router)
app.include_router(ai_features_router)
app.include_router(chatbot_router)
app.include_router(recommendations_router)
app.include_router(chat_router)
app.include_router(cart_router)
app.include_router(orders_router)
app.include_router(purchases_router)
app.include_router(community_router)

app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="game-images")

@app.post("/admin/upload-image")
async def upload_image(file: UploadFile = File(...), token: str = ""):
    from app.utils.cloudinary_service import upload_image as upload_to_cloudinary, initialize_cloudinary
    
    # Try uploading to Cloudinary first
    cloudinary_initialized = initialize_cloudinary()
    if cloudinary_initialized:
        try:
            file_content = await file.read()
            image_url = upload_to_cloudinary(file_content, file.filename or "image.jpg")

            print("CLOUDINARY RESULT:", image_url)

            if image_url:
                return {"url": image_url}

            print("Cloudinary returned None, using local storage")
        except Exception as e:
            print("CLOUDINARY EXCEPTION:", str(e))
    # Fallback to local storage if Cloudinary not configured or failed
    ext = os.path.splitext(file.filename)[1] or ".png"
    filename = f"{uuid.uuid4().hex}{ext}"
    file_location = UPLOAD_DIR / filename
    
    # Reset file pointer after reading for Cloudinary
    await file.seek(0)
    
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Construct URL using API_BASE_URL if available, fallback to relative path
    if settings.api_base_url:
        api_url = f"{settings.api_base_url}/uploads/{filename}"
    else:
        api_url = f"/uploads/{filename}"
    
    return {"url": api_url}


@app.get("/")
async def root():
    return {"message": "Welcome to Project Bheem API"}


@app.get("/debug/config")
async def debug_config():
    """Debug endpoint to check configuration settings."""
    return {
        "app_name": settings.app_name,
        "api_base_url": settings.api_base_url,
        "cors_origins": settings.cors_origins,
        "cors_origins_list": settings.cors_origins_list,
        "upload_dir": str(UPLOAD_DIR),
        "upload_dir_exists": UPLOAD_DIR.exists(),
    }


@app.get("/debug/test-image-url")
async def debug_test_image_url(url: str):
    """Debug endpoint to test image URL normalization."""
    from app.utils.image_url import normalize_image_url
    
    return {
        "input": url,
        "normalized": normalize_image_url(url),
        "api_base_url": settings.api_base_url,
    }
@app.get("/debug/cloudinary")
async def debug_cloudinary():
    from app.config import settings

    return {
        "cloud_name": settings.cloudinary_cloud_name,
        "api_key_exists": bool(settings.cloudinary_api_key),
        "api_secret_exists": bool(settings.cloudinary_api_secret),
    }


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
