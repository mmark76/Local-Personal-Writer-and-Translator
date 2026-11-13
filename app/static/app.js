"use strict";
const el = id => document.getElementById(id);
let token = "", busy = false, draftApproved = false, finalApproved = false, translationValid = false, reverseApproved = false, dirty = false, initialModelPending = true;
const status = message => { el("status").textContent = message; };

async function api(path, options) {
  const response = await fetch(path, options);
  const data = await response.json();
  if (!response.ok) throw new Error(window.translateUi(data.error || "Η εργασία απέτυχε."));
  return data;
}
async function refreshModels() {
  try {
    const selectors = [el("model"), el("translation-model")];
    const previous = selectors.map(select => select.value);
    const data = await api("/api/models");
    selectors.forEach((select, index) => {
      select.replaceChildren(new Option("Επίλεξε μοντέλο", ""));
      data.models.forEach(model => select.add(new Option(model, model)));
      if (data.models.includes(previous[index])) select.value = previous[index];
      else if (index === 0 && initialModelPending) {
        const preferred = ["gemma4:e4b", "gemma4:latest"].find(name => data.models.includes(name));
        if (preferred) select.value = preferred;
      }
    });
    initialModelPending = false;
    status(!data.models.length ? "Δεν βρέθηκαν τοπικά μοντέλα Ollama." : el("model").value ? "Επιλέχθηκε το τοπικό μοντέλο Writer." : "Επίλεξε ένα εγκατεστημένο τοπικό μοντέλο.");
  } catch (err) { status(err.message); }
}
function resetFinal() { finalApproved = false; el("save").disabled = true; el("final-status").textContent = "Η μετάφραση χρειάζεται τον έλεγχό σου."; }
function resetDraft() { draftApproved = false; translationValid = false; el("translate").disabled = true; el("draft-status").textContent = "Το προσχέδιο χρειάζεται τον έλεγχό σου."; resetFinal(); }
function setBusy(value) {
  busy = value;
  ["write", "refresh", "approve-draft", "approve-final", "save-notes", "save-draft"].forEach(id => { el(id).disabled = value; });
  ["notes", "draft", "translation", "model", "translation-model", "translation-engine", "writer-engine", "translation-direction", "english-source", "approve-source"].forEach(id => { el(id).disabled = value; });
  document.querySelectorAll(".text-actions button").forEach(button => { button.disabled = value; });
  el("translate").disabled = value || !(el("translation-direction").value === "en-el" ? reverseApproved : draftApproved);
  el("save").disabled = value || !finalApproved;
}
let stopRequested = false, activeJobId = "";
const waitForJob = () => new Promise(resolve => setTimeout(resolve, 350));
el("stop-generation").addEventListener("click", async () => {
  stopRequested = true;
  el("stop-generation").disabled = true;
  try {
    const result = await api("/api/generation-cancel", {method: "POST", headers: {"Content-Type": "application/json", "X-Session-Token": token}, body: JSON.stringify({id: activeJobId})});
    if (!result.cancelled) stopRequested = false;
  } catch (err) { stopRequested = false; status(err.message); el("stop-generation").disabled = false; }
});
async function generate(task, text) {
  const engine = task === "write" ? el("writer-engine").value : el("translation-engine").value;
  const model = task === "write" ? el("model").value : el("translation-model").value;
  if (busy || !text.trim() || (engine === "ollama" && !model)) { status("Πρόσθεσε κείμενο και, για Ollama, επίλεξε μοντέλο."); return; }
  const target = task === "write" ? "draft" : "translation";
  if (el(target).value.trim() && !window.confirm(window.translateUi("Υπάρχει ήδη κείμενο σε αυτό το πεδίο. Να αντικατασταθεί;"))) return;
  setBusy(true); status(engine === "nlg" ? "Οι τοπικοί κανόνες επεξεργάζονται τις σημειώσεις…" : engine === "argos" ? "Το Argos μεταφράζει τοπικά. Περίμενε…" : "Το τοπικό μοντέλο εργάζεται. Περίμενε…");
  try {
    stopRequested = false;
    el("stop-generation").hidden = true;
    el("stop-generation").disabled = false;
    let data = await api(engine === "nlg" ? "/api/generate" : "/api/generation-start", {
      method: "POST", headers: {"Content-Type": "application/json", "X-Session-Token": token},
      body: JSON.stringify({task, text, engine, direction: task === "translate" ? el("translation-direction").value : "el-en", model})
    });
    if (engine !== "nlg") {
      activeJobId = data.id;
      el("stop-generation").hidden = false;
      while (data.state === "running" || data.state === "stopping") {
        await waitForJob();
        data = await api("/api/generation-status?id=" + encodeURIComponent(activeJobId), {headers: {"X-Session-Token": token}});
      }
      if (stopRequested || data.state === "cancelled") {
        status(engine === "ollama" ? "Η αίτηση διακόπηκε. Το Ollama μπορεί να συνεχίζει προσωρινά τη δική του επεξεργασία." : "Η αίτηση διακόπηκε. Το αρχικό κείμενο παραμένει διαθέσιμο.");
        return;
      }
      if (data.state !== "completed") throw new Error(window.translateUi(data.error || "Η εργασία απέτυχε."));
    }
    if (task === "write") { el("draft").value = data.text; resetDraft(); }
    else { el("translation").value = data.text; translationValid = true; resetFinal(); }
    dirty = true; status(data.partial ? "Μερικό αποτέλεσμα: αμφίσημες ή μη ολοκληρωμένες σημειώσεις διατηρήθηκαν. Έλεγξέ τες πριν την έγκριση." : "Ολοκληρώθηκε. Έλεγξε το αποτέλεσμα.");
  } catch (err) { status(err.message + " " + window.translateUi("Το κείμενό σου παραμένει διαθέσιμο.")); }
  finally { activeJobId = ""; el("stop-generation").hidden = true; setBusy(false); }
}
el("writer-engine").addEventListener("change", () => {
  el("writer-model-wrap").hidden = el("writer-engine").value === "nlg";
  el("writer-engine-hint").textContent = el("writer-engine").value === "nlg"
    ? "Περιορισμένοι τοπικοί κανόνες: αναγνωρίζουν ορισμένα πρότυπα και ενώνουν ολοκληρωμένα bullets, χωρίς γενική γραμματική σύνθεση. Οι αμφίσημες σημειώσεις παραμένουν. Έλεγξε και επεξεργάσου το κείμενο."
    : "Το Ollama χρησιμοποιεί το μοντέλο που επέλεξες σε αυτή τη στήλη.";
  status("");
});
const columnSizes = ["minmax(250px, .92fr)", "minmax(330px, 1.17fr)", "minmax(280px, 1fr)"];
const columnButtons = [...document.querySelectorAll(".panel-toggle")];
function updateColumns() {
  const desktop = window.matchMedia("(min-width: 961px)").matches;
  document.querySelector(".workspace").style.gridTemplateColumns = desktop
    ? columnButtons.map((button, index) => button.getAttribute("aria-expanded") === "true" ? columnSizes[index] : "48px").join(" ") : "";
}
columnButtons.forEach(button => button.addEventListener("click", () => {
  const open = button.getAttribute("aria-expanded") === "true";
  button.setAttribute("aria-expanded", String(!open));
  const label = open ? "Εμφάνιση στήλης" : "Απόκρυψη στήλης";
  button.setAttribute("aria-label", label); button.title = label;
  button.closest(".panel").classList.toggle("collapsed", open);
  updateColumns();
}));
window.addEventListener("resize", updateColumns);
document.querySelectorAll(".height-divider").forEach(divider => {
  const panel = divider.previousElementSibling;
  divider.setAttribute("aria-valuenow", String(Math.round(panel.getBoundingClientRect().height)));
  function resizeTo(height) {
    const max = Math.min(600, Math.max(90, Math.floor(window.innerHeight * 0.65)));
    const value = Math.round(Math.max(90, Math.min(max, height)));
    panel.style.setProperty("--engine-height", value + "px");
    panel.classList.add("resized");
    divider.setAttribute("aria-valuemax", String(max));
    divider.setAttribute("aria-valuenow", String(value));
  }
  divider.addEventListener("pointerdown", event => {
    if (event.button !== 0) return;
    event.preventDefault();
    const startY = event.clientY, startHeight = panel.getBoundingClientRect().height;
    divider.setPointerCapture(event.pointerId);
    const move = next => resizeTo(startHeight + next.clientY - startY);
    const done = () => { divider.removeEventListener("pointermove", move); divider.removeEventListener("pointerup", done); divider.removeEventListener("pointercancel", done); };
    divider.addEventListener("pointermove", move);
    divider.addEventListener("pointerup", done);
    divider.addEventListener("pointercancel", done);
  });
  divider.addEventListener("keydown", event => {
    if (event.key !== "ArrowUp" && event.key !== "ArrowDown") return;
    event.preventDefault();
    resizeTo(panel.getBoundingClientRect().height + (event.key === "ArrowUp" ? -20 : 20));
  });
});
function setTheme(light) {
  document.documentElement.classList.toggle("light", light);
  el("theme-toggle").textContent = light ? "Σκοτεινό" : "Φωτεινό";
  try { localStorage.setItem("writer-theme", light ? "light" : "dark"); } catch {}
}
try { setTheme(localStorage.getItem("writer-theme") === "light"); } catch {}
el("theme-toggle").addEventListener("click", () => setTheme(!document.documentElement.classList.contains("light")));
["help", "info", "settings"].forEach(name => {
  el(name + "-open").addEventListener("click", () => el(name + "-dialog").showModal());
  el(name + "-close").addEventListener("click", () => el(name + "-dialog").close());
});
el("stop-local").addEventListener("click", async () => {
  if (!window.confirm(window.translateUi("Να τερματιστεί η εφαρμογή; Αποθήκευσε πρώτα όσα κείμενα θέλεις να κρατήσεις."))) return;
  try {
    await api("/api/shutdown", {method: "POST", headers: {"X-Session-Token": token}});
    dirty = false;
    status("Η εφαρμογή τερματίστηκε. Κλείσε αυτή την καρτέλα.");
  } catch (err) { status(err.message); }
});
el("restart-local").addEventListener("click", async () => {
  if (!window.confirm(window.translateUi("Να γίνει επανεκκίνηση; Αποθήκευσε πρώτα όσα κείμενα θέλεις να κρατήσεις."))) return;
  try {
    await api("/api/restart", {method: "POST", headers: {"X-Session-Token": token}});
    dirty = false;
    status("Η επανεκκίνηση ζητήθηκε. Έλεγξε τη νέα καρτέλα στον browser.");
  } catch (err) { status(err.message); }
});
["notes", "draft", "english-source", "translation"].forEach(id => {
  const field = el(id);
  const fieldLabel = field.labels[0];
  fieldLabel.id = `text-label-${id}`;
  const actions = document.createElement("div");
  actions.className = "text-actions";
  const clear = document.createElement("button");
  clear.type = "button"; clear.className = "secondary"; clear.textContent = "Καθαρισμός";
  clear.id = `clear-${id}`;
  clear.setAttribute("aria-labelledby", `${clear.id} ${fieldLabel.id}`);
  clear.addEventListener("click", () => {
    if (!field.value || !window.confirm(window.translateUi("Να καθαριστεί αυτό το πεδίο; Το κείμενό του θα διαγραφεί."))) return;
    field.value = ""; field.dispatchEvent(new Event("input", {bubbles: true})); field.focus();
  });
  const copy = document.createElement("button");
  copy.type = "button"; copy.className = "secondary"; copy.textContent = "Αντιγραφή";
  copy.id = `copy-${id}`;
  copy.setAttribute("aria-labelledby", `${copy.id} ${fieldLabel.id}`);
  copy.addEventListener("click", async () => {
    if (!field.value) return;
    try { await navigator.clipboard.writeText(field.value); status("Το κείμενο αντιγράφηκε."); }
    catch { status("Η αντιγραφή απέτυχε. Επίλεξε και αντέγραψε το κείμενο χειροκίνητα."); }
  });
  actions.append(clear, copy); field.insertAdjacentElement("afterend", actions);
});
let argosPolling = false;
async function refreshArgos() {
  try {
    const direction = el("translation-direction").value;
    const data = await api(direction === "en-el" ? "/api/argos-status?direction=en-el" : "/api/argos-status");
    const job = data.job;
    el("argos-install").hidden = !data.available || data.installed || job.state === "running";
    el("argos-status").textContent = job.state === "running" || job.state === "failed" ? job.status :
      !data.available ? "Το Argos δεν είναι διαθέσιμο στο Python της εφαρμογής." :
      data.installed ? "Το επιλεγμένο γλωσσικό πακέτο είναι εγκατεστημένο." : "Λείπει το επιλεγμένο γλωσσικό πακέτο.";
    if (job.state === "running" && !argosPolling) {
      argosPolling = true;
      setTimeout(async () => { argosPolling = false; await refreshArgos(); }, 1500);
    }
  } catch { el("argos-status").textContent = "Δεν ήταν δυνατός ο έλεγχος του Argos."; }
}
el("translation-engine").addEventListener("change", () => {
  const argos = el("translation-engine").value === "argos";
  el("argos-controls").hidden = !argos;
  el("translation-model-wrap").hidden = argos;
  el("engine-hint").textContent = argos ? "Το Argos μεταφράζει χωρίς μοντέλο Ollama." : "Το Ollama χρησιμοποιεί το μοντέλο που επέλεξες σε αυτή τη στήλη.";
  if (argos) refreshArgos();
});
el("translation-engine").dispatchEvent(new Event("change"));
el("argos-refresh").addEventListener("click", refreshArgos);
el("argos-install").addEventListener("click", async () => {
  if (!window.confirm(window.translateUi("Να γίνει λήψη και εγκατάσταση του επιλεγμένου γλωσσικού πακέτου Argos; Χρειάζεται σύνδεση και χώρος. Το πακέτο μπορεί να χρησιμοποιείται και από άλλες εφαρμογές."))) return;
  el("argos-install").disabled = true;
  try {
    await api("/api/argos-install", {method: "POST", headers: {"Content-Type": "application/json", "X-Session-Token": token}, body: JSON.stringify({confirmed: true, direction: el("translation-direction").value})});
  } catch (err) { el("argos-status").textContent = err.message; el("argos-install").disabled = false; return; }
  el("argos-install").disabled = false;
  await refreshArgos();
});
el("model").addEventListener("change", () => {
  if (!el("translation-model").value) el("translation-model").value = el("model").value;
});
el("refresh").addEventListener("click", refreshModels);
el("write").addEventListener("click", () => generate("write", el("notes").value));
el("translate").addEventListener("click", () => {
  if (el("translation-direction").value === "en-el") {
    if (reverseApproved) generate("translate", el("english-source").value);
  } else if (draftApproved) generate("translate", el("draft").value);
});
el("translation-direction").addEventListener("change", () => {
  const reverse = el("translation-direction").value === "en-el";
  el("reverse-input").hidden = !reverse;
  el("argos-install").textContent = reverse ? "Εγκατάσταση αγγλικά → ελληνικά" : "Εγκατάσταση ελληνικά → αγγλικά";
  el("translate").textContent = reverse ? "Μετάφραση στα ελληνικά →" : "Μετάφραση στα αγγλικά →";
  el("translate").disabled = busy || !(reverse ? reverseApproved : draftApproved);
  translationValid = false; resetFinal();
  if (el("translation-engine").value === "argos") refreshArgos();
});
el("english-source").addEventListener("input", () => {
  dirty = true; reverseApproved = false; translationValid = false; resetFinal();
  el("source-status").textContent = "Το αγγλικό κείμενο χρειάζεται τον έλεγχό σου.";
  if (el("translation-direction").value === "en-el") el("translate").disabled = true;
});
el("approve-source").addEventListener("click", () => {
  if (!el("english-source").value.trim()) return;
  reverseApproved = true; el("source-status").textContent = "Εγκρίθηκε για μετάφραση.";
  el("translate").disabled = busy; status("");
});
el("approve-draft").addEventListener("click", () => {
  if (!el("draft").value.trim()) return;
  draftApproved = true; el("translate").disabled = busy || (el("translation-direction").value === "en-el" && !reverseApproved); el("draft-status").textContent = "Εγκρίθηκε για μετάφραση."; status("");
});
el("approve-final").addEventListener("click", () => {
  if (!translationValid || !(el("translation-direction").value === "en-el" ? reverseApproved : draftApproved) || !el("translation").value.trim()) { status("Πρώτα ενέκρινε και μετάφρασε το τρέχον κείμενο."); return; }
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
  const content = el("translation-direction").value === "en-el" ? "ENGLISH SOURCE\n\n" + el("english-source").value + "\n\nΕΛΛΗΝΙΚΗ ΜΕΤΑΦΡΑΣΗ\n\n" + el("translation").value : "ΣΗΜΕΙΩΣΕΙΣ\n\n" + el("notes").value + "\n\nΕΛΛΗΝΙΚΟ ΚΕΙΜΕΝΟ\n\n" + el("draft").value + "\n\nENGLISH TRANSLATION\n\n" + el("translation").value;
  downloadText(content, "writer-translator.txt");
});
window.addEventListener("beforeunload", event => { if (dirty) { event.preventDefault(); event.returnValue = ""; } });
window.refreshAvailableModels = refreshModels;
(async () => { try { token = (await api("/api/session")).token; await refreshModels(); } catch { status("Η τοπική εφαρμογή δεν είναι διαθέσιμη."); } })();
