#!/usr/bin/env python3
"""Fix common markdownlint errors in a file.

Fixes:
  MD060 - Table style (compact pipes, delimiter rows)
  MD033 - Inline HTML (<br> -> <br/>)
  MD011 - Inline link spacing
  MD024 - Duplicate headings

MD040 (code block language) is intentionally NOT auto-fixed — blindly
appending ``text`` changes semantics for non-text code (shell, YAML, etc.).
The user must specify the appropriate language manually.

Usage: fix-markdown-fix.py <file-path>

Atomic write: writes to a temp file first, then os.replace() for safety.
Encoding: explicitly uses UTF-8 for all I/O.
"""

import contextlib
import os
import re
import sys
import tempfile


def fix_md060_compact(line: str) -> str:
    """Remove trailing spaces before | (compact style)."""
    return re.sub(r" +\|", " |", line)


def fix_md060_delimiter(line: str) -> str:
    """Replace padded delimiter rows with simple | --- |."""
    if not line.startswith("|"):
        return line

    cells = line.split("|")
    is_delim = True
    for cell in cells:
        t = cell.strip()
        if t and not re.match(r"^-+$", t):
            is_delim = False
            break

    if is_delim:
        non_empty = [c for c in cells if c.strip()]
        n = len(non_empty)
        line = "| " + " | ".join("---" for _ in range(n)) + " |\n"

    return line


def fix_md033(line: str) -> str:
    """Convert <br> or <br/> to <br/>."""
    return re.sub(r"<br/?>", "<br/>", line)


def fix_md011(line: str) -> str:
    """Add space before [[N]](#anchor) after closing paren."""
    return re.sub(
        r"\)\[\[([0-9]+)\]\]\((#[^)]+)\)",
        r") [[\1]](\2)",
        line,
    )


def fix_md024(line: str, seen_headings: dict[str, int]) -> str:
    """Fix duplicate headings by appending (2), (3), etc.

    The dedup key includes the heading level (e.g. "# Foo") so that
    headings at different levels do not collide.
    """
    m = re.match(r"^(#+)\s+(.+)$", line)
    if not m:
        return line

    heading_level = m.group(1)
    heading_text = m.group(2)
    # Key includes heading level to avoid cross-level collision
    key = f"{heading_level} {heading_text}"
    if key in seen_headings:
        seen_headings[key] += 1
        return f"{heading_level} {heading_text} ({seen_headings[key]})\n"

    seen_headings[key] = 1
    return line


def main():
    if len(sys.argv) != 2:
        print("Usage: fix-markdown-fix.py <file-path>", file=sys.stderr)
        sys.exit(1)

    file_path = sys.argv[1]

    # Read the entire file with explicit UTF-8 encoding
    with open(file_path, encoding="utf-8") as f:
        original_content = f.read()

    # Track whether the file originally ended with a newline
    has_trailing_newline = (
        original_content.endswith("\n") if original_content else False
    )

    # Process lines
    lines = original_content.splitlines(True)  # keep line endings
    seen_headings: dict[str, int] = {}
    fixed_lines: list[str] = []

    for line in lines:
        line = fix_md060_compact(line)
        line = fix_md060_delimiter(line)
        line = fix_md033(line)
        line = fix_md011(line)
        line = fix_md024(line, seen_headings)
        fixed_lines.append(line)

    fixed_content = "".join(fixed_lines)

    # Preserve the original trailing-newline status
    if has_trailing_newline and not fixed_content.endswith("\n"):
        fixed_content += "\n"
    elif not has_trailing_newline and fixed_content.endswith("\n"):
        fixed_content = (
            fixed_content.rstrip("\n") + "\n"
            if fixed_content.rstrip("\n")
            else fixed_content
        )

    # Atomic write: write to temp file, then os.replace()
    dir_name = os.path.dirname(os.path.abspath(file_path))
    fd, tmp_path = tempfile.mkstemp(dir=dir_name, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as tmp_f:
            tmp_f.write(fixed_content)
        os.replace(tmp_path, file_path)
    except Exception:
        # Clean up temp file on failure
        with contextlib.suppress(OSError):
            os.unlink(tmp_path)
        raise


if __name__ == "__main__":
    main()
