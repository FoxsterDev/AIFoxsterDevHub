#!/usr/bin/env python3
"""Adversarial tests for exact Unity Harness review scopes."""

from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path

from unity_harness_review import ReviewScope, parse_scopes, scope_fingerprint, validate_outcome


def git(repo: Path, *args: str) -> str:
    result = subprocess.run(["git", *args], cwd=repo, text=True, capture_output=True, check=True)
    return result.stdout.strip()


class HarnessReviewTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory(prefix="unity-harness-review-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)

    def make_repo(self, name: str = "repo") -> tuple[Path, str]:
        repo = self.root / name
        repo.mkdir()
        git(repo, "init", "-q")
        git(repo, "config", "user.name", "Harness Test")
        git(repo, "config", "user.email", "harness@example.invalid")
        (repo / "tracked.txt").write_text("base\n", encoding="utf-8")
        git(repo, "add", "tracked.txt")
        git(repo, "commit", "-q", "-m", "base")
        base = git(repo, "rev-parse", "HEAD")
        (repo / "tracked.txt").write_text("reviewed change\n", encoding="utf-8")
        git(repo, "add", "tracked.txt")
        git(repo, "commit", "-q", "-m", "reviewed change")
        return repo, base

    def scope(self, identity: str, repo: Path, base: str, paths: list[str]) -> ReviewScope:
        resolved, digest = scope_fingerprint(repo, base, paths)
        return ReviewScope(identity, repo, resolved, tuple(paths), f"sha256:{digest}")

    def record(
        self,
        scopes: list[ReviewScope],
        *,
        readiness: str = "owner-QA-ready",
        acceptance: str = "PASS",
        complete: str = "yes",
        action: str = "none",
        authored: str = "no",
        blockers: str = "none",
    ) -> str:
        lines = [
            f"Readiness: {readiness}",
            f"Independent acceptance: {acceptance}",
            f"Accept as complete: {complete}",
            f"Next required action: {action}",
            "Reviewer context: fresh-test-reviewer; reviewer authored the reviewed diff: " + authored + ".",
            f"Proof blockers: {blockers}",
        ]
        for scope in scopes:
            lines.extend(
                (
                    f"Review repository: id={scope.identity}; path={scope.repository}",
                    f"Review base: {scope.base}",
                    f"Review scoped paths: {', '.join(scope.paths)}",
                    f"Review fingerprint: {scope.fingerprint}",
                )
            )
        return "\n".join(lines) + "\n"

    def test_fresh_non_author_pass_is_bound_to_scope(self) -> None:
        repo, base = self.make_repo()
        (repo / "tracked.txt").write_text("changed\n", encoding="utf-8")
        scope = self.scope("root", repo, base, ["tracked.txt"])
        self.assertEqual(
            validate_outcome(
                self.record([scope]), lane="high-risk", expected_repositories={"root": repo}
            ),
            [],
        )

    def test_self_authored_or_author_pass_fails(self) -> None:
        repo, base = self.make_repo()
        scope = self.scope("root", repo, base, ["tracked.txt"])
        errors = validate_outcome(self.record([scope], authored="yes"), lane="high-risk")
        self.assertTrue(any("did not author" in error for error in errors))

    def test_pending_and_revise_cannot_be_ready_or_complete(self) -> None:
        repo, base = self.make_repo()
        scope = self.scope("root", repo, base, ["tracked.txt"])
        for acceptance in ("pending", "REVISE"):
            errors = validate_outcome(
                self.record([scope], acceptance=acceptance), lane="high-risk"
            )
            self.assertTrue(any("implemented-unverified" in error for error in errors))

    def test_pass_cannot_hide_a_proof_blocker(self) -> None:
        repo, base = self.make_repo()
        scope = self.scope("root", repo, base, ["tracked.txt"])
        errors = validate_outcome(
            self.record([scope], blockers="Unity consumer compile missing"), lane="high-risk"
        )
        self.assertTrue(any("missing proof gate" in error for error in errors))

    def test_in_scope_mutation_fails_but_unrelated_dirty_path_does_not(self) -> None:
        repo, base = self.make_repo()
        scope = self.scope("root", repo, base, ["tracked.txt"])
        record = self.record([scope])
        (repo / "unrelated.txt").write_text("owner dirt\n", encoding="utf-8")
        self.assertEqual(validate_outcome(record, lane="high-risk"), [])
        (repo / "tracked.txt").write_text("mutated\n", encoding="utf-8")
        errors = validate_outcome(record, lane="high-risk")
        self.assertTrue(any("fingerprint" in error for error in errors))

    def test_executable_bit_symlink_target_and_deletion_are_fingerprinted(self) -> None:
        repo, base = self.make_repo()
        executable = repo / "run.sh"
        executable.write_text("#!/bin/sh\n", encoding="utf-8")
        executable.chmod(0o644)
        link = repo / "link"
        link.symlink_to("tracked.txt")
        git(repo, "add", "run.sh", "link")
        git(repo, "commit", "-q", "-m", "add modes")
        (repo / "tracked.txt").unlink()
        scope = self.scope("root", repo, base, ["link", "run.sh", "tracked.txt"])
        record = self.record([scope])
        self.assertEqual(validate_outcome(record, lane="high-risk"), [])
        executable.chmod(0o755)
        self.assertTrue(any("fingerprint" in e for e in validate_outcome(record, lane="high-risk")))
        executable.chmod(0o644)
        link.unlink()
        link.symlink_to("run.sh")
        self.assertTrue(any("fingerprint" in e for e in validate_outcome(record, lane="high-risk")))

    def test_invalid_paths_duplicate_paths_and_missing_base_fail(self) -> None:
        repo, base = self.make_repo()
        for paths in (["../tracked.txt"], ["/tracked.txt"], ["tracked.txt", "tracked.txt"]):
            with self.assertRaises(ValueError):
                scope_fingerprint(repo, base, paths)
        with self.assertRaises(ValueError):
            scope_fingerprint(repo, "0" * 40, ["tracked.txt"])

    def test_repository_identity_is_exact(self) -> None:
        repo, base = self.make_repo()
        other, _ = self.make_repo("other")
        scope = self.scope("root", repo, base, ["tracked.txt"])
        errors = validate_outcome(
            self.record([scope]), lane="high-risk", expected_repositories={"root": other}
        )
        self.assertTrue(any("repository path" in error for error in errors))

    def test_recorded_repository_identity_must_be_absolute(self) -> None:
        repo, base = self.make_repo()
        scope = self.scope("root", repo, base, ["tracked.txt"])
        relative = self.record([scope]).replace(
            f"Review repository: id=root; path={repo}",
            "Review repository: id=root; path=.",
        )
        _, errors = parse_scopes(relative)
        self.assertTrue(any("must be absolute" in error for error in errors))

    def test_multi_repo_scope_cannot_omit_child_or_parent_gitlink(self) -> None:
        parent, parent_base = self.make_repo("parent")
        child, child_base = self.make_repo("child")
        child_head = git(child, "rev-parse", "HEAD")
        (parent / "child-link").symlink_to(child, target_is_directory=True)
        git(
            parent,
            "update-index",
            "--add",
            "--cacheinfo",
            f"160000,{child_head},child-link",
        )
        git(parent, "commit", "-q", "-m", "add child gitlink")
        parent_scope = self.scope("root", parent, parent_base, ["child-link", "tracked.txt"])
        child_scope = self.scope("child", child, child_base, ["tracked.txt"])
        expected = {"root": parent, "child": child}
        relation = [("root", "child-link", "child")]
        self.assertEqual(
            validate_outcome(
                self.record([parent_scope, child_scope]), lane="high-risk",
                expected_repositories=expected, required_relations=relation,
            ),
            [],
        )
        errors = validate_outcome(
            self.record([parent_scope]), lane="high-risk",
            expected_repositories=expected, required_relations=relation,
        )
        self.assertTrue(any("denominator" in error or "omits relation" in error for error in errors))
        bad_parent = self.scope("root", parent, parent_base, ["tracked.txt"])
        errors = validate_outcome(
            self.record([bad_parent, child_scope]), lane="high-risk",
            expected_repositories=expected, required_relations=relation,
        )
        self.assertTrue(any("omits child gitlink" in error for error in errors))

    def test_parent_gitlink_index_mutation_invalidates_fingerprint(self) -> None:
        parent, parent_base = self.make_repo("gitlink-parent")
        child, _ = self.make_repo("gitlink-child")
        child_head = git(child, "rev-parse", "HEAD")
        (parent / "child-link").symlink_to(child, target_is_directory=True)
        git(
            parent,
            "update-index",
            "--add",
            "--cacheinfo",
            f"160000,{child_head},child-link",
        )
        git(parent, "commit", "-q", "-m", "add child gitlink")
        scope = self.scope("root", parent, parent_base, ["child-link", "tracked.txt"])
        record = self.record([scope])
        self.assertEqual(validate_outcome(record, lane="high-risk"), [])

        git(
            parent,
            "update-index",
            "--cacheinfo",
            f"160000,{'1' * 40},child-link",
        )
        errors = validate_outcome(record, lane="high-risk")
        self.assertTrue(any("fingerprint" in error for error in errors))

    def test_committed_scope_cannot_omit_an_ordinary_changed_file(self) -> None:
        repo, base = self.make_repo("omitted-file")
        (repo / "second.txt").write_text("second\n", encoding="utf-8")
        git(repo, "add", "second.txt")
        git(repo, "commit", "-q", "-m", "second change")
        incomplete = self.scope("root", repo, base, ["tracked.txt"])
        errors = validate_outcome(self.record([incomplete]), lane="high-risk")
        self.assertTrue(any("scoped paths do not equal committed diff" in error for error in errors))

    def test_outcome_block_must_start_at_line_one(self) -> None:
        repo, base = self.make_repo()
        scope = self.scope("root", repo, base, ["tracked.txt"])
        errors = validate_outcome("# heading\n" + self.record([scope]), lane="high-risk")
        self.assertTrue(any("line 1" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
