"""Refuse a commit or CI run whose added lines contain something shaped like a secret.

Usage: check_secrets.py            (scans `git diff --cached`)
       check_secrets.py --stdin    (scans a unified diff on stdin)
       check_secrets.py --range A..B   (scans each commit in the range)
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
    # The name may carry a prefix or suffix (OPENAI_API_KEY, client_secret, "api_key": in JSON),
    # but not one that makes it a reference (SECRET_NAME, token_url). An unquoted value must
    # contain a digit, so `token = request_headers_get` is not a hit.
    "assigned key or secret": re.compile(
        r"(?i)(?<![a-z])(api[_-]?key|secret|token|passw(?:or)?d)"
        r"(?:[_-](?!(?:name|id|arn|path|file|ref|env|url)\b)[a-z0-9_-]*)?['\"]?"
        r"\s*[:=]\s*(?:['\"][^'\"\s]{16,}['\"]|(?=[^\s'\"]*\d)[A-Za-z0-9+/=_-]{16,}(?![^\s,;]))"
    ),
    "password in a connection url": re.compile(r"[a-z][a-z0-9+.-]*://[^:/\s@]+:[^@\s/${<]{3,}@"),
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
        # A range is scanned commit by commit, so a secret added and later removed still shows.
        if "--range" in argv:
            cmd = ["git", "log", "-p", "--unified=0", "--format=", argv[argv.index("--range") + 1]]
        else:
            cmd = ["git", "diff", "--unified=0", "--cached"]
        diff = subprocess.run(cmd, capture_output=True, text=True, check=True).stdout
    hits = scan(diff)
    for hit in hits:
        print(hit, file=sys.stderr)
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
