# Unity Harness Validation Evidence — 2026-08-29

## Version decision

Both authoritative upstream remotes expose `v0.3.62` as the newest
version-sorted stable tag. It is annotated:

- tag object: `b1a559337a04d403498fdf836d53d84b62cf5789`;
- peeled commit and Unity package lock hash:
  `7b8b139d8bdd5d226e5e6703b586e1ca9f16f442`;
- package version: `0.3.62`;
- local standalone Harness-only descendant:
  `d5a38b9dc416fd92570c17d7e38e1d2090583ee7`.

All seven tracked consumers pin the tag URL and lock the peeled hash. No old
`v0.3.20` or `v0.3.43` consumer pin remains.

## Privacy and clean-import preflight

- Seven Unity roots were resolved from `ProjectSettings/ProjectVersion.txt`.
- Before first live use, none had a `Library/` directory; every executed slice
  therefore performed a clean regeneration.
- All seven project settings pass codename, application identifier, empty
  Cloud identity, disabled service startup, and full legacy-name scans.
- `EnableEditorAnalytics` and `EnableEditorAnalyticsV2` are both `0` after the
  final Unity invocation. One Editor launch rewrote V2 to `1`; the fail-closed
  host preflight detected it and both keys were restored to `0`.
- Unity-created untracked `.meta` noise outside the requested change was
  removed after exact path verification and was not committed.

## MCP package-source proof

- Router generator: 2/2 exact `AGENTS.md` outputs current; legacy mixed-case
  routers deleted.
- Host Python suite: 966/966 effective passes; 14 expected Windows/platform
  skips. A sandbox-only loopback bind denial was rerun outside the sandbox and
  passed.
- Release/version/docs/public-safety checks: green; public site live check:
  green. The upstream annotated tag is not cryptographically signed.
- Fresh temporary version matrix:
  - Unity `2022.3.67f2`: EditMode 91/91, PlayMode 5/5, interactive acceptance
    9/9, refresh 2/2, compile 2/2, StandaloneOSX batch compile green;
  - Unity `6000.0.58f2`: the same steps and counts green.
- Temporary matrix projects were recreated without pre-existing `Library/`
  and removed after success. No Unity Editor process remained.

## Hub consumer proof

| Consumer | Exact editor | MCP resolve | Compile | Truthful result |
| --- | --- | --- | --- | --- |
| CCP-PUB | 2022.3.62f3 | pass | pass | compiled |
| CCP-S21 | 2021.3.45f2 | pass | pass | compiled; pre-existing asmdef ownership warning only |
| CCP-S22 | 2022.3.62f3 | pass | pass | compiled after obsolete local-SDK dependency removal on 2026-08-30 |
| CCP-S60 | 6000.0.58f2 | pass | pass | compiled |
| CCP-S63 | 6000.3.3f1 | structural lock only | not run | exact editor unavailable |
| DAS-SRC | 2022.3.62f3 | pass | pass | compiled |
| DAS-DEMO | 2022.3.62f3 | pass | pass | compiled |

No product/package runtime was modified to manufacture a pilot result.

## Harness/static proof

- Frozen scorer: 8/8 mandatory cases pass; its built-in intentional release
  failure is rejected 7/8 as designed.
- Root static gate: all required files, JSON, privacy, routing, generators,
  exact router case, and seven MCP pins/locks pass.
- Scoped Stop hook unit tests: 4/4 pass; ordinary product paths no-op.
- AIRoot setup smoke: pass. XUUnity public protocol tests: 174/174. Model
  fitness: 178 pass with 2 expected skips.
- Connectivity standalone generator/privacy gates: 6/6 and 5/5. DAS
  repository validation: 3/3 packages.

## Proof ceilings and remaining owner actions

This refresh is implementation-green for static Harness routing and for the
listed package-source/consumer slices, but not release-green for the entire
Hub. CCP-S63 retains the explicit ceiling above. Native permission,
hardware, store, Addressables, migration, and physical-device claims were not
in the changed runtime surface and were not manufactured.

The repository Stop hook remains untrusted until the owner approves it through
native Codex `/hooks`. Global Editor Analytics should remain a preflight because
Unity ID/editor synchronization can rewrite the V2 preference.
