"""Create a simple original procedural score, not neural music inference."""
import argparse
import math
from pathlib import Path
import struct
import wave


def write_score(path: Path, seconds: float):
    if not math.isfinite(seconds) or not .5 <= seconds <= 600:
        raise ValueError('Duration must be 0.5–600 seconds')
    rate = 24000
    notes = [220., 261.625565, 329.627557, 293.664768, 246.941651, 293.664768, 349.228231, 329.627557]
    # Exclusive create: preserve earlier takes.
    with path.open('xb') as output, wave.open(output, 'wb') as wav:
        wav.setparams((1, 2, rate, 0, 'NONE', 'not compressed'))
        frames = bytearray()
        for n in range(round(seconds * rate)):
            t = n / rate
            frequency = notes[int(t / .75) % len(notes)]
            phase = t % .75
            envelope = min(1., phase / .04, (.75 - phase)/.18, t/.15, (seconds-t)/.4)
            value = .12 * envelope * (math.sin(2*math.pi*frequency*t) + .2*math.sin(4*math.pi*frequency*t))
            frames.extend(struct.pack('<h', round(value*32767)))
            if len(frames) >= 65536:
                wav.writeframesraw(frames)
                frames.clear()
        wav.writeframes(frames)


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--seconds', type=float, required=True)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    write_score(args.output, args.seconds)
    print('Original procedural WAV written:', args.output)
