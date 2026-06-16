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
DIR="$(cd "$(dirname "$FILE")" && pwd)"
for d in "$DIR" "${DIR%/*}" "${DIR%/*/*}" "${DIR%/*/*/*}"; do
  if [ -f "$d/.markdownlint.json" ]; then
    CONFIG_FILE="$d/.markdownlint.json"
    break
  fi
done

# Extract line_length from MD013 config (default 120)
PRINT_WIDTH=120
if [ -n "${CONFIG_FILE:-}" ]; then
  PW=$(python3 -c "
import json, sys
try:
    c = json.load(open('$CONFIG_FILE'))
    print(c.get('MD013', {}).get('line_length', 120))
except Exception:
    print(120)
" 2>/dev/null)
  [ -n "$PW" ] && PRINT_WIDTH="$PW"
fi

echo "Config:   ${CONFIG_FILE:-<none>} (MD013 line_length=$PRINT_WIDTH)"

# Step 1: Prettier
echo "Prettier: --print-width=$PRINT_WIDTH"
prettier --write --prose-wrap=always --print-width="$PRINT_WIDTH" "$FILE" 2>&1

# Step 2: Iterative lint + fix
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

  # Single-pass perl: handles MD060, MD040, MD033, MD011, MD024
  perl -pi -e '
    BEGIN {
      our $in_block = 0;
      our %seen_headings;
    }

    # MD060: Remove trailing spaces before | (compact style)
    s/ +\|/ |/g;

    # MD060: Replace padded delimiter rows with simple | --- |
    if (/^\|/) {
      my @cells = split(/\|/, $_);
      my $is_delim = 1;
      for my $c (@cells) {
        my $t = $c;
        $t =~ s/^\s+|\s+$//g;
        if ($t ne "" && $t !~ /^-+$/) { $is_delim = 0; last; }
      }
      if ($is_delim) {
        my @non_empty = grep { my $t = $_; $t =~ s/^\s+|\s+$//g; $t ne "" } @cells;
        my $n = @non_empty;
        my $repl = join(" | ", map { "---" } (1..$n));
        $_ = "| $repl |\n";
      }
    }

    # MD040: Add default language to opening bare code blocks (stateful)
    if (/^```(text)?$/) {
      if (!$in_block) {
        $_ = "```text\n";
        $in_block = 1;
      } else {
        $in_block = 0;
      }
    }

    # MD033: <br> -> <br/>
    s/<br(\/)?>/<br\/>/g;

    # MD011: Add space before [[N]](#anchor) after closing paren
    s/\)\[\[([0-9]+)\]\]\((#[^)]+)\)/) [[\1]](\2)/g;

    # MD024: Fix duplicate headings by appending (2), (3), etc.
    if (/^(#+)\s+(.+)$/ && $seen_headings{$2}++) {
      my $n = $seen_headings{$2};
      $_ = "$1 $2 ($n)\n";
    }
  ' "$FILE"

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
