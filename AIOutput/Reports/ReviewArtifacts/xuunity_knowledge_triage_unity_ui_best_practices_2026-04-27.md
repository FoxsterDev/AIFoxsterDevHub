# XUUnity Knowledge Intake Review Report

## Source
- Type: external web article and tutorial set
- Topic: Unity UI authoring, scaling, layout stability, batching, raycast cost, text cost, and scroll-view performance
- Scope: public-safe reusable guidance for `AIRoot/Modules/XUUnity/skills/ui/`
- Source set:
  - Medium: `https://medium.com/@dariarodionovano/unity-ui-best-practices-40964a7a9aba`
  - DEV: `https://dev.to/marbleit/unity-ui-system-best-practices-2o24`
  - Unity Discussions: `https://discussions.unity.com/t/unity-ui-best-practices/573484`
  - Unity Learn: `https://learn.unity.com/course/doozyui-related-tutorials/tutorial/optimizing-unity-ui`
- Source access notes:
  - Medium, DEV, and Unity Learn were readable.
  - The Unity Discussions URL was blocked by anti-crawler protection during this run, so no content from that thread was extracted.
- Source summary:
  - The community articles focus on practical authoring hygiene: Canvas Scaler setup, anchors and pivots, consistent naming, prefabs, initial active-state discipline, avoiding `Best Fit`, disabling unnecessary `Raycast Target`, and not hiding inactive UI via alpha alone.
  - The Unity Learn tutorial provides the strongest performance-grounded rules: profile first, classify the problem before optimizing, split non-trivial Canvases by change cadence, treat layout groups and text generation as measurable cost centers, minimize raycast targets, and pool significant scroll content.
  - The strongest durable overlap across sources is not "use many Canvases" or "never use layouts"; it is to make change frequency, input surface, and text behavior explicit design constraints.

## Extracted Knowledge
- Durable rules:
  - Begin Unity UI optimization with profiling, and classify the bottleneck before changing structure:
    - GPU fill-rate or overdraw
    - Canvas batch rebuild cost
    - over-dirtying or too many rebuilds
    - text vertex or font-atlas cost
  - Split any non-trivial UI into static and dynamic Canvas regions based on change cadence, not purely by feature ownership.
  - Co-locate elements that update together on the same Canvas. Separate frequently changing elements from static backgrounds and labels.
  - Do not over-split into dozens of Sub-canvases. The correct tradeoff is rebuild isolation versus extra draw-call pressure.
  - Treat layout groups, `ContentSizeFitter`, and hierarchy-driven layout recalculation as performance-sensitive. Prefer RectTransform-driven layouts when the structure is small, fixed, and simple.
  - On hot or touch-heavy flows, audit `Raycast Target` aggressively. Only interactive elements should receive raycasts, and composite controls should prefer one root target instead of multiple child targets.
  - Avoid hiding inactive UI by alpha alone. If it is invisible and inactive in the product sense, it should usually stop participating in rendering.
  - Be careful with frequent enable or disable on large text-heavy UI trees. Re-enabling forces rebuild and rebatch work and can create visible stutter.
  - Avoid `Best Fit` on legacy UGUI `Text`. It creates inconsistent typography and can trigger expensive glyph-atlas behavior.
  - Prefer TMP over legacy `Text` for text quality, but still treat TMP auto-size and dynamic fallback configuration as performance and memory decisions rather than free defaults.
  - For localized or dynamic text systems, standardize font size and style combinations whenever possible to reduce atlas churn and batching fallout.
  - Scroll views with significant content should use pooling. For larger lists, only the visible window should own real visual items.
  - `RectMask2D` is useful on scroll views because off-viewport items should not keep contributing drawable geometry during rebuild analysis.
  - Reparenting pooled UI items can dirty graphics and trigger rebuilds. Pooling strategy should minimize hierarchy churn or isolate the churn with narrower Canvas boundaries.
  - UI state should not depend on the last scene state left in the Editor. Initial visibility and active-state ownership should be explicit.
  - UI authoring hygiene still matters because it reduces layout drift and review cost:
    - consistent naming
    - clean RectTransform values
    - predictable anchors and pivots
    - scale left at `1` outside intentional animation
    - reusable presets for repeated component defaults
  - Prefer white source assets plus tinting for uniformly colored visuals instead of multiplying near-identical textures.
- Non-durable examples or narrative:
  - specific screenshots and inspector examples from Medium and DEV
  - version-specific advice tied to Unity 5.2 through 5.4 internals
  - exact layout examples such as inventory rectangles or two-column anchor demos
  - the inaccessible Unity Discussions thread, which could not be validated in this run
- Project-specific details:
  - none

## Candidate Outputs
- Review artifact candidate:
  - this report as the approval package
- Skill candidate:
  - update `AIRoot/Modules/XUUnity/skills/ui/ugui.md`
  - update `AIRoot/Modules/XUUnity/skills/ui/layout_and_rebuilds.md`
  - update `AIRoot/Modules/XUUnity/skills/ui/input_and_navigation.md`
- Shared knowledge candidate:
  - none recommended at root `knowledge/` level
- Internal-shared candidate:
  - none
- Project-only candidate:
  - none
- No-action remainder:
  - general design-taste advice such as "use Unity Editor as inspiration" or typography taste guidance that is too broad for engineering prompts unless attached to a concrete implementation rule

## Existing Coverage
- Existing shared files:
  - `AIRoot/Modules/XUUnity/skills/ui/ugui.md`
  - `AIRoot/Modules/XUUnity/skills/ui/layout_and_rebuilds.md`
  - `AIRoot/Modules/XUUnity/skills/ui/input_and_navigation.md`
- Existing project override files:
  - none relevant
- Overlap summary:
  - current `ugui.md` already covers stable Canvas hierarchy, partial updates, pooling, safe area, and scene-authored hierarchy ownership
  - current `layout_and_rebuilds.md` already covers layout rebuild sensitivity, nested layout-group caution, non-interactive `RaycastTarget` auditing, and pooled list population
  - current `input_and_navigation.md` is intentionally narrow and does not yet encode raycast-surface discipline
  - the current shared stack does not yet state several useful rules explicitly:
    - profile-first UI optimization categories
    - split Canvas by synchronized change cadence
    - avoid alpha-only hiding of inactive UI
    - root-only raycast target preference for composite controls
    - explicit warning that frequent enable or disable of text-heavy UI trees can stutter
    - explicit `Best Fit` avoidance and TMP auto-size caution
    - `RectMask2D` and pooling guidance for substantial scroll content
    - explicit initial active-state ownership rather than editor-last-state dependence
- Existing family sufficient:
  - yes
- New skill family needed:
  - no

## Quality Evaluation
- Technical quality: 4
- Production safety: 5
- Unity `6000+` relevance: 4
- Mobile relevance: 5
- Zero-crash and zero-ANR alignment: 4
- Performance and microfreeze impact: 5
- Novelty: 3
- Merge fitness: 5
- Expected usefulness: 5

## Impact Analysis
- What problem this knowledge solves:
  - prevents broad, taste-driven UI refactors when the real issue is a specific Canvas, text, layout, or raycast cost center
  - raises the baseline on mobile UI microfreeze prevention
  - converts scattered Unity UI folklore into smaller reviewable rules that fit existing `xuunity` UI skills
- What becomes better if integrated:
  - more precise UI performance triage
  - better separation of static and dynamic UI ownership
  - fewer accidental raycast and text-cost regressions
  - better scroll-view decisions before teams commit to large dynamic lists
  - fewer bugs caused by implicit editor-authored initial active states
- What does not improve even after integration:
  - source-specific performance numbers still need project profiling
  - complex UI Toolkit guidance is not covered here
  - the blocked Unity Discussions source remains a confidence gap until accessed manually
- Risk of semantic loss during merge:
  - low if merged as compact rules into the existing UI skill files
  - moderate if merged as a broad new UI doctrine document with repeated or outdated version-specific detail

## Recommendation
- Recommended action:
  - keep this as a review artifact now
  - if approved, integrate selected public-core items into existing `skills/ui/` files only
- Candidate destination:
  - `AIRoot/Modules/XUUnity/skills/ui/ugui.md`
  - `AIRoot/Modules/XUUnity/skills/ui/layout_and_rebuilds.md`
  - `AIRoot/Modules/XUUnity/skills/ui/input_and_navigation.md`
- Destination-specific recommendations:
  - `skills/ui/ugui.md`
    - add a compact rule to keep initial UI active-state ownership explicit instead of relying on editor-left scene state
    - add a compact rule to avoid alpha-only hiding for inactive UI
    - add a compact rule to prefer TMP over legacy `Text` while still treating auto-size as a measured choice
  - `skills/ui/layout_and_rebuilds.md`
    - add profile-first optimization categories
    - add explicit static versus dynamic Canvas split guidance
    - add warning that frequent enable or disable of text-heavy trees causes rebuild spikes
    - add `Best Fit` avoidance
    - add `RectMask2D` plus pooling guidance for substantial scroll views
    - add caution that pooled reparenting can dirty large UI regions unless isolated
  - `skills/ui/input_and_navigation.md`
    - add one rule to minimize raycast surface area
    - add one rule that composite controls should usually receive input through one root target rather than many child targets
- Why nearby alternatives were rejected:
  - root `knowledge/` was rejected because these are repeatable implementation and review rules for a specific engineering domain, not repo-wide routing doctrine
  - `codestyle/` was rejected because the extracted material is about runtime UI behavior and performance structure, not naming or API-shape conventions
  - internal shared destinations were rejected because the content is public-safe and not tied to monorepo-private architecture
- External promotion candidate:
  - yes
- Target external repo id:
  - none selected in this package
- New family or topic proposal:
  - no
- Shared vs project-specific split:
  - all validated content is shared and public-safe
  - no project-only split is required
- Required narrowing or cleanup:
  - remove Unity 5.x-specific workaround details unless they still map to a current supported engine line
  - keep only rules that survive modern Unity review and profiling practice
  - do not copy inaccessible-thread assumptions into shared prompts

## Public-Safety Assessment
- Public-safe: yes
- Reason:
  - the extracted rules are generic Unity UI engineering practices and contain no project architecture, internal process, or confidential rollout context

## Internal-Sensitivity Assessment
- Internal sensitivity: none identified
- Reason:
  - no monorepo-private presenter stack, validation path, or package topology rule is required to apply these recommendations

## Project-Dependency Assessment
- Project dependency: low
- Reason:
  - the material is reusable across mobile Unity projects
  - any project-specific application will still require profiling and flow-specific validation

## Duplicate And Conflict Analysis
- Duplicate risk:
  - moderate, because `skills/ui/ugui.md` and `skills/ui/layout_and_rebuilds.md` already cover part of this territory
- Conflict risk:
  - low
- Conflict notes:
  - the current shared guidance says to avoid enabling or disabling large UI trees every frame; the extracted guidance strengthens this with a more concrete rebuild reason, not a conflicting rule
  - the current shared guidance already favors pooling on repeated lists; the extracted guidance narrows when pooling is worth the complexity and adds scroll-specific caveats
  - the only likely merge risk is importing outdated Unity-version-specific workarounds too literally

## Score Table
- `technical_quality`: 4
- `production_safety`: 5
- `mobile_relevance`: 5
- `novelty`: 3
- `merge_fitness`: 5
- `expected_usefulness`: 5
- Total: 27

## Recommended Apply Scope
- `apply shared skill items only`

## Approval Options
- `apply all approved items`
- `apply shared skill items only`
- `apply only ugui updates`
- `apply only layout-and-rebuild updates`
- `apply only input-and-navigation updates`
- `apply review artifact only`
- `reject`
