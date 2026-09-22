# Principal review: validation evidence and release acceptance design

Date: 2026-09-21. Visibility: host-private. Reviewed artifact: [technical design](2026-09-21_validation_evidence_technical_design.md) (revised in place by this review; the pre-review text is not kept in this folder).
Live baseline checked: MCP `v0.3.78` at `dce8b8e`, plus `master` at `98bf6eb` (one docs commit after the tag). Consumer reference: `ConnectivityCheckerPro/scripts/close-connectivity-checker-pro-release.py` and its `ccp_*.py` helpers, verdict `release/evidence/1.2.2/release-verdict.json` (E07).

## 1. Verdict

Accept with revisions, applied. The direction is right and the retro-derived rules (fixed denominator, no stage promotion, channel truth, warning policy separate from compile PASS) are all backed by real evidence. Three things were wrong and would have sent the implementer to the wrong code: the compile-field path, the "existing summary module" owners, and the assumption that a native-client receipt can be captured server-side. One thing was materially understated: the consumer already implements most of the evaluator's semantics in its own runner, so the work is extraction and standardization, not greenfield. Nothing in the design is a transport or bridge change, which is correct.

## 2. What is real, what is not

| Design claim | Reality | Evidence (MCP repo unless noted) | Disposition |
|---|---|---|---|
| Baseline `v0.3.78` at `dce8b8e` | Real. `master` is one commit ahead (`98bf6eb`, retro registry header fix). AIFoxsterDevHub mounts the MCP detached at the tag. | `git log`, `git tag` in both mounts | Start work from `master`; A7 is already done |
| Compact output has an 8192-byte ceiling | Real, with an existing truncation ladder | `templates/server_launcher.py:52`, `build_compact_terminal_envelope`, `_bounded_compact_json` | Reuse, do not reimplement (WP4) |
| Compile results retain `warning_count`, `unique_warning_count`, `warnings_truncated`, rebuild counts | Real | decoded `payload_json.result` of E05; `XUUnityLightMcpCompileModels.cs`, `server_bridge_payloads.py` | Keep |
| Compile PASS is error-based | Real | `XUUnityLightMcpCompileUtility.cs:144` `errors.Count > 0 ? "failed" : "passed"` | Keep |
| Test acceptance uses `test_verdict`, counts, post-settle | Real; zero matches already yield `test_filter_no_match`, not `passed` | `templates/server_operation_evidence.py:120-175` | Keep; evaluator requires `test_verdict == passed` |
| "Normalize direct compile fields from `payload.result`" | Wrong path. Saved helper responses are `{request_id, status, completed_at_utc, payload_type, payload_json (string), error, _xuunity_lifecycle}`. Compile facts are in decoded `payload_json.result.*`; test facts are top-level keys of decoded `payload_json`. | E05 and E06 decoded in this review | Fixed in §3/§5.2 |
| `server_readiness_summary.py`, `server_summary_status.py`, `server_summary_scenario.py` own the relevant summaries | Wrong owners for this evaluator. Evidence normalization lives in `server_operation_evidence.py`, `server_bridge_payloads.py`, and `scripts/testing/run_multi_project.py::normalize_compile_evidence` (`compile_evidence{outcome, evidence_source, execution_lane}` from the 2026-07-12 design). | file greps; `DESIGN_PLAN_HISTORY.md:75` | Fixed in §3 |
| Native-client verification requires a receipt from the named client session calling `unity_status_summary` | Cannot be server-emitted today. `unity_status_summary` is a read-only summary and writes no journal event; the MCP protocol layer does not persist `clientInfo`; journal `client_kind` (`mcp_server`/`cli`) and `client_session_id` come from env overrides (`XUUNITY_CLIENT_KIND`, `XUUNITY_CLIENT_SESSION_ID`). The README's rule is an operator rule: only the live tool call in the client proves wiring. | `templates/server_bridge_journal.py:14-38`, `templates/server_summary_status.py`, `README.md:697` | Receipt redefined as operator-captured tool result; optional host-side `client_probe` journal event left as owner decision D2 |
| Existing evidence-summary v1 "remains usable"; legacy adapter extracts facts | Nobody emits or validates v1. It is referenced only by the three workflow templates' `closeoutSchema` strings and `AGENT_WORKFLOWS.md:272-310`. | repo-wide grep | AT15 reduced to "file byte-identical"; legacy adapter dropped |
| Strict schema tests | The host has no `jsonschema` dependency and no schema is validated in code anywhere. Python 3.10+, stdlib only. | import inventory of `templates/*.py`; `README.md:90` | Design now specifies hand-written strict validators and `no third-party dependency` as a non-goal |
| Exit code 2 = invalid input | Correct for argparse, but the consumer's `run_command` maps any exit 2 to `BLOCKED`. | `close-connectivity-checker-pro-release.py:44` | Consumer mapping rule added (§5) |
| `executionChannel` is new vocabulary | Partly. The Unity-side lane already exists as `execution_lane` (`batch`/`gui`/`none`). Channel (who called the host) is a different axis. | `run_multi_project.py:352-380` | Both axes named; `executionLane` reuses the existing enum |
| AT07: "40 rows: 23 pass, 17 blocked" | E07 is 8 `PASS` + 15 `REUSED` + 17 `BLOCKED`; the design's row enum had no place for reuse | E07 `checks.unity_matrix.lanes` | `reused` flag added; AT07 corrected |
| Consumer must "define supported matrix, warning ownership, sample interactions, fixture restoration, source identity" (WP6 builds a runner) | Already built. Verdict v2 has 12 `required_checks`, per-lane `status`+`reason`, `compatibility.rows` with backend and per-stage results, `sample_e2e.lanes` with `input_mode`, scene assertion and `compiler_cleanliness`, `artifact.source_identity` with `dirty_paths`, `impact.digests` with `reuse_allowed`, `toolchain_preflight` first, `stage_timings`. Missing: execution channel, native-client receipt, warning counts on matrix lanes, exact stage names on device rows. | E07 structure dump; ~2,000 lines across the closeout runner, matrix/sample/lifecycle runners and five `ccp_*` helpers | §1 reframed; adapter B (verdict v2 to receipts) added; WP6 reduced to adoption |
| §7 validation order is new guidance | Already the consumer's order (`toolchain_preflight`, then compile, sample e2e per input mode, matrix). | E07 `stage_timings`, `run-connectivity-checker-pro-sample-e2e.py` | Marked done-in-consumer; only promoted into `SMOKE_TESTS.md` |
| Host tests on Windows, Ubuntu, macOS | Real | `.github/workflows/windows-integration-tests.yml` os matrix | Named |
| Guidance docs "cross-platform Python, shell, atomic IPC" | Real, mandated by the MCP router | `AGENTS.md:46-48`, `skills/*/SKILL.md` | Exact paths named |
| `CONTINUATION.md` | Lives at `docs/operations/CONTINUATION.md` | ls | Path fixed |
| `scripts/tools/` for the evaluator | Folder holds two wrapper helpers; the sibling with ledger, frozen denominator, `payload_mode: compact_*` and `--output compact|full` is `scripts/testing/run_consumer_rollout.py`, which also shows how to import `templates/` modules | `scripts/README.md`, `run_consumer_rollout.py:33,959-1000` | Moved to `scripts/testing/`; flag names aligned |
| "No unresolved architectural choice" | One optional choice remains (D2, server-side client probe event) | this review | Stated honestly in §12 |

## 3. Findings by severity

**[P1] Wrong field path for compile evidence**
File: design §5.2 (pre-review). Problem: `payload.result` does not exist in saved helper responses; an adapter written to it reads nothing and, without the design's own null-not-zero rule, could report zero warnings. Evidence: E05 top-level keys and decoded `payload_json.result` keys listed in this review. Fix: §3 now documents the verified shape for compile and test responses; AT02 covers the missing-count case.

**[P1] Native-client receipt assumed to exist server-side**
Problem: the design required "a receipt captured from the actual named client session calling `unity_status_summary`" as if the host could produce it. It cannot: no journal event, no persisted `clientInfo`, env-overridable kind. Impact: WP3 would have blocked on a non-existent artifact or, worse, accepted a journal `client_kind=mcp_server` event as attestation although the CLI defaults to `mcp_server` until `mark_host_client_kind` runs and the env can force any value. Fix: receipt is an operator-captured file (client tool result containing `mcp_server_info.version` and project root, plus a capture block); journal correlation is supporting evidence only; D2 offers the smallest host-side improvement as a separate decision.

**[P1] Consumer state understated; work framed as greenfield**
Problem: §1 said consumer reporting "did not enforce" evidence meaning, and WP6 asked the consumer to define matrix, identity, fixtures and a runner. E07 shows all of that already enforced with a fixed denominator and BLOCKED verdict; the retro's actual failure was operator/chat overclaiming and channel naming. Impact: duplicate implementation and a schema that ignores the only proven shape. Fix: §1 reframed, §3 lists verdict v2 fields, adapter B maps verdict v2 to receipts, WP1 derives the schemas from that mapping, WP6 is adoption of channel labels and lane warning counts.

**[P2] Wrong reuse owners**
Problem: pointing WP3 at the readiness/status/scenario summary modules. Fix: owners corrected to `server_operation_evidence.py`, `server_bridge_payloads.py`, `normalize_compile_evidence`, `server_launcher.py` compact helpers, `run_consumer_rollout.py` ledger conventions.

**[P2] Schema validation without a validator**
Problem: "strict schema tests" with no `jsonschema` in the host and no precedent of code-validated schemas. Fix: hand-written strict validators (required keys, `additionalProperties: false`, enums, null-vs-int) in a pure module, fixtures for valid and invalid cases, schema JSON kept as the documented contract mirrored by tests; adding a dependency is a non-goal.

**[P2] Exit-code collision with the consumer**
Problem: consumer maps exit 2 to BLOCKED, which would turn a malformed plan into a blocked row that still has a denominator. Fix: §5 states the consumer must map evaluator exit 2 to `evaluation_invalid` (fail-closed, no acceptance rows), and the compact envelope carries that reason.

**[P2] Reuse invisible in rows; AT07 wrong**
Fix: `reused` boolean per row, reused count in the compact envelope, AT07 uses the real E07 split.

**[P3] Vocabulary collision `channel` vs `execution_lane`**
Fix: `executionChannel` (native-mcp / helper-cli / direct-unity / any) and optional `executionLane` (batch / gui / none) are separate fields; mapping rule from consumer stage names to the design's stage enum added.

**[P3] Placement and flag names**
Fix: evaluator in `scripts/testing/` beside the rollout runner; `--report` for the output path, `--output compact|full` for mode; `payload_mode: compact_validation_acceptance`.

**[P3] Path and status wording**
Fix: `docs/operations/CONTINUATION.md`; status uses the `DESIGN_PLAN_HISTORY.md` vocabulary (`design`); public retro registry path is `docs/archive/retros/RETRO_REGISTRY.md`; public promotion must pass `check_public_release_safety.py` and `check_release_docs_freshness.py`; `templates/workflows/README.md` must list the new schemas.

## 4. Pareto core

Build first, because each item is a measured defect from the retro and is cheap against the verified code:

1. WP1 schemas derived from verdict v2 plus the E05/E06 response shape, with hand-written strict validation and sanitized fixtures.
2. WP2 pure evaluator (match, policy, aggregate, compact via the existing launcher helper).
3. WP3 adapter A (saved helper response) and adapter B (consumer verdict v2). Adapter B alone lets E07 be re-evaluated with zero consumer changes and proves the counts.
4. Consumer adds `executionChannel` to its rows and captures one native `unity_status_summary` receipt file.

Defer or drop: legacy v1 adapter (no producer), MCP tool registration, supersession beyond a pinned `receiptId` or an explicit `supersedes` list, benchmark telemetry beyond recording evaluator wall time and byte sizes, host-side client probe journaling (D2), `client-integration` stage semantics beyond the operator-captured receipt.

## 5. Open owner decisions

- D1 (decided in the revised design, overridable): evaluator lives in `scripts/testing/` and imports `templates/` the way the rollout runner does.
- D2 (open): add a host-only `client_probe` journal event when `unity_status_summary` is served to a native client, carrying `client_kind`, `client_session_id`, `mcp_server_info.version`. It is Python host code, no bridge change, but it is a runtime behavior change and belongs in its own small change after the offline evaluator is used once.

## 6. Review provenance

- Review: principal design review using the `xuunity` design-retro-review method (evidence over self-assessment), 2026-09-21.
- Selected stack: `AIRoot/Modules/XUUnity/tasks/start_session.md`, `utilities/design_retro_review.md`, MCP router `AIRoot/Operations/XUUnityLightUnityMcp/AGENTS.md`, host routers of both hubs. Risk class: low (documentation only; no runtime, no bridge, no consumer code changed). Concurrency: not applicable. Validation focus: every claim traced to a file, line or decoded evidence record.
- Commands run: `git log/tag/cat-file/status` in both MCP mounts; `grep` for `8192`, compile/test field names, `client_kind`, `evidence_summary`, `jsonschema`, `clientInfo`, `status_summary`; Python decoding of E05, E06 and E07; import inventory of `templates/*.py`; CI workflow matrix read.
- Files sampled: `templates/server_launcher.py`, `server_bridge_journal.py`, `server_operation_evidence.py`, `server_summary_status.py`, `scripts/testing/run_consumer_rollout.py`, `run_multi_project.py`, `templates/workflows/*`, `docs/agents/AGENT_WORKFLOWS.md`, `docs/architecture/designs/DESIGN_PLAN_HISTORY.md`, the 2026-07-12 and 2026-09-15 designs, `XUUnityLightMcpCompileUtility.cs`; consumer `close-connectivity-checker-pro-release.py`, `run-connectivity-checker-pro-sample-e2e.py`, `run-connectivity-checker-pro-unity-matrix.py`, `ccp_*.py`, verdict E07.
- Tests run: none; review only. No test counts are quoted anywhere in this review or the revised design.
- Subjective axis: the Pareto ordering in §4. Everything in §2 is evidence-based at the sampled commit and can drift.
