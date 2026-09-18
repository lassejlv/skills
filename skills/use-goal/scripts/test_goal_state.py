#!/usr/bin/env python3
"""Behavioral regression tests for goal persistence, using disposable workspaces."""

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import goal_state as state


SCRIPT = Path(__file__).with_name("goal_state.py")


def goal(title="Fix refunds"):
    return {
        "title": title,
        "objective": "Refund totals follow the currency rule.",
        "agent": "test-agent",
        "run_id": "test-run-1",
        "criteria": [{"text": "Negative half-cent cases pass.", "done": False, "evidence": []}],
        "next_action": "Inspect the refund calculation.",
    }


def note(note_id="refund-tests"):
    return {"id": note_id, "kind": "fact", "text": "Refund tests live in checkout.",
            "evidence": ["Inspected checkout test target."], "valid_when": "Checkout still owns refunds.",
            "verified": None}


class GoalStateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.workspace = Path(self.temp.name).resolve()
        self.store = state.Store(self.workspace)
        self.current_path = self.workspace / ".use-goal/current.md"

    def cli(self, *args, payload=None, success=True):
        result = subprocess.run([sys.executable, str(SCRIPT), "--workspace", str(self.workspace), *args],
                                input=json.dumps(payload) if payload is not None else None,
                                text=True, capture_output=True)
        self.assertEqual(result.returncode, 0 if success else 1, result.stderr)
        return json.loads(result.stdout if success else result.stderr)

    def test_read_only_missing_state_does_not_create_files(self):
        for command, expected in (("read", None), ("memory", None), ("history", []), ("previous", None)):
            self.assertEqual(self.cli(command), expected)
        self.assertFalse(self.store.root.exists())

    def test_cli_lifecycle_and_metadata_round_trip(self):
        payload = goal('Quotes: "hello" — Æøå\n---\nsecond line\rcarriage')
        payload["extensions"] = {"harness": {"enabled": True, "counter": 1}}
        first = self.cli("start", "--input", "-", payload=payload)
        self.assertEqual(self.cli("read"), first)
        self.assertTrue(self.current_path.read_text().startswith("---\nschema_version: 1\n"))
        self.assertEqual(first["criteria_done"], 0)
        self.assertEqual(first["criteria_total"], 1)
        self.assertTrue(state.timestamp(first["started"]))
        paused = self.cli("checkpoint", "--goal-id", first["id"], "--expected-revision", "1", "--input", "-", payload={"status": "paused"})
        resumed = self.cli("checkpoint", "--goal-id", first["id"], "--expected-revision", "2", "--input", "-", payload={"status": "active", "run_id": "test-run-2"})
        self.assertEqual(paused["status"], "paused")
        self.assertEqual(resumed["id"], first["id"])
        self.assertEqual(resumed["started"], first["started"])
        self.assertEqual(resumed["revision"], 3)
        self.assertEqual(resumed["extensions"], payload["extensions"])

    def test_stale_revision_and_old_goal_id_cannot_overwrite(self):
        first = self.store.start(goal())
        second = self.store.checkpoint({"progress": ["Located the bug."]}, first["id"], 1)
        before = self.current_path.read_bytes()
        with self.assertRaisesRegex(state.StateError, "Stale"):
            self.store.checkpoint({"status": "paused"}, first["id"], 1)
        self.assertEqual(self.current_path.read_bytes(), before)
        successor = self.store.start(goal("Restore health"), True, first["id"], second["revision"])
        with self.assertRaisesRegex(state.StateError, "Stale"):
            self.store.checkpoint({"status": "paused"}, first["id"], successor["revision"])
        self.assertEqual(self.store.read("current.md"), successor)

    def test_yaml_harness_sees_identical_metadata(self):
        try:
            import yaml
        except ImportError:
            self.skipTest("Optional YAML interoperability check needs the repository's PyYAML validator dependency.")
        payload = goal('Æøå 🚀 "quotes"\n---\n\r\u0085\u007f\u2028\u2029')
        payload["extensions"] = {"measurements": [1e-9, 1e20, -2e-12, 3.5e20, 42, True, None],
                                 "literal": '"1e+20" and \\1e-9 stay text'}
        data = self.store.start(payload)
        memory = self.store.remember([dict(note(), text="Remember 🚀\u2028next")], data["id"], 0)
        for filename, expected in (("current.md", data), ("memory.md", memory)):
            with self.store.path(filename).open(encoding="utf-8", newline="") as handle:
                header = handle.read().split("---\n", 2)[1]
            self.assertEqual(yaml.safe_load(header), expected)
            self.assertEqual(self.store.read(filename), expected)

    def test_replacement_racing_with_clear_requires_fresh_intent(self):
        first = self.store.start(goal())
        self.store.clear(first["id"], 1)
        with self.assertRaisesRegex(state.StateError, "no longer exists"):
            self.store.start(goal("Late replacement"), True, first["id"], 1)
        self.assertIsNone(self.store.read("current.md"))

    def test_input_rejects_duplicate_keys_and_nonfinite_numbers(self):
        for raw in ('{"status":"active","status":"completed"}', '{"extensions":{"score":NaN}}', '{"criteria":[{"done":false,"done":true}]}'):
            with self.subTest(raw=raw), self.assertRaises(state.StateError):
                state.decode(raw)

    def test_memory_verification_requires_an_actual_utc_timestamp(self):
        first = self.store.start(goal())
        for invalid in ("2026-09-18Z", "2026-13-18T00:00:00Z", "yesterday", "2026-09-18T12:00:00+02:00"):
            with self.subTest(invalid=invalid), self.assertRaisesRegex(state.StateError, "verification timestamp"):
                self.store.remember([dict(note(), verified=invalid)], first["id"], 0)
        self.assertIsNone(self.store.read("memory.md"))

    def test_start_refuses_replacement_and_invalid_new_keeps_history_unchanged(self):
        first = self.store.start(goal())
        with self.assertRaisesRegex(state.StateError, "already exists"):
            self.store.start(goal("Other task"))
        with self.assertRaises(state.StateError):
            self.store.start({"title": "Incomplete"}, True, first["id"], 1)
        self.assertEqual(self.store.read("current.md"), first)
        self.assertEqual(self.store.history(), [])

    def test_completion_requires_evidence_and_is_terminal(self):
        first = self.store.start(goal())
        criteria = deepcopy(first["criteria"])
        with self.assertRaisesRegex(state.StateError, "Completion requires"):
            self.store.checkpoint({"status": "completed"}, first["id"], 1)
        criteria[0]["done"] = True
        with self.assertRaisesRegex(state.StateError, "needs evidence"):
            self.store.checkpoint({"criteria": criteria}, first["id"], 1)
        criteria[0]["evidence"] = ["Refund boundary test passed."]
        done = self.store.checkpoint({"status": "completed", "criteria": criteria,
                                     "next_action": "None; all acceptance criteria are verified."}, first["id"], 1)
        self.assertTrue(state.timestamp(done["finished"]))
        self.assertEqual(done["criteria_done"], done["criteria_total"])
        with self.assertRaisesRegex(state.StateError, "immutable"):
            self.store.checkpoint({"status": "active"}, done["id"], 2)

    def test_blocker_and_runtime_limit_do_not_claim_completion(self):
        first = self.store.start(goal())
        with self.assertRaisesRegex(state.StateError, "need a blocker"):
            self.store.checkpoint({"status": "blocked"}, first["id"], 1)
        limited = self.store.checkpoint({"stop_reason": "context_limit"}, first["id"], 1)
        self.assertEqual(limited["status"], "active")
        self.assertIsNone(limited["finished"])
        blocker = {"reason": "Cannot verify deployed refunds without registry access.",
                   "attempts": ["Verified local behavior; observed registry authentication failure."],
                   "unblock_action": "Provide registry access through the approved environment."}
        blocked = self.store.checkpoint({"status": "blocked", "blocker": blocker}, first["id"], 2)
        resumed = self.store.checkpoint({"status": "active", "blocker": None, "stop_reason": None}, first["id"], 3)
        self.assertEqual(blocked["blocker"], blocker)
        self.assertIsNone(resumed["blocker"])

    def test_memory_upsert_preserves_other_notes_and_checks_its_own_revision(self):
        first = self.store.start(goal())
        memory = self.store.remember([note(), note("refund-rule")], first["id"], 0)
        updated_note = dict(note(), text="Refund tests moved to money.")
        memory = self.store.remember([updated_note], first["id"], memory["revision"])
        self.assertEqual(len(memory["entries"]), 2)
        self.assertEqual(memory["entries"][0]["text"], updated_note["text"])
        self.assertEqual(memory["entries"][0]["source_goal_id"], first["id"])
        with self.assertRaisesRegex(state.StateError, "Stale memory"):
            self.store.remember([note()], first["id"], 1)
        self.assertEqual(self.store.read("memory.md"), memory)
        self.assertEqual(self.store.read("current.md")["revision"], 1)

    def test_previous_goals_survive_replace_clear_and_restart(self):
        untouched = self.workspace / "work.txt"
        untouched.write_text("User work")
        first = self.store.start(goal())
        self.store.remember([note()], first["id"], 0)
        memory_bytes = self.store.path("memory.md").read_bytes()
        second = self.store.start(goal("Restore health"), True, first["id"], 1)
        self.assertEqual(second["previous_goal_id"], first["id"])
        prior = self.cli("previous")
        self.assertEqual(prior["status"], "active")
        self.assertEqual(prior["archive_reason"], "replaced")
        old_archive = self.store.path(f"history/{first['id']}.md").read_bytes()
        self.store.clear(second["id"], 1)
        self.assertFalse(self.current_path.exists())
        self.assertIsNone(self.store.clear(second["id"], 1))
        self.assertEqual(self.store.history()[0]["archive_reason"], "cleared")
        third = self.store.start(goal("Return to refunds"))
        self.assertEqual(third["previous_goal_id"], second["id"])
        self.assertEqual(self.store.path(f"history/{first['id']}.md").read_bytes(), old_archive)
        self.assertEqual(self.store.path("memory.md").read_bytes(), memory_bytes)
        self.assertEqual(untouched.read_text(), "User work")

    def test_failed_atomic_rename_preserves_checkpoint(self):
        first = self.store.start(goal())
        before = self.current_path.read_bytes()
        with patch.object(state.os, "replace", side_effect=OSError("simulated disk error")):
            with self.assertRaises(OSError):
                self.store.checkpoint({"status": "paused"}, first["id"], 1)
        self.assertEqual(self.current_path.read_bytes(), before)
        self.assertEqual(list(self.store.root.glob(".tmp-*")), [])
        self.store.checkpoint({"status": "paused"}, first["id"], 1)

    def test_interrupted_replacement_keeps_current_and_retry_refreshes_archive(self):
        first = self.store.start(goal())
        original_write = self.store.write

        def fail_current(relative, data):
            if relative == "current.md":
                raise OSError("interrupted after archive")
            original_write(relative, data)

        with patch.object(self.store, "write", side_effect=fail_current):
            with self.assertRaises(OSError):
                self.store.start(goal("Other task"), True, first["id"], 1)
        self.assertEqual(self.store.read("current.md"), first)
        self.assertEqual(self.store.history(), [])
        self.assertTrue(self.store.path(f"history/{first['id']}.md").exists())
        self.store.checkpoint({"progress": ["Observed the interrupted replacement."]}, first["id"], 1)
        self.store.start(goal("Other task"), True, first["id"], 2)
        self.assertEqual(self.store.history()[0]["revision"], 2)

    def test_failed_archive_prevents_clear(self):
        first = self.store.start(goal())
        with patch.object(self.store, "archive", side_effect=OSError("disk full")):
            with self.assertRaises(OSError):
                self.store.clear(first["id"], 1)
        self.assertEqual(self.store.read("current.md"), first)

    def test_writer_lock_blocks_other_process_and_releases_after_exit(self):
        first = self.store.start(goal())
        args = ("checkpoint", "--goal-id", first["id"], "--expected-revision", "1", "--input", "-")
        with self.store.lock():
            error = self.cli(*args, payload={"status": "paused"}, success=False)
            self.assertIn("writer holds", error["error"])
        self.assertEqual(self.cli(*args, payload={"status": "paused"})["status"], "paused")
        child = subprocess.Popen([sys.executable, "-c",
                                  "import fcntl,sys,time; f=open(sys.argv[1], 'a'); fcntl.flock(f, fcntl.LOCK_EX); print('locked', flush=True); time.sleep(30)",
                                  str(self.store.path(".lock"))], stdout=subprocess.PIPE, text=True)
        try:
            self.assertEqual(child.stdout.readline().strip(), "locked")
        finally:
            child.kill()
            child.wait(timeout=5)
            child.stdout.close()
        self.store.checkpoint({"status": "active"}, first["id"], 2)

    def test_corrupt_unknown_version_and_manual_edits_are_preserved(self):
        first = self.store.start(goal())
        original = self.current_path.read_text()
        for raw in ("Unrelated user notes\n", original.replace("schema_version: 1", "schema_version: 99", 1),
                    original.replace("---\n", "---\nkind: \"goal\"\n", 1),
                    original + "\nManual unsaved detail.\n"):
            with self.subTest(raw=raw[:40]):
                self.current_path.write_text(raw)
                with self.assertRaises(state.StateError):
                    self.store.checkpoint({"status": "paused"}, first["id"], 1)
                self.assertEqual(self.current_path.read_text(), raw)

    def test_symlink_state_and_cross_workspace_records_are_rejected(self):
        self.store.start(goal())
        other = self.workspace / "other"
        other.mkdir()
        other_store = state.Store(other)
        other_store.root.mkdir()
        other_store.path("current.md").write_bytes(self.current_path.read_bytes())
        with self.assertRaisesRegex(state.StateError, "another workspace"):
            other_store.read("current.md")
        other_store.path("current.md").unlink()
        other_store.path("current.md").symlink_to(self.current_path)
        with self.assertRaisesRegex(state.StateError, "symlink"):
            other_store.read("current.md")

    def test_legacy_migration_preserves_exact_backup_and_unknown_started_time(self):
        raw = "# Current Goal\n\n" + "\n\n".join(f"## {heading}\n{body}" for heading, body in (
            ("Objective", "Fix refunds."), ("Status", "paused"),
            ("Definition of done", "- [ ] Negative half-cent cases pass."), ("Constraints", "None."),
            ("Progress", "None."), ("Evidence", "None."),
            ("Next action", "Inspect the refund calculation."), ("Blocker", "None."))) + "\n"
        self.store.root.mkdir()
        self.current_path.write_text(raw)
        digest = hashlib.sha256(raw.encode()).hexdigest()
        with self.assertRaisesRegex(state.StateError, "changed"):
            self.store.migrate(dict(goal(), status="paused"), "outdated")
        with self.assertRaisesRegex(state.StateError, "preserve the legacy status"):
            self.store.migrate(goal(), digest)
        migrated = self.store.migrate(dict(goal(), status="paused"), digest)
        self.assertIsNone(migrated["started"])
        self.assertEqual(migrated["status"], "paused")
        self.assertEqual(self.store.path(f"history/legacy-{digest}.md").read_bytes(), raw.encode())
        self.assertEqual(self.store.read("current.md"), migrated)
        self.assertEqual(self.store.history(), [])


if __name__ == "__main__":
    unittest.main()
