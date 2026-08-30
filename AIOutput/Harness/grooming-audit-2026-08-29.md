# Unity Harness Grooming Audit — 2026-08-29

Scope denominator: root Hub, AIRoot, three root gitlinks, the nested MCP gitlink,
14 tracked routers, setup generators, XUUnity protocol surfaces, host overlays,
status/report owners, hooks, package manifests, exact Unity versions, and seven
active Unity project roots.

## Baseline identity

- Root: `4e7d0636a4659d024dbfb1b40de8f73058ba587a`, branch `main`.
- Root gitlinks: AIRoot `00252ca6`, Connectivity `3ec3f673`, DAS `cd970c6a`.
- Checked out before changes: AIRoot `dcc039dd`, Connectivity `3ec3f673`, DAS
  `d3b9b25c`, nested MCP `a794216e`.
- AIRoot and DAS gitlink drift predated this work. All three child worktrees and
  the nested MCP worktree were clean. Connectivity and DAS LFS fsck were green.

## Classification

### Active

- Native Codex `AGENTS.md` discovery and repository-local `.codex` hook layer.
- AIRoot setup generators and routing audit, after canonical-case correction.
- Public `AIRoot/Modules/XUUnity/` role, skill, task, risk, validation, test, and
  release guidance.
- Connectivity package source and five version consumers.
- DAS package source and tracked demo consumer.
- Project-local `Assets/AIOutput/ProjectMemory/` and current status owners.
- Existing Unity version-matrix, package self-test, compilation, EditMode,
  PlayMode, platform-build, and device resources when available.

### Consolidate

- Generated `Agents.md` routers into exact `AGENTS.md`; keep only thin legacy
  compatibility for a demonstrably supported non-Codex host.
- Repeated project routers into a compact satellite adapter plus local facts.
- Host topology/setup status into dated, path-relative truthful evidence.
- Validation wording into the four lanes and common proof-ceiling vocabulary.
- Root and satellite bootstrap checks into deterministic generators/validators.

### Archive

- `AIRoot/Operations/XUUnityAiCliOrchestrator/` as historical/non-runtime.
- Stale reports and old absolute-path status as historical evidence after a
  current owner record exists.
- Optional `DAS.LocalProject` claims until that ignored workspace is explicitly
  supplied and validated.
- Divergent embedded Connectivity 2022 package copy as a baseline exception,
  not canonical release evidence.

### Delete only after replacement/reference proof

- Legacy DAS `unity_compilation_runner_mac.sh` after its callers use the native
  compile lane.
- Connectivity `SYNC_TO_PUBLISH.sh` after publishing ownership is replaced.
- Unreferenced review artifacts identified in AIRoot only after owner review.

No deletion is performed merely because a file looks old. The current refresh
prefers archive/deprecation where ownership or replacement is uncertain.

## Boundaries and known baselines

- Connectivity exact editors: 2021.3.45f2, 2022.3.62f3, 6000.0.58f2, and
  6000.3.3f1. The last is not installed; 6000.3.21f1 is not an exact substitute.
- Connectivity Sample2022 has an unavailable absolute Aghanim tarball and a
  divergent embedded package copy; it cannot be called release-green.
- DAS source and demo use 2022.3.62f3; static package validation was green.
- Build targets are not established by tracked files alone and must be recorded
  at execution time.
- XUUnity Light Unity MCP is active as an independent standalone-capable
  tooling satellite. Owner direction changed during the refresh: its canonical
  router/generator and consumers are updated to stable `v0.3.62`; its existing
  execution/runtime architecture is retained without a new broker.

Machine-readable audit aggregates used for synthesis:

- `/tmp/unified-harness-audit-airroot-mcp.json`
- `/tmp/unified-harness-audit-connectivity.json`
- `/tmp/unified-harness-audit-devaccel.json`

These are local evidence aggregates, not tracked runtime state.
