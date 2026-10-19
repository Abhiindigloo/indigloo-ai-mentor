# ADR 0007 — Open architecture decisions (register)

- **Status:** Proposed (O18 closed)
- **Date:** 2026-10-19
- **Decider:** Owner (pending items); O18 decided by owner 2026-10-19

## Context
ADRs 0001–0006 fix the repository shape, backend, Android app, model delivery, board and bands. Several choices they depend on are still open. Each item below becomes its own ADR when decided. Facts about vendors, models, prices and laws change — re-verify at decision time.

## Closed in this register

| # | Decision | Outcome |
|---|---|---|
| **O18** | History / monorepo home | **Accepted — new public repo** `Abhiindigloo/indigloo-ai-mentor`. Legacy `Abhiindigloo/ai-mentor` is **frozen** (no commits, PRs, or comments for this migration). Clean import with provenance notes; optional later history graft is out of scope for v0. See ADR 0001 and `docs/PROVENANCE.md`. |

## Open decisions

| # | Decision | Options | Inputs needed / recommendation | Blocks |
|---|---|---|---|---|
| O1 | On-device model family | Gemma (e.g. Gemma 3 1B / 270M; Gemma 3n on capable phones) vs Qwen (Qwen2.5-0.5B is the current training target) vs other | Owner prefers Gemma; benchmark both on real 2/3/4 GB phones via LiteRT-LM for Hindi quality, latency, RAM, licence terms. Recommendation (KT): Gemma, Qwen as baseline | Catalogue content, training target, Gate G1 |
| O2 | Cloud reasoning model / vendor | Claude tier, Gemini, NIM-hosted open model | Cost per resolved turn vs. $0.01/student-hour, Hindi quality, minors usage policy, DPA/no-training, data region. Keep provider interface | Cloud intelligence phase, Gate G2 |
| O3 | Orchestrator | Own FastAPI state machine vs Google ADK / Vertex AI Agent Engine | KT recommends own FastAPI (ADR 0002) unless going Google-first | Cloud phase |
| O4 | Sync protocol | HTTPS batched outbox push + cursor pull (KT `04` §7) vs WebSockets | KT recommends HTTPS batch; WebSockets only for live voice. Conflict rules, event schema versioning | Accounts + sync phase |
| O5 | Hosting, region, CDN for API + weights | TBD (cloud provider, India region, object storage + CDN with HTTP Range) | DPDP cross-border rules, egress cost, Range support | Catalogue + downloader (ADR 0004) |
| O6 | Catalogue signing + cert pinning | e.g. signed manifest (Ed25519) / none; pinning yes/no | Key custody (secret manager), rotation | ADR 0004 |
| O7 | Downloader mechanism | WorkManager + OkHttp Range vs Android `DownloadManager` | Resume reliability, unmetered constraint, OEM background limits | ADR 0004 |
| O8 | Teacher-copy channel for offline schools | USB/SD import, Nearby Connections, local Wi-Fi | Classroom constraints | ADR 0004 |
| O9 | ASR (voice) | Multilingual Whisper tiny/base (quantised), Android on-device `SpeechRecognizer`, AI4Bharat Indic models | `whisper-tiny.en` (spec) cannot do Hindi. Must test on children's voices | Multimodal phase, Gate G3 |
| O10 | Hindi OCR for handwriting/maths | ML Kit Devanagari (built) + maths path (cloud escalation?) | Accuracy on children's handwriting | Gate G3 |
| O11 | Languages beyond English + Hindi | Which Eighth Schedule languages, in what order | Market + content capacity | Curriculum schema `lang` enum |
| O12 | Answer-reveal policy (KT D6) | Never / after verified attempt / after N scaffolded turns / teacher policy | Interim rule (non-negotiable #1): every path that returns the lesson's final answer (`answer`, `steps`, API `example`, web `activity`/`simple` fallbacks) gated until policy ships — see `docs/SAFETY.md` | Pedagogy phase |
| O13 | Codegen toolchain for contracts | e.g. datamodel-code-generator (Python), openapi-generator / openapi-typescript (TS), openapi-generator Kotlin | Must run offline in CI, deterministic output | ADR 0001 contract-first |
| O14 | Web app typing | JSDoc + `tsc --checkJs` vs migrate `apps/web` to TypeScript | Owner rule: typed code | ADR 0001 |
| O15 | Database | SQLite (today) → Postgres (+ pgvector) trigger | Multi-instance, RAG | Cloud phase |
| O16 | Onboarding fields | Grade/class, age, or both; how "K" (kindergarten) is represented | Age gate + consent need age; band needs grade. **Kindergarten grade encoding TBD** (e.g. `0` vs omit); koko range documented as K–5 / grades 0–5 or 1–5 pending this decision | ADR 0006, Gate G4 |
| O17 | Legal roles + launch market | Indigloo as Data Fiduciary vs school as fiduciary; India-only first | Counsel | Gate G4 |

## Consequences
- Until O1/O2 close, catalogue entries and cloud calls stay behind feature flags; the pilot cannot start.
- O18 closed means all new work happens in `indigloo-ai-mentor`; do not reopen migration PRs on `ai-mentor`.
- Each decision records model/vendor IDs and prices as verified on the decision date.

## Follow-ups
- Owner to prioritise O1, O5, O12, O16, O17 (they block the next phases).
