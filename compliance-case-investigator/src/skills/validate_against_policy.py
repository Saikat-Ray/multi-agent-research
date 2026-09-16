"""
Skill: validate_against_policy

Checks a drafted memo against a small hand-written rulebook. Kept as an
LLM call (rules are expressed in natural language, matching is fuzzy by
nature) but the rulebook itself is deterministic and human-authored —
see data/policy_rules.json. Don't synthesize the rulebook; it defines
what "correct" means for the eval set.
"""

from typing import Any, Dict, List

import anthropic

client = anthropic.Anthropic()

VALIDATOR_SYSTEM_PROMPT = """You are a compliance policy auditor. Given a \
disposition memo and a set of policy rules, check whether the memo's \
recommendation and reasoning satisfy every applicable rule.

Respond in this exact format:
Verdict: <pass | fail>
Issues: <bullet list of any rule violations or missing justification, or \
"None" if verdict is pass>
"""


def validate_against_policy(
    memo_text: str, policy_rules: List[Dict[str, Any]]
) -> Dict[str, Any]:
    rules_text = "\n".join(
        f"- {r['rule_id']}: IF {r['condition']} THEN {r['required_action']}"
        for r in policy_rules
    )

    user_prompt = f"""Policy rules:
{rules_text}

Memo to audit:
{memo_text}
"""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=300,
        system=VALIDATOR_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    )
    text = response.content[0].text
    passed = text.strip().lower().startswith("verdict: pass")
    return {"passed": passed, "raw_response": text}
