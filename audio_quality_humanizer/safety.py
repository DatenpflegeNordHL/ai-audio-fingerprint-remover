"""Safety checks for public-facing project wording."""

from __future__ import annotations

import re


_UNSAFE_TERM_PARTS = (
    ("watermark", "removal"),
    ("remove", "watermark"),
    ("removes", "watermarks"),
    ("removing", "watermarks"),
    ("fingerprint", "removal"),
    ("remove", "fingerprint"),
    ("removes", "fingerprints"),
    ("removing", "fingerprints"),
    ("detector", "bypass"),
    ("bypass", "detector"),
    ("bypass", "detectors"),
    ("bypass", "detection"),
    ("evade", "detection"),
    ("un" + "detectable",),
    ("provenance", "suppression"),
    ("suppress", "provenance"),
    ("origin", "marker", "removal"),
    ("remove", "origin", "marker"),
    ("remove", "all", "traces"),
    ("neutralize", "watermark"),
    ("verify", "removal"),
    ("watermarks", "detected", "and", "removed"),
    ("spectral", "watermark", "detection"),
    ("watermark", "elimination"),
)

UNSAFE_TERMS = tuple(" ".join(parts) for parts in _UNSAFE_TERM_PARTS)


def assert_no_unsafe_public_claims(text: str) -> list[str]:
    """Return unsafe public-facing feature-claim terms found in text."""

    normalized = re.sub(r"[\s_-]+", " ", text.casefold())
    matched: list[str] = []
    for term in UNSAFE_TERMS:
        pattern = r"\b" + re.escape(term.casefold()).replace(r"\ ", r"\s+") + r"\b"
        matches = list(re.finditer(pattern, normalized))
        if any(not _is_safety_boundary_denial(normalized, match.start()) for match in matches):
            matched.append(term)
    return matched


def _is_safety_boundary_denial(text: str, match_start: int) -> bool:
    prefix = text[max(0, match_start - 60) : match_start]
    prefix = re.split(r"[.!?\n;:]", prefix)[-1]
    denial_markers = (
        "does not ",
        "do not ",
        "doesn't ",
        "not ",
        "never ",
        "must never ",
        "must not ",
        "no ",
        "does it make ",
    )
    return any(marker in prefix for marker in denial_markers)
