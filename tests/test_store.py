from contextlib import closing

from expense_tracker import store
from expense_tracker.normalize import Movement


def test_replace_source_overwrites_only_that_source(tmp_path):
    first = Movement("2026-01-01", "Bar", -100, "ristorazione")
    second = Movement("2026-01-03", "Cinema", -1400, "svago")
    replacement = Movement("2026-01-01", "Bar", -250, "ristorazione")
    other = Movement("2026-01-02", "Farmacia", -990, "salute")

    with closing(store.connect(tmp_path / "test.db")) as conn:
        store.replace_source(conn, "a.csv", [first, second])
        store.replace_source(conn, "b.csv", [other])
        store.replace_source(conn, "a.csv", [replacement])

        assert store.load_movements(conn) == [replacement, other]
