#!/usr/bin/env python3
"""Mutation tests for current-tree Unity Harness contracts."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from unity_harness_contract import (
    DuplicateKeyError,
    load_json,
    select_release_tag,
    validate_consumer_pin,
)


EXPECTED_URL = (
    "https://github.com/FoxsterDev/xuunity-mcp.git"
    "?path=/packages/com.xuunity.light-mcp#v9.8.7"
)
EXPECTED_HASH = "a" * 40


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


if __name__ == "__main__":
    unittest.main()
