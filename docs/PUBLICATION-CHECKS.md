# Public edition validation

Checked on 8 November 2026 on the publication workstation. This public edition does not claim a fresh Spark end-to-end run.

- Python AST/JSON validation, relative Markdown links and bounded secret/private-identifier patterns: passed.
- Offline behavior suite: 18 tests, 17 passed, one skipped because FFmpeg/ffprobe were unavailable on the Windows PATH. The skip is not a decode success claim.
- GitHub Linux CI with FFmpeg installed: **18/18 passed, no skips**, including real WAV generation, full FFmpeg decode and required-stream rejection. [Verified run](https://github.com/Lab-Verse/dgx-spark-media-lab/actions/runs/42463965797).
- Git Bash syntax check of the setup script: passed.
- Live read-only upstream checks: four source commits, four model revisions and selected PyPI release metadata were available.
- Independent reproducibility review identified output traversal, lost-submission receipt discoverability and invalid pip constraints-with-extras. These were corrected. The first two have regression tests; the corrected constraints approach passed a real pip `--dry-run --no-index` check using installed-distribution freeze output.
- Independent final privacy/security/license review found no publication blockers in the allowlisted text/code export.

The public repository begins with fresh history, a GitHub noreply commit identity and no parent working-directory history. No raw evidence archives, model weights, generated films, private voice references/embeddings or account state were exported.

GitHub reports the repository as **PUBLIC**, and unauthenticated reads of its page, README and launch drafts returned HTTP 200. Native private vulnerability reporting is enabled.

Expected commands:

```bash
python3 scripts/check_package.py
python3 -m unittest discover -s tests -v
bash -n scripts/setup_media.sh
```

CI repeats source/package and offline behavior checks on a CPU runner. No model weights, credentials, private references or generation hardware are required.
