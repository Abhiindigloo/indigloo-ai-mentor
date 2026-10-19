# ADR 0001 — Monorepo layout (new public repo)

- **Status:** Accepted
- **Date:** 2026-10-19
- **Decider:** Owner (Indigloo)
- **Supersedes:** the earlier draft `docs/adr/0001-monorepo-layout.md` (Accepted 2026-10-18) on branch `refactor/monorepo-layout` / PR #3 of `Abhiindigloo/ai-mentor`, and the interim plan to rebuild that PR on the legacy repo.

## Context
- Work split into two lines on 12 Oct 2026 (common ancestor `14a8ac2`) in `Abhiindigloo/ai-mentor`:
  - `main` (`543700f`, v0.1.1): Kotlin WebView app, vanilla-JS web app, AES-GCM Keystore vault, optional on-device LiteRT-LM, no backend, INTERNET permission removed.
  - `feature/ai-mentor-mvp` (`579fc06`, v0.1.0): FastAPI + SQLite, Java Android app (Room), separate web client, Postman, LoRA training pilot.
- PR #3 (`refactor/monorepo-layout` → `main` on the legacy repo) already sketched a monorepo close to this decision, but continuing on `ai-mentor` would entangle open PRs (#1–#3), dual Android apps, and divergent history.
- **Owner decision (2026-10-19):** ship a **brand-new public repository** `Abhiindigloo/indigloo-ai-mentor` as the canonical monorepo. Leave `Abhiindigloo/ai-mentor` completely untouched (frozen archive / pre-monorepo reference). Do not open PRs, commits, or comments on the legacy repo for this migration.

## Decision
One repository, **`Abhiindigloo/indigloo-ai-mentor`**, with this layout:

| Path | Contents | Origin |
|---|---|---|
| `services/api/` | FastAPI service (`mentor_api` package), tests, Dockerfile | `feature/ai-mentor-mvp` `backend/` (via PR #3 tree at `32e5156`) |
| `apps/web/` | Learner PWA; also bundled into the Android APK as `assets/www` by `scripts/sync-assets.mjs` | `main` `web/` |
| `apps/android/` | Kotlin app: WebView shell, Keystore vault, OCR, TTS, on-device LiteRT-LM | `main` `android/` |
| `packages/curriculum/` | **Single source** lesson pack + JSON Schema + `bands.json` | `main` `web/curriculum.json` |
| `packages/contracts/` | **Source of truth** OpenAPI + JSON Schemas for sync events and the model catalogue | seeded from feature/PR #3 OpenAPI; hand-extended |
| `training/` | Fine-tuning code, data prep, eval sets and **model manifests only**; weights never in git | `feature/ai-mentor-mvp` `training/` |
| `docs/` | Architecture, privacy, safety, ADRs, migration plan, provenance | drafted + ported |
| `.github/workflows/` | Path-filtered jobs per area | adapted from PR #2 / PR #3 |

Rules:
- Contract-first: endpoint/event changes start in `packages/contracts`.
- Generated copies (e.g. `apps/web/curriculum.json`, Android `assets/www/**`) are produced by one script and checked for drift in CI.
- Readable source is preferred; minification at build time only. Current `apps/web/*.mjs` is still minified (TBD deminify — see MIGRATION_PLAN).
- **No secrets in the repo.** `MODEL_API_KEY` and similar stay in env / secret manager only.
- The Java Android app from `feature/ai-mentor-mvp` is **not** ported as a second app (ADR 0003).

## Alternatives considered
- **Rebuild PR #3 on `ai-mentor` (history merge):** rejected in favour of a clean public monorepo; legacy repo stays frozen.
- **Two/three repos** (api, apps, curriculum): multi-repo coordination cost too high pre-pilot.
- **Keep the feature branch as canonical:** discarded; owner chose FastAPI + Kotlin in one tree.

## Consequences
- **Positive:** clear canonical home; legacy `ai-mentor` remains a readable archive without risk of accidental pushes during migration.
- **Positive:** lesson, contract and client changes land atomically; path filters keep Android builds off API-only PRs.
- **Negative:** git blame for FastAPI/Kotlin lines starts at the import commit in this repo (see `docs/PROVENANCE.md`); full line history remains on the frozen `ai-mentor` branches.
- **Negative:** clients do not call the API until INTERNET is restored (ADR 0004) and sync ships.

## Follow-ups
- Path-filtered CI + aggregate `ci-ok` check (initial workflows land with this repo).
- Hand-authored OpenAPI + model catalogue + sync stubs in `packages/contracts`.
- Curriculum JSON Schema + `bands.json` (K–5 / 6–8 / 9–12).
- Deminify `apps/web`; gate answer-leak modes before pilot (see `docs/SAFETY.md`).
