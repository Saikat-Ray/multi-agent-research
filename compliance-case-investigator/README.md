# Compliance Case Investigator — Multi-Agent POC

A pipeline of agents that investigates a compliance case: retrieves similar
historical cases, screens the entity against a watchlist, drafts a
disposition memo, and challenges that memo against a policy rulebook before
it's considered final.

## Structure

```
compliance-case-investigator/
├── main.py                        # demo entry point
├── requirements.txt
├── data/
│   ├── generate_synthetic_data.py # generates cases_corpus.json, eval_set.json, watchlist.json
│   ├── policy_rules.json          # hand-written rulebook (not synthesized)
│   ├── cases_corpus.json          # generated
│   ├── eval_set.json              # generated (held-out, for measuring accuracy)
│   └── watchlist.json             # generated
└── src/
    ├── orchestrator.py            # runs the pipeline for a case
    ├── agents/
    │   ├── base_agent.py          # interface every agent implements
    │   ├── history_retriever.py
    │   ├── screening_agent.py
    │   ├── drafting_agent.py
    │   └── challenger_agent.py
    └── skills/
        ├── retrieve_similar_cases.py   # TF-IDF similarity (swap for pgVector/Chroma later)
        ├── check_watchlist.py          # deterministic exact + fuzzy match
        ├── draft_memo.py               # LLM call, grounded in retrieval + screening
        └── validate_against_policy.py  # LLM call, checked against policy_rules.json
```

## Running it

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=your_key
python data/generate_synthetic_data.py
python main.py
```

## How the pipeline works

1. **History retriever** and **screener** run against the case (independent
   of each other).
2. **Drafter** writes a disposition memo grounded in both outputs.
3. **Challenger** checks the memo against `policy_rules.json`. If it fails,
   the drafter gets the feedback and retries (up to `max_revisions`).

## Plugging in a new agent

1. Subclass `BaseAgent` in `src/agents/`, implement `run(context)`.
2. Write any new skill functions it needs in `src/skills/` — plain
   functions, no framework lock-in.
3. Instantiate it in `main.py` (or wherever you build the `Orchestrator`)
   and insert it into the pipeline in `src/orchestrator.py`.

Skills are intentionally decoupled from agents — any agent can call any
skill function. That's what lets you reassign responsibilities later
(e.g. give the challenger its own retrieval skill) without rewriting agents.

## Next steps once the smoke test works

- Run `main.py` against the full `eval_set.json` and score recommendation
  vs. the known `disposition` field to get a rough accuracy number.
- Swap `retrieve_similar_cases` for a real vector store once corpus size
  makes TF-IDF too coarse.
- Consider making the orchestrator's pipeline dynamic (a planner agent
  choosing which agents to call) only after the fixed pipeline is solid —
  it adds a new failure mode (bad plans) that's easier to debug once the
  agents themselves are trustworthy.
