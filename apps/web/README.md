# Learner PWA (`apps/web`)

Vanilla ES-module PWA (English / Hindi). Also synced into the Android APK via `npm run sync`.

## Source readability

The current `*.mjs` files were imported **minified** from legacy `main` (`543700f`) / PR #3 (`32e5156`). Longest lines are ~4 KB. **TBD: deminify** (MIGRATION_PLAN Phase 1.1) and keep readable source in git; minify only at asset-bundle time if needed.

## Run

```bash
python3 -m http.server 8000 --directory apps/web
# or via API: uvicorn serves the same files at /app/
```

## Tests

```bash
npm test   # from repo root — includes core.test.mjs
```
