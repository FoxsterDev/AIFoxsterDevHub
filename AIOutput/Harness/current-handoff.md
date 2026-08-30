# Current Unity Harness Handoff

Updated: 2026-08-29

- Privacy: 7/7 project roots use `FD`, `CCP-PUB/S21/S22/S60/S63`, or
  `DAS-SRC/DEMO`; legacy identities are absent from all `ProjectSettings/**`.
  Unity Analytics/Connect/Cloud settings and explicit Analytics/Collab
  packages are disabled. Final host preflight has both
  `EnableEditorAnalytics` and `EnableEditorAnalyticsV2` at `0`.
- MCP: consumers pin stable `v0.3.62`, whose annotated tag object is
  `b1a559337a04d403498fdf836d53d84b62cf5789` and peeled package commit is
  `7b8b139d8bdd5d226e5e6703b586e1ca9f16f442`. The standalone Harness router
  commit on that base is `d5a38b9dc416fd92570c17d7e38e1d2090583ee7`.
- Child commits: AIRoot `b03874f1cd68eb3f9d627c71c8826d18a14aaefa`;
  Connectivity `7f56a5932c37f5cfa71658beef4863a74199fbd7`;
  DAS `5995aada17657a8e53c2148e27967babb733a4de`.
- Root convergence commit:
  `1da888cda854b1d590fedd071252b2d46fe903f3`.
- Live proof: MCP clean matrix passed Unity `2022.3.67f2` and `6000.0.58f2`
  with EditMode 91/91, PlayMode 5/5, three scenarios, and StandaloneOSX batch
  compile. Clean Hub consumer resolve/compile passed CCP-PUB, CCP-S21,
  CCP-S60, DAS-SRC, and DAS-DEMO.
- Follow-up proof on 2026-08-30: CCP-S22's obsolete absolute local-SDK
  dependency was removed; clean resolve/compile passes on exact Unity
  `2022.3.62f3`. CCP-S63 still requires exact `6000.3.3f1`, which is not
  installed; its lock is structurally aligned but has no exact-editor proof.
- Hook: the Stop gate is static and scoped to Harness routing/config only. It
  must still be explicitly trusted by the owner through `/hooks`.
- Final generated-state cleanup: no `Library/` directory remains in any of the
  seven tracked Unity project roots; the next Editor open will regenerate from
  clean state.
- Detailed evidence: `AIOutput/Harness/validation-evidence-2026-08-29.md`.
