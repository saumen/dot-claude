---
description: >
  Swordy Review: Structured code review workflow that produces a severity-ranked
  audit report. Review code changes for correctness, security, performance, and
  test coverage. Use when reviewing pull requests, auditing changes, checking
  performance implications, or assessing test coverage. Triggers on requests like
  "review these changes", "audit this code", "check for security issues", or
  "review this branch".
when_to_use: Use when reviewing code changes for correctness, security, performance, or test coverage.
---

# Reviewer Workflow

Orchestrates a structured code review using the review sub-agent and produces a severity-ranked handover document.

## Workflow

1. Spawn the reviewer using the Agent tool with subagent_type: swordy-agent-reviewer with the review scope (files, directory, branch, or diff).
2. The reviewer audits the code and produces findings.
3. After the reviewer finishes, write the handover document:
   - Copy the template from `references/review_template.md` (sibling directory)
   - Fill in all sections with the reviewer's audit results
   - Write to `docs/reviews/{YYYYMMDDHHMM}__{feature-slug}/review.md` in the project repo

## Agent Routing

- **Must be executed by spawning the reviewer using the Agent tool with subagent_type: swordy-agent-reviewer. Do not review inline.**
- **Fallback:** If the reviewer agent fails twice (stream disconnect or other error), run the review inline using the template structure from `references/review_template.md`. Do not retry the agent.

## Approval Gate

Present the review summary inline first for user validation. Write the full handover to file only after approval.

## Parallelization Guidance

Not Applicable. Code review is a sequential process.

## Scope

Not Applicable. The skill's frontmatter description defines when to use it.
