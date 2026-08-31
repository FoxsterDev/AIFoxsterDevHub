#!/usr/bin/env python3
"""Regression tests for the static, narrowly scoped Unity Harness Stop hook."""

from __future__ import annotations

import io
import json
import unittest
from pathlib import Path
from unittest import mock

import harness_stop


class HarnessStopTests(unittest.TestCase):
    def test_root_untracked_and_rename_paths_are_parsed(self) -> None:
        output = "?? evals/unity-harness/new.json\0R  AIOutput/Harness/new.md\0AIOutput/Harness/old.md\0"
        self.assertEqual(
            harness_stop.parse_porcelain_z(output),
            ["evals/unity-harness/new.json", "AIOutput/Harness/new.md"],
        )

    def test_root_and_child_harness_paths_trigger(self) -> None:
        self.assertTrue(harness_stop.is_harness_path(Path("."), ".codex/hooks/harness_stop.py"))
        self.assertTrue(harness_stop.is_harness_path(Path("AIRoot"), "scripts/routing_audit.py"))
        self.assertTrue(
            harness_stop.is_harness_path(
                Path("ConnectivityCheckerPro"), "ConnectivityCheckerPro_Sample2022/AGENTS.md"
            )
        )

    def test_unrelated_product_and_marketing_paths_no_op(self) -> None:
        self.assertFalse(
            harness_stop.is_harness_path(
                Path("ConnectivityCheckerPro"), "Marketing/asset-store/artwork/unity_exports/key.png"
            )
        )
        self.assertFalse(
            harness_stop.is_harness_path(
                Path("DevAccelerationSystem"), "DevAccelerationSystem/Assets/Runtime/Feature.cs"
            )
        )

    @mock.patch.object(harness_stop, "changed_harness_paths", return_value=[])
    def test_unrelated_dirty_worktree_does_not_validate(self, changed: mock.Mock) -> None:
        with mock.patch.object(harness_stop, "run_validation") as validate:
            self.assertEqual(harness_stop.decision({}, Path("/repo")), {})
            validate.assert_not_called()
        changed.assert_called_once()

    @mock.patch.object(harness_stop, "changed_harness_paths", return_value=[".:AGENTS.md"])
    @mock.patch.object(harness_stop, "run_validation", return_value=(False, "bounded failure"))
    def test_scoped_failure_blocks_once(self, validate: mock.Mock, changed: mock.Mock) -> None:
        result = harness_stop.decision({}, Path("/repo"))
        self.assertEqual(result["decision"], "block")
        self.assertIn("bounded failure", result["reason"])
        self.assertEqual(harness_stop.decision({"stop_hook_active": True}, Path("/repo")), {})
        validate.assert_called_once()
        changed.assert_called_once()

    def test_validation_failure_output_is_bounded_to_tail(self) -> None:
        completed = harness_stop.subprocess.CompletedProcess(
            args=[], returncode=1, stdout="prefix" * 400, stderr="final-error"
        )
        with mock.patch.object(harness_stop.subprocess, "run", return_value=completed):
            passed, output = harness_stop.run_validation(Path("/repo"))
        self.assertFalse(passed)
        self.assertLessEqual(len(output), 1800)
        self.assertTrue(output.endswith("final-error"))

    def test_internal_fault_fails_open_with_warning(self) -> None:
        stdout = io.StringIO()
        with mock.patch.object(harness_stop.json, "load", side_effect=ValueError("broken input")):
            with mock.patch.object(harness_stop.sys, "stdout", stdout):
                self.assertEqual(harness_stop.main(), 0)
        payload = json.loads(stdout.getvalue())
        self.assertIn("systemMessage", payload)
        self.assertIn("broken input", payload["systemMessage"])


if __name__ == "__main__":
    unittest.main()
