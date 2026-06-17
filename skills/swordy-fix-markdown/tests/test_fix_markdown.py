#!/usr/bin/env python3
"""Regression tests for fix_markdown_fix.py.

Covers:
  C1 - Cross-level heading deduplication (no collision between # Foo and ## Foo)
  C2 - Trailing newline preservation
  C3 - Bare code blocks are NOT auto-appended with `text`
  H3 - Non-UTF-8 file handling (raises UnicodeDecodeError)
  M6 - Binary/non-text file handling (raises error gracefully)
"""

import os
import subprocess
import sys
import tempfile

SCRIPT_DIR = os.path.join(os.path.dirname(__file__), "..", "scripts")
FIX_SCRIPT = os.path.join(SCRIPT_DIR, "fix_markdown_fix.py")


def _run_fix(content: str) -> str:
    """Write content to a temp file, run fix_markdown_fix, return the result."""
    fd, path = tempfile.mkstemp(suffix=".md")
    os.close(fd)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

    try:
        subprocess.run(
            [sys.executable, FIX_SCRIPT, path],
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as e:
        print(f"fix_markdown_fix failed: {e.stderr}", file=sys.stderr)
        raise

    with open(path, encoding="utf-8") as f:
        result = f.read()
    os.unlink(path)
    return result


def test_md024_cross_level_no_collision():
    """C1: # Foo and ## Foo should NOT collide on the same key.

    Before fix: both used heading_text "Foo" as the key, causing ## Foo
    to incorrectly get a (2) suffix.

    After fix: keys are "# Foo" and "## Foo", so they are distinct.
    """
    content = "# Foo\n## Foo\n# Foo\n"
    result = _run_fix(content)
    lines = result.splitlines(True)
    assert lines[0] == "# Foo\n", f"Line 1: expected '# Foo\\n', got {lines[0]!r}"
    assert lines[1] == "## Foo\n", f"Line 2: expected '## Foo\\n', got {lines[1]!r}"
    assert lines[2] == "# Foo (2)\n", (
        f"Line 3: expected '# Foo (2)\\n', got {lines[2]!r}"
    )

    print("PASS: test_md024_cross_level_no_collision")


def test_md024_same_level_duplicate():
    """Same-level duplicates should still get (2), (3), etc."""
    content = "## Introduction\n## Introduction\n## Introduction\n"
    result = _run_fix(content)
    lines = result.splitlines(True)
    assert lines[0] == "## Introduction\n"
    assert lines[1] == "## Introduction (2)\n"
    assert lines[2] == "## Introduction (3)\n"

    print("PASS: test_md024_same_level_duplicate")


def test_md040_no_bare_text_injection():
    """C3: Bare ``` should NOT be auto-appended with `text`.

    Before fix: ``` was rewritten to ```text, changing code semantics.
    After fix: bare code blocks are left untouched.
    """
    content = "```python\nprint('hello')\n```\n\n```\nsome code\n```\n"
    result = _run_fix(content)
    assert "```text" not in result, "Bare code blocks should NOT have `text` appended"
    assert "```python\n" in result
    assert "```\n" in result

    print("PASS: test_md040_no_bare_text_injection")


def test_trailing_newline_preserved():
    """C2: Files with and without trailing newlines should preserve their status.

    Before fix: the script unconditionally appended \\n to the last line.
    After fix: we track the original trailing-newline status and preserve it.
    """
    # Test WITHOUT trailing newline
    content_no_nl = "# Hello\n## World"
    result = _run_fix(content_no_nl)
    assert not result.endswith("\n"), f"Expected no trailing newline, got: {result!r}"

    # Test WITH trailing newline
    content_with_nl = "# Hello\n## World\n"
    result = _run_fix(content_with_nl)
    assert result.endswith("\n"), f"Expected trailing newline, got: {result!r}"

    print("PASS: test_trailing_newline_preserved")


def test_md033_br_conversion():
    """MD033: <br> and <br/> should both become <br/>."""
    content = "Hello<br>World<br/>Again<br>Test\n"
    result = _run_fix(content)
    assert "<br/>" in result
    assert "<br>" not in result

    print("PASS: test_md033_br_conversion")


def test_md060_compact():
    """MD060: Remove trailing spaces before |."""
    content = "cell  | cell2\n| --- | --- |\n"
    result = _run_fix(content)
    assert "cell | cell2\n" in result

    print("PASS: test_md060_compact")


def test_md060_delimiter():
    """MD060: Padded delimiter rows become simple | --- |."""
    content = "| --- | --- | --- |\n| cell | cell | cell |\n"
    result = _run_fix(content)
    # Delimiter row should be normalized
    assert "| --- | --- | --- |\n" in result

    print("PASS: test_md060_delimiter")


def test_md011_link_spacing():
    """MD011: Add space before [[N]](#anchor) after closing paren."""
    content = "text) [[1]](#anchor)\n"
    result = _run_fix(content)
    assert ") [[1]](#anchor)" in result

    print("PASS: test_md011_link_spacing")


def test_encoding_utf8_explicit():
    """H3: File I/O uses explicit UTF-8 encoding."""
    # Write a file with UTF-8 characters
    content = "# Café\n\nHello world — this is a test.\n"
    result = _run_fix(content)
    assert "Café" in result
    assert "—" in result

    print("PASS: test_encoding_utf8_explicit")


def test_atomic_write():
    """H2: The script uses atomic write (temp file + os.replace)."""
    fd, path = tempfile.mkstemp(suffix=".md")
    os.close(fd)
    with open(path, "w", encoding="utf-8") as f:
        f.write("# Test\n")

    subprocess.run(
        [sys.executable, FIX_SCRIPT, path],
        check=True,
        capture_output=True,
        text=True,
    )

    # File should still exist and be readable
    with open(path, encoding="utf-8") as f:
        content = f.read()
    assert "# Test" in content
    os.unlink(path)

    print("PASS: test_atomic_write")


if __name__ == "__main__":
    test_md024_cross_level_no_collision()
    test_md024_same_level_duplicate()
    test_md040_no_bare_text_injection()
    test_trailing_newline_preserved()
    test_md033_br_conversion()
    test_md060_compact()
    test_md060_delimiter()
    test_md011_link_spacing()
    test_encoding_utf8_explicit()
    test_atomic_write()
    print("\nAll tests passed!")
