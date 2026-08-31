#!/usr/bin/env python3
"""Guard the root gate against obsolete child commands and self-reported counts."""

from __future__ import annotations

import unittest
from pathlib import Path

import unity_harness_contract


class RootGateContractTests(unittest.TestCase):
    def test_obsolete_mcp_router_generator_is_not_active(self) -> None:
        validator = Path(__file__).with_name("validate-unity-harness.py").read_text(encoding="utf-8")
        self.assertNotIn("scripts/tools/sync_agent_routers.py", validator)
        self.assertIn("scripts/testing/check_release_version_consistency.py", validator)

    def test_context_scenarios_and_budgets_have_one_code_owner(self) -> None:
        self.assertEqual(
            set(unity_harness_contract.CONTEXT_SCENARIOS),
            set(unity_harness_contract.CONTEXT_BUDGETS),
        )
        self.assertEqual(len(unity_harness_contract.CONTEXT_SCENARIOS), 8)


if __name__ == "__main__":
    unittest.main()
