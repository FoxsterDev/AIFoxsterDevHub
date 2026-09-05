#!/usr/bin/env python3
"""Bind high-risk Harness acceptance to exact multi-repository diff scopes."""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import stat
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path, PurePosixPath


OUTCOME_FIELDS = (
    "Readiness",
    "Independent acceptance",
    "Accept as complete",
    "Next required action",
)
READINESS = {"designed", "implemented-unverified", "owner-QA-ready", "release-ready"}
ACCEPTANCE = {"pending", "PASS", "REVISE", "not-required"}
BASE_RE = re.compile(r"[0-9a-f]{40}(?:[0-9a-f]{24})?")
FINGERPRINT_RE = re.compile(r"sha256:[0-9a-f]{64}")
REPOSITORY_RE = re.compile(r"Review repository: id=([A-Za-z0-9._-]+); path=(.+)")
REVIEWER_RE = re.compile(r"Reviewer context: (.+); reviewer authored the reviewed diff: (yes|no)\.")
@dataclass(frozen=True)
class ReviewScope:
    identity: str
    repository: Path
    base: str
    paths: tuple[str, ...]
    fingerprint: str


def parse_outcome_block(text: str) -> tuple[dict[str, str], list[str]]:
    lines = text.splitlines()
    if len(lines) < len(OUTCOME_FIELDS):
        return {}, ["outcome block is incomplete"]
    values: dict[str, str] = {}
    errors: list[str] = []
    for index, field in enumerate(OUTCOME_FIELDS):
        prefix = f"{field}: "
        if not lines[index].startswith(prefix) or not lines[index][len(prefix):].strip():
            errors.append(f"line {index + 1} must be {prefix}<value>")
        else:
            values[field] = lines[index][len(prefix):].strip()
    for field in OUTCOME_FIELDS:
        count = sum(line.startswith(f"{field}: ") for line in lines)
        if count != 1:
            errors.append(f"expected exactly one {field!r} field, found {count}")
    return values, errors


def _one_value(lines: list[str], field: str) -> tuple[str | None, list[str]]:
    prefix = f"{field}: "
    values = [line[len(prefix):].strip() for line in lines if line.startswith(prefix)]
    if len(values) != 1:
        return None, [f"expected exactly one {field!r} field, found {len(values)}"]
    return values[0], []


def normalized_paths(value: str) -> tuple[tuple[str, ...], list[str]]:
    raw = [item.strip() for item in value.split(",") if item.strip()]
    errors: list[str] = []
    if not raw:
        return (), ["Review scoped paths must list at least one path"]
    if len(raw) != len(set(raw)):
        errors.append("Review scoped paths contains duplicates")
    for item in raw:
        path = PurePosixPath(item)
        if path.is_absolute() or ".." in path.parts or item == "." or path.as_posix() != item:
            errors.append(f"invalid repository-relative review path: {item!r}")
    if raw != sorted(raw):
        errors.append("Review scoped paths must be sorted")
    return tuple(raw), errors


def parse_scopes(text: str) -> tuple[list[ReviewScope], list[str]]:
    lines = text.splitlines()
    scopes: list[ReviewScope] = []
    errors: list[str] = []
    for index, line in enumerate(lines):
        if not line.startswith("Review repository: "):
            continue
        match = REPOSITORY_RE.fullmatch(line)
        if not match:
            errors.append(f"invalid Review repository line: {line!r}")
            continue
        repository = Path(match.group(2))
        if not repository.is_absolute():
            errors.append(
                f"{match.group(1)}: Review repository path must be absolute: {match.group(2)!r}"
            )
        if index + 3 >= len(lines):
            errors.append(f"review tuple for {match.group(1)} is incomplete")
            continue
        expected_prefixes = ("Review base: ", "Review scoped paths: ", "Review fingerprint: ")
        values: list[str] = []
        for offset, prefix in enumerate(expected_prefixes, start=1):
            candidate = lines[index + offset]
            if not candidate.startswith(prefix) or not candidate[len(prefix):].strip():
                errors.append(f"review tuple for {match.group(1)} must contain contiguous {prefix}<value>")
                values.append("")
            else:
                values.append(candidate[len(prefix):].strip())
        paths, path_errors = normalized_paths(values[1]) if values[1] else ((), [])
        errors.extend(path_errors)
        if values[0] and BASE_RE.fullmatch(values[0]) is None:
            errors.append(f"{match.group(1)}: Review base must be a full commit id")
        if values[2] and FINGERPRINT_RE.fullmatch(values[2]) is None:
            errors.append(f"{match.group(1)}: Review fingerprint must be sha256:<64 lowercase hex>")
        scopes.append(
            ReviewScope(match.group(1), repository, values[0], paths, values[2])
        )
    identities = [scope.identity for scope in scopes]
    repositories = [str(scope.repository.resolve()) for scope in scopes]
    if len(identities) != len(set(identities)):
        errors.append("Review repository IDs must be unique")
    if len(repositories) != len(set(repositories)):
        errors.append("Review repository paths must be unambiguous and unique")
    return scopes, errors


def _git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args], text=True, capture_output=True, check=False
    )
    if result.returncode != 0:
        raise ValueError(result.stderr.strip() or f"git {' '.join(args)} failed")
    return result.stdout.strip()


def _feed(hasher: "hashlib._Hash", value: bytes) -> None:  # type: ignore[name-defined]
    hasher.update(len(value).to_bytes(8, "big"))
    hasher.update(value)


def _base_has_path(repo: Path, base: str, relative: str) -> bool:
    return subprocess.run(
        ["git", "-C", str(repo), "cat-file", "-e", f"{base}:{relative}"],
        text=True, capture_output=True, check=False,
    ).returncode == 0


def _index_entry(repo: Path, relative: str) -> tuple[str, str] | None:
    output = _git(repo, "ls-files", "--stage", "--", relative)
    if not output:
        return None
    lines = output.splitlines()
    if len(lines) != 1:
        raise ValueError(f"review path has ambiguous index stages: {relative!r}")
    match = re.fullmatch(r"([0-7]{6}) ([0-9a-f]{40,64}) 0\t.+", lines[0])
    if not match:
        raise ValueError(f"cannot parse index entry for {relative!r}: {lines[0]!r}")
    return match.group(1), match.group(2)


def _tree_entry(repo: Path, relative: str) -> tuple[str, str, str] | None:
    output = _git(repo, "ls-tree", "HEAD", "--", relative)
    if not output:
        return None
    lines = output.splitlines()
    if len(lines) != 1:
        raise ValueError(f"review path has ambiguous HEAD tree entries: {relative!r}")
    match = re.fullmatch(
        r"([0-7]{6}) (blob|commit|tree) ([0-9a-f]{40,64})\t.+", lines[0]
    )
    if not match:
        raise ValueError(f"cannot parse HEAD tree entry for {relative!r}: {lines[0]!r}")
    return match.group(1), match.group(2), match.group(3)


def _committed_diff_paths(repo: Path, base: str) -> tuple[str, ...]:
    output = _git(repo, "diff", "--name-only", "--no-renames", f"{base}...HEAD", "--")
    paths = tuple(sorted({line for line in output.splitlines() if line}))
    _, errors = normalized_paths(",".join(paths)) if paths else ((), [])
    if errors:
        raise ValueError("cannot normalize committed diff: " + "; ".join(errors))
    return paths


def _tree_gitlink(repo: Path, relative: str) -> str | None:
    entry = _tree_entry(repo, relative)
    if entry is None or entry[0] != "160000" or entry[1] != "commit":
        return None
    return entry[2]


def scope_fingerprint(repo: Path, base: str, paths: list[str] | tuple[str, ...]) -> tuple[str, str]:
    repo = repo.resolve()
    top = Path(_git(repo, "rev-parse", "--show-toplevel")).resolve()
    if top != repo:
        raise ValueError(f"repository path is ambiguous: {repo} resolves to Git root {top}")
    base_oid = _git(repo, "rev-parse", "--verify", f"{base}^{{commit}}")
    normalized, errors = normalized_paths(",".join(paths))
    if errors:
        raise ValueError("; ".join(errors))

    hasher = hashlib.sha256()
    _feed(hasher, b"unity-harness-review-scope-v4")
    _feed(hasher, base_oid.encode())
    for relative in normalized:
        candidate = repo / relative
        try:
            candidate.parent.resolve().relative_to(repo)
        except ValueError as error:
            raise ValueError(f"review path escapes repository: {relative!r}") from error
        exists_now = candidate.exists() or candidate.is_symlink()
        existed_at_base = _base_has_path(repo, base_oid, relative)
        index_entry = _index_entry(repo, relative)
        tree_entry = _tree_entry(repo, relative)
        if not exists_now and not existed_at_base and index_entry is None:
            raise ValueError(f"review path is absent now and at base: {relative!r}")
        _feed(hasher, relative.encode())
        _feed(hasher, b"head-entry")
        if tree_entry is None:
            _feed(hasher, b"absent")
        else:
            for value in tree_entry:
                _feed(hasher, value.encode())
        _feed(hasher, b"index-entry")
        if index_entry is None:
            _feed(hasher, b"absent")
        else:
            for value in index_entry:
                _feed(hasher, value.encode())
        is_gitlink = (
            (index_entry is not None and index_entry[0] == "160000")
            or (tree_entry is not None and tree_entry[0] == "160000")
        )
        if is_gitlink:
            _feed(hasher, b"gitlink")
            if not exists_now:
                _feed(hasher, b"checkout-absent")
                continue
            child_top = subprocess.run(
                ["git", "-C", str(candidate), "rev-parse", "--show-toplevel"],
                text=True, capture_output=True, check=False,
            )
            child_head = subprocess.run(
                ["git", "-C", str(candidate), "rev-parse", "HEAD"],
                text=True, capture_output=True, check=False,
            )
            if (
                child_top.returncode == 0
                and child_head.returncode == 0
                and Path(child_top.stdout.strip()).resolve() == candidate.resolve()
            ):
                _feed(hasher, b"checkout-head")
                _feed(hasher, child_head.stdout.strip().encode())
            else:
                _feed(hasher, b"checkout-unavailable")
            continue
        if not exists_now:
            _feed(hasher, b"deleted")
            continue
        info = candidate.lstat()
        if stat.S_ISLNK(info.st_mode):
            _feed(hasher, b"symlink")
            _feed(hasher, os.readlink(candidate).encode())
        elif stat.S_ISREG(info.st_mode):
            _feed(hasher, b"executable" if info.st_mode & 0o111 else b"file")
            _feed(hasher, candidate.read_bytes())
        else:
            raise ValueError(f"review path is not a regular file, symlink, or gitlink: {relative!r}")
    return base_oid, hasher.hexdigest()


def validate_outcome(
    text: str,
    *,
    lane: str,
    expected_repositories: dict[str, Path] | None = None,
    required_relations: list[tuple[str, str, str]] | None = None,
) -> list[str]:
    values, errors = parse_outcome_block(text)
    if errors:
        return errors
    readiness = values["Readiness"]
    acceptance = values["Independent acceptance"]
    accept_complete = values["Accept as complete"]
    next_action = values["Next required action"]
    if readiness not in READINESS:
        errors.append(f"invalid Readiness: {readiness!r}")
    if acceptance not in ACCEPTANCE:
        errors.append(f"invalid Independent acceptance: {acceptance!r}")
    if accept_complete not in {"yes", "no"}:
        errors.append("Accept as complete must be 'yes' or 'no'")
    if acceptance in {"pending", "REVISE"}:
        if readiness != "implemented-unverified" or accept_complete != "no":
            errors.append(f"{acceptance} requires implemented-unverified and Accept as complete: no")
        if next_action == "none":
            errors.append(f"{acceptance} requires a concrete next action")
    if accept_complete == "yes":
        if acceptance not in {"PASS", "not-required"}:
            errors.append("Accept as complete: yes requires PASS or not-required")
        if readiness not in {"owner-QA-ready", "release-ready"} or next_action != "none":
            errors.append("Accept as complete: yes requires justified ready state and no next action")

    strict_review = lane in {"high-risk", "release"}
    if strict_review and acceptance == "not-required":
        errors.append(f"{lane} work cannot waive independent acceptance")
    if not strict_review:
        return errors

    lines = text.splitlines()
    reviewer_lines = [line for line in lines if line.startswith("Reviewer context: ")]
    if len(reviewer_lines) != 1 or REVIEWER_RE.fullmatch(reviewer_lines[0]) is None:
        errors.append("high-risk outcome needs one canonical Reviewer context line")
        authored = None
    else:
        authored = REVIEWER_RE.fullmatch(reviewer_lines[0]).group(2)  # type: ignore[union-attr]
    if acceptance in {"PASS", "REVISE"} and authored != "no":
        errors.append(f"{acceptance} requires a reviewer who did not author the diff")

    blockers, blocker_errors = _one_value(lines, "Proof blockers")
    errors.extend(blocker_errors)
    if acceptance == "PASS" and blockers != "none":
        errors.append("PASS cannot coexist with a missing proof gate")

    scopes, scope_errors = parse_scopes(text)
    errors.extend(scope_errors)
    if not scopes:
        errors.append("high-risk outcome needs at least one review scope tuple")
    by_id = {scope.identity: scope for scope in scopes}
    expected_repositories = expected_repositories or {}
    if expected_repositories and set(by_id) != set(expected_repositories):
        errors.append(
            f"review repository denominator mismatch: recorded={sorted(by_id)}, expected={sorted(expected_repositories)}"
        )
    for identity, expected in expected_repositories.items():
        scope = by_id.get(identity)
        if scope and scope.repository.resolve() != expected.resolve():
            errors.append(f"{identity}: repository path does not match expected identity")

    for scope in scopes:
        try:
            committed_paths = _committed_diff_paths(scope.repository, scope.base)
        except (OSError, ValueError) as error:
            errors.append(f"{scope.identity}: cannot resolve committed review diff: {error}")
            continue
        if scope.paths != committed_paths:
            errors.append(
                f"{scope.identity}: scoped paths do not equal committed diff; "
                f"missing={sorted(set(committed_paths) - set(scope.paths))} "
                f"extra={sorted(set(scope.paths) - set(committed_paths))}"
            )

    for parent, gitlink, child in required_relations or []:
        if parent not in by_id or child not in by_id:
            errors.append(f"multi-repository scope omits relation {parent}:{gitlink}:{child}")
            continue
        if gitlink not in by_id[parent].paths:
            errors.append(f"parent scope {parent} omits child gitlink {gitlink}")
            continue
        parent_scope = by_id[parent]
        child_scope = by_id[child]
        try:
            index_entry = _index_entry(parent_scope.repository, gitlink)
            tree_oid = _tree_gitlink(parent_scope.repository, gitlink)
            child_head = _git(child_scope.repository, "rev-parse", "HEAD")
        except (OSError, ValueError) as error:
            errors.append(f"relation {parent}:{gitlink}:{child} could not be resolved: {error}")
            continue
        if index_entry is None or index_entry[0] != "160000" or tree_oid is None:
            errors.append(f"relation {parent}:{gitlink}:{child} is not a committed mode-160000 gitlink")
            continue
        if index_entry[1] != tree_oid or tree_oid != child_head:
            errors.append(
                f"relation {parent}:{gitlink}:{child} OID mismatch: "
                f"index={index_entry[1]} tree={tree_oid} child={child_head}"
            )

    if not errors:
        for scope in scopes:
            try:
                actual_base, actual = scope_fingerprint(scope.repository, scope.base, scope.paths)
            except (OSError, ValueError) as error:
                errors.append(f"{scope.identity}: {error}")
                continue
            if actual_base != scope.base:
                errors.append(f"{scope.identity}: base resolves to {actual_base}, not recorded {scope.base}")
            if f"sha256:{actual}" != scope.fingerprint:
                errors.append(f"{scope.identity}: fingerprint does not match current scoped content")
    return errors


def _expected_repository(value: str) -> tuple[str, Path]:
    if "=" not in value:
        raise argparse.ArgumentTypeError("expected ID=PATH")
    identity, path = value.split("=", 1)
    if not identity or not path:
        raise argparse.ArgumentTypeError("expected ID=PATH")
    return identity, Path(path)


def _relation(value: str) -> tuple[str, str, str]:
    parts = value.split(":", 2)
    if len(parts) != 3 or not all(parts):
        raise argparse.ArgumentTypeError("expected PARENT:GITLINK:CHILD")
    return parts[0], parts[1], parts[2]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    validate = subparsers.add_parser("validate")
    validate.add_argument("record", type=Path)
    validate.add_argument("--lane", required=True, choices=("docs", "ordinary", "high-risk", "release"))
    validate.add_argument("--expected-repository", action="append", default=[], type=_expected_repository)
    validate.add_argument("--require-relation", action="append", default=[], type=_relation)
    fingerprint = subparsers.add_parser("fingerprint")
    fingerprint.add_argument("--id", required=True)
    fingerprint.add_argument("--repo", type=Path, default=Path.cwd())
    fingerprint.add_argument("--base", required=True)
    fingerprint.add_argument("paths", nargs="+")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        if args.command == "fingerprint":
            base, digest = scope_fingerprint(args.repo, args.base, args.paths)
            paths, errors = normalized_paths(",".join(args.paths))
            if errors:
                raise ValueError("; ".join(errors))
            print(f"Review repository: id={args.id}; path={args.repo.resolve()}")
            print(f"Review base: {base}")
            print(f"Review scoped paths: {', '.join(paths)}")
            print(f"Review fingerprint: sha256:{digest}")
            return 0
        expected = dict(args.expected_repository)
        if len(expected) != len(args.expected_repository):
            raise ValueError("duplicate --expected-repository ID")
        errors = validate_outcome(
            args.record.read_text(encoding="utf-8"),
            lane=args.lane,
            expected_repositories=expected,
            required_relations=args.require_relation,
        )
    except (OSError, ValueError) as error:
        errors = [str(error)]
    if errors:
        print("Unity Harness outcome validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("Unity Harness outcome validation passed with exact scoped fingerprints.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
