# XUUnity Internal Overlay

## Purpose
This directory is the host-local `xuunity` overlay for `AIFoxsterDevHub`.
Load it after `AIRoot/Modules/XUUnity/` and before project-local memory when the task needs hub-specific routing, workspace selection, validation targeting, or nested-repo awareness.

## Entry Point
- `start_session.md`

## Files
- `knowledge/host_topology.md`
- `knowledge/validation_paths.md`
- `knowledge/runtime_safety_rules.md`

## Use This Overlay For
- choosing between canonical package source projects and consumer validation projects
- routing work across the hub solution and nested Unity workspaces
- remembering nested git boundaries inside the hub
- handling known host-specific exceptions such as embedded sample copies
- applying host-local runtime safety guidance for async teardown and platform-target test seams when those patterns recur across projects

## Do Not Use This Overlay For
- project-only facts that belong in `Assets/AIOutput/ProjectMemory/`
- public-safe generic Unity rules that belong in `AIRoot/Modules/XUUnity/`
- mutable reports, incident logs, or temporary notes
