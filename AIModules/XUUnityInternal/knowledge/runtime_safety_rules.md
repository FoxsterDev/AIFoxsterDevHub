# Runtime Safety Rules

## Purpose
Capture internal reusable rules for Unity runtime validation and deadlock avoidance that are broader than one project but still operationally specific to this host.

## Async Disposal Rule
- Do not block the Unity main thread on an async disposal path that awaits work while capturing the current `SynchronizationContext`.
- If a disposal path may be waited synchronously in tests, shutdown, or teardown code, awaited internal tasks should avoid resuming onto the blocked Unity context.
- In practice, prefer `ConfigureAwait(false)` or an equivalent context-free await on the internal background task before exposing a sync wait pattern such as `GetAwaiter().GetResult()`.

## Platform Target Test-Seam Rule
- For platform-native targets, prefer internal bridge seams over public-API changes when the goal is testability.
- The test seam should allow runtime-path validation of `Log()` and `LogBatch()` without weakening or redesigning the user-facing contract.
- Use editor tests for deterministic mapping and payload rules.
- Use playmode or player-runnable tests for the real runtime execution path.
- Keep physical device proof separate when the claim depends on native log sinks, platform observability, or device-only lifecycle behavior.
