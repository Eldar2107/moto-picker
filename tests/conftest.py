"""Ortaq fixture-lər."""

from __future__ import annotations

import pytest

from motopicker.enums import Experience, LicenseClass, Purpose
from motopicker.models import Motorcycle, UserProfile


def make_bike(**overrides) -> Motorcycle:
    """Test üçün standart motosiklet; istənilən sahə dəyişdirilə bilər."""
    defaults = dict(
        brand="Test",
        model="Base",
        price_usd=5000.0,
        power_kw=30.0,
        weight_kg=180.0,
        seat_height_mm=800.0,
        fuel_l_per_100km=4.0,
        category=Purpose.CITY,
        license_class=LicenseClass.A2,
    )
    defaults.update(overrides)
    return Motorcycle(**defaults)


def make_profile(**overrides) -> UserProfile:
    """Test üçün standart profil."""
    defaults = dict(
        budget_usd=10000.0,
        purpose=Purpose.CITY,
        experience=Experience.INTERMEDIATE,
        height_cm=175.0,
        license_class=LicenseClass.A,
    )
    defaults.update(overrides)
    return UserProfile(**defaults)


@pytest.fixture
def profile() -> UserProfile:
    return make_profile()


@pytest.fixture
def bikes() -> list[Motorcycle]:
    return [
        make_bike(model="Cheap", price_usd=4000, power_kw=10, weight_kg=130, fuel_l_per_100km=2.0),
        make_bike(model="Mid", price_usd=7000, power_kw=40, weight_kg=190, fuel_l_per_100km=4.5,
                  license_class=LicenseClass.A),
        make_bike(model="Sporty", price_usd=9000, power_kw=90, weight_kg=200, fuel_l_per_100km=6.0,
                  category=Purpose.SPORT, license_class=LicenseClass.A),
    ]
