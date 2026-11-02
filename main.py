import argparse
import json
import logging
from pathlib import Path

from autoqa.grader import model_grading
from autoqa.comparison import load_dataset_to_dataframe, load_compare
from autoqa.helper import load_label

### Grade v.0
ROOT = Path(__file__).resolve().parent
LABELS_PATH = ROOT / "data" / "golden" / "labels_v0.1.jsonl"
RAW_PATH = ROOT / "data" / "abcd_pretty.json"
RUBRIC_PATH = ROOT / "rubric.md"
GUIDELINES_PATH = ROOT / "data" / "guidelines.json"
OUTPUT_PATH = ROOT / "data" / "model" / "output"
CSV_PATH = ROOT / "data" / "csv"

logging.basicConfig(level=logging.INFO)


def latest_run() -> str:
    """Return the run ID of the latest grading output."""
    runs = sorted(OUTPUT_PATH.glob("*.json"))
    if not runs:
        raise SystemExit(f"No grading runs found in {OUTPUT_PATH}")
    return runs[-1].stem

def grade() -> str:
    """Step 1: grade the golden set with the model. """
    output_file_path = model_grading(LABELS_PATH=LABELS_PATH, RAW_PATH=RAW_PATH, RUBRIC_PATH=RUBRIC_PATH, 
                  GUIDELINES_PATH=GUIDELINES_PATH, OUTPUT_PATH=OUTPUT_PATH)
    logging.info(f"Model grading output file path: {output_file_path}")

    return Path(output_file_path).stem


def build_csv(run_id: str) -> None:
    """Step 2: join run model verdicts with the golden labels into a CSV."""
    ### Extract data of golden datasets
    label_data: dict[dict[dict]] = load_label(LABELS_PATH)
    
    ### Extract data of model output data
    with open(OUTPUT_PATH/ f"{run_id}.json") as f:
        original_model_data = json.load(f)
        model_data = original_model_data["results"]

    compare_df = load_dataset_to_dataframe(model_data, label_data)

    ### load to csv
    compare_df.to_csv(CSV_PATH / f"comparedf_{run_id}.csv", index=False)
    logging.info(f"Comparison CSV written for run: {run_id}")

def compare(run_id: str) -> None:
    metrics_df = load_compare(CSV_PATH / f"comparedf_{run_id}")
    print(metrics_df.to_string())

def main() -> None:
    parser = argparse.ArgumentParser(description="AutoQA pipeline")
    parser.add_argument("--grade", action="store_true", help="grade the golden dataset using current model")
    parser.add_argument("--build", action="store_true", help="join the model verdict with golden dataset")
    parser.add_argument("--compare", action="store_true", help="compare model verdict with golden dataset")
    parser.add_argument("--all", action="store_true", help="running the whole pipeline")
    
    args = parser.parse_args()

    run_id = latest_run()

    if args.grade:
        grade()
    
    if args.build:
        build_csv(run_id)
    
    if args.compare:
        compare(run_id)
    
    if args.all:
        grade()
        build_csv(run_id)
        compare(run_id)

if __name__ == "__main__":
    main()


    


    