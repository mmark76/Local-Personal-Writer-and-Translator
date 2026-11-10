# Risk register

Owner for each risk: project owner; review at R1 readiness.

| ID | Risk | Planned treatment | Status |
|---|---|---|---|
| R-01 | Supplied approved standards are transcriptions without a machine-verifiable comparison against the original conversation. | Project owner to compare with original approved drafts or explicitly resolve the provenance limitation; complete consistency review. | OPEN; blocks R0 acceptance. |
| R-02 | Local text is disclosed or acted on unexpectedly. | Shield assessment, explicit file authorization, network and negative tests. | OPEN. |
| R-03 | Original is lost or overwritten. | Separate source lifecycle; failure and recovery tests. | OPEN. |
| R-04 | Translation changes meaning or voice. | Human review and representative bilingual evaluation. | OPEN. |
| R-05 | Model or hardware is unavailable or unsuitable. | Verify actual environment and define performance criteria. | OPEN. |
| R-06 | Fetch in the sandbox failed to start the credential helper. | Authenticated fetch and remote-head listing succeeded through Desktop Commander on 2026-11-10; recheck before future Git writes. | MITIGATED for this task; sandbox limitation remains. |
| R-07 | Personal data outside designated ignored paths could be staged inadvertently. | Keep personal documents and history outside the repository; ignored private/local-data/backup paths and database patterns add protection. Review the actual storage design and staged files before use. | OPEN. |
