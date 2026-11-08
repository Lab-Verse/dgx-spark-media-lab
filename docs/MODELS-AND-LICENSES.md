# Model selection and license notes

This repository contains code, documentation, configuration and workflow graphs. **No model weights are redistributed.** The Apache-2.0 repository license applies to this contribution, not to everything you may download or generate.

The exact public starter revisions, filenames, expected sizes and integrity methods are in [models.json](../config/models.json). Read the pinned model card and each dependency's terms before enabling downloads. A repackaged checkpoint's metadata does not replace the original model/auxiliary terms.

For the wider context, see the [20-bundle research inventory](RESEARCH-MODEL-INVENTORY.md). It is a dated acquisition list, not a claim that every model ran successfully.

| Role | Starter selection | Terms recorded at research time | Status |
| --- | --- | --- | --- |
| Image | [Comfy-Org/Z-Image-Turbo](https://huggingface.co/Comfy-Org/Z-Image-Turbo), selected diffusion/text/VAE files | Apache-2.0 metadata; inspect original dependencies | Public starter; image path based on local research |
| T2V / I2V | [Comfy-Org/Wan-2.1](https://huggingface.co/Comfy-Org/Wan-2.1), T2V 14B / optional I2V 720p 14B, UMT5, VAE and CLIP Vision | Apache-2.0 metadata; check [original Wan project](https://github.com/Wan-Video/Wan2.1) and component terms | Dated T2V test exists; public variants need fresh qualification |
| Speech model | [SPRINGLab/Indic-Mio](https://huggingface.co/SPRINGLab/Indic-Mio) | Apache-2.0 card | Experimental narration; no language-quality guarantee |
| Speech codec | [Aratako/MioCodec-25Hz-44.1kHz-v2](https://huggingface.co/Aratako/MioCodec-25Hz-44.1kHz-v2) and [source](https://github.com/Aratako/MioCodec) | MIT metadata/source notice | Exact selected codec; do not swap sample rates silently |
| Codec dependency | [TorchAudio WavLM base-plus](https://docs.pytorch.org/audio/main/generated/torchaudio.pipelines.WAVLM_BASE_PLUS.html) | Selected TorchAudio redistribution documented as MIT; upstream provenance still matters | Official-origin/size plus local full-digest baseline |
| Agent | [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent) | MIT source | Installed/tested separately in research; no bundled source/account state |
| Optional neural music | [ACE-Step 1.5](https://github.com/ace-step/ACE-Step-1.5) | Review code, chosen weights and every auxiliary model's current terms | Research acquisition only; excluded from starter downloader |

The broader private research also examined Whisper, VAD, diarization, Demucs, translation/coding/VL models, FLUX variants, HunyuanVideo and Cosmos. Some were acquired-only; some selections had conditional, gated or noncommercial terms. They are **not** all included, all tested or collectively cleared for commercial use. FLUX.1 dev and FLUX.2 klein 4B are different selections and must not share an assumed license or runtime claim.

Use original or expressly cleared scripts/images/music. Obtain separate permission for an identifiable speaker reference and the intended distribution of synthetic speech. Rights to the model are distinct from rights to a person's identity, an underlying literary work, source video, logos, music, likenesses or data. Do not publish our private adaptation or owner voice from other folders as repository examples.

The included procedural score is original example synthesis code, not sampled music or a neural music benchmark. The original generic narration is provided as editable tutorial text. Check publication/disclosure requirements for the destination platform before releasing realistic synthetic media; [YouTube's official disclosure guidance](https://support.google.com/youtube/answer/14328491) is one example.
