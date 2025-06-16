def test_get_total_views(stats_service, test_db):
    test_db.add(View(promo_id=1))
    test_db.add(View(promo_id=1))
    test_db.commit()
    request = TotalViewsRequest(promo_id=1)
    response = stats_service.GetTotalViews(request, None)
    assert response.count == 2

def test_get_click_stats(stats_service, test_db):
    request = ClickStatsRequest(date="2025-06-01")
    response = stats_service.GetClickStats(request, None)
    assert isinstance(response.count, int)

def test_get_user_stats(stats_service, test_db):
    test_db.add(View(promo_id=1, user_id=123))
    test_db.commit()
    request = UserStatsRequest(user_id=123)
    response = stats_service.GetUserStats(request, None)
    assert response.total_views >= 1
