# AI ilə vibe-coding: istifadə olunan promptlar

Alət: Claude (Anthropic). Bütün layihə aşağıdakı bir əsas promptla generasiya edilib, sonra testlər işə salınıb.

## Prompt 1 (əsas)

```
Python 3.11 ilə "Motosiklet Seçim Köməkçisi" adlı kiçik, lakin production-keyfiyyətli layihə yarat.

MƏQSƏD: İstifadəçi profilinə (büdcə USD, istifadə məqsədi: city/touring/offroad/sport, təcrübə: beginner/intermediate/expert, boy sm, vəsiqə kateqoriyası A1/A2/A) görə data/motorcycles.csv-dən ən uyğun top-N motosikleti izahatla qaytar.

ARXİTEKTURA: src/motopicker/ paketi: models.py (dataclass-lar, type hints), data.py (CSV yükləmə və validasiya, səhv sətirlər üçün aydın exception), filters.py (sərt filtrlər: büdcə, vəsiqə-güc uyğunluğu: A1 ≤ 11kW, A2 ≤ 35kW; oturacaq hündürlüyü boyla uyğunluq), scoring.py (min-max normallaşdırma, istifadə məqsədinə görə çəkili xal), recommender.py (nəticə + hər tövsiyə üçün 'niyə bu model?' izahatı), cli.py (argparse).

DATA: 20 real motosiklet modeli (brand, model, price_usd, power_kw, weight_kg, seat_height_mm, fuel_l_per_100km, category, license_class).

TESTLƏR (pytest): hər modul üçün unit test; edge case-lər (boş nəticə, sərhəd dəyərləri, səhv CSV, bərabər xallar); parametrize istifadə et; ≥90% coverage (pytest-cov).

DİGƏR: README.md (quraşdırma, istifadə nümunələri, alqoritmin izahı), requirements.txt, .gitignore, GitHub Actions workflow (pytest + coverage), docstring-lər, kodda sehrli rəqəm olmasın (konstantlara çıxar).

Əvvəlcə qısa plan göstər, sonra faylları ardıcıl yarat, sonda testləri işə sal və nəticəni göstər.
```

## Nəticə

- 130 test keçdi, coverage 100%.
- Prompt-dan sonra əlavə düzəliş promptları olarsa, bura əlavə et.
