"""
Orchestrator: runs the agent pipeline for a single case.

The pipeline is a plain list of agents run in order, with one loop-back
for the challenger's rejection path. This is deliberately simple for the
POC — no dynamic planning agent yet. To add a new agent to the flow,
instantiate it and insert it into `pipeline` below; to add a new agent
type entirely, subclass BaseAgent and drop it in src/agents/.
"""

from typing import Any, Dict, List

from src.agents.base_agent import BaseAgent


class Orchestrator:
    def __init__(
        self,
        retriever: BaseAgent,
        screener: BaseAgent,
        drafter: BaseAgent,
        challenger: BaseAgent,
        max_revisions: int = 2,
    ):
        self.retriever = retriever
        self.screener = screener
        self.drafter = drafter
        self.challenger = challenger
        self.max_revisions = max_revisions

    def run_case(self, case: Dict[str, Any]) -> Dict[str, Any]:
        context: Dict[str, Any] = {"case": case, "trace": []}

        # Parallel in spirit (sequential in this POC — both are cheap
        # and independent, easy to thread/async later).
        context = self.retriever.run(context)
        context = self.screener.run(context)

        for attempt in range(1, self.max_revisions + 1):
            context = self.drafter.run(context)
            context = self.challenger.run(context)
            if context["validation_result"]["passed"]:
                break
        else:
            context["trace"].append(
                f"[orchestrator] max revisions ({self.max_revisions}) reached without passing"
            )

        return context

    def run_batch(self, cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return [self.run_case(c) for c in cases]
