from app.services.ai_explanation_service import AIExplanationService
from app.services.ai_upgrade_advisor_service import AIUpgradeAdvisorService
from app.schemas.ai_schemas import ExplanationRequest, UpgradeRequest


def test_explanation_mock():
    svc = AIExplanationService()
    req = ExplanationRequest(
        game_id=1,
        game_requirements={"cpu_score": 1500, "gpu_score": 5000, "ram_gb": 8},
        system_profile={"cpu_score": 1400, "gpu_score": 6000, "ram_gb": 16},
    )
    resp = svc.explain(req)
    print("Explanation response:", resp)
    assert "GPU" in resp.summary or resp.summary


def test_upgrade_advisor_mock():
    svc = AIUpgradeAdvisorService()
    req = UpgradeRequest(system_profile={"cpu_score": 1200, "gpu_score": 3000, "ram_gb": 8})
    resp = svc.recommend(req)
    print("Upgrade advisor response:", resp)
    assert hasattr(resp, "bottleneck")


if __name__ == "__main__":
    test_explanation_mock()
    test_upgrade_advisor_mock()
    print("AI services mock tests passed")
