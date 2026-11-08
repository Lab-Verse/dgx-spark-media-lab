# Evidence ledger and limits

Snapshot: **8 November 2026**. “Observed” below means recorded in Labverse's private research evidence, not rerun for this publication. The underlying private reports contain machine/account information and are not bundled. The public summaries are maintainer-reported observations, not independently reproducible benchmark artifacts. Contributors should add sanitized reproducible results from their own hardware.

## Recorded research results

| Component or experiment | Evidence state | Practical limit |
| --- | --- | --- |
| Original library acquisition | 20 bundles, 170,820,511,897 bytes acquired at the 6 November checkpoint | Acquisition is not inference qualification |
| Expanded integrity audit | 245 selected files / 464.22 GB logical bytes checked on 7 November | Includes original library, ComfyUI components and separate existing text cache; does not qualify all runtimes |
| Integrity methods | Publisher SHA-256, Git blobs, one publisher prefix and two local-baseline exceptions | WavLM and Real-ESRGAN had no independent full publisher digest in the research; Demucs used a prefix plus local full digest |
| Native CUDA runtime | aarch64 / GB10, CUDA 13, PyTorch 2.11.0; actual BF16 multiplication passed | Not an all-library compatibility certificate |
| Hermes | Official v0.23.0; local text/tool call/result, streaming and cancellation tests passed | Accounts/connectors and production readiness are separate |
| Profiles | Fresh-chat memory and cross-profile non-disclosure checks passed | One OS user; no security sandbox |
| Hermes recovery | A bounded idle-process crash recovered in 10.05 seconds; backup/export/import tests passed | Host reboot, power-loss recovery during media and 48–72-hour soak not certified |
| 147.10-second first pilot | Technical file checks passed; most visuals were animated stills | Owner rejected that visual treatment |
| 147.2917-second replacement | 3,535 selected native-24-fps frames, 30 generated Wan clips, 1280×720 delivery; provenance/decode and sampled-motion checks passed | 704×416 source generation; scaling is not native 720p detail. Owner final acceptance remained pending |
| Wan 2.1 14B qualification | 512×320, 81 frames / 16 fps / 5.0625 seconds; generation 286.62 seconds, full AV decode and distinct-frame checks passed | Short experiment; not a throughput guarantee, perfect motion or all-agent render qualification |
| Text/media scheduling | Roughly 99 GiB text allocation; one speech/video/reload cycle about 9m19s, cold text reload about 4m | Model/host configuration matters; gateway availability is not inference availability |
| Indic-Mio / MioCodec | Local synthetic and later private consented-reference auditions generated; decode/ASR checks passed | Speaker stability, pronunciation and naturalness require listening. No private reference is distributed |
| Later 46.42-second opening | Ten unique native 1280×704 Wan shots, 1280×720 delivery / 24 fps, narration/caption/decode/provenance checks passed | Offscreen narration; longer film, lip sync and publication rights are separate |
| Latest 15-shot portfolio | Nine sources last verified before connectivity loss | Final job/recovery outcome unknown at publication snapshot; do not describe it as complete |
| ACE-Step and other additional models | Acquired/integrity checked | No music inference qualification in these cited tests |
| Optional hosted NIM | Bounded text/tool and preset-speech tests recorded | Explicit hosted selection; quota/terms vary. DeepSeek timed out; Cosmos routes returned 404 in the tested account |

## This public edition

The installation recipe, paths and public wrappers were reconstructed from that research. Workflow graphs preserve the selected architecture while replacing internal prompts and paths. The voice helper preserves the offline dependency approach but deliberately exposes only a zero-embedding baseline. These exported variants have **not** undergone a fresh end-to-end Spark render.

Local repository checks exercise graph structure, manifest integrity metadata, file/path protections, client behavior with mocked native APIs, synthetic WAV creation and FFmpeg probe/decode where available. CI uses a standard CPU runner and never downloads weights. See [PUBLICATION-CHECKS.md](PUBLICATION-CHECKS.md) for the actual publication check record.

## Acceptance sequence for a new installation

1. Prove CUDA with a real tensor operation and save runtime versions.
2. Verify selected artifact bytes against the pinned manifest.
3. Pass export-only diagnostic; label it as export-only.
4. Generate one short image/video/speech sample and save native IDs, settings and hashes.
5. Decode and inspect it; listen with a native speaker for each target language.
6. Confirm source-frame/audio coverage, caption timing and explicit rights for your intended release.
7. Restore original services and prove real inference again.
8. Test longer scenes, restart/reboot and unattended operation separately before making those claims.

Passing step 2 or 3 cannot establish step 5 or 8. An automatic transcript is a useful screen, not a substitute for listening. A unique-frame count is not a motion-quality measure. Account authentication is not provider entitlement or a passing generation test.
