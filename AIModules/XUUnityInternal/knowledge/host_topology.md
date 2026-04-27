# Host Topology

## Purpose
Describe the reusable workspace map for `AIFoxsterDevHub`.
Use this file when project selection, ownership, or canonical-source routing matters.

## Hub Shape
- Repo root solution: `AIFoxsterDevHub.sln`
- Public protocol core: `AIRoot/Modules/XUUnity/`
- Host-local overlay: `AIModules/XUUnityInternal/`
- Two nested git repos:
  - `ConnectivityCheckerPro/`
  - `DevAccelerationSystem/`

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
  - `DevAccelerationSystem/DAS.LocalProject/`

## Selection Rules
- Package code changes belong in canonical source projects.
- Consumer projects are the default validation target for integration behavior.
- Sample or demo projects should not become the durable source of shared package truth unless they intentionally own divergent code.
- When a task is phrased around a sample-only failure, verify whether the bug belongs to the package source or to that sample's local setup before patching.
