# XUUnity System Health Review

## Scope
- Host: `AIFoxsterDevHub`
- Protocol: `xuunity system health review`
- Date: `2026-04-26`
- Review target: routing system, shared prompt layers, internal overlay, project-memory wiring, and evidence pipeline

## High-severity conflicts
- None found.

## Medium-severity findings
- Knowledge extraction regression evidence is missing.
  - The health-review protocol explicitly asks for a latest authoritative extraction baseline or recent regression run when available.
  - No machine-readable extraction regression summary or baseline artifact was found under repo-level `AIOutput/`.
  - Result: extraction pipeline health is currently unverifiable from the host evidence layer.

## Low-severity findings
- `AIRoot/backup_Apr_12_2026/Agents.md` remains present as legacy backup ballast.
  - It is outside the active routing path, so this is not a behavioral conflict.
  - It still increases search noise and can mislead manual archaeology if mistaken for an active router.
- The system is currently in a partially staged rollout state across four git surfaces.
  - Hub root, `AIRoot`, `ConnectivityCheckerPro`, and `DevAccelerationSystem` all contain uncommitted routing changes.
  - This is not a design contradiction, but it is a deployment consistency risk until committed in each owning repo.

## Redundant files or sections
- No active duplicate routing contract was found between:
  - root `Agents.md`
  - nested workspace routers
  - project routers
- The `Fast Shortcuts` block is consistent between:
  - root `Agents.md`
  - `AIRoot/scripts/init_ai_repo.sh`
  - `AIRoot/Templates/REPO_AGENTS_ROUTER_TEMPLATE.md`
- The backup router under `AIRoot/backup_Apr_12_2026/` is the main remaining redundant artifact in visible search space.

## Missing files or weak layers
- Missing repo-level extraction regression evidence under `AIOutput/Reports/`.
- Canonical source memory still lacks dedicated `known_issues.md` files if recurring issue patterns need durable capture later.

## Knowledge extraction regression status
- Status: `missing evidence`
- Findings:
  - No latest machine-readable extraction baseline was found under repo-level `AIOutput/`.
  - No recent extraction regression run summary was found.
  - Extraction pipeline health therefore cannot be upgraded beyond design intent and file presence.

## Knowledge reachability status
- Public core knowledge:
  - No immediate unreachable active-core issue was found in the reviewed host routing layer.
- Internal overlay knowledge:
  - `host_topology.md` and `validation_paths.md` are conceptually relevant, correctly placed, and now have explicit selection rules in `AIModules/XUUnityInternal/start_session.md`.
- Result:
  - Reachability is `strong` for the current internal overlay knowledge layer.

## Public core versus internal overlay boundary status
- Status: `healthy`
- Evidence:
  - Public reusable guidance stays in `AIRoot/Modules/XUUnity/`.
  - Monorepo-specific reusable guidance is placed in `AIModules/XUUnityInternal/`.
  - Project-only truth is placed in `Assets/AIOutput/ProjectMemory/`.
- No active rule was found that collapses public core and internal overlay into one undifferentiated shared layer.

## Storage consistency status
- Status: `strong`
- Evidence:
  - Repo router stores project-local truth in `<Project>/Assets/AIOutput/ProjectMemory/`.
  - Repo router stores project reports in `<Project>/Assets/AIOutput/`.
  - Project routers reference both `Assets/AIOutput/ProjectMemory/` and `Assets/AIOutput/` distinctly.
  - Project routers load prior outputs from `Assets/AIOutput/`, not from `ProjectMemory/` only.
  - Internal overlay storage rules also preserve the split between reusable host rules, project memory, and mutable reports.
- No contradiction was found between:
  - root `Agents.md`
  - managed project routers
  - `AIModules/XUUnityInternal/start_session.md`

## Recommended cleanup order
1. Create or import a canonical extraction regression baseline under repo-level `AIOutput/Reports/`.
2. Commit the routing rollout separately in:
   - hub root
   - `AIRoot`
   - `ConnectivityCheckerPro`
   - `DevAccelerationSystem`
3. Archive or isolate `AIRoot/backup_Apr_12_2026/Agents.md` more clearly if it should no longer appear in normal search paths.
4. Add `known_issues.md` only when repeated issue classes become stable enough to justify durable project memory.

## Verification status
- `mixed verification`
