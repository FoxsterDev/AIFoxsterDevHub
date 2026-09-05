Readiness: implemented-unverified
Independent acceptance: REVISE
Accept as complete: no
Next required action: With owner authorization, disable Unity Editor `EnableEditorAnalyticsV2`, rerun `scripts/validate-unity-privacy.py --require-host-opt-out`, then resolve the exact MCP v0.3.72 package graph and compile the affected Hub source/consumer projects on their recorded Unity versions.
Reviewer context: `/root/final_diff_reviewer`; reviewer authored the reviewed diff: no.
Proof blockers: Exact Hub consumer package resolve/compile for MCP v0.3.72 is missing because launch authority is blocked solely by `EnableEditorAnalyticsV2`; Unity was not launched. Upstream v0.3.72 static/maintainer evidence does not substitute for this Hub consumer boundary.

# Unity Harness Current-Contract Convergence Evidence

Date: 2026-09-02 task packet, executed and revalidated 2026-09-05

## Scope And Method

This is the single new detailed outcome for the current-contract convergence.
It records the isolated implementation branch, the latest immutable Unity MCP
release decision, deterministic static proof, the independent review result,
and the remaining owner gate. Historical 2026-08-29 and 2026-08-31 evidence
was neither edited nor relabelled.

Work was isolated from the user's active checkouts under
`/private/tmp/aifoxster-harness-v0372.qOpzLa/`. Child repositories were
committed before their parent gitlinks. No push, tag, release, upload, host
preference mutation, Unity launch, product regression run, or device claim was
performed.

The final review uses a detached attestation because a file cannot contain the
SHA-256 of its own exact bytes. There are no status-file exclusions: each scope
must equal the complete sorted `git diff --name-only --no-renames BASE...HEAD`
denominator. The final task handoff reports the exact final root commit and all
five v4 fingerprints after this outcome commit exists.

## Git Boundaries And Pins

| Boundary | Isolated base | Task/follow-up head represented by this outcome | Parent-pin decision |
| --- | --- | --- | --- |
| Hub root | `878f4e6d3ddfea1647330a63c5dfe1bdfd02fe14` | `d1d4b831d7d1a3e69d2449691b929ecd9ea5fcd2` | Root status-only outcome commit follows; its exact SHA is reported externally because a commit cannot contain its own SHA. |
| AIRoot | `86e86d64975fedccb195e0a21ea6ff2c340b62a7` | `517493efeca711def648d18aecaf6882ed8de313` | Root pin advanced exactly from base to child head. |
| ConnectivityCheckerPro | `8cc785f94be6558169f48b91840efe37b0466d90` | `c8559e81df493d1f740d834d2a7908dcae4a541c` | Root pin advanced exactly from base to child head. |
| DevAccelerationSystem | `ca99e6932cbda965463753fc3c75c162b571c07b` | `ebea7cb98fdd77556c8529eacc9f9d05b895faa2` | Root pin advanced to the Harness head and then to the owner-authorized `.editorconfig` line-ending snapshot. |
| XUUnity Light Unity MCP | `a72c79b675311583827ef5c9e966279555e64261` (`v0.3.63`) | `facc2081ab19d1fe4ab3adfd048e1385575aca70` (`v0.3.72`) | AIRoot pin advanced to the latest stable annotated release after explicit owner authorization. |

Task-owned child commits:

- AIRoot: `ee03277b133c87333fae854c4afd0132548a9aa3` and
  `517493efeca711def648d18aecaf6882ed8de313`.
- ConnectivityCheckerPro: `c9dfcb44fd2ed6a2ed2c7f18b84cac0159df5442`
  and `c8559e81df493d1f740d834d2a7908dcae4a541c`.
- DevAccelerationSystem: `feecdaa4757d20b2f4d22a6e2c7d33ed360086c6`,
  `bd43ad20cf259a137180fc97f520d07672d4c56f`, and the explicit follow-up
  snapshot `ebea7cb98fdd77556c8529eacc9f9d05b895faa2`.
- Hub implementation range: `878f4e6d3ddfea1647330a63c5dfe1bdfd02fe14..d1d4b831d7d1a3e69d2449691b929ecd9ea5fcd2`
  (ten commits, followed only by this outcome/handoff commit).

Imported gitlink ranges are exactly:

- AIRoot: `86e86d64975fedccb195e0a21ea6ff2c340b62a7..517493efeca711def648d18aecaf6882ed8de313`;
- ConnectivityCheckerPro: `8cc785f94be6558169f48b91840efe37b0466d90..c8559e81df493d1f740d834d2a7908dcae4a541c`;
- DevAccelerationSystem: `ca99e6932cbda965463753fc3c75c162b571c07b..ebea7cb98fdd77556c8529eacc9f9d05b895faa2`;
- MCP: `a72c79b675311583827ef5c9e966279555e64261..facc2081ab19d1fe4ab3adfd048e1385575aca70`.

The MCP range contains 21 commits and 165 changed paths (`+9355/-534`): eight
mixed, three runtime, two release, six documentation/evidence, and two
tests/tooling commits. This is a deliberate immutable release import, not a
claim that every changed runtime path was exercised in this Hub.

## Baseline Versus Current Topology

The task packet's reproduced 2026-09-02 baseline exited `1`: five stale
Connectivity router paths, five stale privacy/project paths, ten routing-audit
errors, root/AIRoot and root/Connectivity gitlink mismatches, stale consumer
paths that reduced pin proof to `2/7`, one stale context path, a false hard
failure at 203 lines below 10,000 bytes, and a blocked host analytics opt-out.
That snapshot used the active checkout state recorded by the packet. The
isolated execution base had since advanced to the exact bases above and its
seven consumer files were already on v0.3.70; the nested MCP gitlink was still
v0.3.63. These two observations are kept distinct.

`AIOutput/Registry/host_topology.yaml` is now the one machine-readable owner.
It declares five Git boundaries and exactly seven Unity projects:

| ID | Path | Role | Unity |
| --- | --- | --- | --- |
| `CCP-PUB` | `ConnectivityCheckerPro/CCP_PUB` | source | `2022.3.62f3` |
| `CCP-S21` | `ConnectivityCheckerPro/CCP_S21` | unsupported negative lane | `2021.3.45f2` |
| `CCP-S22` | `ConnectivityCheckerPro/CCP_S22` | consumer/context sample | `2022.3.62f3` |
| `CCP-S60` | `ConnectivityCheckerPro/CCP_S60` | consumer | `6000.0.58f2` |
| `CCP-S63` | `ConnectivityCheckerPro/CCP_S63` | consumer | `6000.3.23f1` |
| `DAS-SRC` | `DevAccelerationSystem/DevAccelerationSystem` | source | `2022.3.62f3` |
| `DAS-DEMO` | `DevAccelerationSystem/DevAccelerationSystem.DemoProject` | demo/context sample | `2022.3.62f3` |

`DevAccelerationSystem/DAS.LocalProject` remains optional and absent-safe.
The setup status only points to the owner; the routed-project compatibility
projection is validated against the seven records. Duplicate top-level YAML
keys, cross-boundary paths/targets, duplicate context samples, removed long
names (including Windows separators and child-adapter prose), and an inline
competing routed-project list now fail deterministically.

## Routing And Review Architecture

The current route is:

`native host -> compact Hub kernel -> nearest standalone-capable adapter -> at most one conditional XUUnity protocol -> focused proof -> zero or one outcome`

The root router and `WORKSPACE.md` mirror current `CCP_*` and prefixed DAS
paths. AIRoot exposes a host-agnostic compact post-implementation impact card;
CCP and DAS resolve that card and the Hub kernel only when mounted, while their
standalone fallbacks remain truthful. The DAS adapter's Hub-relative links were
corrected. No shared kernel was copied into a child.

The v4 review helper binds absolute, exact Git-root identity; a full base
commit; every sorted `BASE...HEAD` path; HEAD tree mode/type/OID; index
mode/OID; checkout bytes, executable mode, deletion, or symlink target; child
gitlink checkout HEAD; and committed parent/index/tree/child relations. It
rejects self-authored verdicts, omissions, traversal, duplicate paths,
ambiguous repositories, staged-pointer changes, and alternate committed index
blobs even when checkout bytes are unchanged. Review-helper tests: 15/15 PASS.

The independent reviewer found and caused correction of false negatives in
DAS routes, Stop ownership, deleted/malformed topology handling, route-source
aggregation, full committed-diff coverage, optional workspaces, Windows names,
inline lists, containment, strict JSON depth typing, removed CCP prose,
absolute repository identity, duplicate YAML sections, context denominators,
nested gitlink dirt, WORKSPACE mirrors, status-scope exclusions, and ordinary
HEAD/index binding. At implementation head `d1d4b831...` the reviewer reported
no remaining Hub-owned static implementation finding.

## Latest MCP Decision

Remote stable tags were re-read on 2026-09-05. Among 62 stable tags, the newest
was still annotated `v0.3.72`: tag object
`53e5cd99565cf1cc02899a1d4568cb4df58a59bf`, peeled commit
`facc2081ab19d1fe4ab3adfd048e1385575aca70`, package version `0.3.72`.
All 7/7 manifests and lockfiles use that exact tag and hash with JSON integer
depth `0` and source `git`.

Two immutable-upstream hygiene findings remain visible:

- `docs/reference/STATUS.md` lines 29-32 describe compiler-warning evidence as
  a v0.3.72 addition, while the changelog assigns that evidence to v0.3.70 and
  describes v0.3.72 as the Game View group/guarded click repair.
- The two imported test metadata files
  `XUUnityLightMcpGameViewGroupEditModeTests.cs.meta` and
  `XUUnityLightMcpUiClickRaycastIdentityPlayModeTests.cs.meta` contain trailing
  spaces on their three empty importer fields.

The tagged child was not rewritten. These findings require a later upstream
documentation/hygiene release; they are not functional or live-proof success.

## Post-Change Static Results

| Check | Result |
| --- | --- |
| `python3 -B scripts/validate-unity-harness.py` | PASS, full-static, 23 named checks, v0.3.72 consumers 7/7 |
| `python3 -B scripts/validate-unity-harness.py --stop` | PASS, bounded static subset, 19 named checks |
| Root Harness mutation/unit suite | 43/43 PASS |
| Stop-hook suite | 12/12 PASS |
| Frozen evaluator unit suite | 25/25 PASS |
| Frozen evaluator score | 10/10 PASS |
| Frozen evaluator adversarial self-test | 13/13 mutations rejected |
| AIRoot routing smoke | PASS through the aggregate |
| CCP router generator and privacy contract | PASS through the aggregate |
| DAS router generator | PASS through the aggregate |
| MCP host Python suite | PASS through the aggregate in an execution context permitting local loopback |
| Root refresh script syntax | PASS |
| Root refresh optional-absent/present/required-missing fixture | PASS in the root suite |

The clean isolated root does not contain ignored Unity-generated `.sln` and
`.csproj` inputs, so a direct root solution regeneration was not represented as
successful. The deterministic fixture proves optional DAS absence/presence and
required-input failure; the curated solution was updated without inventing
missing inputs.

Task-authored root/AIRoot/CCP/DAS diffs pass whitespace checks. The immutable
MCP import reports the six trailing-space lines in the two `.meta` files above;
that imported-tag advisory is retained rather than silently repaired.

## Context And Document Budgets

Lines are advisory; bytes are the hard limit.

| Scenario | Lines | Bytes / hard ceiling | Result |
| --- | ---: | ---: | --- |
| Hub root | 149 | 8,514 / 12,000 | PASS |
| AIRoot | 39 | 1,918 / 3,000 | PASS |
| CCP root | 211 | 9,620 / 10,000 | PASS with line warning (>200) |
| CCP consumer | 233 | 10,578 / 12,000 | PASS with line warning (>230) |
| DAS root | 280 | 12,710 / 14,000 | PASS |
| DAS demo | 313 | 14,089 / 16,000 | PASS |
| MCP standalone | 63 | 6,983 / 9,000 | PASS |
| MCP host-mounted | 251 | 17,415 / 21,000 | PASS |

| Document | Lines | Bytes / hard ceiling | Result |
| --- | ---: | ---: | --- |
| Hub kernel | 80 | 3,874 / 4,096 | PASS |
| Change delivery protocol | 246 | 13,936 / 24,576 | PASS |
| Compact impact review | 66 | 3,469 / 8,192 | PASS |

Only the two CCP line advisories remain. No byte ceiling fails.

## Evaluator And Stop Semantics

The frozen evaluator contains ten immutable policy fixtures: nine
`deterministic-contract` records and one `historical-replay` record. Its lanes
are three docs, two ordinary, three high-risk, and two release; observed fixture
verdicts are eight pass, one partial, and one intentionally blocked historical
release case. They are contract examples, not ten new live project runs.

The 13/13 rejected mutations cover unknown/missing fields, missing cases,
duplicate IDs, false release/device claims, stale tag/hash/pin, obsolete
generator, brittle standalone logic, calendar-only audit, and historical
relabel. Generic maintenance is therefore trigger-bound, not scheduled by date.

The Stop hook is static-only, bounded, recursive-safe, and fail-open only for
hook faults. Root, child, nested router, rename, deletion, untracked, and actual
gitlink-pointer changes trigger. Ordinary product/runtime, marketing,
generated, build, log, and release-evidence dirt no-ops. A real nested-repo
fixture proves ordinary MCP runtime dirt does not impersonate an AIRoot gitlink
change, while a nested router edit, checkout-ahead pointer, and staged pointer
do trigger.

## Privacy, Proof Ceiling, And Owner Actions

Repository privacy is PASS for 7/7 configured projects. The separate launch
preflight exits `1` only because host `EnableEditorAnalyticsV2` is not disabled.
The host preference was not modified. Unity was not launched.

The strongest current proof is static repository/host-tooling validation. It
does not establish Unity package resolution, compilation, EditMode, PlayMode,
exact-version matrix behavior, player builds, physical-device behavior, or
release readiness for the newly pinned MCP. Independent acceptance is REVISE,
not PASS, for that missing consumer boundary.

Required owner sequence:

1. Explicitly authorize or manually perform the Unity Editor analytics opt-out.
2. Re-run `python3 -B scripts/validate-unity-privacy.py --require-host-opt-out`
   and require launch authority PASS.
3. Resolve v0.3.72 in all seven configured projects; compile the supported
   source/consumer/demo projects with their recorded editors, and retain
   `CCP_S21` only as unsupported negative evidence.
4. Record exact package-resolution/compile results and any intentional failure;
   only then request a fresh readiness review.
5. Correct the upstream v0.3.72 STATUS summary and `.meta` whitespace in a
   later MCP release rather than mutating the existing tag.

## Dirty Partition And Rollback

Before the explicit cleanup follow-up, the user's active root checkout was at
`835e78c8c9800c274fdb87bf079c62969ccb6a98` with modified AIRoot and CCP
gitlinks. The seven pre-existing CCP Marketing changes were then preserved on
`codex/connectivity-checker-pro-post-approval-marketing` in commit
`81832ab7e6145a913a9a59b0ce4a8b2b292478eb`; they are not part of the Harness
gitlink scope. The isolated DAS `.editorconfig` mixed-line-ending difference
was likewise preserved, at the owner's request, in
`ebea7cb98fdd77556c8529eacc9f9d05b895faa2`. No dirty path was discarded or
silently folded into a different commit.

If Hub consumer proof finds an MCP regression, rollback should be a new set of
child commits: restore all seven consumer pins to their previous common
v0.3.70 commit `a6cf9c9da08b020d050820806dbf4d78a2ed38e5`, point the AIRoot nested gitlink
to that same commit, validate, then advance root child gitlinks. Do not rewrite
v0.3.72 or destructively reset user checkouts.

No application/package version, supported Unity floor, device promise, or
publication state changed incidentally. The only deliberate version change is
the explicitly authorized Unity MCP tooling pin to v0.3.72; `CCP_S21` remains
unsupported and the minimum supported line remains Unity 2022.3.
