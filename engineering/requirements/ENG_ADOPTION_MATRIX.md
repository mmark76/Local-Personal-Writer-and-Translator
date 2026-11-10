# Engineering adoption matrix

Authority: [Engineering Requirements at the observed revision](https://github.com/mmark76/Ecosystem-Engineering-Standards/blob/3bc6e9222ce4385af86a785148e00748fb4f4230/ENGINEERING-REQUIREMENTS.md). These are project plans, not a replacement for normative text. Owner for each row: project owner; implementation and review assignees pending. Applicability is provisional and must be reassessed against the supplied project standards and resolved decisions. No row is VERIFIED.

| ID | Applicability and plan | Verification / evidence still needed | Status |
|---|---|---|---|
| ENG-ARCH-001 | Applicable: assign UI, domain, provider and data responsibilities. | Review actual component ownership. | PLANNED |
| ENG-ARCH-002 | Applicable: define data, interfaces and permitted dependencies. | Interface and dependency review. | PLANNED |
| ENG-ARCH-003 | Applicable: isolate domain from UI and provider implementations. | Inspect dependency direction and cycles. | PLANNED |
| ENG-ARCH-004 | Applicable: justify architecture against actual need. | Review selected design. | PLANNED |
| ENG-MAINT-001 | Applicable: maintain clear, testable implementation. | Code and test review. | PLANNED |
| ENG-MAINT-002 | Applicable: investigate root causes of defects. | Review change and regression evidence. | PLANNED |
| ENG-DEBT-001 | Applicable: record debt, owner and treatment. | Review maintained register. | PLANNED |
| ENG-API-001 | Applicable: specify material interface contracts and errors. | Review contracts and integration tests. | PLANNED |
| ENG-API-002 | Applicable: assess breaking changes and supported consumers. | Review compatibility or deprecation records as needed. | PLANNED |
| ENG-TEST-001 | Applicable: automate critical logic and boundary checks. | Repeatable test results. | PLANNED |
| ENG-DOC-001 | Applicable: maintain architecture, operations and decisions. | Review against actual implementation. | PLANNED |
| ENG-DATA-001 | Conditional: if persistence is chosen, define versioned evolution and recovery. | Decision and migration/recovery tests if applicable. | PLANNED |
| ENG-REL-001 | Applicable: define local provider and partial-failure recovery. | Failure and preservation tests. | PLANNED |
| ENG-OBS-001 | Applicable: define local diagnostics without exposing personal text. | Operational and privacy review. | PLANNED |
| ENG-PERF-001 | Applicable: define realistic model, hardware and measurable criteria. | Representative performance results. | PLANNED |
| ENG-CONF-001 | Applicable: document and validate local runtime configuration. | Configuration and failure tests. | PLANNED |
| ENG-DEP-001 | Applicable: inventory and assign dependency lifecycle. | Dependency review and update plan. | PLANNED |
| ENG-DEP-002 | Applicable: isolate Ollama provider behavior behind an owned boundary. | Interface and provider failure tests. | PLANNED |
| ENG-SEC-001 | Applicable: assess controls governed by [Shield](https://github.com/mmark76/Ecosystem-Security-The-Shield/tree/a8ef59f1689c9a0fc0a233ed94b5a52e79a426ac). | Scoped Shield assessment and evidence; security exceptions follow Shield. | PLANNED |

No requirement is currently claimed NOT_APPLICABLE or excepted. R0 has no runtime or persistent schema; conditional applicability must be resolved when R1 scope is approved.
