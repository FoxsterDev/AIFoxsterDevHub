# Validation Paths

## Purpose
Capture host-level validation routing for `AIFoxsterDevHub`.
Use this file when deciding where code should be edited and where the result should be verified.

## Authoring Path
- Start package authoring from `AIFoxsterDevHub.sln`.
- Edit shared package code in:
  - `ConnectivityCheckerPro/ConnectivityCheckerPro_Publish/`
  - `DevAccelerationSystem/DevAccelerationSystem/`

## Validation Path
- Validate Unity runtime or package integration behavior in a representative consumer workspace.
- Prefer at least one consumer that matches the engine line affected by the change.
- If a bug is version-specific, choose the consumer project on that engine branch instead of a generic sample.

## ConnectivityCheckerPro Guidance
- Shared package fixes start in `ConnectivityCheckerPro_Publish/`.
- Use `ConnectivityCheckerPro_Sample2021/` for older-engine validation.
- Use one of the Unity 6000 samples for current-line validation.
- Use `ConnectivityCheckerPro_Sample2022/` only when the issue depends on its embedded copy or local sample setup.

## DevAccelerationSystem Guidance
- Shared package fixes start in `DevAccelerationSystem/`.
- Use `DevAccelerationSystem.DemoProject/` for tracked consumer validation.
- Use `DAS.LocalProject/` for local repro or local validation when helpful, but remember that the nested repo ignores it.

## Git Boundary Rules
- The hub root is one git repo, but `ConnectivityCheckerPro/` and `DevAccelerationSystem/` are nested git repos with their own status and commits.
- If a task changes files in both nested repos, review and commit them separately.
- Repo-level routers in the hub should not hide nested-repo commit boundaries.
