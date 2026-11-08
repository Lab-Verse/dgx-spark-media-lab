"""Offline source-package checks; prints filenames only for suspicious content."""
import ast
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
ALLOWED = {'.py', '.sh', '.json', '.yaml', '.yml', '.md', '.txt', '.srt'}
NAMES = {'LICENSE', 'NOTICE', '.gitignore', '.gitattributes'}


def check():
    failures = []
    paths = [p for p in ROOT.rglob('*') if p.is_file() and '.git' not in p.parts and '__pycache__' not in p.parts]
    # This is a publication aid, not a comprehensive secret detector.
    patterns = [r'-----BEGIN (?:OPENSSH |RSA |EC )?PRIVATE KEY-----',
                r'gh[pousr]_[A-Za-z0-9]{20,}', r'github_pat_[A-Za-z0-9_]{30,}',
                r'hf_[A-Za-z0-9]{25,}', r'sk-(?:proj-)?[A-Za-z0-9_-]{30,}',
                r'\bAKIA[A-Z0-9]{16}\b', r'\b192\.168\.\d+\.\d+\b',
                r'(?i)[A-Z]:[\\/](?:Users|work|LiveProjects)[\\/]',
                r'/home/(?!YOUR_USER)[A-Za-z0-9_-]+/',
                r'https?://[^\s/@:]+:[^\s/@]+@']
    for path in paths:
        relative = str(path.relative_to(ROOT))
        if path.is_symlink() or path.suffix not in ALLOWED and path.name not in NAMES:
            failures.append(relative + ': unexpected file type or symlink')
            continue
        text = path.read_text(encoding='utf-8')
        if any(re.search(pattern, text) for pattern in patterns):
            failures.append(relative + ': potential secret/private identifier')
        if path.suffix == '.py':
            ast.parse(text, filename=relative)
        if path.suffix == '.json':
            json.loads(text)
        if path.suffix == '.md':
            for link in re.findall(r'\]\(([^)\s]+)\)', text):
                if link.startswith(('https://', 'http://', '#', 'mailto:')):
                    continue
                dest = (path.parent / link.split('#')[0]).resolve()
                if not dest.exists():
                    failures.append(relative + ': broken relative link ' + link)
    if failures:
        raise SystemExit('\n'.join(failures))
    print(f'PASS: {len(paths)} source files, syntax/JSON, relative document links and bounded private-data patterns.')


if __name__ == '__main__':
    check()
