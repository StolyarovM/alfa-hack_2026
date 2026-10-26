
from app.services.recommendation_service import recommend
def test_recommendation_by_goal():
    assert recommend("оборудование") == "Инвестиционный"
    assert recommend("оборот") == "Оборотный"
