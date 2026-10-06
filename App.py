"""Motosiklet Seçim Köməkçisi: Streamlit veb interfeysi.

İşə salmaq: ``streamlit run app.py``
Bütün məntiq ``motopicker`` paketindən gəlir; burada yalnız UI var.
"""

from __future__ import annotations

import html
import json
import re
import sys
import urllib.parse
import urllib.request
from dataclasses import replace
from pathlib import Path

# Paket `pip install -e .` olmadan da tapılsın (məs. Streamlit Cloud).
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

import streamlit as st  # noqa: E402

from motopicker.constants import (  # noqa: E402
    CRITERION_LABELS,
    DEFAULT_DATA_PATH,
    DEFAULT_TOP_N,
    MAX_HEIGHT_CM,
    MAX_SCORE,
    MIN_HEIGHT_CM,
)
from motopicker.data import DataValidationError, load_motorcycles  # noqa: E402
from motopicker.enums import Experience, LicenseClass, Purpose  # noqa: E402
from motopicker.models import Recommendation, UserProfile  # noqa: E402
from motopicker.recommender import recommend  # noqa: E402

PURPOSE_LABELS = {
    Purpose.CITY: "Şəhər",
    Purpose.TOURING: "Səyahət (touring)",
    Purpose.OFFROAD: "Yolsuzluq (offroad)",
    Purpose.SPORT: "İdman (sport)",
}
EXPERIENCE_LABELS = {
    Experience.BEGINNER: "Yeni başlayan",
    Experience.INTERMEDIATE: "Orta səviyyə",
    Experience.EXPERT: "Təcrübəli",
}
LICENSE_LABELS = {
    LicenseClass.A1: "A1 (maks. 11 kW)",
    LicenseClass.A2: "A2 (maks. 35 kW)",
    LicenseClass.A: "A (limitsiz)",
}
BUDGET_MIN, BUDGET_MAX, BUDGET_STEP, BUDGET_DEFAULT = 1000, 50000, 500, 9000
HEIGHT_DEFAULT = 175
MAX_TOP_N = 10
SCORE_PERCENT = 100

# --- Şəkillər (Wikimedia Commons) -------------------------------------------
COMMONS_API = "https://commons.wikimedia.org/w/api.php"
USER_AGENT = "motopicker-student-project/1.0 (educational)"
HTTP_TIMEOUT_S = 8
SEARCH_LIMIT = 20
THUMB_WIDTH_PX = 640
MIN_IMAGES = 2
MAX_IMAGES = 3
IMAGE_MIMES = ("image/jpeg", "image/png")
CACHE_TTL_S = 24 * 3600


def matches_query(rec: Recommendation, query: str) -> bool:
    """Brend və ya model axtarış sözünü ehtiva edirsə (böyük/kiçik hərf fərqsiz)."""
    return query.strip().lower() in rec.motorcycle.name.lower()


def _normalize(text: str) -> str:
    """Müqayisə üçün yalnız hərf-rəqəm: 'MT-07' -> 'mt07'."""
    return re.sub(r"[^a-z0-9]", "", text.lower())


def placeholder_svg(label: str) -> str:
    """Şəkil tapılmayanda göstərilən sadə SVG (həmişə ən azı MIN_IMAGES şəkil yeri olsun)."""
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 400">'
        '<rect width="640" height="400" fill="#e5e7eb"/>'
        '<text x="320" y="190" font-size="40" text-anchor="middle" fill="#6b7280">🏍️</text>'
        f'<text x="320" y="250" font-size="26" text-anchor="middle" fill="#6b7280">'
        f"{html.escape(label)}</text></svg>"
    )


@st.cache_data(ttl=CACHE_TTL_S, show_spinner=False)
def fetch_images(brand: str, model: str) -> list[str]:
    """Wikimedia Commons-dan motosikletin şəkillərini tapır (əvvəlcə dəqiq uyğunluqlar).

    Şəbəkə səhvi olarsa boş siyahı qaytarır; çağıran tərəf placeholder göstərir.
    """
    params = {
        "action": "query", "format": "json", "generator": "search",
        "gsrsearch": f"{brand} {model}", "gsrnamespace": 6, "gsrlimit": SEARCH_LIMIT,
        "prop": "imageinfo", "iiprop": "url|mime", "iiurlwidth": THUMB_WIDTH_PX,
    }
    request = urllib.request.Request(
        f"{COMMONS_API}?{urllib.parse.urlencode(params)}", headers={"User-Agent": USER_AGENT}
    )
    try:
        with urllib.request.urlopen(request, timeout=HTTP_TIMEOUT_S) as response:
            pages = json.load(response).get("query", {}).get("pages", {})
    except (OSError, ValueError):
        return []

    hits = sorted(pages.values(), key=lambda page: page.get("index", 0))
    model_key, brand_key = _normalize(model), _normalize(brand)
    exact, loose = [], []
    for page in hits:
        info = (page.get("imageinfo") or [{}])[0]
        url = info.get("thumburl") or info.get("url")
        if not url or info.get("mime") not in IMAGE_MIMES:
            continue
        title = _normalize(page.get("title", ""))
        if model_key in title:
            exact.append(url)
        elif brand_key in title:
            loose.append(url)
    return (exact + loose)[:MAX_IMAGES]


def render_images(brand: str, model: str) -> None:
    """Ən azı MIN_IMAGES şəkil göstərir; çatmayanı placeholder ilə doldurur."""
    urls = fetch_images(brand, model)
    urls = urls + [placeholder_svg(f"{brand} {model}")] * max(0, MIN_IMAGES - len(urls))
    for column, url in zip(st.columns(len(urls)), urls, strict=True):
        column.image(url, use_container_width=True)


@st.cache_data
def get_motorcycles():
    """CSV bir dəfə oxunur və keşlənir."""
    return load_motorcycles(DEFAULT_DATA_PATH)


def render_card(rec: Recommendation) -> None:
    """Bir tövsiyəni kart şəklində göstərir."""
    bike = rec.motorcycle
    with st.container(border=True):
        st.subheader(f"{rec.rank}. {bike.name}")
        render_images(bike.brand, bike.model)
        st.progress(
            min(rec.score / MAX_SCORE, 1.0), text=f"Xal: {rec.score:.1f} / {MAX_SCORE:g}"
        )
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Qiymət", f"${bike.price_usd:,.0f}")
        c2.metric("Güc", f"{bike.power_kw:g} kW")
        c3.metric("Çəki", f"{bike.weight_kg:g} kg")
        c4.metric("Oturacaq", f"{bike.seat_height_mm:g} mm")
        st.caption(
            f"Kateqoriya: {PURPOSE_LABELS[bike.category]} · Vəsiqə: {bike.license_class} · "
            f"Sərf: {bike.fuel_l_per_100km:g} L/100km"
        )
        st.write(rec.explanation)


def render_breakdown(profile: UserProfile, recs: list[Recommendation]) -> None:
    """Hər meyarın xala töhfəsini cədvəldə göstərir (şəffaflıq üçün)."""
    from motopicker.scoring import effective_weights

    weights = effective_weights(profile.purpose, profile.experience)
    rows = [
        {"Meyar": CRITERION_LABELS[c], "Çəki (%)": round(w * SCORE_PERCENT, 1)}
        for c, w in weights.items()
    ]
    st.caption("Profilinizə görə tətbiq olunan meyar çəkiləri:")
    st.dataframe(rows, hide_index=True, use_container_width=True)


def main() -> None:
    st.set_page_config(page_title="Motosiklet Seçim Köməkçisi", page_icon="🏍️", layout="wide")
    st.title("🏍️ Motosiklet Seçim Köməkçisi")
    st.write("Profilinizi daxil edin, sizə uyğun motosikletləri izahatla tövsiyə edək.")

    try:
        motorcycles = get_motorcycles()
    except (OSError, DataValidationError) as exc:
        st.error(f"Data yüklənmədi: {exc}")
        st.stop()

    with st.sidebar:
        st.header("Profiliniz")
        with st.form("profile"):
            budget = st.slider(
                "Büdcə (USD)", BUDGET_MIN, BUDGET_MAX, BUDGET_DEFAULT, step=BUDGET_STEP
            )
            purpose = st.selectbox(
                "İstifadə məqsədi", list(Purpose), format_func=PURPOSE_LABELS.get
            )
            experience = st.selectbox(
                "Təcrübə", list(Experience), format_func=EXPERIENCE_LABELS.get
            )
            height = st.number_input(
                "Boy (sm)",
                min_value=int(MIN_HEIGHT_CM),
                max_value=int(MAX_HEIGHT_CM),
                value=HEIGHT_DEFAULT,
            )
            license_class = st.selectbox(
                "Vəsiqə kateqoriyası", list(LicenseClass), format_func=LICENSE_LABELS.get
            )
            query = st.text_input("Axtarış (brend və ya model)", placeholder="məs. Honda, MT-03")
            top_n = st.slider("Neçə nəticə?", 1, MAX_TOP_N, DEFAULT_TOP_N)
            submitted = st.form_submit_button("Tövsiyə al", type="primary")

    if not submitted:
        st.info("Soldakı formanı doldurub **Tövsiyə al** düyməsini basın.")
        st.caption(f"Bazada {len(motorcycles)} motosiklet modeli var.")
        return

    try:
        profile = UserProfile(
            budget_usd=float(budget),
            purpose=purpose,
            experience=experience,
            height_cm=float(height),
            license_class=license_class,
        )
        # Əvvəlcə bütün uyğun nəticələr, sonra axtarış, sonra top-N (sıra yenidən nömrələnir).
        all_recs = recommend(profile, motorcycles, top_n=len(motorcycles))
        found = [r for r in all_recs if matches_query(r, query)][:top_n]
        recs = [replace(r, rank=i) for i, r in enumerate(found, start=1)]
    except ValueError as exc:
        st.error(f"Xəta: {exc}")
        return

    if not recs and query.strip() and all_recs:
        st.warning(f"'{query}' üzrə nəticə yoxdur. Axtarış sözünü dəyişin və ya boş buraxın.")
        return
    if not recs:
        st.warning(
            "Bu profilə uyğun motosiklet tapılmadı. Büdcəni artırmağı və ya "
            "vəsiqə kateqoriyasını yoxlamağı sınayın."
        )
        return

    st.success(f"{len(recs)} tövsiyə tapıldı.")
    for rec in recs:
        render_card(rec)
    st.caption("Şəkillər: Wikimedia Commons (müəlliflər və lisenziyalar üçün mənbə səhifəsinə baxın).")
    with st.expander("Xal necə hesablanıb?"):
        render_breakdown(profile, recs)


main()