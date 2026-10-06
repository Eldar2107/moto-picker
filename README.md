# Motosiklet Seçim Köməkçisi (motopicker)

https://moto-picker-uvqurvfr3w68vnjwdxq7n9.streamlit.app/


İstifadəçi profilinə (büdcə, istifadə məqsədi, təcrübə, boy, vəsiqə kateqoriyası) görə
`data/motorcycles.csv`-dəki 20 modeldən ən uyğun motosikletləri **izahatla** tövsiyə edən
kiçik Python layihəsi. Çoxkriteriyalı qərar qəbuletmə (weighted scoring) əsasında işləyir.

> **Qeyd:** `data/motorcycles.csv`-dəki qiymət və texniki göstəricilər təxminidir (tədris məqsədi üçün)
> və rəsmi istehsalçı məlumatı ilə dəqiqləşdirilməlidir.

## Quraşdırma

Python 3.11+ lazımdır.

```bash
git clone https://github.com/ISTIFADECI/moto-picker.git
cd moto-picker
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
```

## İstifadə

```bash
python -m motopicker --budget 9000 --purpose city --experience beginner --height 175 --license A2 --top 3
```

| Parametr | Dəyərlər | Təsvir |
|---|---|---|
| `--budget` | ədəd | Büdcə (USD) |
| `--purpose` | `city`, `touring`, `offroad`, `sport` | İstifadə məqsədi |
| `--experience` | `beginner`, `intermediate`, `expert` | Təcrübə |
| `--height` | 120-230 | Boy (sm) |
| `--license` | `A1`, `A2`, `A` | Vəsiqə kateqoriyası |
| `--top` | tam ədəd (default 5) | Neçə nəticə göstərilsin |
| `--data` | fayl yolu | Başqa CSV faylı |

Nümunə çıxış:

```
1. Honda CB125R  |  92.3 xal  |  $4,500  |  11 kW
   Ümumi xal 92.3/100. Kateqoriyası (city) seçdiyiniz məqsədə uyğundur. Ən güclü cəhətləri: aşağı çəki, sərfəli qiymət. Qiyməti büdcədən 4,500 USD aşağıdır. Oturacaq hündürlüyü (816 mm) boyunuz üçün maksimum 910 mm həddindən aşağıdır.
2. Yamaha MT-03  |  57.6 xal  |  $5,500  |  31 kW
   ...
```

Çıxış kodları: `0` uğurlu, `1` uyğun motosiklet yoxdur, `2` xəta (yanlış giriş / CSV).

## Alqoritm

Tövsiyə üç mərhələdə hesablanır (`recommender.py`):

**1. Sərt filtrlər (`filters.py`)** — keçməyən motosiklet heç xallandırılmır:
- **Büdcə:** `price_usd <= budget`
- **Vəsiqə:** motosikletin tələb etdiyi kateqoriya sürücünün kateqoriyasından yuxarı olmamalıdır;
  güc limiti: **A1 ≤ 11 kW**, **A2 ≤ 35 kW**, **A** limitsiz
- **Boy:** `seat_height_mm <= boy_sm * 10 * 0.52`

**2. Normallaşdırma (`scoring.py`)** — hər ədədi meyar (qiymət, güc, çəki, oturacaq hündürlüyü,
yanacaq sərfi) *namizədlər arasında* min-max ilə [0, 1]-ə gətirilir:

```
normalized = (value - min) / (max - min)        # böyük yaxşıdırsa (güc)
normalized = 1 - (value - min) / (max - min)    # kiçik yaxşıdırsa (qiymət, çəki, sərf, hündürlük)
```
Bütün namizədlərin dəyəri eynidirsə normallaşdırılmış dəyər 1.0 olur. Kateqoriya meyarı 1 (məqsədə
uyğun) və ya 0-dır.

**3. Çəkili xal** — `xal = 100 * Σ (çəki_i * normalized_i)`. Çəkilər istifadə məqsədinə görə
`constants.py`-dəki `BASE_WEIGHTS` cədvəlindən götürülür (məsələn, sport üçün güc çəkisi 0.35,
city üçün 0.05). Sonra təcrübəyə görə vuruqlar tətbiq olunur (məsələn, beginner üçün güc çəkisi ×0.3,
çəki ×1.5) və çəkilər yenidən cəmi 1 olacaq şəkildə normallaşdırılır.

**Bərabərlik:** xallar bərabərdirsə daha ucuz, sonra əlifba sırası ilə (nəticə həmişə deterministikdir).

**İzahat:** hər tövsiyədə kateqoriya uyğunluğu, ən çox xal gətirən 2 meyar, büdcə qənaəti və boy
uyğunluğu yazılır.

## Layihə strukturu

```
src/motopicker/
  enums.py        Purpose, Experience, LicenseClass, Criterion
  constants.py    bütün sabitlər (çəkilər, limitlər, nisbətlər)
  models.py       Motorcycle, UserProfile, ScoredMotorcycle, Recommendation
  data.py         CSV yükləmə + validasiya (DataValidationError)
  filters.py      sərt filtrlər
  scoring.py      min-max normallaşdırma + çəkili xal
  recommender.py  tövsiyə + izahat
  cli.py          argparse interfeysi
data/motorcycles.csv
tests/            pytest testləri
```

## Testlər

```bash
pytest
```

130 test, **100% coverage** (minimum tələb 90%, `pyproject.toml`-da `--cov-fail-under=90`).
Əhatə olunan hallar: sərhəd dəyərləri (büdcə, 11/35 kW, oturacaq hündürlüyü), səhv CSV
(çatışmayan sütun, yanlış tip, mənfi dəyər, boş fayl), boş nəticə, bərabər xallar, CLI xəta halları.
GitHub Actions hər push-da testləri avtomatik işə salır (`.github/workflows/ci.yml`).

## Məhdudiyyətlər

- Data kiçikdir (20 model) və təxminidir.
- Boy → oturacaq hündürlüyü qaydası sadələşdirilmiş nisbətdir (0.52); real ayaqla yerə çatma
  səviyyəsi bədən nisbətlərindən asılıdır.
- Çəkilər ekspert qərarıdır, statistik olaraq öyrənilməyib.
