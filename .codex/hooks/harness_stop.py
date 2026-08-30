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

CHILD_MARKERS = (
    "AGENTS.md",
    "Agents.md",
    "Harness/",
    "harness/",
    "routing_audit.py",
    "init_ai_",
    "generate_agents",
    "generate-agents",
    "agent-routers",
    "sync_agent_routers",
    "run_host_python_tests.sh",
    "validate_routing",
    "validate-routing",
    "Modules/XUUnity/",
)


def is_harness_path(repo: Path, path: str) -> bool:
    if repo == Path("."):
        return any(path == prefix or path.startswith(prefix) for prefix in ROOT_PREFIXES)
    return any(marker in path for marker in CHILD_MARKERS)


def changed_harness_paths(root: Path) -> list[str]:
    changed: list[str] = []
    for repo in REPOS:
        repo_root = root / repo
        result = subprocess.run(
            ["git", "status", "--porcelain=v1", "--untracked-files=all"],
            cwd=repo_root,
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            continue
        for line in result.stdout.splitlines():
            path = line[3:]
            if " -> " in path:
                path = path.split(" -> ", 1)[1]
            if is_harness_path(repo, path):
                changed.append(f"{repo}:{path}")
    return changed


def run_validation(root: Path) -> tuple[bool, str]:
    result = subprocess.run(
        [sys.executable, str(root / "scripts/validate-unity-harness.py")],
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
