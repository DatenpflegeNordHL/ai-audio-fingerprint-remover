"""Ensure historical experimental scripts do not reappear in the repository root."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

ROOT_FILENAME_TERMS = (
    "watermark",
    "fingerprint",
    "detector",
    "remover",
    "steganography",
    "bypass",
    "evasion",
    "undetectable",
    "recognition_failure",
    "effectiveness_tester",
)

ALLOWED_ROOT_FILES = {
    "README.md",
    "SAFETY.md",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "LICENSE",
    "CLAUDE.md",
    "pyproject.toml",
    "requirements.txt",
    ".gitignore",
}


def find_offending_root_files(root: Path) -> list[Path]:
    """Return root-level files with old unsafe or misleading filename terms."""

    offenders: list[Path] = []
    for path in root.iterdir():
        if not path.is_file() or path.name in ALLOWED_ROOT_FILES:
            continue
        name = path.name.casefold()
        if any(term in name for term in ROOT_FILENAME_TERMS):
            offenders.append(path)
    return sorted(offenders)


def main() -> int:
    offenders = find_offending_root_files(ROOT)
    if offenders:
        print("Root-level historical script filenames found:")
        for path in offenders:
            print(path.relative_to(ROOT))
        print("Historical scripts belong in project_reborn/source_drawer/ with neutral names.")
        return 1

    print("Root cleanliness check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
