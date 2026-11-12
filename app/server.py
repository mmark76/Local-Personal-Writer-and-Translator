"""Minimal loopback-only server; text remains in the browser session."""
import json
from pathlib import Path
import secrets
import socket
import sys
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlsplit

import ollama
import model_manager
import argos_translation
import nlg_writer
import generation_jobs

STATIC = Path(__file__).resolve().parent / "static"
TOKEN = secrets.token_urlsafe(32)
BUSY = threading.Lock()
MODELS = model_manager.ModelManager(BUSY)
ARGOS = argos_translation.PackageManager(BUSY)
JOBS = generation_jobs.GenerationJobs(BUSY)
MAX_INPUT = 40_000
FILES = {"/": ("index.html", "text/html; charset=utf-8"),
         "/app.js": ("app.js", "text/javascript; charset=utf-8"),
         "/i18n.js": ("i18n.js", "text/javascript; charset=utf-8"),
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
        if self.path in ("/api/argos-status", "/api/argos-status?direction=en-el"):
            codes = ("en", "el") if self.path.endswith("direction=en-el") else ("el", "en")
            return self.respond(200, {**argos_translation.available(*codes), "job": ARGOS.status()})
        if urlsplit(self.path).path == "/api/generation-status":
            if not self.allowed_token():
                return self.respond(403, {"error": "Η αίτηση δεν επιτρέπεται."})
            job_id = parse_qs(urlsplit(self.path).query).get("id", [""])[0]
            job = JOBS.status(job_id) if job_id else None
            return self.respond(200, job) if job else self.respond(404, {"error": "Δεν βρέθηκε."})
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
        if self.path in ("/api/shutdown", "/api/restart"):
            JOBS.cancel()
            self.server.restart_requested = self.path == "/api/restart"
            self.respond(200, {"stopping": True})
            threading.Thread(target=self.server.shutdown, daemon=True).start()
            return
        if self.path == "/api/generation-cancel":
            if self.headers.get_content_type() != "application/json":
                return self.respond(415, {"error": "Μη έγκυρη αίτηση."})
            try:
                size = int(self.headers.get("Content-Length", "0"))
                if not 0 < size <= 1024:
                    raise ValueError()
                body = json.loads(self.rfile.read(size).decode("utf-8"))
                if not isinstance(body, dict) or not isinstance(body.get("id"), str):
                    raise ValueError()
            except (ValueError, UnicodeDecodeError):
                return self.respond(400, {"error": "Μη έγκυρη αίτηση."})
            return self.respond(200, {"cancelled": JOBS.cancel(body["id"])})
        if self.path == "/api/argos-install":
            return self.argos_install()
        if self.path in ("/api/model-install", "/api/model-delete"):
            return self.model_operation()
        if self.path not in ("/api/generate", "/api/generation-start"):
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
            direction = request.get("direction", "el-en")
            if (not isinstance(text, str) or not text.strip() or len(text) > MAX_INPUT
                    or task not in ("write", "translate")
                    or (task == "write" and engine not in ("ollama", "nlg"))
                    or (task == "translate" and engine not in ("ollama", "argos"))
                    or direction not in ("el-en", "en-el")
                    or (engine == "ollama" and not isinstance(model, str))):
                raise ValueError()
        except (ValueError, UnicodeDecodeError):
            return self.respond(400, {"error": "Ελέγξτε το κείμενο και το μοντέλο."})
        if engine == "nlg":
            return self.respond(200, nlg_writer.generate(text))
        if self.path == "/api/generation-start":
            try:
                return self.respond(202, JOBS.start(task, engine, model, text, direction))
            except generation_jobs.GenerationBusy:
                return self.respond(409, {"error": "Μια εργασία βρίσκεται ήδη σε εξέλιξη."})
            except Exception:
                return self.respond(503, {"error": "Δεν ήταν δυνατή η έναρξη της εργασίας."})
        if not BUSY.acquire(blocking=False):
            return self.respond(409, {"error": "Μια εργασία βρίσκεται ήδη σε εξέλιξη."})
        try:
            if engine == "argos":
                result = (argos_translation.translate(text, "en", "el") if direction == "en-el"
                          else argos_translation.translate(text))
            else:
                result = (ollama.generate(model, text, task, "en-el") if task == "translate" and direction == "en-el"
                          else ollama.generate(model, text, task))
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
            direction = request.get("direction", "el-en")
            if direction not in ("el-en", "en-el"):
                return self.respond(400, {"error": "Μη έγκυρη κατεύθυνση μετάφρασης."})
            return self.respond(202, ARGOS.start("en", "el") if direction == "en-el" else ARGOS.start())
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
    open_browser = "--open" in sys.argv[1:]
    while True:
        with Server(("127.0.0.1", 0), Handler) as server:
            server.restart_requested = False
            print("WRITER & TRANSLATOR LOCAL SERVER", flush=True)
            print("SERVER RUNNING", flush=True)
            print(f"Local address: http://127.0.0.1:{server.server_port}/", flush=True)
            print("\nIMPORTANT", flush=True)
            print("This Terminal runs the Writer & Translator local server.", flush=True)
            print("Closing it will stop the server and make the application unavailable.", flush=True)
            print("Keep this Terminal running. You can minimize it, but do not close it.", flush=True)
            print("Save your texts before stopping; unsaved text will be lost.", flush=True)
            if open_browser:
                webbrowser.open(f"http://127.0.0.1:{server.server_port}/")
            try:
                server.serve_forever()
            except KeyboardInterrupt:
                pass
        if not server.restart_requested:
            break
        print("\nRestarting Writer & Translator...", flush=True)
        open_browser = True


if __name__ == "__main__":
    main()
