# Tutorial 2 — Generate reference images and real moving video

**Goal:** produce one original image, one text-to-video clip and optionally one image-conditioned clip, with saved settings and receipts. Complete [Tutorial 1](01-spark-and-hermes.md) first. These are short experimental renders, not a guaranteed camera/character simulation.

## 1. Download only the selected components

Review [model and license notes](../docs/MODELS-AND-LICENSES.md). The manifest pins repository revisions and individual files; it does not redistribute weights. Image generation uses Z-Image-Turbo; video uses Wan **2.1 14B**, not the distinct Wan 2.2 5B Diffusers bundle used in another private experiment.

```bash
export SPARK_MEDIA_ROOT="$HOME/spark-media"
python3 scripts/models.py --group image --root "$SPARK_MEDIA_ROOT"
python3 scripts/models.py --group video --root "$SPARK_MEDIA_ROOT"
# Only after reviewing each model's terms:
python3 scripts/models.py --group image --root "$SPARK_MEDIA_ROOT" --download --accept-licenses
python3 scripts/models.py --group video --root "$SPARK_MEDIA_ROOT" --download --accept-licenses
```

The image group is about 20.69 GB; T2V about 35.57 GB. Requesting I2V later adds its larger diffusion model and CLIP Vision encoder; shared text/VAE files are verified and reused. Leave room for Python environments, caches, input assets, decoded frames and multiple outputs. The helper checks planned missing bytes against available disk plus a safety margin, downloads sequentially, and verifies size and hash before promoting a `.part` file. A failed partial file is restarted on the next run; it is not a resumable byte-range downloader. Existing completed files are rehashed rather than silently overwritten. Save the download receipts locally.

An LFS SHA-256 match, a Git blob SHA-1 match, and a locally recorded digest have different evidential strengths. Do not label them all “publisher SHA-256 verified.” The voice dependency exception is explained in Tutorial 3.

## 2. Start native ComfyUI on loopback

After deliberately releasing the heavy text-model allocation if necessary:

```bash
"$SPARK_MEDIA_ROOT/.venv/bin/python" "$SPARK_MEDIA_ROOT/ComfyUI/main.py" \
  --listen 127.0.0.1 --port 8188 \
  --extra-model-paths-config "$SPARK_MEDIA_ROOT/extra_model_paths.yaml" \
  --input-directory "$SPARK_MEDIA_ROOT/comfy/input" \
  --output-directory "$SPARK_MEDIA_ROOT/comfy/output" \
  --user-directory "$SPARK_MEDIA_ROOT/comfy/user"
```

Keep this terminal open. From a second Spark terminal:

```bash
python3 scripts/comfy_job.py status
```

From Windows, substitute your own SSH alias, using your normal verified host key:

```powershell
ssh -N -L 8188:127.0.0.1:8188 YOUR_SPARK_SSH_ALIAS
```

Open `http://127.0.0.1:8188`. No public firewall port or anonymous public API is needed. `workflows/ui` contains canvas graphs; `workflows/api` contains execution graphs. Do not send a UI graph to `/prompt`. The UI graphs were rebuilt against the recorded node schemas; fresh-version UI compatibility still needs inspection on your installation.

## 3. Prove export separately from inference

```bash
python3 scripts/comfy_job.py submit workflows/api/diagnostic-export.api.json \
  --receipts "$SPARK_MEDIA_ROOT/receipts/export" --execute
```

This creates four solid-color frames and writes a tiny MP4. It proves the export path only. It uses no generative model and cannot be cited as a successful AI-video test. The helper first checks `/object_info`, required inputs and model choices, then confirms the queue is empty before execution.

## 4. Generate an original reference image

Inspect `workflows/api/z-image.api.json`. Its prompt is an original simple robot on a desk, avoiding identifiable people or brand likenesses. Keep the first test small and fixed-seed. The sample image graph uses 1024×1024, eight steps and CFG 1.0.

```bash
python3 scripts/comfy_job.py submit workflows/api/z-image.api.json \
  --receipts "$SPARK_MEDIA_ROOT/receipts/image"             # validate only
python3 scripts/comfy_job.py submit workflows/api/z-image.api.json \
  --receipts "$SPARK_MEDIA_ROOT/receipts/image" --execute
```

The receipt records the submitted graph, its hash, native prompt ID and final history. Read the resulting filename from native output history; the helper does not guess which file is newest. Open the actual PNG and inspect object count, framing, hands/faces if present, unwanted text and unwanted likenesses. Technical success does not imply a usable composition.

For your own prompt, duplicate the JSON and edit only the positive text node, seed and desired settings. Preserve each accepted version rather than overwriting it. The same seed is useful for comparisons but does not guarantee bitwise reproducibility across software/hardware changes.

## 5. Run the first short T2V canary

```bash
python3 scripts/comfy_job.py submit workflows/api/wan-t2v.api.json \
  --receipts "$SPARK_MEDIA_ROOT/receipts/wan-t2v" --execute
```

The starter uses 512×320, 49 native frames, 16 fps, 30 steps and tiled VAE decoding. Its nominal clip duration is 49/16 = 3.0625 seconds. It is a bounded starting point, not a newly measured performance result. The dated research qualification used **81 frames** at the same resolution/frame rate, produced 5.0625 seconds, and measured 286.62 seconds of generation. Whole GPU-handoff/reload time was longer.

Wan expects temporal lengths appropriate to its compression scheme; these starters use `4n+1` frames. Width/height and frame count must satisfy the installed nodes. Raise one parameter at a time after checking memory and output. Do not infer throughput from parameter count or package download speed.

The helper polls only its prompt ID. On timeout it retains the receipt and reports **outcome unknown**; it never submits a duplicate, clears the shared queue or interrupts another user's work. Resume observation with:

```bash
python3 scripts/comfy_job.py observe PROMPT_ID \
  --receipt /path/to/the/saved-receipt.json --timeout 3600
```

Use the real ID and receipt path printed at submission. If the API is unreachable, recover connectivity before deciding whether generation failed. A network failure is not a cancellation receipt.

## 6. Add image-to-video conditioning

Download the optional group:

```bash
python3 scripts/models.py --group i2v --root "$SPARK_MEDIA_ROOT"
python3 scripts/models.py --group i2v --root "$SPARK_MEDIA_ROOT" --download --accept-licenses
```

Copy your selected, rights-cleared reference PNG to `$SPARK_MEDIA_ROOT/comfy/input/input_image.png`, or change the `LoadImage` filename in a versioned graph. No reference image is shipped. Load `workflows/ui/wan-i2v.json` in the canvas to inspect the conditioning connections, or submit its API counterpart:

```bash
python3 scripts/comfy_job.py submit workflows/api/wan-i2v.api.json \
  --receipts "$SPARK_MEDIA_ROOT/receipts/wan-i2v" --execute
```

Specify one subject action and one camera intent per shot. For example: “The small robot raises one arm slowly; static medium camera; desk objects remain fixed.” Negative prompts can discourage artifacts but cannot enforce physics. In our later experiments, a requested push-in became a pullback and a cricket ball traveled differently from the prompt. A graph that executes cannot certify exact camera control.

For larger work, approve a consistent character reference, wardrobe, lighting and location first. Changing a reference can change identity. An approved close-up does not establish full-scene continuity or lip-sync quality.

## 7. Inspect motion and build a source ledger

```bash
python3 scripts/verify_media.py /path/to/generated.mp4 --require-video
ffmpeg -i /path/to/generated.mp4 -vf fps=1 /path/to/contact-%03d.png
```

Inspect the moving clip at full speed, not only the contact sheet: feet, occlusions, hands, facial drift, background flicker and direction. Frame uniqueness can help catch accidental repeats, but random noise can also be unique. Accept motion visually.

Keep a ledger with shot ID, prompt/graph hash, model revision, native dimensions/fps/frame count, generation seconds, native output filename/hash, selected source-frame range and editorial decision. Example: [shot-plan.json](../examples/shot-plan.json). Retain failed takes as failures.

Our original 147-second montage technically decoded but was rejected because most of it animated still images. The corrected 147.2917-second experiment used 30 locally generated Wan clips and a source-frame ledger. This is why our tutorial distinguishes generated motion from a pan over a still. Upscaling a 704×416 source to 720p does not make it native 720p detail; record source and delivery resolutions separately.

## 8. Release memory and restore text inference

After the queue is genuinely idle, stop your own foreground ComfyUI process with Ctrl+C or use the installed application's documented unload function. Restore the exact text service paused earlier and repeat the text/tool check. Do not rely on an HTTP status alone to prove successful inference.

**Checkpoint:** save one reviewed reference image and one reviewed moving clip with receipts. Continue to [Tutorial 3](03-voice-audio-and-finishing.md).
