#!/usr/bin/env python3
"""Fail-open Stop hook for the bounded, static Unity Harness contract."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT_PREFIXES = (
    ".codex/hooks.json",
    ".codex/hooks/",
    ".gitmodules",
    "AGENTS.md",
    "AIFoxsterDevHub.sln",
    "WORKSPACE.md",
    "AIOutput/Harness/",
    "AIOutput/Registry/host_topology.yaml",
    "AIOutput/Registry/setup_status.yaml",
    "AIModules/XUUnityInternal/start_session.md",
    "AIModules/XUUnityInternal/knowledge/host_topology.md",
    "AIModules/XUUnityInternal/knowledge/validation_paths.md",
    "evals/unity-harness/",
    "scripts/refresh-aifoxster-hub.sh",
    "scripts/unity_harness_contract.py",
    "scripts/unity_harness_review.py",
    "scripts/validate-unity-harness.py",
    "scripts/validate-unity-privacy.py",
    "scripts/test_unity_harness_contract.py",
    "scripts/test_unity_harness_privacy.py",
    "scripts/test_unity_harness_review.py",
    "scripts/test_validate_unity_harness.py",
)


def _relative_to_boundary(global_path: str, boundary_path: str) -> str | None:
    prefix = boundary_path.rstrip("/") + "/"
    if global_path == boundary_path:
        return "."
    if global_path.startswith(prefix):
        return global_path[len(prefix):]
    return None


def configured_paths(
    root: Path,
) -> tuple[dict[Path, tuple[str, ...]], dict[Path, tuple[str, ...]]]:
    """Derive active child triggers and pointer-only parent gitlinks from topology."""
    scripts = str(root / "scripts")
    if scripts not in sys.path:
        sys.path.insert(0, scripts)
    from unity_harness_contract import boundary_map, load_topology  # pylint: disable=import-outside-toplevel

    topology = load_topology(root)
    boundaries = boundary_map(topology)
    child_paths: dict[Path, set[str]] = {}
    gitlinks_by_parent: dict[Path, set[str]] = {}
    for identity, record in boundaries.items():
        if identity == "root":
            continue
        boundary = Path(record["path"])
        child_paths.setdefault(boundary, set())
        if record["parent"] == "root":
            parent_path = Path(".")
        elif record["parent"] in boundaries:
            parent_path = Path(boundaries[record["parent"]]["path"])
        else:
            continue
        gitlinks_by_parent.setdefault(parent_path, set()).add(record["gitlink"])
        for field in ("router", "kernel", "adapter", "generator"):
            target = record[field]
            if target == "none":
                continue
            relative = _relative_to_boundary(target, record["path"])
            if relative and relative != ".":
                child_paths[boundary].add(relative)
    for project in topology["projects"]:
        boundary_record = boundaries[project["git_boundary"]]
        boundary = Path(boundary_record["path"])
        relative = _relative_to_boundary(project["router"], boundary_record["path"])
        if relative:
            child_paths.setdefault(boundary, set()).add(relative)
    return (
        {repo: tuple(sorted(paths)) for repo, paths in child_paths.items()},
        {repo: tuple(sorted(paths)) for repo, paths in gitlinks_by_parent.items()},
    )


def _matches(path: str, prefixes: tuple[str, ...]) -> bool:
    return any(
        path == prefix or (prefix.endswith("/") and path.startswith(prefix))
        for prefix in prefixes
    )


def is_harness_path(repo: Path, path: str, child_paths: dict[Path, tuple[str, ...]]) -> bool:
    if repo == Path("."):
        return _matches(path, ROOT_PREFIXES)
    return path in child_paths.get(repo, ())


def parse_porcelain_z(output: str) -> list[str]:
    """Return both source and destination paths from porcelain-v1 -z."""
    fields = output.split("\0")
    paths: list[str] = []
    index = 0
    while index < len(fields) and fields[index]:
        entry = fields[index]
        if len(entry) < 4:
            raise ValueError(f"invalid git status entry: {entry!r}")
        status = entry[:2]
        paths.append(entry[3:])
        if "R" in status or "C" in status:
            if index + 1 >= len(fields) or not fields[index + 1]:
                raise ValueError("rename/copy status is missing its source path")
            paths.append(fields[index + 1])
            index += 2
        else:
            index += 1
    return paths


def _gitlink_pointer_changed(root: Path, path: str) -> bool:
    for cached in (False, True):
        command = ["git", "diff", "--quiet", "--ignore-submodules=dirty"]
        if cached:
            command.append("--cached")
        command.extend(("--", path))
        result = subprocess.run(command, cwd=root, check=False, capture_output=True, text=True)
        if result.returncode == 1:
            return True
        if result.returncode not in {0, 1}:
            raise RuntimeError(f"git diff failed for {path}: {result.stderr.strip()}")
    return False


def _status_paths(repository: Path) -> list[str]:
    result = subprocess.run(
        ["git", "status", "--porcelain=v1", "-z", "--untracked-files=all"],
        cwd=repository,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"git status failed in {repository}: {result.stderr.strip()}")
    return parse_porcelain_z(result.stdout)


def changed_harness_paths(root: Path) -> list[str]:
    root_status_paths = _status_paths(root)
    fixed_root_changes = sorted(
        {f".:{path}" for path in root_status_paths if _matches(path, ROOT_PREFIXES)}
    )
    if fixed_root_changes:
        return fixed_root_changes

    child_paths, gitlinks_by_parent = configured_paths(root)
    changed: list[str] = []
    for path in root_status_paths:
        if path in gitlinks_by_parent.get(Path("."), ()) and _gitlink_pointer_changed(root, path):
            changed.append(f".:{path}")
    child_repositories = set(child_paths) | {
        repo for repo in gitlinks_by_parent if repo != Path(".")
    }
    for repo in sorted(child_repositories, key=lambda value: value.as_posix()):
        for path in _status_paths(root / repo):
            if path in gitlinks_by_parent.get(repo, ()):
                if _gitlink_pointer_changed(root / repo, path):
                    changed.append(f"{repo}:{path}")
                continue
            if is_harness_path(repo, path, child_paths):
                changed.append(f"{repo}:{path}")
    return sorted(set(changed))


def run_validation(root: Path) -> tuple[bool, str]:
    result = subprocess.run(
        [sys.executable, "-B", str(root / "scripts/validate-unity-harness.py"), "--stop"],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
        timeout=50,
    )
    output = (result.stdout + result.stderr).strip()
    if len(output) > 2_400:
        output = output[-2_400:]
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
        "reason": (
            "Unity Harness static routing/configuration validation is red. "
            "Fix only the reported Harness surface; this gate never runs Unity or product regressions.\n"
            + output
        ),
    }


def main() -> int:
    try:
        payload = json.load(sys.stdin)
        root = Path(
            subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True).strip()
        )
        print(json.dumps(decision(payload, root)))
        return 0
    except Exception as error:  # Fail open so hook faults cannot trap ordinary work.
        print(json.dumps({"systemMessage": f"Unity Harness Stop hook could not run: {error}"}))
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
