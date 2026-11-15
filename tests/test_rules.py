import json
from pathlib import Path

import pytest

from expense_tracker.normalize import UNCATEGORIZED, Movement
from expense_tracker.rules import RuleSet, load_rules

EXAMPLE_RULES = Path(__file__).parents[1] / "config" / "rules.example.json"


def write_rules(tmp_path, data):
    path = tmp_path / "rules.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def movement(description, amount_cents=-100):
    return Movement(date="2026-01-01", description=description, amount_cents=amount_cents)


def test_keyword_matches_case_insensitively(tmp_path):
    rules = load_rules(write_rules(tmp_path, {"Supermercato": "alimentazione"}))
    assert rules.categorize("SUPERMERCATO DEMO") == "alimentazione"


def test_keyword_matches_as_substring(tmp_path):
    rules = load_rules(write_rules(tmp_path, {"benzina": "trasporti"}))
    assert rules.categorize("Benzinaio Prova") == "trasporti"


def test_first_matching_rule_wins(tmp_path):
    rules = load_rules(write_rules(tmp_path, {"bar": "ristorazione", "barbiere": "cura"}))
    assert rules.categorize("Barbiere Demo") == "ristorazione"


def test_no_matching_rule_is_uncategorized(tmp_path):
    rules = load_rules(write_rules(tmp_path, {"bar": "ristorazione"}))
    assert rules.categorize("Negozio Sconosciuto") == UNCATEGORIZED


def test_empty_ruleset_leaves_everything_uncategorized():
    assert RuleSet().categorize("qualunque cosa") == UNCATEGORIZED


def test_assign_sets_category_and_keeps_other_fields(tmp_path):
    rules = load_rules(write_rules(tmp_path, {"bar": "ristorazione"}))
    original = movement("Bar Di Prova", amount_cents=-350)

    assigned = rules.assign(original)

    assert assigned.category == "ristorazione"
    assert assigned.date == original.date
    assert assigned.description == original.description
    assert assigned.amount_cents == -350
    assert original.category == UNCATEGORIZED


def test_example_rules_file_loads():
    rules = load_rules(EXAMPLE_RULES)
    assert rules.categorize("Supermercato Esempio") == "alimentazione"


def test_rejects_json_that_is_not_an_object(tmp_path):
    path = tmp_path / "rules.json"
    path.write_text('["bar"]', encoding="utf-8")
    with pytest.raises(ValueError, match="oggetto JSON"):
        load_rules(path)


def test_rejects_non_string_category(tmp_path):
    with pytest.raises(ValueError, match="categoria non valida"):
        load_rules(write_rules(tmp_path, {"bar": 5}))


def test_rejects_empty_keyword(tmp_path):
    with pytest.raises(ValueError, match="parola chiave vuota"):
        load_rules(write_rules(tmp_path, {"   ": "varie"}))
