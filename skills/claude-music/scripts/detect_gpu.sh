#!/usr/bin/env bash
# Detect GPU capabilities for claude-music
# Output: JSON with gpu_name, driver, vram_total_mb, vram_free_mb, tier, recommendations
set -euo pipefail

if ! command -v nvidia-smi &>/dev/null; then
    echo '{"gpu_detected":false,"error":"nvidia-smi not found"}'
    exit 0
fi

GPU_NAME=$(nvidia-smi --query-gpu=name --format=csv,noheader,nounits 2>/dev/null | head -1 | xargs)
DRIVER=$(nvidia-smi --query-gpu=driver_version --format=csv,noheader,nounits 2>/dev/null | head -1 | xargs)
VRAM_TOTAL=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits 2>/dev/null | head -1 | xargs)
VRAM_FREE=$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits 2>/dev/null | head -1 | xargs)
VRAM_USED=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits 2>/dev/null | head -1 | xargs)
CUDA_CAP=$(nvidia-smi --query-gpu=compute_cap --format=csv,noheader,nounits 2>/dev/null | head -1 | xargs)

if [ "$VRAM_FREE" -ge 16000 ]; then
    TIER="xl"; REC_MODEL="acestep-v15-xl-turbo"; REC_LM="acestep-5Hz-lm-1.7B"
elif [ "$VRAM_FREE" -ge 12000 ]; then
    TIER="high"; REC_MODEL="acestep-v15-turbo"; REC_LM="acestep-5Hz-lm-1.7B"
elif [ "$VRAM_FREE" -ge 8000 ]; then
    TIER="standard"; REC_MODEL="acestep-v15-turbo"; REC_LM="acestep-5Hz-lm-0.6B"
elif [ "$VRAM_FREE" -ge 4000 ]; then
    TIER="low"; REC_MODEL="acestep-v15-turbo"; REC_LM="none"
else
    TIER="minimal"; REC_MODEL="acestep-v15-turbo"; REC_LM="none"
fi

cat <<EOF
{
  "gpu_detected": true,
  "gpu_name": "$GPU_NAME",
  "driver_version": "$DRIVER",
  "vram_total_mb": $VRAM_TOTAL,
  "vram_free_mb": $VRAM_FREE,
  "vram_used_mb": $VRAM_USED,
  "compute_capability": "$CUDA_CAP",
  "tier": "$TIER",
  "recommended_model": "$REC_MODEL",
  "recommended_lm": "$REC_LM"
}
EOF
