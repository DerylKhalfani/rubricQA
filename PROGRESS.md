# 25-26 September 2026
- Cloned ABCD dataset and its guidelines.
- created inspect.ipynb to inspect the dataset by converting the JSON file to DataFrame.
- Created rubric.md as a base version for the grader.

# 2-4 October 2026
- created helper.py
- load_conversation, load_rubric, load_label, load_guideline to be put as a prompt to the model

# 4 October 2026
- Made a simple grader.py
- Problems encountered:
    - load_rubric function load rubric in `list[dict]` format not on markdown.
        - solution: made load_rubric_into_text function
    - in order for `TypedDict` class to be recognized by openAI api use @with_config as it only works with Pydantic
- Reminder:
    - Use logging
    - create more detailed metadata for the json file output by model
    - make the model to have grounded answer e.g. explicitly state which turn in the reasoning for their stance on their verdict.

# 5 October 2026
- Building the comparison.py
- load the golden and model dataset into a dataframe then build the script to compare the result
- Problems encountered:
    -
- Reminder:
    -

# 6 October 2026
- 
- Problems encountered:
    -
- Reminder:
    -

# 7 October 2026
- 
- Problems encountered:
    -
- Reminder:
    -