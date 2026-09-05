#!/usr/bin/env python3
"""Regression tests for the static, topology-scoped Unity Harness Stop hook."""

from __future__ import annotations

import io
import json
import unittest
from pathlib import Path
from unittest import mock

import harness_stop


ROOT = Path(__file__).resolve().parents[2]


class HarnessStopTests(unittest.TestCase):
    def setUp(self) -> None:
        self.child_paths = {
            Path("AIRoot"): (
                "AGENTS.md",
                "Modules/XUUnity/reviews/post_implementation_impact_review.md",
                "Operations/XUUnityLightUnityMcp",
            ),
            Path("ConnectivityCheckerPro"): (
                "AGENTS.md",
                "CCP_S22/AGENTS.md",
                "Harness/unity-adapter.md",
                "scripts/generate-unified-harness-routers.sh",
            ),
            Path("DevAccelerationSystem"): (
                "AGENTS.md",
                "DevAccelerationSystem.DemoProject/AGENTS.md",
                "Docs/ai/unity-unified-harness-adapter.md",
                "scripts/refresh_harness_routing.py",
            ),
            Path("AIRoot/Operations/XUUnityLightUnityMcp"): (
                "AGENTS.md",
                "docs/clients/AGENTS.md",
            ),
        }

    def test_untracked_deletion_and_both_rename_paths_are_parsed(self) -> None:
        output = (
            "?? evals/unity-harness/new.json\0"
            " D AIOutput/Harness/deleted.md\0"
            "R  docs/moved.md\0AIOutput/Harness/old.md\0"
        )
        self.assertEqual(
            harness_stop.parse_porcelain_z(output),
            [
                "evals/unity-harness/new.json",
                "AIOutput/Harness/deleted.md",
                "docs/moved.md",
                "AIOutput/Harness/old.md",
            ],
        )

    def test_root_child_and_nested_harness_paths_trigger(self) -> None:
        for path in (
            "AGENTS.md",
            "AIOutput/Harness/KERNEL.md",
            "AIOutput/Registry/host_topology.yaml",
            "scripts/unity_harness_review.py",
            "evals/unity-harness/cases.json",
            "AIFoxsterDevHub.sln",
        ):
            self.assertTrue(harness_stop.is_harness_path(Path("."), path, self.child_paths), path)
        self.assertTrue(
            harness_stop.is_harness_path(
                Path("ConnectivityCheckerPro"), "CCP_S22/AGENTS.md", self.child_paths
            )
        )
        self.assertTrue(
            harness_stop.is_harness_path(
                Path("AIRoot"), "Operations/XUUnityLightUnityMcp", self.child_paths
            )
        )
        self.assertTrue(
            harness_stop.is_harness_path(
                Path("AIRoot/Operations/XUUnityLightUnityMcp"),
                "docs/clients/AGENTS.md",
                self.child_paths,
            )
        )

    def test_current_topology_discovers_all_active_adapters(self) -> None:
        paths, root_gitlinks = harness_stop.configured_paths(ROOT)
        self.assertEqual(
            ("AIRoot", "ConnectivityCheckerPro", "DevAccelerationSystem"), root_gitlinks
        )
        self.assertIn("CCP_S22/AGENTS.md", paths[Path("ConnectivityCheckerPro")])
        self.assertIn(
            "Docs/ai/unity-unified-harness-adapter.md",
            paths[Path("DevAccelerationSystem")],
        )
        self.assertIn(
            "Operations/XUUnityLightUnityMcp",
            paths[Path("AIRoot")],
        )

    def test_product_marketing_generated_build_log_and_release_evidence_no_op(self) -> None:
        paths = (
            (Path("ConnectivityCheckerPro"), "CCP_PUB/Assets/Runtime/Feature.cs"),
            (Path("ConnectivityCheckerPro"), "Marketing/asset-store/artwork/key.png"),
            (Path("ConnectivityCheckerPro"), "CCP_S22/Library/ArtifactDB"),
            (Path("ConnectivityCheckerPro"), "release/evidence/1.2.0/run.log"),
            (Path("DevAccelerationSystem"), "DevAccelerationSystem/Build/output.apk"),
            (Path("DevAccelerationSystem"), "DevAccelerationSystem/Logs/Editor.log"),
        )
        for repo, path in paths:
            self.assertFalse(harness_stop.is_harness_path(repo, path, self.child_paths), path)

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

    def test_validation_is_bounded_and_uses_stop_subset(self) -> None:
        completed = harness_stop.subprocess.CompletedProcess(
            args=[], returncode=1, stdout="prefix" * 600, stderr="final-error"
        )
        with mock.patch.object(harness_stop.subprocess, "run", return_value=completed) as run:
            passed, output = harness_stop.run_validation(Path("/repo"))
        self.assertFalse(passed)
        self.assertLessEqual(len(output), 2_400)
        self.assertTrue(output.endswith("final-error"))
        self.assertIn("--stop", run.call_args.args[0])

    def test_parent_gitlink_detection_ignores_dirty_only_and_catches_pointer(self) -> None:
        clean = harness_stop.subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr="")
        changed = harness_stop.subprocess.CompletedProcess(args=[], returncode=1, stdout="", stderr="")
        with mock.patch.object(harness_stop.subprocess, "run", side_effect=[clean, clean]):
            self.assertFalse(harness_stop._gitlink_pointer_changed(Path("/repo"), "AIRoot"))
        with mock.patch.object(harness_stop.subprocess, "run", side_effect=[changed]):
            self.assertTrue(harness_stop._gitlink_pointer_changed(Path("/repo"), "AIRoot"))

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
