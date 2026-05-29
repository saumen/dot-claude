#!/usr/bin/env bash
# verify_all_skills.sh
#
# Runs the architecture validator against all swordy-* skills under ~/.claude/skills.
#
# Usage:
#   ./verify_all_skills.sh          # validate all swordy-* skills
#   ./verify_all_skills.sh <name>   # validate a specific skill (e.g. "git-commit-message")
#
# Exit code: 0 if all checks pass, 1 if any fail.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VALIDATOR="$SCRIPT_DIR/verify_skill_architecture.py"
SKILLS_DIR="$HOME/.claude/skills"

if [[ ! -f "$VALIDATOR" ]]; then
  echo "Error: validator not found at $VALIDATOR" >&2
  exit 1
fi

if [[ ! -d "$SKILLS_DIR" ]]; then
  echo "Error: skills directory not found at $SKILLS_DIR" >&2
  exit 1
fi

# If a specific skill name is given, validate only that one
if [[ $# -ge 1 ]]; then
  TARGET="$SKILLS_DIR/swordy-$1"
  if [[ ! -d "$TARGET" ]]; then
    echo "Error: skill directory not found: $TARGET" >&2
    exit 1
  fi
  python3 "$VALIDATOR" "$TARGET"
  exit $?
fi

# Otherwise, validate all swordy-* skills
ALL_PASS=true
for skill in "$SKILLS_DIR"/swordy-*/; do
  [[ -d "$skill" ]] || continue
  NAME="$(basename "$skill")"
  echo "=== $NAME ==="
  if ! python3 "$VALIDATOR" "$skill"; then
    ALL_PASS=false
    echo "❌ FAILED"
  fi
  echo
done

if $ALL_PASS; then
  echo "All skills passed."
  exit 0
else
  echo "Some skills failed validation." >&2
  exit 1
fi
