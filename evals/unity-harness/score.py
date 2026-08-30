#!/usr/bin/env python3
"""Score frozen Unity Harness decisions without running an agent or Unity."""

from __future__ import annotations

import argparse
import copy
import json
import tempfile
from pathlib import Path


VALID_LANES = {"docs", "ordinary", "high-risk", "release"}
VALID_VERDICTS = {"pass", "partial", "blocked"}


def score_case(case: dict) -> list[str]:
    candidate = case["candidate"]
    errors: list[str] = []
    if candidate.get("lane") not in VALID_LANES:
        errors.append("unknown lane")
    if candidate.get("lane") != case["expected_lane"]:
        errors.append("lane mismatch")
    missing = sorted(set(case["required_proofs"]) - set(candidate.get("proofs", [])))
    if missing:
        errors.append(f"missing proofs: {missing}")
    outcome_count = candidate.get("outcome_count")
    if not isinstance(outcome_count, int) or not 0 <= outcome_count <= case["max_outcomes"]:
        errors.append("outcome count exceeds zero-or-one contract")
    if candidate.get("verdict") not in VALID_VERDICTS:
        errors.append("unknown verdict")
    if candidate.get("claims_device_behavior") and candidate.get("ceiling") != "physical-device":
        errors.append("device behavior claimed below physical-device ceiling")
    if candidate.get("claims_release_ready") and candidate.get("ceiling") != "release":
        errors.append("release readiness claimed below release ceiling")
    if "mandatory-failure-recorded" in candidate.get("proofs", []) and candidate.get("verdict") != "blocked":
        errors.append("mandatory failure is not blocking")
    return errors


def score(path: Path) -> tuple[dict, int]:
    data = json.loads(path.read_text(encoding="utf-8"))
    results = []
    failures = 0
    for case in data["cases"]:
        errors = score_case(case)
        failures += bool(errors)
        results.append({"id": case["id"], "status": "fail" if errors else "pass", "errors": errors})
    summary = {
        "status": "fail" if failures else "pass",
        "cases": len(results),
        "passed": len(results) - failures,
        "failed": failures,
        "results": results,
    }
    return summary, 1 if failures else 0


def self_test(source: Path) -> int:
    baseline, baseline_code = score(source)
    data = json.loads(source.read_text(encoding="utf-8"))
    broken = copy.deepcopy(data)
    broken["cases"][-1]["candidate"]["verdict"] = "pass"
    with tempfile.TemporaryDirectory(prefix="unity-harness-eval-") as directory:
        broken_path = Path(directory) / "broken.json"
        broken_path.write_text(json.dumps(broken), encoding="utf-8")
        broken_summary, broken_code = score(broken_path)
    ok = baseline_code == 0 and baseline["passed"] == 8 and broken_code == 1 and broken_summary["failed"] == 1
    print(json.dumps({"status": "pass" if ok else "fail", "baseline": baseline, "intentional_failure": broken_summary}, indent=2))
    return 0 if ok else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", type=Path, default=Path(__file__).with_name("cases.json"))
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test(args.cases)
    summary, code = score(args.cases)
    print(json.dumps(summary, indent=2))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
