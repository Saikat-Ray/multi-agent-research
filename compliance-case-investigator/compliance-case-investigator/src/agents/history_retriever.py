from typing import Any, Dict

from src.agents.base_agent import BaseAgent
from src.skills.retrieve_similar_cases import retrieve_similar_cases


class HistoryRetrieverAgent(BaseAgent):
    name = "history_retriever"

    def __init__(self, case_corpus, top_k: int = 3):
        self.case_corpus = case_corpus
        self.top_k = top_k

    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        case = context["case"]
        similar = retrieve_similar_cases(
            query_narrative=case["narrative"],
            case_corpus=self.case_corpus,
            top_k=self.top_k,
        )
        context["similar_cases"] = similar
        self.log(context, f"found {len(similar)} similar cases")
        return context
