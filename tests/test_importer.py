from pathlib import Path

import pytest

from expense_tracker.importer import import_csv
from expense_tracker.normalize import Movement

FIXTURES = Path(__file__).parent / "fixtures"


def test_sorgente_a_imports_valid_rows_and_skips_invalid_amount():
    result = import_csv(FIXTURES / "sorgente_a.csv", "sorgente_a")

    assert len(result.movements) == 6
    assert len(result.skipped) == 1
    skipped = result.skipped[0]
    assert skipped.line_number == 8
    assert "importo non valido" in skipped.reason


def test_sorgente_a_normalizes_dates_and_amounts():
    movements = import_csv(FIXTURES / "sorgente_a.csv", "sorgente_a").movements

    assert movements[0] == Movement(
        date="2026-01-31", description="Supermercato Esempio", amount_cents=-4520
    )
    assert movements[1] == Movement(
        date="2026-01-02", description="Stipendio Demo", amount_cents=150000
    )


def test_sorgente_b_reads_iso_dates_and_dot_decimals():
    result = import_csv(FIXTURES / "sorgente_b.csv", "sorgente_b")

    assert result.skipped == []
    assert len(result.movements) == 6
    assert result.movements[0] == Movement(
        date="2026-01-03", description="Supermercato Esempio", amount_cents=-3875
    )
    assert result.movements[4].amount_cents == 2000


def test_unknown_source_is_rejected():
    with pytest.raises(ValueError, match="sorgente sconosciuta"):
        import_csv(FIXTURES / "sorgente_a.csv", "sorgente_z")


def test_missing_columns_are_rejected(tmp_path):
    path = tmp_path / "bad.csv"
    path.write_text("data;descrizione\n31/01/2026;Test\n", encoding="utf-8")

    with pytest.raises(ValueError, match="colonne mancanti"):
        import_csv(path, "sorgente_a")


def test_invalid_date_and_short_rows_are_skipped_without_stopping(tmp_path):
    path = tmp_path / "mixed.csv"
    path.write_text(
        "date,description,amount\n"
        "2026-01-10,Cinema Demo,-10.00\n"
        "2026-02-30,Data sbagliata,-5.00\n"
        "2026-01-11\n",
        encoding="utf-8",
    )

    result = import_csv(path, "sorgente_b")

    assert len(result.movements) == 1
    assert [row.line_number for row in result.skipped] == [3, 4]
    assert "data non valida" in result.skipped[0].reason
    assert "numero di campi" in result.skipped[1].reason


def test_blank_lines_are_ignored(tmp_path):
    path = tmp_path / "blank.csv"
    path.write_text("date,description,amount\n\n2026-01-10,Bar,-1.00\n\n", encoding="utf-8")

    result = import_csv(path, "sorgente_b")

    assert len(result.movements) == 1
    assert result.skipped == []
