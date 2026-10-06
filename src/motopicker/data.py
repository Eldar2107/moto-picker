"""CSV-dən motosiklet datasını yükləmə və validasiya."""

from __future__ import annotations

import csv
from pathlib import Path

from .constants import CSV_COLUMNS
from .enums import LicenseClass, Purpose
from .models import Motorcycle

_NUMERIC_FIELDS = (
    "price_usd",
    "power_kw",
    "weight_kg",
    "seat_height_mm",
    "fuel_l_per_100km",
)


class DataValidationError(ValueError):
    """CSV faylı və ya onun sətirləri yanlışdır."""


def parse_row(row: dict[str, str], line_no: int) -> Motorcycle:
    """Bir CSV sətirini ``Motorcycle``-a çevirir; səhv olarsa ``DataValidationError``."""
    numbers: dict[str, float] = {}
    for field in _NUMERIC_FIELDS:
        raw = (row.get(field) or "").strip()
        try:
            value = float(raw)
        except ValueError:
            raise DataValidationError(
                f"Sətir {line_no}: '{field}' ədəd olmalıdır, tapıldı: {raw!r}"
            ) from None
        if value <= 0:
            raise DataValidationError(f"Sətir {line_no}: '{field}' müsbət olmalıdır: {value}")
        numbers[field] = value

    brand = (row.get("brand") or "").strip()
    model = (row.get("model") or "").strip()
    if not brand or not model:
        raise DataValidationError(f"Sətir {line_no}: 'brand' və 'model' boş ola bilməz")

    try:
        category = Purpose((row.get("category") or "").strip().lower())
    except ValueError:
        raise DataValidationError(
            f"Sətir {line_no}: naməlum kateqoriya {row.get('category')!r}"
        ) from None
    try:
        license_class = LicenseClass((row.get("license_class") or "").strip().upper())
    except ValueError:
        raise DataValidationError(
            f"Sətir {line_no}: naməlum vəsiqə kateqoriyası {row.get('license_class')!r}"
        ) from None

    return Motorcycle(
        brand=brand,
        model=model,
        category=category,
        license_class=license_class,
        **numbers,
    )


def load_motorcycles(path: str | Path) -> list[Motorcycle]:
    """CSV faylını oxuyub validasiya edir.

    Raises:
        FileNotFoundError: fayl yoxdursa.
        DataValidationError: başlıq, sətir və ya məzmun yanlışdırsa, yaxud fayl boşdursa.
    """
    with Path(path).open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        missing = [c for c in CSV_COLUMNS if c not in (reader.fieldnames or [])]
        if missing:
            raise DataValidationError(f"CSV-də çatışmayan sütunlar: {', '.join(missing)}")
        # Başlıq 1-ci sətirdir, data 2-dən başlayır.
        motorcycles = [parse_row(row, line_no) for line_no, row in enumerate(reader, start=2)]
    if not motorcycles:
        raise DataValidationError("CSV faylında heç bir motosiklet yoxdur")
    return motorcycles
