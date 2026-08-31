#!/usr/bin/env python3
"""Score frozen Unity Harness observations without running an agent or Unity."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import tempfile
from pathlib import Path
from typing import Any, Callable
SCHEMA_VERSION = 2
EXPECTED_CASE_COUNT = 10
EXPECTED_CONSUMER_COUNT = 7
EXPECTATIONS_SHA256 = "6a6a7b83428aae15a225361243ef44029e9b8fa45236393df78824e586101b78"
REQUIRED_CASE_IDS = (
    "UH-01-docs-only", "UH-02-contained-csharp", "UH-03-package-consumer",
    "UH-04-serialized-scene", "UH-05-save-compatibility", "UH-06-native-device-only",
    "UH-07-unity-version-matrix", "UH-08-release-intentional-failure",
    "UH-09-tooling-version-contract", "UH-10-routing-compatibility",
)
HISTORICAL_CASE_ID = "UH-08-release-intentional-failure"
VALID_LANES = {"docs", "ordinary", "high-risk", "release"}
VALID_VERDICTS = {"pass", "partial", "blocked"}
VALID_MODES = {"deterministic-contract", "historical-replay", "live-observation"}
VALID_CEILINGS = {
    "static", "resolved", "compiled", "editmode", "playmode", "serialized-reopen",
    "platform-build", "physical-device", "release",
}
CASE_KEYS = {
    "id", "evidence_mode", "expected_lane", "required_proofs", "max_outcomes",
    "expected_ceiling", "expected_verdict", "claims_device_behavior", "claims_release_ready",
}
RESULT_KEYS = {
    "id", "evidence_mode", "lane", "proofs", "ceiling", "verdict", "outcome_count",
    "claims_device_behavior", "claims_release_ready",
}
class ContractError(ValueError):
    """A strict fixture contract was violated."""
def _object_no_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ContractError(f"duplicate JSON key: {key}")
        result[key] = value
    return result
def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_object_no_duplicates)
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ContractError(f"cannot load {path.name}: {error}") from error
    if not isinstance(value, dict):
        raise ContractError(f"{path.name}: root must be an object")
    return value
def _exact_keys(value: dict[str, Any], required: set[str], label: str) -> None:
    missing = sorted(required - value.keys())
    unknown = sorted(value.keys() - required)
    if missing or unknown:
        raise ContractError(f"{label}: missing={missing}, unknown={unknown}")
def _string_list(value: Any, label: str) -> list[str]:
    if not isinstance(value, list) or not value or not all(isinstance(item, str) and item for item in value):
        raise ContractError(f"{label}: expected non-empty string list")
    if len(value) != len(set(value)):
        raise ContractError(f"{label}: duplicate values")
    return value
def _base_types(item: dict[str, Any], label: str, expectation: bool) -> None:
    string_fields = ("id", "evidence_mode")
    string_fields += ("expected_lane", "expected_ceiling", "expected_verdict") if expectation else (
        "lane", "ceiling", "verdict",
    )
    for field in string_fields:
        if not isinstance(item[field], str) or not item[field]:
            raise ContractError(f"{label}.{field}: expected string")
    list_field = "required_proofs" if expectation else "proofs"
    _string_list(item[list_field], f"{label}.{list_field}")
    int_field = "max_outcomes" if expectation else "outcome_count"
    if type(item[int_field]) is not int or not 0 <= item[int_field] <= 1:
        raise ContractError(f"{label}.{int_field}: expected integer from 0 to 1")
    for field in ("claims_device_behavior", "claims_release_ready"):
        if type(item[field]) is not bool:
            raise ContractError(f"{label}.{field}: expected boolean")
def _tooling_contract(value: Any, label: str, observation: bool) -> None:
    if not isinstance(value, dict):
        raise ContractError(f"{label}: expected object")
    keys = {"version_owner", "validator_mode", "exact_tag", "exact_commit",
            "package_version_matches_tag"}
    keys |= {"consumer_pins"} if observation else {"consumer_pins_exact", "consumers"}
    _exact_keys(value, keys, label)
    for field in ("version_owner", "validator_mode"):
        if not isinstance(value[field], str) or not value[field]:
            raise ContractError(f"{label}.{field}: expected string")
    bool_fields = ("exact_tag", "exact_commit", "package_version_matches_tag")
    bool_fields += () if observation else ("consumer_pins_exact",)
    if any(type(value[field]) is not bool for field in bool_fields):
        raise ContractError(f"{label}: alignment fields must be boolean")
    if observation:
        pins = value["consumer_pins"]
        if not isinstance(pins, list) or len(pins) != EXPECTED_CONSUMER_COUNT:
            raise ContractError(f"{label}.consumer_pins: expected exactly {EXPECTED_CONSUMER_COUNT}")
        for index, pin in enumerate(pins):
            if not isinstance(pin, dict):
                raise ContractError(f"{label}.consumer_pins[{index}]: expected object")
            _exact_keys(pin, {"id", "exact_tag", "exact_hash"}, f"{label}.consumer_pins[{index}]")
            if not isinstance(pin["id"], str) or not pin["id"]:
                raise ContractError(f"{label}.consumer_pins[{index}].id: expected string")
            if type(pin["exact_tag"]) is not bool or type(pin["exact_hash"]) is not bool:
                raise ContractError(f"{label}.consumer_pins[{index}]: alignment fields must be boolean")
        ids = [pin["id"] for pin in pins]
        if len(ids) != len(set(ids)):
            raise ContractError(f"{label}.consumer_pins: duplicate IDs")
    elif len(_string_list(value["consumers"], f"{label}.consumers")) != EXPECTED_CONSUMER_COUNT:
        raise ContractError(f"{label}.consumers: expected exactly {EXPECTED_CONSUMER_COUNT}")
def _routing_contract(value: Any, label: str) -> None:
    if not isinstance(value, dict):
        raise ContractError(f"{label}: expected object")
    keys = {"standalone_detection", "unsupported_lane_status", "release_supported", "obsolete_generator_referenced"}
    _exact_keys(value, keys, label)
    for field in ("standalone_detection", "unsupported_lane_status"):
        if not isinstance(value[field], str) or not value[field]:
            raise ContractError(f"{label}.{field}: expected string")
    for field in ("release_supported", "obsolete_generator_referenced"):
        if type(value[field]) is not bool:
            raise ContractError(f"{label}.{field}: expected boolean")

def validate_expectations(data: dict[str, Any], raw: bytes) -> list[dict[str, Any]]:
    _exact_keys(data, {"schema_version", "cases"}, "expectations root")
    if data["schema_version"] != SCHEMA_VERSION or type(data["schema_version"]) is not int:
        raise ContractError("expectations root: unsupported schema_version")
    cases = data["cases"]
    if not isinstance(cases, list) or len(cases) != EXPECTED_CASE_COUNT:
        raise ContractError(f"expectations root: expected exactly {EXPECTED_CASE_COUNT} cases")
    for case in cases:
        if not isinstance(case, dict):
            raise ContractError("expectations case: expected object")
        extra = {"tooling_contract"} if case.get("id") == REQUIRED_CASE_IDS[8] else (
            {"routing_contract"} if case.get("id") == REQUIRED_CASE_IDS[9] else set()
        )
        _exact_keys(case, CASE_KEYS | extra, f"expectation {case.get('id')!r}")
        _base_types(case, f"expectation {case['id']}", True)
        if case["evidence_mode"] not in VALID_MODES or case["expected_lane"] not in VALID_LANES:
            raise ContractError(f"expectation {case['id']}: invalid mode or lane")
        if case["expected_ceiling"] not in VALID_CEILINGS or case["expected_verdict"] not in VALID_VERDICTS:
            raise ContractError(f"expectation {case['id']}: invalid ceiling or verdict")
        if "tooling_contract" in extra:
            _tooling_contract(case["tooling_contract"], f"expectation {case['id']}.tooling_contract", False)
        if "routing_contract" in extra:
            _routing_contract(case["routing_contract"], f"expectation {case['id']}.routing_contract")
    ids = tuple(case["id"] for case in cases)
    if ids != REQUIRED_CASE_IDS:
        raise ContractError(f"expectations root: IDs/order must be {list(REQUIRED_CASE_IDS)}")
    historical = cases[7]
    if historical["id"] != HISTORICAL_CASE_ID or historical["evidence_mode"] != "historical-replay":
        raise ContractError("UH-08 historical identity/evidence mode changed")
    if historical["expected_verdict"] != "blocked" or historical["claims_release_ready"]:
        raise ContractError("UH-08 historical blocked invariant changed")
    if hashlib.sha256(raw).hexdigest() != EXPECTATIONS_SHA256:
        raise ContractError("expectations integrity mismatch")
    return cases

def validate_results(data: dict[str, Any]) -> list[dict[str, Any]]:
    _exact_keys(data, {"schema_version", "results"}, "results root")
    if data["schema_version"] != SCHEMA_VERSION or type(data["schema_version"]) is not int:
        raise ContractError("results root: unsupported schema_version")
    results = data["results"]
    if not isinstance(results, list) or len(results) != EXPECTED_CASE_COUNT:
        raise ContractError(f"results root: expected exactly {EXPECTED_CASE_COUNT} results")
    ids: list[str] = []
    for result in results:
        if not isinstance(result, dict):
            raise ContractError("result: expected object")
        extra = {"tooling_observation"} if result.get("id") == REQUIRED_CASE_IDS[8] else (
            {"routing_observation"} if result.get("id") == REQUIRED_CASE_IDS[9] else set()
        )
        _exact_keys(result, RESULT_KEYS | extra, f"result {result.get('id')!r}")
        _base_types(result, f"result {result['id']}", False)
        if result["evidence_mode"] not in VALID_MODES or result["lane"] not in VALID_LANES:
            raise ContractError(f"result {result['id']}: invalid mode or lane")
        if result["ceiling"] not in VALID_CEILINGS or result["verdict"] not in VALID_VERDICTS:
            raise ContractError(f"result {result['id']}: invalid ceiling or verdict")
        if "tooling_observation" in extra:
            _tooling_contract(result["tooling_observation"], f"result {result['id']}.tooling_observation", True)
        if "routing_observation" in extra:
            _routing_contract(result["routing_observation"], f"result {result['id']}.routing_observation")
        ids.append(result["id"])
    if len(ids) != len(set(ids)):
        raise ContractError("results root: duplicate IDs")
    missing, unknown = sorted(set(REQUIRED_CASE_IDS) - set(ids)), sorted(set(ids) - set(REQUIRED_CASE_IDS))
    if missing or unknown:
        raise ContractError(f"results root: missing={missing}, unknown={unknown}")
    return results

def score_case(case: dict[str, Any], result: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    comparisons = (
        ("evidence_mode", "evidence_mode"), ("expected_lane", "lane"),
        ("expected_ceiling", "ceiling"), ("expected_verdict", "verdict"),
        ("claims_device_behavior", "claims_device_behavior"),
        ("claims_release_ready", "claims_release_ready"),
    )
    for expected, observed in comparisons:
        if case[expected] != result[observed]:
            errors.append(f"{observed} mismatch")
    missing = sorted(set(case["required_proofs"]) - set(result["proofs"]))
    if missing:
        errors.append(f"missing proofs: {missing}")
    if result["outcome_count"] > case["max_outcomes"]:
        errors.append("outcome count exceeds zero-or-one contract")
    if result["claims_device_behavior"] and result["ceiling"] != "physical-device":
        errors.append("device behavior claimed below physical-device ceiling")
    if result["claims_release_ready"] and result["ceiling"] != "release":
        errors.append("release readiness claimed below release ceiling")
    if "mandatory-failure-recorded" in result["proofs"] and result["verdict"] != "blocked":
        errors.append("mandatory failure is not blocking")
    if "tooling_contract" in case:
        observed = result["tooling_observation"]
        expected = case["tooling_contract"]
        fields = ("version_owner", "validator_mode", "exact_tag", "exact_commit", "package_version_matches_tag")
        for field in fields:
            if observed[field] != expected[field]:
                errors.append(f"tooling {field} mismatch")
        pins = {pin["id"]: pin for pin in observed["consumer_pins"]}
        if set(pins) != set(expected["consumers"]):
            errors.append("tooling consumer IDs mismatch")
        for consumer in expected["consumers"]:
            pin = pins.get(consumer, {})
            aligned = pin.get("exact_tag") == pin.get("exact_hash") == expected["consumer_pins_exact"]
            if not aligned:
                errors.append(f"tooling consumer pin mismatch: {consumer}")
    if "routing_contract" in case and result["routing_observation"] != case["routing_contract"]:
        errors.append("routing contract mismatch")
    return errors

def score(expectations_path: Path, results_path: Path) -> tuple[dict[str, Any], int]:
    try:
        expectations = load_json(expectations_path)
        cases = validate_expectations(expectations, expectations_path.read_bytes())
        results = validate_results(load_json(results_path))
        by_id = {result["id"]: result for result in results}
        reports = []
        for case in cases:
            errors = score_case(case, by_id[case["id"]])
            reports.append({"id": case["id"], "status": "fail" if errors else "pass", "errors": errors})
        failures = sum(report["status"] == "fail" for report in reports)
        summary = {
            "status": "fail" if failures else "pass", "cases": EXPECTED_CASE_COUNT,
            "passed": EXPECTED_CASE_COUNT - failures, "failed": failures, "results": reports,
        }
        return summary, 1 if failures else 0
    except ContractError as error:
        return {"status": "fail", "cases": EXPECTED_CASE_COUNT, "passed": 0, "failed": EXPECTED_CASE_COUNT,
                "contract_errors": [str(error)], "results": []}, 1

def self_test(expectations_path: Path, results_path: Path) -> int:
    baseline, baseline_code = score(expectations_path, results_path)
    source = load_json(results_path)
    mutations: list[tuple[str, Callable[[dict[str, Any]], None]]] = [
        ("unknown-field", lambda d: d["results"][0].update({"acceptance_floor": 0})),
        ("missing-field", lambda d: d["results"][0].pop("lane")),
        ("missing-case", lambda d: d["results"].pop()),
        ("duplicate-id", lambda d: d["results"][1].update({"id": d["results"][0]["id"]})),
        ("false-release", lambda d: d["results"][7].update({"verdict": "pass", "claims_release_ready": True})),
        ("false-device", lambda d: d["results"][5].update({"claims_device_behavior": True})),
        ("stale-tag", lambda d: d["results"][8]["tooling_observation"].update({"exact_tag": False})),
        ("stale-hash", lambda d: d["results"][8]["tooling_observation"].update({"exact_commit": False})),
        ("stale-pin", lambda d: d["results"][8]["tooling_observation"]["consumer_pins"][0].update({"exact_tag": False})),
        ("obsolete-generator", lambda d: d["results"][8]["tooling_observation"].update({"validator_mode": "obsolete-generator"})),
        ("brittle-standalone", lambda d: d["results"][9]["routing_observation"].update({"standalone_detection": "literal-Standalone-colon"})),
        ("historical-relabel", lambda d: d["results"][7].update({"evidence_mode": "live-observation"})),
    ]
    rejected: list[str] = []
    with tempfile.TemporaryDirectory(prefix="unity-harness-eval-") as directory:
        candidate_path = Path(directory) / "results.json"
        for name, mutate in mutations:
            candidate = copy.deepcopy(source)
            mutate(candidate)
            candidate_path.write_text(json.dumps(candidate), encoding="utf-8")
            if score(expectations_path, candidate_path)[1] != 0:
                rejected.append(name)
    ok = baseline_code == 0 and baseline["passed"] == EXPECTED_CASE_COUNT and len(rejected) == len(mutations)
    print(json.dumps({"status": "pass" if ok else "fail", "baseline": baseline,
                      "mutations": {"rejected": len(rejected), "total": len(mutations), "ids": rejected}}, indent=2))
    return 0 if ok else 1

def main() -> int:
    directory = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", type=Path, default=directory / "cases.json")
    parser.add_argument("--results", type=Path, default=directory / "results.json")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test(args.cases, args.results)
    summary, code = score(args.cases, args.results)
    print(json.dumps(summary, indent=2))
    return code

if __name__ == "__main__":
    raise SystemExit(main())
