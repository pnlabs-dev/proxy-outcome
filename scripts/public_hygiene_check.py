from __future__ import annotations

import pathlib
import re
import sys


ROOT = pathlib.Path(__file__).resolve().parents[1]
TEXT_SUFFIXES = {".md", ".py", ".toml", ".yml", ".yaml", ".txt", ".json"}

# The checker reports only the rule and file path. It never prints a matched
# value, which avoids turning CI logs into a secondary secret-disclosure path.
# Rules intentionally use vendor-neutral labels and generic token shapes so the
# public scanner is not coupled to, or branded around, any external provider.
RULES: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("private-key material", re.compile("-----BEGIN " + r"(?:RSA |EC |OPENSSH )?PRIVATE KEY-----")),
    ("cloud access-key shaped token", re.compile(r"\b[A-Z]{4}[0-9A-Z]{16}\b")),
    (
        "source-control/service token shaped value",
        re.compile(
            r"\b(?:[a-z]{2,8}_[A-Za-z0-9]{20,}|"
            r"[A-Za-z]{5,12}_[A-Za-z]{3}_[A-Za-z0-9_]{20,})\b"
        ),
    ),
    ("API key shaped value", re.compile(r"\bsk-(?:[A-Za-z0-9_-]{3,}-)?[A-Za-z0-9_-]{20,}\b")),
    (
        "credential-bearing proxy/HTTP URL",
        re.compile(r"(?:https?|socks5?)://[^\s/:@]+:[^\s/@]+@", re.IGNORECASE),
    ),
    (
        "private IPv4 literal",
        re.compile(
            r"\b(?:10\.\d{1,3}\.\d{1,3}\.\d{1,3}|"
            r"192\.168\.\d{1,3}\.\d{1,3}|"
            r"172\.(?:1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3})\b"
        ),
    ),
    (
        "email address",
        re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE),
    ),
)

BANNED_FILENAMES = {
    ".env",
    "id_rsa",
    "id_ed25519",
    "credentials.json",
    "secrets.json",
}


def iter_text_files() -> list[pathlib.Path]:
    files: list[pathlib.Path] = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if ".git" in path.parts:
            continue
        if path.suffix.lower() in TEXT_SUFFIXES or path.name in {"LICENSE"}:
            files.append(path)
    return files


def main() -> int:
    failures: list[tuple[str, str]] = []

    for path in iter_text_files():
        rel = path.relative_to(ROOT).as_posix()
        if path.name in BANNED_FILENAMES:
            failures.append((rel, "banned sensitive filename"))
            continue

        text = path.read_text(encoding="utf-8", errors="replace")
        for label, pattern in RULES:
            if pattern.search(text):
                failures.append((rel, label))

    if failures:
        print("public hygiene check: FAIL")
        for rel, label in failures:
            print(f"- {rel}: {label}")
        print("Matched values are intentionally suppressed.")
        return 1

    print("public hygiene check: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
