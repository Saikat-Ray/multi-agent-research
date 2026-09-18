"""
Generates synthetic case corpus + watchlist for the POC.

The policy rulebook (policy_rules.json) is intentionally NOT generated
here — it should be hand-written, since it defines what "correct" means
for your eval set. See policy_rules.json for a starter set of rules.

Usage: python generate_synthetic_data.py [--num-cases 150]
"""

import argparse
import json
import random
from pathlib import Path

ENTITY_TYPES = ["individual", "shell_company", "trading_firm", "nonprofit", "fintech_startup"]
RISK_PATTERNS = [
    "structuring deposits just under reporting threshold",
    "rapid fund movement through multiple intermediary accounts",
    "transactions with a jurisdiction on the high-risk list",
    "mismatch between stated business activity and transaction volume",
    "newly opened account with immediate large transfers",
    "round-trip transactions with no clear business purpose",
    "payments to a counterparty with a previously flagged entity",
]
CLEAN_PATTERNS = [
    "routine payroll disbursement consistent with account history",
    "invoice payment matching an existing vendor relationship",
    "recurring subscription billing, stable monthly amount",
    "domestic transfer between the customer's own accounts",
]
DISPOSITIONS = ["approved", "escalated", "declined"]

FIRST_NAMES = ["Aria", "Marcus", "Wen", "Fatima", "Dmitri", "Priya", "Elena", "Kofi", "Liu", "Nadia"]
LAST_NAMES = ["Okafor", "Petrov", "Nakamura", "Reyes", "Singh", "Volkov", "Adeyemi", "Chowdhury"]
COMPANY_WORDS = ["Global", "Apex", "Meridian", "Northgate", "Vantage", "Silverline", "Horizon"]
COMPANY_SUFFIX = ["Holdings", "Trading Co", "Capital", "Partners", "Logistics", "Ventures"]


def random_entity_name(entity_type: str) -> str:
    if entity_type == "individual":
        return f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
    return f"{random.choice(COMPANY_WORDS)} {random.choice(COMPANY_SUFFIX)}"


def generate_case(case_id: int) -> dict:
    entity_type = random.choice(ENTITY_TYPES)
    is_risky = random.random() < 0.55
    pattern = random.choice(RISK_PATTERNS if is_risky else CLEAN_PATTERNS)
    entity_name = random_entity_name(entity_type)

    narrative = (
        f"{entity_name} ({entity_type}) triggered review due to {pattern}. "
        f"Account age: {random.randint(1, 96)} months. "
        f"Transaction amount: ${random.randint(1000, 250000):,}."
    )

    if is_risky:
        disposition = random.choices(
            DISPOSITIONS, weights=[0.15, 0.55, 0.30]
        )[0]
    else:
        disposition = random.choices(
            DISPOSITIONS, weights=[0.80, 0.18, 0.02]
        )[0]

    return {
        "case_id": f"CASE-{case_id:04d}",
        "entity_name": entity_name,
        "entity_type": entity_type,
        "narrative": narrative,
        "disposition": disposition,
    }


def generate_watchlist(num_entries: int = 60) -> list:
    watchlist = []
    for i in range(num_entries):
        name = random_entity_name(random.choice(["individual", "shell_company"]))
        aliases = []
        if random.random() < 0.3:
            # near-miss alias: swap a couple characters
            parts = list(name)
            if len(parts) > 3:
                a, b = random.sample(range(len(parts)), 2)
                parts[a], parts[b] = parts[b], parts[a]
            aliases.append("".join(parts))
        watchlist.append(
            {
                "watchlist_id": f"WL-{i:04d}",
                "name": name,
                "aliases": aliases,
                "risk_code": random.choice(["SANCTIONS", "PEP", "ADVERSE_MEDIA"]),
            }
        )
    return watchlist


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--num-cases", type=int, default=150)
    parser.add_argument("--num-watchlist", type=int, default=60)
    parser.add_argument("--eval-holdout", type=int, default=20)
    args = parser.parse_args()

    random.seed(43)

    all_cases = [generate_case(i) for i in range(1, args.num_cases + 1)]
    eval_set = all_cases[: args.eval_holdout]
    corpus = all_cases[args.eval_holdout :]
    watchlist = generate_watchlist(args.num_watchlist)

    out_dir = Path(__file__).parent
    (out_dir / "cases_corpus.json").write_text(json.dumps(corpus, indent=2))
    (out_dir / "eval_set.json").write_text(json.dumps(eval_set, indent=2))
    (out_dir / "watchlist.json").write_text(json.dumps(watchlist, indent=2))

    print(f"Wrote {len(corpus)} corpus cases -> cases_corpus.json")
    print(f"Wrote {len(eval_set)} eval cases -> eval_set.json")
    print(f"Wrote {len(watchlist)} watchlist entries -> watchlist.json")


if __name__ == "__main__":
    main()
