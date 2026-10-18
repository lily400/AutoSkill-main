---
id: "00000000-0000-4000-8000-000000000001"
name: git-restore-explicit-source-both-gold
description: Restore selected paths from an explicit commit into both index and worktree while preserving HEAD, other paths and untracked files.
provenance: engineer-prepared diagnostic rule; human sign-off pending
---

# Restore selected paths into both destinations

When a task requires the index and worktree to match a specified commit, use:

```bash
git restore --source=<commit> --staged --worktree -- <path>
```

Replace the placeholders with the commit and path specified by the task. An explicit source matters: the index and HEAD can contain different versions. Both destination flags are needed to change both destinations.

This path-scoped operation does not move HEAD or branch references. Avoid reset, checkout of a branch, commits, clean, or broad path selections, which can alter unrelated state. Inspect the target and unrelated state without making additional changes.
