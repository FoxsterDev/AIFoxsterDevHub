# Unity Privacy Preflight — 2026-08-29

Interpretation: “Unity iCloud” means Unity Cloud/Unity Services linkage, not
Apple iCloud. Scope is the seven active Unity roots in this Hub checkout.

## Result

- Global macOS Unity Editor preferences:
  - `EnableEditorAnalytics = 0`
  - `EnableEditorAnalyticsV2 = 0`
- Every project has empty `cloudProjectId`, `organizationId`, and `projectName`.
- Every project has `cloudEnabled: 0`, empty `cloudServicesEnabled`, and
  `UnityConnectSettings.m_Enabled: 0`.
- Analytics, Ads, Crash Reporting, Purchasing, Performance Reporting, and their
  startup initialization are disabled in tracked settings.
- `submitAnalytics: 0` is tracked for every PlayerSettings root.
- Explicit Analytics modules were removed from three manifests/locks; the one
  explicit Collab/Version Control proxy was removed from Sample2022.
- Unity Hub has no registered entry under the current AIFoxsterDevHub checkout,
  so it has no current checkout Cloud identity to disconnect.

## Unity-visible abbreviations

| Local role | Unity product name | Identifier family |
| --- | --- | --- |
| Connectivity package publisher | `CCP-PUB` | `com.fd.ccp.pub` |
| 2021 consumer | `CCP-S21` | `com.fd.ccp.s21` |
| 2022 consumer | `CCP-S22` | `com.fd.ccp.s22` |
| Unity 6000.0 consumer | `CCP-S60` | `com.fd.ccp.s60` |
| Unity 6000.3 consumer | `CCP-S63` | `com.fd.ccp.s63` |
| DAS source | `DAS-SRC` | `com.fd.das.src` |
| DAS demo | `DAS-DEMO` | `com.fd.das.demo` |

Repository paths and UPM package IDs remain unchanged to preserve Git history,
file consumers, package resolution, and public API compatibility. Global Editor
Analytics is disabled so those paths are not intentionally sent as Editor usage
analytics during validation.

## Reproducible gate

```sh
python3 scripts/validate-unity-privacy.py --require-host-opt-out
```

Observed result: `7` checked, `0` failures, `pass`. Unity was not launched before
this gate became green.

The gate proves local tracked configuration and the macOS opt-out. It does not
claim deletion of historical data from an unrelated Unity Dashboard project.
