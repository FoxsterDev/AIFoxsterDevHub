from __future__ import annotations

import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


DIRECTORY = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("unity_harness_score", DIRECTORY / "score.py")
assert SPEC and SPEC.loader
SCORE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SCORE)


class FrozenScorerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.expectations = json.loads((DIRECTORY / "cases.json").read_text(encoding="utf-8"))
        self.results = json.loads((DIRECTORY / "results.json").read_text(encoding="utf-8"))
        self.temporary = tempfile.TemporaryDirectory(prefix="unity-harness-tests-")
        self.root = Path(self.temporary.name)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def run_score(self, expectations=None, results=None, results_text: str | None = None):
        expectations_path = self.root / "cases.json"
        results_path = self.root / "results.json"
        expectations_path.write_text(
            json.dumps(self.expectations if expectations is None else expectations), encoding="utf-8"
        )
        if expectations is None:
            expectations_path.write_bytes((DIRECTORY / "cases.json").read_bytes())
        if results_text is None:
            results_path.write_text(json.dumps(self.results if results is None else results), encoding="utf-8")
        else:
            results_path.write_text(results_text, encoding="utf-8")
        return SCORE.score(expectations_path, results_path)

    def assert_rejected(self, expectations=None, results=None, results_text=None):
        summary, code = self.run_score(expectations, results, results_text)
        self.assertEqual(1, code, summary)
        self.assertEqual("fail", summary["status"])

    def mutate_result(self, index: int, **changes):
        data = copy.deepcopy(self.results)
        data["results"][index].update(changes)
        return data

    def test_baseline_is_exactly_ten_of_ten(self):
        summary, code = self.run_score()
        self.assertEqual(0, code, summary)
        self.assertEqual((10, 10, 0), (summary["cases"], summary["passed"], summary["failed"]))

    def test_unknown_result_field_is_rejected(self):
        data = self.mutate_result(0, typo_verdit="pass")
        self.assert_rejected(results=data)

    def test_missing_result_field_is_rejected(self):
        data = copy.deepcopy(self.results)
        data["results"][0].pop("lane")
        self.assert_rejected(results=data)

    def test_missing_case_is_rejected_by_code_owned_count(self):
        data = copy.deepcopy(self.results)
        data["results"].pop()
        self.assert_rejected(results=data)

    def test_duplicate_json_key_is_rejected(self):
        text = (DIRECTORY / "results.json").read_text(encoding="utf-8")
        text = text.replace('"schema_version": 2,', '"schema_version": 2, "schema_version": 2,', 1)
        self.assert_rejected(results_text=text)

    def test_duplicate_result_id_is_rejected(self):
        data = self.mutate_result(1, id=self.results["results"][0]["id"])
        self.assert_rejected(results=data)

    def test_duplicate_expectation_id_is_rejected(self):
        data = copy.deepcopy(self.expectations)
        data["cases"][1]["id"] = data["cases"][0]["id"]
        self.assert_rejected(expectations=data)

    def test_unknown_expectation_field_is_rejected(self):
        data = copy.deepcopy(self.expectations)
        data["cases"][0]["acceptance_floor"] = 0
        self.assert_rejected(expectations=data)

    def test_lowered_expectation_floor_is_rejected_by_integrity_owner(self):
        cases = copy.deepcopy(self.expectations)
        results = copy.deepcopy(self.results)
        removed = cases["cases"][1]["required_proofs"].pop()
        results["results"][1]["proofs"].remove(removed)
        self.assert_rejected(expectations=cases, results=results)

    def test_candidate_cannot_supply_a_lower_acceptance_floor(self):
        data = self.mutate_result(0, acceptance_floor=0)
        self.assert_rejected(results=data)

    def test_historical_release_failure_cannot_be_pass(self):
        data = self.mutate_result(7, verdict="pass", claims_release_ready=True)
        self.assert_rejected(results=data)

    def test_historical_failure_markers_cannot_be_deleted(self):
        data = copy.deepcopy(self.results)
        data["results"][7]["proofs"].remove("mandatory-failure-recorded")
        self.assert_rejected(results=data)

    def test_historical_replay_cannot_be_relabelled_live(self):
        data = self.mutate_result(7, evidence_mode="live-observation")
        self.assert_rejected(results=data)

    def test_device_claim_below_physical_device_is_rejected(self):
        data = self.mutate_result(5, claims_device_behavior=True)
        self.assert_rejected(results=data)

    def test_stale_mcp_tag_is_rejected(self):
        data = copy.deepcopy(self.results)
        data["results"][8]["tooling_observation"]["exact_tag"] = False
        self.assert_rejected(results=data)

    def test_stale_mcp_hash_is_rejected(self):
        data = copy.deepcopy(self.results)
        data["results"][8]["tooling_observation"]["exact_commit"] = False
        self.assert_rejected(results=data)

    def test_stale_package_version_relation_is_rejected(self):
        data = copy.deepcopy(self.results)
        data["results"][8]["tooling_observation"]["package_version_matches_tag"] = False
        self.assert_rejected(results=data)

    def test_stale_consumer_pin_is_rejected(self):
        data = copy.deepcopy(self.results)
        pin = data["results"][8]["tooling_observation"]["consumer_pins"][0]
        pin.update({"exact_tag": False, "exact_hash": False})
        self.assert_rejected(results=data)

    def test_missing_consumer_pin_is_rejected_by_code_owned_count(self):
        data = copy.deepcopy(self.results)
        data["results"][8]["tooling_observation"]["consumer_pins"].pop()
        self.assert_rejected(results=data)

    def test_obsolete_generator_entrypoint_is_rejected(self):
        data = copy.deepcopy(self.results)
        data["results"][8]["tooling_observation"]["validator_mode"] = "obsolete-generator"
        self.assert_rejected(results=data)

    def test_brittle_standalone_literal_is_rejected(self):
        data = copy.deepcopy(self.results)
        data["results"][9]["routing_observation"]["standalone_detection"] = "literal-Standalone-colon"
        self.assert_rejected(results=data)

    def test_false_unsupported_release_support_is_rejected(self):
        data = copy.deepcopy(self.results)
        data["results"][9]["routing_observation"]["release_supported"] = True
        self.assert_rejected(results=data)

    def test_nested_unknown_field_is_rejected(self):
        data = copy.deepcopy(self.results)
        data["results"][8]["tooling_observation"]["legacy_counter"] = 7
        self.assert_rejected(results=data)

    def test_wrong_boolean_type_is_rejected(self):
        data = self.mutate_result(0, claims_release_ready=0)
        self.assert_rejected(results=data)


if __name__ == "__main__":
    unittest.main()
