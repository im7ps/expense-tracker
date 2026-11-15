from expense_tracker.normalize import Movement
from expense_tracker.report import format_report, monthly_expenses

MOVEMENTS = [
    Movement("2026-01-05", "Benzina A", -6000, "trasporti"),
    Movement("2026-01-10", "Spesa A", -1000, "alimentazione"),
    Movement("2026-01-20", "Benzina B", -500, "trasporti"),
    Movement("2026-01-25", "Stipendio", 200000, "entrate"),
    Movement("2026-02-01", "Spesa di febbraio", -9999, "alimentazione"),
    Movement("2025-01-15", "Spesa di un altro anno", -9999, "alimentazione"),
]


def test_monthly_expenses_sums_only_expenses_of_the_month():
    totals = monthly_expenses(MOVEMENTS, 2026, 1)

    assert totals == {"trasporti": 6500, "alimentazione": 1000}


def test_monthly_expenses_are_sorted_by_total_descending():
    totals = monthly_expenses(MOVEMENTS, 2026, 1)

    assert list(totals) == ["trasporti", "alimentazione"]


def test_monthly_expenses_for_month_without_data_is_empty():
    assert monthly_expenses(MOVEMENTS, 2026, 3) == {}


def test_format_report_lists_categories_and_total():
    text = format_report({"trasporti": 6500, "alimentazione": 1000}, 2026, 1)

    assert text.splitlines()[0] == "Spese per categoria - 2026-01"
    assert "trasporti" in text
    assert "65,00" in text
    assert "10,00" in text
    assert "Totale" in text
    assert "75,00" in text


def test_format_report_without_expenses_says_so():
    text = format_report({}, 2026, 1)

    assert "Nessuna spesa nel periodo." in text
