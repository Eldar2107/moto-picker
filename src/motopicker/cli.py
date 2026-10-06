"""Komanda sətri interfeysi."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from .constants import DEFAULT_DATA_PATH, DEFAULT_TOP_N
from .data import load_motorcycles
from .enums import Experience, LicenseClass, Purpose
from .models import Recommendation, UserProfile
from .recommender import recommend

EXIT_OK = 0
EXIT_NO_RESULTS = 1
EXIT_ERROR = 2


def build_parser() -> argparse.ArgumentParser:
    """argparse parser-i."""
    parser = argparse.ArgumentParser(
        prog="motopicker", description="Profilinizə uyğun motosiklet tövsiyə edir."
    )
    parser.add_argument("--budget", type=float, required=True, help="Büdcə (USD)")
    parser.add_argument("--purpose", choices=[p.value for p in Purpose], required=True)
    parser.add_argument("--experience", choices=[e.value for e in Experience], required=True)
    parser.add_argument("--height", type=float, required=True, help="Boy (sm)")
    parser.add_argument("--license", dest="license_class",
                        choices=[c.value for c in LicenseClass], required=True)
    parser.add_argument("--top", type=int, default=DEFAULT_TOP_N, help="Neçə nəticə göstərilsin")
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA_PATH, help="CSV faylının yolu")
    return parser


def format_recommendations(recommendations: Sequence[Recommendation]) -> str:
    """Tövsiyələri oxunaqlı mətnə çevirir."""
    lines: list[str] = []
    for rec in recommendations:
        bike = rec.motorcycle
        lines.append(
            f"{rec.rank}. {bike.name}  |  {rec.score:.1f} xal  |  "
            f"${bike.price_usd:,.0f}  |  {bike.power_kw:g} kW"
        )
        lines.append(f"   {rec.explanation}")
    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> int:
    """Giriş nöqtəsi. Çıxış kodu: 0 uğur, 1 nəticə yoxdur, 2 xəta."""
    args = build_parser().parse_args(argv)
    try:
        profile = UserProfile(
            budget_usd=args.budget,
            purpose=Purpose(args.purpose),
            experience=Experience(args.experience),
            height_cm=args.height,
            license_class=LicenseClass(args.license_class),
        )
        motorcycles = load_motorcycles(args.data)
        recommendations = recommend(profile, motorcycles, top_n=args.top)
    except (ValueError, OSError) as exc:
        print(f"Xəta: {exc}", file=sys.stderr)
        return EXIT_ERROR

    if not recommendations:
        print("Bu profilə uyğun motosiklet tapılmadı. Büdcəni artırmağı sınayın.")
        return EXIT_NO_RESULTS
    print(format_recommendations(recommendations))
    return EXIT_OK
