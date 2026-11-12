import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "check_secrets.py"


def run(diff: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--stdin"],
        input=diff,
        capture_output=True,
        text=True,
        check=False,
    )


def diff_adding(line: str) -> str:
    return f"diff --git a/x.py b/x.py\n--- a/x.py\n+++ b/x.py\n@@ -0,0 +1 @@\n+{line}\n"


# Fake values assembled at runtime so this file never contains a literal match itself.
AWS_KEY = "AKIA" + "Z" * 16
PEM = "-----BEGIN " + "RSA PRIVATE KEY-----"
GH_TOKEN = "ghp_" + "a1" * 18
ANTHROPIC_KEY = "sk-ant-" + "api03-" + "x" * 40


def test_clean_diff_passes() -> None:
    result = run(diff_adding("x = compute_surface(chain)"))
    assert result.returncode == 0, result.stderr


def test_each_secret_kind_is_refused() -> None:
    for secret in (AWS_KEY, PEM, GH_TOKEN, ANTHROPIC_KEY, 'api_key = "' + "q" * 24 + '"'):
        result = run(diff_adding(secret))
        assert result.returncode == 1, secret
        assert "x.py" in result.stderr


def test_removed_lines_are_ignored() -> None:
    diff = diff_adding("ok = 1").replace("+ok = 1", f"-{AWS_KEY}")
    assert run(diff).returncode == 0


def test_output_never_echoes_the_secret() -> None:
    result = run(diff_adding(AWS_KEY))
    assert AWS_KEY not in result.stderr + result.stdout
