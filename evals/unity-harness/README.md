# Frozen Unity Harness Eval

This eval is a deterministic policy scorer. It does not launch agents, manage
sessions, run Unity, or write task state.

```sh
python3 evals/unity-harness/score.py
python3 evals/unity-harness/score.py --self-test
```

The eight frozen cases cover docs-only, contained C#, package-to-consumer proof,
serialized assets, high-risk save compatibility, native/device ceilings,
Unity-version matrices, and a release-intentional-failure truth case.
