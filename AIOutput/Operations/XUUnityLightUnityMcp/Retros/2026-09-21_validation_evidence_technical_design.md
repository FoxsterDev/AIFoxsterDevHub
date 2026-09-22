# XUUnity MCP validation evidence and release acceptance

Date: 2026-09-21. Revised 2026-09-21 after [principal review](2026-09-21_validation_evidence_design_principal_review.md).
Status: `implemented` for WP0–WP5 and the WP7 records; WP6 consumer adoption `partially implemented` (runner changed, fresh closeout run pending); independent non-author acceptance pending. Implementation record in §13.
Visibility: host-private implementation handoff. Public promotion must remove private retrospective links and pass `scripts/testing/check_public_release_safety.py`.
Baseline: MCP `v0.3.78`, commit `dce8b8e8027041331f4112428b8b314e5e7a3a43`. Implementation starts from `master` at `98bf6eb` (one docs commit after the tag). The AIFoxsterDevHub mount is detached at the tag; run `git checkout master` in `AIRoot/Operations/XUUnityLightUnityMcp` first.
Sources: [retrospective](2026-09-21_release_validation_retro.md), [evidence catalog](2026-09-21_release_validation_evidence.json).
Consumer reference implementation: `ConnectivityCheckerPro/scripts/close-connectivity-checker-pro-release.py` with `ccp_change_impact.py`, `ccp_evidence.py`, `ccp_compatibility.py`, `ccp_diagnostics.py`, `ccp_unity_toolchain.py`; verdict schema `foxsterlabs.ccp.release-verdict.v2`.

## 1. Problem and desired behavior

The consumer's closeout runner already produced a correct fixed-denominator verdict: E07 is `BLOCKED` with 12 required checks and 40 platform lanes (8 `PASS`, 15 `REUSED`, 17 `BLOCKED`). What failed sat between the tool and the reader. Operator and chat summaries overclaimed scope (a compile was described as regression coverage, an APK build as platform validation). CLI-driven bridge runs were called MCP validation without a native client ever being exercised. Warning evidence existed in every compile payload but was applied as a release decision late. The join between requirement rows and MCP receipts existed only inside one product's scripts, so nothing reusable checked it.

After implementation, a consumer supplies an explicit validation plan and evidence receipts. A deterministic offline evaluator reports acceptance per required row and preserves the complete denominator. It cannot turn missing evidence into PASS, substitute a weaker stage, or relabel CLI evidence as native MCP-client verification. Unity execution, journaling, recovery and transport semantics are unchanged.

Example: an Android APK build passes while its required device-runtime row is blocked by a missing device. The report says `1/2 pass, 1 blocked`; the APK remains a valid build artifact; publication acceptance stays blocked.

## 2. Scope and ownership

| Surface | Work |
|---|---|
| MCP Python host (`scripts/testing/`) | Offline evaluator, two receipt adapters (saved helper response; consumer verdict v2), compact projection via the existing launcher helper |
| MCP templates (`templates/workflows/`) | Three strict schemas derived from the consumer verdict v2 mapping; sanitized fixtures; README entry |
| MCP docs | Channel/stage/policy examples, blocked-denominator example, preflight order, compact usage |
| Unity bridge and host runtime | No change |
| Consumer project | Add `executionChannel` to rows, capture one native-client receipt file, add warning counts to matrix lanes where the producer exposes them; keep ownership of its matrix, fixtures and identity |
| Release owner | Set requirements, approve scope changes; tags never waive requirements |

Non-goals: CI scheduler, process manager, SDK installation, publisher automation, permission expansion, click engine, transport rewrite, universal device support, warning suppression, migration of existing workflow JSON, MCP tool registration in the first delivery, any third-party Python dependency (the host is Python 3.10+, stdlib only), server-side client attestation (see D2).

The retrospective demonstrated no transport defect. `tests/test_terminal_delivery_verdict.py` already covers completed-but-undelivered requests; it is regression protection, not a fix.

## 3. Existing contracts to reuse (verified at `v0.3.78`)

Saved helper response shape, verified on the compile (E05) and PlayMode (E06) records:

```text
{ request_id, status, completed_at_utc, payload_type, payload_json: "<JSON string>",
  error: { code, message },
  _xuunity_lifecycle: { operation, transport, bridge_identity_before_request, idle_wait_before, idle_wait_after, activation } }
```

- Compile facts: decoded `payload_json.result.{status, target, target_group, error_count, errors, warning_count, unique_warning_count, warnings, warning_sample_limit, warnings_truncated, rebuilt_assembly_count, cached_assembly_count, compiled_assembly_count, rebuild_evidence_status, rebuild_evidence_basis}` plus `payload_json.{completion_basis, post_settle_error_count, post_settle_compile_trust_class, authoritative_state_source}`. Compile `status` is error-based (`XUUnityLightMcpCompileUtility.cs`, `errors.Count > 0 ? "failed" : "passed"`).
- Test facts: top-level keys of decoded `payload_json`: `test_verdict` (`passed`, `failed`, `no_tests`, `test_filter_no_match`, `runtime_timeout`), `total`, `passed`, `failed`, `skipped`, `filter_requested`, `filter_summary`, `completion_basis`, `lifecycle_churn_observed`, `post_settle_error_count`, `runtime_timeout_observed`, `result_payload_available`. Owner: `templates/server_operation_evidence.py` (`_attach_direct_test_verdict`, `build_artifact_manifest`).
- The outer `status=ok` and empty `error` never override the decoded payload.
- Unity execution lane already exists: `scripts/testing/run_multi_project.py::normalize_compile_evidence` emits `compile_evidence{outcome, evidence_source, execution_lane}` with `execution_lane` in `batch|gui|none` (2026-07-12 verdict-coherence design). This is orthogonal to the caller channel introduced here.
- Journal (`templates/server_bridge_journal.py`): events carry `client_kind` (`mcp_server` or `cli`), `client_session_id`, `host_delivery_observed`, `test_verdict`. Kind and session are env-configurable (`XUUNITY_CLIENT_KIND`, `XUUNITY_CLIENT_SESSION_ID`), and the CLI path marks itself `cli` at runtime. Journal facts are traceability, not attestation. `unity_status_summary` is a read-only summary (`templates/server_summary_status.py`) and writes no journal event; the protocol layer does not persist MCP `clientInfo`.
- Compact envelope: `templates/server_launcher.py` `COMPACT_OUTPUT_MAX_BYTES = 8192`, `build_compact_terminal_envelope`, `_bounded_compact_json` (truncation ladder). Reuse; do not write a second truncation routine.
- Ledger conventions: `scripts/testing/run_consumer_rollout.py` (`schema_version`, frozen `denominator`, `payload_mode: compact_*`, `--output compact|full`, `full_payload_cli_argument`; it inserts `templates/` into `sys.path` to import server modules).
- `templates/workflows/evidence_summary.schema.json` (`xuunity.light-mcp.evidence.v1`) is a documented closeout contract referenced by the three workflow templates' `closeoutSchema` and by `docs/agents/AGENT_WORKFLOWS.md`. No code emits or validates it. Leave the file byte-identical; no legacy adapter.
- Schemas in this repo are documentation contracts. Strictness is enforced by hand-written validators in tests, not by a schema library.
- Consumer verdict v2 (E07), the only proven acceptance shape: `required_checks` (12), `checks.<name>.status` in `PASS|FAIL|BLOCKED|NOT_RUN|REUSED` with `reason`; `checks.unity_matrix.lanes[40]{line, unity_version, target, status, reason}`; `checks.compatibility.rows{line, unity_version, target, backend, required_stages, compile, player_build, player_run, tests, status}` plus `claim`; `checks.sample_e2e.lanes{line, input_mode, backend, scene, compiler_cleanliness{count, diagnostics, status}, artifact_sha256, consumer_dependencies}`; `checks.artifact.artifact.source_identity{artifact_sha256, manifest_sha256, dirty_paths, captured_at_utc}`; `impact{digests{executable_content_sha256, package_content_sha256}, reuse_allowed, reuse_reason, reasons}`; `stage_timings`. Missing there: execution channel, native-client receipt, warning counts on matrix lanes, exact stage names on device rows.

## 4. Architecture

```text
Owner-approved plan ──────────────────────────┐
                                              v
Saved helper responses ─> adapter A ─> normalized receipts ─> deterministic evaluator
Consumer verdict v2 ────> adapter B ─┘                              |
                                                     full report + bounded compact envelope
                                                                    |
                                                           consumer release gate
```

Evaluation is read-only except for the requested report file. It must not launch Unity, query the network, change project settings, install tooling or retry operations. Producers record execution; the evaluator verifies structure, identity, freshness bindings and policy.

Receipt paths are local files only: no URL fetching, no shell interpolation, no execution of suggested recovery commands. Relative paths resolve against the receipts manifest directory, never a Unity working directory. Resolve with `Path.resolve(strict=True)` and require `is_relative_to` a declared evidence root; a symlink or Windows junction whose target escapes the root is rejected. Missing or unreadable files produce an evidence gap, never an empty success.

## 5. Interfaces and schemas

All names here are proposed.

```bash
python3 scripts/testing/evaluate_validation_evidence.py --plan PLAN --receipts RECEIPTS --report REPORT [--output compact|full]
python3 scripts/testing/evaluate_validation_evidence.py --consumer-verdict VERDICT --report REPORT [--project-id ID --plan-id ID]
```

The second form runs adapter B and writes the derived plan and receipts beside the report for audit.

Writes the full JSON report to `--report`; prints the compact envelope by default (`payload_mode: compact_validation_acceptance`, `full_payload_cli_argument: "--output full"`). Exit codes: `0` accepted; `1` valid evaluation with failed, blocked or partial required rows; `2` invalid input, schema or IO. Exit `2` still prints a bounded envelope with `reason: evaluation_invalid` when possible. Consumer rule: a caller such as the ConnectivityCheckerPro runner, which maps exit `2` to `BLOCKED`, must map this tool's exit `2` to `evaluation_invalid` with no acceptance rows and no denominator, not to a blocked row.

Schemas under `templates/workflows/` (listed in that folder's README):

- `validation_plan.schema.json`, `schemaVersion = xuunity.light-mcp.validation-plan.v1`
- `validation_receipts.schema.json`, `schemaVersion = xuunity.light-mcp.validation-receipts.v1`
- `validation_acceptance.schema.json`, `schemaVersion = xuunity.light-mcp.validation-acceptance.v1`

All objects are strict (`additionalProperties: false`) with explicit optional fields. Unknown enum values or schema versions are invalid input. Validation is a hand-written strict validator (required keys, closed key sets, enums, null-versus-integer) in a pure module, covered by valid and invalid fixtures.

### 5.1 Plan

Required: `schemaVersion`, `planId`, `projectId`, `sourceIdentity`, `requirements` (nonempty). `planId` is stable; the report records the SHA-256 of the exact plan bytes.

`sourceIdentity`: algorithm id, SHA-256 digest, manifest reference (sorted normalized relative paths with per-file digests, the consumer's `sha256_tree` semantics), `dirtyPaths` (the consumer already records them), optional commit id. Commit ids are supplementary and never replace content hashes for dirty trees. Scope covers source, tests, relevant project settings, dependency locks and fixture setup. Toolchain versions are bound per row in `dimensions`.

| Field | Contract |
|---|---|
| `id` | Unique stable nonempty string; duplicates are invalid |
| `required` | Boolean; optional rows are reported but do not block |
| `dimensions` | Exact Unity version, target, scripting backend, input mode where applicable; explicit `null` for nonapplicable |
| `stage` | `static`, `resolve`, `compile`, `editmode`, `playmode`, `build`, `export`, `player-runtime`, `device-runtime`, `client-integration` |
| `scene` | Scene path or GUID when the row depends on it; otherwise `null` |
| `executionChannel` | `native-mcp`, `helper-cli`, `direct-unity`, `any`; `any` never satisfies a native-client row |
| `executionLane` | Optional; `batch`, `gui`, `none`; reuses the existing `execution_lane` enum |
| `policy` | Warning policy, measured-rebuild requirement, minimum test count, expected semantic assertions |
| `artifactRequired` | Boolean; requires a current nonempty hash-matching artifact |
| `receiptId` | Optional pin when more than one receipt could match |

Stages are exact capabilities, not a ladder: `export` does not satisfy `build`; `build` does not satisfy `device-runtime`. Mapping from consumer verdict v2: `compile` to `compile`; `player_build` to `build` for Android and Standalone targets and to `export` for iOS (Xcode project); `player_run` to `player-runtime`; Android profiles to `device-runtime`; `tests` to `editmode` or `playmode` by the producing operation. One receipt may satisfy several rows only when it independently contains every requested dimension and assertion; counts count rows, not operations.

### 5.2 Receipt

Required: `receiptId`, `requirementId`, `sourceIdentity`, `dimensions`, `stage`, `executionChannel`, `producer`, `startedAt`, `completedAt`, `evidenceRef`, `operationOutcome`.

`producer` records version and route; route binds to `completion_basis`, `authoritative_state_source` and `_xuunity_lifecycle.transport` when present. `evidenceRef` is a local path plus SHA-256. Optional: `requestId`, `executionLane`, `clientReceiptRef`, artifact identity, `diagnostics`, test counts, semantic assertions, execution blocker, existing trust or disposition fields, `supersedes` (list of receipt ids). Unknown values are `null`, never `0`.

Adapter A runs when a receipt carries `evidenceKind: helper_response`: the evaluator decodes the file behind `evidenceRef` using the verified shape in §3, fills operation outcome, diagnostics, rebuild and test facts, and preserves provenance to the exact JSON path; such receipts may omit `producer`, timestamps and `operationOutcome`. Adapter B maps a consumer verdict v2 file to one receipt per lane, compatibility row, sample lane and required check, preserving `REUSED` as `reused=true`. Neither adapter assumes one nesting for every operation; an outer `status=ok` never overrides a failing payload.

Native-client verification is an operator-captured receipt, because the host cannot emit one today. The receipt file is the tool result returned inside the named client session for `unity_status_summary`, containing `mcp_server_info.version` and the project root, wrapped with a capture block `{clientName, capturedBy, capturedAt}` and referenced by `clientReceiptRef`. A journal event for the same session with `client_kind=mcp_server` is supporting correlation only. `client_kind=cli`, an installed manifest, a healthy helper or `request-status-summary` output never satisfy a native row. This is traceability against an honest producer, not attestation.

`diagnostics`: `scope` (`all` or declared package roots), `complete` (boolean), `warningCount`, `uniqueWarningCount`, `truncated` (from `warnings_truncated`), bounded samples. Strict package-only cleanliness needs complete ownership accounting for the relevant compiler interval. Complete global counts with truncated samples can prove zero global warnings; they cannot prove package-only cleanliness when ownership is unknown. String matching never hides diagnostics.

### 5.3 Acceptance report

Required: schema version, plan id and hash, evaluator version, source identity, overall verdict, required and optional counts, `reusedCount`, ordered rows, validation gaps, report artifact reference.

Each row keeps requirement id and dimensions, matched receipt ids, original operation outcome, acceptance outcome (`pass`, `fail`, `blocked`, `not_run`), `reused` boolean with the original run timestamp, reason codes, policy and evidence provenance. Reason codes (closed set, owned by `REASON_CODES` in `validation_acceptance.py`): `receipt_missing`, `receipt_conflict`, `source_identity_mismatch`, `dimension_mismatch`, `scene_mismatch`, `stage_mismatch`, `channel_unverified`, `evidence_missing`, `evidence_changed`, `evidence_outside_roots`, `evidence_undecodable`, `operation_failed`, `capability_unavailable`, `test_verdict_not_passed`, `test_count_insufficient`, `runtime_timeout`, `post_settle_errors`, `semantic_assertion_failed`, `diagnostics_unmeasured`, `warning_budget_exceeded`, `rebuild_unmeasured`, `rebuild_cached_only`, `artifact_missing`, `artifact_changed`, `evaluation_invalid`.

New fields require a schema version change, never silent acceptance.

## 6. Evaluation algorithm

1. Validate schemas, unique ids, evidence-root rules and size limits (defaults 10 MiB per JSON input, 10,000 rows or receipts); reject excess explicitly.
2. Verify plan, source and artifact hashes. Preserve original timestamps; never relabel old evidence as a new run.
3. Match requirement id, exact dimensions, scene, stage, channel and content identity. A mismatch cannot satisfy the row.
4. Normalize operation evidence. Tests pass only with `test_verdict == "passed"`, `total >= policy.minTests` and `failed == 0`; `runtime_timeout` yields `blocked`; `no_tests`, `test_filter_no_match` and `failed` yield `fail`. Required semantic assertions must be explicit and successful.
5. Apply diagnostics policy separately from execution outcome. Missing counts or `complete=false` block strict cleanliness (`diagnostics_unmeasured`); counts above budget fail it. Measured rebuild is required only where the plan asks.
6. Require usable artifact proof where declared. A historical build stays successful while current deliverability is blocked by deletion or replacement.
7. Absent receipt is `not_run`; an evidenced capability blocker is `blocked`; confirmed execution, assertion or policy failure is `fail`. Malformed input is exit `2`, never PASS.
8. Never pick the newest receipt blindly. With more than one candidate, the plan's `receiptId` pin or a receipt's `supersedes` list decides; otherwise the row is `blocked` with `receipt_conflict`. Superseded failures stay in history.
9. Aggregate required rows: any `fail` gives `fail`; else any `blocked` gives `blocked`; else any `not_run` gives `partial`; else `pass`. Optional rows never change the verdict. Counts always sum to the fixed required denominator.
10. Emit the full report, then the compact envelope through `_bounded_compact_json`: verdict, counts, reused count, first actionable reasons, truncation indicators, report reference. Truncate diagnostics before identity and counts. Never drop required rows from the full report.

Reuse is content-bound, the consumer's `impact.reuse_allowed` rule: the receipt must match the full source, config and toolchain tuple, the recorded artifact identity and the plan policy. Reused rows report `reused=true` and the original timestamp. Environmental and device rows may demand fresh evidence per release through a plan run id. Changing a relevant input invalidates affected rows only; unexplained scope exclusions block reuse.

## 7. Validation order and failure attribution

The consumer runner already executes this order (`toolchain_preflight` first, `stage_timings` recorded, sample e2e per input mode, idempotent fixture setup, sequential targets). This design promotes the order into `docs/operations/SMOKE_TESTS.md`; it adds no consumer work beyond channel labels.

1. Read-only capability inventory: Unity versions and modules, SDK provenance, runners, devices. Report unavailable rows before expensive work.
2. Static fixture checks: absolute output paths, unique test names, idempotent probe insertion, dependency availability, expected scene.
3. Compile changed scripts with measured rebuild and the chosen warning policy.
4. One focused sample PlayMode scenario: real input route, advancing game loop, observable UI assertions; restore modified settings in teardown.
5. Repeat setup and a sequential target transition to detect duplicate fixture state.
6. Expand the declared input and version matrix, then build, runtime and device rows.
7. Aggregate receipts and verify deliverable identity at handoff.

MCP transports evidence; consumer fixtures define application behavior. Attribute argument rejection to pre-dispatch invocation, missing XML to orchestration, license or toolchain gaps to environment, assertion failure to product or fixture, and request loss only to observed transport evidence. Recovery follows `request-final-status` guidance in `docs/operations/CONTINUATION.md` before any retry.

## 8. Work packages

Paths are relative to the MCP repository. Load `skills/cross_platform_python/SKILL.md` before any Python change (router requirement); `skills/atomic_ipc_files/SKILL.md` only if a report becomes a polled file; `skills/cross_platform_shell/SKILL.md` only if launchers or CI change (none planned).

| Work package | Files and responsibilities | Depends on | Done when |
|---|---|---|---|
| WP0 Rebase | `git checkout master` in the hub mount; re-read §3 against `HEAD` | None | Field paths in §3 still match a fresh saved response |
| WP1 Contract | Three schemas derived from the consumer verdict v2 mapping and the §3 response shape; sanitized fixtures shaped like E05, E06 and E07; hand-written strict validator in `scripts/testing/validation_acceptance.py`; `templates/workflows/README.md` entry | WP0 | Valid and invalid fixtures behave; `evidence_summary.schema.json` byte-identical |
| WP2 Evaluator | `scripts/testing/evaluate_validation_evidence.py` (CLI) over the pure module; `tests/test_validation_acceptance.py` | WP1 | Deterministic aggregation, safe paths, hashes, exit contract tested on the CI OS matrix |
| WP3 Adapters | Adapter A (saved helper response) and adapter B (consumer verdict v2) in the pure module | WP2 | E05 and E06 normalize with provenance; adapter B reproduces E07 as 8 pass, 15 reused, 17 blocked |
| WP4 Compact | Import `_bounded_compact_json` from `templates/server_launcher.py` via the rollout runner's `sys.path` pattern; extract into a shared module only if the import proves impractical | WP2 | 8192-byte bound holds on the large fixture; full report complete |
| WP5 Docs | `docs/agents/AGENT_WORKFLOWS.md` (Evidence Checklist and Workflow 12: channel, stage, policy rows, blocked-denominator example), `docs/operations/SMOKE_TESTS.md` (§7 order), `docs/operations/CONTINUATION.md` (compact example), README cross-link to the existing native-client proof rule | WP1 to WP4 | Examples distinguish channel, stage and policy; `check_release_docs_freshness.py` passes |
| WP6 Consumer adoption | ConnectivityCheckerPro adds `executionChannel` per row, captures one native `unity_status_summary` receipt file, adds lane warning counts where the producer exposes them; evaluates E07-shaped output through adapter B | WP3 | One complete plan evaluated; seeded false-ready cases rejected |
| WP7 Closeout | Public `docs/architecture/designs/XUUNITY_MCP_VALIDATION_EVIDENCE_ACCEPTANCE_DESIGN_2026-09-21.md`; row in `DESIGN_PLAN_HISTORY.md`; no row in the public `docs/archive/retros/RETRO_REGISTRY.md` (its storage rule keeps host-private retros in this folder; the plan-history row names the private retro generically; its version header is already fixed at `98bf6eb`); `check_public_release_safety.py`, `check_release_docs_freshness.py`, `check_release_version_consistency.py` green | WP6 | Independent non-author acceptance recorded with evidence links |

Do not reimplement fields the producers already emit; bind to them by name.

## 9. Acceptance test matrix

| ID | Scenario | Required result |
|---|---|---|
| AT01 | Compile passed with one warning, zero-warning policy | Operation pass, acceptance fail |
| AT02 | Missing warning counts or `complete=false` package attribution | `diagnostics_unmeasured`, never assumed zero |
| AT03 | Cached-only or unmeasured compile, rebuild required | Blocked evidence |
| AT04 | Outer `status=ok` with `test_verdict` in `failed`, `no_tests`, `test_filter_no_match` | No acceptance PASS |
| AT05 | Build or export receipt supplied for a device-runtime row | Row unfulfilled; no stage promotion |
| AT06 | Helper healthy, journal `client_kind=cli`, no client receipt file | Native row `channel_unverified` |
| AT07 | Consumer verdict v2 with 40 lanes: 8 pass, 15 reused, 17 blocked | Counts exactly 40; `reusedCount=15`; overall blocked |
| AT08 | Scene, input mode, backend or version differs | Mismatched receipt cannot satisfy the row |
| AT09 | Artifact deleted or changed after a successful build | Historical outcome retained; deliverability blocked |
| AT10 | Source, settings or lock digest changes | Affected old receipts invalid for acceptance |
| AT11 | Two receipts for one row, no pin, no `supersedes` | `receipt_conflict`; no latest-wins |
| AT12 | Click delivered, UI state unchanged | Semantic acceptance fails |
| AT13 | Relative paths, spaces, Unicode, traversal, escaping symlink or junction | Portable resolution; escaping paths rejected |
| AT14 | Thousands of diagnostics and rows | Compact at most 8192 UTF-8 bytes; full report complete |
| AT15 | `evidence_summary.schema.json` and the three workflow templates | Byte-identical after the change |
| AT16 | Completed request with lost host delivery | Existing `tests/test_terminal_delivery_verdict.py` behavior unchanged |
| AT17 | Repeated sample setup, then sequential targets | One fixture instance, no new warnings, settings restored (consumer-owned) |
| AT18 | SDK or device unavailable | Explicit blocker before builds; no install or mutation |
| AT19 | Malformed, oversized or unknown schema, duplicate ids | Exit 2, bounded envelope with `evaluation_invalid` |
| AT20 | CLI receipt relabeled `native-mcp` without a client receipt file | Native acceptance rejected |
| AT21 | `test_verdict=runtime_timeout` | Row `blocked` with `runtime_timeout`, never pass |
| AT22 | Caller maps exit 2 as a blocked row | Documented as wrong; envelope reason makes it detectable |

Host tests run through `.github/workflows/windows-integration-tests.yml` (Windows, Ubuntu, macOS). Fixtures cover policy and path cases; real Unity is needed only for consumer boundaries that actually change. The live pilot needs recorded exact Unity versions, one real sample interaction, one native-client receipt file and one helper call, each tied to its route. If any is unavailable, the affected gate is reported blocked. Device rows cannot be replaced by simulation.

## 10. Delivery, compatibility and rollback

Small commits in order: schemas and validator with tests; evaluator and adapters; compact projection and docs; consumer adoption. Keep the evaluator opt-in during the pilot, then mandatory only for consumers that adopt an explicit plan. Do not broaden any consumer's platform promises.

No package version bump is specified here. Version and release policy applies when changes are prepared; no tag or publication is authorized by this document. No new runtime protocol or native tool is part of the first delivery.

Rollback removes the evaluator invocation and keeps every evidence and report artifact. It must mark strict acceptance unavailable, never fall back to a green result. Avoid storing reports under asset-imported paths unless the consumer needs them there.

## 11. Risks and success measures

- Bad plan means false completeness: the owner defines scope; unsupported and skipped dimensions are reviewed; software cannot infer product promises.
- Adapter drift: golden fixtures per supported shape (helper response, consumer verdict v2 pinned by its `schema_version`); unknown input blocks acceptance.
- Incomplete hashing scope: include settings, dependencies and tests; document exclusions; a content hash is not a reproducibility proof.
- Client kind is env-overridable: journal facts support but never replace the client receipt file; the design states this instead of implying attestation.
- Excess scope: first release offline and consumer-driven; no scheduler, no transport work, no dependency additions.
- Warning ownership ambiguity: complete classification or strict global policy; third-party diagnostics are never silently waived.
- Overhead: record evaluator wall time and report byte sizes on the fixture set; no token or cost claim without telemetry.

Success: all applicable AT cases pass, denominators stay fixed, zero false-ready outcomes on seeded negatives, bounded compact output, adapter B reproduces E07 exactly, one evidence-bound consumer evaluation. Independent non-author acceptance is required before calling the implementation accepted; missing platform, device or client proof stays a named gap.

## 12. Design history and handoff

- 2026-09-21: initial design from retrospective A1 to A7 against `v0.3.78`. A1 and A2 to WP1 to WP3; A3 to WP3 and WP5; A4 to WP6; A5 to WP4 and WP5; A6 to AT16 using existing recovery tests; A7 to WP7.
- 2026-09-21 (principal review): corrected the saved-response field paths and evidence owners; redefined the native-client receipt as operator-captured; dropped the v1 legacy adapter (no producer exists); added adapter B for the consumer verdict v2 and reframed §1 and WP6 around that existing implementation; stated the stdlib-only validation constraint and the exit-2 consumer mapping; separated `executionChannel` from the existing `executionLane`; added `reused` visibility and AT21 to AT22; moved the evaluator to `scripts/testing/`; noted A7 already landed at `98bf6eb`.

Decisions: D1, evaluator placement in `scripts/testing/`, decided here and overridable by the owner. D2, open: a host-only `client_probe` journal event when `unity_status_summary` is served to a native client (`client_kind`, `client_session_id`, `mcp_server_info.version`). It is Python host code with no bridge change, but it changes runtime behavior and belongs in its own small change after the offline evaluator has been used once.

This private document is the current handoff. On public promotion copy only sanitized reusable design into `docs/architecture/designs/` and register it in `DESIGN_PLAN_HISTORY.md` in the same change; keep private evidence links here. Implementation starts at WP0. Independent acceptance of this design is pending and must not be presented as passed.

## 13. Implementation record (2026-09-21)

Implemented from `master` at `98bf6eb` in the AIFoxsterDevHub mount; nothing committed, tagged or pushed.

- MCP: `scripts/testing/validation_acceptance.py` (specs, validators, adapters A/B, evaluator, compact projection), `scripts/testing/evaluate_validation_evidence.py` (CLI), `tests/test_validation_acceptance.py` (36 tests), three generated schemas plus `templates/workflows/README.md`, docs (`AGENT_WORKFLOWS.md` checklist, anti-patterns and Workflow 12 machine-checked acceptance; `SMOKE_TESTS.md` §5d; `CONTINUATION.md` evaluator section; README native-receipt cross-link), `CHANGELOG.md` Unreleased, public design `docs/architecture/designs/XUUNITY_MCP_VALIDATION_EVIDENCE_ACCEPTANCE_DESIGN_2026-09-21.md`, `DESIGN_PLAN_HISTORY.md` row, designs README bullet.
- Host validation: focused suite 36/36; full suite 1132 tests OK (14 skipped); `check_release_version_consistency.py`, `check_release_docs_freshness.py`, `check_public_release_safety.py` green after the doc edits. Unity was not launched.
- Consumer pilot (WP6): `ConnectivityCheckerPro/scripts/close-connectivity-checker-pro-release.py` gained `EXECUTION_CHANNELS`, `annotate_execution_channels`, `native_client_receipt_check` and `--native-client-receipt` (informational check, not in the required set; making it required is the owner's call); the lifecycle runner records `execution_channel: helper-cli`; consumer suite 105 tests OK. The real E07 verdict re-evaluated through adapter B: 58 required rows, 37 pass, 21 blocked (17 matrix, 3 Android profiles, publisher account), 15 reused; matrix subset exactly 40 = 23 pass + 17 blocked; verdict `blocked`. Report and derived inputs: `ConnectivityCheckerPro/release/evidence/1.2.2/acceptance/`. Matrix lanes already carried `compiler_cleanliness`, so the "lane warning counts" item needed no change. `CCP_PUB/ProjectSettings/EditorSettings.asset` was already modified before this work and was not touched.
- Native-client receipt: captured live from this Claude Code session against `xuunity-mcp 0.3.78` (`client_kind=mcp_server`; the editor was not running, so it proves client wiring only): `ConnectivityCheckerPro/release/evidence/1.2.2/native-client/unity_status_summary-claude-code-2026-09-21.json`, SHA-256 `3645e40b54b9ad79d5d305157a61614aea011d680767e2d25fbbced8f3a31637`.
- Still open: a fresh consumer closeout run with `--native-client-receipt` so the new fields land in a real verdict; D2; independent non-author acceptance. Suggested commit split: schemas+validator+tests; evaluator+adapters+CLI; docs+design records; consumer runner (separate nested repo).
