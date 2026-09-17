"""
Skill: draft_memo

The one generative step in the pipeline that produces the actual
recommendation. Grounded explicitly in the retrieved similar cases and
the screening result so the memo cites its reasoning rather than
free-associating.
"""
import os

from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file
from typing import Any, Dict, List

import anthropic

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from env

MEMO_SYSTEM_PROMPT = """You are a compliance analyst assistant. Given a \
case, similar historical cases, and a watchlist screening result, draft a \
short disposition memo. Structure it as:

Recommendation: <approve | escalate | decline>
Reasoning: <2-4 sentences, referencing specific similar cases and the \
screening result by name>

Be conservative: if the screening result is "match" or "near_miss", lean \
toward escalate/decline unless the similar cases strongly justify approval.
"""


def draft_memo(
    case: Dict[str, Any],
    similar_cases: List[Dict[str, Any]],
    screening_result: Dict[str, Any],
    revision_feedback: str = "",
) -> str:
    similar_cases_text = "\n".join(
        f"- Case {c['case_id']} ({c['disposition']}, similarity "
        f"{c['similarity_score']}): {c['narrative'][:150]}"
        for c in similar_cases
    ) or "None found."

    user_prompt = f"""Case under review:
ID: {case['case_id']}
Entity: {case['entity_name']}
Narrative: {case['narrative']}

Similar historical cases:
{similar_cases_text}

Screening result: {screening_result['status']}
Screening hits: {screening_result['hits']}
"""

    if revision_feedback:
        user_prompt += f"\nA prior draft was rejected. Feedback to address:\n{revision_feedback}\n"

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=400,
        system=MEMO_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    )
    return response.content[0].text
