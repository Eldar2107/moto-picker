import runpy
import sys

import pytest

from motopicker.cli import EXIT_ERROR, EXIT_NO_RESULTS, EXIT_OK, main

BASE_ARGS = [
    "--budget", "9000", "--purpose", "city", "--experience", "beginner",
    "--height", "175", "--license", "A2",
]


def test_success_prints_recommendations(capsys):
    assert main(BASE_ARGS) == EXIT_OK
    out = capsys.readouterr().out
    assert "1." in out and "xal" in out and "kW" in out


def test_top_argument_limits_output(capsys):
    assert main([*BASE_ARGS, "--top", "2"]) == EXIT_OK
    lines = [ln for ln in capsys.readouterr().out.splitlines() if ln[:2] in ("1.", "2.", "3.")]
    assert len(lines) == 2


def test_no_results_exit_code(capsys):
    args = ["--budget", "500", "--purpose", "city", "--experience", "beginner",
            "--height", "175", "--license", "A2"]
    assert main(args) == EXIT_NO_RESULTS
    assert "tapılmadı" in capsys.readouterr().out


def test_invalid_budget_returns_error(capsys):
    args = ["--budget", "-5", "--purpose", "city", "--experience", "beginner",
            "--height", "175", "--license", "A2"]
    assert main(args) == EXIT_ERROR
    assert "Xəta" in capsys.readouterr().err


def test_missing_data_file_returns_error(capsys, tmp_path):
    assert main([*BASE_ARGS, "--data", str(tmp_path / "nope.csv")]) == EXIT_ERROR
    assert "Xəta" in capsys.readouterr().err


def test_bad_csv_returns_error(capsys, tmp_path):
    bad = tmp_path / "bad.csv"
    bad.write_text("brand,model\nHonda,X\n", encoding="utf-8")
    assert main([*BASE_ARGS, "--data", str(bad)]) == EXIT_ERROR
    assert "çatışmayan sütunlar" in capsys.readouterr().err


def test_invalid_top_returns_error(capsys):
    assert main([*BASE_ARGS, "--top", "0"]) == EXIT_ERROR


def test_invalid_choice_exits_with_argparse_error():
    with pytest.raises(SystemExit) as exc:
        main(["--budget", "9000", "--purpose", "boat", "--experience", "beginner",
              "--height", "175", "--license", "A2"])
    assert exc.value.code == 2


def test_missing_required_args_exits():
    with pytest.raises(SystemExit):
        main([])


def test_module_entrypoint(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["motopicker", *BASE_ARGS])
    with pytest.raises(SystemExit) as exc:
        runpy.run_module("motopicker", run_name="__main__")
    assert exc.value.code == EXIT_OK
    assert "xal" in capsys.readouterr().out
