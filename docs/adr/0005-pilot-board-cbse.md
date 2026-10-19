# ADR 0005 — Pilot board: CBSE only

- **Status:** Accepted
- **Date:** 2026-10-19
- **Decider:** Owner (Indigloo)

## Context
- The lesson pack (`packages/curriculum/curriculum.json` on PR #3; `web/curriculum.json` on `main`) has 15 lessons with fields `id, band, grade, subject, title, kw, text, answer{en,hi}, hints{en,hi}[], example{en,hi}, quiz, activity, source{label,version,kind}, minutes`. There is **no `board` field**. Every lesson's `source.kind` is "Original illustrative lesson; teacher review recommended" — none is board-approved.
- Grades covered: 3, 4, 4 (koko); 7 ×9, 8 ×2 (nova); 10 ×2 (principal). Subjects: Maths, EVS, Science, Physics.
- The model catalogue (ADR 0004) takes `board` as an input; retrieval/RAG metadata (`03` §3) needs board, grade, subject, chapter, concept id, language.
- Supporting several boards multiplies content authoring and teacher-review work.

## Decision
The pilot supports **CBSE only**. The curriculum schema gains a required `board` field (enum, initially `["CBSE"]`) and chapter/concept references; API validation and the catalogue accept only `CBSE` for now. No pilot use until pilot-scope lessons are teacher-reviewed against the CBSE syllabus.

## Alternatives considered
- **State boards (e.g. a Hindi-medium state board) first:** stronger Hindi-first story, but syllabus variety and sourcing are TBD.
- **Board-agnostic "NCERT-style" content:** what exists today; not verifiable against a syllabus.
- **Multiple boards at pilot:** content and review cost too high pre-pilot.

## Consequences
- **Positive:** one syllabus to map, one review workflow, one catalogue key.
- **Negative:** Hindi-medium students in state-board schools are out of pilot scope.
- **Negative:** the current 15 lessons must be mapped to CBSE chapters (mapping TBD) and re-reviewed; illustrative status remains until reviewed.
- Schema keeps `board` as an enum so adding boards later is additive.

## Follow-ups
- Pick pilot subjects × grades (KT recommends 2–3 subjects × 2 grades) — owner decision.
- Define teacher-review metadata in the schema (reviewer role, date, curriculum version).
- Confirm CBSE syllabus version/year to map against — TBD.
