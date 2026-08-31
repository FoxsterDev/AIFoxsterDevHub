# Principal Implementation Prompt — Update the Unity Unified Harness

Use this prompt in a fresh Codex task opened at:

`/Users/siarheikha/Projects/FoxsterDev/AIFoxsterDevHub`

## Role

Act as the principal engineer responsible for independently auditing, updating,
stress-testing, and truthfully converging the existing Unity Unified Harness in
`AIFoxsterDevHub`.

This is an implementation task, not a request for another plan or prose-only
review. Continue through diagnosis, focused changes, adversarial tests,
validation, durable evidence, and correctly partitioned commits while safe,
in-scope work remains. Stop only for a genuine owner decision, unavailable
required external state, or an unsafe conflict that cannot be isolated.

Use English for source-controlled prompts, reports, handoffs, specifications,
and technical metadata. Converse with the owner in the language they use.

## Mission

Update the current native-host Unity Harness so that it is:

- aligned with the repository's current gitlinks and Unity tooling contracts;
- resistant to fixture editing, stale constants, unknown fields, relabeling,
  and false-ready or false-release claims;
- reproducible from the current tree instead of relying on stale status prose;
- compact in default context and narrow in Stop-hook scope;
- truthful across Hub, public AIRoot, standalone satellites, package source,
  consumers, exact Unity versions, build targets, and proof ceilings;
- simpler than the process it replaces.

Keep the execution shape native and small:

`native Codex host -> root router -> Hub kernel -> nearest satellite adapter -> optional XUUnity route -> focused proof -> zero or one outcome record`

Do not create an agent runtime, workflow engine, task database, provider
abstraction, daemon, queue, replacement broker, session manager, or parallel
status framework.

## Non-Negotiable Safety And Scope

1. Read every selected `AGENTS.md`, router, protocol entrypoint, or skill from
   first line through EOF before acting on it.
2. Preserve every unrelated dirty-worktree change. At prompt-authoring time,
   `ConnectivityCheckerPro/Marketing/**` contains owner work and exported image
   assets. Enumerate it again and do not edit, stage, delete, regenerate, or
   absorb it.
3. Treat the root, `AIRoot`, `ConnectivityCheckerPro`,
   `DevAccelerationSystem`, and
   `AIRoot/Operations/XUUnityLightUnityMcp` as separate Git boundaries. Review
   and commit a child in its own repository before changing a parent gitlink.
   Do not advance a gitlink merely to make status clean.
4. Never use reset/checkout/clean commands to remove owner changes. Do not
   delete Unity `Library/` unless a clean regeneration is specifically needed,
   the exact project root was resolved from
   `ProjectSettings/ProjectVersion.txt`, and the deletion is limited to that
   one `Library/`.
5. Before any Unity launch, run:

   ```sh
   python3 scripts/validate-unity-privacy.py --require-host-opt-out
   ```

   A red privacy result forbids Unity launch. Docs/tooling-only Harness work
   must not launch Unity or run product regressions merely to make evidence
   look broader.
6. Do not repin MCP, change a supported Unity floor, change product/runtime
   behavior, or alter release promises without an independently justified
   owner-approved reason. Current gitlinks are inputs to reconcile, not
   authorization for another upgrade.
7. Keep host-private topology and evidence in the Hub. Keep reusable,
   public-safe behavior in AIRoot or the independently public MCP repository.
   Do not leak host paths, private project facts, or credentials into public
   satellites.
8. A current green result does not erase a retained historical failure. A
   corrected present-tense result and the original escaped/baseline observation
   are different records.

## Mandatory First Reads

Read these files completely before planning edits:

1. `AGENTS.md`
2. `AIOutput/Harness/KERNEL.md`
3. `AIOutput/Harness/current-handoff.md`
4. `AIOutput/Harness/validation-evidence-2026-08-29.md`
5. `AIOutput/Harness/grooming-audit-2026-08-29.md`
6. `AIOutput/Harness/privacy-preflight-2026-08-29.md`
7. `evals/unity-harness/README.md`
8. `evals/unity-harness/cases.json`
9. `evals/unity-harness/score.py`
10. `scripts/validate-unity-harness.py`
11. `scripts/validate-unity-privacy.py`
12. `.codex/hooks.json`
13. `.codex/hooks/harness_stop.py`
14. `AIOutput/Registry/host_topology.yaml`
15. `AIOutput/Registry/setup_status.yaml`
16. `WORKSPACE.md`

Before editing a child, additionally read its nearest full router and adapter:

- `AIRoot/AGENTS.md`
- `ConnectivityCheckerPro/AGENTS.md`
- `ConnectivityCheckerPro/Harness/README.md`
- `ConnectivityCheckerPro/Harness/unity-adapter.md`
- `DevAccelerationSystem/AGENTS.md`
- `DevAccelerationSystem/Docs/ai/unity-unified-harness-adapter.md`
- `AIRoot/Operations/XUUnityLightUnityMcp/AGENTS.md`
- `AIRoot/Operations/XUUnityLightUnityMcp/docs/clients/AGENTS.md` when client
  routing is affected.

If subagent delegation would materially help and is available, first read
`AIRoot/Modules/AgentOperations/subagent_delegation.md` and give workers
non-overlapping scopes, stable evidence IDs, and explicit denominators. Do not
block on an API key when native subagents are sufficient. The principal agent
must personally verify the final combined evidence and all skill instructions.

## Observed Starting Point — Reproduce, Do Not Trust Blindly

The following was observed on 2026-08-31. Re-resolve every hash and result
before editing because concurrent work may have advanced:

- root HEAD: `44951157d46a3803ed20bb2a56c7d5fadaefa028`;
- AIRoot: `376e4f9ca2f3682df9a655e2021f445f9716fea0`;
- ConnectivityCheckerPro: `0daaab807411f1e43660440b9c9ec3d5e9259655`,
  with unrelated dirty `Marketing/**` work;
- DevAccelerationSystem: `edb9079a12eea3f7a5c0ef384e05ff176ae62c9a`;
- nested MCP: exact tag `v0.3.63`, commit
  `a72c79b675311583827ef5c9e966279555e64261`.

The narrow privacy gate passed for seven projects. The current frozen eval
self-test passed `8/8`, and its one intentional mutation failed `7/8` as
expected. The aggregate static Harness gate was red, not green:

- `scripts/validate-unity-harness.py` still freezes MCP `v0.3.62`, version
  `0.3.62`, and hash `7b8b139d...`, while the checked-in gitlinks, package, and
  seven consumers use exact `v0.3.63` / `a72c79b...`;
- it calls removed command
  `AIRoot/Operations/XUUnityLightUnityMcp/scripts/tools/sync_agent_routers.py`;
- `AIRoot/scripts/routing_audit.py --host-root .` rejects the intentional
  `unity_unsupported_legacy_compatibility_lane` project kind;
- the same routing audit requires literal `Standalone:` although the current
  MCP router truthfully uses `Standalone mode:` under `## Mode Detection`;
- `AIOutput/Harness/current-handoff.md` and the dated validation evidence still
  describe the previous `v0.3.62` / Unity `6000.3.3f1` state.

These are baseline observations, not preselected fixes. Determine the correct
owner and semantic contract for each. Do not add a string or recreate a deleted
script merely to silence a validator.

## Phase 0 — Freeze And Partition The Baseline

Before edits:

1. Record root and recursive submodule status, branch, HEAD, gitlink pins,
   untracked files, and dirty paths for every Git boundary.
2. Confirm that the only known Connectivity dirt is owner-owned marketing work;
   if the scope differs, partition it explicitly before proceeding.
3. Run and preserve the real output of:

   ```sh
   python3 scripts/validate-unity-privacy.py --require-host-opt-out
   python3 evals/unity-harness/score.py
   python3 evals/unity-harness/score.py --self-test
   python3 scripts/validate-unity-harness.py
   python3 AIRoot/scripts/routing_audit.py --host-root .
   git diff --check
   ```

4. Classify every failure as current Harness defect, stale validator, stale
   evidence, child-owned contract drift, unavailable environment, or unrelated
   owner work. Do not call the aggregate green while any mandatory Harness
   failure remains.
5. State a file-touch plan and validation budget. Prefer one bounded
   tooling/docs slice and one final outcome record.

## Required Update Outcomes

### 1. Restore One Current Tooling And Version Contract

Remove contradictory MCP truth. Prefer deriving the approved MCP tag, commit,
package version, and consumer pin/hash from the checked-in gitlinks plus the
exact tag and package metadata, then validating all seven consumers against
that one source. If a separate frozen approval record is genuinely necessary,
there must still be exactly one machine-readable owner.

Do not leave release/tag/hash facts duplicated independently across Python,
handoff prose, evidence, manifests, and locks. Do not make the gate
self-fulfilling: it must still reject a mismatched consumer, non-exact tag,
wrong package version, or unexpected gitlink.

Discover the current supported MCP router/contract validation command from the
`v0.3.63` repository. Use it if it exists and proves the required property. If
router generation was intentionally retired, validate the current semantic
router contract; do not restore `sync_agent_routers.py` as compatibility theater.

### 2. Reconcile Routing Semantics At The Correct Owner

Resolve the two routing-audit failures semantically:

- decide whether an unsupported legacy compatibility lane is a reusable public
  project kind. If yes, add it consistently to AIRoot's kind taxonomy,
  generators, audit, fixtures, and tests. If not, use an existing public kind
  plus an explicit local unsupported-support-status field without weakening the
  release boundary;
- make standalone MCP detection validate meaning, not a brittle obsolete
  substring. `Standalone mode:` under `## Mode Detection` is not a failure just
  because a validator searches for `Standalone:`.

Public AIRoot changes require public-safe tests and an independent child-repo
commit. Host-only exceptions stay in the Hub and must not distort public
taxonomy.

### 3. Harden The Frozen Scorer Against Gaming

Keep the scorer deterministic and offline. It must not launch an agent, Unity,
manage sessions, select models, or write task state.

Upgrade the evaluation contract as follows:

- separate immutable case expectations from candidate/result observations so
  the same object does not own both the question and its claimed answer;
- enforce strict allowed-key schemas for the root payload, cases, results, and
  any optional observation contract;
- reject duplicate JSON keys, unknown fields, missing required fields,
  duplicate IDs, unknown IDs, wrong types, and ambiguous legacy counters;
- keep policy floors and exact case-count expectations in code or one protected
  policy owner, not in easily lowered result data;
- preserve blocked release and device-ceiling truth;
- when a historical failure is retained, pin its stable ID, evidence mode, and
  failed/blocked state so relabeling or deleting its markers cannot silently
  turn it green;
- use explicit evidence modes such as deterministic contract, historical
  replay, and live observation. Never label a replay as a new live run;
- add tracked unit tests. The existing evidence claims four Stop-hook tests,
  but no discoverable test file currently proves that claim; replace the claim
  with a real tracked suite or correct the evidence.

Extend the active Unity-specific set from eight to exactly ten frozen cases,
without creating a general benchmark platform. Keep the existing eight
behavior families and add two regression cases grounded in the reproduced
failures:

9. current tooling/version-contract drift — stale version/hash constants or an
   obsolete validation entrypoint cannot pass against newer checked-in gitlinks;
10. standalone/unsupported-lane routing compatibility — semantic standalone
    mode and the unsupported compatibility boundary remain truthful without
    brittle literal matching or false release support.

Add red-before/green-after mutation tests at minimum for:

- a typo or unknown result field;
- deletion of a required field or case;
- duplicate JSON key and duplicate ID;
- lowering a code-owned case count or any introduced acceptance floor;
- converting the mandatory release failure into pass;
- claiming device behavior below physical-device proof;
- stale MCP tag/hash/consumer pin;
- obsolete generator command or brittle standalone marker.

Do not add a `3/2/1` qualifying-slice pilot merely because another Hub uses
one. If this Hub claims measured live adoption, define a separate observed and
qualifying cohort using genuine existing source records, stable IDs, and
code-owned thresholds. Otherwise make no pilot claim and manufacture no Unity
work.

### 4. Make Context Economy Reproducible

Document the exact default-loaded composition for a task started at:

- Hub root;
- AIRoot;
- Connectivity root and one consumer;
- DevAccelerationSystem root and demo;
- nested MCP standalone and host-mounted mode.

Compute current line/byte counts from the actual tree on every validation run.
If a historical pre-Harness baseline can be reconstructed from a named commit,
freeze that denominator and report a real reduction. If it cannot, do not
invent a percentage: report reproducible current absolute counts and enforce
reasonable head/size budgets instead.

The validator must catch stale self-reported counts. Keep root/kernel/adapters
compact, but do not delete safety, privacy, exact-version, standalone, or proof-
ceiling rules merely to improve a percentage.

### 5. Preserve A Narrow, Tested Stop Hook

Keep the native Codex Stop hook static-only and owner-trusted:

- ordinary product and `ConnectivityCheckerPro/Marketing/**` changes no-op;
- only Harness/routing/config surfaces trigger the gate;
- internal hook faults fail open with a visible warning;
- a real scoped validation failure blocks once with exact bounded output;
- `stop_hook_active` prevents recursion;
- rename, untracked-file, root, child-repository, and unrelated-dirty cases are
  covered by tracked tests;
- no Unity launch, product tests, network access, package installation, daemon,
  or transcript parsing occurs from Stop.

Do not broaden hook scope just because a path is important. Add a path only
when a reproduced unnoticed regression proves the static gate needs it.

### 6. Converge Truthful Status Without Multiplying Artifacts

Keep the existing 2026-08-29 audit/evidence as historical records. Create one
new dated outcome owner for this update, preferably:

`AIOutput/Harness/validation-evidence-2026-08-31.md`

Update `AIOutput/Harness/current-handoff.md` as a short current pointer/state
summary. Do not duplicate command transcripts into the handoff, task registry,
multiple reports, or project-local memories.

The outcome must include:

- exact root/child/nested commit denominator and dirty-work partition;
- pre-fix red failures and post-fix results;
- version/tag/hash ownership and seven-consumer result;
- ten-case scorer and mutation-test results;
- hook test results and trigger/no-op proof;
- current context composition and honest baseline availability;
- strongest proof ceiling and all unavailable Unity/device/release evidence;
- package/app/version decision;
- rollback and remaining owner actions.

Do not append a task-registry closure event unless the human explicitly issues
the repository's closure trigger.

## Implementation Constraints

- Use Python 3 for new deterministic validators/tests. Keep shell as a thin
  wrapper for Git, Unity, or system commands.
- Prefer extending existing files over adding layers. A small sibling contract
  helper is acceptable when it keeps the scorer readable and bounded; it is
  not a registry or runtime.
- Keep the scorer focused and approximately at or below 300 lines, the Stop
  hook at or below 150 lines, and any new helper small enough to review in one
  pass. If a file must exceed its budget, explain the concrete reason in the
  evidence.
- Validate actual semantics rather than passing via literal-string padding.
- Preserve source/consumer separation and exact Unity version/build-target
  truth. A package test is not a consumer compile; a compile is not PlayMode;
  Editor/Simulator is not physical-device proof.
- Do not change runtime code, serialized assets, package contents, public API,
  marketing copy, or release version merely to improve Harness scores.

## Validation Order

Run the smallest affected tests first, including every new red/green mutation.
Then run the current static suite:

```sh
python3 scripts/validate-unity-privacy.py --require-host-opt-out
python3 -m unittest discover -s evals/unity-harness -p 'test_*.py'
python3 evals/unity-harness/score.py
python3 evals/unity-harness/score.py --self-test
python3 -m unittest discover -s .codex/hooks -p 'test_*.py'
python3 AIRoot/scripts/routing_audit.py --host-root .
python3 scripts/validate-unity-harness.py
git diff --check
```

Also run the current child-owned static generator/validator commands selected
from their own routers. Do not preserve obsolete command names from this
prompt if the current child contract names a replacement.

Run Unity only if the final diff affects Unity runtime, packages, serialized
content, or a claim whose required proof cannot be met statically. In that
case, privacy must be green first, use exact editor/build target, acquire the
existing shared execution resource, run the narrowest falsifying proof, and
restore generated state without touching source-owned files. Do not run broad
matrices for a docs/tooling-only update.

## Acceptance Criteria

The update is complete only when all of the following are true:

1. `scripts/validate-unity-harness.py` is green on the current checked-in
   recursive topology, or every remaining failure is accurately shown as an
   external/unavailable proof ceiling rather than a Harness contradiction.
2. MCP tag, commit, package version, and all seven consumer pins/locks have one
   current machine-verifiable owner and no stale `v0.3.62` claim remains active.
3. The current MCP validation route exists; no deleted script was recreated
   only to satisfy the Hub.
4. AIRoot routing audit is green for the chosen semantic taxonomy and current
   MCP standalone contract.
5. Ten frozen cases pass; every required mutation is rejected.
6. Unknown fields, duplicate keys/IDs, deleted cases, lowered policy floors,
   false device claims, and false release claims cannot silently pass.
7. Any retained failure remains visible after the current correction.
8. Context composition is recomputed from the tree; no stale percentage is
   accepted as evidence.
9. The Stop hook has tracked tests, stays static/scoped, and no-ops for ordinary
   product and current owner-owned marketing work.
10. No unrelated dirty file is edited or staged, and each Git boundary is
    committed separately when changed.
11. Exactly one new detailed outcome record owns this update; the current
    handoff remains short.
12. The final response and evidence state an explicit package/app/version
    decision and do not claim Unity, device, release, or clean-worktree proof
    that was not actually run.

## Explicitly Rejected Work

- a new multi-agent runtime or orchestration framework;
- replacing XUUnity Light Unity MCP's existing execution architecture;
- a general benchmark platform, dashboard, task DB, queue, or event stream;
- mandatory per-task profiles/contracts/results/records;
- broad product regression or Unity launch from the Stop hook;
- copying host-private rules into AIRoot or the public MCP repository;
- marking Sample2021 supported to make an audit pass;
- changing a nearby Unity patch version into exact-version proof;
- deleting or staging owner-owned Connectivity marketing work;
- creating fake live slices, fake device proof, or fake release readiness;
- updating gitlinks before child commits and validation are complete.

## Final Handoff Format

Lead with the implemented outcome, not the work log. Report:

1. exact commits by Git boundary;
2. corrected contract and architecture changes;
3. pre-fix failures versus post-fix results;
4. ten-case and mutation-test counts;
5. context composition and whether a historical reduction denominator was
   actually reconstructable;
6. privacy, routing, static Harness, hook, and any Unity proof actually run;
7. remaining blockers/ceilings and owner actions;
8. preserved unrelated dirty paths;
9. package/app/version decision;
10. the single durable evidence path.

Never summarize an aggregate gate as green when its command is red. Never use
the existence of this prompt as evidence that the Harness was updated.

## Optional Cross-Hub Lessons — Read-Only Comparator

If the sibling repository is available, you may inspect these files as a
read-only pattern comparator:

- `/Users/siarheikha/Projects/FoxsterDev/PersonalAppsLifeImprovements/Docs/status/evidence/2026-08-30-unified-harness-independent-principal-audit.md`
- `/Users/siarheikha/Projects/FoxsterDev/PersonalAppsLifeImprovements/Tools/unified_harness_contract.py`
- `/Users/siarheikha/Projects/FoxsterDev/PersonalAppsLifeImprovements/Tools/unified_harness_eval.py`

Transfer only the proven principles: code-owned thresholds, strict schemas,
retained failure invariants, truthful active case counts, and current-tree
context measurement. Do not copy iOS cases, paths, proof ceilings, pilot values,
status machinery, or app-specific policy into this Unity Hub.
