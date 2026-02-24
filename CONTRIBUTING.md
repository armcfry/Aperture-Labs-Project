# Contributing & Merge Guide

Guidelines for what to merge into `main` and what to skip.

## Merge into `main`

| Type | Examples |
|------|----------|
| **Features** | New functionality, UI improvements, API integration |
| **Bug fixes** | Fixes for broken behavior or crashes |
| **Documentation** | README updates, API docs, run instructions |
| **Dependencies** | Security updates, required package changes |
| **Refactors** | Code cleanup that preserves behavior |

**Before merging:** Ensure the change is used by the app and adds value.

---

## Do NOT merge into `main`

| Type | Examples | Why |
|------|----------|-----|
| **Unused assets** | `file.svg`, `globe.svg`, `next.svg`, `vercel.svg`, `window.svg` | Default Next.js template files not referenced anywhere |
| **Boilerplate noise** | Unchanged template files, placeholder content | Adds clutter without benefit |
| **WIP / experimental** | Half-finished features, broken builds | Not production-ready |
| **Duplicate changes** | Same fix already in another PR | Causes merge conflicts |

**Rule of thumb:** If it's not imported, linked, or used anywhere—don't merge it.

---

## Quick checklist before merging a PR

- [ ] Code builds (`npm run build` succeeds)
- [ ] Changes are actually used (no dead code or unused assets)
- [ ] No default template clutter (e.g. unused SVGs from create-next-app)
- [ ] Documentation updated if behavior changed

---

## Branch workflow

```
main (production-ready)
  └── scrum-2-setup-frontend (feature branch)
  └── other feature branches...
```

Merge feature branches into `main` when they meet the criteria above.
