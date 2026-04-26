# AIFoxsterDevHub Workspace

`AIFoxsterDevHub.sln` is a curated hub solution for editing the canonical source of the Unity packages in this workspace without pulling in hundreds of generated `Unity.*` projects.

Use the hub solution for package authoring:

- `ConnectivityCheckerPro/ConnectivityCheckerPro_Publish`
- `DevAccelerationSystem/DevAccelerationSystem`

These are the canonical sources. Changes there apply to the consumer workspaces that already use local `file:` package dependencies:

- `ConnectivityCheckerPro_Sample2021`
- `ConnectivityCheckerPro_Sample6000`
- `ConnectivityCheckerPro_Sample6000_3_2f1`
- `DevAccelerationSystem.DemoProject`
- `DAS.LocalProject`

`ConnectivityCheckerPro_Sample2022` is the exception. It currently contains its own embedded `Assets/ConnectivityCheckerPro` copy and is not auto-synced from `ConnectivityCheckerPro_Publish`.

Recommended workflow:

1. Open `AIFoxsterDevHub.sln` for package code, tests, manifests, and child workspace entry points.
2. Edit canonical package code in `ConnectivityCheckerPro_Publish` or `DevAccelerationSystem`.
3. Open a child Unity workspace only when you need to run scenes, package validation, or Unity-specific compilation in that consumer project.
4. Run `scripts/refresh-aifoxster-hub.sh` if you add/remove authored `asmdef` projects and want the root solution refreshed.
