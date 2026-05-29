#!/usr/bin/env python3
"""verify_skill_architecture.py

Validates Claude Code skill architecture against 8 deterministic rules.

Documentation & References:
- Architecture Rules: references/architecture_rules.md (in swordy-skill-manager)
- Claude Code Skills: https://code.claude.com/docs/en/skills
- Claude Code Sub-agents: https://code.claude.com/docs/en/sub-agents
"""

from __future__ import annotations

import argparse
import json
import os
import re
import stat
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass(frozen=True)
class RuleResult:
    """Result of a single architecture rule check."""
    rule_name: str
    passed: bool
    message: str


def _read_file(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def check_spawn_directive(skill_dir: Path) -> RuleResult:
    """
    Validates that the SKILL.md contains a mandatory spawn directive.
    Rationale: Ensures the skill explicitly delegates to a sub-agent rather than running inline,
    maintaining the separation of concerns between skill (process) and agent (executor).
    See: Architecture Rules Rule 8 (Spawn Directive is Mandatory)
    """
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return RuleResult("check_spawn_directive", False, "SKILL.md not found")
    content = _read_file(skill_md).lower()
    patterns = [
        r"spawn\s*[:\-\s]",
        r"sub\-?\s*agent\s*[:\-\s]",
        r"execute\s*[:\-\s]",
        r"call\s*[:\-\s]",
        r"run\s*[:\-\s]",
    ]
    if any(re.search(p, content) for p in patterns):
        return RuleResult("check_spawn_directive", True, "Spawn directive found")
    return RuleResult("check_spawn_directive", False, "No spawn/sub-agent/execution directive found")


def check_fallback(skill_dir: Path) -> RuleResult:
    """
    Validates that the SKILL.md specifies fallback behavior or routing logic.
    Rationale: Ensures graceful degradation when the spawned agent fails (e.g., stream disconnect),
    preventing infinite retry loops and providing a reliable fallback path.
    """
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return RuleResult("check_fallback", False, "SKILL.md not found")
    content = _read_file(skill_md).lower()
    patterns = [
        r"fallback\s*[:\-\s]",
        r"alternative\s*[:\-\s]",
        r"routing\s*[:\-\s]",
        r"else\s*[:\-\s]",
        r"otherwise\s*[:\-\s]",
        r"if\s+not\s+matched",
        r"default\s+behavior",
    ]
    if any(re.search(p, content) for p in patterns):
        return RuleResult("check_fallback", True, "Fallback/routing logic specified")
    return RuleResult("check_fallback", False, "No fallback or routing logic specified")


def check_frontmatter(skill_dir: Path) -> RuleResult:
    """
    Validates that SKILL.md has YAML frontmatter with 'description' and 'when_to_use' fields.
    Rationale: Ensures every skill has the metadata required for Claude Code skill discovery.
    See: Architecture Rules Rule 4 (Agent-Skill Alignment)
    """
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return RuleResult("check_frontmatter", False, "SKILL.md not found")

    content = _read_file(skill_md)
    fm_match = re.search(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not fm_match:
        return RuleResult("check_frontmatter", False, "No YAML frontmatter found")

    fm_text = fm_match.group(1)
    missing = []
    if not re.search(r"^description\s*:", fm_text, re.MULTILINE):
        missing.append("description")
    if not re.search(r"^when_to_use\s*:", fm_text, re.MULTILINE):
        missing.append("when_to_use")

    if missing:
        return RuleResult("check_frontmatter", False, f"Missing frontmatter fields: {', '.join(missing)}")
    return RuleResult("check_frontmatter", True, "Frontmatter has description and when_to_use")


def check_directory_name_consistency(skill_dir: Path) -> RuleResult:
    """
    Validates that the skill directory name uses the 'swordy-' prefix.
    Rationale: Ensures consistency with the naming convention for swordy skills.
    See: Architecture Rules Rule 4 (Agent-Skill Alignment)
    """
    dir_name = skill_dir.name
    if dir_name.startswith("swordy-"):
        return RuleResult("check_directory_name_consistency", True, f"Directory '{dir_name}' has swordy- prefix")
    return RuleResult("check_directory_name_consistency", False, f"Directory '{dir_name}' missing swordy- prefix")


def check_required_sections(skill_dir: Path) -> RuleResult:
    """
    Validates that the SKILL.md contains all mandatory architectural sections.
    Rationale: Ensures every skill has a defined workflow, agent routing, and scope.
    If a section has no special instructions, it must contain a one-liner:
    "Not Applicable. [Rationale]."

    Required sections (headers):
    1. ## Workflow (canonical header)
    2. ## Agent Routing
    3. ## Parallelization Guidance
    4. ## Scope
    """
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return RuleResult("check_required_sections", False, "SKILL.md not found")

    content = _read_file(skill_md)
    required_sections = [
        "Workflow",
        "Agent Routing",
        "Parallelization Guidance",
        "Scope",
    ]

    missing = []
    for section in required_sections:
        if not re.search(rf"##{{1,3}}\s+{re.escape(section)}", content, re.IGNORECASE):
            missing.append(section)

    if not missing:
        return RuleResult("check_required_sections", True, "All required sections present")
    return RuleResult("check_required_sections", False, f"Missing sections: {', '.join(missing)}")


def check_file_permissions(skill_dir: Path) -> RuleResult:
    """
    Validates file permissions for scripts and core files.
    Rationale: Ensures scripts are executable and core files are readable,
    preventing runtime permission errors.
    """
    issues = []

    for item in skill_dir.rglob("*"):
        if not item.exists():
            continue
        try:
            st = item.stat()
            mode = st.st_mode

            # Check world-writable
            if mode & stat.S_IWOTH:
                issues.append(f"World-writable: {item}")

            # Scripts should be executable
            if item.suffix in (".py", ".sh", ".bash") and item.is_file():
                if not (mode & stat.S_IXUSR):
                    issues.append(f"Non-executable script: {item}")

            # Core files should be readable
            if item.suffix in (".md", ".toml", ".json", ".yaml", ".yml"):
                if not (mode & stat.S_IRUSR):
                    issues.append(f"Unreadable core file: {item}")
        except PermissionError:
            issues.append(f"Cannot stat: {item}")

    if not issues:
        return RuleResult("check_file_permissions", True, "Permissions OK")
    return RuleResult("check_file_permissions", False, "; ".join(issues[:3]))


def check_no_openai_yaml(skill_dir: Path) -> RuleResult:
    """
    Validates that no agents/openai.yaml file exists in the skill directory.
    Rationale: Claude Code skills use SKILL.md frontmatter for metadata,
    not the Codex agents/openai.yaml pattern.
    """
    openai_yaml = skill_dir / "agents" / "openai.yaml"
    if openai_yaml.exists():
        return RuleResult("check_no_openai_yaml", False, "agents/openai.yaml exists (use SKILL.md frontmatter instead)")
    return RuleResult("check_no_openai_yaml", True, "No agents/openai.yaml (correct)")


def check_registry_entry(skill_dir: Path) -> RuleResult:
    """
    Validates that the skill has a valid SKILL.md for auto-discovery.
    Rationale: Ensures the skill is resolvable by Claude Code's skill discovery.
    Claude Code auto-discovers skills from ~/.claude/skills/ directories.
    """
    skill_md = skill_dir / "SKILL.md"
    if skill_md.exists():
        return RuleResult("check_registry_entry", True, "SKILL.md present (valid resolution path)")

    return RuleResult("check_registry_entry", False, "Missing SKILL.md")


# Rule registry
RULES = [
    check_spawn_directive,
    check_fallback,
    check_frontmatter,
    check_directory_name_consistency,
    check_required_sections,
    check_file_permissions,
    check_no_openai_yaml,
    check_registry_entry,
]


def validate_skill(skill_dir: Path) -> list[RuleResult]:
    """Run all architecture checks against a skill directory."""
    results = []
    for rule_fn in RULES:
        try:
            results.append(rule_fn(skill_dir))
        except Exception as e:
            results.append(RuleResult(rule_fn.__name__, False, f"Runtime error: {e}"))
    return results


def format_results(results: list[RuleResult]) -> str:
    lines = []
    passed = 0
    for r in results:
        status = "✅ PASS" if r.passed else "❌ FAIL"
        lines.append(f"[{status}] {r.rule_name}: {r.message}")
        if r.passed:
            passed += 1
    lines.append(f"\nTotal: {passed}/{len(results)} passed")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Validate Claude Code skill architecture")
    parser.add_argument("skill_dir", type=Path, help="Path to skill directory")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    if not args.skill_dir.is_dir():
        print(f"Error: {args.skill_dir} is not a directory", file=sys.stderr)
        sys.exit(1)

    results = validate_skill(args.skill_dir)

    if args.json:
        import json as _json
        print(_json.dumps([{"rule": r.rule_name, "passed": r.passed, "message": r.message} for r in results], indent=2))
    else:
        print(format_results(results))

    sys.exit(0 if all(r.passed for r in results) else 1)


if __name__ == "__main__":
    main()
