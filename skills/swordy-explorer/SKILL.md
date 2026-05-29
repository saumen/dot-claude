---
name: swordy-explorer
description: >
  Swordy Explorer: Structured codebase exploration workflow that produces a
  handover document for planning. Map unfamiliar code, trace execution paths,
  identifying affected modules before changes, or gather architectural context.
  Use when exploring a new codebase, mapping affected files, tracing execution
  paths, or gathering context before planning. Triggers on requests like
  "explore this codebase", "map the affected files", "trace the execution
  path", or "gather context before planning".
when_to_use: Use when exploring unfamiliar codebases, tracing execution paths, or gathering architectural context before planning or making changes.
---

# Explorer Workflow

Orchestrates a structured codebase exploration using the explorer sub-agent and produces a handover document for the planning phase.

## Workflow

1. Spawn the explorer using the Agent tool with subagent_type: swordy-agent-explorer with the exploration scope (directory, feature area, or question).
2. The explorer gathers context and produces findings.
3. After the explorer finishes, write the handover document:
   - Copy the template from `references/exploration_template.md` (sibling directory)
   - Fill in all sections with the explorer's findings
   - Write to `docs/handovers/01-exploration.md` in the project repo

## Agent Routing

- **Must be executed by spawning the explorer using the Agent tool with subagent_type: swordy-agent-explorer. Do not explore inline.**
- **Fallback:** If the explorer agent fails twice (stream disconnect or other error), write the exploration summary inline using the template structure from `references/exploration_template.md`. Do not retry the agent.

## Approval Gate

Present the exploration summary inline first for user validation. Write the full handover to file only after approval.

## Parallelization Guidance

Not Applicable. Code exploration is a sequential process.

## Scope

Not Applicable. The skill's frontmatter description defines when to use it.
