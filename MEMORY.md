- [Swordy Skill Invocation Protocol](memory/swordy-skill-invocation.md) — Never skip agent spawning for swordy skills;
  always use the Agent tool as specified in SKILL.md routing
- [Protocol Failure: Boundary Violation](memories/memory-protocol-failure-20260609.md) — Do NOT combine plan and execute in one turn; wait for explicit approval.
- [Python App Packaging](memory/python-app-packaging.md) — Python apps must be packaged with pyproject.toml, src/
  layout, **main**.py, and tests/
- **Always adhere to the latest Claude Code documentation and standard conventions for all commands, skills, and agent
  orchestrations.** This includes following proper file structures, using the correct tool-calling patterns, and
  respecting architectural rules (like the Swordy protocol).
  - **Why:** To ensure all automated and agentic tasks are robust, predictable, and compliant with the system's intended
    design.
  - **How to apply:** Apply this mindset to every task, specifically ensuring that new commands or workflows are built
    following official patterns rather than improvised ones.
