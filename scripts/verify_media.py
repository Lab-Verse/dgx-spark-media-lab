"""Probe, fully decode and hash media. This is technical QA, not quality review."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import subprocess


def verify(path: Path, video=False, audio=False):
    probe = subprocess.run(['ffprobe', '-v', 'error', '-show_format', '-show_streams', '-of', 'json', str(path)],
                            check=True, capture_output=True, text=True, timeout=60)
    info = json.loads(probe.stdout)
    duration = float(info.get('format', {}).get('duration', 0))
    if not math.isfinite(duration) or duration <= 0:
        raise ValueError('Missing or invalid duration')
    kinds = {s.get('codec_type') for s in info.get('streams', [])}
    if video and 'video' not in kinds or audio and 'audio' not in kinds:
        raise ValueError('Required stream missing')
    subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-xerror', '-i', str(path), '-map', '0:v?', '-map', '0:a?',
                    '-f', 'null', '-'], check=True, capture_output=True, timeout=3600)
    h = hashlib.sha256()
    with path.open('rb') as source:
        for block in iter(lambda: source.read(4*1024*1024), b''):
            h.update(block)
    return {'file': path.name, 'duration_seconds': duration, 'streams': info['streams'],
            'full_decode': 'PASS', 'sha256': h.hexdigest(), 'human_review': 'pending'}


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('file', type=Path)
    ap.add_argument('--require-video', action='store_true')
    ap.add_argument('--require-audio', action='store_true')
    args = ap.parse_args()
    print(json.dumps(verify(args.file, args.require_video, args.require_audio), indent=2))
