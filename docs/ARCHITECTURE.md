# MVP architecture and boundaries

The Android app (Kotlin WebView shell, API 26+) and the browser app share one web codebase (`apps/web`) and one bilingual illustrative lesson pack (`packages/curriculum`). The API (`services/api`) loads the same pack. Offline tutoring is authored content selected by conservative lexical retrieval. It is not a locally running language model. Only explicit short follow-ups retain the last topic; unrelated questions reset it. This keyword method still has false matches and is not a semantic safety classifier.

The Python FastAPI service stores pseudonymous accounts, salted scrypt password hashes, SHA-256 digests of expiring random bearer tokens, user-scoped sessions, chat turns, and practice counts in SQLite. API bodies are bounded at 16 KB and authenticated chat requests are limited to 30/minute. SQLite is appropriate for a single-instance pilot; it is not a horizontally scalable shared database.

Optional server inference accepts a configured NVIDIA NIM or Hugging Face endpoint exposing `/v1/chat/completions`. Retrieval happens first. The model receives one bounded passage and the current question, not the stored chat history. `use_model` is explicit and off by default. Provider failures return a labelled sample answer. Generated explanations carry `grounded: false` and a notice; prompt instructions cannot guarantee factuality.

Android stores learner state in an AES-GCM file vault keyed by the Android Keystore (`Vault.kt`), with backups disabled; the browser stores it AES-GCM-encrypted in IndexedDB. The WebView loads bundled assets only, with file/content access off, and reaches native features (OCR, TTS, optional on-device LiteRT-LM model) through an allowlisted bridge. The Android manifest currently removes the INTERNET permission, so the app cannot reach the API until sync is implemented. API keys remain on the server. English and Devanagari OCR models are bundled through ML Kit; selected photos are processed on the device, then editable recognised text is shown before asking. TTS uses the installed Android voice. Photo OCR and TTS are not WebRTC voice chat.

The browser app stores learner state encrypted in IndexedDB. The service worker caches the app shell and lesson pack, never API responses. It supports offline revisits after one successful load/install, not a first-ever offline visit. Account tokens live only in memory; closing the tab signs the user out locally. Server sessions expire after 24 hours.

## Pilot limits

- 15 sample lessons; not NCERT/board-approved content. Review lessons with teachers before student pilots.
- No MFA, password recovery, parental-consent workflow, school administration, analytics pipeline or production retention policy.
- No trained weights bundled yet, no measured 750 MB RAM claim, no on-device LLM integration, and no fabricated thermal/thread controls.
- Full duplex WebRTC voice, realtime ASR/TTS, animation and semantic retrieval are subsequent milestones. The capabilities endpoint reports unavailable features honestly.
- Put the API behind HTTPS. Do not expose debug builds or the unauthenticated registration API to a public school rollout without deployment controls, consent and abuse review.
- Account deletion cascades through active database records; operators must separately define backup retention/deletion. Local device data is erased separately from server accounts.
- Teacher evaluation and testing on actual 2/3 GB Android phones remain necessary. An APK build is not device validation.
