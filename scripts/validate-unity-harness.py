#!/usr/bin/env python3
"""Static Harness gate; intentionally never launches Unity or product tests."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MCP_TAG = "v0.3.62"
MCP_VERSION = "0.3.62"
MCP_BASE_COMMIT = "7b8b139d8bdd5d226e5e6703b586e1ca9f16f442"
MCP_PACKAGE_HASH = "7b8b139d8bdd5d226e5e6703b586e1ca9f16f442"
MCP_URL = f"https://github.com/FoxsterDev/xuunity-mcp.git?path=/packages/com.xuunity.light-mcp#{MCP_TAG}"

REQUIRED_FILES = (
    "AGENTS.md",
    "AIOutput/Harness/KERNEL.md",
    "AIOutput/Harness/current-handoff.md",
    ".codex/hooks.json",
    ".codex/hooks/harness_stop.py",
    "evals/unity-harness/cases.json",
    "evals/unity-harness/score.py",
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

UNITY_PROJECTS = (
    "ConnectivityCheckerPro/ConnectivityCheckerPro_Publish",
    "ConnectivityCheckerPro/ConnectivityCheckerPro_Sample2021",
    "ConnectivityCheckerPro/ConnectivityCheckerPro_Sample2022",
    "ConnectivityCheckerPro/ConnectivityCheckerPro_Sample6000",
    "ConnectivityCheckerPro/ConnectivityCheckerPro_Sample6000_3_2f1",
    "DevAccelerationSystem/DevAccelerationSystem",
    "DevAccelerationSystem/DevAccelerationSystem.DemoProject",
)


def run(command: list[str], cwd: Path = ROOT) -> tuple[bool, str]:
    result = subprocess.run(command, cwd=cwd, check=False, capture_output=True, text=True)
    return result.returncode == 0, (result.stdout + result.stderr).strip()


def main() -> int:
    failures: list[str] = []
    checks: list[str] = []

    for relative in REQUIRED_FILES:
        if not (ROOT / relative).is_file():
            failures.append(f"missing required file: {relative}")
    checks.append(f"required-files:{len(REQUIRED_FILES)}")

    for relative in (".codex/hooks.json", "evals/unity-harness/cases.json"):
        try:
            json.loads((ROOT / relative).read_text(encoding="utf-8"))
        except Exception as error:
            failures.append(f"invalid JSON {relative}: {error}")
    checks.append("json-shape")

    commands = (
        ([sys.executable, "scripts/validate-unity-privacy.py"], ROOT, "privacy-contract"),
        ([sys.executable, "evals/unity-harness/score.py", "--self-test"], ROOT, "frozen-eval"),
        ([sys.executable, "AIRoot/scripts/routing_audit.py", "--host-root", "."], ROOT, "routing-audit"),
        (["bash", "scripts/generate-unified-harness-routers.sh", "--check"], ROOT / "ConnectivityCheckerPro", "connectivity-router-generator"),
        (["bash", "scripts/check-privacy-identities.sh"], ROOT / "ConnectivityCheckerPro", "connectivity-privacy-contract"),
        ([sys.executable, "scripts/refresh_harness_routing.py", "--check"], ROOT / "DevAccelerationSystem", "das-router-generator"),
        ([sys.executable, "scripts/tools/sync_agent_routers.py", "--check"], ROOT / "AIRoot/Operations/XUUnityLightUnityMcp", "mcp-router-generator"),
    )
    for command, cwd, label in commands:
        passed, output = run(command, cwd)
        checks.append(label)
        if not passed:
            failures.append(f"{label} failed:\n{output[-1200:]}")

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

    mcp = ROOT / "AIRoot/Operations/XUUnityLightUnityMcp"
    passed, head = run(["git", "rev-parse", "HEAD"], mcp)
    base_passed, _ = run(["git", "merge-base", "--is-ancestor", MCP_BASE_COMMIT, "HEAD"], mcp)
    tag_passed, tag = run(["git", "describe", "--exact-match", "--tags", MCP_BASE_COMMIT], mcp)
    if not passed or not base_passed:
        failures.append(f"MCP HEAD {head.strip()} is not based on stable commit {MCP_BASE_COMMIT}")
    if not tag_passed or tag.strip() != MCP_TAG:
        failures.append(f"MCP stable base is not exact tag {MCP_TAG}: {tag.strip()}")
    package_json = json.loads((mcp / "packages/com.xuunity.light-mcp/package.json").read_text(encoding="utf-8"))
    if package_json.get("version") != MCP_VERSION:
        failures.append(f"MCP package version is not {MCP_VERSION}: {package_json.get('version')!r}")

    for project_relative in UNITY_PROJECTS:
        project = ROOT / project_relative
        manifest = json.loads((project / "Packages/manifest.json").read_text(encoding="utf-8"))
        lock = json.loads((project / "Packages/packages-lock.json").read_text(encoding="utf-8"))
        manifest_pin = manifest.get("dependencies", {}).get("com.xuunity.light-mcp")
        lock_entry = lock.get("dependencies", {}).get("com.xuunity.light-mcp", {})
        if manifest_pin != MCP_URL:
            failures.append(f"{project_relative}: MCP manifest pin is {manifest_pin!r}")
        if lock_entry.get("version") != MCP_URL:
            failures.append(f"{project_relative}: MCP lock version is {lock_entry.get('version')!r}")
        if lock_entry.get("hash") != MCP_PACKAGE_HASH:
            failures.append(f"{project_relative}: MCP lock hash is {lock_entry.get('hash')!r}")
    checks.append(f"mcp-stable-base:{MCP_TAG}:consumers={len(UNITY_PROJECTS)}")

    summary = {"status": "fail" if failures else "pass", "checks": checks, "failures": failures}
    print(json.dumps(summary, indent=2))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
