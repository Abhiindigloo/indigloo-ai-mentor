# Migration plan — new monorepo (`indigloo-ai-mentor`)

- **Date:** 2026-10-19
- **Implements:** ADR 0001–0006; open items in ADR 0007
- **Canonical repo:** https://github.com/Abhiindigloo/indigloo-ai-mentor
- **Legacy archive:** https://github.com/Abhiindigloo/ai-mentor — **frozen**. Do not open PRs, push commits, or leave comments there for this work.
- **Rule for every step after the initial import:** new branch → PR → green CI → **human merge**. Prefer not to push directly to `main` once branch protection is on. One concern per PR. Never rewrite someone else's pushed history without the owner's OK.

## Strategy change (vs earlier draft)

Earlier drafts planned to rebuild PR #3 on `ai-mentor`. **Owner decision O18:** create this new public monorepo instead. Code is imported cleanly with provenance (see `docs/PROVENANCE.md`). PR #3 on the legacy repo is a **structure hint only**, not something to merge there.

## 0. Starting point (verified 2026-10-19)

| Source | Ref | What we took |
|---|---|---|
| Legacy `main` | `543700f` | Kotlin Android, web PWA (minified), curriculum |
| Legacy `feature/ai-mentor-mvp` | `579fc06` | FastAPI, training manifests, Postman |
| Legacy PR #3 tree | `32e5156` | Monorepo path layout used as import template |
| Drafted docs | `/workspace/ai-mentor-docs` | ADRs 0001–0007 + this plan (updated for new-repo) |

**Not ported:** Java Android app (ADR 0003); any secrets; model weight files.

## Go/no-go gates (owner-accepted risks)

| Gate | Before | Go criteria | No-go response |
|---|---|---|---|
| **G0 Single green main** | Feature work beyond import | `main` has monorepo layout, path-filtered CI green, branch protection requires aggregate check | Fix CI; no feature PRs |
| **G1 Low-end devices** | Choosing on-device model family (O1) / publishing catalogue | Measured on real 2/3/≥4 GB phones | Lesson-only mode for that RAM tier |
| **G2 Cost ceiling ($0.01 / student-hour)** | Any cloud LLM for students | Edge-first router + budget governor; measured cost | Cloud stays disabled |
| **G3 Hindi ASR/OCR** | Voice input / Hindi handwriting claims | Multilingual ASR + ML Kit Devanagari on children's data (consent) | Hide voice; label OCR best-effort |
| **G4 Child safety & compliance** | **Any pilot with real students** | DPDP consent, age gate, teacher-reviewed CBSE, **answer/steps/example gated**, PII scrub, guardrails, DPIA, notices, VAPT, runbook | No pilot |
| **G-NET Network release** | First release with INTERNET restored | Host allowlist + tests; cleartext off; WebView asset-host only; Play data-safety updated | Keep INTERNET removed in release |

---

## Phase 0 — Done at repo creation
| Step | Action | Status |
|---|---|---|
| 0.1 | Create public `Abhiindigloo/indigloo-ai-mentor`; freeze `ai-mentor` | Done (this import) |
| 0.2 | Layout: `services/api`, `apps/web`, `apps/android`, `packages/*`, `training`, `docs`, workflows | Done |
| 0.3 | ADRs + migration plan reflecting new-repo strategy | Done |
| 0.4 | Curriculum schema + bands; OpenAPI skeleton + catalogue + sync stubs | Done (stubs) |
| 0.5 | Path-filtered CI (api / web / android / docs) | Authored at `docs/ci/ci.yml`; enable under `.github/workflows/` when `workflow` scope available |

## Phase 1 — Harden import (follow-up PRs)
| Step | Scope | Acceptance |
|---|---|---|
| 1.1 | Deminify `apps/web/*.mjs` (lines today up to ~4 KB); build-time minify for assets only | `core.test.mjs` + sync drift green; no source line > 160 chars |
| 1.2 | Add `board: "CBSE"` to every lesson; CI validates against schema | Invalid fixtures fail |
| 1.3 | Wire OpenAPI drift check (running `/openapi.json` vs `packages/contracts/openapi.yaml`) | CI fails on drift |
| 1.4 | Android unit-test baseline (`Vault`, bridge id, RAM precheck) | `testDebugUnitTest` ≥ 1 test green |
| 1.5 | Branch protection on `main` (human): require `ci-ok`, review | Direct push rejected |

## Phase 2 — Safety baseline (**non-negotiable before pilot**)
| Step | Scope | Acceptance |
|---|---|---|
| 2.1 | Gate `answer` / `steps` / `example` / "show answer" paths in web + API (see `docs/SAFETY.md`) | 5 en + 5 hi "just tell me" phrasings return no final answer; unlock only after verified attempt or teacher policy |
| 2.2 | Prompt-injection in question/OCR cannot unlock reveal | Tests green |

## Phase 3 — Bands UI + API grade check (ADR 0006)
| Step | Scope | Acceptance |
|---|---|---|
| 3.1 | Labels K–5 / 6–8 / 9–12 from `bands.json` | UI en/hi |
| 3.2 | Optional `grade` on sessions; validate against band | grade 5 + koko OK; grade 5 + nova → 422 |

## Phase 4 — Contract codegen + sync / catalogue implementation
| Step | Scope | Acceptance |
|---|---|---|
| 4.1 | Codegen from OpenAPI (toolchain O13) | Generated code committed; CI regenerates |
| 4.2 | Implement `GET /v1/models/catalog` from training manifests | pytest per band/board/RAM |
| 4.3 | Sync event schemas leave draft when O4 closes | Wired endpoints |

## Phase 5 — Network + accounts (ADR 0003 / 0004)
| Step | Scope | Acceptance |
|---|---|---|
| 5.1 | Restore INTERNET with allowlist (Gate G-NET) | Tests; offline lessons unaffected |
| 5.2 | Sign-in / account deletion via generated Kotlin client | Token under Keystore |
| 5.3 | Model downloader (resumable, SHA-256, atomic swap) | Gate G1 data |

## Phase 6 — Toward pilot
Sync (O4) → cloud behind G2 → voice behind G3 → pilot only after G4.

## Open questions
See ADR 0007 (O1, O5, O12, O16 kindergarten encoding, O17). O18 is closed.
