# Architecture decisions

Owner for decisions: project owner. Pending decisions block development readiness until resolved or explicitly scoped out with justification.

| ID | Decision |
|---|---|
| DEC-001 | **PROTOTYPE:** Python standard library loopback server and plain HTML/CSS/JavaScript; Ollama runs separately. Long-term stack and release adoption remain subject to review. |
| DEC-002 | **DECIDED:** local browser-based UI, selected by the project owner on 2026-11-10. The prototype uses a Python loopback server and plain browser assets; supported browsers and the long-term technology remain to be assessed. |
| DEC-003 | **DECIDED for initial MVP:** no automatic history or persistence of text; the user explicitly saves or exports desired work. Unexported work may be lost when the session ends. The user selected this simpler option on 2026-11-11. Any future persistence requires a separate decision. |
| DEC-004 | **PROTOTYPE:** explicit browser TXT downloads for notes, Greek draft and the approved translation bundle. Other formats remain undecided. |
| DEC-005 | UI/UX technology and design-system adoption. |
| DEC-006 | **PARTIALLY OBSERVED:** 15.7 GiB reported RAM, Intel i7-13620H and Intel UHD integrated graphics. Ollama listed gemma4:latest, llama3.1:latest, qwen2.5:0.5b, gpt-oss:20b, gemma3:4b, qwen3:8b, qwen3:4b, qwen2.5-coder:7b and qwen2.5-coder:3b on 2026-11-10. Suitability, inference speed, model choice and memory budget remain unverified. Recheck before use. |
| DEC-007 | Packaging, updates and distribution. |

Approved constraints: personal single user, Windows, LOCAL_ONLY, initial local Ollama, original preservation, human approval and no automatic cloud fallback. These constraints do not select an implementation.
