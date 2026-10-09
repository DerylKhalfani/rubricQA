import json
import re
from pathlib import Path
from autoqa.guidelines import GUIDELINES_PATH, guideline_key

### Grade v.0
ROOT = Path(__file__).resolve().parents[2]
LABELS_PATH = ROOT / "data" / "golden" / "labels_v0.1.jsonl"
RAW_PATH = ROOT / "data" / "abcd_pretty.json"
RUBRIC_PATH = ROOT / "rubric.md"
GUIDELINES_PATH = ROOT / "data" / "guidelines.json"

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


def load_conversation(RAW_PATH: str, convo_id: int) -> tuple[str, str, str]:
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
                    conversation += f"==== Conversation: {convo_id} ====\n"

                    for speaker, text in convo["original"]:
                        conversation += f"{speaker}: {text}\n"

                    flow = convo["scenario"]["flow"]
                    subflow = convo["scenario"]["subflow"]

                    return conversation, flow, subflow

        raise ValueError(f"{convo_id} convo id is not found")


def load_guideline(GUIDELINES_PATH: str, flow: str, subflow: str) -> str:

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
    actions_instructions_prompt = f"==== Guidelines: {flow} / {subflow} ====\n"
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


def load_rubric() -> tuple[str, list[dict]]:
    text = RUBRIC_PATH.read_text()
    m = re.search(r"^# .*?(v\d+(?:\.\d+)*)\s*$", text, re.M)
    if not m:
        raise SystemExit("rubric.md needs a title with a version, e.g. '# ABCD Rubric v0.1'")
    criteria = []
    for block in re.split(r"^## ", text, flags=re.M)[1:]:
        name = block.split("\n", 1)[0].strip()
        question = re.search(r"\*\*Question:\*\*\s*(.+)", block)
        pass_body = re.search(r"\*\*Pass:\*\*\s*(.+)", block)
        fail_body = re.search(r"\*\*Fail:\*\*\s*(.+)", block)
        na_body = re.search(r"\*\*N/A:\*\*\s*(.+)", block)
        note_body = re.search(r"\*\*Note:\*\*\s*(.+)", block)

        criteria.append({
            "name": name,
            "question": question.group(1).strip() if question else "",
            "pass": pass_body.group(1) if pass_body else "",
            "fail": fail_body.group(1) if fail_body else "",
            "na": na_body.group(1) if na_body else "",
            "note": note_body.group(1).strip() if note_body else ""
        })
    return m.group(1), criteria


RUBRIC_LABELS = {
    "name": "Criterion",
    "question": "Question",
    "pass": "Pass",
    "fail": "Fail",
    "na": "N/A",
    "note": "Note",
}


def load_rubric_into_text(rubrics: list[dict]) -> str:

    rubric_text = "==== Rubric ====\n"


    for rubric in rubrics:
        for key, text in rubric.items():

            # skip empty fields, e.g. criteria without a note
            if text == "":
                continue

            rubric_text += f"{RUBRIC_LABELS[key]}: {text}\n"
        rubric_text += "\n"

    return rubric_text


def load_input_prompt(conversation: str, guideline: str, rubric: str):

    input_prompt = f"{conversation}\n{guideline}\n{load_rubric_into_text(rubric)}"

    return input_prompt


if __name__ == "__main__":

    conversation, flow, subflow = load_conversation(RAW_PATH, 6689)

    # print(conversation)
    # print(flow)
    # print(subflow)

    guideline = load_guideline(GUIDELINES_PATH, flow, subflow)

    # print(actions_instructions_prompt)
    # test, test1 = load_rubric()

    # print(test1[0])
    # print("\n")

    _, rubric = load_rubric()

    prompt = load_input_prompt(conversation, guideline, rubric)
    print(prompt)
