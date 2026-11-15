"""Lettura di un CSV in base al profilo della sorgente.

Una riga non valida viene saltata e registrata in `ImportResult.skipped`,
senza interrompere l'import. Un file senza le colonne attese è un errore fatale.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path

from expense_tracker.normalize import Movement, parse_amount_cents, parse_date


@dataclass(frozen=True)
class SourceProfile:
    name: str
    delimiter: str
    date_column: str
    description_column: str
    amount_column: str


PROFILES: dict[str, SourceProfile] = {
    "sorgente_a": SourceProfile(
        name="sorgente_a",
        delimiter=";",
        date_column="data",
        description_column="descrizione",
        amount_column="importo",
    ),
    "sorgente_b": SourceProfile(
        name="sorgente_b",
        delimiter=",",
        date_column="date",
        description_column="description",
        amount_column="amount",
    ),
}


@dataclass(frozen=True)
class SkippedRow:
    line_number: int
    reason: str


@dataclass
class ImportResult:
    movements: list[Movement] = field(default_factory=list)
    skipped: list[SkippedRow] = field(default_factory=list)


def import_csv(path: str | Path, source: str) -> ImportResult:
    try:
        profile = PROFILES[source]
    except KeyError:
        valid = ", ".join(PROFILES)
        raise ValueError(f"sorgente sconosciuta: {source!r} (valori ammessi: {valid})") from None

    result = ImportResult()
    with Path(path).open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle, delimiter=profile.delimiter)
        columns = (profile.date_column, profile.description_column, profile.amount_column)
        header = reader.fieldnames or []
        missing = [column for column in columns if column not in header]
        if missing:
            raise ValueError(f"colonne mancanti nel file: {', '.join(missing)}")

        for row in reader:
            if not any(value and value.strip() for value in row.values() if value is not None):
                continue
            try:
                movement = _to_movement(row, profile)
            except ValueError as error:
                result.skipped.append(SkippedRow(line_number=reader.line_num, reason=str(error)))
            else:
                result.movements.append(movement)
    return result


def _to_movement(row: dict[str | None, str | None], profile: SourceProfile) -> Movement:
    if None in row or any(value is None for value in row.values()):
        raise ValueError("numero di campi diverso dall'intestazione")

    description = row[profile.description_column].strip()
    if not description:
        raise ValueError("descrizione vuota")

    return Movement(
        date=parse_date(row[profile.date_column]),
        description=description,
        amount_cents=parse_amount_cents(row[profile.amount_column]),
    )
