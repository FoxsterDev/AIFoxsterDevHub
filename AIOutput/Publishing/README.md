# Development-to-article handoff

Owner policy, 2026-09-08: substantive owner-product work should produce useful,
concise visual explanations on Foxster Labs as part of the development SOW/task.
The reader is a junior developer unfamiliar with the project. Prefer two to four
explanatory visuals with roughly 250–500 words over a prose release report.

## Authoritative route

The saved FoxsterLabs project and scheduled publisher use:
`/Users/siarheikha/Documents/FoxsterLabs`.

Read that repository's `AGENTS.md`, then:

- `docs/engineering-story-pipeline.md`
- `docs/editorial-roles.md`
- `docs/templates/engineering-story-brief.md`

These site-owned files define writing and review. Do not copy the full editorial
policy into product repositories or the shared public AIRoot modules. The separate
checkout at `/Users/siarheikha/Projects/FoxsterDev/foxsterlabs.com` is not a second
publication queue; do not distribute one story across both copies.

## Inside the SOW or development task

At planning, choose `article`, `group-with-related-work`, `changelog-only`, or `skip`
and give a short reader-value reason. Revisit after validation. Capture the concrete
symptom, expected/observed behavior, root cause, change, verified result, availability,
and useful visuals while the evidence is fresh. Use stable claim IDs/sourceKeys and
one storyKey across the task, site article, and later social variants.

If this is an eligible story and the site is accessible, prepare the short article
and diagrams through its author, reader-editor, and linguistic-editor passes before
closing the content part of the SOW. Product implementation and publication retain
separate truthful completion states. Routine internal churn should not force a post.

If site access is unavailable, embed the template's brief in the task's existing
project-local evidence/report and include its exact path in the handoff. Use the
project's normal private output directory. For a host-wide story, use
`AIOutput/Publishing/briefs/<story-id>.md`. The scheduled publisher reads this directory
and registered product sources; do not create an extra background service or timer.

## Scope and privacy

Applies to Connectivity Checker Pro, XUUnity MCP, and other owner-controlled tools
when a real source project is identified. Add a new product to the site's existing
registry only with verified identity and sources. “Another TUI” is not a product ID.

Keep proprietary code, client/employer facts, paths, credentials, and raw logs out of
the public text. Use the public-safe CCP release export for public release facts;
private code may explain a cause without being disclosed. A development brief never
proves that a build is in the Asset Store or otherwise released.

## Publication

The existing daily Foxster Publisher scan is the fallback for missed briefs and
coherent stories spanning several tasks. It shares the site ledger and duplicate
rules with on-demand work. It prepares private candidates and applies the same
reviewer roles. Website approval/release stays in the existing Foxster workflow;
Twitter/X, Threads, and LinkedIn are later drafts derived from the approved story.
Do not post to social accounts without explicit authorization.
