#!/usr/bin/env python3
"""Guard the root gate against obsolete child commands and self-reported counts."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import unity_harness_contract


class RootGateContractTests(unittest.TestCase):
    def test_obsolete_mcp_router_generator_is_not_active(self) -> None:
        validator = Path(__file__).with_name("validate-unity-harness.py").read_text(encoding="utf-8")
        self.assertNotIn("scripts/tools/sync_agent_routers.py", validator)
        self.assertIn("scripts/testing/run_host_python_tests.sh", validator)

    def test_context_scenarios_and_budgets_have_one_code_owner(self) -> None:
        topology = unity_harness_contract.load_topology(Path(__file__).resolve().parents[1])
        scenarios = unity_harness_contract.context_scenarios(topology)
        self.assertEqual(set(scenarios), set(unity_harness_contract.CONTEXT_BUDGETS))
        self.assertEqual(len(scenarios), 8)

    def test_static_gate_does_not_require_host_launch_authority(self) -> None:
        validator = Path(__file__).with_name("validate-unity-harness.py").read_text(encoding="utf-8")
        privacy_command = next(
            line for line in validator.splitlines() if "privacy-structure" in line
        )
        self.assertNotIn("--require-host-opt-out", privacy_command)

    def test_stop_subset_executes_route_mutations(self) -> None:
        validator = Path(__file__).with_name("validate-unity-harness.py").read_text(encoding="utf-8")
        self.assertIn('"current-contract-mutations"', validator)
        self.assertIn("--stop", validator)

    def test_missing_kernel_pointer_or_fallback_fails_route_contract(self) -> None:
        temporary = tempfile.TemporaryDirectory(prefix="unity-harness-routes-")
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        topology = {"boundaries": []}
        common = "KERNEL.md post_implementation_impact_review.md standalone fallback\n"
        for identity in ("AIRoot", "ConnectivityCheckerPro", "DevAccelerationSystem"):
            directory = root / identity
            directory.mkdir(parents=True)
            router = directory / "AGENTS.md"
            adapter = directory / "adapter.md"
            router.write_text(common, encoding="utf-8")
            adapter.write_text(common, encoding="utf-8")
            topology["boundaries"].append(
                {"id": identity, "router": f"{identity}/AGENTS.md", "adapter": f"{identity}/adapter.md"}
            )
        (root / "AGENTS.md").write_text("post_implementation_impact_review.md\n", encoding="utf-8")
        self.assertEqual([], unity_harness_contract.route_contract_failures(root, topology))

        target = root / "ConnectivityCheckerPro/AGENTS.md"
        target.write_text(common.replace("KERNEL.md", ""), encoding="utf-8")
        (root / "ConnectivityCheckerPro/adapter.md").write_text(
            common.replace("KERNEL.md", ""), encoding="utf-8"
        )
        errors = unity_harness_contract.route_contract_failures(root, topology)
        self.assertTrue(any("KERNEL.md" in error for error in errors))

        target.write_text(common.replace("fallback", ""), encoding="utf-8")
        (root / "ConnectivityCheckerPro/adapter.md").write_text(
            common.replace("fallback", ""), encoding="utf-8"
        )
        errors = unity_harness_contract.route_contract_failures(root, topology)
        self.assertTrue(any("fallback" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
