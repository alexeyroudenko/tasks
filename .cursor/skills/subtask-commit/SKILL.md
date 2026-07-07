---
name: subtask-commit
description: Workflow for implementing roadmap subtasks one at a time with a separate commit and push per subtask. Use when working on ROADMAP.md items in this repository, or when the user asks to continue the port, do the next subtask, or commit work incrementally.
---

# Subtask-per-commit workflow

## Workflow

Copy this checklist for each subtask and track progress:

```
- [ ] Step 1: Pick the first unchecked item in ROADMAP.md
- [ ] Step 2: Implement it (see .cursor/skills/port-code-red/SKILL.md for domain mapping)
- [ ] Step 3: Verify: run lints/tests relevant to the change
- [ ] Step 4: Mark the item done in ROADMAP.md
- [ ] Step 5: Commit and push
```

## Commit rules

- One roadmap subtask = one commit. Do not batch several subtasks into one commit.
- Include the ROADMAP.md checkbox update in the same commit as the implementation.
- Push to `origin master` after each commit.
- Conventional commit messages, imperative mood:

**Example 1:** scaffolding subtask →

```
feat: scaffold backend, frontend and docker-compose
```

**Example 2:** bug found during a subtask →

```
fix(graph): escape single quotes in Cypher string literals
```

## Git specifics for this machine

- `GITHUB_TOKEN` in the environment is invalid and overrides working keyring auth. Before any `gh` call, run `Remove-Item Env:GITHUB_TOKEN -ErrorAction SilentlyContinue`. Plain `git push` works without this.
- PowerShell: use `;` instead of `&&` to chain commands.
