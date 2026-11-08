# Broader research model inventory

This is the dated acquisition inventory from 6 November 2026, not a recommendation to download every model. The public starter is smaller. Integrity checks do not qualify runtime, native-language quality or commercial rights. Model names, revisions and terms come from the frozen research selection. No weights are included.

| Original selected bundle | Revision | GB (decimal) | Recorded license metadata |
| --- | --- | ---: | --- |
| [snakers4--silero-vad-onnx](https://github.com/NVIDIA/dgx-spark-playbooks) | `066409f3d9db45a30d21dfcbf9147826ffdd7052` | 0.002 | MIT |
| [xinntao--Real-ESRGAN-x4plus](https://github.com/xinntao/Real-ESRGAN/blob/master/LICENSE) | `v0.1.0;asset:40831506` | 0.067 | BSD-3-Clause |
| [facebookresearch--demucs-htdemucs](https://github.com/NVIDIA/dgx-spark-playbooks) | `e976d93ecc3865e5757426930257e200846a520a` | 0.084 | MIT |
| [speechbrain/spkrec-ecapa-voxceleb](https://huggingface.co/speechbrain/spkrec-ecapa-voxceleb) | `0f99f2d0ebe89ac095bcc5903c4dd8f72b367286` | 0.089 | apache-2.0 |
| [torchaudio--wavlm-base-plus](https://docs.pytorch.org/audio/main/generated/torchaudio.pipelines.WAVLM_BASE_PLUS.html) | `S3-version:V712l76ZtySwp3z5Z5fJGU4LAioHxK9Q` | 0.378 | MIT (selected TorchAudio redistribution) |
| [facebook/wav2vec2-base-960h](https://huggingface.co/facebook/wav2vec2-base-960h) | `22aad52d435eb6dbaf354bdad9b0da84ce7d6156` | 0.378 | apache-2.0 |
| [nvidia/Nemotron-3-Diarization](https://huggingface.co/nvidia/Nemotron-3-Diarization) | `f667ed73aee57d40cc39428eb768b4fd87a0a29e` | 0.397 | openmdw-1.1 |
| [Aratako/MioCodec-25Hz-44.1kHz-v2](https://huggingface.co/Aratako/MioCodec-25Hz-44.1kHz-v2) | `67faba34153fe74e6665991c432a7327e23c5c1c` | 0.528 | mit |
| [SPRINGLab/Indic-Mio](https://huggingface.co/SPRINGLab/Indic-Mio) | `25feace00ca76c71c40b1e8d921fd3c2943c545e` | 1.239 | apache-2.0 |
| [openai/whisper-large-v3-turbo](https://huggingface.co/openai/whisper-large-v3-turbo) | `41f01f3fe87f28c78e2fbf8b568835947dd65ed9` | 1.622 | mit |
| [openai/whisper-large-v3](https://huggingface.co/openai/whisper-large-v3) | `06f233fe06e710322aca913c1bc4249a0d71fce1` | 3.092 | apache-2.0 |
| [ResembleAI/chatterbox](https://huggingface.co/ResembleAI/chatterbox) | `5bb1f6ee58e50c3b8d408bc82a6d3740c2db6e18` | 3.209 | mit |
| [Qwen/Qwen3-TTS-12Hz-1.7B-Base](https://huggingface.co/Qwen/Qwen3-TTS-12Hz-1.7B-Base) | `fd4b254389122332181a7c3db7f27e918eec64e3` | 4.544 | apache-2.0 |
| [ACE-Step/Ace-Step1.5](https://huggingface.co/ACE-Step/Ace-Step1.5) | `19671f406d603126926c1b7e2adc169acbcade22` | 5.300 | mit |
| [openai/gpt-oss-20b](https://huggingface.co/openai/gpt-oss-20b) | `6cee5e81ee83917806bbde320786a8fb61efebee` | 13.789 | apache-2.0 |
| [black-forest-labs/FLUX.2-klein-4B](https://huggingface.co/black-forest-labs/FLUX.2-klein-4B) | `e7b7dc27f91deacad38e78976d1f2b499d76a294` | 15.989 | Apache-2.0 |
| [Qwen/Qwen3-VL-8B-Instruct](https://huggingface.co/Qwen/Qwen3-VL-8B-Instruct) | `0c351dd01ed87e9c1b53cbc748cba10e6187ff3b` | 17.546 | Apache-2.0 |
| [ACE-Step/acestep-v15-xl-turbo](https://huggingface.co/ACE-Step/acestep-v15-xl-turbo) | `d4a0b288b83ebb7e25a8c0b32c573c22e134e8ee` | 19.953 | mit |
| [Wan-AI/Wan2.2-TI2V-5B-Diffusers](https://huggingface.co/Wan-AI/Wan2.2-TI2V-5B-Diffusers) | `b8fff7315c768468a5333511427288870b2e9635` | 34.203 | Apache-2.0 |
| [Qwen/Qwen3-Coder-Next-GGUF](https://huggingface.co/Qwen/Qwen3-Coder-Next-GGUF) | `b82fb7382639d97b38fa7672e526c760c2fb358e` | 48.411 | apache-2.0 |

The later ComfyUI inventory added image/video component bundles, including Wan 2.1 14B, Z-Image, HunyuanVideo, Cosmos, HiDream and FLUX variants. The starter exports only Z-Image and Wan 2.1 selections. Conditional/noncommercial alternatives remain outside the starter; inspect exact weight terms before use.

The original work also used a separately maintained local NVIDIA Sync Qwen/DFlash text service. It was preserved rather than repurposed as a media cache. Public setup can reuse a qualified local tool-calling endpoint; it does not export that machine deployment.

Demucs/VAD/diarization/ASR/alignment are useful ingredients for a future rights-cleared dubbing pilot, but acquiring them does not establish overlapping-speaker separation, identity transfer, translation fidelity or lip sync. ACE-Step music inference, multilingual native listening and remaining research runtimes need their own short qualification runs. See [the evidence ledger](TESTED-AND-LIMITATIONS.md).
