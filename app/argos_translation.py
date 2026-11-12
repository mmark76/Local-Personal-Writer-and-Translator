"""Optional, local-only Greek-to-English Argos translation."""
import re
import threading


class ArgosError(Exception):
    pass


class ArgosBusy(ArgosError):
    pass


def _package():
    try:
        import argostranslate.package as package
        return package
    except Exception as exc:
        raise ArgosError("Το Argos δεν είναι διαθέσιμο στο Python της εφαρμογής. Έλεγξε την εγκατάσταση και τις εξαρτήσεις του.") from exc


def available(from_code="el", to_code="en"):
    if (from_code, to_code) not in (("el", "en"), ("en", "el")):
        return {"available": False, "installed": False}
    try:
        pair = any(p.from_code == from_code and p.to_code == to_code for p in _package().get_installed_packages())
        return {"available": True, "installed": pair}
    except Exception:
        return {"available": False, "installed": False}


def translate(text, from_code="el", to_code="en"):
    if not isinstance(text, str) or not text.strip() or len(text) > 40000:
        raise ArgosError("Πρόσθεσε έγκυρο ελληνικό κείμενο.")
    state = available(from_code, to_code)
    if not state["available"]:
        raise ArgosError("Το Argos δεν είναι διαθέσιμο στο Python της εφαρμογής.")
    if not state["installed"]:
        raise ArgosError("Το γλωσσικό πακέτο για την επιλεγμένη κατεύθυνση δεν είναι εγκατεστημένο.")
    try:
        # Override provider and sentence splitting before importing translate: user
        # Argos settings must not switch this application to a remote provider.
        import argostranslate.settings as settings
        settings.model_provider = settings.ModelProvider.OPENNMT
        settings.chunk_type = settings.ChunkType.STANZA
        import argostranslate.translate as argos
        argos.get_installed_languages.cache_clear()
        translator = argos.get_translation_from_codes(from_code, to_code)
        if translator is None:
            raise ArgosError("Δεν βρέθηκε το επιλεγμένο γλωσσικό ζεύγος.")
        # Argos 1.11 packages can contain older Stanza resources incompatible
        # with current Stanza. Use a local sentence splitter; no downloads.
        underlying = getattr(translator, "underlying", translator)
        if not hasattr(underlying, "sentencizer"):
            raise ArgosError("Μη συμβατή έκδοση Argos για τοπική μετάφραση.")
        class LocalSentencizer:
            def split_sentences(self, value):
                return re.split(r"(?<=[.!?;;])\s+", value)
        underlying.sentencizer = LocalSentencizer()
        pieces = re.split(r"(\r\n|\r|\n)", text)
        return "".join(translator.translate(part) if part.strip() else part for part in pieces)
    except ArgosError:
        raise
    except Exception as exc:
        raise ArgosError("Η τοπική μετάφραση Argos απέτυχε. Έλεγξε το γλωσσικό πακέτο και τα τοπικά αρχεία του.") from exc


class PackageManager:
    def __init__(self, busy):
        self._busy = busy
        self._lock = threading.Lock()
        self._job = {"state": "idle", "status": ""}

    def status(self):
        with self._lock:
            return self._job.copy()

    def _update(self, state, status):
        with self._lock:
            self._job = {"state": state, "status": status}

    def start(self, from_code="el", to_code="en"):
        if (from_code, to_code) not in (("el", "en"), ("en", "el")):
            raise ArgosError("Μη έγκυρη κατεύθυνση μετάφρασης.")
        if not self._busy.acquire(blocking=False):
            raise ArgosBusy("Μια εργασία βρίσκεται ήδη σε εξέλιξη.")
        try:
            state = available(from_code, to_code)
            if not state["available"]:
                raise ArgosError("Το Argos δεν είναι διαθέσιμο στο Python της εφαρμογής.")
            if state["installed"]:
                raise ArgosError("Το γλωσσικό πακέτο είναι ήδη εγκατεστημένο.")
            self._update("running", "Αναζήτηση του γλωσσικού πακέτου…")
            threading.Thread(target=self._install, args=(from_code, to_code), daemon=True).start()
            return self.status()
        except Exception:
            self._busy.release()
            raise

    def _install(self, from_code="el", to_code="en"):
        try:
            package = _package()
            package.update_package_index()
            candidate = next((p for p in package.get_available_packages() if p.from_code == from_code and p.to_code == to_code), None)
            if candidate is None:
                raise ArgosError("Δεν βρέθηκε το επιλεγμένο γλωσσικό πακέτο στον κατάλογο Argos.")
            self._update("running", "Λήψη του γλωσσικού πακέτου…")
            path = candidate.download()
            self._update("running", "Εγκατάσταση του γλωσσικού πακέτου…")
            package.install_from_path(path)
            if not available(from_code, to_code)["installed"]:
                raise ArgosError("Η εγκατάσταση δεν επιβεβαιώθηκε. Έλεγξε το πακέτο Argos.")
            self._update("completed", "Το γλωσσικό πακέτο εγκαταστάθηκε.")
        except ArgosError as exc:
            self._update("failed", str(exc))
        except Exception:
            self._update("failed", "Η λήψη ή η εγκατάσταση απέτυχε. Έλεγξε τη σύνδεση και τον διαθέσιμο χώρο.")
        finally:
            self._busy.release()
