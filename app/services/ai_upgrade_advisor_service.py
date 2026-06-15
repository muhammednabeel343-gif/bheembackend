from typing import Dict, Any, List
from app.services.google_ai_client import GoogleAIClient
from app.config import settings
from app.schemas.ai_schemas import UpgradeRequest, UpgradeResponse, UpgradeOption


class AIUpgradeAdvisorService:
    def __init__(self, client: GoogleAIClient = None):
        self.client = client or GoogleAIClient(api_key=settings.ai_api_key,
                                               project_id=settings.google_project_id,
                                               enable=settings.ai_enabled)

    def recommend(self, req: UpgradeRequest) -> UpgradeResponse:
        profile = req.system_profile

        # Simple heuristic mock: find lowest-percent component vs requirement hints
        # Expect profile to contain cpu_score, gpu_score, ram_gb
        cpu = profile.get("cpu_score")
        gpu = profile.get("gpu_score")
        ram = profile.get("ram_gb")

        # Detect bottleneck
        bottleneck = "unknown"
        scores = {"gpu": gpu or 0, "cpu": cpu or 0, "ram": ram or 0}
        # Find key with lowest normalized value (mock heuristic)
        bottleneck = min(scores, key=lambda k: scores[k])

        options: List[UpgradeOption] = []
        if bottleneck == "gpu":
            options.append(UpgradeOption(component="gpu", current=gpu, suggested="RTX 4060 Ti", cost_estimate="$300-400", expected_gain_pct=30.0))
            options.append(UpgradeOption(component="gpu", current=gpu, suggested="RTX 4070", cost_estimate="$500-700", expected_gain_pct=55.0))
        elif bottleneck == "cpu":
            options.append(UpgradeOption(component="cpu", current=cpu, suggested="Ryzen 7 5700X3D", cost_estimate="$200-350", expected_gain_pct=25.0))
        else:
            options.append(UpgradeOption(component="ram", current=ram, suggested="32GB", cost_estimate="$60-120", expected_gain_pct=10.0))

        return UpgradeResponse(bottleneck=bottleneck, options=options)


__all__ = ["AIUpgradeAdvisorService"]
