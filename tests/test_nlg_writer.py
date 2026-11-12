import http.client
import json
import socket
import sys
import threading
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))
import nlg_writer
import server


class OfflineWriterTests(unittest.TestCase):
    def test_academic_templates_preserve_unclear_fragments(self):
        source = "• σκοπός εργασίας η εξέταση μιας πολιτικής\n• προσωπική εμπειρία\n• αξιολόγηση στο ερώτημα πόσο εξηγεί η θεωρία την επιλογή"
        result = nlg_writer.generate(source)
        self.assertEqual(result["text"], "Σκοπός της εργασίας είναι η εξέταση μιας πολιτικής.\n• προσωπική εμπειρία\nΑξιολογείται το ερώτημα: πόσο εξηγεί η θεωρία την επιλογή.")
        self.assertTrue(result["partial"])

    def test_first_person_chronology_names_numbers_and_paragraphs(self):
        source = ("• Το 2020 εργάστηκα στην Αθήνα.\n• Το 2024 συνεργάστηκα με τη Μαρία Παπαδοπούλου.\n"
                  "• Η αμοιβή ήταν 1.500 ευρώ.\n\n• Στη συνέχεια μετακόμισα στην Κύπρο.")
        expected = ("Το 2020 εργάστηκα στην Αθήνα. Το 2024 συνεργάστηκα με τη Μαρία Παπαδοπούλου. "
                    "Η αμοιβή ήταν 1.500 ευρώ.\n\nΣτη συνέχεια μετακόμισα στην Κύπρο.")
        self.assertEqual(nlg_writer.generate(source), {"text": expected, "partial": False})
        # Removing only list markers and line breaks leaves the authored words intact.
        self.assertEqual(expected.replace("\n", " ").split(), source.replace("• ", "").replace("\n", " ").split())

    def test_uncertainty_questions_contradiction_and_fragments(self):
        source = "• Ίσως ήταν στην Πάφο;\n• Δεν ήταν στην Πάφο.\n• ημερομηνία άγνωστη\n  - εξαρτάται από έγκριση\n• Έργο..."
        result = nlg_writer.generate(source)
        self.assertEqual(result["text"], "Ίσως ήταν στην Πάφο; Δεν ήταν στην Πάφο.\n• ημερομηνία άγνωστη\n  - εξαρτάται από έγκριση\n• Έργο...")
        self.assertTrue(result["partial"])

    def test_complete_plain_sentences_and_numbered_list_are_not_rewritten(self):
        source = "Εργάζομαι στην Αθήνα.\nΔιαχειρίζομαι τρία έργα.\n\n1. Πρώτο στοιχείο\n2. Δεύτερο στοιχείο"
        self.assertEqual(nlg_writer.generate(source), {"text": source, "partial": True})
        self.assertEqual(nlg_writer.generate("Αυτό είναι ήδη πλήρες."), {"text": "Αυτό είναι ήδη πλήρες.", "partial": False})

    def test_no_network_or_ollama_access(self):
        with patch.object(socket.socket, "connect", side_effect=AssertionError("network")), \
             patch.object(server.ollama, "generate", side_effect=AssertionError("Ollama")), \
             patch.object(server.ollama, "_request", side_effect=AssertionError("Ollama")):
            self.assertEqual(nlg_writer.generate("- Εργάζομαι τοπικά.\n- Γράφω κείμενα.")["text"], "Εργάζομαι τοπικά. Γράφω κείμενα.")

    def test_invalid_inputs(self):
        for value in (None, "", " \n ", 123, "a" * 40001):
            with self.subTest(value=str(value)[:20]), self.assertRaises(ValueError):
                nlg_writer.generate(value)


class OfflineWriterHttpTests(unittest.TestCase):
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

    def post(self, body, token=server.TOKEN):
        conn = http.client.HTTPConnection("127.0.0.1", self.httpd.server_port, timeout=5)
        try:
            headers = {"Origin": self.origin, "Content-Type": "application/json", "X-Session-Token": token}
            conn.request("POST", "/api/generate", json.dumps(body), headers)
            response = conn.getresponse()
            return response.status, json.loads(response.read())
        finally:
            conn.close()

    def test_nlg_and_argos_do_not_call_ollama(self):
        source = "• Εργάζομαι στην Αθήνα.\n• Ίσως ταξιδέψω στην Κύπρο;"
        with patch.object(server.ollama, "generate", side_effect=AssertionError("Ollama used")), \
             patch.object(server.ollama, "_request", side_effect=AssertionError("Ollama used")), \
             patch.object(server.argos_translation, "translate", return_value="English") as translate:
            status, draft = self.post({"task": "write", "engine": "nlg", "text": source})
            self.assertEqual(status, 200)
            status, english = self.post({"task": "translate", "engine": "argos", "text": draft["text"]})
            self.assertEqual((status, english["text"]), (200, "English"))
            translate.assert_called_once_with(draft["text"])

    def test_engine_boundaries_and_session_security(self):
        with patch.object(server.nlg_writer, "generate") as generate:
            for task, engine in (("translate", "nlg"), ("write", "argos")):
                self.assertEqual(self.post({"task": task, "engine": engine, "text": "κείμενο"})[0], 400)
            self.assertEqual(self.post({"task": "write", "engine": "nlg", "text": "κείμενο"}, token="invalid")[0], 403)
            generate.assert_not_called()

    def test_legacy_ollama_default_still_routes(self):
        with patch.object(server.ollama, "generate", return_value="draft") as generate:
            code, data = self.post({"task": "write", "model": "local", "text": "κείμενο"})
            self.assertEqual((code, data["text"]), (200, "draft"))
            generate.assert_called_once_with("local", "κείμενο", "write")
