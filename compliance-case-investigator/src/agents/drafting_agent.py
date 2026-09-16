from typing import Any, Dict

from src.agents.base_agent import BaseAgent
from src.skills.draft_memo import draft_memo


class DraftingAgent(BaseAgent):
    name = "drafting_agent"

    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        feedback = context.get("challenger_feedback", "")
        memo = draft_memo(
            case=context["case"],
            similar_cases=context.get("similar_cases", []),
            screening_result=context.get(
                "screening_result", {"status": "unknown", "hits": []}
            ),
            revision_feedback=feedback,
        )
        context["memo"] = memo
        context.setdefault("draft_count", 0)
        context["draft_count"] += 1
        self.log(context, f"drafted memo (revision {context['draft_count']})")
        return context
