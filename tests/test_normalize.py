import pytest

from expense_tracker.normalize import format_cents, parse_amount_cents, parse_date


@pytest.mark.parametrize(
    "value, expected",
    [
        ("31/01/2026", "2026-01-31"),
        ("2026-01-31", "2026-01-31"),
        ("31-01-2026", "2026-01-31"),
        ("31.01.2026", "2026-01-31"),
        (" 1/2/2026 ", "2026-02-01"),
    ],
)
def test_parse_date_normalizes_known_formats_to_iso(value, expected):
    assert parse_date(value) == expected


@pytest.mark.parametrize("value", ["31/02/2026", "2026/01/31", "ieri", ""])
def test_parse_date_rejects_invalid_values(value):
    with pytest.raises(ValueError, match="data non valida"):
        parse_date(value)


@pytest.mark.parametrize(
    "value, expected",
    [
        ("-45,20", -4520),
        ("-45.20", -4520),
        ("1.234,56", 123456),
        ("-1,234.56", -123456),
        ("12", 1200),
        ("+3,5", 350),
        ("-0,01", -1),
        ("1.234", 123400),
        (" -7,00 ", -700),
    ],
)
def test_parse_amount_cents_returns_integer_cents(value, expected):
    result = parse_amount_cents(value)
    assert result == expected
    assert type(result) is int


@pytest.mark.parametrize("value", ["abc", "", "12,", "1.2.3", "1.234,5.6", "1.234.56", "--5"])
def test_parse_amount_cents_rejects_invalid_amounts(value):
    with pytest.raises(ValueError, match="importo non valido"):
        parse_amount_cents(value)


@pytest.mark.parametrize(
    "cents, expected",
    [
        (-4520, "-45,20"),
        (123456, "1.234,56"),
        (5, "0,05"),
        (0, "0,00"),
    ],
)
def test_format_cents_uses_italian_separators(cents, expected):
    assert format_cents(cents) == expected
