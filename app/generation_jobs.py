"""One cancellable generation subprocess, isolated from model management."""
import multiprocessing
import secrets
from multiprocessing.connection import wait
import threading


def _run(send, task, engine, model, text, direction):
    try:
        if engine == "argos":
            import argos_translation
            result = argos_translation.translate(text, "en", "el") if direction == "en-el" else argos_translation.translate(text)
        else:
            import ollama
            result = ollama.generate(model, text, task, "en-el") if task == "translate" and direction == "en-el" else ollama.generate(model, text, task)
        send.send({"state": "completed", "text": result})
    except Exception as exc:
        # Known adapters provide user-facing messages, never user text.
        import argos_translation
        import ollama
        message = str(exc) if isinstance(exc, (argos_translation.ArgosError, ollama.OllamaError)) else "Η εργασία απέτυχε."
        send.send({"state": "failed", "error": message})
    finally:
        send.close()


class GenerationBusy(Exception):
    pass


class GenerationJobs:
    def __init__(self, busy):
        self.busy = busy
        self.lock = threading.Lock()
        self.job = {"state": "idle"}
        self.job_id = None
        self.history = {}
        self.process = None

    def status(self, job_id=None):
        with self.lock:
            if job_id is not None and job_id != self.job_id:
                old = self.history.get(job_id)
                return old.copy() if old else None
            return self.job.copy()

    def start(self, task, engine, model, text, direction):
        if not self.busy.acquire(blocking=False):
            raise GenerationBusy()
        receiver = sender = process = None
        try:
            ctx = multiprocessing.get_context("spawn")
            receiver, sender = ctx.Pipe(duplex=False)
            process = ctx.Process(target=_run, args=(sender, task, engine, model, text, direction), daemon=True)
            process.start()
            sender.close()
            with self.lock:
                if self.job_id is not None:
                    self.history[self.job_id] = self.job.copy()
                    if len(self.history) > 20:
                        self.history.pop(next(iter(self.history)))
                self.job_id = secrets.token_urlsafe(18)
                self.job = {"state": "running", "id": self.job_id}
                self.process = process
            threading.Thread(target=self._wait, args=(process, receiver), daemon=True).start()
            return {"state": "running", "id": self.job_id}
        except Exception:
            if process is not None and process.is_alive():
                process.terminate()
                process.join()
            if receiver is not None:
                receiver.close()
            if sender is not None:
                sender.close()
            with self.lock:
                self.process = None
                self.job = {"state": "failed", "error": "Δεν ήταν δυνατή η έναρξη της εργασίας."}
            self.busy.release()
            raise

    def _wait(self, process, receiver):
        result = {"state": "failed", "error": "Η εργασία διακόπηκε απρόσμενα."}
        try:
            ready = wait([receiver, process.sentinel])
            with self.lock:
                stopping = self.job["state"] == "stopping"
            if not stopping and (receiver in ready or receiver.poll()):
                try:
                    result = receiver.recv()
                except (EOFError, OSError):
                    pass
            process.join()
        except Exception:
            if process.is_alive():
                process.terminate()
                process.join()
        finally:
            receiver.close()
            with self.lock:
                if self.job["state"] == "stopping":
                    result = {"state": "cancelled"}
                self.process = None
                self.busy.release()
                self.job = {**result, "id": self.job_id}

    def cancel(self, job_id=None):
        with self.lock:
            if (job_id is not None and job_id != self.job_id) or self.job["state"] != "running" or self.process is None:
                return False
            self.process.terminate()
            self.job = {"state": "stopping", "id": self.job_id}
            return True
