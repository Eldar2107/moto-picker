"""Bütün sabitlər bir yerdə: kodda "sehrli rəqəm" qalmasın."""

from __future__ import annotations

import math
from pathlib import Path

from .enums import Criterion, Experience, LicenseClass, Purpose

# --- Vəsiqə qaydaları -------------------------------------------------------
LICENSE_MAX_POWER_KW: dict[LicenseClass, float] = {
    LicenseClass.A1: 11.0,
    LicenseClass.A2: 35.0,
    LicenseClass.A: math.inf,
}
LICENSE_RANK: dict[LicenseClass, int] = {
    LicenseClass.A1: 1,
    LicenseClass.A2: 2,
    LicenseClass.A: 3,
}

# --- Boy / oturacaq uyğunluğu -----------------------------------------------
# Oturacaq hündürlüyü (mm) <= boy (sm) * 10 * SEAT_HEIGHT_RATIO olmalıdır.
SEAT_HEIGHT_RATIO = 0.52
MM_PER_CM = 10
FLOAT_PRECISION = 6
MIN_HEIGHT_CM = 120.0
MAX_HEIGHT_CM = 230.0

# --- Tövsiyə ----------------------------------------------------------------
DEFAULT_TOP_N = 5
MAX_SCORE = 100.0
EXPLANATION_TOP_CRITERIA = 2

# --- Data -------------------------------------------------------------------
DEFAULT_DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "motorcycles.csv"
CSV_COLUMNS = (
    "brand",
    "model",
    "price_usd",
    "power_kw",
    "weight_kg",
    "seat_height_mm",
    "fuel_l_per_100km",
    "category",
    "license_class",
)

# --- Xallandırma ------------------------------------------------------------
# True: böyük dəyər yaxşıdır. False: kiçik dəyər yaxşıdır.
HIGHER_IS_BETTER: dict[Criterion, bool] = {
    Criterion.PRICE: False,
    Criterion.POWER: True,
    Criterion.WEIGHT: False,
    Criterion.SEAT_HEIGHT: False,
    Criterion.FUEL: False,
    Criterion.CATEGORY: True,
}

# Meyar -> Motorcycle atributu (CATEGORY ədədi deyil, ayrıca işlənir).
NUMERIC_ATTRIBUTE: dict[Criterion, str] = {
    Criterion.PRICE: "price_usd",
    Criterion.POWER: "power_kw",
    Criterion.WEIGHT: "weight_kg",
    Criterion.SEAT_HEIGHT: "seat_height_mm",
    Criterion.FUEL: "fuel_l_per_100km",
}

# İstifadə məqsədinə görə baza çəkilər (hər sətirdə cəm = 1.0).
BASE_WEIGHTS: dict[Purpose, dict[Criterion, float]] = {
    Purpose.CITY: {
        Criterion.PRICE: 0.20,
        Criterion.POWER: 0.05,
        Criterion.WEIGHT: 0.20,
        Criterion.SEAT_HEIGHT: 0.15,
        Criterion.FUEL: 0.20,
        Criterion.CATEGORY: 0.20,
    },
    Purpose.TOURING: {
        Criterion.PRICE: 0.10,
        Criterion.POWER: 0.20,
        Criterion.WEIGHT: 0.05,
        Criterion.SEAT_HEIGHT: 0.10,
        Criterion.FUEL: 0.15,
        Criterion.CATEGORY: 0.40,
    },
    Purpose.OFFROAD: {
        Criterion.PRICE: 0.10,
        Criterion.POWER: 0.15,
        Criterion.WEIGHT: 0.25,
        Criterion.SEAT_HEIGHT: 0.05,
        Criterion.FUEL: 0.05,
        Criterion.CATEGORY: 0.40,
    },
    Purpose.SPORT: {
        Criterion.PRICE: 0.10,
        Criterion.POWER: 0.35,
        Criterion.WEIGHT: 0.15,
        Criterion.SEAT_HEIGHT: 0.05,
        Criterion.FUEL: 0.00,
        Criterion.CATEGORY: 0.35,
    },
}

# Təcrübəyə görə çəki vuruqları (göstərilməyən meyar = 1.0). Sonda yenidən normallaşdırılır.
EXPERIENCE_MULTIPLIERS: dict[Experience, dict[Criterion, float]] = {
    Experience.BEGINNER: {
        Criterion.POWER: 0.3,
        Criterion.WEIGHT: 1.5,
        Criterion.SEAT_HEIGHT: 1.3,
    },
    Experience.INTERMEDIATE: {},
    Experience.EXPERT: {
        Criterion.POWER: 1.5,
        Criterion.PRICE: 0.8,
    },
}

# İzahatlarda göstərilən meyar adları.
CRITERION_LABELS: dict[Criterion, str] = {
    Criterion.PRICE: "sərfəli qiymət",
    Criterion.POWER: "yüksək güc",
    Criterion.WEIGHT: "aşağı çəki",
    Criterion.SEAT_HEIGHT: "rahat oturacaq hündürlüyü",
    Criterion.FUEL: "aşağı yanacaq sərfi",
    Criterion.CATEGORY: "istifadə məqsədinə uyğunluq",
}
