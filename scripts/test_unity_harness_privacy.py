#!/usr/bin/env python3
"""Regression tests for static privacy versus Unity launch authority."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path
from unittest import mock


MODULE_PATH = Path(__file__).with_name("validate-unity-privacy.py")
SPEC = importlib.util.spec_from_file_location("validate_unity_privacy", MODULE_PATH)
assert SPEC and SPEC.loader
PRIVACY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PRIVACY)


class PrivacyBoundaryTests(unittest.TestCase):
    @mock.patch.object(PRIVACY, "check_hub_records", return_value=[])
    @mock.patch.object(PRIVACY, "check_editor_analytics", return_value=["host: opt-out red"])
    @mock.patch.object(PRIVACY, "check_project", return_value=[])
    @mock.patch.object(
        PRIVACY,
        "privacy_projects",
        return_value=([{"id": "TEST", "path": "Project"}], []),
    )
    def test_host_red_blocks_launch_without_falsifying_static_structure(
        self,
        projects: mock.Mock,
        project: mock.Mock,
        editor: mock.Mock,
        hub: mock.Mock,
    ) -> None:
        static, static_code = PRIVACY.evaluate(Path("/repo"), False)
        self.assertEqual(0, static_code)
        self.assertEqual("pass", static["repository_privacy"]["status"])
        self.assertEqual("not-evaluated", static["unity_launch_authority"]["status"])
        editor.assert_not_called()

        launch, launch_code = PRIVACY.evaluate(Path("/repo"), True)
        self.assertEqual(1, launch_code)
        self.assertEqual("pass", launch["repository_privacy"]["status"])
        self.assertEqual("blocked", launch["unity_launch_authority"]["status"])
        self.assertEqual(["host: opt-out red"], launch["unity_launch_authority"]["failures"])
        projects.assert_called()
        project.assert_called()
        hub.assert_called_once()


if __name__ == "__main__":
    unittest.main()
