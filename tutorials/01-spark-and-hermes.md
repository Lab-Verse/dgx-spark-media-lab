# Tutorial 1 — Prepare a DGX Spark and connect Hermes to local inference

**Goal:** establish a measured, private local route before asking an agent to generate media. All Linux commands below run on the Spark. Windows is an optional SSH client. This guide targets one Linux/aarch64 GB10 Spark with 128 GB unified memory; other machines need separate qualification.

## 1. Inventory before installing

Read the [NVIDIA hardware documentation](https://docs.nvidia.com/dgx/dgx-spark/) for your device and keep its driver/OS maintenance separate from this tutorial. Do not change drivers or reboot a machine while it has an active render.

```bash
uname -m
nvidia-smi
free -h
df -h "$HOME"
python3 --version
git --version
ffmpeg -version
python3 scripts/preflight.py
```

Expect `aarch64`, a visible NVIDIA GPU, enough disk for selected weights plus intermediate frames, and working Python/FFmpeg. A 128 GB unified-memory specification does not mean 128 GB is freely available for simultaneous model allocations. `nvidia-smi` memory reporting can differ on unified-memory systems; inspect host RAM as well.

Our original acquisition phase selected 170.821 GB in 20 bundles. A later integrity audit covered 245 selected payloads / 464.22 GB logical bytes, including additional ComfyUI files and the existing text-model cache. These are historical selections, not a minimum requirement. The public starter is deliberately selective. Review its size plan before downloading.

Choose an empty location. Preserve an existing Sync model cache and qualified serving environment:

```bash
export SPARK_MEDIA_ROOT="$HOME/spark-media"
mkdir -p "$SPARK_MEDIA_ROOT"
```

This repository never repairs, replaces or stops an existing NVIDIA Sync deployment automatically.

## 2. Build an isolated media runtime

Prerequisites: Python 3.12 with `venv`, Git, FFmpeg and a CUDA-compatible NVIDIA driver. Install missing OS packages through your normal administration process. Inspect the setup script before running it:

```bash
less scripts/setup_media.sh
bash scripts/setup_media.sh "$SPARK_MEDIA_ROOT"
```

The script creates a new `.venv`, installs the recorded PyTorch CUDA 13 wheel set, checks a real BF16 matrix multiplication, and checks out pinned ComfyUI and MioCodec sources. It refuses existing runtime/source directories so it cannot upgrade a working installation accidentally. It writes an install log and `pip freeze` into your local root. The new script itself has offline syntax checks; its complete fresh-install path has not been rerun on the disconnected research Spark.

Our observed runtime was Python 3.12, PyTorch `2.11.0+cu130`, TorchAudio `2.11.0`, TorchVision `0.26.0`, Transformers `5.22.1`, ComfyUI `v0.33.2`. See [versions.json](../config/versions.json). These are reproduction pins, not promises about whichever upstream release is latest. If a wheel is unavailable for your platform, stop and record the mismatch. Do not quietly install an x86 build, CPU-only replacement or a different CUDA stack.

NVIDIA also maintains a [ComfyUI playbook](https://github.com/NVIDIA/dgx-spark-playbooks/tree/main/nvidia/playbook-comfyui). Its container and host recipes are alternatives. Our qualified host route used real TorchAudio; the inspected NGC container recipe had an audio stub and is unsuitable for this guide's MioCodec audio stage. Do not mix those two environments.

## 3. Validate an existing local text endpoint

Our research deployment reused a local OpenAI-compatible NVIDIA Sync text server. Its model name and memory footprint are recorded as observations, not a requirement to download that exact model. On another machine, use an already qualified local server, or install one using [NVIDIA's inference recipes](https://github.com/NVIDIA/dgx-spark-playbooks). Confirm the backend supports structured tool calls; plain text completion is insufficient for a tool-using agent.

```bash
python3 scripts/check_llm.py --base-url http://127.0.0.1:18765/v1
python3 scripts/check_llm.py --base-url http://127.0.0.1:18765/v1 \
  --model YOUR_SERVED_MODEL_ID --chat --tool-test
```

Replace `YOUR_SERVED_MODEL_ID` with the ID returned by `/models`. The helper permits loopback URLs only, avoids provider fallback and validates a tiny structured tool-call round trip. If your server requires a key, set `LOCAL_LLM_API_KEY` privately in the shell; no key is bundled or printed. A passing check qualifies that route only at that time.

If you do not already have an inference server, this guide is not evidence that a new server is installed: complete the selected official server recipe first, record its version and repeat the checks. The image/video/voice tutorials can also run directly without Hermes.

## 4. Install Hermes from its official source

Hermes is the agent framework; the local text model supplies inference. Hermes does not include the media weights. The research installation used official Hermes `v0.23.0`, commit `2bd378ed1b8d6bf2192cb26e0a55ff3091e6bd19`. Consult the [official installation guide](https://hermes-agent.nousresearch.com/docs/getting-started/installation) if platform support changes.

Download a pinned installer to a file, inspect it, then run it in a fresh home:

```bash
export HERMES_HOME="$SPARK_MEDIA_ROOT/hermes-state"
export HERMES_INSTALL_DIR="$SPARK_MEDIA_ROOT/hermes-agent"
curl -fL https://raw.githubusercontent.com/NousResearch/hermes-agent/2bd378ed1b8d6bf2192cb26e0a55ff3091e6bd19/scripts/install.sh \
  -o "$SPARK_MEDIA_ROOT/hermes-install.sh"
less "$SPARK_MEDIA_ROOT/hermes-install.sh"
bash "$SPARK_MEDIA_ROOT/hermes-install.sh" \
  --commit 2bd378ed1b8d6bf2192cb26e0a55ff3091e6bd19 \
  --dir "$HERMES_INSTALL_DIR" --hermes-home "$HERMES_HOME" --non-interactive
hermes --version
hermes model
```

Use the interactive model setup to choose your custom local OpenAI-compatible endpoint and the served model ID. [Provider configuration](https://hermes-agent.nousresearch.com/docs/integrations/providers) is version dependent. [hermes-local.yaml](../config/hermes-local.yaml) is a merge example, not a whole replacement configuration. Check `hermes --help`, `hermes model --help` and your installed configuration before merging it. Explicitly disable automatic provider recovery/fallback and external-login adoption; verify by making a bounded request against an unavailable test endpoint in a separate temporary profile. Do not interrupt the live route to test failure.

## 5. Separate workspaces and define permissions

Create operations, creative and personal profiles using the installed CLI's profile help. Use [official profile documentation](https://hermes-agent.nousresearch.com/docs/user-guide/profiles) for the exact version. Give each workspace a `FACTS.md` and `PERMISSIONS.md`. A useful creative permission file says:

```text
Use only this workspace and the local endpoints.
Save scripts, posts and edits as drafts.
Ask for an explicit destination before sending or publishing.
Do not access other profiles, upload private voice references or invent connectors.
Use one heavy GPU stage at a time. Never stop an unrelated process.
Record job IDs and inspect existing work before retrying.
```

Profiles provide memory and configuration separation under one OS user. Stronger isolation requires OS permissions or another security boundary; a prompt is not access control.

Copy [the media skill](../skills/spark-media/SKILL.md) into the chosen profile's skill directory after replacing its local repository/root placeholders. It invokes ordinary scripts and ComfyUI. It does not install another orchestrator, queue service or dashboard.

Try: “Write an original 20-second Urdu narration with three shots. Save the canonical text, a separate pronunciation version and a shot plan. Do not generate or publish yet.” Inspect the files and source claims before execution.

## 6. Plan GPU handoff and recovery

Our recorded Qwen allocation was roughly 99 GiB, and cold reload took about four minutes in one test. A measured speech/video/reload cycle temporarily removed local text inference for about 9 minutes 19 seconds. These numbers vary with settings and caching.

Record the exact text-service owner and stop/start commands in a private runbook. When rendering, verify no unrelated request is active, pause only that identified service, and verify memory is released. Generate through Tutorial 2, release ComfyUI weights, restart the same service, and rerun `check_llm.py`. The public scripts never stop arbitrary containers or call `pkill`.

Keep a human-operated SSH terminal for status while local reasoning is paused. A gateway process can stay alive while its model is unavailable. Do not interpret that as working chat inference or start cloud failover to conceal it.

## 7. Optional native supervision

Once CLI tests pass, use the installed Hermes gateway/native scheduling commands (`hermes gateway --help`, `hermes cron --help`). Start with a draft-only task, inspect an actual run and test restore into a separate temporary profile. Bind APIs to loopback, require native authentication and keep backups private/off-device where appropriate. Scheduled automation is optional; this repository installs none.

The research passed bounded process-crash recovery and backup/export/import checks. A complete host reboot and 48–72-hour unattended soak remained unverified. Test those deliberately on your own installation before promising unattended production.

**Checkpoint:** save hardware/runtime versions, endpoint checks and selected service recovery commands privately. Continue to [Tutorial 2](02-images-and-video.md).
