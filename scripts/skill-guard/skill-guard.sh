#!/bin/bash
# Skill Guard Hook — delegates to the Python package in scripts/skill-guard/.
# Package is stdlib-only, so any python3.10+ works.
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
export PYTHONPATH="${SCRIPT_DIR}/src:${PYTHONPATH}"
# Log Python errors to a date-stamped file (kept per-day for visibility).
# The hook must never block Claude Code operation (exit 0 stays), but failures
# must be observable for debugging.
LOG_DIR="$HOME/.claude/scripts/skill-guard"
LOG_FILE="$LOG_DIR/$(date +%F)-error.log"
mkdir -p "$LOG_DIR"
output=$(python3 -m skill_guard 2>>"$LOG_FILE") || exit 0
if [ -n "$output" ]; then
  printf '%s\n' "$output"
fi
exit 0
