from typing import Any, Dict

from src.agents.base_agent import BaseAgent
from src.skills.validate_against_policy import validate_against_policy


class ChallengerAgent(BaseAgent):
    name = "challenger_agent"

    def __init__(self, policy_rules):
        self.policy_rules = policy_rules

    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        result = validate_against_policy(context["memo"], self.policy_rules)
        context["validation_result"] = result
        if result["passed"]:
            self.log(context, "memo passed policy validation")
        else:
            context["challenger_feedback"] = result["raw_response"]
            self.log(context, "memo rejected, feedback recorded")
        return context
