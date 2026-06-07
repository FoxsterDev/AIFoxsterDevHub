<!-- Managed by AIRoot/scripts/init_ai_repo.sh -->
# Monorepo Agent Router

## Purpose
This file is the repo-level routing layer for the host.
Keep it minimal.
Use it to select shared prompt families, define load order, and route project-local overrides.

## Host Context
- Repo: `AIFoxsterDevHub`
- Topology: `monorepo`
- Shared public core: `AIRoot/Modules/XUUnity/`

## Load Order
1. This repo-level `Agents.md`
2. Shared protocol modules from `AIRoot/Modules/`, with `xuunity` loading public core from `AIRoot/Modules/XUUnity/`
3. Optional monorepo-internal overlay from `AIModules/XUUnityInternal/` when the host uses it
4. Other host-local prompt families from `AIModules/` when the selected protocol is host-local
5. Project-level `Agents.md`
6. Project-local memory from `<Project>/Assets/AIOutput/ProjectMemory/`
7. Project-local previous AI outputs from `<Project>/Assets/AIOutput/` when they are relevant

## Routing Table
- Use `xuunity` as the default protocol for Unity implementation, review, refactoring, product-facing implementation explanation, SDK work, native work, runtime safety, startup, performance, and compliance.
- Use host-local protocol families only when the host intentionally attaches them under `AIModules/`.
- For tasks under `AIRoot/Operations/XUUnityLightUnityMcp/`, route to `AIRoot/Operations/XUUnityLightUnityMcp/Agents.md` before project-specific work. This child project is a public MCP tooling repo, not a host Unity consumer project.
- For tasks under `AIRoot/Operations/XUUnityLightUnityMcp/docs/clients/`, route through the MCP project router first, then the local client-docs router in that folder.

## Fast Shortcuts
- `xuunity fix this bug`
- `xuunity refactor this code`
- `xuunity review the git change`
- `xuunity sdk review this integration`
- `xuunity native review this bridge`
- `xuunity feature plan this flow`
- `xuunity product explain this feature`
- `xuunity product health this project`
- `xuunity project memory freshness this project`

## Prompt Family Map
- `xuunity` -> public core `AIRoot/Modules/XUUnity/` plus internal overlay `AIModules/XUUnityInternal/` when the host uses it
- `xuunity-light-unity-mcp` -> public tooling project `AIRoot/Operations/XUUnityLightUnityMcp/` plus its project router and docs/agents guidance
- optional host-local protocol families -> `AIModules/` when the host attaches them

## Project Memory Override Rule
- Project-specific memory in `<Project>/Assets/AIOutput/ProjectMemory/` overrides shared prompts when there is a conflict.
- Do not move project-specific constraints into shared prompts.
- Historical reports in `<Project>/Assets/AIOutput/` are opt-in context and should be loaded only when relevant.

## AI Output Storage Rule
- Durable project-local guidance belongs in `<Project>/Assets/AIOutput/ProjectMemory/`.
- Project reports and drafts belong in `<Project>/Assets/AIOutput/`.
- Host-level setup, handoff, registry, and reports belong in `AIOutput/`.
- Public reusable `xuunity` guidance belongs in `AIRoot/Modules/XUUnity/`.
- Monorepo-internal shared `xuunity` guidance belongs in `AIModules/XUUnityInternal/`.

## Sensitive Data Protocol
- Treat project-specific intellectual property, internal architecture, business logic, and credentials as confidential by default.
- Never promote project-specific confidential details into shared prompts.
- Report sensitive config evidence using structure and redacted values only.
