"""Conservative, deterministic formatting of Greek notes; no inference services."""
import re

# A marker is removed only for top-level bullet lines with explicit final
# punctuation. Nested bullets, numbered lists and fragments retain their form.
BULLET = re.compile(r"^([•\-*])([ \t]+)(\S.*)$")
ENDING = re.compile(r"[.!?;;][»”\"')\]]*$")
PURPOSE = re.compile(r"^σκοπός\s+(?:της\s+)?εργασίας\s+((?:η|το|οι|τα)\s+.+)$", re.IGNORECASE)
QUESTION = re.compile(r"^αξιολόγηση\s+(?:στο\s+)?ερώτημα\s+((?:πόσο|πώς|πως|αν|κατά\s+πόσο)\s+.+)$", re.IGNORECASE)


def parse_notes(text):
    """Keep every line, its order, and blank paragraph boundaries."""
    if not isinstance(text, str) or not text.strip() or len(text) > 40000:
        raise ValueError("Πρόσθεσε έγκυρες σημειώσεις έως 40.000 χαρακτήρες.")
    return text.splitlines()


def explicitly_finished(text):
    return bool(ENDING.search(text)) and not text.endswith(("...", "…"))


def form_sentence(line):
    """Use the author's punctuation as the only signal for joining bullets."""
    match = BULLET.fullmatch(line)
    if not match:
        return line, False
    content = match.group(3)
    purpose = PURPOSE.fullmatch(content)
    if purpose:
        statement = "Σκοπός της εργασίας είναι " + purpose.group(1)
        return statement if explicitly_finished(statement) else statement + ".", True
    question = QUESTION.fullmatch(content)
    if question:
        statement = "Αξιολογείται το ερώτημα: " + question.group(1)
        return statement if explicitly_finished(statement) else statement + ".", True
    if not explicitly_finished(content):
        return line, False
    return content, True


def organize_paragraphs(lines):
    """Join adjacent finished bullets only; retain all other lines verbatim."""
    result, group = [], []
    partial = False

    def flush():
        if group:
            result.append(" ".join(group))
            group.clear()

    for line in lines:
        sentence, joinable = form_sentence(line)
        if joinable:
            group.append(sentence)
        else:
            flush()
            result.append(line)
            if line.strip() and (not explicitly_finished(line.rstrip()) or BULLET.fullmatch(line) or line[:1].isspace()):
                partial = True
    flush()
    return "\n".join(result), partial


def generate(text):
    """Return a reviewable result without adding facts or changing wording."""
    output, partial = organize_paragraphs(parse_notes(text))
    return {"text": output, "partial": partial}
