#!/usr/bin/env python3
"""Static Unity Harness gate; intentionally never launches Unity or product tests."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True

from unity_harness_contract import load_json, measure_context, validate_mcp_contract


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = (
    "AGENTS.md",
    "AIOutput/Harness/KERNEL.md",
    "AIOutput/Harness/current-handoff.md",
    ".codex/hooks.json",
    ".codex/hooks/harness_stop.py",
    ".codex/hooks/test_harness_stop.py",
    "evals/unity-harness/cases.json",
    "evals/unity-harness/results.json",
    "evals/unity-harness/score.py",
    "evals/unity-harness/test_score.py",
    "scripts/unity_harness_contract.py",
    "scripts/test_unity_harness_contract.py",
    "scripts/test_validate_unity_harness.py",
    "ConnectivityCheckerPro/AGENTS.md",
    "ConnectivityCheckerPro/ConnectivityCheckerPro_Publish/AGENTS.md",
    "ConnectivityCheckerPro/ConnectivityCheckerPro_Sample2021/AGENTS.md",
    "ConnectivityCheckerPro/ConnectivityCheckerPro_Sample2022/AGENTS.md",
    "ConnectivityCheckerPro/ConnectivityCheckerPro_Sample6000/AGENTS.md",
    "ConnectivityCheckerPro/ConnectivityCheckerPro_Sample6000_3_2f1/AGENTS.md",
    "DevAccelerationSystem/AGENTS.md",
    "DevAccelerationSystem/DevAccelerationSystem/AGENTS.md",
    "DevAccelerationSystem/DevAccelerationSystem.DemoProject/AGENTS.md",
    "AIRoot/AGENTS.md",
    "AIRoot/Operations/XUUnityLightUnityMcp/AGENTS.md",
    "AIRoot/Operations/XUUnityLightUnityMcp/docs/clients/AGENTS.md",
)

STATIC_COMMANDS = (
    ([sys.executable, "-B", "scripts/validate-unity-privacy.py", "--require-host-opt-out"], ROOT, "privacy-contract"),
    ([sys.executable, "-B", "-m", "unittest", "discover", "-s", "evals/unity-harness", "-p", "test_*.py"], ROOT, "frozen-eval-tests"),
    ([sys.executable, "-B", "evals/unity-harness/score.py"], ROOT, "frozen-eval"),
    ([sys.executable, "-B", "evals/unity-harness/score.py", "--self-test"], ROOT, "frozen-eval-mutations"),
    ([sys.executable, "-B", "-m", "unittest", "discover", "-s", ".codex/hooks", "-p", "test_*.py"], ROOT, "stop-hook-tests"),
    ([sys.executable, "-B", "-m", "unittest", "discover", "-s", "scripts", "-p", "test_*unity_harness*.py"], ROOT, "current-contract-mutations"),
    ([sys.executable, "-B", "AIRoot/scripts/routing_audit.py", "--host-root", "."], ROOT, "routing-audit"),
    (["bash", "scripts/testing/run_setup_smoke.sh"], ROOT / "AIRoot", "airroot-routing-smoke"),
    (["bash", "scripts/generate-unified-harness-routers.sh", "--check"], ROOT / "ConnectivityCheckerPro", "connectivity-router-generator"),
    (["bash", "scripts/check-privacy-identities.sh"], ROOT / "ConnectivityCheckerPro", "connectivity-privacy-contract"),
    ([sys.executable, "-B", "scripts/refresh_harness_routing.py", "--check"], ROOT / "DevAccelerationSystem", "das-router-generator"),
    ([sys.executable, "-B", "scripts/testing/check_release_version_consistency.py"], ROOT / "AIRoot/Operations/XUUnityLightUnityMcp", "mcp-release-contract"),
)


def run(command: list[str], cwd: Path = ROOT) -> tuple[bool, str]:
    try:
        result = subprocess.run(
            command, cwd=cwd, check=False, capture_output=True, text=True, timeout=20
        )
    except subprocess.TimeoutExpired as error:
        return False, f"timed out after {error.timeout}s"
    return result.returncode == 0, (result.stdout + result.stderr).strip()


def main() -> int:
    failures: list[str] = []
    checks: list[str] = []

    for relative in REQUIRED_FILES:
        if not (ROOT / relative).is_file():
            failures.append(f"missing required file: {relative}")
    checks.append(f"required-files:{len(REQUIRED_FILES)}")

    for relative in (".codex/hooks.json", "evals/unity-harness/cases.json", "evals/unity-harness/results.json"):
        try:
            load_json(ROOT / relative)
        except Exception as error:
            failures.append(f"invalid strict JSON {relative}: {error}")
    checks.append("strict-json")

    for command, cwd, label in STATIC_COMMANDS:
        passed, output = run(command, cwd)
        checks.append(label)
        if not passed:
            failures.append(f"{label} failed:\n{output[-1600:]}")

    for repo in (
        ROOT,
        ROOT / "AIRoot",
        ROOT / "ConnectivityCheckerPro",
        ROOT / "DevAccelerationSystem",
        ROOT / "AIRoot/Operations/XUUnityLightUnityMcp",
    ):
        passed, tracked = run(["git", "ls-files"], repo)
        if not passed:
            failures.append(f"cannot enumerate tracked routers in {repo.name}")
            continue
        legacy = [path for path in tracked.splitlines() if Path(path).name == "Agents.md"]
        if legacy:
            failures.append(f"legacy mixed-case routers remain in {repo.name}: {legacy}")
    checks.append("canonical-router-case")

    try:
        mcp_facts, mcp_failures = validate_mcp_contract(ROOT)
    except Exception as error:
        mcp_facts, mcp_failures = {}, [f"MCP contract could not be resolved: {error}"]
    failures.extend(mcp_failures)
    checks.append(
        f"mcp-current-tree:{mcp_facts.get('tag', 'unresolved')}:"
        f"consumers={mcp_facts.get('consumers_passed', 0)}/{mcp_facts.get('consumers_total', 7)}"
    )

    context, context_failures = measure_context(ROOT)
    failures.extend(context_failures)
    checks.append(f"context-current-tree:scenarios={len(context)}")

    summary = {
        "status": "fail" if failures else "pass",
        "checks": checks,
        "mcp_contract": mcp_facts,
        "context_composition": context,
        "failures": failures,
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
