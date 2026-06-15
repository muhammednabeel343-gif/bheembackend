import sys
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, 'backend')

from app.main import app
from app.database import Base, get_db
import app.models.ai_models as ai_models  # ensure models imported


def run_test():
    # File-based SQLite for testing (shared across threads)
    engine = create_engine('sqlite:///./backend/tests/test_ai_db.sqlite3', connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Create tables
    Base.metadata.create_all(bind=engine)
    print('metadata tables:', list(Base.metadata.tables.keys()))

    # Dependency override
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    client = TestClient(app)

    # Test compatibility explanation route
    payload = {
        "game_id": 1,
        "game_requirements": {"cpu_score": 1500, "gpu_score": 5000, "ram_gb": 8},
        "system_profile": {"cpu_score": 1400, "gpu_score": 6000, "ram_gb": 16},
    }

    r = client.post("/api/ai/compatibility-explanation", json=payload)
    print('status', r.status_code, 'body', r.json())
    assert r.status_code == 200
    assert "summary" in r.json()

    # Test upgrade recommendation route
    r2 = client.post("/api/ai/upgrade-recommendation", json={"system_profile": {"cpu_score": 1200, "gpu_score": 3000, "ram_gb": 8}})
    print('status', r2.status_code, 'body', r2.json())
    assert r2.status_code == 200
    assert "bottleneck" in r2.json()


if __name__ == "__main__":
    run_test()
