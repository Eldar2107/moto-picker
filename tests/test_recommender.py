import pytest

from conftest import make_bike, make_profile
from motopicker.constants import DEFAULT_DATA_PATH, DEFAULT_TOP_N
from motopicker.data import load_motorcycles
from motopicker.enums import Experience, LicenseClass, Purpose
from motopicker.recommender import build_explanation, recommend
from motopicker.scoring import score_motorcycles


@pytest.fixture(scope="module")
def real_bikes():
    return load_motorcycles(DEFAULT_DATA_PATH)


def test_returns_ranked_results(bikes, profile):
    recs = recommend(profile, bikes)
    assert [r.rank for r in recs] == [1, 2, 3]
    scores = [r.score for r in recs]
    assert scores == sorted(scores, reverse=True)


@pytest.mark.parametrize("top_n", [1, 2, 3, 10])
def test_top_n_limits_results(bikes, profile, top_n):
    assert len(recommend(profile, bikes, top_n=top_n)) == min(top_n, len(bikes))


@pytest.mark.parametrize("top_n", [0, -1])
def test_invalid_top_n(bikes, profile, top_n):
    with pytest.raises(ValueError, match="top_n"):
        recommend(profile, bikes, top_n=top_n)


def test_default_top_n(real_bikes):
    assert len(recommend(make_profile(budget_usd=50000), real_bikes)) == DEFAULT_TOP_N


def test_empty_result_when_nothing_matches(bikes):
    assert recommend(make_profile(budget_usd=100), bikes) == []


def test_empty_input(profile):
    assert recommend(profile, []) == []


def test_ties_broken_by_price_then_name():
    a = make_bike(brand="Zed", model="A", price_usd=5000)
    b = make_bike(brand="Alpha", model="B", price_usd=5000)
    recs = recommend(make_profile(), [a, b])
    assert recs[0].score == recs[1].score
    assert [r.motorcycle.brand for r in recs] == ["Alpha", "Zed"]


def test_tie_prefers_cheaper_bike():
    # Eyni xal üçün qiymət fərqi olmamalıdır: yalnız price fərqli olanda xal fərqli olur,
    # ona görə ucuz motosiklet birinci gəlməlidir.
    cheap = make_bike(model="Cheap", price_usd=4000)
    pricey = make_bike(model="Pricey", price_usd=6000)
    assert recommend(make_profile(), [pricey, cheap])[0].motorcycle.model == "Cheap"


def test_input_order_does_not_change_output(bikes, profile):
    forward = [r.motorcycle.model for r in recommend(profile, bikes)]
    backward = [r.motorcycle.model for r in recommend(profile, list(reversed(bikes)))]
    assert forward == backward


def test_every_recommendation_has_explanation(bikes, profile):
    for rec in recommend(profile, bikes):
        assert rec.explanation
        assert "xal" in rec.explanation


def test_explanation_mentions_matching_category(profile):
    bike = make_bike(category=Purpose.CITY)
    scored = score_motorcycles([bike], profile)[0]
    assert "məqsədə uyğundur" in build_explanation(scored, profile)


def test_explanation_mentions_mismatching_category(profile):
    bike = make_bike(category=Purpose.SPORT)
    scored = score_motorcycles([bike], profile)[0]
    assert "fərqlidir" in build_explanation(scored, profile)


def test_explanation_reports_savings():
    profile = make_profile(budget_usd=10000)
    scored = score_motorcycles([make_bike(price_usd=7500)], profile)[0]
    assert "2,500 USD" in build_explanation(scored, profile)


# --- Real data ilə inteqrasiya testləri -------------------------------------
def test_a1_rider_only_gets_a1_bike(real_bikes):
    recs = recommend(
        make_profile(license_class=LicenseClass.A1, budget_usd=20000), real_bikes, top_n=10
    )
    assert [r.motorcycle.model for r in recs] == ["CB125R"]


def test_a2_rider_never_gets_over_35kw(real_bikes):
    profile = make_profile(license_class=LicenseClass.A2, budget_usd=50000)
    recs = recommend(profile, real_bikes, top_n=20)
    assert recs and all(r.motorcycle.power_kw <= 35 for r in recs)


def test_budget_is_respected_on_real_data(real_bikes):
    recs = recommend(make_profile(budget_usd=6000), real_bikes, top_n=20)
    assert recs and all(r.motorcycle.price_usd <= 6000 for r in recs)


@pytest.mark.parametrize("purpose", list(Purpose))
def test_top_pick_matches_purpose_for_rich_expert(real_bikes, purpose):
    profile = make_profile(purpose=purpose, experience=Experience.EXPERT, budget_usd=50000)
    assert recommend(profile, real_bikes)[0].motorcycle.category is purpose


def test_short_rider_does_not_get_tall_offroad_bike(real_bikes):
    profile = make_profile(
        purpose=Purpose.OFFROAD, height_cm=160, license_class=LicenseClass.A2, budget_usd=10000
    )
    recs = recommend(profile, real_bikes, top_n=20)
    assert all(r.motorcycle.seat_height_mm <= 832 for r in recs)
    assert "CRF300L" not in [r.motorcycle.model for r in recs]


def test_no_results_for_tiny_budget_on_real_data(real_bikes):
    assert recommend(make_profile(budget_usd=1000), real_bikes) == []
