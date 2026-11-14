import csv
import importlib.resources
from pathlib import Path

CIRCULARS = ("SEBI/HO/MRD/TPD-1/P/CIR/2024/132", "SEBI/HO/MRD/TPD-1/P/CIR/2025/79")
TODO = Path(__file__).parents[3] / "docs" / "plans" / "u5-sources-todo.md"


def test_circular_cited_rows_are_listed_for_human_verification() -> None:
    """Every row citing a 2024/132 or 2025/79 circular is in the todo and still unverified."""
    todo = TODO.read_text(encoding="utf-8")
    ref = importlib.resources.files("axiom_data.reference")
    found = 0
    for entry in ref.iterdir():
        if not entry.name.endswith(".csv"):
            continue
        for row in csv.DictReader(entry.read_text(encoding="utf-8").splitlines()):
            if row.get("source") in CIRCULARS:
                found += 1
                assert row["verified_against"] == ""
                assert f"| `{entry.name}` | `{row['key']}` | `{row['effective_from']}` |" in todo
    assert found == 12
