# AIFoxsterDevHub

Hub repository for the FoxsterDev AI workspace.

This repo is intentionally thin:

- `AIRoot` is included as a git submodule.
- `ConnectivityCheckerPro` is included as a git submodule.
- `DevAccelerationSystem` is included as a git submodule.
- `AIFoxsterDevHub.sln` is the curated root solution for package authoring and workspace navigation.

## Clone

```bash
git clone --recurse-submodules https://github.com/FoxsterDev/AIFoxsterDevHub.git
```

If you already cloned without submodules:

```bash
git submodule update --init --recursive
```

## Workspace

- Open `AIFoxsterDevHub.sln` for the curated multi-repo workspace.
- See `WORKSPACE.md` for the canonical edit flow and child Unity workspace entry points.
