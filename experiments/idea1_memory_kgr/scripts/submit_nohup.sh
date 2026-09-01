#!/usr/bin/env bash
set -euo pipefail

STAGE="${1:?Usage: bash scripts/submit_nohup.sh <stage0|stage1|stage2|stage3> [config] [extra args...]}"
CONFIG="${2:-configs/webqsp_pilot.json}"
shift || true
shift || true

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"
mkdir -p logs

case "$STAGE" in
  stage0) SCRIPT="scripts/stage0_inventory.py" ;;
  stage1) SCRIPT="scripts/stage1_build_subgraphs.py" ;;
  stage2) SCRIPT="scripts/stage2_build_memory.py" ;;
  stage3) SCRIPT="scripts/stage3_eval_selector.py" ;;
  stage4) SCRIPT="scripts/stage4_build_pairwise_preferences.py" ;;
  stage5) SCRIPT="scripts/stage5_prepare_action_data.py" ;;
  stage6) SCRIPT="scripts/stage6_train_qwen_action_selector.py" ;;
  *) echo "Unknown stage: $STAGE" >&2; exit 2 ;;
esac

STAMP="$(date +%Y%m%d_%H%M%S)"
LOG_PATH="logs/${STAGE}_${STAMP}.log"
PID_PATH="logs/${STAGE}.latest.pid"

PYTHON_BIN="${PYTHON_BIN:-python3}"

nohup "$PYTHON_BIN" "$SCRIPT" --config "$CONFIG" "$@" > "$LOG_PATH" 2>&1 &
PID="$!"
printf '%s\n' "$PID" > "$PID_PATH"

echo "submitted_stage=$STAGE"
echo "pid=$PID"
echo "log=$ROOT_DIR/$LOG_PATH"
echo "pid_file=$ROOT_DIR/$PID_PATH"
