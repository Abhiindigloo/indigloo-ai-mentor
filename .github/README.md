# GitHub Actions

The CI workflow lives at [`docs/ci/ci.yml`](../docs/ci/ci.yml) until a token with the `workflow` OAuth scope can place it under `.github/workflows/`.

To enable Actions on this repo:

```bash
mkdir -p .github/workflows
cp docs/ci/ci.yml .github/workflows/ci.yml
git add .github/workflows/ci.yml && git commit -m "ci: enable path-filtered workflow" && git push
```

Requires a credential with the `workflow` scope (GitHub rejects pushes that create workflow files otherwise).
