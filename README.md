# Bounty Tracker

## Filter Validation

Run the filter validation script to automatically check bounty eligibility:

```bash
npm install
npm run validate
```

### Input Format
The script expects a JSON array of bounties with the following structure:
```json
[
  {
    "amount": 50,
    "stars": 1200,
    "repository": "example-repo",
    "org": "example-org",
    "expertise": ["backend", "frontend"],
    "user": "contributor"
  }
]
```

### Output
Generates a report with validation results for each bounty.

**Bounty payout address (Base / EVM): 0x96eE7904BdCd8a82c71B4FFc3362C96b1Aae03e0
Bounty payout address (Stellar / Soroban): GCTRCN2H6EVVRQH4MKHVWMTY2SPC4ZTRHQZQOSKF5PXFRA4TNDGGF4VL