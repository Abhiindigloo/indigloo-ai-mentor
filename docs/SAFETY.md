# Safety notes (pre-pilot)

This product targets children. Until Gate **G4** and the answer-reveal policy (ADR 0007 **O12**) ship, treat the following as **known gaps**, not features.

## Answer-leak modes (TODO — gate before pilot)

Leave existing code behaviour as-is for the import, but **do not pilot** until these are gated:

| Surface | Modes / paths that can reveal a final answer |
|---|---|
| Web (`apps/web`) | `answer`, `steps` (hints + full answer), `activity` / `simple` fallbacks that surface the answer |
| API (`services/api/mentor_api/tutor.py`) | `answer`, `steps`, `example` |
| Follow-ups | Phrases like "show answer" / "जवाब दिखाओ" must hit the anti-lazy fence, not unlock reveal |

**Interim rule (non-negotiable):** default to `hint`. Full solutions only after a verified attempt, or under an explicit teacher/parent policy flag. Prompt-injection text in the question or OCR must not unlock reveal.

Tracked in MIGRATION_PLAN Phase 2. See also KT guardrails (`05` §10) when that skill is available.

## Other pre-pilot blockers (summary)

- No verifiable parental consent / age gate yet
- Curriculum is illustrative, not teacher-signed CBSE
- No ads/trackers today — keep it that way
- Secrets only in env / secret manager — never commit keys
