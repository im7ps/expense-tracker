"""Totali mensili delle spese per categoria.

Contano solo i movimenti negativi (spese). Le entrate sono escluse.
"""

from __future__ import annotations

from collections.abc import Iterable

from expense_tracker.normalize import Movement, format_cents


def monthly_expenses(movements: Iterable[Movement], year: int, month: int) -> dict[str, int]:
    """Restituisce {categoria: totale spese in centesimi positivi}, dal più alto."""
    prefix = f"{year:04d}-{month:02d}-"
    totals: dict[str, int] = {}
    for movement in movements:
        if not movement.date.startswith(prefix) or movement.amount_cents >= 0:
            continue
        totals[movement.category] = totals.get(movement.category, 0) - movement.amount_cents
    return dict(sorted(totals.items(), key=lambda item: (-item[1], item[0])))


def format_report(totals: dict[str, int], year: int, month: int) -> str:
    title = f"Spese per categoria - {year:04d}-{month:02d}"
    if not totals:
        return f"{title}\nNessuna spesa nel periodo."

    width = max(len("Totale"), *(len(category) for category in totals))
    lines = [title, ""]
    for category, cents in totals.items():
        lines.append(f"{category:<{width}}  {format_cents(cents):>12}")
    lines.append("-" * (width + 14))
    lines.append(f"{'Totale':<{width}}  {format_cents(sum(totals.values())):>12}")
    return "\n".join(lines)
