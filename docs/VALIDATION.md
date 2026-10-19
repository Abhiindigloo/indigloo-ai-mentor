# Validation record

- API: 8 automated tests passed. Covers authenticated use, hashed credentials, logout/expiry, user isolation, cascade deletion, bounded/chunked requests, rate limiting, Hindi token preservation, grade filtering, unrelated follow-up refusal and model fallback/labeling.
- Postman/Newman: 15 requests, 17 assertions; all passed against a local running API using a disposable account. The final request deleted that account.
- Web (historical connected client on `feature/ai-mentor-mvp`): DOM interaction test passed for lesson selection, follow-up answer, unrelated refusal, Hindi and local practice counts. JavaScript syntax checks passed.
- Full browser rendering and service-worker offline reload: not verified here. Browser process launch was blocked by environment socket restrictions.
- Training: 104 train / 28 eval synthetic examples; topic sets do not overlap. Job script parses and pinned package versions exist. No GPU job was submitted, no weights were produced, and no model quality/latency claims are made.
- NVIDIA NIM and Hugging Face inference: adapter implemented; live endpoint test pending credentials and chosen deployment.
- Android (historical Java client on `feature/ai-mentor-mvp`): `assembleDebug` succeeded; two `testDebugUnitTest` cases passed (unrelated-topic isolation, Hindi and grade filtering). Debug APK signature verified. Physical-device OCR, TTS, thermal, battery and memory testing remain pending.
- GitHub: as of the monorepo restructure (ADR 0001), `main` is the single delivery branch. `feature/ai-mentor-mvp` is kept for history only.
- Monorepo restructure: 8 API tests pass against the shared curriculum; web logic tests pass; training data regenerates byte-identically; asset sync produces no drift. The Java Android client and the separate connected web client from `feature/ai-mentor-mvp` were not carried over (superseded by `apps/android` and `apps/web`).
