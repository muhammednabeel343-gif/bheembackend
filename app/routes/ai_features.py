from fastapi import APIRouter, HTTPException
from app.services.ai_explanation_service import AIExplanationService
from app.config import settings
from pydantic import BaseModel
from typing import Optional, List

router = APIRouter(prefix="/api/ai", tags=["AI"])


class CompatibilityExplanationRequest(BaseModel):
    game_name: str
    game_requirements: dict
    user_system: dict
    compatibility_score: float


class UpgradeRecommendationRequest(BaseModel):
    user_system: dict
    average_compatibility: float
    games_played: Optional[List[str]] = None


@router.post("/compatibility-explanation")
async def get_compatibility_explanation(request: CompatibilityExplanationRequest):
    """Generate AI-powered compatibility explanation."""
    try:
        print(f"[AI] Compatibility explanation request for {request.game_name}")
        
        service = AIExplanationService()
        result = service.explain_compatibility(
            game_name=request.game_name,
            game_requirements=request.game_requirements,
            user_system=request.user_system,
            compatibility_score=request.compatibility_score
        )
        
        print(f"[AI] Result: {result}")
        
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        print(f"[AI] Error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upgrade-recommendation")
async def get_upgrade_recommendation(request: UpgradeRecommendationRequest):
    """Generate AI-powered upgrade recommendation."""
    try:
        print(f"[AI] Upgrade recommendation request")
        
        # Simple recommendation based on compatibility score
        should_upgrade = request.average_compatibility < 0.7
        
        return {
            "success": True,
            "data": {
                "should_upgrade": should_upgrade,
                "message": "Upgrade recommended" if should_upgrade else "Your system is adequate for most games"
            }
        }
    except Exception as e:
        print(f"[AI] Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def ai_health_check():
    """Health check for AI services."""
    from app.services.google_ai_client import GoogleAIClient
    
    client = GoogleAIClient(
        api_key=settings.ai_api_key,
        project_id=settings.google_project_id,
        enable=settings.ai_enabled,
        model=settings.gemini_model,
    )
    
    return {
        "status": "ok",
        "ai_enabled": settings.ai_enabled,
        "ai_initialized": not client.mock,
        "model": settings.gemini_model,
    }
