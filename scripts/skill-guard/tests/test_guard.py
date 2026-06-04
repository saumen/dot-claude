"""Unit tests for skill_guard.guard."""

import json
import io
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from skill_guard.guard import (
    ACTIVE_SKILL_FILE,
    INLINE_TOOLS,
    check_active_skill,
    decide,
    parse_tool,
    run,
)


class TestParseTool(unittest.TestCase):
    def test_valid_tool_name(self):
        self.assertEqual(parse_tool('{"tool_name": "Bash"}'), "Bash")

    def test_missing_tool_name(self):
        self.assertIsNone(parse_tool('{"other": "field"}'))

    def test_invalid_json_returns_none(self):
        self.assertIsNone(parse_tool("not json"))

    def test_array_json_returns_none(self):
        self.assertIsNone(parse_tool('["Bash"]'))

    def test_string_json_returns_none(self):
        self.assertIsNone(parse_tool('"Bash"'))

    def test_number_json_returns_none(self):
        self.assertIsNone(parse_tool('42'))

    def test_null_json_returns_none(self):
        self.assertIsNone(parse_tool('null'))

    def test_bool_json_returns_none(self):
        self.assertIsNone(parse_tool('true'))


class TestCheckActiveSkill(unittest.TestCase):
    def test_no_file_returns_none(self):
        with mock.patch.object(Path, "is_file", return_value=False):
            self.assertIsNone(check_active_skill())

    def test_empty_file_returns_none(self):
        with mock.patch.object(Path, "is_file", return_value=True):
            with mock.patch.object(Path, "read_text", return_value=""):
                self.assertIsNone(check_active_skill())
            with mock.patch.object(Path, "read_text", return_value="  \n  "):
                self.assertIsNone(check_active_skill())

    def test_existing_file_returns_name(self):
        tmp = tempfile.NamedTemporaryFile(suffix=".skill", delete=False)
        tmp.write(b"my-skill\n")
        tmp.close()
        with mock.patch.object(Path, "is_file", return_value=True):
            with mock.patch.object(Path, "read_text", return_value="my-skill\n"):
                self.assertEqual(check_active_skill(), "my-skill")
        Path(tmp.name).unlink(missing_ok=True)


class TestDecide(unittest.TestCase):
    def test_no_active_skill_pass_through(self):
        self.assertIsNone(decide("Bash", None))

    def test_agent_clears_file_and_passes(self):
        tmp = tempfile.NamedTemporaryFile(suffix=".skill", delete=False)
        tmp.write(b"test-skill")
        tmp.close()
        fake_path = Path(tmp.name)
        with mock.patch("skill_guard.guard.ACTIVE_SKILL_FILE", fake_path):
            result = decide("Agent", "test-skill")
            self.assertIsNone(result)
            self.assertFalse(fake_path.exists())
        fake_path.unlink(missing_ok=True)

    def test_inline_tool_denies(self):
        decision = decide("Bash", "my-skill")
        self.assertIsNotNone(decision)
        self.assertEqual(decision["hookSpecificOutput"]["permissionDecision"], "deny")
        self.assertEqual(decision["hookSpecificOutput"]["hookEventName"], "PreToolUse")
        self.assertIn("my-skill", decision["hookSpecificOutput"]["reason"])

    def test_non_inline_non_agent_passes(self):
        self.assertIsNone(decide("SendMessage", "my-skill"))

    def test_grep_denies(self):
        decision = decide("Grep", "my-skill")
        self.assertIsNotNone(decision)
        self.assertEqual(decision["hookSpecificOutput"]["permissionDecision"], "deny")

    def test_write_denies(self):
        decision = decide("Write", "my-skill")
        self.assertIsNotNone(decision)
        self.assertEqual(decision["hookSpecificOutput"]["permissionDecision"], "deny")

    def test_special_chars_escaped_in_output(self):
        skill_name = 'skill-with-"quotes"\\and\\backslashes'
        decision = decide("Read", skill_name)
        self.assertIsNotNone(decision)
        out = json.dumps(decision)
        # json.dumps handles escaping; the skill name should be safely encoded
        self.assertIn("\\\"", out)
        self.assertIn("\\\\", out)
        # Verify round-trip is safe
        parsed = json.loads(out)
        self.assertIn(skill_name, parsed["hookSpecificOutput"]["reason"])


class TestRun(unittest.TestCase):
    def _run_with_input(self, input_text: str):
        """Helper to capture stdout/stderr and return (exit_code, stdout, stderr)."""
        old_in, old_out, old_err = sys.stdin, sys.stdout, sys.stderr
        sys.stdin = io.StringIO(input_text)
        out_buf = io.StringIO()
        err_buf = io.StringIO()
        sys.stdout, sys.stderr = out_buf, err_buf
        try:
            code = run()
        finally:
            sys.stdin, sys.stdout, sys.stderr = old_in, old_out, old_err
        return code, out_buf.getvalue(), err_buf.getvalue()

    def test_no_active_skill_pass_through(self):
        with mock.patch("skill_guard.guard.check_active_skill", return_value=None):
            code, out, err = self._run_with_input('{"tool_name": "Bash"}')
            self.assertEqual(code, 0)
            self.assertEqual(out, "")

    def test_inline_tool_denies(self):
        with mock.patch("skill_guard.guard.check_active_skill", return_value="test-skill"):
            code, out, err = self._run_with_input('{"tool_name": "Edit"}')
            self.assertEqual(code, 0)
            decision = json.loads(out.strip())
            self.assertEqual(decision["hookEventName"], "PreToolUse")
            self.assertEqual(decision["hookSpecificOutput"]["permissionDecision"], "deny")

    def test_agent_clears_and_passes(self):
        tmp = tempfile.NamedTemporaryFile(suffix=".skill", delete=False)
        tmp.write(b"test-skill")
        tmp.close()
        fake_path = Path(tmp.name)
        with mock.patch("skill_guard.guard.ACTIVE_SKILL_FILE", fake_path):
            with mock.patch("skill_guard.guard.check_active_skill", return_value="test-skill"):
                code, out, err = self._run_with_input('{"tool_name": "Agent"}')
                self.assertEqual(code, 0)
                self.assertEqual(out, "")
                self.assertFalse(fake_path.exists())
        fake_path.unlink(missing_ok=True)

    def test_malformed_json_passes_through(self):
        code, out, err = self._run_with_input("not valid json")
        self.assertEqual(code, 0)
        self.assertEqual(out.strip(), "{}")
        self.assertEqual(err, "")

    def test_non_dict_json_passes_through(self):
        code, out, err = self._run_with_input('["Bash"]')
        self.assertEqual(code, 0)
        self.assertEqual(out.strip(), "{}")
        self.assertEqual(err, "")

    def test_missing_tool_name_passes_through(self):
        code, out, err = self._run_with_input('{"other": "field"}')
        self.assertEqual(code, 0)
        self.assertEqual(out.strip(), "{}")
        self.assertEqual(err, "")


if __name__ == "__main__":
    unittest.main()
