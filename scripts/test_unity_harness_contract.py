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
    load_topology,
    load_json,
    select_release_tag,
    validate_consumer_pin,
    validate_topology,
)


EXPECTED_URL = (
    "https://github.com/FoxsterDev/xuunity-mcp.git"
    "?path=/packages/com.xuunity.light-mcp#v9.8.7"
)
EXPECTED_HASH = "a" * 40
ROOT = Path(__file__).resolve().parents[1]


class HarnessContractTests(unittest.TestCase):
    def make_consumer(self, manifest_pin: str = EXPECTED_URL, lock_hash: str = EXPECTED_HASH) -> Path:
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
                    "depth": 0,
                    "source": "git",
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


if __name__ == "__main__":
    unittest.main()
