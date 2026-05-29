"""Tests for verify_skill_architecture.py"""

import json
import os
import stat
import sys
from pathlib import Path

import pytest

# Add parent dir to path so we can import the module
sys.path.insert(0, str(Path(__file__).parent.parent))
from verify_skill_architecture import (
    RuleResult,
    check_spawn_directive,
    check_fallback,
    check_frontmatter,
    check_directory_name_consistency,
    check_required_sections,
    check_file_permissions,
    check_no_openai_yaml,
    check_registry_entry,
    validate_skill,
    format_results,
)


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def valid_skill(tmp_path: Path) -> Path:
    """Creates a minimally valid skill directory."""
    skill = tmp_path / "swordy-test-skill"
    skill.mkdir()

    # SKILL.md with required sections, spawn directive, and frontmatter
    md = skill / "SKILL.md"
    md.write_text("""---
description: "Test skill for validation"
when_to_use: "Use when testing validation"
---

# Test Skill

## Agent Routing
Route to sub-agent for execution.

## Parallelization Guidance
Process sequentially.

## Scope
Covers testing.

## Workflow
1. Spawn directive here
2. Fallback logic defined below

### Fallback
If primary fails, use alternative routing.
""")

    # main.py (executable)
    py = skill / "main.py"
    py.write_text("import os\nprint('hello')\n")
    py.chmod(py.stat().st_mode | stat.S_IXUSR)

    return skill


@pytest.fixture
def invalid_spawn_skill(tmp_path: Path) -> Path:
    skill = tmp_path / "swordy-no-spawn"
    skill.mkdir()
    md = skill / "SKILL.md"
    md.write_text("""---
description: "No spawn"
when_to_use: "When testing"
---
# No execution directive
## Scope
Nothing
## Workflow
Done
## Parallelization Guidance
None
## Agent Routing
None
""")
    return skill


@pytest.fixture
def invalid_fallback_skill(tmp_path: Path) -> Path:
    skill = tmp_path / "swordy-no-fallback"
    skill.mkdir()
    md = skill / "SKILL.md"
    md.write_text("""---
description: "No fallback"
when_to_use: "When testing"
---
# No recovery path
## Agent Dispatch
Invoke here
## Scope
Testing
## Workflow
Done
## Parallelization Guidance
None
""")
    return skill


@pytest.fixture
def invalid_frontmatter_skill(tmp_path: Path) -> Path:
    skill = tmp_path / "swordy-bad-fm"
    skill.mkdir()
    md = skill / "SKILL.md"
    md.write_text("""---
description: "Missing when_to_use"
---
# Bad frontmatter
## Agent Routing
Spawn here
## Scope
Test
## Workflow
Done
## Parallelization Guidance
None
""")
    return skill


@pytest.fixture
def invalid_sections_skill(tmp_path: Path) -> Path:
    skill = tmp_path / "swordy-missing-sections"
    skill.mkdir()
    md = skill / "SKILL.md"
    md.write_text("""---
description: "Missing sections"
when_to_use: "When testing"
---
# Missing Sections
## Agent Dispatch
Run
""")
    return skill


@pytest.fixture
def invalid_perms_skill(tmp_path: Path) -> Path:
    skill = tmp_path / "swordy-perms"
    skill.mkdir()
    md = skill / "SKILL.md"
    md.write_text("""---
description: "Perms test"
when_to_use: "When testing"
---
# Perms
## Agent Dispatch
## Scope
## Workflow
## Parallelization Guidance
""")
    py = skill / "script.py"
    py.write_text("print('x')\n")
    py.chmod(0o644)  # not executable
    world_writable = skill / "tmp.txt"
    world_writable.write_text("x")
    world_writable.chmod(0o666)
    return skill


@pytest.fixture
def has_openai_yaml_skill(tmp_path: Path) -> Path:
    skill = tmp_path / "swordy-openai-yaml"
    skill.mkdir()
    (skill / "agents").mkdir()
    (skill / "agents" / "openai.yaml").write_text('interface:\n  display_name: "Bad"\n')
    md = skill / "SKILL.md"
    md.write_text("""---
description: "Has openai yaml"
when_to_use: "When testing"
---
# Has openai yaml
## Agent Routing
Spawn here
## Scope
Test
## Workflow
Done
## Parallelization Guidance
None
""")
    return skill


@pytest.fixture
def no_swordy_prefix_skill(tmp_path: Path) -> Path:
    skill = tmp_path / "bad-prefix"
    skill.mkdir()
    md = skill / "SKILL.md"
    md.write_text("""---
description: "Bad prefix"
when_to_use: "When testing"
---
# Bad prefix
## Agent Routing
Spawn here
## Scope
Test
## Workflow
Done
## Parallelization Guidance
None
""")
    return skill


# ── Tests ─────────────────────────────────────────────────────────────────────

class TestCheckSpawnDirective:
    def test_pass(self, valid_skill):
        r = check_spawn_directive(valid_skill)
        assert r.passed
        assert "Spawn directive" in r.message

    def test_fail(self, invalid_spawn_skill):
        r = check_spawn_directive(invalid_spawn_skill)
        assert not r.passed
        assert "No spawn" in r.message


class TestCheckFallback:
    def test_pass(self, valid_skill):
        r = check_fallback(valid_skill)
        assert r.passed
        assert "Fallback" in r.message

    def test_fail(self, invalid_fallback_skill):
        r = check_fallback(invalid_fallback_skill)
        assert not r.passed
        assert "No fallback" in r.message


class TestCheckFrontmatter:
    def test_pass(self, valid_skill):
        r = check_frontmatter(valid_skill)
        assert r.passed
        assert "description" in r.message.lower()

    def test_fail_missing_when_to_use(self, invalid_frontmatter_skill):
        r = check_frontmatter(invalid_frontmatter_skill)
        assert not r.passed
        assert "when_to_use" in r.message


class TestCheckDirectoryNameConsistency:
    def test_pass_swordy_prefix(self, valid_skill):
        r = check_directory_name_consistency(valid_skill)
        assert r.passed
        assert "swordy-" in r.message

    def test_fail_no_prefix(self, no_swordy_prefix_skill):
        r = check_directory_name_consistency(no_swordy_prefix_skill)
        assert not r.passed
        assert "missing swordy- prefix" in r.message


class TestCheckRequiredSections:
    def test_pass(self, valid_skill):
        r = check_required_sections(valid_skill)
        assert r.passed

    def test_fail(self, invalid_sections_skill):
        r = check_required_sections(invalid_sections_skill)
        assert not r.passed
        assert "Missing sections" in r.message


class TestCheckFilePermissions:
    def test_pass(self, valid_skill):
        r = check_file_permissions(valid_skill)
        assert r.passed

    def test_fail(self, invalid_perms_skill):
        r = check_file_permissions(invalid_perms_skill)
        assert not r.passed
        assert ("Non-executable" in r.message or "World-writable" in r.message)


class TestCheckNoOpenaiYaml:
    def test_pass_no_openai_yaml(self, valid_skill):
        r = check_no_openai_yaml(valid_skill)
        assert r.passed
        assert "correct" in r.message.lower()

    def test_fail_has_openai_yaml(self, has_openai_yaml_skill):
        r = check_no_openai_yaml(has_openai_yaml_skill)
        assert not r.passed
        assert "openai.yaml" in r.message


class TestCheckRegistryEntry:
    def test_pass_has_skill_md(self, valid_skill):
        r = check_registry_entry(valid_skill)
        assert r.passed
        assert "SKILL.md" in r.message

    def test_fail_no_skill_md(self, tmp_path: Path):
        skill = tmp_path / "swordy-orphan"
        skill.mkdir()
        r = check_registry_entry(skill)
        assert not r.passed
        assert "Missing SKILL.md" in r.message


class TestValidateSkill:
    def test_all_pass(self, valid_skill):
        results = validate_skill(valid_skill)
        assert all(r.passed for r in results), [r.message for r in results if not r.passed]
        assert len(results) == 8

    def test_mixed(self, invalid_spawn_skill):
        results = validate_skill(invalid_spawn_skill)
        assert not all(r.passed for r in results)


class TestFormatResults:
    def test_format(self):
        results = [
            RuleResult("r1", True, "ok"),
            RuleResult("r2", False, "fail"),
        ]
        out = format_results(results)
        assert "✅ PASS" in out
        assert "❌ FAIL" in out
        assert "1/2 passed" in out
