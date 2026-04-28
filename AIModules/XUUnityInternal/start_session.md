# XUUnity Internal Start Session Overlay

## Purpose
Apply host-local routing rules for `AIFoxsterDevHub` after the public `xuunity` core is loaded.
Use this file only when the current task is inside this hub and the host-specific workspace map affects implementation, review, or validation.

## Load Order
1. Repo router at `Agents.md`
2. Public core at `AIRoot/Modules/XUUnity/`
3. This file
4. Narrow host-local knowledge files from `knowledge/` using the trigger rules below
5. Target project router
6. Target project memory

## Knowledge File Selection
- Load `knowledge/host_topology.md` when the task needs:
  - canonical source versus consumer selection
  - nested repo boundary awareness
  - sample-versus-package ownership decisions
  - workspace exception handling such as embedded consumer copies
- Load `knowledge/validation_paths.md` when the task needs:
  - validation target selection
  - engine-line-specific consumer choice
  - authoring-versus-validation workspace separation
  - commit-surface or release-proof interpretation for local-only workspaces
  - submodule commit or push ordering
- Load both files when a task spans package implementation plus consumer validation planning.

## Host Routing Rules
1. Resolve the concrete Unity project first.
2. Decide whether the target is:
   - a canonical package source project
   - a consumer validation workspace
   - a local-only reproduction workspace
3. If a change affects shared package behavior, implement it in the canonical source project first.
4. Use consumer workspaces primarily for repro, validation, and integration checks unless the consumer intentionally owns a divergent copy.
5. If the task spans package source and consumer workspaces, keep one implementation target and name the validation target explicitly.
6. If the task touches more than one submodule repo, call out commit boundaries instead of treating the hub as one commit surface.
7. If the task touches a nested repo or `AIRoot/` plus the hub root, commit and push the nested repo first, then land the hub-root pointer update as a separate commit.
8. If the user asks for `commit all changes` or `push all changes` at the hub root, traverse every dirty submodule repo first, then return to the hub root for pointer updates and any remaining host-owned commits.

## Canonical Source Rules
- `ConnectivityCheckerPro/ConnectivityCheckerPro_Publish/` is the canonical source for `ConnectivityCheckerPro`.
- `DevAccelerationSystem/DevAccelerationSystem/` is the canonical source for `DevAccelerationSystem`.
- Do not land durable shared package fixes in sample or demo projects unless the sample intentionally owns an embedded copy.

## Known Exception Rules
- `ConnectivityCheckerPro/ConnectivityCheckerPro_Sample2022/` contains its own embedded `Assets/ConnectivityCheckerPro` copy and is not auto-synced from `ConnectivityCheckerPro_Publish/`.
- `DevAccelerationSystem/DAS.LocalProject/` is a local validation workspace and is ignored by the nested repo's `.gitignore`.

## Validation Rules
- Use `AIFoxsterDevHub.sln` for package authoring and static code navigation at the hub level.
- Validate runtime or Unity integration changes in a representative consumer workspace, not only in the canonical package source.
- Do not assume one consumer workspace proves all supported engine versions.
- Treat local-only workspaces as useful evidence, but not as tracked release proof by default.

## Storage Rules
- Keep cross-project reusable host rules in `AIModules/XUUnityInternal/`.
- Keep project-only truth in `Assets/AIOutput/ProjectMemory/`.
- Keep mutable reports under `Assets/AIOutput/` or repo-level `AIOutput/`, not here.
