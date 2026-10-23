# Project credential entry

The persistent API credential configuration is `configs/credentials.json`.
For Zhizengzeng, use `scripts/Invoke-ProjectCredential.ps1 -CheckOnly`, or its `-Action` wrapper for an authorized execution.
It loads the existing Windows CurrentUser DPAPI credential through `downstream_eval/integration/ZhizengzengCredential.ps1` and restores the process variable afterward.
An absent process/user environment variable does not mean the saved credential is missing. Check this configured loader before searching elsewhere or asking the user to enter a key.
Never print the credential or persist it as plaintext. The credential wrapper itself sends no model requests.
GitChameleon model calls require the case execution gate to pass first; retain the official generators, tasks, answers and tests.
