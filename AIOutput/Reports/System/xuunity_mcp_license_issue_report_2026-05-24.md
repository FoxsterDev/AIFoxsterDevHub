# Unity License & XUUnity Light MCP - Issue Report

Status: `historical host-local incident report`
Storage: `AIOutput/Reports/System/`
Public promotion: `do not promote as-is`

This is a point-in-time AIFoxsterDevHub operational report from 2026-05-24.
Keep it as historical evidence for the local workspace, not as current MCP
guidance. It references `XUUnity Light MCP v0.3.14`; later releases added
license-aware capability probing and batch fallback behavior, so re-check
current behavior against the active MCP version before using this report for
decisions.

**Date**: 2026-05-24  
**Environment**: AIFoxsterDevHub workspace with 7 Unity projects  
**XUUnity Light MCP Version**: v0.3.14  
**Unity Versions Tested**: 2021.3.45f2, 2022.3.62f3, 6000.0.58f2, 6000.3.3f1

---

## Summary

XUUnity Light Unity MCP was successfully installed and configured for 7 Unity projects in the AIFoxsterDevHub workspace. However, **automated test execution via MCP was blocked by Unity licensing requirements** for batch-mode operations.

---

## Installation Status: ✅ SUCCESS

### What Works:
- ✅ MCP server installed in `~/.claude-tools/xuunity-light-unity-mcp/`
- ✅ Unity package `com.xuunity.light-mcp` v0.3.14 installed in all 7 projects
- ✅ Bridge configuration enabled for all projects
- ✅ `.mcp.json` configured with both JetBrains and xuunity_light_unity servers
- ✅ Setup validation passed for all projects
- ✅ Direct Python script invocation works (workaround for Rider)

### Projects Configured:

**ConnectivityCheckerPro:**
- Sample2021 (Unity 2021.3.45f2) - ✅ Test Framework 1.1.33
- Sample2022 (Unity 2022.3.62f3) - ✅ Test Framework 1.1.33 (compilation errors)
- Sample6000 (Unity 6000.0.58f2) - ⚠️ No Test Framework
- Sample6000_3_2f1 (Unity 6000.3.3f1) - ⚠️ No Test Framework
- Publish (Unity 2022.3.62f3) - ⚠️ No Test Framework

**DevAccelerationSystem:**
- Main (Unity 2022.3.62f3) - ✅ Test Framework 1.1.33
- DemoProject (Unity 2022.3.62f3) - ✅ Test Framework 1.1.33

---

## Issue #1: Unity Batch-Mode License Requirement ❌

### Problem:
When attempting to run tests via `batch-editmode-tests`, Unity batch mode failed with:

```
[Licensing::Client] Error: Code 500 while updating license in client
[Licensing::Client] Error: Code 404 while processing request
[Licensing::Module] Error: 'com.unity.editor.headless' was not found.
No valid Unity Editor license found. Please activate your license.
```

### Details:
- **Error Code**: `batch_exit_code: 1`
- **Transport Outcome**: `batch_process_failed`
- **Unity Outcome**: `unknown`
- **Blocker**: Missing Unity batch-mode license activation

### Command Attempted:
```bash
python3 ~/.claude-tools/xuunity-light-unity-mcp/server.py batch-editmode-tests \
  --project-root /path/to/ConnectivityCheckerPro_Sample2021 \
  --timeout-ms 300000
```

### Root Cause:
Unity batch-mode operations (`-batchmode` flag) require a valid Unity license for the `com.unity.editor.headless` entitlement. The current system does not have batch-mode licensing activated.

---

## Issue #2: Interactive Unity Editor Startup Failures ❌

### Problem A: Editor Process Died (Sample2021)

**Error**: `editor_ready_timeout`

Unity Editor started but crashed/exited before MCP bridge could initialize.

**Evidence**:
- Editor PID 93118 started but is no longer alive
- Bridge state never created (no heartbeat)
- `host_health_classification: offline`
- `reconciliation_status: offline`

**Editor Log**:
```
Failed to connect to local IPC Name not known
Could not lock editor preferences. Preferences updates for this instance of Unity will not be saved.
[Licensing::Client] Successfully updated the access token
```

### Problem B: Compilation Errors Block Bridge (Sample2022)

**Error**: `interactive_compile_block_detected`

Unity Editor (PID 93141) is running but has compilation errors that prevent MCP bridge initialization.

**Evidence**:
```
LocalPriceAmount.cs(14,10): error CS0246: The type or namespace name 'JsonPropertyAttribute' could not be found
Library/PackageCache/com.aghanim.sdk@99b91b367c49/.../LocalPriceAmount.cs: Missing JsonProperty
```

**Root Cause**: Missing dependency - `com.aghanim.sdk` package requires Newtonsoft.Json (or similar JSON serialization library) which is not installed.

**Health Status**:
- Editor running: ✅ (PID 93141 alive)
- Bridge state: ❌ (not created due to compilation errors)
- `host_health_classification: stale`
- `reconciliation_status: degraded`

---

## XUUnity Light MCP Operational Modes

### Mode 1: Batch Mode (Closed Editor) ❌ BLOCKED BY LICENSE

**Requirements**:
- Unity Editor must be **closed**
- Unity batch-mode license required (`com.unity.editor.headless`)
- No compilation errors

**Status**: Not functional - license missing

**Use Cases**:
- Automated CI/CD pipelines
- Headless test execution
- Compilation checks without opening Unity

### Mode 2: Interactive Mode (Live Editor) ⚠️ PARTIALLY BLOCKED

**Requirements**:
- Unity Editor must be **running**
- Project must compile without errors
- MCP bridge package installed and enabled

**Status**: Functional only if compilation succeeds

**Blockers**:
- Sample2021: Editor crashes on startup
- Sample2022: Compilation errors prevent bridge initialization
- Sample6000/Sample6000_3_2f1/Publish: No Test Framework (tests unavailable)

**Use Cases**:
- Real-time development workflows
- Manual test execution with AI assistance
- Live project inspection

---

## License Requirements by Unity Edition

| Unity License Type | Batch-Mode Support | Interactive Mode | Notes |
|-------------------|-------------------|------------------|-------|
| **Personal** | ❌ Requires activation | ✅ Yes | Batch needs explicit entitlement |
| **Plus** | ❌ Requires activation | ✅ Yes | Same as Personal |
| **Pro** | ✅ Yes | ✅ Yes | Full batch-mode support |
| **Enterprise** | ✅ Yes | ✅ Yes | Full batch-mode support |

**Current Status**: Unknown license type, batch-mode not activated

---

## Workarounds

### Option 1: Fix Compilation Errors (Sample2022)

Install missing dependency for `com.aghanim.sdk`:

```bash
# Add Newtonsoft.Json via Package Manager
# Or add to Packages/manifest.json:
"com.unity.nuget.newtonsoft-json": "3.2.1"
```

This would enable **Interactive Mode** for Sample2022.

### Option 2: Activate Unity Batch-Mode License

1. Contact Unity support or use Unity Hub
2. Activate batch-mode entitlement for your account
3. Verify with: `Unity -batchmode -quit`

This would enable **Batch Mode** for all projects.

### Option 3: Use Interactive Unity Editor Manually

Open Unity Editor manually for each project and use MCP live bridge for non-test operations:

```bash
# Status check
python3 ~/.claude-tools/xuunity-light-unity-mcp/server.py request-status-summary \
  --project-root /path/to/project

# Compile check  
python3 ~/.claude-tools/xuunity-light-unity-mcp/server.py request-compile \
  --project-root /path/to/project
```

---

## Recommendations

### Short-term:
1. **Fix Sample2022 compilation errors** - Add Newtonsoft.Json dependency
2. **Investigate Sample2021 crashes** - Check Unity logs for startup failures
3. **Use interactive mode** for projects without compilation errors (Sample2021, DevAccelerationSystem projects)

### Long-term:
1. **Activate Unity batch-mode license** for CI/CD and headless operations
2. **Install Test Framework** on Sample6000 projects if test operations are needed
3. **Document Unity license requirements** in project README for team members

---

## MCP Capabilities Matrix

| Project | Package | Bridge | Interactive | Batch | Tests | Status |
|---------|---------|--------|-------------|-------|-------|--------|
| Sample2021 | ✅ | ✅ | ❌ Crash | ❌ License | ✅ TF 1.1.33 | Editor unstable |
| Sample2022 | ✅ | ✅ | ❌ Compile | ❌ License | ✅ TF 1.1.33 | Fix compilation |
| Sample6000 | ✅ | ✅ | ⚠️ Unknown | ❌ License | ❌ No TF | Not tested |
| Sample6000_3_2f1 | ✅ | ✅ | ⚠️ Unknown | ❌ License | ❌ No TF | Not tested |
| Publish | ✅ | ✅ | ⚠️ Unknown | ❌ License | ❌ No TF | Not tested |
| DevAccel Main | ✅ | ✅ | ⚠️ Unknown | ❌ License | ✅ TF 1.1.33 | Not tested |
| DevAccel Demo | ✅ | ✅ | ⚠️ Unknown | ❌ License | ✅ TF 1.1.33 | Not tested |

**Legend**: TF = Test Framework, ✅ = Working, ❌ = Blocked, ⚠️ = Untested

---

## Conclusion

XUUnity Light MCP installation is **technically successful** but **operationally blocked** by:
1. Missing Unity batch-mode license (affects all automated workflows)
2. Project-specific compilation errors (Sample2022)
3. Editor stability issues (Sample2021)

**Next Steps**: Prioritize Unity license activation for batch-mode operations OR fix project compilation errors to use interactive mode as workaround.
