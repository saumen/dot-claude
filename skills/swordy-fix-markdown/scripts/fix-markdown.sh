#!/usr/bin/env bash
# fix-markdown.sh - Lint and fix a markdown file until zero errors.
# Usage: fix-markdown.sh <file-path>
#
# Steps:
#   1. Read MD013 line_length from nearest .markdownlint.json (default 120)
#   2. Run prettier --print-width=<line_length> to fix prose wrapping
#   3. Run markdownlint; if errors remain, apply manual fixes and re-lint
#   4. Report summary

set -euo pipefail

FILE="${1:?Usage: fix-markdown.sh <file-path>}"

if [ ! -f "$FILE" ]; then
	echo "ERROR: File not found: $FILE" >&2
	exit 1
fi

# Resolve config - walk up directory tree for .markdownlint.json
CONFIG_FILE=""
d="$(cd "$(dirname "$FILE")" && pwd)"
while [ -n "$d" ] && [ -z "$CONFIG_FILE" ]; do
	if [ -f "$d/.markdownlint.json" ]; then
		CONFIG_FILE="$d/.markdownlint.json"
		break
	fi
	if [ "$d" = "/" ]; then
		break
	fi
	d="${d%/*}"
done

# Extract line_length from MD013 config (default 120)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PRINT_WIDTH=120
if [ -n "${CONFIG_FILE:-}" ]; then
	if command -v jq &>/dev/null; then
		PW=$(jq -r '.MD013.line_length // 120' "$CONFIG_FILE" 2>/dev/null)
		PRINT_WIDTH="${PW:-$PRINT_WIDTH}"
	else
		echo "WARNING: jq not found. Install it to read MD013 config (e.g., brew install jq)." >&2
	fi
fi

echo "Config:   ${CONFIG_FILE:-<none>} (MD013 line_length=$PRINT_WIDTH)"

# Step 1: Prettier
echo "Prettier: --print-width=$PRINT_WIDTH"
prettier --write --prose-wrap=always --print-width="$PRINT_WIDTH" "$FILE" 2>&1

# Step 2: Iterative lint + fix
# Check that markdownlint is available
if ! command -v markdownlint &>/dev/null; then
	echo "ERROR: markdownlint not found. Install it (e.g., npm install -g markdownlint-cli)." >&2
	exit 1
fi

MAX_ITER=5
ITER=0

while true; do
	ERRORS=$(markdownlint "$FILE" 2>&1 || true)
	if [ -z "$ERRORS" ]; then
		break
	fi

	ITER=$((ITER + 1))
	if [ "$ITER" -gt "$MAX_ITER" ]; then
		echo "WARNING: Max iterations ($MAX_ITER) reached. Remaining errors:"
		echo "$ERRORS"
		break
	fi

	echo "Iter $ITER:"
	echo "$ERRORS" | head -5

	# Single-pass python: handles MD060, MD040, MD033, MD011, MD024
	python3 "$SCRIPT_DIR/fix_markdown_fix.py" "$FILE"

	echo "  -> Fixed, re-linting..."
done

# Final result
if [ -z "$ERRORS" ]; then
	echo ""
	echo "Linting complete with zero errors"
	exit 0
else
	echo ""
	echo "Remaining errors after $ITER iterations:"
	echo "$ERRORS"
	exit 1
fi
