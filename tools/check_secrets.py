"""Refuse a commit or CI run whose added lines contain something shaped like a secret.

Usage: check_secrets.py            (scans `git diff --cached`)
       check_secrets.py --stdin    (scans a unified diff on stdin)
       check_secrets.py --range A..B
Prints only the file and line number of each hit, never the matched value.
"""

import re
import subprocess
import sys

PATTERNS: dict[str, re.Pattern[str]] = {
    "aws access key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "private key block": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    "github token": re.compile(r"\bgh[pousr]_[A-Za-z0-9]{36,}\b"),
    "anthropic key": re.compile(r"\bsk-ant-[A-Za-z0-9_-]{20,}"),
    "assigned key or secret": re.compile(
        r"(?i)\b(api[_-]?key|secret|token|password)\b\s*[:=]\s*['\"][^'\"\s]{16,}['\"]"
    ),
}


def scan(diff: str) -> list[str]:
    hits: list[str] = []
    path = "?"
    line_no = 0
    for raw in diff.splitlines():
        if raw.startswith("+++ "):
            path = raw[6:] if raw.startswith("+++ b/") else raw[4:]
            continue
        if raw.startswith("@@"):
            match = re.search(r"\+(\d+)", raw)
            line_no = int(match.group(1)) - 1 if match else 0
            continue
        if raw.startswith("+"):
            line_no += 1
            for kind, pattern in PATTERNS.items():
                if pattern.search(raw[1:]):
                    hits.append(f"{path}:{line_no}: possible {kind}")
        elif not raw.startswith("-"):
            line_no += 1
    return hits


def main(argv: list[str]) -> int:
    if "--stdin" in argv:
        diff = sys.stdin.read()
    else:
        cmd = ["git", "diff", "--unified=0"]
        cmd += [argv[argv.index("--range") + 1]] if "--range" in argv else ["--cached"]
        diff = subprocess.run(cmd, capture_output=True, text=True, check=True).stdout
    hits = scan(diff)
    for hit in hits:
        print(hit, file=sys.stderr)
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
