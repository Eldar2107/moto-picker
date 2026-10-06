"""Domen modelləri (dataclass-lar)."""

from __future__ import annotations

import math
from dataclasses import dataclass

from .constants import MAX_HEIGHT_CM, MIN_HEIGHT_CM
from .enums import Criterion, Experience, LicenseClass, Purpose


@dataclass(frozen=True)
class Motorcycle:
    """Bir motosiklet modeli.

    ``license_class`` bu motosikleti sürmək üçün lazım olan *minimum* kateqoriyadır.
    ``category`` motosikletin əsas təyinatıdır.
    """

    brand: str
    model: str
    price_usd: float
    power_kw: float
    weight_kg: float
    seat_height_mm: float
    fuel_l_per_100km: float
    category: Purpose
    license_class: LicenseClass

    @property
    def name(self) -> str:
        """Brend + model."""
        return f"{self.brand} {self.model}"


@dataclass(frozen=True)
class UserProfile:
    """İstifadəçi profili. Yanlış dəyərlər ``ValueError`` verir."""

    budget_usd: float
    purpose: Purpose
    experience: Experience
    height_cm: float
    license_class: LicenseClass

    def __post_init__(self) -> None:
        if not math.isfinite(self.budget_usd) or self.budget_usd <= 0:
            raise ValueError(f"Büdcə müsbət olmalıdır: {self.budget_usd}")
        if not MIN_HEIGHT_CM <= self.height_cm <= MAX_HEIGHT_CM:
            raise ValueError(
                f"Boy {MIN_HEIGHT_CM:g}-{MAX_HEIGHT_CM:g} sm aralığında olmalıdır: {self.height_cm}"
            )


@dataclass(frozen=True)
class ScoredMotorcycle:
    """Xallandırılmış motosiklet.

    ``contributions`` hər meyarın (çəki * normallaşdırılmış dəyər) töhfəsidir;
    cəmi * MAX_SCORE = ``score``.
    """

    motorcycle: Motorcycle
    score: float
    contributions: dict[Criterion, float]


@dataclass(frozen=True)
class Recommendation:
    """Son tövsiyə: sıra, motosiklet, xal və izahat."""

    rank: int
    motorcycle: Motorcycle
    score: float
    explanation: str
