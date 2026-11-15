"""Normalizzazione di date e importi.

Le date diventano ISO (YYYY-MM-DD). Gli importi diventano centesimi interi:
mai float, per non perdere precisione sui decimali.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime

UNCATEGORIZED = "non_categorizzato"

DATE_FORMATS = ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%d.%m.%Y")

_AMOUNT_CHARS_RE = re.compile(r"[+-]?\d[\d.,]*")
_INTEGER_RE = re.compile(r"\d+|\d{1,3}(?:\.\d{3})+|\d{1,3}(?:,\d{3})+")


@dataclass(frozen=True)
class Movement:
    date: str  # ISO: YYYY-MM-DD
    description: str
    amount_cents: int  # negativo = spesa, positivo = entrata
    category: str = UNCATEGORIZED


def parse_date(value: str) -> str:
    """Converte una data nei formati noti in ISO (YYYY-MM-DD)."""
    text = value.strip()
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(text, fmt).date().isoformat()
        except ValueError:
            continue
    raise ValueError(f"data non valida: {value!r}")


def parse_amount_cents(value: str) -> int:
    """Converte un importo in centesimi interi.

    Accetta virgola o punto come separatore decimale, con segno opzionale.
    L'ultimo separatore con 1 o 2 cifre dopo di sé è il decimale; gli altri
    separatori sono delle migliaia (es. "1.234,56" e "1,234.56" valgono entrambi
    123456). Un gruppo di 3 cifre dopo l'ultimo separatore è letto come migliaia:
    "1.234" vale 1234.
    """
    text = value.strip().replace(" ", "")
    if not _AMOUNT_CHARS_RE.fullmatch(text):
        raise ValueError(f"importo non valido: {value!r}")

    sign = -1 if text.startswith("-") else 1
    digits = text.lstrip("+-")

    integer_part, fraction = digits, ""
    last_sep = max(digits.rfind("."), digits.rfind(","))
    if last_sep != -1 and len(digits) - last_sep - 1 in (1, 2):
        decimal_sep = digits[last_sep]
        integer_part, fraction = digits[:last_sep], digits[last_sep + 1 :]
        if decimal_sep in integer_part:
            raise ValueError(f"importo non valido: {value!r}")

    if not _INTEGER_RE.fullmatch(integer_part):
        raise ValueError(f"importo non valido: {value!r}")

    euros = int(integer_part.replace(".", "").replace(",", ""))
    cents = int(fraction.ljust(2, "0"))
    return sign * (euros * 100 + cents)


def format_cents(cents: int) -> str:
    """Formatta centesimi in stile italiano: -123456 -> '-1.234,56'."""
    sign = "-" if cents < 0 else ""
    euros, rest = divmod(abs(cents), 100)
    return f"{sign}{euros:,}".replace(",", ".") + f",{rest:02d}"
