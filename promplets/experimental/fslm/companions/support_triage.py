"""Deterministic local bindings for the experimental support-triage machine."""

from __future__ import annotations

import re
from typing import Any

_DOCUMENTS = (
    {
        "title": "Reset a forgotten password",
        "url": "local://docs/account/password-reset",
        "content": (
            "Use the Forgot password link, enter the account email, and follow "
            "the single-use reset link. The link expires after 30 minutes."
        ),
    },
    {
        "title": "Troubleshoot sign-in verification",
        "url": "local://docs/account/sign-in-verification",
        "content": (
            "Check device time, request one fresh code, and use a recovery code "
            "if the authenticator remains unavailable."
        ),
    },
    {
        "title": "Update billing details",
        "url": "local://docs/billing/payment-method",
        "content": (
            "Workspace owners can update a payment method under Settings, "
            "Billing, then Payment method."
        ),
    },
)


def search_docs(query: str, max_results: int = 5) -> dict[str, Any]:
    """Search the bundled demo corpus with deterministic token overlap."""

    normalized_query = query.strip()
    if not normalized_query:
        raise ValueError("query must not be empty")
    limit = max(1, min(int(max_results), len(_DOCUMENTS)))
    terms = set(re.findall(r"[a-z0-9]+", normalized_query.casefold()))

    ranked: list[tuple[int, dict[str, str]]] = []
    for document in _DOCUMENTS:
        haystack = f"{document['title']} {document['content']}".casefold()
        score = sum(term in haystack for term in terms)
        ranked.append((score, document))
    ranked.sort(key=lambda item: (-item[0], item[1]["title"]))
    matches = [document for score, document in ranked if score > 0][:limit]
    return {"query": normalized_query, "results": matches}


def send_message(text: str) -> dict[str, Any]:
    """Return a local delivery receipt without performing network I/O."""

    message = text.strip()
    if not message:
        raise ValueError("text must not be empty")
    return {
        "delivered": True,
        "channel": "local-demo",
        "text": message,
    }


__all__ = ["search_docs", "send_message"]
