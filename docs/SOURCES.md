# Primary sources and provenance

Prepared 8 November 2026. Links identify upstream owners; this independent guide does not imply endorsement. Official pages can change; pin code/model revisions when reproducing a result.

## Setup and workflow references

- [NVIDIA DGX Spark documentation](https://docs.nvidia.com/dgx/dgx-spark/).
- [NVIDIA DGX Spark playbooks](https://github.com/NVIDIA/dgx-spark-playbooks).
- [ComfyUI playbook](https://github.com/NVIDIA/dgx-spark-playbooks/tree/main/nvidia/playbook-comfyui), research pin `30883150541743d580c9c347700c6ac99fc396d2`.
- [ComfyUI source](https://github.com/Comfy-Org/ComfyUI), research pin `7cee3ceb1a35503172e0dfb8dbdbdedee2aba8aa` / v0.33.2.
- [Hermes official install documentation](https://hermes-agent.nousresearch.com/docs/getting-started/installation).
- [Hermes providers](https://hermes-agent.nousresearch.com/docs/integrations/providers), [profiles](https://hermes-agent.nousresearch.com/docs/user-guide/profiles), [native cron](https://hermes-agent.nousresearch.com/docs/user-guide/features/cron).
- [Hermes source](https://github.com/NousResearch/hermes-agent), research pin `2bd378ed1b8d6bf2192cb26e0a55ff3091e6bd19` / v0.23.0.
- [Hugging Face download/CLI guidance](https://huggingface.co/docs/huggingface_hub/en/guides/cli).
- [PyTorch installation](https://pytorch.org/get-started/locally/) and [CUDA 13 wheel index](https://download.pytorch.org/whl/cu130).
- [FFmpeg filters](https://ffmpeg.org/ffmpeg-filters.html), [formats](https://ffmpeg.org/ffmpeg-formats.html), [ffprobe](https://ffmpeg.org/ffprobe.html).

## Media models

- [Z-Image-Turbo Comfy packaging](https://huggingface.co/Comfy-Org/Z-Image-Turbo).
- [Wan original source](https://github.com/Wan-Video/Wan2.1) and [Comfy packaging](https://huggingface.co/Comfy-Org/Wan-2.1).
- [Indic-Mio](https://huggingface.co/SPRINGLab/Indic-Mio), revision `25feace00ca76c71c40b1e8d921fd3c2943c545e`.
- [MioCodec 44.1 kHz v2](https://huggingface.co/Aratako/MioCodec-25Hz-44.1kHz-v2), revision `67faba34153fe74e6665991c432a7327e23c5c1c`.
- [MioCodec source](https://github.com/Aratako/MioCodec), revision `f41765d4d6f48649461fbb0c67add80169ce0f00`.
- [TorchAudio WavLM base-plus](https://docs.pytorch.org/audio/main/generated/torchaudio.pipelines.WAVLM_BASE_PLUS.html).
- [ACE-Step 1.5](https://github.com/ace-step/ACE-Step-1.5), optional future music extension rather than a qualified starter component.
- [NVIDIA API catalog](https://build.nvidia.com/), optional explicit hosted route; entitlement and limits are account-specific.

## Internal evidence used to prepare the public summary

The private working directory held the acquisition manifest/receipts, `Model-Verification-Report`, `Hermes-Implementation-Report`, full-motion test/run records, native CUDA preflight, voice-audition/quality reports and the final connectivity checkpoint. Only allowlisted model metadata, workflow graphs and manually prepared summaries were exported. No raw chat history, account/session state, private voice assets or internal archives were copied.

The public examples adapt paths and prompts. Read [TESTED-AND-LIMITATIONS.md](TESTED-AND-LIMITATIONS.md) to distinguish recorded source-environment tests from public-wrapper checks. Link availability and source pins were checked during preparation where the upstream endpoints permitted it; no clean hardware installation was performed for publication.
