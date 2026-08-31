#!/usr/bin/env python3
"""Fail closed when Hub Unity projects can expose product identity or Cloud data."""

from __future__ import annotations

import argparse
import json
import platform
import subprocess
from pathlib import Path


PROJECTS = {
    "ConnectivityCheckerPro/ConnectivityCheckerPro_Publish": "CCP-PUB",
    "ConnectivityCheckerPro/ConnectivityCheckerPro_Sample2021": "CCP-S21",
    "ConnectivityCheckerPro/ConnectivityCheckerPro_Sample2022": "CCP-S22",
    "ConnectivityCheckerPro/ConnectivityCheckerPro_Sample6000": "CCP-S60",
    "ConnectivityCheckerPro/ConnectivityCheckerPro_Sample6000_3_2f1": "CCP-S63",
    "DevAccelerationSystem/DevAccelerationSystem": "DAS-SRC",
    "DevAccelerationSystem/DevAccelerationSystem.DemoProject": "DAS-DEMO",
}

BANNED_PACKAGES = {
    "com.unity.analytics",
    "com.unity.collab-proxy",
    "com.unity.services.analytics",
    "com.unity.modules.unityanalytics",
    "com.unity.version-control",
}

IDENTITY_FIELDS = (
    "companyName",
    "productName",
    "applicationIdentifier",
    "metroPackageName",
    "metroApplicationDescription",
)

FORBIDDEN_IDENTITY_MARKERS = (
    "ConnectivityChecker",
    "ConnectivityTest",
    "DevAcceleration",
)

FORBIDDEN_PROJECT_SETTINGS_MARKERS = (
    "ConnectivityCheckerPro",
    "ConnectivityTestUnity2022",
    "DevAccelerationSystem",
    "DefaultCompany",
    "com.DefaultCompany",
    "2D_BuiltInRenderer",
)


def scalar(text: str, key: str) -> str | None:
    prefix = f"  {key}:"
    for line in text.splitlines():
        if line.startswith(prefix):
            return line[len(prefix) :].strip()
    return None


def check_project(root: Path, relative: str, codename: str) -> list[str]:
    failures: list[str] = []
    project = root / relative
    player_path = project / "ProjectSettings/ProjectSettings.asset"
    connect_path = project / "ProjectSettings/UnityConnectSettings.asset"

    if not player_path.is_file() or not connect_path.is_file():
        return [f"{codename}: required ProjectSettings files are missing"]

    player = player_path.read_text(encoding="utf-8")
    connect = connect_path.read_text(encoding="utf-8")

    expected_scalars = {
        "companyName": "FD",
        "productName": codename,
        "submitAnalytics": "0",
        "cloudProjectId": "",
        "projectName": "",
        "organizationId": "",
        "cloudEnabled": "0",
    }
    for key, expected in expected_scalars.items():
        actual = scalar(player, key)
        if actual != expected:
            failures.append(f"{codename}: {key}={actual!r}, expected {expected!r}")

    if "  cloudServicesEnabled: {}" not in player:
        failures.append(f"{codename}: cloudServicesEnabled is not empty")

    visible_lines = []
    capture_identifiers = False
    for line in player.splitlines():
        stripped = line.strip()
        if any(stripped.startswith(f"{field}:") for field in IDENTITY_FIELDS):
            visible_lines.append(stripped)
            capture_identifiers = stripped == "applicationIdentifier:"
            continue
        if capture_identifiers and line.startswith("    "):
            visible_lines.append(stripped)
        elif capture_identifiers and not line.startswith("    "):
            capture_identifiers = False
    visible_identity = "\n".join(visible_lines)
    for marker in FORBIDDEN_IDENTITY_MARKERS:
        if marker.lower() in visible_identity.lower():
            failures.append(f"{codename}: Unity-visible identity contains forbidden marker {marker}")

    settings_root = project / "ProjectSettings"
    for settings_path in sorted(path for path in settings_root.rglob("*") if path.is_file()):
        try:
            settings_text = settings_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for marker in FORBIDDEN_PROJECT_SETTINGS_MARKERS:
            if marker.lower() in settings_text.lower():
                failures.append(
                    f"{codename}: {settings_path.relative_to(project)} contains legacy identity marker {marker}"
                )

    for line in connect.splitlines():
        stripped = line.strip()
        if stripped.startswith("m_Enabled:") and stripped != "m_Enabled: 0":
            failures.append(f"{codename}: Unity service is enabled")
        if stripped.startswith("m_InitializeOnStartup:") and stripped != "m_InitializeOnStartup: 0":
            failures.append(f"{codename}: Unity service initializes on startup")

    for package_file in (project / "Packages/manifest.json", project / "Packages/packages-lock.json"):
        if not package_file.is_file():
            continue
        package_data = json.loads(package_file.read_text(encoding="utf-8"))
        dependencies = package_data.get("dependencies", package_data)
        present = BANNED_PACKAGES.intersection(dependencies)
        if present:
            failures.append(f"{codename}: banned Unity Cloud packages present: {sorted(present)}")

    return failures


def check_editor_analytics() -> list[str]:
    if platform.system() != "Darwin":
        return ["host: Editor Analytics opt-out can only be proven automatically on macOS"]
    failures = []
    for key in ("EnableEditorAnalytics", "EnableEditorAnalyticsV2"):
        result = subprocess.run(
            ["defaults", "read", "com.unity3d.UnityEditor5.x", key],
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0 or result.stdout.strip() != "0":
            failures.append(f"host: {key} is not disabled")
    return failures


def check_hub_records(root: Path) -> list[str]:
    database = Path.home() / "Library/Application Support/UnityHub/projects-v1.json"
    if not database.is_file():
        return []
    data = json.loads(database.read_text(encoding="utf-8")).get("data", {})
    failures = []
    root_prefix = f"{root.resolve()}/"
    for project_path, record in data.items():
        if not project_path.startswith(root_prefix):
            continue
        if record.get("cloudEnabled"):
            failures.append("host: a Hub checkout project has cloudEnabled=true")
        if record.get("cloudProjectId") or record.get("organizationId"):
            failures.append("host: a Hub checkout project has a Cloud identity")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--require-host-opt-out", action="store_true")
    args = parser.parse_args()

    root = args.root.resolve()
    failures = []
    for relative, codename in PROJECTS.items():
        failures.extend(check_project(root, relative, codename))
    if args.require_host_opt_out:
        failures.extend(check_editor_analytics())
        failures.extend(check_hub_records(root))

    result = {
        "status": "fail" if failures else "pass",
        "projects_checked": len(PROJECTS),
        "host_opt_out_checked": args.require_host_opt_out,
        "failures": failures,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
