"""Offline experimental Indic-Mio narration with a zero speaker embedding."""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import re
import time


def speech_codes(tokens, offset):
    codes = [t - offset for t in tokens if offset <= t < offset + 12800]
    if not codes:
        raise ValueError('No speech tokens generated')
    return codes


def codec_keys(missing, unexpected):
    bad = [k for k in missing if not k.startswith(('ssl_feature_extractor.', 'conv_upsample.')) and k != 'istft_head.istft.window']
    if bad or unexpected:
        raise ValueError('Unexplained codec weight mismatch')


def offline_wavlm(path):
    import torch
    import torchaudio
    from miocodec.module.ssl_extractor import SSLFeatureExtractor
    def init(self, model_name='wavlm_base_plus', output_layer=None, sample_rate=16000):
        if model_name != 'wavlm_base_plus':
            raise ValueError('Unsupported SSL dependency')
        torch.nn.Module.__init__(self)
        bundle = torchaudio.pipelines.WAVLM_BASE_PLUS
        # Version-sensitive private API, pinned to the recorded TorchAudio runtime.
        self.model = torchaudio.models.wavlm_model(**bundle._params)
        self.model.load_state_dict(torch.load(path, map_location='cpu', weights_only=True), strict=True)
        self.model.eval()
        self.feature_dim = bundle._params['encoder_embed_dim']
        self.ssl_sample_rate = bundle.sample_rate
        self.output_layer = output_layer if output_layer is not None else -1
        self.resampler = torchaudio.transforms.Resample(sample_rate, bundle.sample_rate) if sample_rate != bundle.sample_rate else None
    SSLFeatureExtractor.__init__ = init


def segments_from(path):
    segments = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(segments, list) or not 1 <= len(segments) <= 50:
        raise ValueError('Expected 1–50 narration segments')
    ids = set()
    for segment in segments:
        if not isinstance(segment, dict):
            raise ValueError('Each segment must be an object')
        key, text = segment.get('id'), segment.get('text')
        if not isinstance(key, str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,64}', key) or key in ids:
            raise ValueError('Invalid or duplicate segment ID')
        if not isinstance(text, str) or not text.strip() or len(text) > 600 or any(c in text for c in '<>\0'):
            raise ValueError('Use short plain-text narration without control tags')
        ids.add(key)
    return segments


def output_path(root, output):
    raw = output.absolute()
    if '..' in raw.parts or any(p.is_symlink() for p in (raw, *raw.parents)):
        raise ValueError('Traversal or symlink output refused')
    resolved = raw.resolve()
    relative = resolved.relative_to(root.resolve() / 'runs')
    if not relative.parts:
        raise ValueError('Use a new child directory under runs')
    return resolved


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root', type=Path, required=True)
    ap.add_argument('--script', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--device', choices=['cpu', 'cuda'], default='cpu')
    ap.add_argument('--temperature', type=float, default=.6)
    ap.add_argument('--top-p', type=float, default=.9)
    ap.add_argument('--seed', type=int, default=2406)
    ap.add_argument('--max-new-tokens', type=int, default=1000)
    args = ap.parse_args()
    if not all(math.isfinite(v) for v in (args.temperature, args.top_p)) or not .1 <= args.temperature <= 1.5 or not .1 <= args.top_p <= 1 or not 64 <= args.max_new_tokens <= 2000:
        ap.error('Invalid sampling bounds')
    segments = segments_from(args.script)
    args.root = args.root.resolve()
    args.output = output_path(args.root, args.output)
    for name in ('HF_HUB_OFFLINE', 'TRANSFORMERS_OFFLINE'):
        os.environ[name] = '1'
    os.environ['HF_HUB_DISABLE_TELEMETRY'] = '1'
    from models import MANIFEST, target, verify
    manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))
    for item in manifest['files']:
        if 'voice' in item['groups']:
            verify(target(args.root, item['destination']), item)
    args.output.mkdir(parents=True, exist_ok=False)
    import numpy as np
    import soundfile as sf
    import torch
    from safetensors.torch import load_file
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from miocodec import MioCodecModel
    voice = args.root / 'voice/models'
    offline_wavlm(voice / 'wavlm/wavlm_base_plus.pth')
    tokenizer = AutoTokenizer.from_pretrained(voice / 'Indic-Mio', local_files_only=True, trust_remote_code=False)
    offset = tokenizer.convert_tokens_to_ids('<|s_0|>')
    if offset is None or tokenizer.convert_ids_to_tokens(offset) != '<|s_0|>':
        raise ValueError('Unexpected speech vocabulary')
    dtype = torch.float32 if args.device == 'cpu' else torch.bfloat16
    model = AutoModelForCausalLM.from_pretrained(voice / 'Indic-Mio', local_files_only=True,
             trust_remote_code=False, torch_dtype=dtype, attn_implementation='sdpa').eval().to(args.device)
    codec = MioCodecModel.from_hparams(str(voice / 'MioCodec/config.yaml'))
    state = codec.load_state_dict(load_file(str(voice / 'MioCodec/model.safetensors')), strict=False)
    codec_keys(state.missing_keys, state.unexpected_keys)
    if 'istft_head.istft.window' in state.missing_keys:
        window = codec.istft_head.istft.window
        if window.requires_grad or not torch.equal(window, torch.hann_window(codec.config.n_fft, dtype=window.dtype, device=window.device)):
            raise ValueError('Unexpected Hann buffer')
    if codec.config.sample_rate != 44100 or not codec.config.use_wave_decoder:
        raise ValueError('Wrong codec configuration')
    codec = codec.eval().to(args.device)
    embedding = torch.zeros(codec.global_encoder.output_dim, device=args.device)
    records = []
    for index, segment in enumerate(segments):
        torch.manual_seed(args.seed + index)
        start = time.monotonic()
        prompt = tokenizer.apply_chat_template([{'role': 'user', 'content': segment['text']}], tokenize=False, add_generation_prompt=True)
        inputs = tokenizer(prompt, return_tensors='pt').to(args.device)
        with torch.inference_mode():
            result = model.generate(**inputs, max_new_tokens=args.max_new_tokens, temperature=args.temperature,
                top_p=args.top_p, do_sample=True, use_cache=True, pad_token_id=tokenizer.eos_token_id)
            tokens = result[0, inputs.input_ids.shape[1]:].tolist()
            if len(tokens) >= args.max_new_tokens:
                raise ValueError('Token limit reached; shorten the narration')
            codes = speech_codes(tokens, offset)
            waveform = codec.decode(global_embedding=embedding, content_token_indices=torch.tensor(codes, dtype=torch.long, device=args.device))
            audio = waveform.float().cpu().numpy().reshape(-1)
        if len(audio) < 22050 or not np.isfinite(audio).all() or np.max(np.abs(audio)) < 1e-5:
            raise ValueError('Silent, short or invalid waveform')
        audio *= min(1., .98 / float(np.max(np.abs(audio))))
        path = args.output / (segment['id'] + '.wav')
        sf.write(path, audio, 44100, subtype='PCM_16')
        records.append({**segment, 'file': path.name, 'sample_rate': 44100, 'duration_seconds': len(audio)/44100,
                        'wall_seconds': time.monotonic()-start, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                        'seed': args.seed+index, 'temperature': args.temperature, 'top_p': args.top_p})
        evidence = {'voice_mode': 'experimental_zero_embedding', 'device': args.device,
                    'model_manifest_sha256': hashlib.sha256(MANIFEST.read_bytes()).hexdigest(),
                    'human_listening': 'pending', 'segments': records}
        (args.output / 'speech-evidence.json').write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding='utf-8')
        print(json.dumps(records[-1], ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
