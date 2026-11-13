import importlib.util
import re
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


VALUE = "q1" * 12
SAMPLES: dict[str, list[str]] = {
    "aws access key": [AWS_KEY, "ASIA" + "Z" * 16],
    "private key block": [PEM],
    "github token": [GH_TOKEN, "github_pat_11" + "A" * 20 + "_" + "b" * 59],
    "anthropic key": [ANTHROPIC_KEY],
    "assigned key or secret": [
        f'api_key = "{VALUE}"',
        f'  "api_key": "{VALUE}",',
        f'OPENAI_API_KEY="{VALUE}"',
        f"DB_PASS{'WORD'}={VALUE}",
        f"client_secret = '{VALUE}'",
        f"aws_secret_access_key = {VALUE}",
        f"pass{'word'}: {VALUE}",
        f'const accessToken = "{VALUE}";',
        f'clientSecret: "{VALUE}",',
        f'stripeApiKey = "{VALUE}"',
    ],
    "env-style key": [f"VITE_SCICHART_LICENSE_KEY={VALUE}", f'OPENAI_KEY="{VALUE}"'],
    "bearer token": ["Authorization: Bearer " + "eyJ" + "a1b2" * 10],
    "password in a connection url": ["postgres://app:" + "s3cr" + "et@db.internal/axiom"],
}


def load_patterns() -> dict[str, re.Pattern[str]]:
    spec = importlib.util.spec_from_file_location("check_secrets", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.PATTERNS


def test_each_secret_kind_is_refused() -> None:
    patterns = load_patterns()
    assert set(SAMPLES) == set(patterns)
    for kind, lines in SAMPLES.items():
        for line in lines:
            assert patterns[kind].search(line), (kind, line)
            result = run(diff_adding(line))
            assert result.returncode == 1, line
            assert "x.py" in result.stderr


def test_ordinary_code_is_not_a_secret() -> None:
    for line in (
        "token = request_headers.get('Authorization')",
        "tokenizer = build_tokenizer_from_settings()",
        "api_key = api_key_loaded_from_vault",
        "password = prompt_for_password_interactively()",
        "url = 'postgres://app:${DB_PASS}@db/axiom'",
        "SECRET_NAME = 'axiom/prod/records-db'",
        "cache_key = 'user-profile-region-main'",
        "accessTokenUrl = 'https://example.invalid/oauth/token'",
        'headers={"Authorization": f"Bearer {token}"}',
        "KEYBOARD_LAYOUT=us-international-2026",
        'var RAIL_COLLAPSED_KEY = "archify-rail-collapsed";',
    ):
        result = run(diff_adding(line))
        assert result.returncode == 0, (line, result.stderr)


def git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args], capture_output=True, text=True, check=True
    ).stdout.strip()


def test_range_scan_catches_a_secret_removed_in_a_later_commit(tmp_path: Path) -> None:
    git(tmp_path, "init", "-q")
    git(tmp_path, "config", "user.email", "t@example.invalid")
    git(tmp_path, "config", "user.name", "t")
    (tmp_path / "a.py").write_text("x = 1\n")
    git(tmp_path, "add", ".")
    git(tmp_path, "commit", "-qm", "base")
    base = git(tmp_path, "rev-parse", "HEAD")
    (tmp_path / "a.py").write_text(f"x = 1\nkey = '{AWS_KEY}'\n")
    git(tmp_path, "commit", "-qam", "add")
    (tmp_path / "a.py").write_text("x = 1\n")
    git(tmp_path, "commit", "-qam", "remove")

    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--range", f"{base}..HEAD"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 1, result.stderr
    assert "a.py:2: possible aws access key" in result.stderr


def test_removed_lines_are_ignored() -> None:
    diff = diff_adding("ok = 1").replace("+ok = 1", f"-{AWS_KEY}")
    assert run(diff).returncode == 0


def test_output_never_echoes_the_secret() -> None:
    result = run(diff_adding(AWS_KEY))
    assert AWS_KEY not in result.stderr + result.stdout


def staged_scan(repo: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT)], cwd=repo, capture_output=True, text=True, check=False
    )


def fresh_repo(repo: Path) -> Path:
    git(repo, "init", "-q")
    git(repo, "config", "user.email", "t@example.invalid")
    git(repo, "config", "user.name", "t")
    return repo


def test_forced_colour_in_git_config_does_not_hide_a_staged_key(tmp_path: Path) -> None:
    repo = fresh_repo(tmp_path)
    git(repo, "config", "color.diff", "always")
    (repo / "a.py").write_text(f"key = '{AWS_KEY}'\n")
    git(repo, "add", ".")
    result = staged_scan(repo)
    assert result.returncode == 1, result.stderr
    assert "a.py:1: possible aws access key" in result.stderr


def test_a_key_in_a_file_git_calls_binary_is_still_found(tmp_path: Path) -> None:
    repo = fresh_repo(tmp_path)
    (repo / "blob.dat").write_bytes(f"k={AWS_KEY}\n".encode() + b"\x00bin\n")
    git(repo, "add", ".")
    result = staged_scan(repo)
    assert result.returncode == 1, result.stderr
    assert "blob.dat" in result.stderr
