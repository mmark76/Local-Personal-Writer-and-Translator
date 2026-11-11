"use strict";
const el = id => document.getElementById(id);
let token = "", busy = false, draftApproved = false, finalApproved = false, translationValid = false, dirty = false;
const status = message => { el("status").textContent = message; };

async function api(path, options) {
  const response = await fetch(path, options);
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || "Η εργασία απέτυχε.");
  return data;
}
async function refreshModels() {
  try {
    const previous = el("model").value;
    const data = await api("/api/models");
    el("model").replaceChildren(new Option("Επίλεξε μοντέλο", ""));
    data.models.forEach(model => el("model").add(new Option(model, model)));
    if (data.models.includes(previous)) el("model").value = previous;
    status(data.models.length ? "Επίλεξε ένα εγκατεστημένο τοπικό μοντέλο." : "Δεν βρέθηκαν τοπικά μοντέλα Ollama.");
  } catch (err) { status(err.message); }
}
function resetFinal() { finalApproved = false; el("save").disabled = true; el("final-status").textContent = "Η μετάφραση χρειάζεται τον έλεγχό σου."; }
function resetDraft() { draftApproved = false; translationValid = false; el("translate").disabled = true; el("draft-status").textContent = "Το προσχέδιο χρειάζεται τον έλεγχό σου."; resetFinal(); }
function setBusy(value) {
  busy = value;
  ["write", "refresh", "approve-draft", "approve-final", "save-notes", "save-draft"].forEach(id => { el(id).disabled = value; });
  ["notes", "draft", "translation", "model", "translation-engine", "writer-engine"].forEach(id => { el(id).disabled = value; });
  el("translate").disabled = value || !draftApproved;
  el("save").disabled = value || !finalApproved;
}
async function generate(task, text) {
  const engine = task === "write" ? el("writer-engine").value : el("translation-engine").value;
  if (busy || !text.trim() || (engine === "ollama" && !el("model").value)) { status("Πρόσθεσε κείμενο και, για Ollama, επίλεξε μοντέλο."); return; }
  const target = task === "write" ? "draft" : "translation";
  if (el(target).value.trim() && !window.confirm("Υπάρχει ήδη κείμενο σε αυτό το πεδίο. Να αντικατασταθεί;")) return;
  setBusy(true); status(engine === "nlg" ? "Οι τοπικοί κανόνες επεξεργάζονται τις σημειώσεις…" : engine === "argos" ? "Το Argos μεταφράζει τοπικά. Περίμενε…" : "Το τοπικό μοντέλο εργάζεται. Περίμενε…");
  try {
    const data = await api("/api/generate", {
      method: "POST", headers: {"Content-Type": "application/json", "X-Session-Token": token},
      body: JSON.stringify({task, text, engine, model: el("model").value})
    });
    if (task === "write") { el("draft").value = data.text; resetDraft(); }
    else { el("translation").value = data.text; translationValid = true; resetFinal(); }
    dirty = true; status(data.partial ? "Μερικό αποτέλεσμα: αμφίσημες ή μη ολοκληρωμένες σημειώσεις διατηρήθηκαν. Έλεγξέ τες πριν την έγκριση." : "Ολοκληρώθηκε. Έλεγξε το αποτέλεσμα.");
  } catch (err) { status(err.message + " Το κείμενό σου παραμένει διαθέσιμο."); }
  finally { setBusy(false); }
}
el("writer-engine").addEventListener("change", () => {
  el("writer-engine-hint").textContent = el("writer-engine").value === "nlg"
    ? "Περιορισμένοι τοπικοί κανόνες: ενώνουν bullets με τελική στίξη, χωρίς γραμματικό έλεγχο ή συμπλήρωση. Οι ελλιπείς σημειώσεις παραμένουν. Έλεγξε και επεξεργάσου το κείμενο."
    : "Το Ollama χρησιμοποιεί το μοντέλο που επέλεξες στην κορυφή.";
  status("");
});
let argosPolling = false;
async function refreshArgos() {
  try {
    const data = await api("/api/argos-status");
    const job = data.job;
    el("argos-install").hidden = !data.available || data.installed || job.state === "running";
    el("argos-status").textContent = job.state === "running" || job.state === "failed" ? job.status :
      !data.available ? "Το Argos δεν είναι διαθέσιμο στο Python της εφαρμογής." :
      data.installed ? "Το πακέτο ελληνικά → αγγλικά είναι εγκατεστημένο." : "Λείπει το πακέτο ελληνικά → αγγλικά.";
    if (job.state === "running" && !argosPolling) {
      argosPolling = true;
      setTimeout(async () => { argosPolling = false; await refreshArgos(); }, 1500);
    }
  } catch { el("argos-status").textContent = "Δεν ήταν δυνατός ο έλεγχος του Argos."; }
}
el("translation-engine").addEventListener("change", () => {
  const argos = el("translation-engine").value === "argos";
  el("argos-controls").hidden = !argos;
  el("engine-hint").textContent = argos ? "Το Argos μεταφράζει χωρίς Ollama. Το μοντέλο στην κορυφή παραμένει διαθέσιμο όταν επιλέγεις Ollama." : "Το Ollama χρησιμοποιεί το μοντέλο που επέλεξες στην κορυφή.";
  if (argos) refreshArgos();
});
el("argos-refresh").addEventListener("click", refreshArgos);
el("argos-install").addEventListener("click", async () => {
  if (!window.confirm("Να γίνει λήψη και εγκατάσταση του πακέτου Argos ελληνικά → αγγλικά; Χρειάζεται σύνδεση και χώρος. Το πακέτο μπορεί να χρησιμοποιείται και από άλλες εφαρμογές.")) return;
  el("argos-install").disabled = true;
  try {
    await api("/api/argos-install", {method: "POST", headers: {"Content-Type": "application/json", "X-Session-Token": token}, body: JSON.stringify({confirmed: true})});
  } catch (err) { el("argos-status").textContent = err.message; el("argos-install").disabled = false; return; }
  el("argos-install").disabled = false;
  await refreshArgos();
});
el("refresh").addEventListener("click", refreshModels);
el("write").addEventListener("click", () => generate("write", el("notes").value));
el("translate").addEventListener("click", () => { if (draftApproved) generate("translate", el("draft").value); });
el("approve-draft").addEventListener("click", () => {
  if (!el("draft").value.trim()) return;
  draftApproved = true; el("translate").disabled = busy; el("draft-status").textContent = "Εγκρίθηκε για μετάφραση."; status("");
});
el("approve-final").addEventListener("click", () => {
  if (!translationValid || !draftApproved || !el("translation").value.trim()) { status("Πρώτα ενέκρινε και μετάφρασε το τρέχον ελληνικό κείμενο."); return; }
  finalApproved = true; el("save").disabled = busy; el("final-status").textContent = "Εγκρίθηκε για αποθήκευση."; status("");
});
el("notes").addEventListener("input", () => { dirty = true; resetDraft(); });
el("draft").addEventListener("input", () => { dirty = true; resetDraft(); });
el("translation").addEventListener("input", () => { dirty = true; resetFinal(); });
function downloadText(content, filename) {
  const url = URL.createObjectURL(new Blob([content], {type: "text/plain;charset=utf-8"}));
  const link = document.createElement("a"); link.href = url; link.download = filename; link.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
  status("Το αρχείο ζητήθηκε από τον browser. Επιβεβαίωσε ότι αποθηκεύτηκε.");
}
el("save-notes").addEventListener("click", () => {
  if (el("notes").value.trim()) downloadText(el("notes").value, "notes.txt");
});
el("save-draft").addEventListener("click", () => {
  if (el("draft").value.trim()) downloadText(el("draft").value, "greek-draft.txt");
});
el("save").addEventListener("click", () => {
  if (!finalApproved) return;
  const content = "ΣΗΜΕΙΩΣΕΙΣ\n\n" + el("notes").value + "\n\nΕΛΛΗΝΙΚΟ ΚΕΙΜΕΝΟ\n\n" + el("draft").value + "\n\nENGLISH TRANSLATION\n\n" + el("translation").value;
  downloadText(content, "writer-translator.txt");
});
window.addEventListener("beforeunload", event => { if (dirty) { event.preventDefault(); event.returnValue = ""; } });
window.refreshAvailableModels = refreshModels;
(async () => { try { token = (await api("/api/session")).token; await refreshModels(); } catch { status("Η τοπική εφαρμογή δεν είναι διαθέσιμη."); } })();
