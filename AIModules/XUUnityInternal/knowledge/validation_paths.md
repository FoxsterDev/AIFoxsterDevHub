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
- Use `DAS.LocalProject/` only as optional local-only repro or validation when it exists; remember that the nested repo ignores it and it is not tracked release proof.

## Git Boundary Rules
- The hub root is one git repo, and it tracks `AIRoot/`, `ConnectivityCheckerPro/`, and `DevAccelerationSystem/` as separate submodule commit surfaces.
- If a task changes files in more than one submodule repo, review and commit them separately.
- If the user runs a host-level `commit all changes`, `push all changes`, or `publish all changes`, treat that as a cascade request across every dirty submodule repo plus the host repo.
- If a task changes a submodule and the hub root, push the submodule commit first, then commit and push the hub-root pointer update.
- If the host repo has both its own file edits and submodule pointer movement, split them into separate host commits by default.
- If the hub root has only submodule pointer movement, prefer a pointer-only hub commit instead of mixing it with unrelated root edits.
- Repo-level routers in the hub should not hide nested-repo commit boundaries.
