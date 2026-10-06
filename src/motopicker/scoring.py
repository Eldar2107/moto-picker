"""Min-max normallaşdırma və çəkili xal hesablanması."""

from __future__ import annotations

from collections.abc import Sequence

from .constants import (
    BASE_WEIGHTS,
    EXPERIENCE_MULTIPLIERS,
    HIGHER_IS_BETTER,
    MAX_SCORE,
    NUMERIC_ATTRIBUTE,
)
from .enums import Criterion, Experience, Purpose
from .models import Motorcycle, ScoredMotorcycle, UserProfile


def min_max_normalize(
    value: float, lo: float, hi: float, higher_is_better: bool = True
) -> float:
    """Dəyəri [0, 1] aralığına gətirir.

    Bütün dəyərlər eynidirsə (``hi == lo``) fərq yoxdur, ona görə 1.0 qaytarılır.
    ``higher_is_better=False`` olduqda kiçik dəyər 1.0 alır.
    """
    if hi < lo:
        raise ValueError(f"Aralıq yanlışdır: lo={lo} > hi={hi}")
    if hi == lo:
        return 1.0
    ratio = (value - lo) / (hi - lo)
    return ratio if higher_is_better else 1.0 - ratio


def effective_weights(purpose: Purpose, experience: Experience) -> dict[Criterion, float]:
    """Məqsəd + təcrübəyə görə yekun çəkilər (cəmi 1.0)."""
    base = BASE_WEIGHTS[purpose]
    multipliers = EXPERIENCE_MULTIPLIERS[experience]
    raw = {c: base[c] * multipliers.get(c, 1.0) for c in Criterion}
    total = sum(raw.values())
    return {c: value / total for c, value in raw.items()}


def score_motorcycles(
    candidates: Sequence[Motorcycle], profile: UserProfile
) -> list[ScoredMotorcycle]:
    """Namizədləri xallandırır (0-100). Boş siyahı üçün boş siyahı qaytarır."""
    if not candidates:
        return []

    weights = effective_weights(profile.purpose, profile.experience)
    ranges: dict[Criterion, tuple[float, float]] = {}
    for criterion, attr in NUMERIC_ATTRIBUTE.items():
        values = [getattr(b, attr) for b in candidates]
        ranges[criterion] = (min(values), max(values))

    scored: list[ScoredMotorcycle] = []
    for bike in candidates:
        contributions: dict[Criterion, float] = {}
        for criterion in Criterion:
            if criterion is Criterion.CATEGORY:
                normalized = 1.0 if bike.category == profile.purpose else 0.0
            else:
                lo, hi = ranges[criterion]
                normalized = min_max_normalize(
                    getattr(bike, NUMERIC_ATTRIBUTE[criterion]),
                    lo,
                    hi,
                    HIGHER_IS_BETTER[criterion],
                )
            contributions[criterion] = weights[criterion] * normalized
        scored.append(
            ScoredMotorcycle(
                motorcycle=bike,
                score=sum(contributions.values()) * MAX_SCORE,
                contributions=contributions,
            )
        )
    return scored
