# Contributing

Useful contributions include a clean Spark installation report, an ARM64 runtime fix, a smaller verified workflow, native-language listening feedback or a model-license correction.

Open an issue with your OS/architecture/GPU, versions, model IDs/revisions, exact minimal command/graph, expected/observed behavior and sanitized error. State whether the result was planned, downloaded, integrity checked, load tested, generated, technically decoded or human quality reviewed. Include timing boundaries: generation alone differs from model load, GPU handoff and recovery.

Never attach credentials, private recordings, speaker embeddings, account sessions, client documents or unlicensed media. Replace machine names, usernames and addresses with placeholders. Do not upload model weights. Obtain permission before contributing identifiable speech/media.

For a code change:

```bash
python3 -m unittest discover -s tests -v
python3 scripts/check_package.py
```

If FFmpeg is installed, the tests also exercise a real procedural WAV and full media decode. CI runs on CPU and cannot certify Spark generation. Add a bounded regression test for a meaningful behavior change; document any real GPU test separately. Preserve existing files and avoid hidden cloud fallbacks or automatic provider/account actions.

For model/runtime changes, update pins, licenses, expected hashes, tutorial commands and evidence limits together. A private result can be summarized honestly, but do not label it independently reproducible without the required public artifacts.

By submitting a contribution you agree to license your contribution under this repository's Apache-2.0 license and confirm you have the rights to submit it. Third-party components retain their notices and terms.
