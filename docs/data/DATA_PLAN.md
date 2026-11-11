# Data plan

Originals, generated drafts and approved outputs are distinct logical data. The user owns them and chooses authorized import/export paths. No real personal data belongs in Git, test fixtures or logs. Synthetic data should be used for verification.

For the initial MVP the user selected no automatic text persistence or history. Original, draft and translation are session data; the user explicitly saves or exports what they wish to keep. Warn about unsaved work before leaving where the browser supports it; a warning cannot guarantee recovery after a crash or forced close. Exact export formats and implementation are still undecided (DEC-004). No durability, encryption or recovery after session loss is claimed. Failure and cancellation must preserve the original during the session. If persistent storage is later introduced, decide retention, protection, deletion and recovery and test restoration. Owner: project owner.
