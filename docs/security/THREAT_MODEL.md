# Threat model — preliminary

Assets: user originals, generated text, authorized exports and configuration. Actors include the user, local processes, malicious input and compromised dependencies or model artifacts. Trust boundaries include user-to-UI, application-to-local Ollama, filesystem and dependency supply chain; exact processes and interfaces are pending.

| Threat | Planned response | Evidence needed |
|---|---|---|
| Unintended remote disclosure | Local-only provider; no fallback; inspect actual network behavior. | Negative and network tests on chosen implementation. |
| Original overwritten or output mistaken for original | Separate lifecycle and explicit approval; test failure and cancellation. | Synthetic preservation and recovery tests. |
| Prompt content induces unintended actions | Treat source/model output as untrusted; no unauthorized file actions. | Adversarial synthetic tests and permission review. |
| Local unauthorized access or logs expose text | Assess Windows-user boundary, storage and logs under Shield. | Design review and evidence for actual environment. |
| Untrusted dependency/model | Evaluate provenance and updates before use. | Inventory and security review. |

Owner: project owner; security reviewer pending. Risk is not eliminated by this plan.
