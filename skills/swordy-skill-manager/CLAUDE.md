# Swordy Skill Manager — Navigation & Documentation

## Official Claude Code Documentation

Always fetch the latest content from these URLs when creating or updating skills:

- [Skills](https://code.claude.com/docs/en/skills)
  - Fetch before: creating new skills, updating existing skills, validating metadata
- [Sub-agents](https://code.claude.com/docs/en/sub-agents)
  - Fetch before: creating agent files, updating agent configurations, understanding subagent architecture
- [Agents overview](https://code.claude.com/docs/en/agents)
  - Fetch before: designing agent-skill pairings, choosing between subagent approaches

> **Rule:** Always fetch the latest content from the URLs above before creating or updating skills.
> Do not rely on cached or bundled documentation — the live URL is authoritative.

## References Directory

| File | Purpose |
|------|---------|
| [architecture_rules.md](references/architecture_rules.md) | Full architecture rules with embedded examples for agents and skills |

## Python Scripts and Tests Organization

### Directory Layout

Production scripts and their tests live under `scripts/`:

```
skills/<name>/
├── scripts/
│   ├── <tool>.py              # production script
│   ├── <tool>.sh              # shell scripts (if any)
│   └── tests/
│       └── test_<tool>.py     # unit tests, colocated with source
└── references/
```

**Rules:**
- Tests live directly under `scripts/tests/`, not at the skill root. This keeps the test one directory level from its source, making imports natural (`from ..<tool> import ...`) and avoiding fragile parent-path hacks.
- Do **not** create a `tests/` directory at the skill root — it only adds noise and forces awkward `parent.parent` import paths.
- Every `scripts/<tool>.py` that contains testable logic should have a corresponding `scripts/tests/test_<tool>.py`.

### Running the Validator

The architecture validator (`scripts/verify_skill_architecture.py`) uses only Python stdlib. No dependencies needed.

```bash
# Python 3.11+
python3 ~/.claude/skills/swordy-skill-manager/scripts/verify_skill_architecture.py ~/.claude/skills/<skill-name>
```

> **Rule:** Always run `python3 ~/.claude/skills/swordy-skill-manager/scripts/verify_skill_architecture.py ~/.claude/skills/<skill-name>` after adding or updating any `swordy-*` skill. All architecture checks must pass.

### Running Tests

```bash
# Conda (recommended — reproducible environment)
conda env create -f ~/.claude/skills/swordy-skill-manager/environment.yml
conda activate skill-validator
pytest ~/.claude/skills/swordy-skill-manager/scripts/tests/

# Or pip
pip install pytest
pytest ~/.claude/skills/swordy-skill-manager/scripts/tests/
```

> **Rule:** Always run `pytest ~/.claude/skills/swordy-skill-manager/scripts/tests/` after adding or updating any Python scripts in this skill. All tests must pass before considering the change complete.

### Batch Validation

To validate **all** `swordy-*` skills at once:

```bash
# Via shell script
~/.claude/skills/swordy-skill-manager/scripts/verify_all_skills.sh

# Via Makefile
cd ~/.claude/skills/swordy-skill-manager && make verify
```

To validate a **single** skill by name:

```bash
# Via shell script
~/.claude/skills/swordy-skill-manager/scripts/verify_all_skills.sh plan-feature

# Via Makefile
cd ~/.claude/skills/swordy-skill-manager && make verify NAME=plan-feature
```

### Makefile Targets

| Target | Description |
|--------|-------------|
| `make verify` | Validate all `swordy-*` skills |
| `make verify NAME=<skill>` | Validate a specific skill |
| `make test` | Run unit tests |
| `make all` | Run verify + test |

### Dependencies

| Package | Used by | Notes |
|---------|---------|-------|
| `pytest` | Tests | Test runner only |
