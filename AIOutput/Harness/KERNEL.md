# Unity Unified Harness Kernel

Status: active | Owner: AIFoxsterDevHub | Updated: 2026-09-02

## Shape And Ownership

Use the native host; this is routing and proof policy, not a runtime, broker,
queue, daemon, or task store:

`native host -> compact kernel -> nearest standalone adapter -> conditional Unity guidance -> focused proof -> zero or one outcome`

Load the root and nearest `AGENTS.md`, this kernel, and the selected adapter.
Load project memory only for the target. Satellites work without the Hub or
private overlay. Public Unity rules belong in `AIRoot/Modules/XUUnity/`; the
topology owner is `AIOutput/Registry/host_topology.yaml`.

## Lanes

| Lane | Trigger | Minimum truthful route |
| --- | --- | --- |
| docs | prose, routing, frozen data | exact diff plus narrow static owner |
| ordinary | contained code or package wiring | exact-version resolve/compile plus focused test |
| high-risk | lifecycle, serialization, migration, native, permissions | ordinary proof plus the matching transition, fixture, build, or device boundary |
| release | version, support, distribution, readiness claim | clean source and consumer proof plus every claimed matrix/platform gate |

Escalate on higher risk; never lower a lane to fit the machine. Package-source and consumer proof are distinct.

## Final Impact Route

After runtime implementation, load
`AIRoot/Modules/XUUnity/reviews/post_implementation_impact_review.md` for the
default final pass. Load broader delivery, policy, platform, full-review, or
release guidance only when that card names a concrete trigger.

## Proof And Claims

Start with the smallest falsifying static/resolve check, then compile, focused
EditMode or PlayMode, lifecycle/reopen, platform build, and physical device only
as required. Record exact Unity version and build target. A helper test proves
only its helper unless decisive proof crosses the real orchestration boundary.

Strongest ceiling labels are `static`, `resolved`, `compiled`, `editmode`,
`playmode`, `serialized-reopen`, `platform-build`, `physical-device`, and
`release`. Missing versions, licenses, targets, devices, or baseline health stay
explicit; they never become passing claims.

## Privacy And Launch Authority

`python3 scripts/validate-unity-privacy.py` owns deterministic repository
privacy structure. Immediately before Unity, add `--require-host-opt-out` to
check host Editor/Hub launch authority. A red host result forbids Unity and its
claims, but does not falsify docs-only topology or static Harness checks. Never
change host preferences or Hub records without explicit owner authorization.

## Outcome And Independent Acceptance

Most turns write no durable outcome; write at most one when a reusable decision
or blocker must be handed off. Every final implementation/review handoff begins:

```text
Readiness: <designed|implemented-unverified|owner-QA-ready|release-ready>
Independent acceptance: <pending|PASS|REVISE|not-required>
Accept as complete: <yes|no>
Next required action: <action|none>
```

High-risk authors cannot self-certify. PASS or REVISE comes only from a fresh
non-author review bound to each repository, full base commit, sorted scoped
paths, and SHA-256 of exact current content. In-scope mutation invalidates it;
unrelated dirt does not. Pending or REVISE is never ready/complete. PASS cannot
erase a missing Unity, consumer, platform, device, owner, or release gate.

## Finish And Maintenance

The scoped Stop hook is static-only, bounded, owner-trusted, fail-open on faults,
and a no-op for product/generated/build/log/marketing paths; it never runs Unity.

Open another generic audit only after a demonstrated false-ready/route, the same
gap in two natural tasks/repositories, a material scorer/contract change, a new
satellite/project class, or an explicit release-owner request. Calendar time alone is not a trigger.
