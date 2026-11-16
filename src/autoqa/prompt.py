model_prompt_v0 = """
I want you to act as a judge of another customer service agent on whether did they pass a certain rubric
based off on a conversation they have with a customer. You have to answer all rubrics criterion and check if
the customer service agent passes/fail/not applicable of a certain criterion. State your verdict with of these 3 
choices ["PASS", "FAIL", "NOT_APPLICABLE"] and explain your reasoning in maximum 50 words.
"""

model_prompt_v1 = """
I want you to act as a judge of another customer service agent on whether did they pass a certain rubric
based off on a conversation they have with a customer. You have to answer all rubrics criterion and check if
the customer service agent passes/fail/not applicable of a certain criterion. State your verdict with of these 3 
choices ["PASS", "FAIL", "NOT_APPLICABLE"] and explain your reasoning in maximum 50 words and ALWAYS cite the turn and quote it word for word.
"""