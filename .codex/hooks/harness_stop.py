#!/usr/bin/env python3
"""Codex Stop hook scoped to Harness-owned routing and configuration paths."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


REPOS = (
    Path("."),
    Path("AIRoot"),
    Path("ConnectivityCheckerPro"),
    Path("DevAccelerationSystem"),
    Path("AIRoot/Operations/XUUnityLightUnityMcp"),
)

ROOT_PREFIXES = (
    ".codex/",
    "AGENTS.md",
    "Agents.md",
    "AIOutput/Harness/",
    "evals/unity-harness/",
    "scripts/validate-unity-harness.py",
    "scripts/validate-unity-privacy.py",
)

CHILD_PREFIXES = {
    Path("AIRoot"): (
        "AGENTS.md",
        "Modules/XUUnity/",
        "scripts/routing_audit.py",
        "scripts/init_ai_",
    ),
    Path("ConnectivityCheckerPro"): (
        "AGENTS.md",
        "Harness/",
        "scripts/generate-unified-harness-routers.sh",
    ),
    Path("DevAccelerationSystem"): (
        "AGENTS.md",
        "Docs/ai/unity-unified-harness-adapter.md",
        "scripts/refresh_harness_routing.py",
    ),
    Path("AIRoot/Operations/XUUnityLightUnityMcp"): (
        "AGENTS.md",
        "docs/clients/AGENTS.md",
    ),
}


def is_harness_path(repo: Path, path: str) -> bool:
    if repo == Path("."):
        return any(path == prefix or path.startswith(prefix) for prefix in ROOT_PREFIXES)
    prefixes = CHILD_PREFIXES.get(repo, ())
    return path.endswith("/AGENTS.md") or any(path == prefix or path.startswith(prefix) for prefix in prefixes)


def parse_porcelain_z(output: str) -> list[str]:
    """Return destination paths from porcelain-v1 -z, including renames."""
    fields = output.split("\0")
    paths: list[str] = []
    index = 0
    while index < len(fields) and fields[index]:
        entry = fields[index]
        if len(entry) < 4:
            raise ValueError(f"invalid git status entry: {entry!r}")
        status = entry[:2]
        paths.append(entry[3:])
        index += 2 if "R" in status or "C" in status else 1
    return paths


def changed_harness_paths(root: Path) -> list[str]:
    changed: list[str] = []
    for repo in REPOS:
        repo_root = root / repo
        result = subprocess.run(
            ["git", "status", "--porcelain=v1", "-z", "--untracked-files=all"],
            cwd=repo_root,
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(f"git status failed in {repo}: {result.stderr.strip()}")
        for path in parse_porcelain_z(result.stdout):
            if is_harness_path(repo, path):
                changed.append(f"{repo}:{path}")
    return changed


def run_validation(root: Path) -> tuple[bool, str]:
    result = subprocess.run(
        [sys.executable, "-B", str(root / "scripts/validate-unity-harness.py")],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
        timeout=25,
    )
    output = (result.stdout + result.stderr).strip()
    if len(output) > 1800:
        output = output[-1800:]
    return result.returncode == 0, output


def decision(payload: dict, root: Path) -> dict:
    if payload.get("stop_hook_active"):
        return {}
    changed = changed_harness_paths(root)
    if not changed:
        return {}
    passed, output = run_validation(root)
    if passed:
        return {}
    return {
        "decision": "block",
        "reason": "Unity Harness routing/config validation is red. Fix only the reported Harness surface; do not run product regressions from this Stop gate.\n" + output,
    }


def main() -> int:
    try:
        payload = json.load(sys.stdin)
        root = Path(subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True).strip())
        print(json.dumps(decision(payload, root)))
        return 0
    except Exception as error:  # Fail open so a hook implementation fault cannot trap ordinary work.
        print(json.dumps({"systemMessage": f"Unity Harness Stop hook could not run: {error}"}))
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
