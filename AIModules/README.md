# Host-Local AI Modules

## Purpose
This directory holds host-local AI overlays for `AIFoxsterDevHub`.
Load these modules only after the public `AIRoot` core when the task needs hub-specific routing or reusable internal context.

## Active Modules
- `XUUnityInternal/` -> monorepo-internal overlay for `xuunity`

## Rules
- Keep public-safe reusable guidance in `AIRoot/`.
- Keep hub-specific reusable guidance in `AIModules/`.
- Keep project-only truth in each project's `Assets/AIOutput/ProjectMemory/`.
- Do not store mutable reports or one-off investigations in this tree.
