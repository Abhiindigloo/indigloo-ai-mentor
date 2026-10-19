# ADR 0003 — One Android app (Kotlin); retire the Java app

- **Status:** Accepted
- **Date:** 2026-10-19
- **Decider:** Owner (Indigloo)

## Context
Two Android apps exist, both package `co.indigloo.mentor`, minSdk 26, targetSdk 35:

| | Kotlin app (`main` `android/`, PR #3 `apps/android/`) | Java app (`feature/ai-mentor-mvp` `android/`) |
|---|---|---|
| UI | WebView over bundled `apps/web` via `WebViewAssetLoader`; file/content access off | Native views |
| Storage | `Vault.kt`: Keystore AES-GCM key, `AtomicFile` `learning.enc` | Room (`MentorDb`, `Practice`, `PracticeDao`), ≤ 500 turns, **unencrypted** |
| AI | LiteRT-LM `litertlm-android` 0.8.0, CPU, `maxNumTokens=1024`, refuses < 3 GB RAM, user-imported `mentor.litertlm` | none |
| OCR / TTS | ML Kit Latin + Devanagari 16.0.1; Android TTS | same |
| Network | INTERNET + ACCESS_NETWORK_STATE removed | `ApiClient` (24 lines): register/login, `/v1/sessions`, `/v1/chat`, token in memory only; account menu: erase local, sign out, delete server account |
| Build | AGP 8.9.2, Kotlin 2.1.10, Gradle 8.11.1, JDK 21; versionCode 2 / 0.1.1 | Groovy Gradle, JDK 17; versionCode 1 / 0.1.0 |
| Tests | none (`src/test` absent) | `LocalTutorTest` (2 tests) |

## Decision
`apps/android` (Kotlin) is the only Android app. The Java app is retired and not carried into the monorepo tree (it stays in git history via `579fc06`). These behaviours are ported into the Kotlin/web stack:
1. **Sign-in flow** from `ApiClient.java` — re-implemented against the generated Kotlin client from `packages/contracts`, with HTTPS-only origin (debug may allow `http://10.0.2.2:8000`), and a refresh token stored under a Keystore key instead of memory-only.
2. **Account deletion** (`DELETE /v1/me`) and **local erase** — exposed in the web UI via the native bridge.
3. **Room practice log** — not ported as Room; practice turns go into the encrypted vault (`Vault.kt`) state, bounded (500 entries, as today), later feeding the sync outbox.

## Alternatives considered
- **Keep the Java app:** native UI, but duplicates the web app, lacks vault and on-device AI, and stores child data unencrypted.
- **SQLCipher/Room with Keystore-held key:** reasonable if relational offline queries become necessary; deferred — vault blobs suffice for 500 entries.
- **Two apps (lite + full):** doubles QA and store listings.

## Consequences
- **Positive:** one encrypted store, one UI codebase shared with the browser, on-device AI path retained.
- **Negative:** WebView-based UI depends on the device's WebView version; performance on 2–3 GB phones is unverified (Gate G1).
- **Negative:** needs network permission back (ADR 0004) to use the ported sign-in; this changes the app's privacy posture and Play data-safety declaration.
- **Negative:** Kotlin app has zero unit tests; adding them is part of this migration.
- `web/*.mjs` on `main` is committed minified (e.g. `apps/web/app.mjs` 36 lines, longest line ~4 KB on PR #3) — must be de-minified before porting features into it.

## Follow-ups
- Add `apps/android/app/src/test` (vault round-trip, bridge id validation, RAM/storage prechecks).
- Retire the Java app: confirm no references remain; archive `feature/ai-mentor-mvp` only after its history is merged into `main` (human decision; deleting a branch is irreversible).
