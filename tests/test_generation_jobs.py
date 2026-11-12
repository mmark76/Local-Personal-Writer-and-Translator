import sys
import threading
import time
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))
import generation_jobs


def fake_worker(send, task, engine, model, text, direction):
    if text == "slow":
        time.sleep(20)
    send.send({"state": "completed", "text": text})
    send.close()


class GenerationJobsTests(unittest.TestCase):
    def wait_terminal(self, manager):
        deadline = time.monotonic() + 15
        while time.monotonic() < deadline:
            job = manager.status()
            if job["state"] not in ("running", "stopping"):
                return job
            time.sleep(.05)
        self.fail("Generation job did not reach a terminal state")

    def test_cancel_releases_lock_and_following_job_completes(self):
        busy = threading.Lock()
        manager = generation_jobs.GenerationJobs(busy)
        with patch.object(generation_jobs, "_run", fake_worker):
            first = manager.start("write", "ollama", "local", "slow", "el-en")
            self.assertFalse(manager.cancel("other-job"))
            self.assertTrue(manager.cancel(first["id"]))
            self.assertEqual(self.wait_terminal(manager)["state"], "cancelled")
            self.assertFalse(busy.locked())
            manager.start("write", "ollama", "local", "next", "el-en")
            self.assertEqual(self.wait_terminal(manager)["text"], "next")
            self.assertEqual(manager.status(first["id"])["state"], "cancelled")

    def test_large_result_does_not_deadlock_pipe(self):
        manager = generation_jobs.GenerationJobs(threading.Lock())
        content = "x" * 300000
        with patch.object(generation_jobs, "_run", fake_worker):
            manager.start("write", "ollama", "local", content, "el-en")
            self.assertEqual(self.wait_terminal(manager)["text"], content)
