"""Interfaccia da terminale.

    expense-tracker import <file> --source sorgente_a|sorgente_b [--rules FILE] [--db FILE]
    expense-tracker report --year 2026 --month 1 [--db FILE]
"""

from __future__ import annotations

import argparse
import csv
import sqlite3
import sys
from collections import Counter
from contextlib import closing
from pathlib import Path

from expense_tracker import store
from expense_tracker.importer import PROFILES, import_csv
from expense_tracker.report import format_report, monthly_expenses
from expense_tracker.rules import RuleSet, load_rules

DEFAULT_DB = "expenses.db"


def _month(value: str) -> int:
    try:
        number = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"mese non valido: {value!r}") from None
    if not 1 <= number <= 12:
        raise argparse.ArgumentTypeError("il mese deve essere compreso tra 1 e 12")
    return number


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="expense-tracker",
        description="Importa movimenti da CSV e genera il report mensile delle spese.",
    )
    subcommands = parser.add_subparsers(dest="command", required=True)

    importer = subcommands.add_parser("import", help="importa un file CSV")
    importer.add_argument("file", type=Path, help="file CSV da importare")
    importer.add_argument(
        "--source", required=True, choices=sorted(PROFILES), help="profilo della sorgente"
    )
    importer.add_argument("--rules", type=Path, help="file JSON con le regole di categoria")
    importer.add_argument("--db", type=Path, default=DEFAULT_DB, help=f"database (default: {DEFAULT_DB})")

    reporter = subcommands.add_parser("report", help="totale delle spese per categoria nel mese")
    reporter.add_argument("--year", type=int, required=True, help="anno, es. 2026")
    reporter.add_argument("--month", type=_month, required=True, help="mese, da 1 a 12")
    reporter.add_argument("--db", type=Path, default=DEFAULT_DB, help=f"database (default: {DEFAULT_DB})")

    return parser


def _run_import(args: argparse.Namespace) -> int:
    try:
        result = import_csv(args.file, args.source)
        rules = load_rules(args.rules) if args.rules else RuleSet()
        with closing(store.connect(args.db)) as conn:
            movements = [rules.assign(movement) for movement in result.movements]
            store.replace_source(conn, str(args.file.resolve()), movements)
    except (OSError, ValueError, csv.Error, sqlite3.Error) as error:
        print(f"Errore: {error}", file=sys.stderr)
        return 1

    for skipped in result.skipped:
        print(f"Attenzione: riga {skipped.line_number} saltata: {skipped.reason}", file=sys.stderr)

    print(f"Import da {args.source}: {args.file}")
    print(f"Movimenti importati: {len(movements)}")
    print(f"Righe saltate: {len(result.skipped)}")
    for category, count in sorted(Counter(m.category for m in movements).items()):
        print(f"  {category}: {count}")
    print(f"Database: {args.db}")
    return 0


def _run_report(args: argparse.Namespace) -> int:
    if not args.db.exists():
        print(f"Errore: database non trovato: {args.db} (esegui prima un import)", file=sys.stderr)
        return 1
    try:
        with closing(store.connect(args.db)) as conn:
            movements = store.load_movements(conn)
    except sqlite3.Error as error:
        print(f"Errore: {error}", file=sys.stderr)
        return 1

    totals = monthly_expenses(movements, args.year, args.month)
    print(format_report(totals, args.year, args.month))
    return 0


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "import":
        return _run_import(args)
    return _run_report(args)


if __name__ == "__main__":
    sys.exit(main())
