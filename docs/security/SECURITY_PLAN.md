# Security plan

Shield is the security authority; assess applicable controls at the pinned revision in [FOUNDATION_VERSIONS](../../FOUNDATION_VERSIONS) and keep security exceptions under Shield governance. No private controls are copied here. Owner: project owner; security reviewer to be assigned.

Before R1 approval, assess personal-text handling, local provider and any loopback boundary, filesystem permissions, dependencies, logs, model provenance and updates. Design for explicit file authorization, minimal disclosure, original preservation and fail-closed provider errors. Verify with synthetic data, network observation and negative tests appropriate to the chosen stack. Applicable Shield controls and evidence remain unassessed; this plan is not security verification.

Prototype evidence: server binds 127.0.0.1 and verifies Host, Origin and a random session token for generation. Its fixed Ollama client disables proxy use, filters cloud-designated and remote models, and rechecks the model before generation. Focused synthetic HTTP tests cover rejected origins, host names and tokens. These checks do not prove the complete privacy or security of the environment, browser, Ollama or models. Complete Shield applicability assessment, model-origin and network verification remain open.
