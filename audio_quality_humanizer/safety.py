"""Safety checks for public-facing project wording."""

from __future__ import annotations

import re


UNSAFE_TERMS = (
    "watermark removal",
    "remove watermark",
    "removes watermarks",
    "removing watermarks",
    "fingerprint removal",
    "remove fingerprint",
    "removes fingerprints",
    "removing fingerprints",
    "detector bypass",
    "bypass detector",
    "bypass detection",
    "evade detection",
    "undetectable",
    "provenance suppression",
    "suppress provenance",
    "origin marker removal",
    "remove origin marker",
    "remove all traces",
    "neutralize watermark",
    "verify removal",
    "watermarks detected and removed",
    "spectral watermark detection",
    "watermark elimination",
)


def assert_no_unsafe_public_claims(text: str) -> list[str]:
    """Return unsafe public-facing feature-claim terms found in text."""

    normalized = re.sub(r"[\s_-]+", " ", text.casefold())
    matched: list[str] = []
    for term in UNSAFE_TERMS:
        pattern = r"\b" + re.escape(term.casefold()).replace(r"\ ", r"\s+") + r"\b"
        if re.search(pattern, normalized):
            matched.append(term)
    return matched
