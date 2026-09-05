#!/usr/bin/env python3
"""Regression tests for the static, topology-scoped Unity Harness Stop hook."""

from __future__ import annotations

import io
import json
import subprocess
import tempfile
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

    def make_git_root(self) -> Path:
        temporary = tempfile.TemporaryDirectory(prefix="unity-harness-hook-")
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        subprocess.run(["git", "init", "-q"], cwd=root, check=True)
        subprocess.run(["git", "config", "user.name", "Harness Test"], cwd=root, check=True)
        subprocess.run(
            ["git", "config", "user.email", "harness@example.invalid"], cwd=root, check=True
        )
        topology = root / "AIOutput/Registry/host_topology.yaml"
        topology.parent.mkdir(parents=True)
        topology.write_text("schema_version: 3\n", encoding="utf-8")
        subprocess.run(["git", "add", topology.relative_to(root)], cwd=root, check=True)
        subprocess.run(["git", "commit", "-q", "-m", "base"], cwd=root, check=True)
        return root

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
            "scripts/test_unity_harness_contract.py",
            "scripts/test_unity_harness_privacy.py",
            "scripts/test_unity_harness_review.py",
            "scripts/test_validate_unity_harness.py",
            "evals/unity-harness/cases.json",
            "AIFoxsterDevHub.sln",
        ):
            self.assertTrue(harness_stop.is_harness_path(Path("."), path, self.child_paths), path)
        self.assertTrue(
            harness_stop.is_harness_path(
                Path("ConnectivityCheckerPro"), "CCP_S22/AGENTS.md", self.child_paths
            )
        )
        self.assertFalse(
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

    def test_root_file_triggers_do_not_match_lookalike_paths(self) -> None:
        self.assertFalse(
            harness_stop.is_harness_path(Path("."), "AGENTS.md.backup", self.child_paths)
        )
        self.assertFalse(
            harness_stop.is_harness_path(
                Path("."), "scripts/validate-unity-harness.py.old", self.child_paths
            )
        )

    def test_current_topology_discovers_all_active_adapters(self) -> None:
        paths, gitlinks_by_parent = harness_stop.configured_paths(ROOT)
        self.assertEqual(
            ("AIRoot", "ConnectivityCheckerPro", "DevAccelerationSystem"),
            gitlinks_by_parent[Path(".")],
        )
        self.assertIn("CCP_S22/AGENTS.md", paths[Path("ConnectivityCheckerPro")])
        self.assertIn(
            "Docs/ai/unity-unified-harness-adapter.md",
            paths[Path("DevAccelerationSystem")],
        )
        self.assertNotIn(
            "Operations/XUUnityLightUnityMcp",
            paths[Path("AIRoot")],
        )
        self.assertEqual(
            ("Operations/XUUnityLightUnityMcp",),
            gitlinks_by_parent[Path("AIRoot")],
        )

    def test_nested_mcp_dirt_is_scoped_but_gitlink_pointer_and_router_trigger(self) -> None:
        root = self.make_git_root()
        airroot = root / "AIRoot"
        airroot.mkdir()
        subprocess.run(["git", "init", "-q"], cwd=airroot, check=True)
        subprocess.run(["git", "config", "user.name", "Harness Test"], cwd=airroot, check=True)
        subprocess.run(
            ["git", "config", "user.email", "harness@example.invalid"],
            cwd=airroot,
            check=True,
        )
        (airroot / "AGENTS.md").write_text("AIRoot router\n", encoding="utf-8")

        nested_relative = "Operations/XUUnityLightUnityMcp"
        mcp = airroot / nested_relative
        mcp.mkdir(parents=True)
        subprocess.run(["git", "init", "-q"], cwd=mcp, check=True)
        subprocess.run(["git", "config", "user.name", "Harness Test"], cwd=mcp, check=True)
        subprocess.run(
            ["git", "config", "user.email", "harness@example.invalid"], cwd=mcp, check=True
        )
        (mcp / "AGENTS.md").write_text("MCP router\n", encoding="utf-8")
        (mcp / "runtime.txt").write_text("base runtime\n", encoding="utf-8")
        subprocess.run(["git", "add", "AGENTS.md", "runtime.txt"], cwd=mcp, check=True)
        subprocess.run(["git", "commit", "-q", "-m", "MCP base"], cwd=mcp, check=True)
        mcp_head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=mcp, text=True).strip()

        subprocess.run(["git", "add", "AGENTS.md"], cwd=airroot, check=True)
        subprocess.run(
            [
                "git", "update-index", "--add", "--cacheinfo",
                f"160000,{mcp_head},{nested_relative}",
            ],
            cwd=airroot,
            check=True,
        )
        subprocess.run(["git", "commit", "-q", "-m", "AIRoot base"], cwd=airroot, check=True)
        airroot_head = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=airroot, text=True
        ).strip()
        subprocess.run(
            ["git", "update-index", "--add", "--cacheinfo", f"160000,{airroot_head},AIRoot"],
            cwd=root,
            check=True,
        )
        subprocess.run(["git", "commit", "-q", "-m", "mount AIRoot"], cwd=root, check=True)

        configured = (
            {
                Path("AIRoot"): ("AGENTS.md",),
                Path("AIRoot") / nested_relative: ("AGENTS.md",),
            },
            {
                Path("."): ("AIRoot",),
                Path("AIRoot"): (nested_relative,),
            },
        )
        with mock.patch.object(harness_stop, "configured_paths", return_value=configured):
            (mcp / "ordinary-runtime.cs").write_text("owner dirt\n", encoding="utf-8")
            self.assertEqual([], harness_stop.changed_harness_paths(root))
            (mcp / "ordinary-runtime.cs").unlink()

            (mcp / "AGENTS.md").write_text("changed router\n", encoding="utf-8")
            self.assertEqual(
                [f"AIRoot/{nested_relative}:AGENTS.md"],
                harness_stop.changed_harness_paths(root),
            )
            (mcp / "AGENTS.md").write_text("MCP router\n", encoding="utf-8")

            (mcp / "runtime.txt").write_text("new MCP head\n", encoding="utf-8")
            subprocess.run(["git", "add", "runtime.txt"], cwd=mcp, check=True)
            subprocess.run(["git", "commit", "-q", "-m", "advance MCP"], cwd=mcp, check=True)
            self.assertEqual(
                [f"AIRoot:{nested_relative}"],
                harness_stop.changed_harness_paths(root),
            )

            advanced_head = subprocess.check_output(
                ["git", "rev-parse", "HEAD"], cwd=mcp, text=True
            ).strip()
            subprocess.run(
                [
                    "git", "update-index", "--cacheinfo",
                    f"160000,{advanced_head},{nested_relative}",
                ],
                cwd=airroot,
                check=True,
            )
            self.assertEqual(
                [f"AIRoot:{nested_relative}"],
                harness_stop.changed_harness_paths(root),
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

    def test_deleted_or_malformed_topology_still_runs_and_blocks(self) -> None:
        for mutation in ("delete", "malform"):
            with self.subTest(mutation=mutation):
                root = self.make_git_root()
                topology = root / "AIOutput/Registry/host_topology.yaml"
                if mutation == "delete":
                    topology.unlink()
                else:
                    topology.write_text("broken: [\n", encoding="utf-8")
                self.assertIn(
                    ".:AIOutput/Registry/host_topology.yaml",
                    harness_stop.changed_harness_paths(root),
                )
                with mock.patch.object(
                    harness_stop, "run_validation", return_value=(False, "invalid topology")
                ) as validate:
                    result = harness_stop.decision({}, root)
                self.assertEqual("block", result["decision"])
                validate.assert_called_once_with(root)


if __name__ == "__main__":
    unittest.main()
