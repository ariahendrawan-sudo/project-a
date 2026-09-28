#!/usr/bin/env python3
"""
Validates bounties against weekly scout filters.
"""
import re
import sys
from typing import Dict, List

MIN_AMOUNT = 10
MIN_STARS = 500
EXCLUDED_REPOS = ["bounty-farm", "bounty-hunt"]


def validate_bounty(bounty: Dict) -> bool:
    """Check if bounty passes all filters."""
    # Amount validation
    if "amount" not in bounty or not isinstance(bounty["amount"], (int, float)):
        print("❌ Error: Bounty must declare a valid amount.", file=sys.stderr)
        return False
    if bounty["amount"] < MIN_AMOUNT:
        print(f"❌ Error: Amount must be ≥${MIN_AMOUNT}.", file=sys.stderr)
        return False

    # Stars validation
    if "stars" not in bounty or bounty["stars"] < MIN_STARS:
        print(f"❌ Error: Repository must have ≥{MIN_STARS} stars.", file=sys.stderr)
        return False

    # Repository type validation
    if "repo" not in bounty:
        print("❌ Error: Repository field missing.", file=sys.stderr)
        return False
    repo_name = bounty["repo"].lower()
    if any(excluded in repo_name for excluded in EXCLUDED_REPOS):
        print(f"❌ Error: Repository '{bounty['repo']}' is excluded.", file=sys.stderr)
        return False

    # Organization validation
    if "org" not in bounty or not bounty["org"]:
        print("❌ Error: Bounty must be from an organization.", file=sys.stderr)
        return False

    return True


def validate_bounties(bounties: List[Dict]) -> bool:
    """Validate a list of bounties."""
    for bounty in bounties:
        if not validate_bounty(bounty):
            return False
    return True


if __name__ == "__main__":
    import json
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--bounties", type=str, required=True, help="Path to JSON file with bounties")
    args = parser.parse_args()
    
    with open(args.bounties) as f:
        bounties = json.load(f)
    
    if not validate_bounties(bounties):
        sys.exit(1)
    print("✅ All bounties pass filters.")