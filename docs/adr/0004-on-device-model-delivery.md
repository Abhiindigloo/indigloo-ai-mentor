# ADR 0004 — On-device model delivery: single APK + post-onboarding download

- **Status:** Accepted
- **Date:** 2026-10-19
- **Decider:** Owner (Indigloo)

## Context
- Today the Kotlin app ships **no weights**. The learner imports a `.litertlm` file through the document picker (`importModel` in `apps/android/.../MainActivity.kt`): name must end `.litertlm`; size limited to `min(3 GB, free − 256 MB)`; copied to `model.tmp` then renamed over `mentor.litertlm`. The engine is closed first, so the old model is overwritten **before** the new one is proven loadable; there is no checksum or signature check.
- `loadModel` refuses if `ActivityManager.MemoryInfo.totalMem < 3 GB`; `generate` refuses at `THERMAL_STATUS_SEVERE` (API 29+), caps prompts at 1800 bytes and times out at 60 s.
- The manifest removes INTERNET and ACCESS_NETWORK_STATE (`tools:node="remove"`), so the app cannot download anything.
- Target users are on low-cost phones and constrained data plans; many schools have poor connectivity.
- Model family is not yet chosen (ADR 0007): Gemma is the owner's preference; the training pilot targets Qwen2.5-0.5B (a LoRA adapter, not an Android model).

## Decision
1. **Single APK** (no per-model APK variants, no bundled weights).
2. After onboarding collects **age band** and **board** (plus language), the app requests the **model catalogue** and downloads the matching on-device model.
3. **Catalogue endpoint** in `services/api`, defined first in `packages/contracts` (path proposed: `GET /v1/models/catalog`, name TBD):
   - Inputs: `age_band` (band id `koko|nova|principal`, ADR 0006), `board` (`CBSE`, ADR 0005), `lang`, `device_ram_mb`.
   - Output per entry: `model_id`, `version`, `url`, `size_bytes`, `sha256`, `licence` (id + URL), plus `runtime` (`litertlm`), `min_ram_mb`. Response is cacheable and contains no user identifiers; request params are not logged with any account id.
   - Catalogue response is signed (mechanism TBD) so a compromised CDN cannot swap URLs + hashes together.
4. **Weights** are hosted on CDN/object storage outside the repo; `training/` holds manifests only. Host/CDN TBD (ADR 0007).
5. **Downloader** (Kotlin, native, not WebView):
   - Resumable (HTTP `Range`), Wi-Fi/unmetered by default with an explicit user opt-in for mobile data; survives app restarts (WorkManager or Android `DownloadManager` — TBD).
   - Prechecks: free storage ≥ `size_bytes` + margin; RAM ≥ `min_ram_mb`; otherwise do not download.
   - Verify SHA-256 before use; reject on mismatch and delete the partial file.
   - **Atomic swap on update:** download to a versioned file, verify, test-load it with LiteRT-LM, then switch the active pointer; keep the previous version until the new one has loaded successfully once; then delete the old one.
6. **Lesson-only offline fallback:** guided lessons (authored content + lexical retrieval) are always available while downloading, on low-RAM devices, or when no model is installed. No guided-lesson path may depend on the download.
7. **INTERNET permission restored with tight scope:** network calls only from native Kotlin code to an allowlist of hosts (API + model CDN), HTTPS only (`usesCleartextTraffic=false` retained; network security config), WebView navigation stays restricted to `appassets.androidplatform.net`. `ACCESS_NETWORK_STATE` restored only if needed for the unmetered constraint. Certificate pinning: TBD.
8. **Offline-school fallback:** a teacher device holds a verified copy of the model; students import it via the existing `importModel` path, but the file must now match a `sha256` from a catalogue snapshot already on the device (bundled in the APK and/or last fetched). Transfer channel (USB/SD, Nearby, local Wi-Fi) TBD.

## Alternatives considered
- **Bundle weights in the APK / Play Asset Delivery:** APK size balloons (hundreds of MB to GB per model) and one size cannot fit all bands/devices; Play Asset Delivery ties distribution to Play and is unsuitable for sideloaded school installs. Rejected for now.
- **Per-band APK flavours:** multiplies release/QA work.
- **Keep user import only (status quo):** unusable for children; no integrity check.
- **Cloud-only generation:** breaks offline-first and the cost ceiling.

## Consequences
- **Positive:** one build to test and ship; model updates without app releases; integrity verified; offline lessons never blocked.
- **Negative:** restoring INTERNET removes the strongest current privacy guarantee ("app cannot talk to the network"); privacy notice, Play data-safety form and DPIA must be updated before release (Gate G4).
- **Negative:** first-run data cost and time on slow links; CDN egress cost counts toward the cost ceiling (Gate G2).
- **Negative:** new attack surface: CDN, catalogue, download code. Mitigated by HTTPS, signed catalogue, SHA-256, fail-closed loading.
- **Risk (Gate G1):** 2–3 GB RAM phones may not run any useful model; today's hard floor is 3 GB total RAM. Must be measured on real devices before committing to a model family.
- **Risk:** model licences (e.g. Gemma Terms of Use, Apache-2.0 for Qwen) must be surfaced in the catalogue and app's licence screen.


## First-commit stance (this repo)
For the initial import, the Android manifest stays **closer to `main`**: INTERNET and ACCESS_NETWORK_STATE remain removed (`tools:node="remove"`). Offline guided lessons and user-imported LiteRT-LM models continue to work. Restoring INTERNET is a later change under Gate G-NET (MIGRATION_PLAN); do not break the offline path when that lands.

## Follow-ups
- Contract: add catalogue schema to `packages/contracts`; generate server model + Kotlin client.
- Decide signing scheme, CDN/host, downloader mechanism, pinning, teacher-copy channel (ADR 0007).
- Replace in-place overwrite in `importModel` with the verified atomic swap.
- Real-device test matrix (2 GB / 3 GB / 4 GB+) before Gate G1.
