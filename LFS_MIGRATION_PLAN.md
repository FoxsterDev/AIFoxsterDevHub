# Git LFS Migration Plan

This plan is intentionally forward-only by default. It avoids history rewrites and keeps rollback simple.

## Current state

- Git LFS is installed locally and active in `AIFoxsterDevHub`, `AIRoot`, `ConnectivityCheckerPro`, and `DevAccelerationSystem`.
- `ConnectivityCheckerPro` and `DevAccelerationSystem` already have `.gitattributes` rules for LFS.
- Existing binary files in both repos are still stored as normal Git blobs, not LFS pointers.

Confirmed examples:

- `ConnectivityCheckerPro_Publish/Assets/FoxsterDev/ConnectivityCheckerPro/_Main.png`
- `ConnectivityCheckerPro_Publish/Assets/ConnectivityCheckerPro/Documentation/README.pdf`
- `ConnectivityCheckerPro_Sample2022/Assets/ConnectivityCheckerPro/Documentation/README.pdf`
- `DevAccelerationSystem/Packages/ZString.Unity.2.6.0.tgz`
- `Docs/Img12.png`

## Main risk

The current `ConnectivityCheckerPro/.gitattributes` tracks broad extensions like `*.png` and `*.pdf`.
If those rules are applied as-is during migration, tiny third-party icons under Unity vendor packages can also move into LFS.

That is usually not what you want.

## Safe strategy

1. Freeze changes in the target repo while doing the migration.
2. Create a backup tag and a backup branch before touching tracked binaries.
3. Narrow LFS tracking rules to the binary files you actually own and want in LFS.
4. Re-add only those files so the next commit stores LFS pointers.
5. Push and validate on a clean clone.
6. Consider history rewrite only later, as a separate explicit project.

## Repo-specific scope

### ConnectivityCheckerPro

Recommended LFS candidates:

- `ConnectivityCheckerPro_Publish/Assets/FoxsterDev/ConnectivityCheckerPro/_Main.png`
- `ConnectivityCheckerPro_Publish/Assets/FoxsterDev/ConnectivityCheckerPro/_AppImage.png`
- `ConnectivityCheckerPro_Publish/Assets/ConnectivityCheckerPro/Documentation/README.pdf`
- `ConnectivityCheckerPro_Sample2022/Assets/ConnectivityCheckerPro/Documentation/README.pdf`

Recommended non-goals for the first pass:

- Unity package cache/vendor icons under `Packages/com.unity.asset-store-tools/...`
- generated build outputs

### DevAccelerationSystem

Recommended LFS candidates:

- `DevAccelerationSystem/Packages/ZString.Unity.2.6.0.tgz`
- `Docs/Img12.png`
- `Docs/Img15.png`
- `Docs/Img2.png`
- `Docs/Img3.png`
- `Docs/Img4.png`
- `Docs/Img6.png`
- `Docs/Img7.png`

## Forward-only migration procedure

Run these steps inside each target repo independently.

### 1. Create safety points

```bash
git checkout <target-branch>
git pull --ff-only
git tag pre-lfs-migration-$(date +%Y%m%d)
git branch backup/pre-lfs-migration-$(date +%Y%m%d)
```

### 2. Narrow `.gitattributes`

Prefer explicit owned paths over broad global extension rules.

Example direction for `ConnectivityCheckerPro`:

```gitattributes
ConnectivityCheckerPro_Publish/Assets/FoxsterDev/ConnectivityCheckerPro/*.png filter=lfs diff=lfs merge=lfs -text
ConnectivityCheckerPro_Publish/Assets/ConnectivityCheckerPro/Documentation/*.pdf filter=lfs diff=lfs merge=lfs -text
ConnectivityCheckerPro_Sample2022/Assets/ConnectivityCheckerPro/Documentation/*.pdf filter=lfs diff=lfs merge=lfs -text
```

Example direction for `DevAccelerationSystem`:

```gitattributes
DevAccelerationSystem/Packages/*.tgz filter=lfs diff=lfs merge=lfs -text
Docs/*.png filter=lfs diff=lfs merge=lfs -text
```

If you want to keep the broad extension rules, do that consciously and accept that many more files may move to LFS.

### 3. Re-add only selected files

After updating `.gitattributes`:

```bash
git rm --cached <file1> <file2> ...
git add .gitattributes <file1> <file2> ...
git status
git lfs ls-files
```

Expected result:

- the files stay in the working tree
- Git index now stores LFS pointers
- `git lfs ls-files` lists the selected files

### 4. Commit

```bash
git commit -m "Move owned binary assets to Git LFS"
```

### 5. Validate before push

```bash
git show --stat --summary HEAD
git lfs ls-files
git cat-file -p HEAD:<path-to-file>
```

For an LFS-managed file, `git cat-file -p` should show pointer text starting with `version https://git-lfs.github.com/spec/v1`.

### 6. Push and verify from a clean clone

```bash
git push origin <target-branch>
git lfs push origin <target-branch>
```

Then verify using a fresh clone:

```bash
git clone <repo-url> test-lfs-clone
cd test-lfs-clone
git lfs ls-files
```

## Optional later step: historical cleanup

Only do this if repository size or clone performance still matters after the forward-only migration.

This step rewrites history and must be treated as a coordinated migration:

- notify all collaborators
- push backup refs first
- rewrite in a dedicated branch
- validate tags/branches/submodules
- force-push only after approval

Typical tool:

```bash
git lfs migrate import --include="<pattern1>,<pattern2>"
```

Do not run `git lfs migrate import --everything` casually.

## Recommended next execution order

1. Migrate `DevAccelerationSystem` first because the candidate set is small and explicit.
2. Migrate `ConnectivityCheckerPro` second after narrowing `.gitattributes`.
3. Push those repos first.
4. Then update `AIFoxsterDevHub` submodule pointers if the submodule commits changed.
