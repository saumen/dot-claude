# AGENTS.md — Repository Guidelines

## Documentation & File Purposes

This project uses multiple markdown files, each with a distinct audience and scope. Do not duplicate content across them.

| File | Audience | Scope |
|---|---|---|
| [`README.md`](README.md) | End users | Setup, usage workflow, level system, status line format, feature coverage |
| `AGENTS.md` (this file) | Developers & AI assistants | Project structure, test commands, commit conventions, development guidance |
| [`SKILL.md`](SKILL.md) | AI agents | Skill definition, persona, workflow, agent routing instructions |

**Rule:** If content belongs to a user-facing guide (setup, usage), it goes in README. If it's developer/AI guidance (standards, conventions, structure), it goes here. Planning docs stay in `docs/plans/`.

## Project Structure & Module Organization

```
swordy-kid-math/
├── SKILL.md              # Skill definition — persona, workflow, routing
├── README.md             # Human-oriented usage guide
├── AGENTS.md             # This file — developer/AI guidelines
└── scripts/
    └── test_quiz.py      # Test harness — simulates quiz logic, validates state machine
```

## Build, Test, and Development Commands

| Command | Purpose |
|---|---|
| `python3 scripts/test_quiz.py` | Run the full test harness (10 tests) |
| `python3 -m pytest scripts/test_quiz.py` | Run with pytest (if available) |
| `ruff check scripts/test_quiz.py` | Lint the test harness |

## Commit & Pull Request Guidelines

- Use conventional commit prefixes (`feat:`, `fix:`, `docs:`, `refactor:`, `test:`). Imperative mood, subject line under 72 characters, no trailing period.
- Example: `feat: Add level 5 support`
- PRs should include a clear description, link related issues, and note any environment variable changes.

## Agent-Specific Instructions

### Skill Execution

- This skill runs **inline** in the main conversation. No sub-agent spawn.
- The SKILL.md contains the full workflow — read it before executing.
- If a future agent is created for this skill, update the routing in SKILL.md.

### Test Harness

- `scripts/test_quiz.py` simulates the quiz state machine (GameState dataclass).
- 10 tests cover: status line format, question generation, answer checking, streak tracking, level completion, no-cap counter, score format, ambiguity check, subtraction non-negative, and all-level question production.
- Run after any logic changes in SKILL.md to verify correctness.

### Prompt Development

- The SKILL.md is the primary artifact — it's a prompt template executed by the AI.
- Changes to the workflow, status line format, or level definitions must be reflected in both the prompt and the test harness.
- Variable names in the status line must be distinct (no ambiguous `correct` — use `total_correct`, `streak`, `best_streak`).
