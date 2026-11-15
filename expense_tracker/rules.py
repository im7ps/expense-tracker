"""Assegnazione delle categorie tramite regole lette da un file JSON.

Il file ha la forma {"parola chiave": "categoria"}. Una regola corrisponde se la
parola chiave compare nella descrizione, senza distinguere maiuscole e minuscole.
Vince la prima regola del file che corrisponde.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, replace
from pathlib import Path

from expense_tracker.normalize import UNCATEGORIZED, Movement


@dataclass(frozen=True)
class Rule:
    keyword: str  # già in minuscolo (casefold)
    category: str


@dataclass(frozen=True)
class RuleSet:
    rules: tuple[Rule, ...] = ()

    def categorize(self, description: str) -> str:
        text = description.casefold()
        for rule in self.rules:
            if rule.keyword in text:
                return rule.category
        return UNCATEGORIZED

    def assign(self, movement: Movement) -> Movement:
        return replace(movement, category=self.categorize(movement.description))


def load_rules(path: str | Path) -> RuleSet:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("il file delle regole deve contenere un oggetto JSON {parola: categoria}")

    rules = []
    for keyword, category in data.items():
        key = keyword.strip().casefold()
        if not key:
            raise ValueError("parola chiave vuota nel file delle regole")
        if not isinstance(category, str) or not category.strip():
            raise ValueError(f"categoria non valida per la parola chiave {keyword!r}")
        rules.append(Rule(keyword=key, category=category.strip()))
    return RuleSet(rules=tuple(rules))
