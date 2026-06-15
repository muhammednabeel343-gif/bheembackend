from typing import Dict, Any, Optional
from app.services.google_ai_client import GoogleAIClient
from app.config import settings
from app.schemas.ai_schemas import ExplanationRequest, ExplanationResponse


class AIExplanationService:
    def __init__(self, client: GoogleAIClient = None):
        self.client = client or GoogleAIClient(api_key=settings.google_api_key,
                                               project_id=settings.google_project_id,
                                               enable=settings.enable_ai_features)

    def explain(self, req: ExplanationRequest) -> ExplanationResponse:
        # If AI is not enabled or client is in mock mode, return deterministic explanation
        if self.client.mock:
            # Simple heuristic-based explanation
            cpu_req = req.game_requirements.get("cpu_score", None)
            gpu_req = req.game_requirements.get("gpu_score", None)
            ram_req = req.game_requirements.get("ram_gb", None)

            cpu_sys = req.system_profile.get("cpu_score", None)
            gpu_sys = req.system_profile.get("gpu_score", None)
            ram_sys = req.system_profile.get("ram_gb", None)

            parts = []
            if gpu_req and gpu_sys is not None:
                if gpu_sys >= gpu_req:
                    parts.append("✅ GPU meets or exceeds requirements.")
                else:
                    parts.append("⚠ GPU may limit performance.")

            if cpu_req and cpu_sys is not None:
                if cpu_sys >= cpu_req:
                    parts.append("✅ CPU meets requirements.")
                else:
                    parts.append("⚠ CPU may bottleneck in CPU-heavy scenes.")

            if ram_req and ram_sys is not None:
                if ram_sys >= ram_req:
                    parts.append("✅ RAM is sufficient.")
                else:
                    parts.append("⚠ Consider increasing RAM for smoother experience.")

            summary = " ".join(parts) or "No clear compatibility signals available."
            details = {
                "game_requirements": req.game_requirements,
                "system_profile": req.system_profile,
            }
            return ExplanationResponse(summary=summary, details=details)

        # Real AI path: build prompt and request structured response
        prompt = (
            f"Explain why the following system_profile is compatible or not with the game_requirements.\n"
            f"Game requirements: {req.game_requirements}\nSystem profile: {req.system_profile}\n"
            "Provide a short summary and a details object."
        )

        schema = {"summary": "str", "details": {}}
        ai_resp = self.client.generate_structured_response(prompt, schema)
        # Normalize response
        if isinstance(ai_resp, dict) and "summary" in ai_resp:
            return ExplanationResponse(summary=str(ai_resp.get("summary")), details=ai_resp.get("details") or {})
        # Fallback
        return ExplanationResponse(summary=str(ai_resp.get("raw", ai_resp)), details={})

    def explain_compatibility(self, game_name: str, game_requirements: Dict, user_system: Dict, compatibility_score: float) -> Optional[Dict]:
        """Generate AI-powered detailed compatibility explanation."""
        
        prompt = f"""You are a gaming expert analyzing PC hardware compatibility.

Game: {game_name}
Game Requirements:
- GPU: {game_requirements.get('gpu', 'Unknown')}
- CPU: {game_requirements.get('cpu', 'Unknown')}  
- RAM: {game_requirements.get('ram', 0)}GB
- Storage: {game_requirements.get('storage', 0)}GB
- OS: {game_requirements.get('os', 'Windows')}

User's System:
- GPU: {user_system.get('gpu', 'Unknown')}
- CPU: {user_system.get('cpu', 'Unknown')}
- RAM: {user_system.get('ram', 0)}GB
- Storage: {user_system.get('storage', 0)}GB
- OS: {user_system.get('os', 'Windows')}

Compatibility Score: {int(compatibility_score * 100)}%

Provide detailed analysis with:
1. GPU Analysis (1-2 sentences)
2. CPU Analysis (1-2 sentences)
3. RAM Analysis (1 sentence)
4. Storage Analysis (1 sentence)
5. OS Analysis (1 sentence)
6. Expected Experience (e.g., "Ultra settings at 100+ FPS")
7. Recommended Settings (2-3 specific settings)
8. Tips (2-3 optimization tips)
9. Warnings (any concerns, or empty array if none)"""

        response_format = {
            "gpu_analysis": "GPU compatibility analysis",
            "cpu_analysis": "CPU compatibility analysis",
            "ram_analysis": "RAM sufficiency analysis",
            "storage_analysis": "Storage space analysis",
            "os_analysis": "OS compatibility analysis",
            "expected_experience": "e.g., Ultra 120FPS",
            "recommended_settings": ["Ray Tracing: On", "Resolution: 4K", "Upscaling: DLSS Ultra"],
            "tips": ["Close background apps", "Update drivers", "Adjust power settings"],
            "warnings": []
        }

        result = self.client.generate_structured_response(prompt, response_format)
        
        # If result is None, return fallback mock data
        if not result:
            print("[AI] Using fallback mock data")
            return {
                "gpu_analysis": f"Your {user_system.get('gpu', 'GPU')} is well-suited for {game_name}.",
                "cpu_analysis": f"Your {user_system.get('cpu', 'CPU')} provides solid performance.",
                "ram_analysis": f"With {user_system.get('ram', 0)}GB RAM, you have sufficient memory.",
                "storage_analysis": f"You have enough storage space for this game.",
                "os_analysis": f"{user_system.get('os', 'Windows')} is fully compatible.",
                "expected_experience": f"{'Ultra' if compatibility_score >= 0.9 else 'High' if compatibility_score >= 0.7 else 'Medium'} settings with stable FPS",
                "recommended_settings": [
                    f"Graphics Quality: {'Ultra' if compatibility_score >= 0.9 else 'High' if compatibility_score >= 0.7 else 'Medium'}",
                    "Ray Tracing: On" if compatibility_score >= 0.8 else "Ray Tracing: Off",
                    "Resolution: 1440p" if compatibility_score >= 0.8 else "Resolution: 1080p"
                ],
                "tips": [
                    "Keep GPU drivers updated for optimal performance",
                    "Close background applications before gaming",
                    "Monitor temperatures during extended sessions"
                ],
                "warnings": [] if compatibility_score >= 0.7 else [f"Consider lowering graphics settings for better stability"]
            }
        
        return result


__all__ = ["AIExplanationService"]
