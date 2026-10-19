# Indigloo AI Mentor

**K-12 Agentic AI Mentor** — a multilingual (English + Hindi first), Socratic tutor for students on low-cost Android phones and the web. Thin cloud, thick edge: guided lessons work offline; optional on-device LiteRT-LM; FastAPI backend for accounts, sessions and (later) sync / model catalogue.

> **Canonical monorepo.** Legacy pre-monorepo archive: [`Abhiindigloo/ai-mentor`](https://github.com/Abhiindigloo/ai-mentor) (frozen — do not use for new work).

## Layout

```
services/api/           FastAPI + SQLite backend
apps/web/               Learner PWA (also bundled into the Android APK)
apps/android/           Kotlin app (WebView + Keystore vault + LiteRT-LM)
packages/curriculum/    Lesson pack + JSON Schema + bands (single source)
packages/contracts/     OpenAPI + sync / model-catalogue schemas
training/               Fine-tune scripts + manifests only (no weight files)
docs/                   ADRs, migration plan, provenance, safety
docs/ci/ci.yml           Path-filtered CI (copy to .github/workflows/ — needs workflow scope)
```

Architecture decisions: [`docs/adr/`](docs/adr/). Migration & gates: [`docs/MIGRATION_PLAN.md`](docs/MIGRATION_PLAN.md). Import provenance: [`docs/PROVENANCE.md`](docs/PROVENANCE.md). Pre-pilot safety: [`docs/SAFETY.md`](docs/SAFETY.md).

## Owner decisions encoded here

- **FastAPI only** (no Spring Boot) — ADR 0002
- **One Kotlin Android app** (Java app not ported) — ADR 0003
- **Model delivery:** single APK; download after onboarding (age band + board); CBSE pilot; bands K–5 / 6–8 / 9–12 — ADR 0004–0006
- **INTERNET:** still removed in the Android manifest for this first commit (offline path intact); restore later under Gate G-NET — ADR 0004
- **No secrets in git**

## Quick start

Requirements: Node ≥ 20, Python 3.12, JDK 21 + Android SDK 35 (Android only).

```bash
npm test                 # web logic + CI config checks
npm run sync             # after editing apps/web or packages/curriculum — commit the result
```

### API

```bash
cd services/api
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt pytest==8.3.5
python -m pytest -q
python -m uvicorn mentor_api.app:app --host 127.0.0.1 --port 8000
# http://127.0.0.1:8000/app/  http://127.0.0.1:8000/docs
```

Or from repo root: `cp .env.example .env && docker compose up --build -d` (binds `127.0.0.1:8000`).

Env (server-side only): `DATABASE_PATH`, `CURRICULUM_PATH`, `WEB_DIR`, optional `MODEL_BASE_URL` / `MODEL_NAME` / `MODEL_API_KEY`. Never commit real keys.

### Web PWA (offline guest)

```bash
python3 -m http.server 8000 --directory apps/web
```

Note: `apps/web/*.mjs` is currently minified — deminify is tracked in the migration plan.

### Android

```bash
npm run sync
cd apps/android && ./gradlew testDebugUnitTest assembleDebug
adb install -r app/build/outputs/apk/debug/app-debug.apk
```

Set `ANDROID_HOME` or `apps/android/local.properties`. Package `co.indigloo.mentor`, Android 8+. Release signing keys are not included.

## GitHub Actions

Path-filtered CI is authored at [`docs/ci/ci.yml`](docs/ci/ci.yml) (api / web / android / docs + aggregate `ci-ok`). The initial push could not write `.github/workflows/` because the available OAuth token lacks the `workflow` scope. Copy that file into `.github/workflows/ci.yml` with a credential that has `workflow` scope to turn Actions on (see [`.github/README.md`](.github/README.md)).

## Current limitations

- Web/Android do **not** call the backend yet (INTERNET removed; sync not shipped).
- Answer / steps / example modes are **not gated** — must be before any student pilot (`docs/SAFETY.md`).
- Curriculum is illustrative CBSE-oriented content, not teacher-signed.
- No parental-consent flow or age gate yet.

## Licence / fonts

Noto Sans Devanagari under `apps/web/fonts/OFL.txt`. Third-party dependencies retain their own licences.
