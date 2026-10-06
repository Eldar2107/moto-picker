import pytest

from conftest import make_bike, make_profile
from motopicker.constants import MAX_SCORE
from motopicker.enums import Criterion, Experience, Purpose
from motopicker.scoring import effective_weights, min_max_normalize, score_motorcycles


@pytest.mark.parametrize(
    ("value", "lo", "hi", "higher", "expected"),
    [
        (5, 0, 10, True, 0.5),
        (0, 0, 10, True, 0.0),
        (10, 0, 10, True, 1.0),
        (0, 0, 10, False, 1.0),
        (10, 0, 10, False, 0.0),
        (2.5, 0, 10, False, 0.75),
        (7, 7, 7, True, 1.0),    # bərabər dəyərlər
        (7, 7, 7, False, 1.0),
    ],
)
def test_min_max_normalize(value, lo, hi, higher, expected):
    assert min_max_normalize(value, lo, hi, higher) == pytest.approx(expected)


def test_min_max_invalid_range():
    with pytest.raises(ValueError, match="Aralıq"):
        min_max_normalize(1, 10, 0)


@pytest.mark.parametrize("purpose", list(Purpose))
@pytest.mark.parametrize("experience", list(Experience))
def test_effective_weights_sum_to_one(purpose, experience):
    weights = effective_weights(purpose, experience)
    assert set(weights) == set(Criterion)
    assert sum(weights.values()) == pytest.approx(1.0)
    assert all(w >= 0 for w in weights.values())


def test_beginner_weights_power_less_than_expert():
    beginner = effective_weights(Purpose.SPORT, Experience.BEGINNER)[Criterion.POWER]
    expert = effective_weights(Purpose.SPORT, Experience.EXPERT)[Criterion.POWER]
    assert beginner < expert


def test_beginner_weights_lightness_more_than_intermediate():
    b = effective_weights(Purpose.CITY, Experience.BEGINNER)[Criterion.WEIGHT]
    i = effective_weights(Purpose.CITY, Experience.INTERMEDIATE)[Criterion.WEIGHT]
    assert b > i


def test_purpose_changes_weights():
    sport = effective_weights(Purpose.SPORT, Experience.INTERMEDIATE)
    city = effective_weights(Purpose.CITY, Experience.INTERMEDIATE)
    assert sport[Criterion.POWER] > city[Criterion.POWER]
    assert sport[Criterion.FUEL] == 0.0


def test_empty_candidates():
    assert score_motorcycles([], make_profile()) == []


def test_single_candidate_gets_full_score_when_category_matches():
    result = score_motorcycles([make_bike(category=Purpose.CITY)], make_profile())
    assert result[0].score == pytest.approx(MAX_SCORE)


def test_single_candidate_wrong_category_loses_category_weight():
    result = score_motorcycles([make_bike(category=Purpose.SPORT)], make_profile())
    weight = effective_weights(Purpose.CITY, Experience.INTERMEDIATE)[Criterion.CATEGORY]
    assert result[0].score == pytest.approx(MAX_SCORE * (1 - weight))


def test_scores_within_bounds(bikes, profile):
    for item in score_motorcycles(bikes, profile):
        assert 0.0 <= item.score <= MAX_SCORE


def test_contributions_sum_matches_score(bikes, profile):
    for item in score_motorcycles(bikes, profile):
        assert sum(item.contributions.values()) * MAX_SCORE == pytest.approx(item.score)


def test_matching_category_scores_higher_all_else_equal():
    city = make_bike(model="City", category=Purpose.CITY)
    sport = make_bike(model="Sport", category=Purpose.SPORT)
    scored = {s.motorcycle.model: s.score for s in score_motorcycles([city, sport], make_profile())}
    assert scored["City"] > scored["Sport"]


def test_cheaper_bike_scores_higher_for_city_all_else_equal():
    cheap = make_bike(model="Cheap", price_usd=4000)
    pricey = make_bike(model="Pricey", price_usd=9000)
    scored = {s.motorcycle.model: s.score for s in score_motorcycles([cheap, pricey], make_profile())}
    assert scored["Cheap"] > scored["Pricey"]


def test_sport_purpose_prefers_powerful_bike():
    weak = make_bike(model="Weak", power_kw=20, category=Purpose.SPORT)
    strong = make_bike(model="Strong", power_kw=100, category=Purpose.SPORT)
    profile = make_profile(purpose=Purpose.SPORT, experience=Experience.EXPERT)
    scored = {s.motorcycle.model: s.score for s in score_motorcycles([weak, strong], profile)}
    assert scored["Strong"] > scored["Weak"]


def test_identical_bikes_get_identical_scores():
    a, b = make_bike(model="A"), make_bike(model="B")
    scores = [s.score for s in score_motorcycles([a, b], make_profile())]
    assert scores[0] == scores[1]
