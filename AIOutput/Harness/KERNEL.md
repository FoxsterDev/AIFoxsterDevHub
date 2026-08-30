# Unity Unified Harness Kernel

Status: active
Owner: AIFoxsterDevHub
Updated: 2026-08-29

## Runtime shape

Use the native Codex host. This repository adds routing and proof policy, not an
agent runtime or workflow engine:

`native host -> this compact kernel -> satellite adapter -> XUUnity when needed -> focused proof -> zero or one outcome record`

Load only the layers required by the current path:

1. exact `AGENTS.md` files from repository root to the working directory;
2. this kernel when a Hub checkout is available;
3. the nearest satellite adapter;
4. `AIRoot/Modules/XUUnity/` only for Unity implementation or validation work;
5. project memory and prior reports only when directly relevant.

`AIModules/XUUnityInternal/` is an optional Hub overlay. A satellite must remain
truthful and usable when the Hub, AIRoot, or that overlay is absent.

The nested XUUnity Light Unity MCP repository is the active Unity execution
satellite. Consumers and the AIRoot gitlink use the same verified stable
release. Its existing launcher, smoke tests, and version matrix are reused;
the Harness does not wrap them in a replacement broker or process hierarchy.

## Active boundaries

- `AIRoot/`: shared XUUnity protocol and repository setup generators.
- `ConnectivityCheckerPro/`: one package source plus five versioned consumers.
- `DevAccelerationSystem/`: package source plus tracked demo consumer.
- `AIRoot/Operations/XUUnityLightUnityMcp/`: independently versioned public MCP
  tooling satellite with its own exact router and standalone fallback.
- `AIModules/`: optional host-local overlay; never a satellite dependency.

`AIRoot/Operations/XUUnityAiCliOrchestrator/` is historical tooling and is not a
Harness runtime. The nested MCP project is independently active; host routing
augments it without taking over its runtime, sessions, or release ownership.

## Privacy preflight

Before any Unity launch in this Hub, run:

```sh
python3 scripts/validate-unity-privacy.py --require-host-opt-out
```

The command must prove neutral Unity-visible identities, disabled Editor and
project Analytics, empty Unity Cloud identity, disabled Unity services, and no
explicit Analytics/Collab packages. A red result forbids Unity launch but does
not block docs or ordinary non-Unity repository work.

For a requested clean regeneration, delete only the target Unity project's
`Library/` after resolving the exact project root from
`ProjectSettings/ProjectVersion.txt`; never broaden cleanup to `Assets/`,
`Packages/`, `ProjectSettings/`, or a satellite root.

## Lanes

| Lane | Typical change | Minimum truthful proof |
| --- | --- | --- |
| docs | prose, router wording, frozen data | diff review plus the narrow static validator |
| ordinary | contained C# or package change | exact-version resolve/compile and the smallest relevant EditMode or PlayMode set |
| high-risk | serialized assets, lifecycle, save/migration, native integration | ordinary proof plus reopen/reload or fixture/migration/device evidence matching the risk |
| release | release intent, package publication, support claim | source proof, consumer proof, required version/build-target matrix, clean release inputs, and no unresolved mandatory failure |

Escalate the lane when evidence shows higher risk. Never lower it to match the
available machine.

## Unity proof routing

- Package source and consumer validation are distinct. A green package test is
  not consumer proof; a consumer compile is not package self-test proof.
- Record exact Unity editor version and active build target. A nearby installed
  patch version does not prove the requested version.
- `asmdef` or C# changes require a real Unity compile ceiling. Text search or
  IDE compilation alone is below that ceiling.
- EditMode proves editor/test-domain behavior. PlayMode proves runtime behavior.
  Neither substitutes for the other.
- Scene, prefab, ScriptableObject, and other serialized changes require YAML or
  Inspector review plus reopen/reload proof appropriate to the change. Never
  normalize or rewrite unrelated serialized content.
- Domain reload, editor startup/shutdown, delayed callbacks, and play-mode
  transition claims require the matching lifecycle transition.
- Save/data migrations require versioned fixtures, backup/rollback behavior,
  idempotence, corrupt/partial-data handling, and compatibility evidence.
- Addressables and content catalogs require catalog/profile/build/load proof;
  an asset-database compile is insufficient.
- Native SDK and permission changes require platform build evidence. Runtime,
  permission-prompt, sensor, store, or hardware claims remain device-only until
  exercised on a real supported device.

## Journey Zero and proof ceilings

Journey Zero is the smallest path that can falsify the change before broader
work. Start with static/privacy/resolve evidence, then compile, then the narrow
test or lifecycle slice. Broaden only after the previous step is green.

Report the strongest completed proof and its ceiling. Valid ceiling labels are:

- `static`
- `resolved`
- `compiled`
- `editmode`
- `playmode`
- `serialized-reopen`
- `platform-build`
- `physical-device`
- `release`

Do not translate missing Unity versions, unavailable build modules, blocked
licenses, absent devices, or baseline failures into a passing claim.

## Outcome discipline

Most turns produce no durable outcome record. Create at most one when a
decision, release block, migration result, or reusable failure boundary must be
handed off. It must include lane, source/consumer boundary, exact version and
target, commands/evidence, strongest ceiling, known baseline failures, and next
owner action. Do not create event streams, task databases, queues, or session
state for this kernel.

## Stop gate

The repository Stop hook is scoped to Harness-owned routing/configuration
changes. It runs only static router, privacy-contract, and frozen-eval checks;
it never launches Unity or product regressions and no-ops for ordinary product
development. Hook trust remains an explicit owner action through `/hooks`.
