"""Integration test for RecommendationService using a temporary SQLite file DB.

Usage: python backend/scripts/integration_test_recs.py

This script sets DATABASE_URL to a local SQLite file, creates tables, seeds data,
then invokes RecommendationService.recommend_for_user and prints the top results.
"""
import os
import tempfile
import json
import sys

# Ensure backend is on path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Use a temporary sqlite file
tmp = tempfile.NamedTemporaryFile(prefix='recs_test_', suffix='.db', delete=False)
db_path = tmp.name
tmp.close()

os.environ['DATABASE_URL'] = f'sqlite:///{db_path}'

from app.database import engine, Base, SessionLocal
from app.models.game import Game
from app.models.requirement import Requirement
from app.models.user_scan import UserScan
from app.services.recommendation_service import RecommendationService

print('Using test DB at', db_path)

# Create tables
Base.metadata.create_all(bind=engine)

# Seed data
db = SessionLocal()
try:
    # Create sample games
    game1 = Game(name='Fast Racer', description='Racing game', genre='Racing')
    game2 = Game(name='Slow Puzzle', description='Puzzle game', genre='Puzzle')
    game3 = Game(name='Action Blast', description='Action game', genre='Action')
    db.add_all([game1, game2, game3])
    db.commit()
    db.refresh(game1)
    db.refresh(game2)
    db.refresh(game3)

    # Add requirements
    req1 = Requirement(game_id=game1.id, cpu='Ryzen 7', gpu='RTX 3080', ram=16, storage=50, directx='12', operating_system='Windows 10')
    req2 = Requirement(game_id=game2.id, cpu='i3', gpu='Intel HD', ram=4, storage=10, directx='11', operating_system='Windows 7')
    req3 = Requirement(game_id=game3.id, cpu='i5', gpu='GTX 1060', ram=8, storage=30, directx='12', operating_system='Windows 10')
    db.add_all([req1, req2, req3])
    db.commit()

    # Seed a user scan with strong GPU
    scan = UserScan(user_id=1, game_id=None, cpu='i7', gpu='RTX 3070', ram_gb=16, storage_gb=200, operating_system='Windows 10', compatibility_score=0.0, fps_estimate=0, status='OK')
    db.add(scan)
    db.commit()
    db.refresh(scan)

    print('Seeded data: games', [g.id for g in [game1, game2, game3]], 'scan id', scan.id)

    # Run recommendation
    svc = RecommendationService()
    resp = svc.recommend_for_user(user_id=1, limit=3)
    print('Recommendations:')
    for r in resp.recommendations:
        print(f' - {r.game_id}: {r.name} (compat={r.compatibility})')

finally:
    db.close()

# Cleanup note
print('Test DB left at', db_path)
print('Remove it when done if desired.')
