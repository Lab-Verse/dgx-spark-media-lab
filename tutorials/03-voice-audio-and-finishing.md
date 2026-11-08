# Tutorial 3 — Local voiceover, original audio and finishing

**Goal:** generate a short local narration, audition it, create a small original background score and finish a reviewed audiovisual clip. This is offscreen narration. Multi-speaker dubbing and lip synchronization require additional qualification.

## 1. Keep canonical text and pronunciation experiments separate

Write an original, short script in the target script. [narration.json](../examples/narration.json) contains a two-sentence Urdu example. Preserve canonical spelling for captions. Put pronunciation experiments into a separate copy so spelling changes do not leak into final subtitles.

In our tests, words such as `سانس` and character names needed listening and targeted cues. Diacritics or a temporary phonetic spelling can change pronunciation, but a successful speech recognizer transcription cannot certify the exact vowel, nasalization, accent or naturalness. Prefer a native speaker's listening decision over an ASR score.

Start with one or two sentences, not an entire film. Record text, language/script, sampling settings, seed, voice mode, sample rate, duration, output hash and reviewer disposition.

## 2. Prepare local speech components

The experimental path uses Indic-Mio, the selected **44.1 kHz v2 MioCodec**, its exact WavLM dependency and pinned MioCodec source. Do not substitute the 24 kHz codec from another example while labeling the result 44.1 kHz. Review [the model card](https://huggingface.co/SPRINGLab/Indic-Mio), [codec source](https://github.com/Aratako/MioCodec) and [TorchAudio dependency](https://docs.pytorch.org/audio/main/generated/torchaudio.pipelines.WAVLM_BASE_PLUS.html).

```bash
export SPARK_MEDIA_ROOT="$HOME/spark-media"
python3 scripts/models.py --group voice --root "$SPARK_MEDIA_ROOT"
python3 scripts/models.py --group voice --root "$SPARK_MEDIA_ROOT" --download --accept-licenses
```

The WavLM asset had an official source and expected size, plus a locally computed SHA-256 baseline. The public manifest records that baseline explicitly; it is not an independent publisher digest. For the other selected files, the manifest records publisher LFS hashes or Git blob identifiers. A matching checksum does not prove a checkpoint is safe to deserialize. Use only the reviewed source and `weights_only=True` for the local TorchAudio checkpoint.

The runtime setup in Tutorial 1 checks out MioCodec. This public helper applies the same bounded offline WavLM adapter approach as our experiment: no `bundle.get_model()` network download and no `trust_remote_code=True`.

## 3. Generate an experimental synthetic baseline

```bash
"$SPARK_MEDIA_ROOT/.venv/bin/python" scripts/voiceover.py \
  --root "$SPARK_MEDIA_ROOT" --script examples/narration.json \
  --output "$SPARK_MEDIA_ROOT/runs/voice-baseline-001" \
  --device cpu --temperature 0.6 --top-p 0.9 --seed 2406
```

The output directory must be new. CPU is the default to avoid competing with GPU footage generation, but synthesis still uses shared RAM and CPU. CUDA mode is optional after explicitly scheduling memory. Runtime imports and speech generation are not exercised by the repository's CPU-only CI.

This public example uses a **zero speaker embedding** and contains no identifiable voice reference, preset or embedding. It is an experimental baseline, not a claim of a polished narrator. Our private preferred timbre used an owner-consented reference that is intentionally excluded. The public helper does not offer identity cloning. For a reference-conditioned extension, obtain consent and rights for both synthesis and intended distribution, follow the upstream API, keep references/embeddings private and record that separate qualification.

The helper uses local paths only, writes WAV/evidence files, checks finite audio and non-silence, and fails if generation hits its token limit. If you hit the limit, shorten the passage rather than silently accepting truncated narration. It permits only the previously identified codec missing-key classes; unexpected or unexplained missing weights fail.

## 4. Audition controls in a useful order

Keep one text and seed fixed while changing one variable:

| Control | What it affects | What it does not prove |
| --- | --- | --- |
| Temperature / top-p | Sampling randomness and potential delivery variation | Stable identity, better pronunciation or emotion |
| Seed | Repeatable comparison within one runtime | Identical results across library/hardware changes |
| Speed | Playback timing after synthesis | Better source articulation |
| Pitch / EQ | Audible tonal processing | A natural or consented speaker identity |
| Pronunciation text | The model's spoken input | Correct canonical subtitle spelling |

Preserve raw takes. Loudness-match candidates before comparing so louder does not automatically sound better. A modest pitch-preserving pace change can be auditioned with FFmpeg:

```bash
ffmpeg -n -i "$SPARK_MEDIA_ROOT/runs/voice-baseline-001/narration.wav" \
  -af "atempo=1.05,alimiter=limit=0.97:level=0" \
  -ar 44100 -ac 1 "$SPARK_MEDIA_ROOT/runs/voice-baseline-001/narration-fast.wav"
```

`atempo=1.05` makes speech about 5% faster. Avoid changing sample rate metadata to simulate speed: that also changes pitch. Large pitch corrections and resynthesis produced artificial-sounding candidates in our auditions. Keep an accepted timbre/reference fixed and tune pronunciation separately.

Native-language listening should cover wording, missing/repeated words, register, names, nasal vowels, speaker stability and transitions. A preferred short sample is not whole-film acceptance. Urdu, Hindi and Punjabi/Shahmukhi need separate evaluations; translation quality is distinct from speech quality.

## 5. Create an original procedural background score

The public example creates simple original tones with a deterministic melody and fades, using only Python's standard library:

```bash
python3 scripts/make_score.py --seconds 12 --output "$SPARK_MEDIA_ROOT/runs/score-001.wav"
```

This is procedural synthesis, **not an ACE-Step or other neural music-model demonstration**. Keep the uncompressed WAV and listen for clipping, harshness and competing frequencies. Mix it quietly beneath narration. For a real commission, compose or license music appropriate to the piece.

We also acquired ACE-Step 1.5 model bundles for research. Their acquisition did not qualify music inference on this Spark. A contributor can follow the [official ACE-Step guide](https://github.com/ace-step/ACE-Step-1.5), install it in a separate environment, record the exact model/revision and run a short benchmark. Do not advertise that optional extension as a tested part of this public recipe until a reproducible result exists.

## 6. Fit shots to measured narration

Use `ffprobe` to read actual duration before selecting footage:

```bash
ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 \
  "$SPARK_MEDIA_ROOT/runs/voice-baseline-001/narration.wav"
```

Generate enough unique moving footage to cover it. If narration is longer than the selected clip, add more approved shots or rewrite/regenerate narration. Do not quietly loop, freeze or slow footage to claim a full-motion film. Choose source ranges on frame boundaries and preserve the ledger.

For a one-clip canary, use narration shorter than that clip. For several compatible clips, first normalize their dimensions/fps, then create a private `shots.txt` with one `file '/absolute/path/shot.mp4'` line per selected source. Use only your own generated list and filenames; do not consume an untrusted concat list.

```bash
ffmpeg -n -f concat -safe 0 -i shots.txt -an -c:v libx264 -crf 18 \
  -pix_fmt yuv420p "$SPARK_MEDIA_ROOT/runs/picture-edit.mp4"
```

If clips differ in size/cadence, normalize them deliberately before concatenation; `-r` cannot create genuinely generated new motion. Record native and delivery cadence separately.

## 7. Mix and mux

Replace the input paths below with your chosen edit, accepted narration and score. The picture must cover the narration. Use a score at least as long as the voice. This example produces video ending with the narration and deliberately trims any excess picture.

```bash
ffmpeg -n -i "$SPARK_MEDIA_ROOT/runs/picture-edit.mp4" \
  -i "$SPARK_MEDIA_ROOT/runs/voice-baseline-001/narration.wav" \
  -i "$SPARK_MEDIA_ROOT/runs/score-001.wav" \
  -filter_complex "[1:a]loudnorm=I=-18:TP=-2:LRA=7[v];[2:a]volume=0.10[m];[v][m]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.95:level=0[a]" \
  -map 0:v:0 -map "[a]" -c:v copy -c:a aac -ar 48000 \
  -shortest -movflags +faststart "$SPARK_MEDIA_ROOT/runs/finished.mp4"
```

Check mix loudness and intelligibility yourself; these are starting settings, not a delivery standard. `-shortest` can hide missing picture coverage if used carelessly, so compare source narration duration with final duration explicitly.

## 8. Captions and final checks

The included [SRT](../examples/captions.srt) illustrates formatting only. Its timings are placeholders; align real cues to the selected narration and check them by listening. Do not claim forced alignment from evenly divided captions. Keep UTF-8 Urdu text and an appropriate shaping-capable font/player. Burn-in through `subtitles` requires FFmpeg built with libass and an installed font; alternatively distribute SRT separately or mux selectable MP4 captions:

```bash
ffmpeg -n -i "$SPARK_MEDIA_ROOT/runs/finished.mp4" -i your-aligned-captions.srt \
  -map 0 -map 1:0 -c copy -c:s mov_text -metadata:s:s:0 language=urd \
  "$SPARK_MEDIA_ROOT/runs/finished-captioned.mp4"
python3 scripts/verify_media.py "$SPARK_MEDIA_ROOT/runs/finished-captioned.mp4" \
  --require-video --require-audio
```

The checker probes streams, fully decodes audiovisual streams, rejects empty/non-finite duration and hashes the final file. It does not judge meaning, lip sync, rights or artistic quality. Watch the full film with sound and inspect its first/last second, cue boundaries, voice/music balance and source-range transitions. Save the final hash, source ledger, model terms and human review decision.

Our private records contain a technically verified 46.42-second later opening preview with ten native moving shots and owner-consented narration. That does not release its voice or underlying adaptation for public redistribution, and does not establish full-film or lip-sync acceptance. This repository uses an original generic script instead.

**Checkpoint:** you have a reviewed local canary and its receipts. Longer work should repeat these bounded stages, preserving failed takes and recording actual outcomes rather than assuming every installed model or automation works.
