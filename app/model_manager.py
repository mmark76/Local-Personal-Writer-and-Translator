"""Explicit local Ollama model management; no shell or browser-supplied endpoint."""
import json
import re
import threading
import urllib.error
import urllib.request

import ollama

MODEL_NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]*(?:/[A-Za-z0-9][A-Za-z0-9_.-]*)?(?::[A-Za-z0-9][A-Za-z0-9_.-]*)?\Z", re.ASCII)


class ModelError(ValueError):
    pass


class ModelBusy(ModelError):
    pass


def validate_name(name):
    # Restrict pulls to the default Ollama registry, optionally with a namespace.
    if (not isinstance(name, str) or not 1 <= len(name) <= 128
            or not MODEL_NAME.fullmatch(name) or "cloud" in name.lower()
            or ("/" in name and "." in name.split("/", 1)[0])):
        raise ModelError("Μη έγκυρο όνομα. Χρησιμοποίησε όνομα τοπικού μοντέλου από το Ollama.")
    return name


def installed_models():
    result = ollama._request("/api/tags")
    if not isinstance(result, dict) or not isinstance(result.get("models"), list):
        raise ModelError("Δεν ήταν δυνατή η ανάγνωση των μοντέλων.")
    models = {}
    for item in result["models"]:
        if not isinstance(item, dict):
            continue
        name, size = item.get("name"), item.get("size")
        if (not isinstance(name, str) or not name or len(name) > 200
                or any(ord(ch) < 32 for ch in name)
                or item.get("remote_model") or item.get("remote_host")
                or name.lower().endswith((":cloud", "-cloud"))):
            continue
        models[name] = {"name": name, "size": size if type(size) is int and size >= 0 else None}
    return sorted(models.values(), key=lambda model: model["name"].casefold())


def _canonical(name):
    name = name.casefold()
    if name.startswith("library/"):
        name = name[len("library/"):]
    return name if ":" in name else name + ":latest"


class ModelManager:
    def __init__(self, busy):
        self._busy = busy
        self._lock = threading.Lock()
        self._job = {"state": "idle", "model": "", "status": "", "completed": 0, "total": 0}

    def status(self):
        with self._lock:
            return self._job.copy()

    def _update(self, **values):
        with self._lock:
            self._job.update(values)

    def start(self, name):
        name = validate_name(name)
        if not self._busy.acquire(blocking=False):
            raise ModelBusy("Μια εργασία βρίσκεται ήδη σε εξέλιξη.")
        try:
            if any(_canonical(item["name"]) == _canonical(name) for item in installed_models()):
                raise ModelError("Το μοντέλο είναι ήδη εγκατεστημένο.")
            self._update(state="running", model=name, status="Σύνδεση με το Ollama…",
                         completed=0, total=0)
            thread = threading.Thread(target=self._pull, args=(name,), daemon=True)
            thread.start()
            return self.status()
        except Exception:
            self._update(state="failed", status="Δεν ήταν δυνατή η έναρξη της λήψης.", completed=0, total=0)
            self._busy.release()
            raise

    def _pull(self, name):
        request = urllib.request.Request(
            ollama.BASE + "/api/pull",
            data=json.dumps({"model": name, "stream": True}).encode("utf-8"),
            headers={"Content-Type": "application/json"}, method="POST")
        succeeded = False
        try:
            with ollama.OPENER.open(request, timeout=120) as response:
                while True:
                    line = response.readline(16385)
                    if not line:
                        break
                    if len(line) > 16384:
                        raise ModelError("Μη έγκυρη απάντηση προόδου από το Ollama.")
                    event = json.loads(line)
                    if not isinstance(event, dict):
                        raise ModelError("Η λήψη απέτυχε. Έλεγξε το όνομα, τη σύνδεση και τον διαθέσιμο χώρο.")
                    error = event.get("error")
                    if error:
                        if isinstance(error, str) and any(term in error.casefold() for term in ("not found", "does not exist", "manifest unknown")):
                            raise ModelError("Το μοντέλο δεν βρέθηκε. Έλεγξε το ακριβές όνομα στη βιβλιοθήκη Ollama.")
                        raise ModelError("Η λήψη απέτυχε. Έλεγξε το όνομα, τη σύνδεση και τον διαθέσιμο χώρο.")
                    status = event.get("status", "")
                    completed, total = event.get("completed", 0), event.get("total", 0)
                    if not isinstance(status, str) or type(completed) is not int or type(total) is not int or completed < 0 or total < 0:
                        raise ModelError("Μη έγκυρη απάντηση προόδου από το Ollama.")
                    self._update(status=status[:160], completed=completed, total=total)
                    if status == "success":
                        succeeded = True
            if not succeeded:
                raise ModelError("Η λήψη σταμάτησε πριν επιβεβαιωθεί η ολοκλήρωση.")
            if not any(_canonical(item["name"]) == _canonical(name) for item in installed_models()):
                raise ModelError("Το Ollama ανέφερε επιτυχία, αλλά το μοντέλο δεν εμφανίστηκε στη λίστα.")
            self._update(state="completed", status="Το μοντέλο εγκαταστάθηκε.", completed=0, total=0)
        except ModelError as exc:
            self._update(state="failed", status=str(exc), completed=0, total=0)
        except urllib.error.HTTPError as exc:
            status = ("Το μοντέλο δεν βρέθηκε. Έλεγξε το ακριβές όνομα στη βιβλιοθήκη Ollama."
                      if exc.code == 404 else "Η λήψη απέτυχε. Έλεγξε το Ollama, τη σύνδεση και τον διαθέσιμο χώρο.")
            self._update(state="failed", status=status, completed=0, total=0)
        except Exception:
            # A background job must always reach a terminal state even on unexpected stream errors.
            self._update(state="failed", status="Η λήψη απέτυχε. Έλεγξε το όνομα, το Ollama, τη σύνδεση και τον διαθέσιμο χώρο.", completed=0, total=0)
        finally:
            self._busy.release()

    def delete(self, name):
        if not isinstance(name, str) or not 1 <= len(name) <= 200 or any(ord(ch) < 32 for ch in name):
            raise ModelError("Μη έγκυρο όνομα μοντέλου.")
        if not self._busy.acquire(blocking=False):
            raise ModelBusy("Μια εργασία βρίσκεται ήδη σε εξέλιξη.")
        try:
            if name not in {item["name"] for item in installed_models()}:
                raise ModelError("Το μοντέλο δεν βρέθηκε στα τοπικά εγκατεστημένα μοντέλα.")
            request = urllib.request.Request(
                ollama.BASE + "/api/delete", data=json.dumps({"model": name}).encode("utf-8"),
                headers={"Content-Type": "application/json"}, method="DELETE")
            try:
                with ollama.OPENER.open(request, timeout=30) as response:
                    if response.status not in (200, 204):
                        raise ModelError("Η διαγραφή απέτυχε.")
            except (urllib.error.URLError, OSError, TimeoutError) as exc:
                raise ModelError("Η διαγραφή απέτυχε. Έλεγξε το τοπικό Ollama.") from exc
        finally:
            self._busy.release()
