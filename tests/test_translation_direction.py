import http.client
import json
import sys
import threading
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))
import argos_translation
import server

class DirectionTests(unittest.TestCase):
    def test_pair_detection_is_direction_specific(self):
        pkg = Mock()
        pkg.get_installed_packages.return_value = [SimpleNamespace(from_code="el", to_code="en")]
        with patch.object(argos_translation, "_package", return_value=pkg):
            self.assertTrue(argos_translation.available("el", "en")["installed"])
            self.assertFalse(argos_translation.available("en", "el")["installed"])
            self.assertFalse(argos_translation.available("en", "fr")["available"])

    def test_reverse_prompt_selects_correct_languages(self):
        responses = [{"models": [{"name": "local", "size": 1}]}, {},
                     {"done": True, "done_reason": "stop", "message": {"content": "Γεια"}}]
        with patch.object(server.ollama, "_request", side_effect=responses) as request:
            self.assertEqual(server.ollama.generate("local", "Hello", "translate", "en-el"), "Γεια")
            self.assertIn("English text into Greek", request.call_args.args[1]["messages"][0]["content"])

class DirectionHttpTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.httpd = server.Server(("127.0.0.1", 0), server.Handler)
        cls.thread = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown(); cls.httpd.server_close(); cls.thread.join()

    def post(self, data):
        conn = http.client.HTTPConnection("127.0.0.1", self.httpd.server_port, timeout=5)
        try:
            conn.request("POST", "/api/generate", json.dumps(data), {"Content-Type":"application/json", "Origin":f"http://127.0.0.1:{self.httpd.server_port}", "X-Session-Token":server.TOKEN})
            response = conn.getresponse()
            return response.status, json.loads(response.read())
        finally:
            conn.close()

    def test_routes_reverse_without_requiring_a_model_for_argos(self):
        with patch.object(server.argos_translation, "translate", return_value="Γεια") as translate:
            status, data = self.post({"task":"translate", "engine":"argos", "direction":"en-el", "text":"Hello"})
            self.assertEqual((status, data["text"]), (200, "Γεια"))
            translate.assert_called_once_with("Hello", "en", "el")

    def test_stop_endpoint_requires_valid_session_and_origin(self):
        conn = http.client.HTTPConnection("127.0.0.1", self.httpd.server_port, timeout=5)
        try:
            with patch.object(server.JOBS, "cancel") as cancel:
                conn.request("POST", "/api/generation-cancel", headers={"Origin": "https://example.com", "X-Session-Token": server.TOKEN})
                response = conn.getresponse()
                self.assertEqual(response.status, 403)
                response.read()
                cancel.assert_not_called()
        finally:
            conn.close()

    def test_invalid_direction_rejected(self):
        with patch.object(server.argos_translation, "translate") as translate:
            status, _ = self.post({"task":"translate", "engine":"argos", "direction":"en-fr", "text":"Hello"})
            self.assertEqual(status, 400)
            translate.assert_not_called()
