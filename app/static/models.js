"use strict";
(() => {
  const get = id => document.getElementById(id);
  const dialog = get("models-dialog");
  let sessionToken = "", operationBusy = false, pulling = false, timer = null, models = [];

  async function request(path, options = {}) {
    const response = await fetch(path, options);
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Η ενέργεια απέτυχε.");
    return data;
  }
  function message(text) { get("models-message").textContent = text; }
  function sizeLabel(size) {
    if (typeof size !== "number" || size < 0) return "Μέγεθος μη διαθέσιμο";
    if (size < 1_000) return size + " B";
    if (size < 1_000_000) return (size / 1_000).toFixed(0) + " KB";
    if (size >= 1_000_000_000) return (size / 1_000_000_000).toFixed(1) + " GB";
    return (size / 1_000_000).toFixed(0) + " MB";
  }
  function updateControls() {
    get("model-install").disabled = pulling || operationBusy;
    get("model-name").disabled = pulling || operationBusy;
    document.querySelectorAll(".model-delete").forEach(button => { button.disabled = pulling || operationBusy; });
  }
  function renderModels() {
    const list = get("models-list");
    list.replaceChildren();
    if (!models.length) {
      const empty = document.createElement("li");
      empty.textContent = "Δεν βρέθηκαν τοπικά εγκατεστημένα μοντέλα.";
      list.append(empty);
    }
    for (const model of models) {
      const row = document.createElement("li"), info = document.createElement("div");
      const name = document.createElement("strong"), details = document.createElement("span");
      const remove = document.createElement("button");
      row.className = "model-row"; info.className = "model-row-info";
      name.textContent = model.name;
      details.textContent = sizeLabel(model.size) + (get("model").value === model.name ? " · Επιλεγμένο" : "");
      remove.type = "button"; remove.className = "model-delete"; remove.textContent = "Διαγραφή";
      remove.setAttribute("aria-label", "Διαγραφή μοντέλου " + model.name);
      remove.addEventListener("click", () => deleteModel(model.name));
      info.append(name, details); row.append(info, remove); list.append(row);
    }
    updateControls();
  }
  function renderJob(job) {
    pulling = job.state === "running";
    const bar = get("model-progress"), detail = get("model-progress-detail");
    if (job.state === "idle") {
      get("model-job-status").textContent = "Δεν υπάρχει ενεργή λήψη.";
      bar.hidden = true; detail.textContent = "";
    } else {
      get("model-job-status").textContent = (job.model ? job.model + " · " : "") + job.status;
      bar.hidden = job.state !== "running";
      if (job.state === "running" && job.total > 0) {
        const percent = Math.max(0, Math.min(100, Math.floor(job.completed * 100 / job.total)));
        bar.value = percent;
        detail.textContent = "Τρέχον αρχείο: " + percent + "% (" + sizeLabel(job.completed) + " / " + sizeLabel(job.total) + ").";
      } else if (job.state === "running") {
        bar.removeAttribute("value");
        detail.textContent = "Αναμονή για στοιχεία προόδου από το Ollama.";
      } else { detail.textContent = ""; }
    }
    updateControls();
  }
  async function loadModels(syncSelector = false) {
    if (syncSelector) await window.refreshAvailableModels();
    const data = await request("/api/model-management");
    models = data.models;
    renderModels();
    renderJob(data.job);
    return data.job;
  }
  async function poll() {
    clearTimeout(timer);
    try {
      const job = await request("/api/model-job", {headers: {"X-Session-Token": sessionToken}});
      renderJob(job);
      if (job.state === "running") { timer = setTimeout(poll, 1000); return; }
      await loadModels(true);
      message(job.status);
    } catch (error) {
      updateControls();
      message("Δεν ήταν δυνατή η ενημέρωση της λήψης. Ανανέωσε τη λίστα για να ελέγξεις την κατάσταση. " + error.message);
    }
  }
  async function installModel() {
    const model = get("model-name").value.trim();
    if (!model) { message("Πληκτρολόγησε το όνομα του μοντέλου."); return; }
    if (!window.confirm("Να ληφθεί το «" + model + "» μέσω Ollama; Η λήψη χρησιμοποιεί διαδίκτυο και χώρο στον δίσκο.")) return;
    operationBusy = true; updateControls(); message("");
    try {
      const job = await request("/api/model-install", {
        method: "POST", headers: {"Content-Type": "application/json", "X-Session-Token": sessionToken},
        body: JSON.stringify({model})
      });
      renderJob(job);
      operationBusy = false; updateControls();
      await poll();
    } catch (error) { message(error.message); }
    finally { operationBusy = false; updateControls(); }
  }
  async function deleteModel(model) {
    const selected = get("model").value === model;
    const warning = selected ? " Είναι το μοντέλο που έχεις επιλέξει." : "";
    if (!window.confirm("Να διαγραφεί το «" + model + "» από το τοπικό Ollama; Δεν θα είναι διαθέσιμο ούτε σε άλλες εφαρμογές που το χρησιμοποιούν." + warning)) return;
    operationBusy = true; updateControls(); message("");
    try {
      await request("/api/model-delete", {
        method: "POST", headers: {"Content-Type": "application/json", "X-Session-Token": sessionToken},
        body: JSON.stringify({model, confirmed: true})
      });
      await loadModels(true);
      message("Το μοντέλο διαγράφηκε.");
    } catch (error) { message(error.message + " Ανανέωσε τη λίστα για να ελέγξεις την κατάσταση."); }
    finally { operationBusy = false; updateControls(); }
  }
  get("manage-models").addEventListener("click", async () => {
    dialog.showModal(); message(""); operationBusy = true; updateControls();
    try {
      sessionToken = (await request("/api/session")).token;
      const job = await loadModels();
      if (job.state === "running") await poll();
    } catch (error) { message(error.message); }
    finally { operationBusy = false; updateControls(); }
  });
  get("models-close").addEventListener("click", () => dialog.close());
  get("models-refresh").addEventListener("click", async () => {
    try { await loadModels(true); message("Η λίστα ενημερώθηκε."); }
    catch (error) { message(error.message); }
  });
  get("model-install").addEventListener("click", installModel);
  get("model").addEventListener("change", renderModels);
})();
