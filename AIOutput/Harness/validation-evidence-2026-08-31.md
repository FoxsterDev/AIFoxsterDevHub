# Unity Harness Validation Evidence — 2026-08-31

## Outcome

The native-host Unity Harness is static-green on the current recursive tree.
The update changes routing, deterministic validation, frozen evaluation, and
the Stop hook only. It does not change Unity runtime code, package contents,
consumer manifests/locks, serialized assets, app behavior, or release support.

Strongest new proof ceiling: `static`.

## Git denominator and dirty-work partition

Pre-fix denominator:

- Hub root: `4a546bb00780467ad4ed88f56c549297b6a2d6cb` (`main`)
- AIRoot: `376e4f9ca2f3682df9a655e2021f445f9716fea0` (`master`)
- ConnectivityCheckerPro:
  `0daaab807411f1e43660440b9c9ec3d5e9259655` (`master`)
- DevAccelerationSystem:
  `edb9079a12eea3f7a5c0ef384e05ff176ae62c9a` (`master`)
- nested XUUnity Light Unity MCP:
  `a72c79b675311583827ef5c9e966279555e64261` (`master`)

Implemented denominator:

- AIRoot commit: `86e86d64975fedccb195e0a21ea6ff2c340b62a7`
- Hub implementation commit:
  `7fd51d99d88b68b82193ced66513087682f8d0ff`
- ConnectivityCheckerPro, DevAccelerationSystem, and nested MCP remain at the
  pre-fix commits above.

Before the first edit, ConnectivityCheckerPro contained exactly nine modified
and two untracked owner-owned paths under `Marketing/**`, including two PNG
exports. They were not edited, generated, staged, deleted, or absorbed. No
other child or nested repository was dirty. Final root status intentionally
continues to show the dirty Connectivity gitlink because that owner work is
still present.

## Reproduced baseline

The required pre-fix commands produced:

- host privacy preflight: pass, 7/7 projects;
- frozen scorer: pass, 8/8;
- old scorer self-test: baseline 8/8 and the one intentional mutation rejected
  as 7/8;
- AIRoot routing audit: fail with exactly two semantic defects—an unrecognized
  unsupported legacy kind and obsolete literal `Standalone:` matching;
- aggregate Harness gate: fail with 24 reported entries, comprising the
  routing-audit failure, a nonexistent MCP router-generator command, stale MCP
  package-version ownership, and three stale pin/hash assertions for each of
  seven consumers;
- `git diff --check`: pass.

The failures were classified as stale Hub validator/evidence plus AIRoot-owned
routing contract drift. No package, consumer, Unity, device, or owner-marketing
defect was inferred from them.

## Current MCP tooling and version contract

The root gate now derives one current contract from the checked-in root and
AIRoot gitlinks, the nested package metadata, the exact annotated tag, and the
seven consumer manifests/locks:

- release tag: `v0.3.63`;
- annotated tag object:
  `2923acfa594e70a6b4081b4e924274c2be81d1c0`;
- peeled commit and Unity lock hash:
  `a72c79b675311583827ef5c9e966279555e64261`;
- package version: `0.3.63`;
- consumer result: 7/7 exact URL, `source=git`, `depth=0`, and peeled hash.

The gate owns no frozen tag, version, or hash constant. A changed gitlink,
non-exact or lightweight release tag, mismatched package version, stale URL,
wrong lock hash, or unexpected checkout is rejected. The retired
`scripts/tools/sync_agent_routers.py` command was not restored; complete child
history shows it was never tracked. The selected current child-owned static
release command is
`scripts/testing/check_release_version_consistency.py`. Standalone router
semantics are validated by AIRoot against the MCP-owned `## Mode Detection`
section.

## Frozen eval and adversarial coverage

- active frozen cases: 10/10 pass;
- tracked scorer tests: 24/24 pass;
- built-in scorer mutations: 12/12 rejected;
- current-tree contract/meta mutation tests: 7/7 pass;
- scorer size: 299 lines.

Expectations and observations are separate strict-schema files. The suite
rejects duplicate JSON keys/IDs, unknown or missing fields/IDs, wrong types,
case/consumer deletion, expectation-floor changes, false release/device claims,
stale tooling relations, obsolete validation entrypoints, brittle standalone
matching, and false support relabeling. `UH-08` remains pinned as blocked
`historical-replay` evidence; it cannot be deleted, passed, or relabeled as a
new live observation.

## Routing and Stop hook

AIRoot now recognizes `unity_unsupported_legacy_compatibility_lane` as a
public-safe project kind only when its router explicitly states that its
evidence does not prove advertised support. Both public generators, template
guidance, audit logic, and smoke fixtures share that contract. MCP standalone
detection parses a nonempty standalone-mode declaration under
`## Mode Detection`; it does not require obsolete wording.

The Stop hook remains static and owner-trusted. It no-ops for ordinary product
and `ConnectivityCheckerPro/Marketing/**` changes, scopes root/child/untracked/
rename routing surfaces, prevents recursion through `stop_hook_active`, bounds
failure output to 1,800 characters, and fails open with a visible warning on
internal faults. Its tracked suite passes 7/7. Internal Python invocations use
no-bytecode mode so the hook does not leave cache files. Owner trust through
native Codex `/hooks` remains an explicit action.

## Current context composition

The aggregate gate recomputes these values from the actual tree on every run;
no stored self-reported count is accepted:

| Start context | Files | Lines | Bytes | Budget (lines/bytes) |
| --- | ---: | ---: | ---: | ---: |
| Hub root | 2 | 198 | 10,263 | 220 / 12,000 |
| AIRoot | 1 | 32 | 1,417 | 50 / 3,000 |
| Connectivity root | 3 | 174 | 8,215 | 200 / 10,000 |
| Connectivity Sample2022 consumer | 4 | 196 | 9,199 | 230 / 12,000 |
| DevAccelerationSystem root | 2 | 267 | 12,029 | 300 / 14,000 |
| DevAccelerationSystem demo | 3 | 300 | 13,408 | 340 / 16,000 |
| nested MCP standalone | 1 | 63 | 6,983 | 90 / 9,000 |
| nested MCP host-mounted | 4 | 293 | 18,663 | 330 / 21,000 |

The named pre-Harness parent commit
`d4196f9da6cfe94d71fbc10fe59ad084d0eb9ed2` contains none of the root router,
kernel, scorer, static gate, or Stop-hook owners. It therefore does not define
a comparable default-loaded composition. No historical reduction percentage
is claimed.

## Final validation

All commands exited zero:

- `python3 scripts/validate-unity-privacy.py --require-host-opt-out` — 7/7;
- scorer unittest discovery — 24/24;
- scorer — 10/10;
- scorer self-test — 12/12 mutations rejected;
- Stop-hook unittest discovery — 7/7;
- current contract/meta tests — 7/7;
- AIRoot routing audit and setup smoke;
- Connectivity router generation check and 5/5 privacy identity check;
- DevAccelerationSystem routing check — 3 routers and 2 aliases;
- MCP release version consistency, docs freshness, and public safety checks;
- MCP release-versioning tests — 15/15;
- aggregate `scripts/validate-unity-harness.py`;
- root and AIRoot `git diff --check`.

The aggregate result is green with 25 required files, strict JSON, all child
routes above, exact current-tree MCP `7/7`, and eight context scenarios.

## Proof ceilings, decision, rollback, and owner actions

No Unity Editor was launched. No package self-test, consumer resolve/compile,
EditMode, PlayMode, platform build, simulator, physical-device, publication,
or release run was performed. Historical 2026-08-29 live evidence remains a
historical record and was not promoted to current proof. Current routing warns
that the Unity 6000.3 consumer must be proved only with its exact tracked editor;
this static update makes no new claim for it.

Package/app/version decision: retain the current MCP package `0.3.63` and every
product package/app version unchanged. No repin, runtime change, support-floor
change, app-version change, or release promise is justified by this Harness
update.

Rollback is repository-partitioned: revert the Hub implementation/evidence
commits, then revert AIRoot `86e86d6...` only if the public routing semantics
must also be withdrawn. Do not alter or clean Connectivity marketing work, and
do not move the nested MCP, Connectivity, or DevAccelerationSystem gitlinks.

Remaining owner actions are limited to trusting the Stop hook through `/hooks`
if desired and publishing the already partitioned AIRoot commit before the Hub
commits if these local commits are pushed. Stronger Unity/device/release proof
should be run only for a future change that actually requires it.
