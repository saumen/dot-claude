"""Core hook logic — parse, check, decide."""

import json
import os
import sys
from pathlib import Path

INLINE_TOOLS = {"Bash", "Read", "Grep", "Edit", "Write"}

HOME = Path.home()
ACTIVE_SKILL_FILE = HOME / ".claude" / ".active-skill"


def parse_tool(input_text: str) -> str | None:
    """Parse JSON from stdin text and extract tool_name.

    Returns None if parsing fails or tool_name is missing.
    """
    data = json.loads(input_text)
    if not isinstance(data, dict):
        raise ValueError("input is not a JSON object")
    return data.get("tool_name")


def check_active_skill() -> str | None:
    """Read the .active-skill file atomically.

    Returns the skill name string, or None if the file does not exist.
    """
    if not ACTIVE_SKILL_FILE.is_file():
        return None
    text = ACTIVE_SKILL_FILE.read_text().strip()
    return text if text else None


def decide(tool_name: str, skill_name: str | None) -> dict | None:
    """Return a deny decision dict, or None to pass through.

    - No active skill → pass through (None)
    - Agent tool with active skill → clear file, pass through (None)
    - Inline tool with active skill → deny dict with reason
    """
    if skill_name is None:
        return None

    if tool_name == "Agent":
        ACTIVE_SKILL_FILE.unlink(missing_ok=True)
        return None

    if tool_name in INLINE_TOOLS:
        return {
            "hookSpecificOutput": {
                "permissionDecision": "deny",
                "reason": (
                    f"swordy skill '{skill_name}' requires agent spawning. "
                    "Do not use inline tools. "
                    "Use Agent tool with the correct subagent_type."
                ),
            }
        }

    return None


def run() -> int:
    """Main entry point. Read stdin, parse, check, decide, output."""
    input_text = sys.stdin.read()

    try:
        tool_name = parse_tool(input_text)
    except (json.JSONDecodeError, ValueError) as exc:
        print(f"skill-guard: malformed JSON input: {exc}", file=sys.stderr)
        return 1

    if tool_name is None:
        print("skill-guard: missing 'tool_name' in input", file=sys.stderr)
        return 1

    skill_name = check_active_skill()
    decision = decide(tool_name, skill_name)

    if decision is not None:
        sys.stdout.write(json.dumps(decision) + "\n")

    return 0
