import math

import pytest

from conftest import make_bike, make_profile
from motopicker.enums import LicenseClass


def test_motorcycle_name():
    assert make_bike(brand="Honda", model="CB125R").name == "Honda CB125R"


def test_motorcycle_is_immutable():
    bike = make_bike()
    with pytest.raises(AttributeError):
        bike.price_usd = 1  # type: ignore[misc]


@pytest.mark.parametrize("budget", [0, -1, -5000.0, math.inf, math.nan])
def test_invalid_budget_rejected(budget):
    with pytest.raises(ValueError, match="Büdcə"):
        make_profile(budget_usd=budget)


@pytest.mark.parametrize("height", [119.9, 0, -170, 230.1, 300])
def test_invalid_height_rejected(height):
    with pytest.raises(ValueError, match="Boy"):
        make_profile(height_cm=height)


@pytest.mark.parametrize("height", [120.0, 175.0, 230.0])
def test_height_boundaries_accepted(height):
    assert make_profile(height_cm=height).height_cm == height


def test_license_enum_values():
    assert [c.value for c in LicenseClass] == ["A1", "A2", "A"]
