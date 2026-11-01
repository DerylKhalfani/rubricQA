from autoqa.grader import model_grading
from autoqa.comparison import load_dataset_to_dataframe, load_compare
from autoqa.helper import load_label

from pathlib import Path
from typing import Literal
import logging
import json

# Grade v.0
comparison_date = "2026-10-04_18-42-35"

### Grade v.0
ROOT = Path(__file__).resolve().parent
LABELS_PATH = ROOT / "data" / "golden" / "labels_v0.1.jsonl"
RAW_PATH = ROOT / "data" / "abcd_pretty.json"
RUBRIC_PATH = ROOT / "rubric.md"
GUIDELINES_PATH = ROOT / "data" / "guidelines.json"
OUTPUT_PATH = ROOT / "data" / "model" / "output"
COMPARE_PATH = ROOT / "data" / "csv" / f"comparedf_{comparison_date}"

logging.basicConfig(level=logging.INFO)


def main(load_dataset: Literal[True, False]):

    # apply model to grade golden label dataset
    output_file_path = model_grading(LABELS_PATH=LABELS_PATH, RAW_PATH=RAW_PATH, RUBRIC_PATH=RUBRIC_PATH, 
                  GUIDELINES_PATH=GUIDELINES_PATH, OUTPUT_PATH=OUTPUT_PATH)

    logging.info(f"Model grading output file path: {output_file_path}")
    compare_path = ROOT / "data" / "csv" / f"comparedf_{Path(output_file_path).stem}"

    if load_dataset:

        ### Extract data of golden datasets
        label_data: dict[dict[dict]] = load_label(LABELS_PATH)
        
        ### Extract data of model output data
        with open(output_file_path, "r") as f:
            original_model_data = json.load(f)
            model_data = original_model_data["results"]

        compare_df = load_dataset_to_dataframe(model_data, label_data)

        ### load to csv
        compare_df.to_csv(f"{compare_path}.csv", index=False)

    metrics_df = load_compare(compare_path)
    print(metrics_df.to_string())

if __name__ == "__main__":
    main(load_dataset=False)


