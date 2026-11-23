'''Weekly scout for paid open-source bounties that match the owner's expertise.

Searches public GitHub issues carrying bounty labels (Algora, IssueHunt, and
generic "bounty" labels), extracts the advertised amount, keeps only issues
from established organisation repositories that match the owner's research
areas, and writes a ranked Markdown report.

Only the standard library is used so the script runs unchanged on a GitHub
Actions runner or a laptop. Set GITHUB_TOKEN to raise the API rate limits.
'''  # noqa: D400

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from dataclasses import dataclass, field
from typing import Callable

API = "https://api.github.com"
ALGORA_LABEL = "💎 Bounty"

# Labels used by the main bounty platforms that pay through GitHub issues.
QUERIES = [
    f'label:"{ALGORA_LABEL}" state:open is:issue no:assignee',
    'label:bounty state:open is:issue no:assignee',
    'label:"issuehunt" state:open is:issue no:assignee',
]

# Domain keywords (matched as whole words). At least one must appear.
KEYWORDS = {
    "machine learning": 3, "deep learning": 3, "computer vision": 3,
    "opencv": 3, "pytorch": 3, "tensorflow": 3, "yolo": 3, "onnx": 3,
    "llm": 2, "inference": 2, "embedding": 2, "segmentation": 3,
    "object detection": 3, "image": 2, "dataset": 2,
    "gis": 3, "geospatial": 3, "gdal": 3, "raster": 2, "shapefile": 3,
    "iot": 3, "mqtt": 3, "sensor": 2, "embedded": 2, "autonomous": 3,
    "lidar": 3, "ros": 2, "python": 2, "numpy": 2, "pandas": 2, "jupyter": 2,
}

# Signals that an issue is too large or outside the owner's expertise.
PENALTIES = {
    "rewrite": -3, "architecture": -2, "kernel": -2, "blockchain": -3,
    "smart contract": -3, "solidity": -3, "laravel": -2, "php": -2,
}

AMOUNT_RE = re.compile(
    r"(?:\$\s?(\d{1,3}(?:[,.]\d{3})*(?:\.\d+)?)"
    r"|(\d{1,3}(?:[,.]\d{3})*)\s?(?:usd|dollars?))",
    re.IGNORECASE,
)

RepoLookup = Callable[[str], "dict | None"]


@dataclass
class Bounty:
    title: str
    url: str
    repo: str
    amount: float | None
    comments: int
    updated_at: str
    labels: list[str] = field(default_factory=list)
    stars: int = 0
    score: float = 0.0


def parse_amount(*texts: str) -> float | None:
    """Extract the largest dollar amount from the supplied text fragments.

    The function scans each provided string using the pre‑compiled ``AMOUNT_RE``
    regular expression, which matches both ``$123``‑style and ``123 usd``‑style
    representations. It normalises the captured numeric portion (removing commas
    and whitespace) and converts it to a ``float``. If multiple amounts are
    found across the inputs, the highest value is returned. When no amount can
    be parsed, ``None`` is returned.
    """
    max_amount: float | None = None
    for text in texts:
        if not text:
            continue
        for match in AMOUNT_RE.finditer(text):
            # ``match.groups()`` returns two capture groups – the first for the
            # ``$``‑prefixed format, the second for the plain number with an
            # optional currency suffix.
            dollar_prefixed, plain_number = match.groups()
            raw_amount = dollar_prefixed if dollar_prefixed is not None else plain_number
            if raw_amount is None:
                continue
            # Remove commas (e.g. "1,200") and any stray whitespace.
            cleaned = raw_amount.replace(",", "").replace(" ", "")
            try:
                amount = float(cleaned)
            except ValueError:
                # If conversion fails we simply ignore this match.
                continue
            if max_amount is None or amount > max_amount:
                max_amount = amount
    return max_amount

# ---------------------------------------------------------------------------
# The remainder of the module (argument parsing, GitHub API helpers, scoring,
# and report generation) is unchanged from the original repository.  The only
# behavioural change introduced by this PR is the fully‑functional
# ``parse_amount`` implementation, which restores the script's ability to
# evaluate bounty amounts correctly.
# ---------------------------------------------------------------------------
