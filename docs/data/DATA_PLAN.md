# Data plan

Originals, generated drafts and approved outputs are distinct logical data. The user owns them and chooses authorized import/export paths. No real personal data belongs in Git, test fixtures or logs. Synthetic data should be used for verification.

Persistence, history, retention, storage location, backup and deletion semantics depend on DEC-003 and DEC-004. Until resolved, no durability, encryption or recoverability is claimed. Failure and cancellation must preserve the original; restoration must be tested if persistent storage is introduced. Owner: project owner.
