# Local Personal Writer and Translator

An early local prototype is under development for a personal, single-user Windows project. It can request a Greek draft from notes and an English translation through a locally installed Ollama model, with separate fields and human approval. Quality and full release readiness are not yet verified.

The intended profile is LOCAL_ONLY, with Ollama as the initial local inference provider. Originals remain separate from generated output; no automatic cloud inference or remote fallback is authorized. File access requires user authorization. Actual security and privacy properties require implementation and verification.

R0 covers project governance, requirements, architecture, risk and verification planning. R1 development has started at the owner's request; it is not approved for release. The prototype uses a local browser UI, Python standard library and local Ollama. It has no automatic text history and offers manual TXT downloads. Design-system adoption, model quality, packaging and distribution remain open. See [release scope](docs/product/RELEASE_SCOPE.md), [architecture](docs/architecture/SYSTEM_ARCHITECTURE.md) and [decisions](docs/architecture/ARCHITECTURE_DECISIONS.md).

Engineering Standards defines required outcomes, Framework/DNA the delivery approach, Shield security requirements, and Infrastructure shared infrastructure patterns; this project owns its implementation and evidence. See [source revisions](FOUNDATION_VERSIONS) and [adoption matrix](engineering/requirements/ENG_ADOPTION_MATRIX.md). The supplied [REP-001](docs/standards/REP-001.md), [SEC-001](docs/standards/SEC-001.md), [HLT-001](docs/standards/HLT-001.md) and [SAF-001](docs/standards/SAF-001.md) record approval on 10 November 2026. They match the supplied handoff checksums; fidelity to the original conversation remains unverified, as explained in the [initialization gate](checklists/INITIALIZATION_GATE.md).

## Try the development prototype

Requires an existing Python 3 installation and a running local Ollama with at least one local model. Double-click `Start Local Writer.bat` to open the application. Alternatively, from the repository root run:

```text
python app/server.py
```

Open the printed `http://127.0.0.1:…/` address in a browser. Keep the console open; press Ctrl+C to stop. No software or models are installed automatically. Unsaved text is lost when the session closes. The browser chooses where to save explicit TXT downloads; verify that they were saved. This is a prototype, not a release. Do not rely on generated text without reviewing it.

The standards provenance limitation, remaining security assessment, model evaluation and release readiness remain open.

### Manage Ollama models

Open **Διαχείριση μοντέλων** next to the model selector to see locally installed models, their sizes and the selected model. Refresh the list, enter a model name from the official Ollama library and explicitly confirm its download, or confirm deletion of an installed model. The link and downloads require internet access and disk space; the application does not verify names against the online library before a pull. The progress percentage is for the current download layer, not necessarily the entire model. Downloads continue while the application server is running even if the dialog is closed. Models are shared by local Ollama applications, so deletion affects those applications too. Each running app instance permits one generation, download or deletion at a time; separate app instances and other Ollama clients are not coordinated.

### Argos Translate (optional)

The translation panel offers Ollama or Argos. Argos uses the approved Greek draft directly and does not rewrite it with an LLM; check names, numbers, facts and meaning before approval. The Writer still uses the selected Ollama model. The Argos Python package and Greek-to-English language package must be available to the same `python` used by the launcher. The optional dependency is pinned in `requirements-argos.txt` (`argostranslate==1.11.0`); the application continues to work with Ollama if Argos is unavailable. To check the launcher environment, run `python -c "import sys; print(sys.executable)"` and `python -m pip show argostranslate`.

If the language package is missing, select Argos and explicitly confirm installation in the application. The official Argos package index and download require internet and write into the user's shared Argos package directory; no text is sent for this installation. Translation uses local models and an in-process sentence splitter, without downloading tokenizer resources. This simple sentence splitting can affect translation quality. Installation is not automatic. Paragraph and line breaks are preserved; output quality is not guaranteed. If the Python package itself is missing, install it in the launcher's Python environment only if desired, then restart the application.
