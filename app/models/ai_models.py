from sqlalchemy import Column, Integer, String, DateTime, JSON, func
from app.database import Base


class AIExplanationCache(Base):
    __tablename__ = "explanation_cache"

    id = Column(Integer, primary_key=True, index=True)
    cache_key = Column(String(128), unique=True, nullable=False, index=True)
    request = Column(JSON, nullable=False)
    response = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class AIUpgradeRecommendationCache(Base):
    __tablename__ = "upgrade_recommendations_cache"

    id = Column(Integer, primary_key=True, index=True)
    cache_key = Column(String(128), unique=True, nullable=False, index=True)
    request = Column(JSON, nullable=False)
    response = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
