"""Minimal loopback-only server; text remains in the browser session."""
import json
from pathlib import Path
import secrets
import socket
import sys
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import ollama
import model_manager
import argos_translation
import nlg_writer

STATIC = Path(__file__).resolve().parent / "static"
TOKEN = secrets.token_urlsafe(32)
BUSY = threading.Lock()
MODELS = model_manager.ModelManager(BUSY)
ARGOS = argos_translation.PackageManager(BUSY)
MAX_INPUT = 40_000
FILES = {"/": ("index.html", "text/html; charset=utf-8"),
         "/app.js": ("app.js", "text/javascript; charset=utf-8"),
         "/models.js": ("models.js", "text/javascript; charset=utf-8"),
         "/style.css": ("style.css", "text/css; charset=utf-8")}


class Server(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = False

    def server_bind(self):
        if hasattr(socket, "SO_EXCLUSIVEADDRUSE"):
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
        super().server_bind()


class Handler(BaseHTTPRequestHandler):
    server_version = "LocalWriter"
    sys_version = ""

    def log_message(self, *_args):
        pass

    def allowed_host(self):
        return self.headers.get("Host") == f"127.0.0.1:{self.server.server_port}"

    def allowed_token(self):
        value = self.headers.get("X-Session-Token", "")
        return value.isascii() and secrets.compare_digest(value, TOKEN)

    def reject_post(self):
        # Consume only a small, declared body so Windows can deliver the error
        # response without resetting a connection that still has unread input.
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if 0 < size <= 200_000:
                previous_timeout = self.connection.gettimeout()
                try:
                    self.connection.settimeout(2)
                    self.rfile.read(size)
                finally:
                    self.connection.settimeout(previous_timeout)
        except (ValueError, OSError):
            pass
        return self.respond(403, {"error": "Η αίτηση δεν επιτρέπεται."})

    def respond(self, status, data, content_type="application/json; charset=utf-8"):
        raw = data if isinstance(data, bytes) else json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "default-src 'self'; base-uri 'none'; frame-ancestors 'none'; form-action 'none'")
        self.send_header("Referrer-Policy", "no-referrer")
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        if not self.allowed_host():
            return self.respond(403, {"error": "Μη έγκυρη διεύθυνση."})
        if self.path in FILES:
            filename, mime = FILES[self.path]
            return self.respond(200, (STATIC / filename).read_bytes(), mime)
        if self.path == "/api/session":
            return self.respond(200, {"token": TOKEN})
        if self.path == "/api/models":
            try:
                return self.respond(200, {"models": ollama.local_models()})
            except ollama.OllamaError as exc:
                return self.respond(503, {"error": str(exc)})
        if self.path == "/api/model-management":
            try:
                return self.respond(200, {"models": model_manager.installed_models(), "job": MODELS.status()})
            except (ollama.OllamaError, model_manager.ModelError) as exc:
                return self.respond(503, {"error": str(exc), "job": MODELS.status()})
        if self.path == "/api/argos-status":
            return self.respond(200, {**argos_translation.available(), "job": ARGOS.status()})
        if self.path == "/api/model-job":
            if not self.allowed_token():
                return self.respond(403, {"error": "Η αίτηση δεν επιτρέπεται."})
            return self.respond(200, MODELS.status())
        self.respond(404, {"error": "Δεν βρέθηκε."})

    def do_POST(self):
        origin = f"http://127.0.0.1:{self.server.server_port}"
        if (not self.allowed_host() or self.headers.get("Origin") != origin
                or not self.allowed_token()):
            return self.reject_post()
        if self.path == "/api/argos-install":
            return self.argos_install()
        if self.path in ("/api/model-install", "/api/model-delete"):
            return self.model_operation()
        if self.path != "/api/generate":
            return self.respond(404, {"error": "Δεν βρέθηκε."})
        if self.headers.get_content_type() != "application/json":
            return self.respond(415, {"error": "Μη έγκυρη αίτηση."})
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if not 0 < size <= 200_000:
                raise ValueError()
            request = json.loads(self.rfile.read(size).decode("utf-8"))
            if not isinstance(request, dict):
                raise ValueError()
            text, model, task = request.get("text"), request.get("model"), request.get("task")
            engine = request.get("engine", "ollama")
            if (not isinstance(text, str) or not text.strip() or len(text) > MAX_INPUT
                    or task not in ("write", "translate")
                    or (task == "write" and engine not in ("ollama", "nlg"))
                    or (task == "translate" and engine not in ("ollama", "argos"))
                    or (engine == "ollama" and not isinstance(model, str))):
                raise ValueError()
        except (ValueError, UnicodeDecodeError):
            return self.respond(400, {"error": "Ελέγξτε το κείμενο και το μοντέλο."})
        if engine == "nlg":
            return self.respond(200, nlg_writer.generate(text))
        if not BUSY.acquire(blocking=False):
            return self.respond(409, {"error": "Μια εργασία βρίσκεται ήδη σε εξέλιξη."})
        try:
            result = argos_translation.translate(text) if engine == "argos" else ollama.generate(model, text, task)
            return self.respond(200, {"text": result})
        except (ollama.OllamaError, argos_translation.ArgosError) as exc:
            return self.respond(503, {"error": str(exc)})
        finally:
            BUSY.release()

    def argos_install(self):
        if self.headers.get_content_type() != "application/json":
            return self.respond(415, {"error": "Μη έγκυρη αίτηση."})
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if not 0 < size <= 4096:
                raise ValueError()
            request = json.loads(self.rfile.read(size).decode("utf-8"))
            if not isinstance(request, dict) or request.get("confirmed") is not True:
                raise ValueError()
        except (ValueError, UnicodeDecodeError):
            return self.respond(400, {"error": "Απαιτείται επιβεβαίωση εγκατάστασης."})
        try:
            return self.respond(202, ARGOS.start())
        except argos_translation.ArgosBusy as exc:
            return self.respond(409, {"error": str(exc)})
        except argos_translation.ArgosError as exc:
            return self.respond(400, {"error": str(exc)})

    def model_operation(self):
        if self.headers.get_content_type() != "application/json":
            return self.respond(415, {"error": "Μη έγκυρη αίτηση."})
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if not 0 < size <= 4096:
                raise ValueError()
            request = json.loads(self.rfile.read(size).decode("utf-8"))
            if not isinstance(request, dict):
                raise ValueError()
            model = request.get("model")
        except (ValueError, UnicodeDecodeError):
            return self.respond(400, {"error": "Μη έγκυρη αίτηση."})
        try:
            if self.path == "/api/model-install":
                return self.respond(202, MODELS.start(model))
            if request.get("confirmed") is not True:
                return self.respond(400, {"error": "Απαιτείται επιβεβαίωση διαγραφής."})
            MODELS.delete(model)
            return self.respond(200, {"deleted": model})
        except model_manager.ModelBusy as exc:
            return self.respond(409, {"error": str(exc)})
        except model_manager.ModelError as exc:
            return self.respond(400, {"error": str(exc)})
        except ollama.OllamaError as exc:
            return self.respond(503, {"error": str(exc)})


def main():
    with Server(("127.0.0.1", 0), Handler) as server:
        print(f"Open: http://127.0.0.1:{server.server_port}/", flush=True)
        print("Press Ctrl+C to stop. Unsaved text will be lost.", flush=True)
        if "--open" in sys.argv[1:]:
            webbrowser.open(f"http://127.0.0.1:{server.server_port}/")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
