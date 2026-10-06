"""Filtr + xal + izahat = son tövsiyə."""

from __future__ import annotations

from collections.abc import Sequence

from .constants import (
    CRITERION_LABELS,
    DEFAULT_TOP_N,
    EXPLANATION_TOP_CRITERIA,
    FLOAT_PRECISION,
    MAX_SCORE,
)
from .enums import Criterion
from .filters import apply_hard_filters, max_seat_height_mm
from .models import Motorcycle, Recommendation, ScoredMotorcycle, UserProfile
from .scoring import score_motorcycles


def build_explanation(scored: ScoredMotorcycle, profile: UserProfile) -> str:
    """"Niyə bu model?" izahatı."""
    bike = scored.motorcycle
    # Kateqoriya uyğunluğu ayrıca cümlə ilə deyilir; burada yalnız digər meyarlar.
    ranked = sorted(
        (c for c in scored.contributions if c is not Criterion.CATEGORY),
        key=lambda c: scored.contributions[c],
        reverse=True,
    )
    strengths = ", ".join(CRITERION_LABELS[c] for c in ranked[:EXPLANATION_TOP_CRITERIA])

    parts = [f"Ümumi xal {scored.score:.1f}/{MAX_SCORE:g}."]
    if bike.category == profile.purpose:
        parts.append(f"Kateqoriyası ({bike.category}) seçdiyiniz məqsədə uyğundur.")
    else:
        parts.append(
            f"Kateqoriyası ({bike.category}) məqsədinizdən ({profile.purpose}) fərqlidir, "
            "digər meyarlara görə siyahıdadır."
        )
    parts.append(f"Ən güclü cəhətləri: {strengths}.")
    savings = profile.budget_usd - bike.price_usd
    parts.append(f"Qiyməti büdcədən {savings:,.0f} USD aşağıdır.")
    parts.append(
        f"Oturacaq hündürlüyü ({bike.seat_height_mm:.0f} mm) boyunuz üçün "
        f"maksimum {max_seat_height_mm(profile):.0f} mm həddindən aşağıdır."
    )
    return " ".join(parts)


def _sort_key(item: ScoredMotorcycle) -> tuple[float, float, str, str]:
    """Xal azalan; bərabərlikdə ucuz olan, sonra əlifba sırası (deterministik)."""
    bike = item.motorcycle
    return (-round(item.score, FLOAT_PRECISION), bike.price_usd, bike.brand, bike.model)


def recommend(
    profile: UserProfile,
    motorcycles: Sequence[Motorcycle],
    top_n: int = DEFAULT_TOP_N,
) -> list[Recommendation]:
    """Profilə ən uyğun ``top_n`` motosikleti izahatla qaytarır.

    Heç bir motosiklet filtrləri keçməzsə boş siyahı qaytarılır.
    """
    if top_n < 1:
        raise ValueError(f"top_n ən azı 1 olmalıdır: {top_n}")
    candidates = apply_hard_filters(motorcycles, profile)
    scored = sorted(score_motorcycles(candidates, profile), key=_sort_key)
    return [
        Recommendation(
            rank=rank,
            motorcycle=item.motorcycle,
            score=item.score,
            explanation=build_explanation(item, profile),
        )
        for rank, item in enumerate(scored[:top_n], start=1)
    ]
