from typing import Any, Dict

from src.agents.base_agent import BaseAgent
from src.skills.check_watchlist import check_watchlist


class ScreeningAgent(BaseAgent):
    name = "screening_agent"

    def __init__(self, watchlist):
        self.watchlist = watchlist

    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        case = context["case"]
        result = check_watchlist(
            entity_name=case["entity_name"], watchlist=self.watchlist
        )
        context["screening_result"] = result
        self.log(context, f"screening status: {result['status']}")
        return context
