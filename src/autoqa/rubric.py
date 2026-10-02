import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUBRIC_PATH = ROOT / "rubric.md"


def load_rubric() -> tuple[str, list[dict]]:
    text = RUBRIC_PATH.read_text()
    m = re.search(r"^# .*?(v\d+(?:\.\d+)*)\s*$", text, re.M)
    if not m:
        raise SystemExit("rubric.md needs a title with a version, e.g. '# ABCD Rubric v0.1'")
    criteria = []
    for block in re.split(r"^## ", text, flags=re.M)[1:]:
        name = block.split("\n", 1)[0].strip()
        question = re.search(r"\*\*Question:\*\*\s*(.+)", block)
        na = re.search(r"\*\*N/A:\*\*\s*(.+)", block)
        criteria.append({
            "name": name,
            "question": question.group(1).strip() if question else "",
            "allows_na": not (na and "never NOT_APPLICABLE" in na.group(1)),
        })
    return m.group(1), criteria