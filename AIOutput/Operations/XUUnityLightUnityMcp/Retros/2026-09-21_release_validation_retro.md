# XUUnity MCP release-validation retrospective

Date: 2026-09-21. Visibility: host-private. Status: analysis complete; promotion proposals pending.
Scope: this chat's ConnectivityCheckerPro release work and XUUnity MCP use. No new Unity execution or MCP code changes were made for this retrospective.

## 1. Executive summary

The strongest demonstrated failure was validation scope and operator reporting: narrow compile/test success was initially described too broadly, while the customer's actual sample scene and input configuration were not adequately exercised. Product defects and product-owned runner defects must not be counted as MCP transport failures.

Six deliberately selected saved helper responses show successful Unity outcomes: four lifecycle test requests, one sample PlayMode request and one clean compile. This is a final-evidence sample, not a session-wide success rate. Two user-project requests additionally have matching Unity completion and host-delivery journal events. Native MCP client wiring and transport recovery under fault injection remain unproven.

Existing MCP contracts already preserve warnings, distinguish delivery from semantic success, expose request recovery, and recommend compact output. The smallest useful improvement is to enforce those contracts in consumer release summaries and acceptance criteria, rather than invent another verdict vocabulary or rewrite transport.

## 2. Evidence base

See [machine-readable evidence catalog](2026-09-21_release_validation_evidence.json): source paths, SHA-256 hashes, request IDs, selected payload fields and journal event references. Private raw logs are not duplicated into public documentation.

| ID | Evidence | Supported conclusion |
|---|---|---|
| E01–E04 | Final lifecycle helper responses, two tests on each of Unity 2022.3.62f3 and 6000.6.0b3 | Four named test requests passed, callback completion, zero post-settle errors; all report no lifecycle churn |
| E05 | User-project compile response | StandaloneOSX script compilation passed, zero errors/warnings, measured rebuilt-assembly evidence |
| E06 | User-project PlayMode response | One selected sample test passed; not certification of every UI interaction or platform |
| J01 | Ten matched journal events for E05/E06 | Both requests have submitted, started, completed, delivery-observed and progress events; client kind is CLI |
| S01 | Later bridge-state snapshot | Unity 6000.6.0b3, generation 10, reported healthy/idle at its recorded heartbeat; cannot prove earlier request state or current liveness |
| E07 | Final release verdict | Overall BLOCKED; compatibility 23/40 PASS, 17 BLOCKED; sample E2E 6/6 PASS |
| E08–E09 | Earlier and corrected sample-runner aggregates | An earlier failing orchestration result was followed by successful corrected runs |
| E10 | Warning negative-control report | Archived diagnostic replay; not a newly executed Unity negative-control run |
| T01 | Chat/session summary and owner-reported errors | Initial license block, invocation mistake, fixture repairs, UI-modal incident and polling behavior; not independently journal-certified here |

Reviewed current public contracts: README.md (warning counts, compact output and native-client readiness), DESIGN.md (terminal envelope, semantic click effectiveness and recovery), CONTINUATION.md (recovery mini-playbook and warning evidence), SMOKE_TESTS.md (compile-first ordering). Public RETRO_REGISTRY.md already records implemented verdict/warning/rebuild improvements; its header still says v0.3.77, so it is not an authoritative package-version probe.

Selected full helper response files total 102,735 bytes; E07 is 166,823 bytes. These are stored JSON byte sizes, not measured token consumption. There is no controlled compact-versus-full benchmark or complete polling census. Four lifecycle journals were not independently re-correlated in this retrospective; their saved callback-backed responses were inspected.

## 3. Timeline

| Phase | Incident and actual owner | Resolution/evidence boundary |
|---|---|---|
| Initial build failure | Generic runtime-initialization entry point; product code | Dispatcher initialization corrected and named lifecycle checks added |
| Editor availability | Invalid editor license reported; environment | Owner restored license; no evidence that transport caused it |
| New-project sample | Legacy StandaloneInputModule under Input System-only settings; shipped sample | Input-backend-aware setup and actual sample-scene coverage added |
| Test authoring | Assembly references, focus settings and scene-load timing; test fixture | Fixture corrected; later tests passed |
| Compiler diagnostics | UAC1001 and CS0618; product/sample | Runtime-only field serialization and deprecated lookup fixed; E05 clean |
| Runner false failure | Relative XML result destination; product Python runner | Absolute output path; E08 versus E09; not an MCP lifecycle false negative |
| Strict runtime warning gate | Duplicate smoke component across sequential target builds; fixture | Idempotent setup and sequential-target proof; warning not suppressed |
| Validation interruption | Asset Store Tools update modal and CUA failures; vendor/UI route | Runner scoped update-check handling; do not attribute to MCP or claim a process was killed |
| Release closeout | Partial platform capacity and missing device/publisher evidence | E07 correctly remains BLOCKED despite artifact/tag preparation |
| Retrospective | Large registry/raw payload output repeated during evidence gathering | Another operator compact-output lapse; bounded extraction used afterwards |

## 4. What worked well

- Request identity and journals let us distinguish Unity completion from host delivery for E05/E06 without rerunning operations.
- Callback-backed test results retain counts, filters, post-settle state and trust information. Compile evidence includes diagnostics and rebuilt/cache accounting.
- The release process eventually tested the shipped sample, input modes and observable behavior, and enforced compiler/runtime warning cleanliness.
- The final verdict preserves blocked rows instead of silently shrinking the denominator. Owner-authorized local tagging did not become proof of publication readiness.
- Existing public recovery guidance explicitly prevents blindly retrying a completed operation.

## 5. What worked poorly

- Early regression claims exceeded the scene, backend and execution stages actually tested. The owner found the missing real-user path.
- CLI-to-bridge execution was loosely called MCP validation without proving native client tool wiring.
- Warning evidence existed but was not consistently treated as a release-policy decision from the start. Compile PASS is intentionally error-based.
- Test fixtures and orchestration were debugged during expensive matrix execution. Cheap path, idempotency and input-fixture checks should have preceded it.
- Repeated polling, raw payload dumps and large error storms increased diagnosis cost. Exact time/token totals are unavailable.
- The selected evidence demonstrates no transport-loss defect. It would be misleading to blame MCP for product bugs, unavailable toolchains, CUA failures or runner path mistakes.

## 6. What was not explicit enough

Every claim needed its execution channel, exact source/artifact identity, Unity version, platform/backend, scene/input mode and stage. Script compilation, APK creation, Xcode export, native player launch and physical-device validation are different proofs.

The 23 passing platform rows mean seven Android IL2CPP APK builds, eight iOS Xcode exports and eight macOS Mono build/runtime checks. They do not prove Android or iOS device behavior. Sixteen Windows/Linux rows were blocked by missing modules/runners, and one Android Unity 6000.4 row by missing toolchain components. Desktop IL2CPP and physical-device network/performance behavior were not established. Native MCP client setup was not certified by helper readiness.

## 7. What the operator needed but did not have

The main missing artifact was a concise, enforced consumer acceptance ledger that joins the existing MCP evidence to release requirements. The operator also needed a fixture preflight before the matrix and an early capability report explaining unavailable devices/toolchains.

The operator did have request journals, compact status and diagnostic counts; those were not missing MCP features. No evidence supports an additional automatic retry mechanism. Recovery should use request-final-status and the existing recommended action before replaying work.

## 8. Scoring

Subjective 1–5 assessment of this observed session, not a benchmark. No aggregate score: several categories lack sufficient evidence.

| Category | Score | Basis / confidence |
|---|---|---|
| Unity-side execution stability | 4/5 | Six selected final outcomes succeeded; selection-biased, medium confidence |
| Request journaling quality | 4/5 | Completion plus delivery correlated for two requests; medium |
| Bridge health observability | 4/5 | Rich state and post-settle fields; historical snapshot limits, medium |
| Wrapper-to-operator clarity | 3/5 | Good fields, inconsistent operator interpretation/channel naming; medium |
| Recovery guidance quality | 4/5 | Concrete existing mini-playbook; not fault-injection tested here, medium |
| Transport lifecycle transparency | N/A | No demonstrated reconnect/lost-response incident in selected receipts |
| End-to-end trustworthiness during churn | N/A | Selected tests explicitly report no lifecycle churn |
| Parallel request handling | N/A | No controlled parallel-request evidence |
| Token efficiency of default operator path | N/A | Compact default not benchmarked; actual operator usage 2/5 |
| Time-to-diagnosis | 2/5 | Repeated owner-discovered gaps and fixture rework; qualitative, low confidence |
| Validation workflow discipline | 2/5 initially; 4/5 at closeout | Real scene, warning gates and explicit BLOCKED reporting added; medium |

## 9. Priority improvements

This is the concrete apply package. Proposed items are not represented as shipped MCP changes.

| ID / priority | Owner and target | Smallest change / current status | Acceptance check |
|---|---|---|---|
| A1 / P0 | Consumer release runner and XUUnity delivery protocol | Require a coverage row with channel, version, backend, scene/input, stage, artifact/source hash, outcome and evidence pointer. Partially implemented in this product; standardize reuse. | APK build cannot satisfy device-runtime requirement; missing rows remain BLOCKED/NOT_RUN and denominator stays fixed. |
| A2 / P0 | Consumer summary policy; MCP README/SMOKE_TESTS examples | Use existing warning/rebuild fields and test_verdict; never infer clean release from status=ok/passed. Warning gate already implemented in this product. | Compile with one warning yields compile PASS but release cleanliness FAIL; cached-only compile cannot prove rebuilt edits. |
| A3 / P1 | Setup acceptance and operator summaries | Label helper/CLI bridge verification separately from native MCP-client verification. Existing README already requires this; enforce report generation. | Helper healthy plus absent native unity_status_summary receipt yields native-client UNVERIFIED. |
| A4 / P1 | Product fixture and smoke ordering | Before matrix: compile, one actual sample PlayMode lane, output-path check, repeat fixture setup, sequential-target check, then input/version expansion. Several fixes already applied locally. | Relative output input is normalized; repeated setup creates one probe; actual click changes expected UI state and a no-op fails. |
| A5 / P1 | Operator wrappers and CONTINUATION examples | Use existing compact summaries by default, persist full responses once, inspect bounded failure samples. Do not add redundant verdict fields. | Normal run emits compact terminal decision plus artifact pointers; full output only on explicit escalation; no raw repeated polling. |
| A6 / P2 | Wrapper regression tests and SMOKE_TESTS | Reuse existing lifecycle-recovery acceptance cases; run only when transport changes warrant it. No new defect demonstrated here. | Completed Unity request with lost delivery preserves confirmed completion and no blind retry; pre-submit argument error is not a Unity failure. |
| A7 / P2 | Public retro registry maintenance | Reconcile header version against actual release metadata during normal triage; avoid historical evidence relabeling. | Registry freshness is separate from the release/version probe and archived evidence retains its original version. |

## 10. Public-promotion recommendations

Promote sanitized acceptance examples and the scope-ledger template into README/SMOKE_TESTS or the consumer XUUnity delivery protocol. Add one compact operator example to CONTINUATION using existing result fields. DESIGN already explains lifecycle disposition, semantic click success and compact envelopes; do not duplicate these as new architecture work.

Keep project names, local absolute paths, request IDs, license/account details and raw journals in this private retro. Public promotion remains proposed and requires removal of session-specific material. Do not add public MCP transport work solely to address product-owned build scripts. No public files or MCP runtime code were changed in this retrospective.

## 11. Final verdict

The inspected helper/bridge operations are supported by useful evidence. The major systemic issue was overclaiming validation scope and failing to apply existing evidence contracts consistently. Confidence improved after testing the actual sample and making warning, stage and blocked-coverage evidence explicit; the final release verdict is still BLOCKED.

Next implementation order: enforce A1/A2 in reusable consumer reporting, enforce A3 channel truth, then A4/A5 preflight and compact operation. Keep A6 as existing-contract acceptance coverage, not an asserted transport bug. The report and evidence catalog are complete; promotion proposals remain open.
