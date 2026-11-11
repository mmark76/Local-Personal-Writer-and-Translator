import http.client
import json
import sys
import threading
import time
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))
import model_manager
import ollama
import server


class FakeResponse:
    def __init__(self, lines=(), status=200):
        self.lines = list(lines)
        self.status = status

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def readline(self, _limit):
        return self.lines.pop(0) if self.lines else b""


class FakeOllama:
    def __init__(self):
        self.models = [{"name": "local:8b", "size": 3_000_000_000}]
        self.calls = []
        self.progress_seen = threading.Event()
        self.continue_pull = threading.Event()

    def request(self, path, data=None, timeout=15):
        if path == "/api/tags":
            return {"models": list(self.models)}
        if path == "/api/show":
            return {}
        if path == "/api/chat":
            text = "Greek draft" if "Δημιούργησε" in data["messages"][0]["content"] else "English translation"
            return {"done": True, "done_reason": "stop", "message": {"content": text}}
        raise AssertionError(path)

    def open(self, request, timeout=0):
        self.calls.append((request.get_method(), request.full_url))
        body = json.loads(request.data)
        if request.full_url.endswith("/api/delete"):
            self.models = [model for model in self.models if model["name"] != body["model"]]
            return FakeResponse(status=200)
        if request.full_url.endswith("/api/pull"):
            outer = self

            class Stream(FakeResponse):
                def __init__(self):
                    self.step = 0

                def readline(self, _limit):
                    self.step += 1
                    if self.step == 1:
                        return b'{"status":"pulling layer","completed":50,"total":100}\n'
                    if self.step == 2:
                        outer.progress_seen.set()
                        if not outer.continue_pull.wait(3):
                            raise TimeoutError()
                        outer.models.append({"name": body["model"] + ":latest", "size": 200})
                        return b'{"status":"success"}\n'
                    return b""
            return Stream()
        raise AssertionError(request.full_url)


class ModelManagerTests(unittest.TestCase):
    def setUp(self):
        self.fake = FakeOllama()
        self.request_patch = patch.object(ollama, "_request", side_effect=self.fake.request)
        self.opener_patch = patch.object(ollama, "OPENER", self.fake)
        self.request_patch.start()
        self.opener_patch.start()
        self.addCleanup(self.request_patch.stop)
        self.addCleanup(self.opener_patch.stop)
        self.manager = model_manager.ModelManager(threading.Lock())

    def wait_for(self, condition, timeout=3):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if condition():
                return
            time.sleep(0.01)
        self.fail("Timed out waiting for the synthetic model job")

    def test_install_progress_prevents_duplicates_and_refreshes(self):
        self.manager.start("example")
        self.addCleanup(self.fake.continue_pull.set)
        self.wait_for(lambda: self.manager.status()["completed"] == 50)
        self.assertEqual(self.manager.status()["total"], 100)
        with self.assertRaises(model_manager.ModelBusy):
            self.manager.start("example")
        with self.assertRaises(model_manager.ModelBusy):
            self.manager.delete("local:8b")
        self.fake.continue_pull.set()
        self.wait_for(lambda: self.manager.status()["state"] == "completed")
        self.assertEqual([m["name"] for m in model_manager.installed_models()], ["example:latest", "local:8b"])
        self.assertEqual(self.fake.calls[0][0], "POST")

    def test_validate_input_and_reject_already_installed(self):
        for name in ("", "../bad", "https://evil.test/x", "example:cloud", "model;whoami", "host.test/name"):
            with self.subTest(name=name), self.assertRaises(model_manager.ModelError):
                self.manager.start(name)
        with self.assertRaises(model_manager.ModelError):
            self.manager.start("library/local:8b")
        self.assertEqual(self.fake.calls, [])

    def test_accepts_standard_library_model_names(self):
        for name in ("llama3.1:latest", "qwen3.5:9b", "gemma4", "author/model:tag"):
            with self.subTest(name=name):
                self.assertEqual(model_manager.validate_name(name), name)

    def test_delete_only_installed_model_and_refresh(self):
        with self.assertRaises(model_manager.ModelError):
            self.manager.delete("missing")
        self.assertEqual(self.fake.calls, [])
        self.manager.delete("local:8b")
        self.assertEqual(model_manager.installed_models(), [])
        self.assertEqual(self.fake.calls, [("DELETE", ollama.BASE + "/api/delete")])

    def test_pull_error_and_missing_final_success_are_failures(self):
        for lines in ([b'{"error":"not found"}\n'], [b'{"status":"pulling"}\n']):
            with self.subTest(lines=lines), patch.object(self.fake, "open", return_value=FakeResponse(lines)):
                self.manager.start("absent")
                self.wait_for(lambda: self.manager.status()["state"] == "failed")
                if b"not found" in lines[0]:
                    self.assertIn("δεν βρέθηκε", self.manager.status()["status"])
                self.wait_for(lambda: not self.manager._busy.locked())

    def test_ollama_unavailable_is_reported(self):
        with patch.object(ollama, "_request", side_effect=ollama.OllamaError("offline")):
            with self.assertRaises(ollama.OllamaError):
                self.manager.start("model")
        self.assertFalse(self.manager._busy.locked())

    def test_writing_and_translation_still_use_local_models(self):
        self.assertEqual(ollama.generate("local:8b", "σημειώσεις", "write"), "Greek draft")
        self.assertEqual(ollama.generate("local:8b", "ελληνικό κείμενο", "translate"), "English translation")


class ModelManagementHttpTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.httpd = server.Server(("127.0.0.1", 0), server.Handler)
        cls.thread = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.thread.start()
        cls.origin = f"http://127.0.0.1:{cls.httpd.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()
        cls.thread.join()

    def post(self, path, body, origin=None, token=None):
        conn = http.client.HTTPConnection("127.0.0.1", self.httpd.server_port, timeout=5)
        headers = {"Content-Type": "application/json", "Origin": origin or self.origin,
                   "X-Session-Token": token or server.TOKEN}
        try:
            conn.request("POST", path, json.dumps(body), headers)
            response = conn.getresponse()
            return response.status, json.loads(response.read())
        finally:
            conn.close()

    def test_delete_requires_confirmation_and_authorized_origin(self):
        with patch.object(server.MODELS, "delete") as delete:
            code, _ = self.post("/api/model-delete", {"model": "local:8b"})
            self.assertEqual(code, 400)
            code, _ = self.post("/api/model-delete", {"model": "local:8b", "confirmed": True}, origin="https://example.com")
            self.assertEqual(code, 403)
            delete.assert_not_called()
            code, _ = self.post("/api/model-delete", {"model": "local:8b", "confirmed": True})
            self.assertEqual(code, 200)
            delete.assert_called_once_with("local:8b")

    def test_install_rejects_bad_token(self):
        with patch.object(server.MODELS, "start") as start:
            code, _ = self.post("/api/model-install", {"model": "example"}, token="invalid")
            self.assertEqual(code, 403)
            code, _ = self.post("/api/model-install", {"model": "example"}, token="é")
            self.assertEqual(code, 403)
            start.assert_not_called()


if __name__ == "__main__":
    unittest.main()
