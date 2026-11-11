import http.client
import json
import sys
import threading
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))
import ollama
import server


class OllamaTests(unittest.TestCase):
    def test_only_locally_identified_models_are_offered(self):
        data = {"models": [
            {"name": "local:8b", "size": 100},
            {"name": "hosted:20b-cloud", "size": 100},
            {"name": "alias", "size": 100, "remote_model": "remote"},
            {"name": "no-weights", "size": 0},
        ]}
        with patch.object(ollama, "_request", return_value=data):
            self.assertEqual(ollama.local_models(), ["local:8b"])

    def test_incomplete_output_is_not_reported_as_success(self):
        results = [
            {"models": [{"name": "local:8b", "size": 100}]},
            {},
            {"done": True, "done_reason": "length", "message": {"content": "partial"}},
        ]
        with patch.object(ollama, "_request", side_effect=results):
            with self.assertRaises(ollama.OllamaError):
                ollama.generate("local:8b", "συνθετικό", "write")

    def test_remote_show_info_is_rejected(self):
        results = [{"models": [{"name": "local:8b", "size": 100}]}, {"remote_model": "hosted"}]
        with patch.object(ollama, "_request", side_effect=results):
            with self.assertRaises(ollama.OllamaError):
                ollama.generate("local:8b", "συνθετικό", "write")

    def test_reasoning_is_disabled_for_simple_writing(self):
        results = [
            {"models": [{"name": "local:8b", "size": 100}]},
            {},
            {"done": True, "done_reason": "stop", "message": {"content": "draft"}},
        ]
        with patch.object(ollama, "_request", side_effect=results) as request:
            self.assertEqual(ollama.generate("local:8b", "sample", "write"), "draft")
        self.assertFalse(request.call_args.args[1]["think"])


class HttpBoundaryTests(unittest.TestCase):
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

    def request(self, method, path, body=None, headers=None):
        conn = http.client.HTTPConnection("127.0.0.1", self.httpd.server_port, timeout=5)
        try:
            conn.request(method, path, body=body, headers=headers or {})
            response = conn.getresponse()
            return response.status, response.read()
        finally:
            conn.close()

    def test_rejects_foreign_origin_and_dns_rebinding(self):
        body = json.dumps({"model": "local:8b", "text": "sample", "task": "write"})
        headers = {"Content-Type": "application/json", "Origin": "https://example.com",
                   "X-Session-Token": server.TOKEN}
        self.assertEqual(self.request("POST", "/api/generate", body, headers)[0], 403)
        self.assertEqual(self.request("GET", "/", headers={"Host": "attacker.example"})[0], 403)
        headers["Origin"] = self.origin
        headers["X-Session-Token"] = "invalid"
        self.assertEqual(self.request("POST", "/api/generate", body, headers)[0], 403)

    def test_authorized_synthetic_request_preserves_input(self):
        body = json.dumps({"model": "local:8b", "text": "sample", "task": "write"})
        headers = {"Content-Type": "application/json", "Origin": self.origin,
                   "X-Session-Token": server.TOKEN}
        with patch.object(ollama, "generate", return_value="draft") as generate:
            code, result = self.request("POST", "/api/generate", body, headers)
        self.assertEqual(code, 200)
        self.assertEqual(json.loads(result), {"text": "draft"})
        generate.assert_called_once_with("local:8b", "sample", "write")

    def test_unapproved_model_does_not_trigger_chat(self):
        with patch.object(ollama, "_request", return_value={"models": []}) as request:
            with self.assertRaises(ollama.OllamaError):
                ollama.generate("unknown", "sample", "write")
        self.assertEqual(request.call_count, 1)

    def test_large_input_is_rejected_before_inference(self):
        body = json.dumps({"model": "local:8b", "text": "x" * 40001, "task": "write"})
        headers = {"Content-Type": "application/json", "Origin": self.origin,
                   "X-Session-Token": server.TOKEN}
        with patch.object(ollama, "generate") as generate:
            code, _ = self.request("POST", "/api/generate", body, headers)
        self.assertEqual(code, 400)
        generate.assert_not_called()


if __name__ == "__main__":
    unittest.main()
