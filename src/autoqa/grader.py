import json
from pathlib import Path
from autoqa.guidelines import GUIDELINES_PATH, SUBFLOW_MAP, guideline_key

### Grade v.0
ROOT = Path(__file__).resolve().parents[2]
LABELS_PATH = ROOT / "data" / "golden" / "labels_v0.1.jsonl"
RAW_PATH = ROOT / "data" / "abcd_pretty.json"


def load_label(LABELS_PATH: str) -> dict[dict[dict]]:
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

    return grouping_label


def load_conversation(RAW_PATH: str, convo_id: int):
    # loading the conversation from raw file
    with open(RAW_PATH) as f:
        raw_data = json.load(f)

        conversation = ""
        # raw_data has train, dev, test set

        # load the whole file every time it runs, find a way to reduce it!!
        for split, set_value in raw_data.items():
            # print(split)
            # print(type(set_value))
            for convo in set_value:

                if convo["convo_id"] == convo_id:
                    conversation += f"==Conversation: {convo_id}==\n"

                    for speaker, text in convo["original"]:
                        conversation += f"{speaker}: {text}\n"

                    flow = convo["scenario"]["flow"]
                    subflow = convo["scenario"]["subflow"]

                    return conversation, flow, subflow

        raise ValueError(f"{convo_id} convo id is not found")


def load_guideline(GUIDELINES_PATH: str, flow: str, subflow: str):

    key = guideline_key(flow,subflow)
    if key is None:
        raise ValueError(f"No guideline passage for {flow} / {subflow}")
    flow, subflow = key

    with open(GUIDELINES_PATH) as f:
        guidelines = json.load(f)

    actions_instructions = guidelines[flow]["subflows"][subflow]
    actions = actions_instructions["actions"]
    instructions = actions_instructions["instructions"]

    # print(actions)
    # print("\n")
    # print(instructions)
    actions_instructions_prompt = f"== Guidelines: {flow} / {subflow} ==\n"
    instruction_prompt = "\n".join(instructions)
    actions_instructions_prompt += f"{instruction_prompt}\n\nSteps:\n"

    action_prompt = ""
    for index, action in enumerate(actions, 1):
        if action["button"] == "N/A":
            button_text = ""
        else:
            button_text = f"[{action['button']}] "

        text_text = action["text"]

        # empty list is falsy, so steps without subtext add nothing
        if action["subtext"]:
            separator = "\n  - "
            subtext_text = separator + separator.join(action["subtext"])
        else:
            subtext_text = ""

        action_prompt += f"{index}. {button_text}{text_text}{subtext_text}\n"

    actions_instructions_prompt += action_prompt

    return actions_instructions_prompt


conversation, flow, subflow = load_conversation(RAW_PATH, 6689)

# print(conversation)
# print(flow)
# print(subflow)

actions_instructions_prompt = load_guideline(GUIDELINES_PATH, flow, subflow)

print(actions_instructions_prompt)
