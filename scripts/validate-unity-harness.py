#!/usr/bin/env python3
"""Static Unity Harness gate; never launches Unity or product regressions."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True

from unity_harness_contract import (
    duplicate_semantic_sections,
    legacy_active_path_failures,
    load_json,
    measure_context,
    measure_documents,
    route_contract_failures,
    validate_mcp_contract,
    validate_topology,
    workspace_topology_mirror_failures,
)


ROOT = Path(__file__).resolve().parents[1]

FIXED_REQUIRED_FILES = (
    "AGENTS.md",
    "WORKSPACE.md",
    "AIOutput/Harness/KERNEL.md",
    "AIOutput/Harness/current-handoff.md",
    "AIOutput/Registry/host_topology.yaml",
    "AIOutput/Registry/setup_status.yaml",
    ".codex/hooks.json",
    ".codex/hooks/harness_stop.py",
    ".codex/hooks/test_harness_stop.py",
    "evals/unity-harness/cases.json",
    "evals/unity-harness/results.json",
    "evals/unity-harness/score.py",
    "evals/unity-harness/test_score.py",
    "scripts/unity_harness_contract.py",
    "scripts/unity_harness_review.py",
    "scripts/test_unity_harness_contract.py",
    "scripts/test_unity_harness_privacy.py",
    "scripts/test_unity_harness_review.py",
    "scripts/test_validate_unity_harness.py",
)

STATIC_COMMANDS = (
    ([sys.executable, "-B", "scripts/validate-unity-privacy.py"], ROOT, "privacy-structure"),
    ([sys.executable, "-B", "-m", "unittest", "discover", "-s", "evals/unity-harness", "-p", "test_*.py"], ROOT, "frozen-eval-tests"),
    ([sys.executable, "-B", "evals/unity-harness/score.py"], ROOT, "frozen-policy-self-consistency"),
    ([sys.executable, "-B", "evals/unity-harness/score.py", "--self-test"], ROOT, "frozen-eval-mutations"),
    ([sys.executable, "-B", "-m", "unittest", "discover", "-s", ".codex/hooks", "-p", "test_*.py"], ROOT, "stop-hook-tests"),
    ([sys.executable, "-B", "-m", "unittest", "discover", "-s", "scripts", "-p", "test_*unity_harness*.py"], ROOT, "current-contract-mutations"),
    ([sys.executable, "-B", "AIRoot/scripts/routing_audit.py", "--host-root", "."], ROOT, "routing-audit"),
    (["bash", "scripts/testing/run_setup_smoke.sh"], ROOT / "AIRoot", "airroot-routing-smoke"),
    (["bash", "scripts/generate-unified-harness-routers.sh", "--check"], ROOT / "ConnectivityCheckerPro", "connectivity-router-generator"),
    (["bash", "scripts/check-privacy-identities.sh"], ROOT / "ConnectivityCheckerPro", "connectivity-privacy-contract"),
    ([sys.executable, "-B", "scripts/refresh_harness_routing.py", "--check"], ROOT / "DevAccelerationSystem", "das-router-generator"),
    (["bash", "scripts/testing/run_host_python_tests.sh"], ROOT / "AIRoot/Operations/XUUnityLightUnityMcp", "mcp-static-suite"),
)

STOP_LABELS = {
    "privacy-structure",
    "frozen-eval-tests",
    "frozen-policy-self-consistency",
    "stop-hook-tests",
    "current-contract-mutations",
    "routing-audit",
    "connectivity-router-generator",
    "das-router-generator",
}

SEMANTIC_OWNERS = (
    "AIOutput/Harness/KERNEL.md",
    "AIRoot/Modules/XUUnity/tasks/change_delivery.md",
    "AIRoot/Modules/XUUnity/reviews/post_implementation_impact_review.md",
    "ConnectivityCheckerPro/Harness/unity-adapter.md",
    "DevAccelerationSystem/Docs/ai/unity-unified-harness-adapter.md",
)


def run(command: list[str], cwd: Path = ROOT, timeout: int = 120) -> tuple[bool, str]:
    try:
        result = subprocess.run(
            command, cwd=cwd, check=False, capture_output=True, text=True, timeout=timeout
        )
    except subprocess.TimeoutExpired as error:
        return False, f"timed out after {error.timeout}s"
    return result.returncode == 0, (result.stdout + result.stderr).strip()


def topology_required_files(topology: dict) -> list[str]:
    required = set(FIXED_REQUIRED_FILES)
    for record in topology.get("boundaries", []):
        for field in ("router", "kernel", "adapter", "generator"):
            value = record.get(field)
            if value and value != "none":
                required.add(value)
    for record in topology.get("projects", []):
        if record.get("router"):
            required.add(record["router"])
    for record in topology.get("operations", []):
        for field in ("router", "client_router"):
            value = record.get(field)
            if value:
                required.add(value)
    return sorted(required)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stop", action="store_true", help="run the bounded Stop-hook subset")
    args = parser.parse_args()

    failures: list[str] = []
    warnings: list[str] = []
    checks: list[str] = []

    topology, topology_failures = validate_topology(ROOT)
    failures.extend(topology_failures)
    checks.append("topology-owner")

    required_files = topology_required_files(topology) if topology else list(FIXED_REQUIRED_FILES)
    for relative in required_files:
        if not (ROOT / relative).is_file():
            failures.append(f"missing required file: {relative}")
    checks.append(f"required-files:{len(required_files)}")

    for relative in (".codex/hooks.json", "evals/unity-harness/cases.json", "evals/unity-harness/results.json"):
        try:
            load_json(ROOT / relative)
        except Exception as error:
            failures.append(f"invalid strict JSON {relative}: {error}")
    checks.append("strict-json")

    commands = [entry for entry in STATIC_COMMANDS if not args.stop or entry[2] in STOP_LABELS]
    for command, cwd, label in commands:
        passed, output = run(command, cwd, timeout=35 if args.stop else 180)
        checks.append(label)
        if not passed:
            failures.append(f"{label} failed:\n{output[-2400:]}")

    for repo in (
        ROOT,
        ROOT / "AIRoot",
        ROOT / "ConnectivityCheckerPro",
        ROOT / "DevAccelerationSystem",
        ROOT / "AIRoot/Operations/XUUnityLightUnityMcp",
    ):
        passed, tracked = run(["git", "ls-files"], repo)
        if not passed:
            failures.append(f"cannot enumerate tracked routers in {repo}")
            continue
        legacy = [path for path in tracked.splitlines() if Path(path).name == "Agents.md"]
        if legacy:
            failures.append(f"legacy mixed-case routers remain in {repo.name}: {legacy}")
    checks.append("canonical-router-case")

    if topology:
        failures.extend(workspace_topology_mirror_failures(ROOT, topology))
        checks.append("workspace-topology-mirror")
        failures.extend(route_contract_failures(ROOT, topology))
        checks.append("conditional-routes-and-fallbacks")
        try:
            mcp_facts, mcp_failures = validate_mcp_contract(ROOT, topology)
        except Exception as error:
            mcp_facts, mcp_failures = {}, [f"MCP contract could not be resolved: {error}"]
        failures.extend(mcp_failures)
        checks.append(
            f"mcp-current-tree:{mcp_facts.get('tag', 'unresolved')}:"
            f"consumers={mcp_facts.get('consumers_passed', 0)}/{mcp_facts.get('consumers_total', 7)}"
        )
        try:
            context, context_warnings, context_failures = measure_context(ROOT, topology)
        except Exception as error:
            context, context_warnings, context_failures = {}, [], [f"context composition failed: {error}"]
        warnings.extend(context_warnings)
        failures.extend(context_failures)
        checks.append(f"context-current-tree:scenarios={len(context)}")
    else:
        mcp_facts, context = {}, {}

    documents, document_warnings, document_failures = measure_documents(ROOT)
    warnings.extend(document_warnings)
    failures.extend(document_failures)
    checks.append("document-shape-advisory-bytes-hard")

    failures.extend(duplicate_semantic_sections(ROOT, SEMANTIC_OWNERS))
    failures.extend(legacy_active_path_failures(ROOT))
    checks.extend(("canonical-section-uniqueness", "active-topology-paths"))

    summary = {
        "status": "fail" if failures else "pass",
        "mode": "stop" if args.stop else "full-static",
        "checks": checks,
        "mcp_contract": mcp_facts,
        "context_composition": context,
        "document_shape": documents,
        "warnings": warnings,
        "failures": failures,
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
