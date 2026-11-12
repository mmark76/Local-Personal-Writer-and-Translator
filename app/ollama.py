"""Local Ollama integration. No cloud fallback or automatic downloads."""
import json
import urllib.error
import urllib.request

BASE = "http://127.0.0.1:11434"
OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))
MAX_RESPONSE = 4 * 1024 * 1024


class OllamaError(Exception):
    pass


def _request(path, data=None, timeout=15):
    request = urllib.request.Request(
        BASE + path,
        data=None if data is None else json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="GET" if data is None else "POST",
    )
    try:
        with OPENER.open(request, timeout=timeout) as response:
            raw = response.read(MAX_RESPONSE + 1)
            if len(raw) > MAX_RESPONSE:
                raise OllamaError("Η απάντηση του Ollama είναι πολύ μεγάλη.")
            return json.loads(raw.decode("utf-8"))
    except OllamaError:
        raise
    except (urllib.error.URLError, TimeoutError, OSError, ValueError) as exc:
        raise OllamaError("Το τοπικό Ollama δεν είναι διαθέσιμο ή επέστρεψε σφάλμα.") from exc


def local_models():
    result = _request("/api/tags")
    if not isinstance(result, dict) or not isinstance(result.get("models"), list):
        raise OllamaError("Δεν ήταν δυνατή η ανάγνωση των μοντέλων.")
    names = []
    for item in result["models"]:
        if not isinstance(item, dict):
            continue
        name = item.get("name")
        if (isinstance(name, str) and 0 < len(name) <= 200
                and not name.lower().endswith((":cloud", "-cloud"))
                and not item.get("remote_model") and not item.get("remote_host")
                and isinstance(item.get("size"), int) and item["size"] > 0):
            names.append(name)
    return sorted(set(names))


def generate(model, text, task, direction="el-en"):
    if model not in local_models():
        raise OllamaError("Το επιλεγμένο τοπικό μοντέλο δεν είναι διαθέσιμο.")
    info = _request("/api/show", {"model": model})
    if not isinstance(info, dict) or info.get("remote_model") or info.get("remote_host"):
        raise OllamaError("Το μοντέλο δεν επιβεβαιώθηκε ως τοπικό.")
    if task == "write":
        instruction = ("Δημιούργησε συνεκτικό ελληνικό κείμενο από τις σημειώσεις. "
                       "Διατήρησε νόημα και ύφος, μην επινοήσεις γεγονότα ή πηγές. "
                       "Επίστρεψε μόνο το κείμενο.")
    elif task == "translate":
        if direction not in ("el-en", "en-el"):
            raise OllamaError("Μη έγκυρη κατεύθυνση μετάφρασης.")
        languages = "Greek text into English" if direction == "el-en" else "English text into Greek"
        instruction = (f"Translate the {languages}. Preserve meaning, "
                       "names, numbers, uncertainty and personal voice. "
                       "Do not add facts. Return only the translation.")
    else:
        raise OllamaError("Μη έγκυρη εργασία.")
    result = _request("/api/chat", {
        "model": model, "stream": False, "think": False,
        "messages": [{"role": "system", "content": instruction},
                     {"role": "user", "content": text}],
        "options": {"num_predict": 2048},
    }, timeout=600)
    message = result.get("message") if isinstance(result, dict) else None
    content = message.get("content") if isinstance(message, dict) else None
    if not isinstance(content, str) or not content.strip():
        raise OllamaError("Το μοντέλο δεν επέστρεψε κείμενο.")
    if result.get("done") is not True or result.get("done_reason") == "length":
        raise OllamaError("Το μοντέλο επέστρεψε ελλιπές αποτέλεσμα. Το πρωτότυπο διατηρήθηκε.")
    return content.strip()
