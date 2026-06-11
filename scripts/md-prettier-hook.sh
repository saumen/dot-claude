#!/bin/bash
# Auto-format markdown files with Prettier after Write/Edit tools.
# Reads tool input JSON from stdin, extracts file_path, and runs
# prettier --write --prose-wrap=always --print-width=120 on .md files.
# Always exits 0 so it never blocks Claude Code operation.

input=$(cat)
file_path=$(echo "$input" | jq -r '.tool_input.file_path // empty' 2>/dev/null)

# Only process markdown files
[[ "$file_path" == *.md ]] || exit 0

/opt/homebrew/bin/prettier --write --prose-wrap=always --print-width=120 "$file_path" 2>/dev/null
exit 0
