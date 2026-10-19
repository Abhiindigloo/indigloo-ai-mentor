# Provenance — where this code came from

Initial import into **`Abhiindigloo/indigloo-ai-mentor`** on 2026-10-19.
Source repository (frozen archive): **`Abhiindigloo/ai-mentor`**.

History was **not** rewritten with `git filter-repo` for this first push (reliability over blame continuity). Line-level history remains on the frozen branches below. A future optional graft is out of scope for v0.

## Source commits

| Area | Path here | Source branch | Commit | Notes |
|---|---|---|---|---|
| Monorepo skeleton | (tree layout) | `refactor/monorepo-layout` (PR #3) | `32e5156` | Template only; not merged on legacy |
| Kotlin Android | `apps/android/` | `main` | `543700f` | Via PR #3 tree (same Kotlin sources) |
| Web PWA | `apps/web/` | `main` | `543700f` | **Minified** `.mjs` — deminify TBD |
| FastAPI | `services/api/` | `feature/ai-mentor-mvp` | `579fc06` | Via PR #3 `mentor_api` package layout |
| Curriculum | `packages/curriculum/curriculum.json` | `main` | `543700f` | 15 lessons; `board` field added at import |
| Training (no weights) | `training/` | `feature/ai-mentor-mvp` | `579fc06` | Manifests + scripts only |
| Postman | `packages/contracts/postman/` | `feature/ai-mentor-mvp` | `579fc06` | |
| CI hardening pattern | `.github/workflows/` | PR #2 / PR #3 | `3fe991b` / `32e5156` | Path filters rewritten for this repo |
| ADRs + migration | `docs/adr/`, `docs/MIGRATION_PLAN.md` | Local drafts | 2026-10-19 | Updated for **new-repo** strategy |

## Explicitly left out

- Java Android app (`feature/ai-mentor-mvp` `android/`) — ADR 0003
- Any `.env` secrets, keystores, or model weight binaries
- Open PRs / comments on the legacy repo (untouched)

## How to compare

```bash
# On a machine with the legacy clone (read-only fetch is fine):
git -C ai-mentor show 543700f:android/app/src/main/java/co/indigloo/mentor/Vault.kt
git -C ai-mentor show 579fc06:backend/tutor.py
```
