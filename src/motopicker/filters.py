"""Sərt filtrlər: bunları keçməyən motosiklet heç xallandırılmır."""

from __future__ import annotations

from collections.abc import Iterable

from .constants import (
    FLOAT_PRECISION,
    LICENSE_MAX_POWER_KW,
    LICENSE_RANK,
    MM_PER_CM,
    SEAT_HEIGHT_RATIO,
)
from .models import Motorcycle, UserProfile


def max_seat_height_mm(profile: UserProfile) -> float:
    """İstifadəçinin boyuna görə icazə verilən maksimum oturacaq hündürlüyü (mm)."""
    return round(profile.height_cm * MM_PER_CM * SEAT_HEIGHT_RATIO, FLOAT_PRECISION)


def within_budget(bike: Motorcycle, profile: UserProfile) -> bool:
    """Qiymət büdcəni aşmır (bərabər olmaq olar)."""
    return bike.price_usd <= profile.budget_usd


def license_allows(bike: Motorcycle, profile: UserProfile) -> bool:
    """Vəsiqə həm motosikletin tələb etdiyi kateqoriyanı, həm də güc limitini ödəyir."""
    rank_ok = LICENSE_RANK[bike.license_class] <= LICENSE_RANK[profile.license_class]
    power_ok = bike.power_kw <= LICENSE_MAX_POWER_KW[profile.license_class]
    return rank_ok and power_ok


def seat_height_fits(bike: Motorcycle, profile: UserProfile) -> bool:
    """Oturacaq hündürlüyü boya uyğundur (bərabər olmaq olar)."""
    return bike.seat_height_mm <= max_seat_height_mm(profile)


def apply_hard_filters(
    motorcycles: Iterable[Motorcycle], profile: UserProfile
) -> list[Motorcycle]:
    """Bütün sərt filtrləri keçən motosikletlərin siyahısı (ardıcıllıq saxlanılır)."""
    return [
        bike
        for bike in motorcycles
        if within_budget(bike, profile)
        and license_allows(bike, profile)
        and seat_height_fits(bike, profile)
    ]
