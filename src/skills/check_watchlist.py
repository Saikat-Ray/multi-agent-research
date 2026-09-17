"""
Skill: check_watchlist

Deliberately rule-based, not generative — screening decisions need to be
deterministic and auditable, not phrased by an LLM. Does exact match plus
a simple fuzzy match so near-miss aliases (typos, transliterations) still
surface for a human/agent to weigh.
"""

from difflib import SequenceMatcher
from typing import Any, Dict, List


def _similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def check_watchlist(
    entity_name: str,
    watchlist: List[Dict[str, Any]],
    fuzzy_threshold: float = 0.85,
) -> Dict[str, Any]:
    """
    Returns a dict with:
      - status: "match" | "near_miss" | "clear"
      - hits: list of watchlist entries that matched or nearly matched,
              each with a match_score and which name/alias triggered it
    """
    hits = []
    for entry in watchlist:
        candidates = [entry["name"]] + entry.get("aliases", [])
        best_score = max(_similarity(entity_name, c) for c in candidates)
        if best_score == 1.0:
            hits.append({**entry, "match_score": best_score, "match_type": "exact"})
        elif best_score >= fuzzy_threshold:
            hits.append({**entry, "match_score": round(best_score, 3), "match_type": "fuzzy"})

    if any(h["match_type"] == "exact" for h in hits):
        status = "match"
    elif hits:
        status = "near_miss"
    else:
        status = "clear"

    return {"status": status, "hits": hits}
