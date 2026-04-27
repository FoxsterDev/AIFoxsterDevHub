# AIRoot Setup Retrospective

## Scope
- Host: `AIFoxsterDevHub`
- Date: `2026-04-26`
- Subject: retrospective on adopting `AIRoot` into a new multi-project host and evaluating what should improve in the public setup protocols

## Executive Summary
The public `AIRoot` setup model is directionally strong.
It gave a clean mental model for:
- repo router
- public `xuunity` core
- optional internal overlay
- project routers
- project memory

That model prevented several classes of failure:
- leaking host-specific knowledge into public `AIRoot`
- silently overwriting existing routers
- mixing durable project memory with mutable reports
- skipping project-local context in favor of one huge shared layer

The friction came from a different place:
the docs are topology-aware, but the automation is still only partially topology-aware.
In practice, the setup succeeded because the human operator understood the intended model and patched the gaps.
It did not succeed end-to-end from public bootstrap alone.

That distinction matters.
If `AIRoot` wants to be a reliable public setup system, it should optimize not only for “a skilled operator can make it work”, but for “the default bootstrap path naturally converges on the intended architecture”.

## What Worked Well

### 1. Public core versus private overlay separation is excellent
The strongest design choice in the public protocol stack is the clear split between:
- public reusable guidance in `AIRoot/Modules/XUUnity/`
- host-local reusable guidance in `AIModules/XUUnityInternal/`
- project-specific truth in `Assets/AIOutput/ProjectMemory/`

Why this was good:
- it made it obvious where the new hub-specific routing rules belonged
- it prevented accidental contamination of public `AIRoot` with repo-private workspace knowledge
- it kept the future publishing boundary intact

Why it matters:
Without this boundary, the system would degrade into one shared prompt swamp.
That would be cheaper in the first hour and much more expensive forever after.

### 2. Existing-router safety rules are correct and necessary
The refusal to silently rewrite existing `Agents.md` files is a strong public default.

Why this was good:
- it protects user-owned prompts
- it keeps bootstrap from acting destructively in repos with unknown history
- it forced deliberate adoption instead of blind replacement

Why it matters:
This is not optional polish.
AI setup automation that can casually erase working routing layers will eventually burn trust irrecoverably.

### 3. The generated router contract is compact and understandable
The managed repo router and project router shapes are good.
They are short enough to inspect, but specific enough to be operational.

Why this was good:
- the system stayed legible during bootstrap
- generated routers were easy to refresh safely
- the load order was explicit enough to debug later

Why it matters:
Prompt infrastructure fails when it becomes too magical to audit.
`AIRoot` largely avoids that trap.

### 4. Storage separation between `ProjectMemory` and `Assets/AIOutput/` is a strong default
The public storage contract is one of the best parts of the setup design.

Why this was good:
- it gave a clean place for durable truth
- it gave a separate place for reports and investigations
- it made later health review and freshness review meaningful

Why it matters:
If durable memory and temporary outputs share one bucket, freshness becomes impossible to reason about and every retrieval step becomes archaeology.

### 5. `xuunity` is a strong default family
Using one well-defined default protocol family for daily Unity work reduces cognitive overhead.

Why this was good:
- there was no routing ambiguity for most work
- the public docs stayed simple
- the internal overlay could extend behavior without replacing the public core

Why it matters:
A public protocol system wins when the default path is obvious.
`xuunity` gives that.

## What Worked Poorly

### 1. Topology is a first-class concept in docs, but not in bootstrap automation
This was the biggest real weakness.

The docs say:
- choose host topology first
- decide single-project vs monorepo
- decide whether internal overlay exists

But the scripts still infer too much from fixed assumptions.
In practice:
- `init_ai_repo.sh --repo-mode auto` detects monorepo only by checking whether `AIModules/XUUnityInternal/` already exists
- `init_ai_project.sh --repo-mode auto` follows the same assumption

Why this is bad:
- topology becomes circular
- the internal overlay is supposed to depend on host needs, but the scripts infer host mode from whether the overlay already exists
- the system cannot reliably recognize a multi-project host before the overlay is created

Why this matters:
This makes the public model intellectually cleaner than the public bootstrap.
That gap creates operator confusion exactly at the moment when confidence is most fragile: first setup.

### 2. Repo bootstrap and project bootstrap are too dependent on sequencing
`init_ai_project.sh` requires the root `Agents.md` to exist first.
That is reasonable internally, but the public ergonomics are weak.

What happened in practice:
- project bootstrap failed until repo bootstrap had already been applied
- the fix was straightforward, but the failure mode still cost a pass

Why this is bad:
- the system knows the dependency, but the public flow does not actively guide the operator through it beyond documentation
- there is no “topology plan then apply” command that computes the full safe sequence

Why this matters:
Good setup automation should reduce ordering errors, not merely document them.

### 3. `AIModules/XUUnityInternal/` had no public-safe scaffold path
The public docs correctly say the internal overlay is optional and useful for monorepos.
But until we added it manually, there was no scaffold that created:
- overlay README
- overlay entrypoint
- reachability rules
- starter host-local knowledge files

Why this is bad:
- the docs encourage the concept
- the scripts do not help instantiate the concept
- the first host-local overlay therefore tends to be improvised

Why this matters:
Optional does not mean under-supported.
If `AIRoot` wants internal overlays to be used well, it needs a minimal public-safe skeleton for them.

### 4. Project memory bootstrap was structurally correct but semantically weak
The project init script creates `Assets/AIOutput/ProjectMemory/`, but it does not seed useful baseline files.

What this meant in practice:
- every project got an empty memory root
- the system was formally “ready” but not operationally ready for memory-first workflows
- we had to invent starter memory files after bootstrap

Why this is bad:
- the setup reports success before the project is actually useful for repeated AI work
- freshness and health reviews then immediately report thin memory

Why this matters:
An empty memory directory is not the same thing as a usable memory layer.
Public setup should not confuse the two.

### 5. Public setup has no explicit story for nested git repos inside one host
This mattered a lot in `AIFoxsterDevHub`.

The host root contains nested repos:
- `AIRoot`
- `ConnectivityCheckerPro`
- `DevAccelerationSystem`

The public setup model never contradicted this, but it also did not help with it.

Why this is bad:
- the root repo can look “dirty” while the real actionable changes live inside child repos
- operators can misread commit surfaces
- rollout becomes harder to reason about

Why this matters:
This is a common real-world host shape for monorepos, package hubs, and tool overlays.
Public setup should at least acknowledge it and define a safe expectation.

### 6. System health is still stronger at detecting storage shape than setup maturity
The public health protocol is good at catching contradictions.
It is less good at judging whether a newly bootstrapped host is actually mature enough to rely on.

Why this is bad:
- a host can pass routing and storage checks while still being weak in:
  - memory completeness
  - internal overlay reachability
  - extraction evidence
  - rollout maturity across git surfaces

Why this matters:
Users care about operational readiness, not just architectural non-contradiction.

## What Should Improve In Public Protocols

### Improvement 1. Add topology-first bootstrap as the canonical public path
Recommendation:
- introduce `init_ai_topology.sh` as the new recommended public entrypoint
- keep `init_ai_repo.sh` and `init_ai_project.sh` for compatibility
- make the topology entrypoint render a plan first, then apply

Why:
- this aligns docs with automation
- it eliminates the circular dependency where monorepo inference depends on overlay existence
- it reduces user error on first setup

Why you should want this:
Right now the system is “understand the architecture, then drive the scripts correctly”.
That is fine for experts and bad for adoption.
Topology-first bootstrap turns expertise from a requirement into an advantage.

### Improvement 2. Persist host topology metadata
Recommendation:
- write `AIOutput/Registry/host_topology.yaml` during bootstrap

At minimum:
- `profile_id`
- `repo_mode`
- `storage_profile`
- `router_mode`
- `routed_projects`
- `active_repo_router`
- `active_project_memory_root`
- `active_project_reports_root`

Why:
- setup, health review, and registry tools need the same durable source of truth
- current behavior still infers too much from directory presence

Why you should want this:
Metadata removes ambiguity cheaply.
Without it, every future tool has to re-guess the host shape from the filesystem and will occasionally guess wrong.

### Improvement 3. Add a public-safe internal overlay scaffold
Recommendation:
- add an optional bootstrap flag such as `--with-xuunity-internal-overlay`
- generate:
  - `AIModules/README.md`
  - `AIModules/XUUnityInternal/README.md`
  - `AIModules/XUUnityInternal/start_session.md`
  - starter `knowledge/` files or placeholders

Why:
- the docs already teach the concept
- the setup path should support the concept directly

Why you should want this:
The first overlay sets the tone for every later host-local rule.
If that first version is improvised, the cost compounds.
If the first version is scaffolded well, consistency compounds instead.

### Improvement 4. Add a project memory baseline template to public bootstrap
Recommendation:
- on project bootstrap, optionally generate:
  - `ProjectMemory/README.md`
  - `ProjectMemory/SkillOverrides/README.md`
- for canonical source style projects, optionally offer a baseline pack such as:
  - `testing_strategy.md`
  - `platform_constraints.md`
  - `release_rules.md`

Why:
- an empty folder is not a usable memory system
- the current bootstrap overstates readiness

Why you should want this:
This is one of the highest-ROI changes in the whole retrospective.
It moves the system from “files exist” to “the next AI session has something stable to load”.

### Improvement 5. Add explicit public guidance for nested-repo hosts
Recommendation:
- extend public setup docs with a short section:
  - how nested repos affect rollout
  - how to read `git status`
  - when a workspace router belongs to a child repo rather than the host root

Why:
- the current model silently assumes one host repo surface
- real package hubs often do not look like that

Why you should want this:
This avoids avoidable rollout mistakes without complicating the default path for simpler repos.
It is a high-value clarification with low documentation cost.

### Improvement 6. Add post-bootstrap health validation as a public default
Recommendation:
- after bootstrap, offer a standard follow-up step:
  - `xuunity system health review`
  - `xuunity project memory freshness this project`

Why:
- setup success should be followed by setup verification
- current public path stops too early

Why you should want this:
Bootstrap creates structure.
Health and freshness tell you whether the structure is trustworthy.
Without that second step, teams can confuse installed scaffolding with actual readiness.

### Improvement 7. Define reachability expectations for host-local knowledge files
Recommendation:
- public docs should say explicitly:
  - every new knowledge file needs a selection path
  - that selection path must live in an entrypoint, trigger rule, or utility reference

Why:
- otherwise overlay knowledge becomes ballast quickly

Why you should want this:
Knowledge that cannot be selected is not a capability.
It is storage cost disguised as intelligence.

## What Should Not Be Changed

### 1. Do not weaken existing-router safety
This should stay strict.
Any change that makes adoption easier by making silent rewrite easier is the wrong trade.

### 2. Do not collapse public core and internal overlay into one layer
That would look simpler and age badly.
The current separation is one of the best parts of the architecture.

### 3. Do not move project truth out of `ProjectMemory` just to make bootstrap look easier
The solution to thin project memory is better project-memory scaffolding, not weaker project-memory boundaries.

## Recommended Public Protocol Priority Order

### Highest ROI
1. topology-first bootstrap entrypoint
2. project memory baseline template
3. persisted host topology metadata

### Next
4. internal overlay scaffold
5. post-bootstrap health validation
6. nested-repo host guidance

### Later
7. broader profile-aware health tooling and storage-profile expansion

## Why These Improvements Are Worth It
If you do nothing, `AIRoot` still works for expert operators.
If you implement the improvements above, `AIRoot` becomes:
- easier to adopt correctly
- less dependent on human patch-up after bootstrap
- safer to scale across different host shapes
- more honest about actual readiness

That is the key argument.

The problem is not that the current public setup is wrong.
The problem is that it is better as an architecture than it is as a default operational experience.

Closing that gap matters because public protocol systems are judged by the first setup path, not only by the elegance of their internal design.

## Verification Status
- based on direct bootstrap experience in `AIFoxsterDevHub`
- based on current public docs, templates, and bootstrap scripts
- based on subsequent health and freshness remediation performed during the same rollout
