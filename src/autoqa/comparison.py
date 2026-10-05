import json 
from pathlib import Path

from autoqa.helper import load_label

# Grade v.0
ROOT = Path(__file__).resolve().parents[2]
LABELS_PATH = ROOT / "data" / "golden" / "labels_v0.1.jsonl"
OUTPUT_PATH = ROOT / "data" / "model" / "output"

### Extract data of golden datasets
label_data = load_label(LABELS_PATH)


### Extract data of model output data
with open(f"{OUTPUT_PATH}/2026-10-04_18-42-35.json", "r") as f:
    model_data = json.load(f)

