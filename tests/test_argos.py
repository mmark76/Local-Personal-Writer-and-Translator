import json
import sys
import threading
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))
import argos_translation as argos
import server
from test_local_app import HttpBoundaryTests


class ArgosAdapterTests(unittest.TestCase):
    def test_missing_dependency_and_empty_input(self):
        with patch.object(argos, "_package", side_effect=argos.ArgosError("missing")):
            self.assertFalse(argos.available()["available"])
            with self.assertRaises(argos.ArgosError):
                argos.translate("δοκιμή")
        for value in ("", "  ", None, "a" * 40001):
            with self.assertRaises(argos.ArgosError):
                argos.translate(value)

    def test_detects_pair_and_avoids_reinstall(self):
        pkg = Mock()
        pkg.get_installed_packages.return_value = [SimpleNamespace(from_code="el", to_code="en")]
        with patch.object(argos, "_package", return_value=pkg):
            self.assertEqual(argos.available(), {"available": True, "installed": True})
            with self.assertRaises(argos.ArgosError):
                argos.PackageManager(threading.Lock()).start()
        pkg.update_package_index.assert_not_called()

    def test_install_success_and_failure_are_verified(self):
        pkg = Mock()
        candidate = SimpleNamespace(from_code="el", to_code="en", download=Mock(return_value="path"))
        pkg.get_available_packages.return_value = [candidate]
        manager = argos.PackageManager(threading.Lock())
        with patch.object(argos, "_package", return_value=pkg), patch.object(argos, "available", return_value={"installed": True}):
            manager._busy.acquire()
            manager._install()
        self.assertEqual(manager.status()["state"], "completed")
        pkg.install_from_path.assert_called_once_with("path")
        pkg.update_package_index.side_effect = OSError("offline")
        with patch.object(argos, "_package", return_value=pkg):
            manager._busy.acquire()
            manager._install()
        self.assertEqual(manager.status()["state"], "failed")


class ArgosHttpTests(HttpBoundaryTests):
    def test_engine_switch_and_source_preservation(self):
        headers = {"Content-Type": "application/json", "Origin": self.origin, "X-Session-Token": server.TOKEN}
        source = "Η Μαρία στην Αθήνα.\n\nΤο 2024."
        with patch.object(argos, "translate", return_value="English") as trans, patch.object(server.ollama, "generate", return_value="LLM") as llm:
            code, data = self.request("POST", "/api/generate", json.dumps({"task": "translate", "engine": "argos", "text": source}), headers)
            self.assertEqual((code, json.loads(data)["text"]), (200, "English"))
            trans.assert_called_once_with(source)
            llm.assert_not_called()
            code, data = self.request("POST", "/api/generate", json.dumps({"task": "translate", "engine": "ollama", "model": "local", "text": source}), headers)
            self.assertEqual((code, json.loads(data)["text"]), (200, "LLM"))
            llm.assert_called_once_with("local", source, "translate")
            code, _ = self.request("POST", "/api/generate", json.dumps({"task": "write", "engine": "argos", "text": source}), headers)
            self.assertEqual(code, 400)

    def test_install_needs_confirmation_and_origin(self):
        headers = {"Content-Type": "application/json", "Origin": self.origin, "X-Session-Token": server.TOKEN}
        with patch.object(server.ARGOS, "start") as start:
            self.assertEqual(self.request("POST", "/api/argos-install", "{}", headers)[0], 400)
            headers["Origin"] = "https://example.com"
            self.assertEqual(self.request("POST", "/api/argos-install", '{"confirmed":true}', headers)[0], 403)
            start.assert_not_called()
