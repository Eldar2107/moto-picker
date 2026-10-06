"""Layihə boyu istifadə olunan enum-lar."""

from enum import StrEnum


class Purpose(StrEnum):
    """İstifadə məqsədi (eyni zamanda motosikletin kateqoriyası)."""

    CITY = "city"
    TOURING = "touring"
    OFFROAD = "offroad"
    SPORT = "sport"


class Experience(StrEnum):
    """Sürücünün təcrübə səviyyəsi."""

    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    EXPERT = "expert"


class LicenseClass(StrEnum):
    """Sürücülük vəsiqəsi kateqoriyası."""

    A1 = "A1"
    A2 = "A2"
    A = "A"


class Criterion(StrEnum):
    """Xallandırma meyarları."""

    PRICE = "price"
    POWER = "power"
    WEIGHT = "weight"
    SEAT_HEIGHT = "seat_height"
    FUEL = "fuel"
    CATEGORY = "category"
