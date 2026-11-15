from pathlib import Path

import pytest

from expense_tracker.cli import main

ROOT = Path(__file__).parents[1]
FIXTURES = ROOT / "tests" / "fixtures"
RULES = ROOT / "config" / "rules.example.json"


def test_import_then_report_shows_monthly_totals_by_category(tmp_path, capsys):
    db = tmp_path / "test.db"

    assert main([
        "import", str(FIXTURES / "sorgente_a.csv"),
        "--source", "sorgente_a", "--rules", str(RULES), "--db", str(db),
    ]) == 0
    assert main([
        "import", str(FIXTURES / "sorgente_b.csv"),
        "--source", "sorgente_b", "--rules", str(RULES), "--db", str(db),
    ]) == 0
    capsys.readouterr()

    assert main(["report", "--year", "2026", "--month", "1", "--db", str(db)]) == 0

    out = capsys.readouterr().out
    assert "Spese per categoria - 2026-01" in out
    assert "alimentazione" in out
    assert "83,95" in out  # 45,20 + 38,75
    assert "non_categorizzato" in out
    assert "12,34" in out


def test_import_prints_warning_for_invalid_row_and_continues(tmp_path, capsys):
    db = tmp_path / "test.db"

    code = main([
        "import", str(FIXTURES / "sorgente_a.csv"),
        "--source", "sorgente_a", "--db", str(db),
    ])

    captured = capsys.readouterr()
    assert code == 0
    assert "riga 8 saltata" in captured.err
    assert "Movimenti importati: 6" in captured.out
    assert "Righe saltate: 1" in captured.out


def test_import_missing_file_returns_error(tmp_path, capsys):
    code = main([
        "import", str(tmp_path / "non_esiste.csv"),
        "--source", "sorgente_a", "--db", str(tmp_path / "test.db"),
    ])

    assert code == 1
    assert "Errore" in capsys.readouterr().err


def test_report_without_database_returns_error(tmp_path, capsys):
    code = main(["report", "--year", "2026", "--month", "1", "--db", str(tmp_path / "missing.db")])

    assert code == 1
    assert "esegui prima un import" in capsys.readouterr().err


def test_report_rejects_month_out_of_range(tmp_path):
    with pytest.raises(SystemExit):
        main(["report", "--year", "2026", "--month", "13", "--db", str(tmp_path / "x.db")])
