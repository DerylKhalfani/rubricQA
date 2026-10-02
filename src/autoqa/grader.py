import json
from pathlib import Path
from autoqa.guidelines import SUBFLOW_MAP, guideline_key, load_guidelines

### Grade v.0
ROOT = Path(__file__).resolve().parents[2]
LABELS_PATH = ROOT / "data" / "golden" / "labels_v0.1.jsonl"
RAW_PATH = ROOT / "data" / "abcd_pretty.json"


# Loading the golden label
with open(LABELS_PATH) as f:
    label_data = [json.loads(line) for line in f if line.strip()]

# label or rubric data always has 6 lines according to rubric v0.1
grouping_label = {}
for row_label in label_data:
    convo_id = row_label["convo_id"]

    if row_label["pass_no"] == 1:

        # check convo id, make empty inner dict
        if convo_id not in grouping_label:
            grouping_label[convo_id] = grouping_label.get(convo_id, {})

        criterion = row_label["criterion"]
        verdict = row_label["verdict"]
        reason = row_label["reason"]
        unsure = row_label["unsure"]
        rubric_version = row_label["rubric_version"]
        labeled_at = row_label["labeled_at"]

        # check criterion, make empty inner inner dict
        if criterion not in grouping_label[convo_id]:
            grouping_label[convo_id][criterion] = grouping_label[convo_id].get(criterion, {})

        grouping_label[convo_id][criterion]["verdict"] = verdict
        grouping_label[convo_id][criterion]["reason"] = reason
        grouping_label[convo_id][criterion]["unsure"] = unsure
        grouping_label[convo_id][criterion]["rubric_version"] = rubric_version
        grouping_label[convo_id][criterion]["labeled_at"] = labeled_at



# loading the conversation from raw file
with open(RAW_PATH) as f:
    raw_data = json.load(f)

