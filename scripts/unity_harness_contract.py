#!/usr/bin/env python3
"""Deterministic current-tree contracts for the Unity Unified Harness."""

from __future__ import annotations

import json
import os
import re
import subprocess
from collections import Counter
from pathlib import Path, PurePosixPath
from typing import Any


TOPOLOGY_PATH = "AIOutput/Registry/host_topology.yaml"
EXPECTED_CONSUMER_COUNT = 7
EXPECTED_PROJECT_ROLES = {
    "CCP-PUB": ("ConnectivityCheckerPro", "source"),
    "CCP-S21": ("ConnectivityCheckerPro", "unsupported"),
    "CCP-S22": ("ConnectivityCheckerPro", "consumer"),
    "CCP-S60": ("ConnectivityCheckerPro", "consumer"),
    "CCP-S63": ("ConnectivityCheckerPro", "consumer"),
    "DAS-SRC": ("DevAccelerationSystem", "source"),
    "DAS-DEMO": ("DevAccelerationSystem", "demo"),
}
EXPECTED_ROLE_COUNTS = {"source": 2, "consumer": 3, "unsupported": 1, "demo": 1}
EXPECTED_BOUNDARY_IDS = {"root", "AIRoot", "ConnectivityCheckerPro", "DevAccelerationSystem", "MCP"}

PROJECT_FIELDS = {
    "id", "path", "git_boundary", "role", "project_kind", "router",
    "unity_version", "mcp_consumer", "privacy_check", "standalone",
    "release_proof", "context_sample",
}
BOUNDARY_FIELDS = {
    "id", "path", "parent", "gitlink", "router", "kernel", "adapter",
    "generator", "standalone",
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

DOCUMENT_BUDGETS = {
    "hub-kernel": ("AIOutput/Harness/KERNEL.md", 30, 80, 4_096),
    "change-delivery": ("AIRoot/Modules/XUUnity/tasks/change_delivery.md", None, 250, 24_576),
    "impact-review": (
        "AIRoot/Modules/XUUnity/reviews/post_implementation_impact_review.md",
        None,
        160,
        8_192,
    ),
}

ROUTE_TARGETS = {
    "KERNEL.md": "AIOutput/Harness/KERNEL.md",
    "post_implementation_impact_review.md": (
        "AIRoot/Modules/XUUnity/reviews/post_implementation_impact_review.md"
    ),
}

ACTIVE_TOPOLOGY_TEXT_FILES = (
    "AGENTS.md",
    "WORKSPACE.md",
    "AIOutput/Registry/host_topology.yaml",
    "AIOutput/Registry/setup_status.yaml",
    "AIModules/XUUnityInternal/start_session.md",
    "AIModules/XUUnityInternal/knowledge/host_topology.md",
    "AIModules/XUUnityInternal/knowledge/validation_paths.md",
    "scripts/refresh-aifoxster-hub.sh",
    "AIFoxsterDevHub.sln",
)


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


def _yaml_value(raw: str) -> str:
    value = raw.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    return value


def parse_yaml_scalars(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line or line[0].isspace() or ":" not in line:
            continue
        key, raw = line.split(":", 1)
        if not raw.strip():
            continue
        if key in values:
            raise ValueError(f"duplicate top-level YAML scalar: {key}")
        values[key] = _yaml_value(raw)
    return values


def parse_yaml_list(path: Path, key: str) -> list[str]:
    values: list[str] = []
    active = False
    for line in path.read_text(encoding="utf-8").splitlines():
        if line == f"{key}:":
            active = True
            continue
        if active and line and not line.startswith(" "):
            break
        if active and line.startswith("  - "):
            values.append(_yaml_value(line[4:]))
    return values


def parse_yaml_blocks(path: Path, key: str) -> list[dict[str, str]]:
    blocks: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    active = False
    for line in path.read_text(encoding="utf-8").splitlines():
        if line == f"{key}:":
            active = True
            continue
        if active and line and not line.startswith(" "):
            break
        if not active or not line.strip() or line.lstrip().startswith("#"):
            continue
        if line.startswith("  - "):
            if current is not None:
                blocks.append(current)
            current = {}
            item = line[4:]
            if ":" not in item:
                raise ValueError(f"{key}: list item must start a mapping: {line!r}")
            field, raw = item.split(":", 1)
            current[field.strip()] = _yaml_value(raw)
        elif line.startswith("    ") and current is not None and ":" in line:
            field, raw = line.strip().split(":", 1)
            field = field.strip()
            if field in current:
                raise ValueError(f"{key}: duplicate field {field!r}")
            current[field] = _yaml_value(raw)
        elif line.strip():
            raise ValueError(f"{key}: unsupported YAML shape: {line!r}")
    if current is not None:
        blocks.append(current)
    return blocks


def load_topology(root: Path) -> dict[str, Any]:
    path = root / TOPOLOGY_PATH
    return {
        "path": path,
        "scalars": parse_yaml_scalars(path),
        "boundaries": parse_yaml_blocks(path, "git_boundaries"),
        "projects": parse_yaml_blocks(path, "project_contracts"),
        "routed_projects": parse_yaml_list(path, "routed_projects"),
        "optional_projects": parse_yaml_blocks(path, "optional_local_projects"),
        "operations": parse_yaml_blocks(path, "routed_operation_projects"),
    }


def _bool(record: dict[str, str], field: str) -> bool:
    value = record.get(field)
    if value not in {"true", "false"}:
        raise ValueError(f"{record.get('id', '<record>')}: {field} must be true or false")
    return value == "true"


def _relative(value: str, *, allow_dot: bool = False) -> bool:
    path = PurePosixPath(value)
    return bool(value) and not path.is_absolute() and ".." not in path.parts and (
        allow_dot or value != "."
    ) and path.as_posix() == value


def boundary_map(topology: dict[str, Any]) -> dict[str, dict[str, str]]:
    return {record["id"]: record for record in topology["boundaries"] if "id" in record}


def project_records(topology: dict[str, Any], flag: str | None = None) -> list[dict[str, str]]:
    records = list(topology["projects"])
    if flag is None:
        return records
    selected = []
    for record in records:
        if _bool(record, flag):
            selected.append(record)
    return selected


def _project_version(path: Path) -> str | None:
    if not path.is_file():
        return None
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("m_EditorVersion: "):
            return line.split(":", 1)[1].strip()
    return None


def validate_topology(root: Path) -> tuple[dict[str, Any], list[str]]:
    failures: list[str] = []
    try:
        topology = load_topology(root)
    except (OSError, ValueError) as error:
        return {}, [f"topology could not be parsed: {error}"]

    scalars = topology["scalars"]
    if scalars.get("schema_version") != "3":
        failures.append("topology schema_version must be 3")
    if scalars.get("topology_owner") != TOPOLOGY_PATH:
        failures.append(f"topology_owner must be {TOPOLOGY_PATH}")

    projects = topology["projects"]
    ids = [record.get("id", "") for record in projects]
    paths = [record.get("path", "") for record in projects]
    if len(projects) != EXPECTED_CONSUMER_COUNT:
        failures.append(
            f"project denominator is {len(projects)}, expected {EXPECTED_CONSUMER_COUNT}"
        )
    if len(ids) != len(set(ids)) or set(ids) != set(EXPECTED_PROJECT_ROLES):
        failures.append(f"project IDs are not the exact code-owned set: {ids}")
    if len(paths) != len(set(paths)):
        failures.append("project paths must be unique")

    roles: Counter[str] = Counter()
    boundaries: Counter[str] = Counter()
    for record in projects:
        identity = record.get("id", "<missing-id>")
        missing = PROJECT_FIELDS - set(record)
        unknown = set(record) - PROJECT_FIELDS
        if missing or unknown:
            failures.append(f"{identity}: project fields missing={sorted(missing)} unknown={sorted(unknown)}")
            continue
        expected = EXPECTED_PROJECT_ROLES.get(identity)
        if expected and (record["git_boundary"], record["role"]) != expected:
            failures.append(
                f"{identity}: boundary/role is {(record['git_boundary'], record['role'])}, expected {expected}"
            )
        roles[record["role"]] += 1
        boundaries[record["git_boundary"]] += 1
        if not _relative(record["path"]):
            failures.append(f"{identity}: invalid project path {record['path']!r}")
            continue
        if record["git_boundary"] == "ConnectivityCheckerPro" and not Path(record["path"]).name.startswith("CCP_"):
            failures.append(f"{identity}: Connectivity project must use current CCP_* topology")
        expected_router = f"{record['path']}/AGENTS.md"
        if record["router"] != expected_router:
            failures.append(f"{identity}: router must be {expected_router}")
        project = root / record["path"]
        if not project.is_dir():
            failures.append(f"{identity}: project directory is missing: {record['path']}")
        if not (root / record["router"]).is_file():
            failures.append(f"{identity}: active router is missing: {record['router']}")
        actual_version = _project_version(project / "ProjectSettings/ProjectVersion.txt")
        if actual_version != record["unity_version"]:
            failures.append(
                f"{identity}: Unity version is {actual_version!r}, expected {record['unity_version']!r}"
            )
        try:
            mcp_consumer = _bool(record, "mcp_consumer")
            privacy_check = _bool(record, "privacy_check")
            release_proof = _bool(record, "release_proof")
            _bool(record, "standalone")
            _bool(record, "context_sample")
        except ValueError as error:
            failures.append(str(error))
            continue
        if not mcp_consumer or not privacy_check:
            failures.append(f"{identity}: every active project must participate in MCP and privacy proof")
        if release_proof == (record["role"] == "unsupported"):
            failures.append(f"{identity}: release_proof contradicts role {record['role']}")

    if dict(roles) != EXPECTED_ROLE_COUNTS:
        failures.append(f"project role denominator is {dict(roles)}, expected {EXPECTED_ROLE_COUNTS}")
    if boundaries != Counter({"ConnectivityCheckerPro": 5, "DevAccelerationSystem": 2}):
        failures.append(f"project boundary denominator is {dict(boundaries)}, expected Connectivity=5/DAS=2")
    try:
        context_samples = [record for record in projects if _bool(record, "context_sample")]
    except ValueError:
        context_samples = []
    sample_pairs = {(record.get("git_boundary"), record.get("role")) for record in context_samples}
    if sample_pairs != {("ConnectivityCheckerPro", "consumer"), ("DevAccelerationSystem", "demo")}:
        failures.append("context_sample must select one Connectivity consumer and the DAS demo")

    if topology["routed_projects"] != paths:
        failures.append("routed_projects compatibility projection must exactly match project_contracts order")

    boundaries_list = topology["boundaries"]
    boundary_ids = [record.get("id", "") for record in boundaries_list]
    if len(boundary_ids) != len(set(boundary_ids)) or set(boundary_ids) != EXPECTED_BOUNDARY_IDS:
        failures.append(f"git boundary IDs are not exact: {boundary_ids}")
    for record in boundaries_list:
        identity = record.get("id", "<missing-id>")
        missing = BOUNDARY_FIELDS - set(record)
        unknown = set(record) - BOUNDARY_FIELDS
        if missing or unknown:
            failures.append(f"{identity}: boundary fields missing={sorted(missing)} unknown={sorted(unknown)}")
            continue
        if not _relative(record["path"], allow_dot=True):
            failures.append(f"{identity}: invalid boundary path {record['path']!r}")
        try:
            _bool(record, "standalone")
        except ValueError as error:
            failures.append(str(error))
        for field in ("router", "kernel", "adapter", "generator"):
            target = record[field]
            if target != "none" and (not _relative(target) or not (root / target).exists()):
                failures.append(f"{identity}: advertised {field} target is missing or invalid: {target}")

    expected_relations = {
        "root": (".", "none", "none"),
        "AIRoot": ("AIRoot", "root", "AIRoot"),
        "ConnectivityCheckerPro": ("ConnectivityCheckerPro", "root", "ConnectivityCheckerPro"),
        "DevAccelerationSystem": ("DevAccelerationSystem", "root", "DevAccelerationSystem"),
        "MCP": ("AIRoot/Operations/XUUnityLightUnityMcp", "AIRoot", "Operations/XUUnityLightUnityMcp"),
    }
    for identity, expected in expected_relations.items():
        record = boundary_map(topology).get(identity)
        if record and (record.get("path"), record.get("parent"), record.get("gitlink")) != expected:
            failures.append(f"{identity}: path/parent/gitlink relation is not canonical")

    setup = root / "AIOutput/Registry/setup_status.yaml"
    try:
        setup_text = setup.read_text(encoding="utf-8")
        setup_scalars = parse_yaml_scalars(setup)
        if re.search(r"^routed_projects:\s*$", setup_text, re.MULTILINE):
            failures.append("setup_status.yaml must not own a competing routed_projects list")
        if setup_scalars.get("topology_source") != TOPOLOGY_PATH:
            failures.append("setup_status.yaml must point to the topology owner")
    except OSError as error:
        failures.append(f"setup status could not be read: {error}")

    return topology, failures


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
        return errors + ["lock entry must be an object"]
    if lock_entry.get("version") != expected_url:
        errors.append(f"lock version is {lock_entry.get('version')!r}, expected {expected_url!r}")
    if lock_entry.get("hash") != expected_hash:
        errors.append(f"lock hash is {lock_entry.get('hash')!r}, expected {expected_hash!r}")
    if lock_entry.get("source") != "git" or lock_entry.get("depth") != 0:
        errors.append("lock source/depth is not exact git depth 0")
    return errors


def validate_mcp_contract(root: Path, topology: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    failures: list[str] = []
    boundaries = boundary_map(topology)
    for record in topology["boundaries"]:
        if record.get("parent") == "none":
            continue
        parent = boundaries.get(record.get("parent", ""))
        if not parent:
            failures.append(f"{record.get('id')}: unknown parent boundary")
            continue
        try:
            verify_gitlink(root / parent["path"], record["gitlink"], root / record["path"])
        except (OSError, ValueError) as error:
            failures.append(str(error))

    mcp_record = boundaries.get("MCP", {})
    mcp = root / mcp_record.get("path", "AIRoot/Operations/XUUnityLightUnityMcp")
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
                f"MCP release tag {tag} is not annotated and peeled to HEAD: type={tag_type}, peeled={peeled}, head={head}"
            )
    except ValueError as error:
        failures.append(str(error))

    expected_url = (
        "https://github.com/FoxsterDev/xuunity-mcp.git"
        f"?path=/packages/com.xuunity.light-mcp#{tag}"
    )
    consumers = project_records(topology, "mcp_consumer")
    passing = 0
    for record in consumers:
        try:
            errors = validate_consumer_pin(root / record["path"], expected_url, head)
        except (OSError, ValueError, json.JSONDecodeError) as error:
            errors = [str(error)]
        if errors:
            failures.extend(f"{record['id']} ({record['path']}): {error}" for error in errors)
        else:
            passing += 1
    if len(consumers) != EXPECTED_CONSUMER_COUNT:
        failures.append(f"MCP consumer denominator is {len(consumers)}, expected {EXPECTED_CONSUMER_COUNT}")

    facts = {
        "tag": tag,
        "tag_object": tag_object,
        "commit": head,
        "package_version": version,
        "package_hash": head,
        "consumer_url": expected_url,
        "consumers_passed": passing,
        "consumers_total": len(consumers),
    }
    return facts, failures


def context_scenarios(topology: dict[str, Any]) -> dict[str, tuple[str, ...]]:
    boundaries = boundary_map(topology)
    ccp = boundaries["ConnectivityCheckerPro"]
    das = boundaries["DevAccelerationSystem"]
    airroot = boundaries["AIRoot"]
    mcp = boundaries["MCP"]
    ccp_sample = next(
        record for record in project_records(topology, "context_sample")
        if record["git_boundary"] == "ConnectivityCheckerPro"
    )
    das_sample = next(
        record for record in project_records(topology, "context_sample")
        if record["git_boundary"] == "DevAccelerationSystem"
    )
    return {
        "hub-root": ("AGENTS.md", "AIOutput/Harness/KERNEL.md"),
        "airroot": (airroot["router"],),
        "connectivity-root": (ccp["router"], ccp["kernel"], ccp["adapter"]),
        "connectivity-consumer": (ccp["router"], ccp["kernel"], ccp["adapter"], ccp_sample["router"]),
        "devaccel-root": (das["router"], das["adapter"]),
        "devaccel-demo": (das["router"], das["adapter"], das_sample["router"]),
        "mcp-standalone": (mcp["router"],),
        "mcp-host-mounted": ("AGENTS.md", "AIOutput/Harness/KERNEL.md", airroot["router"], mcp["router"]),
    }


def assess_budget(
    label: str,
    lines: int,
    size: int,
    *,
    line_min: int | None,
    line_max: int,
    byte_ceiling: int,
) -> tuple[list[str], list[str]]:
    """Treat shape as advisory and bytes as the deterministic hard boundary."""
    warnings: list[str] = []
    failures: list[str] = []
    if (line_min is not None and lines < line_min) or lines > line_max:
        target = f"{line_min}-{line_max}" if line_min is not None else f"at most {line_max}"
        warnings.append(f"{label}: {lines} lines is outside advisory {target}; {size}/{byte_ceiling} bytes")
    if size > byte_ceiling:
        failures.append(f"{label}: {size} bytes exceeds hard {byte_ceiling}-byte ceiling")
    return warnings, failures


def measure_context(
    root: Path, topology: dict[str, Any]
) -> tuple[dict[str, Any], list[str], list[str]]:
    measurements: dict[str, Any] = {}
    warnings: list[str] = []
    failures: list[str] = []
    for scenario, relatives in context_scenarios(topology).items():
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
        shape_warnings, shape_failures = assess_budget(
            scenario, lines, size, line_min=None, line_max=line_budget, byte_ceiling=byte_budget
        )
        warnings.extend(shape_warnings)
        failures.extend(shape_failures)
        measurements[scenario] = {
            "files": list(relatives), "lines": lines, "bytes": size,
            "line_advisory": line_budget, "byte_ceiling": byte_budget,
        }
    return measurements, warnings, failures


def measure_documents(root: Path) -> tuple[dict[str, Any], list[str], list[str]]:
    measurements: dict[str, Any] = {}
    warnings: list[str] = []
    failures: list[str] = []
    for label, (relative, minimum, maximum, byte_ceiling) in DOCUMENT_BUDGETS.items():
        path = root / relative
        if not path.is_file():
            failures.append(f"{label}: missing document {relative}")
            continue
        content = path.read_bytes()
        lines, size = len(content.splitlines()), len(content)
        shape_warnings, shape_failures = assess_budget(
            label, lines, size, line_min=minimum, line_max=maximum, byte_ceiling=byte_ceiling
        )
        warnings.extend(shape_warnings)
        failures.extend(shape_failures)
        measurements[label] = {
            "path": relative, "lines": lines, "bytes": size,
            "line_min": minimum, "line_max": maximum, "byte_ceiling": byte_ceiling,
        }
    return measurements, warnings, failures


def _markdown_sections(path: Path) -> list[tuple[str, str]]:
    sections: list[tuple[str, str]] = []
    heading: str | None = None
    body: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            if heading is not None:
                normalized = "\n".join(part.strip() for part in body).strip()
                if len(normalized) >= 120:
                    sections.append((heading, normalized))
            heading, body = line[3:].strip(), []
        elif heading is not None:
            body.append(line)
    if heading is not None:
        normalized = "\n".join(part.strip() for part in body).strip()
        if len(normalized) >= 120:
            sections.append((heading, normalized))
    return sections


def duplicate_semantic_sections(root: Path, relatives: tuple[str, ...]) -> list[str]:
    owners: dict[str, list[str]] = {}
    for relative in relatives:
        path = root / relative
        if not path.is_file():
            continue
        for heading, body in _markdown_sections(path):
            owners.setdefault(body, []).append(f"{relative}##{heading}")
    return [f"exact repeated canonical semantic section: {items}" for items in owners.values() if len(items) > 1]


def route_contract_failures(root: Path, topology: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    boundaries = boundary_map(topology)
    requirements = {
        "AIRoot": ("KERNEL.md", "post_implementation_impact_review.md", "standalone", "fallback"),
        "ConnectivityCheckerPro": ("KERNEL.md", "post_implementation_impact_review.md", "standalone", "fallback"),
        "DevAccelerationSystem": ("KERNEL.md", "post_implementation_impact_review.md", "standalone", "fallback"),
    }
    route_files: list[tuple[str, str]] = [("root", "AGENTS.md")]
    for identity, markers in requirements.items():
        record = boundaries.get(identity, {})
        paths = [record.get("router", ""), record.get("adapter", "")]
        route_files.extend(
            (identity, path) for path in paths if path and path != "none"
        )
        text = "\n".join(
            (root / path).read_text(encoding="utf-8")
            for path in paths if path and path != "none" and (root / path).is_file()
        ).lower()
        for marker in markers:
            if marker.lower() not in text:
                failures.append(f"{identity}: routing contract missing marker {marker!r}")
    root_router = (root / "AGENTS.md").read_text(encoding="utf-8") if (root / "AGENTS.md").is_file() else ""
    if "post_implementation_impact_review.md" not in root_router:
        failures.append("root router does not route the compact runtime final pass")
    for identity, relative in sorted(set(route_files)):
        source = root / relative
        if not source.is_file():
            continue
        for advertised in re.findall(r"`([^`\n]+)`", source.read_text(encoding="utf-8")):
            for suffix, expected_relative in ROUTE_TARGETS.items():
                if not advertised.endswith(suffix):
                    continue
                actual = Path(os.path.normpath(str(source.parent / advertised)))
                expected = Path(os.path.normpath(str(root / expected_relative)))
                if actual != expected or not expected.is_file():
                    failures.append(
                        f"{identity}: advertised route {advertised!r} from {relative} "
                        f"does not resolve to {expected_relative}"
                    )
    return failures


def legacy_active_path_failures(root: Path) -> list[str]:
    marker = "ConnectivityCheckerPro/" + "ConnectivityCheckerPro_"
    failures: list[str] = []
    for relative in ACTIVE_TOPOLOGY_TEXT_FILES:
        path = root / relative
        if path.is_file() and marker in path.read_text(encoding="utf-8", errors="replace"):
            failures.append(f"active file contains removed long-form Connectivity path: {relative}")
    return failures
