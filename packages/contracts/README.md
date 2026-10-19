# Contracts

Contract-first API and event schemas.

| File | Purpose |
|---|---|
| `openapi.yaml` | **Source of truth** OpenAPI 3 (hand-authored + catalogue) |
| `openapi.json` | JSON twin of the YAML (kept in sync for tooling) |
| `schemas/model-catalogue.schema.json` | Catalogue response JSON Schema |
| `events/sync-event.schema.json` | Draft sync outbox event schema (O4) |
| `postman/` | Collection + local environment |

Server Pydantic models and Kotlin/TS clients should be **generated** from `openapi.yaml` (toolchain TBD — ADR 0007 O13). Do not invent endpoints only in code.
