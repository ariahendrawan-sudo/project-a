"""Utility functions for scouting GitHub bounties.

This module provides a single public function, :func:`filter_bounties`, which
filters a list of bounty dictionaries according to configurable criteria.
It is deliberately defensive – missing or malformed fields are ignored
instead of raising exceptions, ensuring the function can be used safely in
automation pipelines.
"""

from __future__ import annotations

from typing import Any, Dict, List, Mapping


def _safe_float(value: Any) -> float | None:
    """Attempt to coerce *value* to a ``float``.

    Returns ``None`` if conversion fails. This helper allows the main filter
    logic to treat numeric strings (e.g. ``"50"``) as valid amounts while
    gracefully handling unexpected types.
    """
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def filter_bounties(
    bounties: List[Mapping[str, Any]] | None,
    *,
    min_amount: float = 10.0,
    min_stars: int = 500,
) -> List[Dict[str, Any]]:
    """Return bounties that satisfy the given thresholds.

    Parameters
    ----------
    bounties:
        An iterable of mapping objects representing bounty metadata. ``None``
        or an empty list results in an empty list being returned.
    min_amount:
        Minimum monetary amount (inclusive) a bounty must have to be kept.
    min_stars:
        Minimum repository star count (inclusive) required.

    The function is tolerant of missing keys – entries lacking ``amount`` or
    ``stars`` are simply excluded from the result rather than causing a crash.
    """
    if not bounties:
        return []

    filtered: List[Dict[str, Any]] = []
    for bounty in bounties:
        # Ensure we are working with a dict‑like object.
        if not isinstance(bounty, Mapping):
            continue

        # Extract and validate amount.
        raw_amount = bounty.get("amount")
        amount = _safe_float(raw_amount)
        if amount is None or amount < min_amount:
            continue

        # Extract and validate star count.
        raw_stars = bounty.get("stars")
        stars = _safe_float(raw_stars)
        if stars is None or int(stars) < min_stars:
            continue

        # All checks passed – copy the original mapping to a plain dict.
        filtered.append(dict(bounty))

    return filtered
