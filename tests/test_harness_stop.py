#!/usr/bin/env python3

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("harness_stop", ROOT / ".codex/hooks/harness_stop.py")
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class HarnessStopScopeTests(unittest.TestCase):
    def test_root_harness_path_matches(self) -> None:
        self.assertTrue(MODULE.is_harness_path(Path("."), "AIOutput/Harness/KERNEL.md"))

    def test_product_path_does_not_match(self) -> None:
        self.assertFalse(MODULE.is_harness_path(Path("ConnectivityCheckerPro"), "ConnectivityCheckerPro_Publish/Assets/Foo.cs"))

    def test_mcp_router_path_matches_without_product_runtime(self) -> None:
        self.assertTrue(
            MODULE.is_harness_path(
                Path("AIRoot/Operations/XUUnityLightUnityMcp"),
                "AGENTS.md",
            )
        )

    def test_loop_guard_returns_empty(self) -> None:
        self.assertEqual(MODULE.decision({"stop_hook_active": True}, ROOT), {})


if __name__ == "__main__":
    unittest.main()
