# Host Topology

## Purpose
Describe the reusable workspace map for `AIFoxsterDevHub`.
Use this file when project selection, ownership, or canonical-source routing matters.

## Hub Shape
- Repo root solution: `AIFoxsterDevHub.sln`
- Public protocol core: `AIRoot/Modules/XUUnity/`
- Host-local overlay: `AIModules/XUUnityInternal/`
- Three nested git repos or tracked submodules:
  - `AIRoot/`
  - `ConnectivityCheckerPro/`
  - `DevAccelerationSystem/`
- Public tooling submodule nested under `AIRoot`:
  - `AIRoot/Operations/XUUnityLightUnityMcp/`

## ConnectivityCheckerPro Map
- Canonical source project: `ConnectivityCheckerPro/ConnectivityCheckerPro_Publish/`
- Consumer validation projects:
  - `ConnectivityCheckerPro/ConnectivityCheckerPro_Sample2021/`
  - `ConnectivityCheckerPro/ConnectivityCheckerPro_Sample6000/`
  - `ConnectivityCheckerPro/ConnectivityCheckerPro_Sample6000_3_2f1/`
- Embedded-copy exception:
  - `ConnectivityCheckerPro/ConnectivityCheckerPro_Sample2022/`

## DevAccelerationSystem Map
- Canonical source project: `DevAccelerationSystem/DevAccelerationSystem/`
- Consumer validation projects:
  - `DevAccelerationSystem/DevAccelerationSystem.DemoProject/`
- Optional local-only validation project:
  - `DevAccelerationSystem/DAS.LocalProject/`

## XUUnityLightUnityMcp Map
- Public MCP tooling project: `AIRoot/Operations/XUUnityLightUnityMcp/`
- Project router: `AIRoot/Operations/XUUnityLightUnityMcp/Agents.md`
- Unity package source: `AIRoot/Operations/XUUnityLightUnityMcp/packages/com.xuunity.light-mcp/`
- Client docs route: `AIRoot/Operations/XUUnityLightUnityMcp/docs/clients/`
- Client docs router: `AIRoot/Operations/XUUnityLightUnityMcp/docs/clients/Agents.md`

## Selection Rules
- Package code changes belong in canonical source projects.
- Consumer projects are the default validation target for integration behavior.
- Optional local-only projects are useful for repro and fast checks, but they are not required to exist and are not tracked release proof by default.
- Sample or demo projects should not become the durable source of shared package truth unless they intentionally own divergent code.
- When a task is phrased around a sample-only failure, verify whether the bug belongs to the package source or to that sample's local setup before patching.
- Tasks targeting `AIRoot/Operations/XUUnityLightUnityMcp/` should stay in that nested tooling repo unless the user explicitly asks to modify a consumer Unity project.
