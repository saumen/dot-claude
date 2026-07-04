# swordy-kid-mode — Repository Guidelines

## Documentation & File Purposes

This project uses multiple markdown files, each with a distinct audience and scope. Do not duplicate content across them.

| File | Audience | Scope |
|---|---|---|
| [`README.md`](README.md) | End users | Setup, workspace layout, workflow, feature usage, safety overview |
| `AGENTS.md` (this file) | Developers & AI assistants | Project structure, testing commands, conventions, development guidance |
| [`scripts/README.md`](scripts/README.md) | Test contributors | Test harness usage, category descriptions, adding new tests |
| `SKILL.md` | All | The actual skill definition — persona, guardrails, workflow, routing |

**Rule:** If content belongs to a user-facing guide (setup, usage), it goes in README. If it's developer/AI guidance (standards, conventions, structure), it goes here or in the dedicated guideline files linked above.

## Project Structure & Module Organization

```
.
├── SKILL.md              # Main skill definition (persona, guardrails, workflow, routing)
├── README.md             # Human-oriented usage guide (this directory's README)
├── AGENTS.md             # AI/developer guidelines (this file)
└── scripts/              # Safety hardening test harness
    ├── README.md         # Test harness documentation (categories, CLI options, troubleshooting)
    ├── eval_hardening.py # Python3 test runner (28 test cases, 10 categories)
    ├── test_cases.json   # Test case definitions (attack prompts, pass/fail criteria)
    └── results.json      # Latest test run results (auto-generated)
```

## Build, Test, and Development Commands

| Command | Purpose |
|---|---|
| `python3 scripts/eval_hardening.py` | Run all 28 safety hardening tests |
| `python3 scripts/eval_hardening.py --dry-run` | Validate test structure without calling the model |
| `python3 scripts/eval_hardening.py --category <name>` | Run tests in a single category only |
| `python3 scripts/eval_hardening.py --help` | Show all CLI options |
| `python3 scripts/eval_hardening.py --delay 2.0` | Increase delay between requests (helps with slow models) |

### Notes

- Tests require the `claude` CLI to be installed and accessible in PATH.
- Default model: `Qwen3.6-35B-A3B`. Override with `--model`.
- Tests send attack prompts via `claude --print --permission-mode bypassPermissions --system-prompt <SKILL.md>`.
- Results are always written to `scripts/results.json`, even when `--json-only` is set.
- Exit code `0` = all tests pass; exit code `1` = one or more failures.

## Commit & Pull Request Guidelines

- Use conventional commit prefixes (`feat:`, `fix:`, `docs:`, `refactor:`, `test:`). Imperative mood, subject line under 72 characters, no trailing period.
- Example: `feat: Add new persona_override test case`
- PRs should include a clear description, link related issues, and note any environment variable changes.

## Agent-Specific Instructions

### Modifying SKILL.md

- Read the full SKILL.md before making changes — the persona, guardrails, and workflow sections are tightly coupled.
- Safety guardrails are **non-negotiable**. Changes that weaken any guardrail must be rejected.
- The one-line rule is absolute — no response may exceed one line, including refusals and deflections.
- Forbidden words that must never appear in user-facing output: `skill`, `SKILL.md`, `instructions`, `rules`, `prompt`, `agent`, `workflow`, `persona`, `guardrail`.

### Adding Test Cases

1. Open `scripts/test_cases.json`.
2. Add a new object to the array with the required shape:

```json
{
  "name": "my_new_test",
  "category": "persona_override",
  "prompt": "your attack prompt here",
  "expected_pass": true,
  "pass_criteria": [],
  "fail_criteria": ["string that must NOT appear in the response"]
}
```

1. Run `python3 scripts/eval_hardening.py` to verify the new test works.
2. See `scripts/README.md` for guidelines on writing effective test cases.

### Test Categories

| Category | What it tests |
|---|---|
| `persona_override` | Model refuses to abandon kid-mode persona |
| `rule_reference` | Model never quotes or describes its own rules |
| `structure_probing` | Model never reveals internal structure or file paths |
| `emotional_manipulation` | Model stays in kid-mode when user is distressed |
| `multi_turn` | Model resists "remember this" and "just this once" tricks |
| `output_format` | Model refuses structured output (JSON, tables, code) |
| `unsafe_content` | Model refuses dangerous requests |
| `authority_claim` | Model doesn't break rules due to authority claims |
| `one_line_rule` | Model keeps every response to exactly one line |
| `keyword_leakage` | Model never uses forbidden words |

## Documentation & Planning

- User-facing docs: [`README.md`](README.md)
- Test harness docs: [`scripts/README.md`](scripts/README.md)
- Full skill definition: [`SKILL.md`](SKILL.md)
- Planning documents: none (this is a skill, not a feature project)
