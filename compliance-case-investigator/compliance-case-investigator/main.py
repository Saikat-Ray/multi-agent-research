"""
Demo entry point. Runs the full agent pipeline against the eval set and
prints each case's outcome.

Prereqs:
  1. pip install -r requirements.txt
  2. export ANTHROPIC_API_KEY=your_key
  3. python data/generate_synthetic_data.py   (creates the JSON data files)
  4. python main.py
"""

import json
from pathlib import Path
import os
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file

from src.agents.challenger_agent import ChallengerAgent
from src.agents.drafting_agent import DraftingAgent
from src.agents.history_retriever import HistoryRetrieverAgent
from src.agents.screening_agent import ScreeningAgent
from src.orchestrator import Orchestrator

DATA_DIR = Path(__file__).parent / "data"


def load_json(filename):
    return json.loads((DATA_DIR / filename).read_text())


def main():
    case_corpus = load_json("cases_corpus.json")
    watchlist = load_json("watchlist.json")
    policy_rules = load_json("policy_rules.json")
    eval_cases = load_json("eval_set.json")

    orchestrator = Orchestrator(
        retriever=HistoryRetrieverAgent(case_corpus=case_corpus, top_k=3),
        screener=ScreeningAgent(watchlist=watchlist),
        drafter=DraftingAgent(),
        challenger=ChallengerAgent(policy_rules=policy_rules),
        max_revisions=2,
    )

    # Run on the first 3 eval cases as a quick smoke test.
    for case in eval_cases[:3]:
        print("=" * 70)
        print(f"Case: {case['case_id']} — {case['entity_name']}")
        result = orchestrator.run_case(case)

        print(f"\nMemo:\n{result['memo']}")
        print(f"\nValidation passed: {result['validation_result']['passed']}")
        print(f"Known historical disposition (for comparison): {case['disposition']}")
        print("\nTrace:")
        for line in result["trace"]:
            print(f"  {line}")
        print()


if __name__ == "__main__":
    main()
