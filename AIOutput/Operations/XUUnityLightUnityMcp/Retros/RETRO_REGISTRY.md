# Host-private XUUnity MCP Retro Registry

Keep private evidence here. Public-safe lessons require sanitization before promotion.

| Date | Retrospective | Status | Follow-up |
|---|---|---|---|
| 2026-09-21 | [Release validation and operator evidence](2026-09-21_release_validation_retro.md) | Host-private; analysis complete | A1–A6 promotion/implementation proposals pending; A7 landed as MCP `master` `98bf6eb`; no MCP runtime change |

Implementation design for the 2026-09-21 retro: [Validation evidence and release acceptance](2026-09-21_validation_evidence_technical_design.md). Status: revised after the [principal review](2026-09-21_validation_evidence_design_principal_review.md); WP0–WP5 and the WP7 records implemented 2026-09-21 (uncommitted, see design §13), WP6 consumer adoption partially implemented, owner decision D2 open, independent acceptance pending.

## Grooming reconciliation — 2026-09-24

The row and design implementation record above describe the September 21
snapshot. The shared MCP source at `41e79e8` now records the offline evaluator
as shipped in `v0.3.79`, with helper-measurement authority corrected in `v0.3.80`.
The historical "uncommitted" and A1–A6 proposal labels must not be used to
reimplement that shipped scope. Original measurement dates/counts stay intact.

| Follow-up | Current backlog disposition | Completion requirement |
|---|---|---|
| A1/A2, WP1–WP5 | Shared evaluator implemented; consumer adoption partial | Reuse the shipped evaluator; preserve stage/channel/policy and denominator proof. |
| A3 / WP6 | Fresh consumer closeout pending in the inspected design | Run the existing consumer closeout with channel fields and the native-client receipt, then evaluate its exact output. A saved receipt alone is not the fresh closeout. |
| WP7 acceptance | Independent non-author acceptance pending | Review exact current scoped content and evidence; release publication alone does not close acceptance. |
| D2 | Optional owner decision, open | Decide whether to add host-only `client_probe` journaling as a separate bounded change; it is traceability, not client attestation. |
| A4/A5 | Existing consumer preflight and public compact guidance; adoption verification | Validate in the consumer closeout; do not invent a replacement runner. |
| A6 | Existing-contract regression / conditional | Re-run recovery proof when transport changes warrant it; no transport defect was established here. |
| A7 | Implemented maintenance | Keep current index state separate from historical measurement versions. |

This registry plus both linked design/review documents are mandatory inputs to
the Retro Groom automation. Private evidence remains here; the public design
history links only the sanitized acceptance design. This pass inspected local
source and records; it did not rerun the consumer or grant independent acceptance.
