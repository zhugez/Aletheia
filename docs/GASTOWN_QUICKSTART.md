# Gas Town Quickstart for Aletheia (Codex-first)

This guide documents the minimal workflow used to run Aletheia in a multi-agent workspace with Gas Town.

## 1) Prerequisites

- `gt` (Gas Town CLI)
- `bd` (beads CLI)
- `dolt`
- `codex` CLI

## 2) Workspace layout

- HQ: `/root/gt`
- Rig: `/root/gt/aletheia`
- Crew workspace: `/root/gt/aletheia/crew/yasna`

## 3) Codex as agent runtime

```bash
gt config agent set codex codex
gt config agent get codex
```

## 4) Start services

```bash
cd /root/gt
gt up
```

Check health:

```bash
gt status
gt health
```

## 5) Daily flow (Aletheia)

```bash
cd /root/gt/aletheia/crew/yasna

# inspect pending work
bd list || true

# run coding session with Codex
codex

# after change
git status
git add -A
git commit -m "docs: update gastown quickstart"
git push
```

## Notes

- If Dolt/beads server is unstable, rig git workspaces still function for coding.
- For production use, keep Dolt healthy first, then rely on beads for issue/state persistence.
