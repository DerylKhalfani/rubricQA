import json 
import pandas as pd
from pathlib import Path

from autoqa.helper import load_label

# Grade v.0
ROOT = Path(__file__).resolve().parents[2]
LABELS_PATH = ROOT / "data" / "golden" / "labels_v0.1.jsonl"
OUTPUT_PATH = ROOT / "data" / "model" / "output"

### Extract data of golden datasets
label_data: dict[dict[dict]] = load_label(LABELS_PATH)


### Extract data of model output data
with open(f"{OUTPUT_PATH}/2026-10-04_18-42-35.json", "r") as f:
    original_model_data = json.load(f)
    model_data = original_model_data["results"]


### COMPARISON PIPELINE

def load_dataset_to_dataframe(model_data: list[dict[dict[dict]]], label_data: dict[dict[dict]]):

    compare_df = []

    for convo_verdict in model_data:
        convo_id = convo_verdict["convo_id"]

        ### golden dataset verdict
        gd_identity_verified_verdict = label_data[convo_id]['identity_verified']['verdict']
        gd_policy_followed_verdict = label_data[convo_id]['policy_followed']['verdict']
        gd_outcome_communicated_verdict = label_data[convo_id]['outcome_communicated']['verdict']
        gd_bad_news_handled_verdict = label_data[convo_id]['bad_news_handled']['verdict']
        gd_closing_check_verdict = label_data[convo_id]['closing_check']['verdict']
        gd_respectful_tone_verdict = label_data[convo_id]['respectful_tone']['verdict']


        ### golden dataset reason
        gd_identity_verified_reason = label_data[convo_id]['identity_verified']['reason']
        gd_policy_followed_reason = label_data[convo_id]['policy_followed']['reason']
        gd_outcome_communicated_reason = label_data[convo_id]['outcome_communicated']['reason']
        gd_bad_news_handled_reason = label_data[convo_id]['bad_news_handled']['reason']
        gd_closing_check_reason = label_data[convo_id]['closing_check']['reason']
        gd_respectful_tone_reason = label_data[convo_id]['respectful_tone']['reason']
        

        ### model dataset verdict
        md_identity_verified_verdict = convo_verdict['grade']['identity_verified']['verdict']
        md_policy_followed_verdict = convo_verdict['grade']['policy_followed']['verdict']
        md_outcome_communicated_verdict = convo_verdict['grade']['outcome_communicated']['verdict']
        md_bad_news_handled_verdict = convo_verdict['grade']['bad_news_handled']['verdict']
        md_closing_check_verdict = convo_verdict['grade']['closing_check']['verdict']
        md_respectful_tone_verdict = convo_verdict['grade']['respectful_tone']['verdict']


        ### model_dataset reason
        md_identity_verified_reason = convo_verdict['grade']['identity_verified']['reason']
        md_policy_followed_reason = convo_verdict['grade']['policy_followed']['reason']
        md_outcome_communicated_reason = convo_verdict['grade']['outcome_communicated']['reason']
        md_bad_news_handled_reason = convo_verdict['grade']['bad_news_handled']['reason']
        md_closing_check_reason = convo_verdict['grade']['closing_check']['reason']
        md_respectful_tone_reason = convo_verdict['grade']['respectful_tone']['reason']


        ## buidling the dataframe
        compare_df.append({
            "conversation_id": convo_id,
            "gd_identity_verified_verdict": gd_identity_verified_verdict,
            "gd_policy_followed_verdict": gd_policy_followed_verdict,
            "gd_outcome_communicated_verdict": gd_outcome_communicated_verdict,
            "gd_bad_news_handled_verdict": gd_bad_news_handled_verdict,
            "gd_closing_check_verdict": gd_closing_check_verdict,
            "gd_respectful_tone_verdict": gd_respectful_tone_verdict,

            "gd_identity_verified_reason": gd_identity_verified_reason,
            "gd_policy_followed_reason": gd_policy_followed_reason,
            "gd_outcome_communicated_reason": gd_outcome_communicated_reason,
            "gd_bad_news_handled_reason": gd_bad_news_handled_reason,
            "gd_closing_check_reason": gd_closing_check_reason,
            "gd_respectful_tone_reason": gd_respectful_tone_reason,

            "md_identity_verified_verdict": md_identity_verified_verdict,
            "md_policy_followed_verdict": md_policy_followed_verdict,
            "md_outcome_communicated_verdict": md_outcome_communicated_verdict,
            "md_bad_news_handled_verdict": md_bad_news_handled_verdict,
            "md_closing_check_verdict": md_closing_check_verdict,
            "md_respectful_tone_verdict": md_respectful_tone_verdict,
            
            "md_identity_verified_reason": md_identity_verified_reason,
            "md_policy_followed_reason": md_policy_followed_reason,
            "md_outcome_communicated_reason": md_outcome_communicated_reason,
            "md_bad_news_handled_reason": md_bad_news_handled_reason,
            "md_closing_check_reason": md_closing_check_reason,
            "md_respectful_tone_reason": md_respectful_tone_reason,
        })

    return pd.DataFrame(compare_df)


compare_df = load_dataset_to_dataframe(model_data, label_data)

### load to csv
compare_df.to_csv("data/csv/comparedf_2026-10-04_18-42-35.csv", index=False)