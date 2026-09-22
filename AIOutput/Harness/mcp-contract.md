# MCP Release Baseline and Development Checkout

`mcp-release-baseline.json` is the host's explicit supported consumer release:
a stable annotated tag and its immutable full commit SHA. It is not derived from
the developer checkout or whichever consumer happens to be inspected first.

The default static Harness gate verifies:

- every Git boundary still matches its parent gitlink;
- the configured tag exists, is annotated, and peels to the configured SHA;
- the package version stored at that tag matches the tag version;
- all seven consumers have the exact release URL, SHA, Git source and depth;
- the checkout contains the configured release in its ancestry.

The MCP checkout may advance or contain development changes. The report names
its actual commit, package version, dirty state and `checkout_state` separately
from `release_commit` / `package_hash`. Workspace PASS is not MCP release-ready.

Before MCP release acceptance, run:

```sh
python3 scripts/validate-unity-harness.py --stop --mcp-release
```

This adds the requirement that MCP is clean, exactly at the configured release
commit and has the release package version. It remains static proof only;
GitHub CI, Unity/package tests and all other release gates still apply.

To adopt a new release, explicitly update the baseline and consumer pins/locks
as one coordinated change after verifying that release. Do not move an existing
tag, rewrite locks to an unreleased checkout, or edit the baseline merely to
silence a check. A missing tag/object, invalid version, changed tag target,
unknown ancestry or incorrect consumer hash remains a hard failure.
