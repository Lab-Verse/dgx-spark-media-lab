# Troubleshooting from the research

| Symptom | Inspect first | Bounded next step |
| --- | --- | --- |
| “Cannot verify” after a model acquisition | Active manifest, selected shard/index files, sizes and actual hashes | Verify the active snapshot. An unrelated old `.incomplete` file is not proof the active model is broken; do not delete a working cache wholesale |
| Download interrupted | Free disk, network response, `.part` and lock ownership | This downloader restarts the current partial file. Preserve finished hashes; remove a stale `download.lock` only after confirming no acquisition process owns this root |
| Existing file hash mismatch | Revision, filename and expected verification method | Stop; retain/quarantine deliberately and investigate. The downloader refuses to overwrite it |
| CUDA missing / no kernel image | `uname -m`, wheel architecture, driver, `torch.version.cuda`, actual tensor operation | Reconcile the ARM64/Blackwell runtime with official sources. Do not replace a working server environment |
| TorchAudio ABI error | Whether an NGC-optimized Torch was mixed with a PyPI TorchAudio wheel | Use an isolated matched runtime. A Torchaudio stub cannot perform MioCodec/WavLM inference |
| Out of memory or stalled text while generating | Host RAM, exact text-server allocation, ComfyUI queue and GPU process | Use sequential stages. Pause only the owned identified text service and restore/verify it afterward |
| ComfyUI missing node/model | Installed source commit, `/object_info`, manifest paths, extra model-path file | Load API vs UI format correctly and acquire the exact missing component. Do not install arbitrary custom nodes from an error message |
| Export succeeds but no generated motion | Which graph ran and which weights were loaded | The solid-color diagnostic tests MP4 encoding only. Run and inspect a genuine Wan graph |
| Job polling times out | Saved prompt ID, native history, queue, process and connection | Treat outcome as unknown. Resume observation rather than resubmitting or clearing the whole queue |
| Spark unreachable during a render | Local console, power/network, assigned address, DNS and existing job state | Preserve the last receipt. Connectivity loss does not prove failure or justify a duplicate batch or forced reboot |
| Speech tokenizer/codec mismatch | Selected tokenizer, `<\|s_0\|>` vocabulary, exact 44.1 kHz codec/config and WavLM artifact | Stop on unexplained keys or wrong decoder; do not suppress all missing-key warnings |
| Voice reaches token cap | Short input text, output length and missing ending | Shorten into natural phrases and retain the failed take; do not deliver clipped narration |
| Correct ASR but unnatural Urdu | Actual listening, names, nasal vowels, phrase boundaries and pitch shifts | Compare short loudness-matched auditions, one variable at a time, with a native listener |
| Voice sounds robotic after pitch processing | Raw vs processed take and magnitude of change | Return to raw accepted timbre; use modest changes and re-listen. F0 metrics are not naturalness certification |
| A film decodes but has bad acting or wrong camera direction | Full-speed footage and shot contract | Reject/rerender the shot or revise the editorial intent. Unique frames and prompt wording cannot certify physics |
| Captions drift | Actual narration start/end and per-cue timing | Align by listening or qualify a real alignment pipeline. Even cue spacing is not forced alignment |
| Agent skill installed but account action fails | Native tool discovery, authentication, connector capability and permissions | An instruction file is not a connected service. Keep drafts local until an authorized real operation passes |
| Hosted endpoint 404/timeouts | Exact official endpoint/model ID and account entitlement | Record failure and stop blind retries; do not invent a successful cloud fallback |

Never paste tokens, environment dumps, SSH configuration, raw account sessions or voice references into a public issue. Share sanitized versions, a minimal graph, model revision, error type and reproduction steps instead.
