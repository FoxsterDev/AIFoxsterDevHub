#!/usr/bin/env python3
"""Mutation tests for current-tree Unity Harness contracts."""

from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from unity_harness_contract import (
    DuplicateKeyError,
    assess_budget,
    duplicate_semantic_sections,
    legacy_active_path_failures,
    load_topology,
    load_json,
    select_release_tag,
    validate_consumer_pin,
    validate_topology,
    workspace_topology_mirror_failures,
)


EXPECTED_URL = (
    "https://github.com/FoxsterDev/xuunity-mcp.git"
    "?path=/packages/com.xuunity.light-mcp#v9.8.7"
)
EXPECTED_HASH = "a" * 40
ROOT = Path(__file__).resolve().parents[1]


class HarnessContractTests(unittest.TestCase):
    def make_consumer(
        self,
        manifest_pin: str = EXPECTED_URL,
        lock_hash: str = EXPECTED_HASH,
        *,
        lock_source: str = "git",
        lock_depth: int | bool = 0,
    ) -> Path:
        temporary = tempfile.TemporaryDirectory(prefix="unity-harness-contract-")
        self.addCleanup(temporary.cleanup)
        project = Path(temporary.name)
        packages = project / "Packages"
        packages.mkdir()
        manifest = {"dependencies": {"com.xuunity.light-mcp": manifest_pin}}
        lock = {
            "dependencies": {
                "com.xuunity.light-mcp": {
                    "version": manifest_pin,
                    "depth": lock_depth,
                    "source": lock_source,
                    "hash": lock_hash,
                }
            }
        }
        (packages / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
        (packages / "packages-lock.json").write_text(json.dumps(lock), encoding="utf-8")
        return project

    def test_current_exact_consumer_contract_passes(self) -> None:
        self.assertEqual(validate_consumer_pin(self.make_consumer(), EXPECTED_URL, EXPECTED_HASH), [])

    def test_stale_tag_and_consumer_pin_fail(self) -> None:
        stale = EXPECTED_URL.replace("v9.8.7", "v9.8.6")
        errors = validate_consumer_pin(self.make_consumer(manifest_pin=stale), EXPECTED_URL, EXPECTED_HASH)
        self.assertTrue(any("manifest pin" in error for error in errors))
        self.assertTrue(any("lock version" in error for error in errors))

    def test_stale_lock_hash_fails(self) -> None:
        errors = validate_consumer_pin(self.make_consumer(lock_hash="b" * 40), EXPECTED_URL, EXPECTED_HASH)
        self.assertTrue(any("lock hash" in error for error in errors))

    def test_lock_source_and_depth_require_exact_json_types(self) -> None:
        for source, depth in (("registry", 0), ("git", False), ("git", 1)):
            with self.subTest(source=source, depth=depth):
                errors = validate_consumer_pin(
                    self.make_consumer(lock_source=source, lock_depth=depth),
                    EXPECTED_URL,
                    EXPECTED_HASH,
                )
                self.assertTrue(any("source/depth" in error for error in errors))

    def test_non_exact_release_tag_fails(self) -> None:
        with self.assertRaisesRegex(ValueError, "not exact stable tag"):
            select_release_tag(["v9.8.6"], "9.8.7")

    def test_duplicate_json_key_fails(self) -> None:
        temporary = tempfile.TemporaryDirectory(prefix="unity-harness-json-")
        self.addCleanup(temporary.cleanup)
        path = Path(temporary.name) / "duplicate.json"
        path.write_text('{"dependencies": {}, "dependencies": {}}', encoding="utf-8")
        with self.assertRaises(DuplicateKeyError):
            load_json(path)

    def test_203_lines_under_byte_ceiling_warns_and_passes(self) -> None:
        warnings, failures = assess_budget(
            "connectivity-root", 203, 9_180,
            line_min=None, line_max=200, byte_ceiling=10_000,
        )
        self.assertEqual(1, len(warnings))
        self.assertEqual([], failures)

    def test_byte_ceiling_overflow_remains_hard(self) -> None:
        warnings, failures = assess_budget(
            "connectivity-root", 199, 10_001,
            line_min=None, line_max=200, byte_ceiling=10_000,
        )
        self.assertEqual([], warnings)
        self.assertTrue(any("hard" in failure for failure in failures))

    def test_exact_repeated_canonical_section_fails(self) -> None:
        temporary = tempfile.TemporaryDirectory(prefix="unity-harness-sections-")
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        body = "same semantic owner " * 12
        (root / "one.md").write_text(f"## Owner One\n\n{body}\n", encoding="utf-8")
        (root / "two.md").write_text(f"## Owner Two\n\n{body}\n", encoding="utf-8")
        errors = duplicate_semantic_sections(root, ("one.md", "two.md"))
        self.assertTrue(any("exact repeated" in error for error in errors))

    def test_current_topology_resolves_five_ccp_projects(self) -> None:
        topology = load_topology(ROOT)
        ccp = [
            record for record in topology["projects"]
            if record["git_boundary"] == "ConnectivityCheckerPro"
        ]
        self.assertEqual(5, len(ccp))
        self.assertTrue(all(Path(record["path"]).name.startswith("CCP_") for record in ccp))

    def test_wrong_role_or_denominator_fails_the_actual_validator(self) -> None:
        topology = load_topology(ROOT)
        wrong_role = copy.deepcopy(topology)
        wrong_role["projects"][2]["role"] = "source"
        with mock.patch("unity_harness_contract.load_topology", return_value=wrong_role):
            _, errors = validate_topology(ROOT)
        self.assertTrue(any("boundary/role" in error or "role denominator" in error for error in errors))

        missing = copy.deepcopy(topology)
        missing["projects"].pop()
        with mock.patch("unity_harness_contract.load_topology", return_value=missing):
            _, errors = validate_topology(ROOT)
        self.assertTrue(any("denominator" in error for error in errors))

    def test_duplicate_topology_section_key_is_rejected(self) -> None:
        temporary = tempfile.TemporaryDirectory(prefix="unity-harness-duplicate-section-")
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        topology_path = root / "AIOutput/Registry/host_topology.yaml"
        topology_path.parent.mkdir(parents=True)
        topology_path.write_text(
            (ROOT / "AIOutput/Registry/host_topology.yaml").read_text(encoding="utf-8")
            + "\nproject_contracts:\n"
            + "  - id: contradictory\n",
            encoding="utf-8",
        )
        with self.assertRaisesRegex(ValueError, "duplicate top-level YAML key 'project_contracts'"):
            load_topology(root)

    def test_context_sample_denominator_rejects_duplicate_pair(self) -> None:
        topology = load_topology(ROOT)
        duplicate = copy.deepcopy(topology)
        extra = next(record for record in duplicate["projects"] if record["id"] == "CCP-S60")
        extra["context_sample"] = "true"
        with mock.patch("unity_harness_contract.load_topology", return_value=duplicate):
            _, errors = validate_topology(ROOT)
        self.assertTrue(any("context_sample" in error for error in errors))

    def test_missing_router_and_stale_long_form_path_fail(self) -> None:
        topology = load_topology(ROOT)
        missing_router = copy.deepcopy(topology)
        missing_router["projects"][0]["router"] = "ConnectivityCheckerPro/CCP_PUB/NO_ROUTER.md"
        with mock.patch("unity_harness_contract.load_topology", return_value=missing_router):
            _, errors = validate_topology(ROOT)
        self.assertTrue(any("router" in error for error in errors))

        stale = copy.deepcopy(topology)
        stale["projects"][2]["path"] = (
            "ConnectivityCheckerPro/" + "ConnectivityCheckerPro_Sample2022"
        )
        with mock.patch("unity_harness_contract.load_topology", return_value=stale):
            _, errors = validate_topology(ROOT)
        self.assertTrue(any("CCP_*" in error or "missing" in error for error in errors))

    def test_solution_backslashes_do_not_hide_removed_long_form_paths(self) -> None:
        temporary = tempfile.TemporaryDirectory(prefix="unity-harness-legacy-solution-")
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        (root / "AIFoxsterDevHub.sln").write_text(
            "ConnectivityCheckerPro\\ConnectivityCheckerPro_Sample2022\\Project.csproj\n",
            encoding="utf-8",
        )
        self.assertEqual(
            [
                "active file contains removed Connectivity names "
                "['ConnectivityCheckerPro/ConnectivityCheckerPro_', 'Sample2022']: "
                "AIFoxsterDevHub.sln"
            ],
            legacy_active_path_failures(root),
        )

    def test_child_adapter_rejects_bare_removed_project_names(self) -> None:
        temporary = tempfile.TemporaryDirectory(prefix="unity-harness-legacy-adapter-")
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        adapter = root / "ConnectivityCheckerPro/Harness/unity-adapter.md"
        adapter.parent.mkdir(parents=True)
        adapter.write_text("Use Sample6000_3_2f1 and Sample2021.\n", encoding="utf-8")
        errors = legacy_active_path_failures(root)
        self.assertEqual(1, len(errors))
        self.assertIn("Sample6000_3_2f1", errors[0])
        self.assertIn("Sample2021", errors[0])
        self.assertIn("ConnectivityCheckerPro/Harness/unity-adapter.md", errors[0])

    def test_workspace_mirror_requires_exact_prefixed_das_paths(self) -> None:
        temporary = tempfile.TemporaryDirectory(prefix="unity-harness-workspace-mirror-")
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        text = (ROOT / "WORKSPACE.md").read_text(encoding="utf-8")
        text = text.replace(
            "`DevAccelerationSystem/DevAccelerationSystem.DemoProject`",
            "`DevAccelerationSystem.DemoProject`",
        ).replace(
            "`DevAccelerationSystem/DAS.LocalProject`",
            "`DAS.LocalProject`",
        )
        (root / "WORKSPACE.md").write_text(text, encoding="utf-8")
        errors = workspace_topology_mirror_failures(root, load_topology(ROOT))
        self.assertEqual(2, len(errors))
        self.assertTrue(any("DevAccelerationSystem.DemoProject" in error for error in errors))
        self.assertTrue(any("DAS.LocalProject" in error for error in errors))

    def test_inline_competing_setup_list_is_rejected(self) -> None:
        topology = load_topology(ROOT)
        temporary = tempfile.TemporaryDirectory(prefix="unity-harness-inline-setup-")
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        setup = root / "AIOutput/Registry/setup_status.yaml"
        setup.parent.mkdir(parents=True)
        setup.write_text(
            "topology_source: AIOutput/Registry/host_topology.yaml\n"
            "routed_projects: [stale/project]\n",
            encoding="utf-8",
        )
        with mock.patch("unity_harness_contract.load_topology", return_value=topology):
            _, errors = validate_topology(root)
        self.assertTrue(any("competing routed_projects" in error for error in errors))

    def test_boundary_targets_and_project_paths_cannot_cross_boundaries(self) -> None:
        topology = load_topology(ROOT)
        cross_target = copy.deepcopy(topology)
        airroot = next(record for record in cross_target["boundaries"] if record["id"] == "AIRoot")
        airroot["router"] = "ConnectivityCheckerPro/AGENTS.md"
        with mock.patch("unity_harness_contract.load_topology", return_value=cross_target):
            _, errors = validate_topology(ROOT)
        self.assertTrue(any("outside declared boundary" in error for error in errors))

        cross_project = copy.deepcopy(topology)
        das = next(record for record in cross_project["projects"] if record["id"] == "DAS-SRC")
        das["path"] = "ConnectivityCheckerPro/CCP_PUB"
        das["router"] = "ConnectivityCheckerPro/CCP_PUB/AGENTS.md"
        with mock.patch("unity_harness_contract.load_topology", return_value=cross_project):
            _, errors = validate_topology(ROOT)
        self.assertTrue(any("outside git boundary" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
