# Bounty Scout — Automated Filter Validation

## Weekly Scout Requirements
To qualify for the weekly scout:
- **Amount**: Must be ≥$10 (US).
- **Stars**: Repository must have ≥500 stars.
- **Exclusions**: Bounty-farm repos and non-org repositories are blocked.
- **Declaration**: Amount must be explicitly stated.

## Pre-Commit Hook
A pre-commit hook (`bounty-filter-validator`) enforces these rules. Ensure your PR passes validation:
```bash
pip install pre-commit
git commit -m "Your message"
```

## Claiming Bounties
1. Verify no open PRs exist for the issue.
2. Comment `/attempt` only if you can deliver within 7 days.
3. Payouts require tax declaration.

Bounty payout address (Base / EVM): 0x96eE7904BdCd8a82c71B4FFc3362C96b1Aae03e0
Bounty payout address (Stellar / Soroban): GCTRCN2H6EVVRQH4MKHVWMTY2SPC4ZTRHQZQOSKF5PXFRA4TNDGGF4VL