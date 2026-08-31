#!/usr/bin/env python3
"""Current-tree contracts shared by the static Unity Harness gate and tests."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Any


CONSUMERS = (
    "ConnectivityCheckerPro/ConnectivityCheckerPro_Publish",
    "ConnectivityCheckerPro/ConnectivityCheckerPro_Sample2021",
    "ConnectivityCheckerPro/ConnectivityCheckerPro_Sample2022",
    "ConnectivityCheckerPro/ConnectivityCheckerPro_Sample6000",
    "ConnectivityCheckerPro/ConnectivityCheckerPro_Sample6000_3_2f1",
    "DevAccelerationSystem/DevAccelerationSystem",
    "DevAccelerationSystem/DevAccelerationSystem.DemoProject",
)

CONTEXT_SCENARIOS = {
    "hub-root": (
        "AGENTS.md",
        "AIOutput/Harness/KERNEL.md",
    ),
    "airroot": ("AIRoot/AGENTS.md",),
    "connectivity-root": (
        "ConnectivityCheckerPro/AGENTS.md",
        "ConnectivityCheckerPro/Harness/README.md",
        "ConnectivityCheckerPro/Harness/unity-adapter.md",
    ),
    "connectivity-consumer": (
        "ConnectivityCheckerPro/AGENTS.md",
        "ConnectivityCheckerPro/Harness/README.md",
        "ConnectivityCheckerPro/Harness/unity-adapter.md",
        "ConnectivityCheckerPro/ConnectivityCheckerPro_Sample2022/AGENTS.md",
    ),
    "devaccel-root": (
        "DevAccelerationSystem/AGENTS.md",
        "DevAccelerationSystem/Docs/ai/unity-unified-harness-adapter.md",
    ),
    "devaccel-demo": (
        "DevAccelerationSystem/AGENTS.md",
        "DevAccelerationSystem/Docs/ai/unity-unified-harness-adapter.md",
        "DevAccelerationSystem/DevAccelerationSystem.DemoProject/AGENTS.md",
    ),
    "mcp-standalone": ("AIRoot/Operations/XUUnityLightUnityMcp/AGENTS.md",),
    "mcp-host-mounted": (
        "AGENTS.md",
        "AIOutput/Harness/KERNEL.md",
        "AIRoot/AGENTS.md",
        "AIRoot/Operations/XUUnityLightUnityMcp/AGENTS.md",
    ),
}

CONTEXT_BUDGETS = {
    "hub-root": (220, 12_000),
    "airroot": (50, 3_000),
    "connectivity-root": (200, 10_000),
    "connectivity-consumer": (230, 12_000),
    "devaccel-root": (300, 14_000),
    "devaccel-demo": (340, 16_000),
    "mcp-standalone": (90, 9_000),
    "mcp-host-mounted": (330, 21_000),
}


class DuplicateKeyError(ValueError):
    pass


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKeyError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_unique_object)
    if not isinstance(value, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return value


def run_git(repo: Path, *arguments: str) -> str:
    result = subprocess.run(
        ["git", *arguments], cwd=repo, check=False, capture_output=True, text=True
    )
    if result.returncode != 0:
        raise ValueError(f"git {' '.join(arguments)} failed in {repo}: {result.stderr.strip()}")
    return result.stdout.strip()


def gitlink_commit(parent: Path, relative: str) -> str:
    output = run_git(parent, "ls-tree", "HEAD", "--", relative)
    match = re.fullmatch(r"160000 commit ([0-9a-f]{40})\t.+", output)
    if not match:
        raise ValueError(f"expected exact gitlink for {relative} in {parent}: {output!r}")
    return match.group(1)


def verify_gitlink(parent: Path, relative: str, child: Path) -> str:
    expected = gitlink_commit(parent, relative)
    actual = run_git(child, "rev-parse", "HEAD")
    if actual != expected:
        raise ValueError(f"gitlink mismatch for {relative}: tree={expected}, checkout={actual}")
    return actual


def select_release_tag(tags: list[str], package_version: str) -> str:
    expected = f"v{package_version}"
    stable = [tag for tag in tags if re.fullmatch(r"v\d+\.\d+\.\d+", tag)]
    if expected not in stable:
        raise ValueError(f"MCP HEAD is not exact stable tag {expected}; tags={sorted(tags)}")
    return expected


def validate_consumer_pin(project: Path, expected_url: str, expected_hash: str) -> list[str]:
    errors: list[str] = []
    manifest = load_json(project / "Packages/manifest.json")
    lock = load_json(project / "Packages/packages-lock.json")
    manifest_pin = manifest.get("dependencies", {}).get("com.xuunity.light-mcp")
    lock_entry = lock.get("dependencies", {}).get("com.xuunity.light-mcp", {})
    if manifest_pin != expected_url:
        errors.append(f"manifest pin is {manifest_pin!r}, expected {expected_url!r}")
    if not isinstance(lock_entry, dict):
        errors.append("lock entry must be an object")
        return errors
    if lock_entry.get("version") != expected_url:
        errors.append(f"lock version is {lock_entry.get('version')!r}, expected {expected_url!r}")
    if lock_entry.get("hash") != expected_hash:
        errors.append(f"lock hash is {lock_entry.get('hash')!r}, expected {expected_hash!r}")
    if lock_entry.get("source") != "git" or lock_entry.get("depth") != 0:
        errors.append("lock source/depth is not exact git depth 0")
    return errors


def validate_mcp_contract(root: Path) -> tuple[dict[str, Any], list[str]]:
    failures: list[str] = []
    boundaries = (
        (root, "AIRoot", root / "AIRoot"),
        (root, "ConnectivityCheckerPro", root / "ConnectivityCheckerPro"),
        (root, "DevAccelerationSystem", root / "DevAccelerationSystem"),
        (
            root / "AIRoot",
            "Operations/XUUnityLightUnityMcp",
            root / "AIRoot/Operations/XUUnityLightUnityMcp",
        ),
    )
    for parent, relative, child in boundaries:
        try:
            verify_gitlink(parent, relative, child)
        except (OSError, ValueError) as error:
            failures.append(str(error))

    mcp = root / "AIRoot/Operations/XUUnityLightUnityMcp"
    head = run_git(mcp, "rev-parse", "HEAD")
    package = load_json(mcp / "packages/com.xuunity.light-mcp/package.json")
    version = package.get("version")
    if not isinstance(version, str) or not re.fullmatch(r"\d+\.\d+\.\d+", version):
        failures.append(f"MCP package version is not stable semver: {version!r}")
        version = "invalid"
    try:
        tag = select_release_tag(run_git(mcp, "tag", "--points-at", "HEAD").splitlines(), version)
    except ValueError as error:
        failures.append(str(error))
        tag = f"v{version}"
    tag_object = "unresolved"
    try:
        tag_reference = f"refs/tags/{tag}"
        tag_object = run_git(mcp, "rev-parse", tag_reference)
        tag_type = run_git(mcp, "cat-file", "-t", tag_reference)
        peeled = run_git(mcp, "rev-parse", f"{tag_reference}^{{}}")
        if tag_type != "tag" or peeled != head:
            failures.append(
                f"MCP release tag {tag} is not an annotated tag peeled to HEAD: "
                f"type={tag_type}, peeled={peeled}, head={head}"
            )
    except ValueError as error:
        failures.append(str(error))

    expected_url = (
        "https://github.com/FoxsterDev/xuunity-mcp.git"
        f"?path=/packages/com.xuunity.light-mcp#{tag}"
    )
    passing_consumers = 0
    for relative in CONSUMERS:
        try:
            errors = validate_consumer_pin(root / relative, expected_url, head)
        except (OSError, ValueError, json.JSONDecodeError) as error:
            errors = [str(error)]
        if errors:
            failures.extend(f"{relative}: {error}" for error in errors)
        else:
            passing_consumers += 1

    facts = {
        "tag": tag,
        "tag_object": tag_object,
        "commit": head,
        "package_version": version,
        "package_hash": head,
        "consumer_url": expected_url,
        "consumers_passed": passing_consumers,
        "consumers_total": len(CONSUMERS),
    }
    return facts, failures


def measure_context(root: Path) -> tuple[dict[str, Any], list[str]]:
    measurements: dict[str, Any] = {}
    failures: list[str] = []
    for scenario, relatives in CONTEXT_SCENARIOS.items():
        lines = 0
        size = 0
        missing: list[str] = []
        for relative in relatives:
            path = root / relative
            if not path.is_file():
                missing.append(relative)
                continue
            content = path.read_bytes()
            lines += len(content.splitlines())
            size += len(content)
        line_budget, byte_budget = CONTEXT_BUDGETS[scenario]
        if missing:
            failures.append(f"{scenario}: missing context files {missing}")
        if lines > line_budget or size > byte_budget:
            failures.append(
                f"{scenario}: context {lines} lines/{size} bytes exceeds "
                f"{line_budget}/{byte_budget} budget"
            )
        measurements[scenario] = {
            "files": list(relatives),
            "lines": lines,
            "bytes": size,
            "line_budget": line_budget,
            "byte_budget": byte_budget,
        }
    return measurements, failures
