"""Plan or sequentially acquire explicitly selected, pinned public artifacts."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path, PurePosixPath
import urllib.parse
import urllib.request

MANIFEST = Path(__file__).resolve().parents[1] / 'config/models.json'


def target(root: Path, relative: str) -> Path:
    part = PurePosixPath(relative)
    if part.is_absolute() or not part.parts or any(p in ('..', '.') for p in part.parts) or '\\' in relative or ':' in relative:
        raise ValueError('Unsafe manifest destination')
    result = root.joinpath(*part.parts)
    if any(p.is_symlink() for p in (result, *result.parents)):
        raise ValueError('Symlink destination refused')
    result.resolve().relative_to(root.resolve())
    return result


def digest(path: Path, git_blob: bool = False) -> str:
    h = hashlib.sha1() if git_blob else hashlib.sha256()
    if git_blob:
        h.update(f'blob {path.stat().st_size}\0'.encode())
    with path.open('rb') as f:
        for block in iter(lambda: f.read(4 * 1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def verify(path: Path, item: dict) -> dict:
    if path.stat().st_size != item['size_bytes']:
        raise ValueError('Size mismatch: ' + item['destination'])
    sha = digest(path)
    if item.get('sha256') and sha != item['sha256']:
        raise ValueError('SHA-256 mismatch: ' + item['destination'])
    if item.get('git_blob_sha1') and digest(path, True) != item['git_blob_sha1']:
        raise ValueError('Git blob mismatch: ' + item['destination'])
    return {'destination': item['destination'], 'bytes': path.stat().st_size,
            'sha256': sha, 'verification': item['verification']}


def url_for(item: dict) -> str:
    if item.get('url'):
        url = item['url']
    else:
        path = urllib.parse.quote(item['file'], safe='/')
        url = f"https://huggingface.co/{item['repo']}/resolve/{item['revision']}/{path}"
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme != 'https' or parsed.hostname not in ('huggingface.co', 'download.pytorch.org') or parsed.username:
        raise ValueError('Unexpected artifact origin')
    return url


def acquire(root: Path, items: list[dict]) -> list[dict]:
    records = []
    for item in items:
        path = target(root, item['destination'])
        if path.exists():
            record = verify(path, item)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            partial = path.with_name(path.name + '.part')
            if partial.is_symlink():
                raise ValueError('Symlink partial refused')
            request = urllib.request.Request(url_for(item), headers={'User-Agent': 'Labverse-Spark-Media-Lab/0.1'})
            with urllib.request.urlopen(request, timeout=120) as response:
                if response.status != 200 or urllib.parse.urlsplit(response.url).scheme != 'https':
                    raise ValueError('Unexpected response')
                written = 0
                with partial.open('wb') as output:
                    while block := response.read(4 * 1024 * 1024):
                        written += len(block)
                        if written > item['size_bytes']:
                            raise ValueError('Payload exceeds declared size')
                        output.write(block)
            record = verify(partial, item)
            # Never overwrite an artifact another process committed during transfer.
            # A hard link is atomic and fails if the destination exists.
            import os
            os.link(partial, path)
            partial.unlink()
        records.append(record)
        print(json.dumps(record), flush=True)
    return records


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--group', required=True, choices=['image', 'video', 'i2v', 'voice'])
    ap.add_argument('--root', type=Path, required=True)
    ap.add_argument('--download', action='store_true')
    ap.add_argument('--accept-licenses', action='store_true')
    args = ap.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))
    items = [item for item in manifest['files'] if args.group in item['groups']]
    root = args.root.absolute()
    for item in items:
        target(root, item['destination'])
        url_for(item)
    missing = sum(item['size_bytes'] for item in items if not target(root, item['destination']).exists())
    print(json.dumps({'group': args.group, 'files': len(items), 'selected_bytes': sum(i['size_bytes'] for i in items),
                      'missing_bytes': missing, 'mode': 'download' if args.download else 'plan'}, indent=2))
    for item in items:
        print(item['destination'], item['size_bytes'], item['license'])
    if not args.download:
        return
    if not args.accept_licenses:
        ap.error('Review upstream terms and pass --accept-licenses explicitly.')
    root.mkdir(parents=True, exist_ok=True)
    if shutil.disk_usage(root).free < missing + 5_000_000_000:
        raise SystemExit('Insufficient free space plus 5 GB safety margin.')
    # Serialize acquisitions under this root; no shared worker service.
    import os
    lock_path = target(root, 'download.lock')
    fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    try:
        os.close(fd)
        rows = acquire(root, items)
        receipts = target(root, 'receipts/downloads')
        receipts.mkdir(parents=True, exist_ok=True)
        from datetime import datetime, timezone
        stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
        (receipts / f'{args.group}-{stamp}.json').write_text(json.dumps(rows, indent=2), encoding='utf-8')
    finally:
        lock_path.unlink()


if __name__ == '__main__':
    main()
