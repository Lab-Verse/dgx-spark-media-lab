"""Read-only local inventory; no network or service changes."""
import json
import platform
import shutil
import subprocess
import sys


def command(args):
    if not shutil.which(args[0]):
        return {'available': False}
    result = subprocess.run(args, capture_output=True, text=True, timeout=30)
    return {'available': True, 'exit_code': result.returncode, 'output': result.stdout[:4000]}


if __name__ == '__main__':
    print(json.dumps({'architecture': platform.machine(), 'os': platform.system(),
                      'python': sys.version.split()[0],
                      'disk_free_bytes': shutil.disk_usage('.').free,
                      'gpu': command(['nvidia-smi', '--query-gpu=name,driver_version', '--format=csv,noheader']),
                      'ffmpeg': command(['ffmpeg', '-version']),
                      'memory': command(['free', '-h'])}, indent=2))
