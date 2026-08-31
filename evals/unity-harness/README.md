# Frozen Unity Harness Eval

This directory contains a deterministic, offline policy scorer. It does not
launch agents or Unity, access the network, manage sessions, or write task
state.

`cases.json` owns immutable expectations. Its exact content digest, ten-case
denominator, stable IDs, and seven-consumer denominator are protected by
`score.py`. `results.json` contains only candidate observations and cannot
lower those policy owners. Both fixtures use strict schemas: unknown or
missing fields, duplicate JSON keys or IDs, wrong types, and legacy counters
are rejected.

Evidence modes are explicit:

- `deterministic-contract` is an offline contract observation;
- `historical-replay` retains a known historical state and is not a new run;
- `live-observation` is reserved for genuinely executed evidence and is not
  used by the frozen baseline.

The ten cases retain the original eight behavior families, including the
blocked `UH-08` historical release invariant. `UH-09` covers exact MCP tooling,
tag, hash, package version, validator, and seven consumer pins. `UH-10` covers
semantic standalone detection and the unsupported compatibility lane without
claiming release support.

Run the scorer, its built-in mutation check, and the tracked mutation suite:

```sh
python3 evals/unity-harness/score.py
python3 evals/unity-harness/score.py --self-test
python3 -m unittest discover -s evals/unity-harness -p 'test_*.py'
```
