from app.services.recommendation_service import RecommendationService


def test_recommend_for_user_fallback():
    svc = RecommendationService()
    resp = svc.recommend_for_user(None, limit=3)
    assert resp is not None
    assert len(resp.recommendations) == 3
    for item in resp.recommendations:
        assert item.compatibility >= 0


if __name__ == '__main__':
    test_recommend_for_user_fallback()
    print('recommendation service fallback test passed')
