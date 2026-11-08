#!/usr/bin/env bash
# Creates a fresh local runtime only. Inspect before execution.
set -euo pipefail
root="${1:?Usage: bash scripts/setup_media.sh /absolute/empty-runtime-root}"
[[ "$root" = /* ]] || { echo 'Use an absolute root'; exit 2; }
[[ "$(uname -m)" = aarch64 && "$(uname -s)" = Linux ]] || { echo 'This recipe targets Linux aarch64'; exit 2; }
python3 -c 'import sys; assert sys.version_info[:2] == (3,12), "Recorded runtime requires Python 3.12"'
command -v git >/dev/null
command -v ffmpeg >/dev/null
command -v ffprobe >/dev/null
nvidia-smi
mkdir -p "$root"
root="$(cd "$root" && pwd -P)"
for component in .venv ComfyUI MioCodec; do
  [[ ! -e "$root/$component" ]] || { echo "Refusing existing $component; use a fresh runtime root"; exit 2; }
done
repo="$(cd "$(dirname "$0")/.." && pwd -P)"
mkdir -p "$root/receipts"
exec > >(tee "$root/receipts/setup-$(date -u +%Y%m%dT%H%M%SZ).log") 2>&1
python3 -m venv "$root/.venv"
py="$root/.venv/bin/python"
"$py" -m pip install 'torch==2.11.0' 'torchaudio==2.11.0' 'torchvision==0.26.0' --index-url https://download.pytorch.org/whl/cu130
"$py" -m pip install -r "$repo/config/requirements-media.txt"
"$py" - <<'PY'
import torch
assert torch.cuda.is_available(), 'CUDA is unavailable'
x = torch.randn((256,256), device='cuda', dtype=torch.bfloat16)
y = x @ x.T
torch.cuda.synchronize()
assert torch.isfinite(y).all()
print({'torch':torch.__version__, 'cuda':torch.version.cuda, 'gpu':torch.cuda.get_device_name(), 'bf16_matmul':'PASS'})
PY
git clone https://github.com/Comfy-Org/ComfyUI.git "$root/ComfyUI"
git -C "$root/ComfyUI" checkout --detach 7cee3ceb1a35503172e0dfb8dbdbdedee2aba8aa
# Freeze installed distributions to valid constraints (requirements may use extras;
# pip constraints cannot). Preserve the matched CUDA/audio wheels and base runtime.
"$py" -m pip freeze > "$root/receipts/before-comfy-constraints.txt"
"$py" -m pip install -c "$root/receipts/before-comfy-constraints.txt" -r "$root/ComfyUI/requirements.txt"
git clone https://github.com/Aratako/MioCodec.git "$root/MioCodec"
git -C "$root/MioCodec" checkout --detach f41765d4d6f48649461fbb0c67add80169ce0f00
"$py" -m pip install --no-deps "$root/MioCodec"
mkdir -p "$root/comfy/models" "$root/comfy/input" "$root/comfy/output" "$root/comfy/user" "$root/runs"
"$py" - "$root" <<'PY'
from pathlib import Path
import json,sys
root=Path(sys.argv[1])
text='spark_media:\n  base_path: '+json.dumps(str(root/'comfy/models'))+'\n'
text+=''.join('  '+k+': '+k+'\n' for k in ['diffusion_models','text_encoders','vae','clip_vision'])
(root/'extra_model_paths.yaml').write_text(text)
PY
"$py" -m pip check
"$py" -m pip freeze > "$root/receipts/requirements-installed.txt"
echo 'Runtime prepared. Follow the tutorial to download selected models and start ComfyUI.'
