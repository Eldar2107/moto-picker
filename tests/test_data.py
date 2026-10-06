import pytest

from motopicker.constants import CSV_COLUMNS, DEFAULT_DATA_PATH
from motopicker.data import DataValidationError, load_motorcycles, parse_row
from motopicker.enums import LicenseClass, Purpose

HEADER = ",".join(CSV_COLUMNS)
GOOD_ROW = "Honda,CB125R,4500,11.0,130,816,2.1,city,A1"


def write_csv(tmp_path, *lines: str):
    path = tmp_path / "bikes.csv"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def test_real_dataset_loads_with_20_models():
    bikes = load_motorcycles(DEFAULT_DATA_PATH)
    assert len(bikes) == 20
    assert {b.category for b in bikes} == set(Purpose)
    assert {b.license_class for b in bikes} == set(LicenseClass)


def test_real_dataset_has_unique_models():
    names = [b.name for b in load_motorcycles(DEFAULT_DATA_PATH)]
    assert len(names) == len(set(names))


def test_valid_row_parsed(tmp_path):
    bikes = load_motorcycles(write_csv(tmp_path, HEADER, GOOD_ROW))
    assert bikes[0].name == "Honda CB125R"
    assert bikes[0].price_usd == 4500.0
    assert bikes[0].license_class is LicenseClass.A1


def test_category_and_license_are_case_insensitive(tmp_path):
    row = "Honda,CB125R,4500,11,130,816,2.1,CITY,a1"
    bike = load_motorcycles(write_csv(tmp_path, HEADER, row))[0]
    assert bike.category is Purpose.CITY and bike.license_class is LicenseClass.A1


def test_missing_file_raises():
    with pytest.raises(FileNotFoundError):
        load_motorcycles("does/not/exist.csv")


def test_missing_columns(tmp_path):
    path = write_csv(tmp_path, "brand,model", "Honda,CB125R")
    with pytest.raises(DataValidationError, match="çatışmayan sütunlar"):
        load_motorcycles(path)


def test_empty_file_has_no_columns(tmp_path):
    path = tmp_path / "empty.csv"
    path.write_text("", encoding="utf-8")
    with pytest.raises(DataValidationError, match="çatışmayan sütunlar"):
        load_motorcycles(path)


def test_header_only_file(tmp_path):
    with pytest.raises(DataValidationError, match="heç bir motosiklet yoxdur"):
        load_motorcycles(write_csv(tmp_path, HEADER))


@pytest.mark.parametrize(
    ("row", "message"),
    [
        ("Honda,CB125R,abc,11,130,816,2.1,city,A1", "'price_usd' ədəd olmalıdır"),
        ("Honda,CB125R,,11,130,816,2.1,city,A1", "'price_usd' ədəd olmalıdır"),
        ("Honda,CB125R,-5,11,130,816,2.1,city,A1", "müsbət olmalıdır"),
        ("Honda,CB125R,4500,0,130,816,2.1,city,A1", "'power_kw' müsbət"),
        ("Honda,CB125R,4500,11,130,816,x,city,A1", "'fuel_l_per_100km' ədəd"),
        (",CB125R,4500,11,130,816,2.1,city,A1", "boş ola bilməz"),
        ("Honda,,4500,11,130,816,2.1,city,A1", "boş ola bilməz"),
        ("Honda,CB125R,4500,11,130,816,2.1,scooter,A1", "naməlum kateqoriya"),
        ("Honda,CB125R,4500,11,130,816,2.1,city,B", "naməlum vəsiqə"),
    ],
)
def test_invalid_rows_raise_clear_error(tmp_path, row, message):
    with pytest.raises(DataValidationError, match=message):
        load_motorcycles(write_csv(tmp_path, HEADER, row))


def test_error_reports_correct_line_number(tmp_path):
    bad = "Honda,Bad,oops,11,130,816,2.1,city,A1"
    with pytest.raises(DataValidationError, match="Sətir 3"):
        load_motorcycles(write_csv(tmp_path, HEADER, GOOD_ROW, bad))


def test_parse_row_directly():
    row = dict(zip(CSV_COLUMNS, GOOD_ROW.split(","), strict=True))
    assert parse_row(row, 2).model == "CB125R"


def test_validation_error_is_value_error():
    assert issubclass(DataValidationError, ValueError)
