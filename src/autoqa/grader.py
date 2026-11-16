import os
import json

import openai
from dotenv import load_dotenv
from datetime import datetime
from langsmith import traceable
from langsmith.wrappers import wrap_openai

from autoqa.helper import load_conversation, load_guideline, load_label, load_rubric, load_input_prompt
from autoqa.prompt import model_prompt_v0, model_prompt_v1
from typing import TypedDict, Literal, Annotated
from pydantic import ConfigDict, with_config, Field


load_dotenv()
client = wrap_openai(openai.Client())

# One criterion
@with_config(ConfigDict(extra="forbid"))
class ResponseOutput(TypedDict):
    verdict: Literal["PASS", "FAIL", "NOT_APPLICABLE"]
    reason: str
    evidence: Annotated[str, Field(description="Exact quote and turn number of the conversation to support the reason and verdict")]


# All six criterion
@with_config(ConfigDict(extra="forbid"))
class CriterionOutput(TypedDict):
    identity_verified: ResponseOutput
    policy_followed: ResponseOutput
    outcome_communicated: ResponseOutput
    bad_news_handled: ResponseOutput
    closing_check: ResponseOutput
    respectful_tone: ResponseOutput


@traceable(name="Model Grading Pipeline")
def grading_per_conversation(RAW_PATH, convo_id, GUIDELINES_PATH, RUBRIC_PATH):
    # load conversation from conversation id
    conversation, flow, subflow = load_conversation(RAW_PATH=RAW_PATH, convo_id=convo_id)

    # load guidelines from conversation id
    guideline = load_guideline(GUIDELINES_PATH=GUIDELINES_PATH, flow=flow, subflow=subflow)

    # load rubric
    _, criteria = load_rubric(RUBRIC_PATH=RUBRIC_PATH)

    input_prompt = load_input_prompt(conversation, guideline, criteria)

    model_prompt = model_prompt_v1 # change variable output_list in model_grading func

    # Calling the model
    response = client.responses.parse(
        model=os.environ["OPENAI_MODEL"],
        input=input_prompt,
        instructions=model_prompt,
        text_format=CriterionOutput
    )

    output = response.output_parsed

    return output


def model_grading(LABELS_PATH, RAW_PATH, RUBRIC_PATH, GUIDELINES_PATH, OUTPUT_PATH):
    """
    Upload a graded file to be compared to the golden dataset.
    """
    ### GRADING PIPELINE ###
    response_list = []

    # Load label from golden set
    grouping_label = load_label(LABELS_PATH=LABELS_PATH)

    # looping conversation id 
    for convo_id in grouping_label:

        output = grading_per_conversation(RAW_PATH=RAW_PATH, convo_id=convo_id, GUIDELINES_PATH=GUIDELINES_PATH, RUBRIC_PATH=RUBRIC_PATH)

        # include metadata later
        response_list.append({"convo_id": convo_id, "grade": output})

        print(f"Finished conversation id:{convo_id}.")

    output_list = {"metadata": {"model_type": os.environ["OPENAI_MODEL"], "prompt_version": "model_prompt_v1"}, "results" : response_list}

    # Upload to a file to be inspect/examined
    output_file_path = f"{OUTPUT_PATH}/{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.json"
    
    with open(output_file_path, "w") as f:
        json.dump(output_list, f, indent=2)
    
    return output_file_path
