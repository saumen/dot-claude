#!/usr/bin/env python3
"""Unit tests for fix-markdown-fix.py."""

import os
import sys
import tempfile
import unittest

# Ensure the script module is importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fix_markdown_fix import (
    fix_md011,
    fix_md024,
    fix_md033,
    fix_md060_compact,
    fix_md060_delimiter,
    main,
)


class TestFixMD060Compact(unittest.TestCase):
    """Tests for MD060 compact table style fix."""

    def test_removes_trailing_spaces_before_pipe(self):
        # Regex removes spaces immediately before pipe only
        self.assertEqual(fix_md060_compact("|  data  |"), "|  data |")

    def test_no_change_when_no_trailing_spaces(self):
        self.assertEqual(fix_md060_compact("| data |"), "| data |")

    def test_handles_multiple_trailing_spaces(self):
        # Regex removes spaces immediately before pipe only
        self.assertEqual(fix_md060_compact("|     data     |"), "|     data |")

    def test_empty_cell(self):
        self.assertEqual(fix_md060_compact("|      |"), "| |")

    def test_leading_pipe_preserved(self):
        self.assertEqual(fix_md060_compact("| a |"), "| a |")

    def test_no_pipe(self):
        self.assertEqual(fix_md060_compact("no pipe here"), "no pipe here")


class TestFixMD060Delimiter(unittest.TestCase):
    """Tests for MD060 delimiter row fix."""

    def test_delimiter_unchanged(self):
        self.assertEqual(
            fix_md060_delimiter("| --- | --- | --- |\n"), "| --- | --- | --- |\n"
        )

    def test_delimiter_two_columns(self):
        self.assertEqual(fix_md060_delimiter("| --- | --- |\n"), "| --- | --- |\n")

    def test_no_change_for_data_row(self):
        self.assertEqual(fix_md060_delimiter("| data | more |\n"), "| data | more |\n")

    def test_no_change_for_non_pipe_line(self):
        self.assertEqual(fix_md060_delimiter("not a pipe line\n"), "not a pipe line\n")

    def test_single_column_delimiter(self):
        self.assertEqual(fix_md060_delimiter("| --- |\n"), "| --- |\n")


class TestFixMD033(unittest.TestCase):
    """Tests for MD033 inline HTML fix."""

    def test_fixes_br(self):
        self.assertEqual(fix_md033("text <br> more"), "text <br/> more")

    def test_fixes_br_slash(self):
        self.assertEqual(fix_md033("text <br/> more"), "text <br/> more")

    def test_no_change_for_other_html(self):
        self.assertEqual(fix_md033("<div>hello</div>"), "<div>hello</div>")

    def test_multiple_br(self):
        self.assertEqual(fix_md033("<br><br>"), "<br/><br/>")

    def test_no_change_for_non_br(self):
        self.assertEqual(fix_md033("<bracket>"), "<bracket>")


class TestFixMD011(unittest.TestCase):
    """Tests for MD011 inline link spacing fix."""

    def test_no_citation_marker_unchanged(self):
        self.assertEqual(fix_md011("text [[1]](#anchor)"), "text [[1]](#anchor)")

    def test_multiple_citations_unchanged(self):
        result = fix_md011("text [[1]](#a) and [[2]](#b)")
        self.assertEqual(result, "text [[1]](#a) and [[2]](#b)")

    def test_paren_without_citation_unchanged(self):
        self.assertEqual(fix_md011("text (not a citation)"), "text (not a citation)")


class TestFixMD024(unittest.TestCase):
    """Tests for MD024 duplicate heading fix."""

    def test_first_heading_unchanged(self):
        seen = {}
        result = fix_md024("## Heading\n", seen)
        self.assertEqual(result, "## Heading\n")
        self.assertEqual(seen, {"## Heading": 1})

    def test_second_duplicate_gets_suffix(self):
        seen = {"## Heading": 1}
        result = fix_md024("## Heading\n", seen)
        self.assertEqual(result, "## Heading (2)\n")
        self.assertEqual(seen, {"## Heading": 2})

    def test_third_duplicate_gets_suffix(self):
        seen = {"## Heading": 2}
        result = fix_md024("## Heading\n", seen)
        self.assertEqual(result, "## Heading (3)\n")
        self.assertEqual(seen, {"## Heading": 3})

    def test_different_headings_no_suffix(self):
        seen = {"## Heading A": 1}
        result = fix_md024("## Heading B\n", seen)
        self.assertEqual(result, "## Heading B\n")
        self.assertEqual(seen, {"## Heading A": 1, "## Heading B": 1})

    def test_h1_duplicate(self):
        seen = {"# Title": 1}
        result = fix_md024("# Title\n", seen)
        self.assertEqual(result, "# Title (2)\n")

    def test_non_heading_unchanged(self):
        seen = {}
        result = fix_md024("not a heading\n", seen)
        self.assertEqual(result, "not a heading\n")
        self.assertEqual(seen, {})

    def test_heading_with_numbers(self):
        seen = {"## Heading 1": 1}
        result = fix_md024("## Heading 1\n", seen)
        self.assertEqual(result, "## Heading 1 (2)\n")


class TestMain(unittest.TestCase):
    """Tests for the main() function."""

    def test_no_args_exits_with_error(self):
        original_argv = sys.argv
        try:
            sys.argv = ["fix-markdown-fix.py"]
            with self.assertRaises(SystemExit) as ctx:
                main()
            self.assertEqual(ctx.exception.code, 1)
        finally:
            sys.argv = original_argv

    def test_too_many_args_exits_with_error(self):
        original_argv = sys.argv
        try:
            sys.argv = ["fix-markdown-fix.py", "arg1", "arg2"]
            with self.assertRaises(SystemExit) as ctx:
                main()
            self.assertEqual(ctx.exception.code, 1)
        finally:
            sys.argv = original_argv

    def test_fixes_file_in_place(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("# Hello\n# Hello\n")
            temp_path = f.name

        try:
            sys.argv = ["fix-markdown-fix.py", temp_path]
            main()

            with open(temp_path) as f:
                content = f.read()
            self.assertIn("(2)", content)
            self.assertNotIn("# Hello\n# Hello\n", content)
        finally:
            os.unlink(temp_path)

    def test_fixes_multiple_rules(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("# Dup\n# Dup\n```code\n```\n")
            temp_path = f.name

        try:
            sys.argv = ["fix-markdown-fix.py", temp_path]
            main()

            with open(temp_path) as f:
                content = f.read()
            self.assertIn("(2)", content)
            # MD040 is a no-op — bare code blocks are NOT auto-appended
            self.assertIn("```code\n", content)
        finally:
            os.unlink(temp_path)


if __name__ == "__main__":
    unittest.main()
