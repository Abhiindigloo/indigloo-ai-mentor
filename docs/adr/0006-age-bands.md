# ADR 0006 — Age bands: K–5 / 6–8 / 9–12

- **Status:** Accepted
- **Date:** 2026-10-19
- **Decider:** Owner (Indigloo)

## Context
- Spec personas (`01` §3.4, `04` §9): K–5 Learning Guide, 6–8 Academic Coach, 9–12 Subject Matter Mentor.
- Code uses band ids `koko | nova | principal` with ranges 1–4 / 5–8 / 9–12. The ranges exist only as UI labels:
  - `apps/web/app.mjs`: `bandLabel = {koko:'Koko · 1–4', nova:'Nova · 5–8', principal:'Principal · 9–12'}` and onboarding `<select id="band">` options "Grades 1–4 / 5–8 / 9–12".
  - `index.html` (legacy single-file demo): `PERSONA` grades `1–4`, `5–8`, `9–12`.
- API (`services/api/mentor_api/app.py`): `band: Literal['koko','nova','principal']` on sessions and `GET /v1/lessons?band=`; no grade field and no grade↔band check.
- Lessons: grades 3, 4 (koko), 7, 8 (nova), 10 (principal). **No lesson is grade 5 or 6**, so no lesson changes band.
- Onboarding today collects nickname (optional), band and language — **not grade, age or board**.

## Decision
- Bands: **K–5 → `koko` (Koko / Learning Guide)**, **6–8 → `nova` (Nova / Academic Coach)**, **9–12 → `principal` (Principal / Subject Matter Mentor)**. Band ids stay unchanged (no data migration).
- One band table lives in `packages/curriculum` (e.g. `bands.json`: id, persona, min grade, max grade) and is the source for web labels, API validation and training data.
- Curriculum schema enforces that a lesson's `grade` lies within its `band`'s range; the API validates `grade` (when supplied) against `band`.

## Alternatives considered
- **Keep 1–4 / 5–8 / 9–12:** matches code, not the spec or the persona design.
- **Grade-only, no bands:** finer grained, but personas and model catalogue are band-based.

## Consequences
- **Positive:** spec, UI, API and personas agree; grade-5 learners move to Koko, matching the K–5 persona.
- **Negative:** representation of "K" (kindergarten/pre-primary) as a grade value is TBD (e.g. `0`), and the pack has no K–2 content.
- **Negative:** existing device state stores the band only; a grade-5 student who picked Nova keeps Nova until they change it (no automatic re-banding without a stored grade).
- Age band is also the model catalogue key (ADR 0004).

## Follow-ups
- Decide whether onboarding asks **grade/class** (derive band) or **age** (needed for the age gate/consent, Gate G4) or both.
- Update tests: `apps/web/core.test.mjs`, `services/api/tests/test_api.py`; the `training/prepare_data.py` reproducibility check in CI must still pass.
