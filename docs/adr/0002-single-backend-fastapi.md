# ADR 0002 — Single backend stack: FastAPI only

- **Status:** Accepted
- **Date:** 2026-10-19
- **Decider:** Owner (Indigloo)

## Context
- The spec (`01` §6) names FastAPI for AI nodes **plus** Java Spring Boot for state/transactions/payments, with gRPC internally.
- The only backend code is FastAPI 0.115.12 / uvicorn 0.34.2 / httpx 0.28.1 on Python 3.12, with SQLite (`services/api/mentor_api/app.py` on PR #3; `backend/app.py` on `feature/ai-mentor-mvp`): 11 paths (`/health`, `/v1/capabilities`, `/v1/auth/{register,login,logout}`, `/v1/me`, `/v1/lessons`, `/v1/sessions`, `/v1/sessions/{id}/messages`, `/v1/chat`, `/v1/progress`), 8 pytest tests, Docker image built and smoke-tested in PR #3 CI.
- The product is pre-pilot with no students and no payments.

## Decision
FastAPI is the only backend stack. New server capabilities (model catalogue, sync push/pull, consent records, orchestrator, budget governor, RAG) are modules in `services/api`, not new services. No Spring Boot and no gRPC. Revisit only if payments or heavy transactional workloads arrive and FastAPI + a relational DB demonstrably cannot meet them.

## Alternatives considered
- **FastAPI + Spring Boot (spec):** two languages, two dependency trees, two security surfaces, an RPC layer — disproportionate for a pre-pilot team.
- **Spring Boot only:** discards the working, tested API and the Python ML ecosystem used by `training/`.
- **Managed agent platform as orchestrator (Gemini Enterprise / Vertex AI Agent Engine / ADK):** still open for the orchestration layer only (ADR 0007), but it would sit behind the FastAPI service, not replace it.

## Consequences
- **Positive:** one language on the server, one CI job (`api`), one container image, shared typed models generated from `packages/contracts`.
- **Positive:** cheaper to run, consistent with the ≤ $0.01/student-hour ceiling.
- **Negative:** SQLite is single-instance; a move to Postgres (+ pgvector for RAG) is expected before multi-school scale — timing TBD (ADR 0007).
- **Negative:** async Python must handle long-running cloud LLM calls carefully (timeouts already 25 s, `max_tokens` 220).
- Every cloud LLM call added to this service must pass through the budget governor (MIGRATION_PLAN Gate G2).

## Follow-ups
- Keep the provider adapter (`MODEL_BASE_URL`, `MODEL_NAME`, `MODEL_API_KEY`, server-side env only) behind an interface so vendor choice stays open.
- Decide Postgres migration trigger and hosting region (ADR 0007).
