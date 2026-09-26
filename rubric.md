# ABCD Rubric v0.1

Every Criterion except `respectful_tone` is derived from a recurring pattern in `data/guidelines.json`. The rubric states the
question; the specific rule comes from the Policy Passage for the Conversation's Subflow, supplied
alongside it. PASS always means good Agent behaviour.

"The guidelines" below always means the Policy Passage for this Conversation's Subflow.

## identity_verified
**Question:** Did the agent verify the customer with the details this subflow's guidelines require, before acting on the account?
**Pass:** Collected the details the subflow requires (e.g. username + email + order ID, or 3 of 4 identity items) and ran verification before any account change or disclosure of account information. Also PASS if the customer could not provide the details and the agent did not proceed.
**Fail:** Skipped verification, accepted fewer or different details than required, or acted before verifying.
**N/A:** The subflow's guidelines contain no [Verify Identity] or [Validate Purchase] step. Pulling up the account by name alone is not verification.
**Source:** [Verify Identity] / [Validate Purchase] steps (33 of 55 subflows).

## policy_followed
**Question:** Did the agent make the decision the guidelines require for this customer's situation (membership level, dates, receipt, packaging, shipping status)?
**Pass:** The outcome matches the guideline rule, and the agent checked the conditions the rule depends on before deciding. Covers amounts (e.g. refund totals) and the order in which things may be offered (e.g. a promo code only if the customer keeps pushing).
**Fail:** Gave something not allowed, refused something allowed, or refused without checking every route the rule allows (e.g. checked the date but not receipt or packaging).
**N/A:** The subflow has no rule that depends on the customer's situation, or the conversation ended before a decision was reached.
**Note:** Helpful extras the guidelines don't mention (e.g. offering to escalate) are not a FAIL, unless they grant something the rule forbids.
**Source:** Membership, date, and status rules (19 of 55 subflows).

## outcome_communicated
**Question:** After acting or finding the answer, did the agent tell the customer the result in plain words?
**Pass:** The customer was told what was done or what the answer is (e.g. "your order has been updated", the new password, the refund status).
**Fail:** The agent acted or found the answer but did not tell the customer, or only pasted a system response without explaining it.
**N/A:** The conversation ended before any action or answer was reached.
**Source:** "Tell the customer…", "Share the password…", "Explain the details in natural language…", "Give instructions in your own words without copy/paste" (~47 of 55 subflows).

## bad_news_handled
**Question:** When the agent had to refuse or give an unfavourable result, did they both apologize and explain why?
**Pass:** Both an apology and the reason were given before the conversation ended.
**Fail:** Refused or gave bad news without an apology, without a reason, or without both.
**N/A:** No refusal or unfavourable result in this conversation.
**Source:** "If the customer cannot return, apologize and explain the problem"; "If nothing works, just apologize" (~20 of 55 subflows).

## closing_check
**Question:** Did the agent ask whether the customer needs anything else, after the main request was handled?
**Pass:** Asked at any point after the main request was handled, even if the conversation continued afterwards.
**Fail:** The conversation ended without the agent asking.
**N/A:** The customer left, or said they needed nothing else, before the agent had a chance to ask.
**Source:** "As always, wrap up by nicely asking if the customer needs any further assistance." Treated as applying to every subflow because of "as always" / "as usual".

## respectful_tone
**Question:** Was the agent polite, respectful, and professional throughout the conversation?
**Pass:** Polite and professional throughout.
**Fail:** Rude, sarcastic, dismissive, or ignored the customer at any point.
**N/A:** Always applies; never NOT_APPLICABLE.
**Source:** Not derived from the guidelines. Added because tone is a standard QA check that the guidelines assume rather than state. Real FAILs are expected to be very rare in ABCD, so this Criterion relies on Synthetic Cases.
