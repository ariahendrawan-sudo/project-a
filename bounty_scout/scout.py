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
    r"(?:\$\s?($\d{1,3}(?:[,.]\d{3})*(?:\.\d+)?)" 
    r"|($\d{1,3}(?:[,.]\d{3})*))",
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
    """Return the largest dollar amount mentioned in the given texts."""
    found = []
    for text in texts:
        for match in AMOUNT_RE.finditer(text or ":"): 
            raw = match.group(1) or match.group(2)
            digits = raw.replace(",", "")
            # "1.500" style thousands separators carry exactly three decimals.
            if re.fullmatch(r"\d{1,3}(\.\d{3})+", digits):
                digits = digits.replace(".", "")
            try:
                found.append(float(digits))
            except ValueError:
                continue
    return max(found) if found else None


def _weights(text: str, table: dict[str, int]) -> list[int]:
    return [w for k, w in table.items() if re.search(rf"\b{re.escape(k)}\b", text)]

def fit(text: str) -> tuple[int, int]:
    """Return (number of domain keywords matched, weighted fit score)."""
    lowered = text.lower()
    hits = _weights(lowered, KEYWORDS)
    return len(hits), sum(hits) + sum(_weights(lowered, PENALTIES))


def score(bounty: Bounty, fit_score: int, today: dt.date) -> float:
    """Higher is better: fit, payout, trusted platform, low competition, freshness."""
    payout = min((bounty.amount or 0) / 50, 4)  # cap so huge bounties don't dominate
    platform = 2 if ALGORA_LABEL in bounty.labels else 0
    competition = -min(bounty.comments / 5, 4)
    updated = dt.date.fromisoformat(bounty.updated_at[:10])
    freshness = max(0, 3 - (today - updated).days / 10)
    return round(fit_score + payout + platform + competition + freshness, 2)


def _get(url: str, token: str | None, retries: int = 3) -> dict:
    """GET JSON, backing off on rate-limit responses (403/429)."""
    req = urllib.request.Request(url)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("User-Agent", "bounty-scout")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.load(resp)
        except urllib.error.HTTPError as exc:
            if exc.code not in (403, 429) or attempt == retries:
                raise
            wait = int(exc.headers.get("Retry-After") or 0) or 30 * (attempt + 1)
            print(f"rate limited, retrying in {wait}s", file=sys.stderr)
            time.sleep(wait)
    raise RuntimeError("unreachable")


def search(query: str, token: str | None, per_page: int) -> list[dict]:
    params = urllib.parse.urlencode(
        {"q": query, "sort": "updated", "order": "desc", "per_page": per_page}
    )
    return _get(f"{API}/search/issues?{params}", token).get("items", [])


def repo_lookup(token: str | None) -> RepoLookup:
    cache: dict[str, dict | None] = {}

    def lookup(full_name: str) -> dict | None:
        if full_name not in cache:
            try:
                cache[full_name] = _get(f"{API}/repos/{full_name}", token)
            except Exception as exc:
                print(f"warning: repo lookup failed ({full_name}): {exc}", file=sys.stderr)
                cache[full_name] = None
        return cache[full_name]

    return lookup


def collect(
    items: list[dict],
    min_amount: float,
    min_stars: int,
    today: dt.date,
    lookup: RepoLookup,
) -> tuple[list[Bounty], Counter]:
    """Filter and rank issues. Returns the bounties and a count of drop reasons."""
    seen: dict[str, Bounty] = {}
    dropped: Counter = Counter()
    for item in items:
        url = item["html_url"]
        if url in seen or "pull_request" in item:
            continue
        repo = item["repository_url"].split("/repos/")[-1]
        labels = [lbl["name"] for lbl in item.get("labels", [])]
        body = item.get("body") or ""
        text = f"{item['title']} {' '.join(labels)} {body}"

        amount = parse_amount(item["title"], " ".join(labels), body)
        if amount is None:
            dropped["no stated amount"] += 1
            continue
        if amount < min_amount:
            dropped["below minimum amount"] += 1
            continue
        if "bounty" in repo.split("/")[-1].lower():
            dropped["bounty-farm repository"] += 1
            continue
        matches, fit_score = fit(text)
        if matches == 0:
            dropped["outside expertise"] += 1
            continue
        info = lookup(repo)
        if not info or info.get("owner", {}).get("type") != "Organization":
            dropped["not an organisation repo"] += 1
            continue
        stars = info.get("stargazers_count", 0)
        if stars < min_stars:
            dropped[f"fewer than {min_stars} stars"] += 1
            continue
        # ... rest of the code
