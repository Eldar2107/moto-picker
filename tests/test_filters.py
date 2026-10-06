import pytest

from conftest import make_bike, make_profile
from motopicker.enums import LicenseClass
from motopicker.filters import (
    apply_hard_filters,
    license_allows,
    max_seat_height_mm,
    seat_height_fits,
    within_budget,
)


@pytest.mark.parametrize(
    ("price", "expected"),
    [(9999.99, True), (10000, True), (10000.01, False), (1, True), (50000, False)],
)
def test_budget_boundary(price, expected):
    assert within_budget(make_bike(price_usd=price), make_profile(budget_usd=10000)) is expected


@pytest.mark.parametrize(
    ("user", "power", "bike_class", "expected"),
    [
        (LicenseClass.A1, 11.0, LicenseClass.A1, True),    # sərhəd: tam 11 kW
        (LicenseClass.A1, 11.1, LicenseClass.A1, False),
        (LicenseClass.A1, 10.0, LicenseClass.A2, False),   # A2 motosiklet A1 ilə olmaz
        (LicenseClass.A2, 35.0, LicenseClass.A2, True),    # sərhəd: tam 35 kW
        (LicenseClass.A2, 35.1, LicenseClass.A2, False),
        (LicenseClass.A2, 11.0, LicenseClass.A1, True),    # aşağı kateqoriya sürülə bilər
        (LicenseClass.A2, 20.0, LicenseClass.A, False),    # A tələb edən motosiklet
        (LicenseClass.A, 150.0, LicenseClass.A, True),     # A-da güc limiti yoxdur
        (LicenseClass.A, 5.0, LicenseClass.A1, True),
    ],
)
def test_license_rules(user, power, bike_class, expected):
    bike = make_bike(power_kw=power, license_class=bike_class)
    assert license_allows(bike, make_profile(license_class=user)) is expected


def test_max_seat_height_formula():
    assert max_seat_height_mm(make_profile(height_cm=175)) == 910.0
    assert max_seat_height_mm(make_profile(height_cm=160)) == 832.0


@pytest.mark.parametrize(
    ("seat", "expected"),
    [(909, True), (910, True), (910.5, False), (1000, False), (600, True)],
)
def test_seat_height_boundary(seat, expected):
    assert seat_height_fits(make_bike(seat_height_mm=seat), make_profile(height_cm=175)) is expected


def test_short_rider_excludes_tall_bikes():
    tall = make_bike(seat_height_mm=880)
    assert not seat_height_fits(tall, make_profile(height_cm=160))
    assert seat_height_fits(tall, make_profile(height_cm=175))


def test_apply_hard_filters_combines_all(bikes):
    profile = make_profile(budget_usd=8000, license_class=LicenseClass.A2)
    result = apply_hard_filters(bikes, profile)
    assert [b.model for b in result] == ["Cheap"]  # Mid A lazımdır, Sporty büdcədən baha


def test_apply_hard_filters_keeps_order(bikes):
    result = apply_hard_filters(bikes, make_profile())
    assert [b.model for b in result] == ["Cheap", "Mid", "Sporty"]


def test_apply_hard_filters_empty_result(bikes):
    assert apply_hard_filters(bikes, make_profile(budget_usd=1)) == []


def test_apply_hard_filters_empty_input(profile):
    assert apply_hard_filters([], profile) == []
