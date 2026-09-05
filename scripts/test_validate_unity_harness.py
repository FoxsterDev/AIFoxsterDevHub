#!/usr/bin/env python3
"""Guard the root gate against obsolete child commands and self-reported counts."""

from __future__ import annotations

import os
import subprocess
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

    def test_privacy_regression_owner_is_explicitly_required(self) -> None:
        validator = Path(__file__).with_name("validate-unity-harness.py").read_text(encoding="utf-8")
        self.assertIn('"scripts/test_unity_harness_privacy.py"', validator)

    def test_missing_kernel_pointer_or_fallback_fails_route_contract(self) -> None:
        temporary = tempfile.TemporaryDirectory(prefix="unity-harness-routes-")
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        topology = {"boundaries": []}
        common = (
            "standalone fallback\n"
            "`../AIOutput/Harness/KERNEL.md`\n"
            "`../AIRoot/Modules/XUUnity/reviews/post_implementation_impact_review.md`\n"
        )
        (root / "AIOutput/Harness").mkdir(parents=True)
        (root / "AIOutput/Harness/KERNEL.md").write_text("kernel\n", encoding="utf-8")
        impact = root / "AIRoot/Modules/XUUnity/reviews/post_implementation_impact_review.md"
        impact.parent.mkdir(parents=True)
        impact.write_text("impact\n", encoding="utf-8")
        for identity in ("AIRoot", "ConnectivityCheckerPro", "DevAccelerationSystem"):
            directory = root / identity
            directory.mkdir(parents=True, exist_ok=True)
            router = directory / "AGENTS.md"
            adapter = directory / "adapter.md"
            router.write_text(common, encoding="utf-8")
            adapter.write_text(common, encoding="utf-8")
            topology["boundaries"].append(
                {"id": identity, "router": f"{identity}/AGENTS.md", "adapter": f"{identity}/adapter.md"}
            )
        (root / "AGENTS.md").write_text(
            "`AIRoot/Modules/XUUnity/reviews/post_implementation_impact_review.md`\n",
            encoding="utf-8",
        )
        self.assertEqual([], unity_harness_contract.route_contract_failures(root, topology))

        target = root / "ConnectivityCheckerPro/adapter.md"
        target.write_text(
            common.replace("`../AIOutput/Harness/KERNEL.md`\n", ""), encoding="utf-8"
        )
        errors = unity_harness_contract.route_contract_failures(root, topology)
        self.assertTrue(
            any("ConnectivityCheckerPro adapter" in error and "KERNEL.md" in error for error in errors)
        )
        self.assertTrue(any("missing advertised target" in error for error in errors))

        target.write_text(common.replace("fallback", ""), encoding="utf-8")
        errors = unity_harness_contract.route_contract_failures(root, topology)
        self.assertTrue(
            any("ConnectivityCheckerPro adapter" in error and "fallback" in error for error in errors)
        )

    def test_advertised_hub_route_resolves_from_the_advertising_file(self) -> None:
        temporary = tempfile.TemporaryDirectory(prefix="unity-harness-route-target-")
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        (root / "AIOutput/Harness").mkdir(parents=True)
        (root / "AIOutput/Harness/KERNEL.md").write_text("kernel\n", encoding="utf-8")
        impact = root / "AIRoot/Modules/XUUnity/reviews/post_implementation_impact_review.md"
        impact.parent.mkdir(parents=True)
        impact.write_text("impact\n", encoding="utf-8")
        adapter = root / "DevAccelerationSystem/Docs/ai/adapter.md"
        adapter.parent.mkdir(parents=True)
        adapter.write_text(
            "KERNEL.md post_implementation_impact_review.md standalone fallback\n"
            "`../../AIOutput/Harness/KERNEL.md`\n"
            "`../../AIRoot/Modules/XUUnity/reviews/post_implementation_impact_review.md`\n",
            encoding="utf-8",
        )
        router = root / "DevAccelerationSystem/AGENTS.md"
        router.write_text(
            "standalone fallback\n"
            "`../AIOutput/Harness/KERNEL.md`\n"
            "`../AIRoot/Modules/XUUnity/reviews/post_implementation_impact_review.md`\n",
            encoding="utf-8",
        )
        (root / "AGENTS.md").write_text(
            "`AIRoot/Modules/XUUnity/reviews/post_implementation_impact_review.md`\n",
            encoding="utf-8",
        )
        topology = {
            "boundaries": [
                {
                    "id": "DevAccelerationSystem",
                    "router": "DevAccelerationSystem/AGENTS.md",
                    "adapter": "DevAccelerationSystem/Docs/ai/adapter.md",
                }
            ]
        }

        errors = unity_harness_contract.route_contract_failures(root, topology)
        self.assertTrue(any("advertised route" in error for error in errors))

        adapter.write_text(
            "KERNEL.md post_implementation_impact_review.md standalone fallback\n"
            "`../../../AIOutput/Harness/KERNEL.md`\n"
            "`../../../AIRoot/Modules/XUUnity/reviews/post_implementation_impact_review.md`\n",
            encoding="utf-8",
        )
        errors = unity_harness_contract.route_contract_failures(root, topology)
        self.assertFalse(any("advertised route" in error for error in errors))

    def test_root_solution_refresh_accepts_absent_optional_but_not_missing_required(self) -> None:
        temporary = tempfile.TemporaryDirectory(prefix="unity-harness-solution-refresh-")
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        required_items = (
            "WORKSPACE.md",
            "scripts/refresh-aifoxster-hub.sh",
            "AIRoot/README.md",
            "AIRoot/INTEGRATION.md",
            "AIRoot/Modules/XUUnity/README.md",
            "AIRoot/Design/XUUNITY_PRODUCT_PROTOCOLS_DESIGN.md",
            "ConnectivityCheckerPro/CCP_PUB/CCP_PUB.sln",
            "ConnectivityCheckerPro/CCP_PUB/Assets/ConnectivityCheckerPro/package.json",
            "ConnectivityCheckerPro/CCP_S21/Packages/manifest.json",
            "ConnectivityCheckerPro/CCP_S22/Packages/manifest.json",
            "ConnectivityCheckerPro/CCP_S60/CCP_S60.sln",
            "ConnectivityCheckerPro/CCP_S60/Packages/manifest.json",
            "ConnectivityCheckerPro/CCP_S63/CCP_S63.sln",
            "ConnectivityCheckerPro/CCP_S63/Packages/manifest.json",
            "DevAccelerationSystem/DevAccelerationSystem/DevAccelerationSystem.sln",
            "DevAccelerationSystem/DevAccelerationSystem/Assets/DevAccelerationSystem/package.json",
            "DevAccelerationSystem/DevAccelerationSystem/Assets/TheBestLogger/package.json",
            "DevAccelerationSystem/DevAccelerationSystem.DemoProject/DevAccelerationSystem.DemoProject.sln",
            "DevAccelerationSystem/DevAccelerationSystem.DemoProject/Packages/manifest.json",
        )
        project_paths = (
            "ConnectivityCheckerPro/CCP_PUB/ConnectivityCheckerPro.Runtime.csproj",
            "ConnectivityCheckerPro/CCP_PUB/ConnectivityCheckerPro.Samples.csproj",
            "ConnectivityCheckerPro/CCP_PUB/ConnectivityCheckerPro.Tests.csproj",
            "ConnectivityCheckerPro/CCP_PUB/ConnectivityCheckerPro.PlayMode.Tests.csproj",
            "DevAccelerationSystem/DevAccelerationSystem/DevAccelerationSystem.Core.csproj",
            "DevAccelerationSystem/DevAccelerationSystem/DevAccelerationSystem.ProjectCompilationCheck.csproj",
            "DevAccelerationSystem/DevAccelerationSystem/DevAccelerationSystem.Editor.Tests.csproj",
            "DevAccelerationSystem/DevAccelerationSystem.DemoProject/TheBestLoggerSample.csproj",
            "DevAccelerationSystem/DevAccelerationSystem.DemoProject/TheBestLogger.Integration.Tests.csproj",
        )
        for relative in required_items:
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("fixture\n", encoding="utf-8")
        for index, relative in enumerate(project_paths, start=1):
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            guid = f"00000000-0000-0000-0000-{index:012d}"
            path.write_text(f"<ProjectGuid>{{{guid}}}</ProjectGuid>\n", encoding="utf-8")

        script = Path(__file__).with_name("refresh-aifoxster-hub.sh")
        environment = {**os.environ, "AIFOXSTER_HUB_ROOT": str(root)}
        absent = subprocess.run(
            [str(script)], check=False, capture_output=True, text=True, env=environment
        )
        self.assertEqual(0, absent.returncode, absent.stderr)
        self.assertNotIn("DAS.LocalProject", (root / "AIFoxsterDevHub.sln").read_text())

        for relative in (
            "DevAccelerationSystem/DAS.LocalProject/DAS.LocalProject.sln",
            "DevAccelerationSystem/DAS.LocalProject/Packages/manifest.json",
        ):
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("optional\n", encoding="utf-8")
        present = subprocess.run(
            [str(script)], check=False, capture_output=True, text=True, env=environment
        )
        self.assertEqual(0, present.returncode, present.stderr)
        self.assertIn("DAS.LocalProject", (root / "AIFoxsterDevHub.sln").read_text())

        (root / "WORKSPACE.md").unlink()
        missing = subprocess.run(
            [str(script)], check=False, capture_output=True, text=True, env=environment
        )
        self.assertNotEqual(0, missing.returncode)
        self.assertIn("Missing solution item: WORKSPACE.md", missing.stderr)


if __name__ == "__main__":
    unittest.main()
