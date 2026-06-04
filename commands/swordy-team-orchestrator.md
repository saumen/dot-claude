---
name: swordy-team-orchestrator
description: Runs a multi-agent team-based orchestration to solve an algorithmic challenge using swordy-* skills. Teammates read SKILL.md files for workflow knowledge and execute work directly — they do NOT use the Skill tool (that would create a circular agent spawn loop).
usage: /swordy-team-orchestrator [problem_statement | file_path]
---

# Swordy Team Orchestrator: Team-Based Orchestration

## Objective

Solve an independent, deterministic algorithmic challenge using a coordinated team of agents. The orchestration spawns typed agents that **read** `swordy-*` SKILL.md files for workflow knowledge and execute the work directly using their own tools. They do NOT use the `Skill` tool — doing so would create a circular agent spawn loop (the SKILL.md says "spawn the agent," but the agent is already spawned).

## Agent-to-Skill Mapping

Each phase spawns a **typed agent** that reads the corresponding SKILL.md for workflow knowledge and executes directly. The agent `subagent_type` and the skill name differ:

| Phase | Agent (spawned) | SKILL.md (read for workflow) | Artifact Template |
|-------|----------------|------------------------------|-------------------|
| Explore | `swordy-agent-explorer` | `/Users/swordfish/.claude/skills/swordy-explore/SKILL.md` | `exploration.md` |
| Plan | `swordy-agent-planner` | `/Users/swordfish/.claude/skills/swordy-plan-feature/SKILL.md` | `plan.md` |
| Execute | `swordy-agent-execute` | `/Users/swordfish/.claude/skills/swordy-plan-execute/SKILL.md` | `solution.py` + updated `plan.md` |
| Review | `swordy-agent-reviewer` | `/Users/swordfish/.claude/skills/swordy-review/SKILL.md` | `review.md` |
| Deliver | `swordy-agent-git-commit-message` | `/Users/swordfish/.claude/skills/swordy-git-commit-message/SKILL.md` | commit message (no file) |

## CWD-Independent Handover Protocol

**The benchmark runner does not guarantee a shared CWD between the main session and spawned agents.** Agents may resolve relative paths to a different directory than the Team Lead.

1. **Team Lead passes the absolute workspace directory** (`workspace_dir`) to every spawned agent.
2. **Agents resolve artifact paths** as `{workspace_dir}/docs/{phase}/{timestamp}__{slug}/{artifact_template}`.
3. **Agents return** the absolute file path and `sha256sum` checksum after writing.
4. **Team Lead verifies** the checksum at the returned absolute path before proceeding.

Phase prompt template — always include these two lines:

```
Your workspace directory is /absolute/path/to/the/workspace.
Phase: {phase}. Artifact template: {artifact_template}
```

After writing, the agent must return:

```
Artifact: {artifact_template}
Path: /absolute/path/to/workspace/docs/{phase}/{timestamp}__{slug}/{artifact_template}
Checksum: <sha256sum>
```

**Handoff Map** (artifact feeds the next phase):

| From Phase | Artifact | Resolved Path | To Phase |
|------------|----------|---------------|----------|
| Explore | `exploration.md` | `{workspace_dir}/docs/explorations/{timestamp}__{slug}/exploration.md` | Plan |
| Plan | `plan.md` | `{workspace_dir}/docs/plans/{timestamp}__{slug}/plan.md` | Execute |
| Execute | Solution files + updated plan (all `- [x]`) | (solution-specific paths) | Review |
| Review | `review.md` | `{workspace_dir}/docs/reviews/{timestamp}__{slug}/review.md` | Fix (if failed) or Deliver |
| Fix | Updated solution files | (solution-specific paths) | Review (re-entry) |
| Deliver | Commit message + summary table | (no file) | User |

## Orchestration Protocol (Team of Agents)

### CRITICAL: Sequential Execution (NOT Parallel)

**ALL phases MUST execute sequentially, one at a time. NEVER spawn multiple teammates in parallel.**

- Spawn exactly ONE teammate at a time via the `Agent` tool; wait for completion before spawning the next.
- Verify the handover document from the completed phase before proceeding.
- **Anti-patterns (FORBIDDEN):** Creating all teammates upfront; using `parallel()` or any concurrent mechanism; telling an agent to use the `Skill` tool (circular dependency — the SKILL.md says "spawn the agent," but the agent is already spawned).

### Phase Sequence

```
Explore → Plan → Execute → Review → (Fix if review failed) → Review again → ... → Deliver
```

**Shared prompt template** (use for Explore, Plan, Review phases — replace `{phase}`, `{artifact_template}`, `{skill_path}`, and `{input_doc}`):

```
Your workspace directory is {workspace_dir}.
Phase: {phase}. Artifact template: {artifact_template}

1. Read the SKILL.md at {skill_path} and summarize the workflow in 3 bullet points.
2. {input_doc}
3. Execute the {phase} workflow directly using your own tools — do NOT use the Skill tool or spawn another agent.
4. Produce the {phase} handover document at {workspace_dir}/docs/{phase}/{YYYYMMDDHHMM}__{feature-slug}/{artifact_template}.
5. Return the absolute file path and sha256sum checksum.
```

**Team Lead verification:** Read the handover at the returned absolute path, verify checksum (`sha256sum <path>`), validate meaningful content. **If passes → spawn next phase. If fails → send follow-up with specific feedback (do not proceed).**

**Escalation:** If an agent stalls (outputs the same file path or "let me read" narration without emitting a tool call), send **one** follow-up with specific feedback. If it stalls again, intervene directly — read the file yourself and proceed. Never wait more than 2 follow-up turns per agent.

1. **Phase 1 — Explore** (`subagent_type=swordy-agent-explorer`):
   - `{skill_path}` = `/Users/swordfish/.claude/skills/swordy-explore/SKILL.md`, `{artifact_template}` = `exploration.md`
   - `{input_doc}` = *(none — explore the problem space directly)*
   - Produces: problem understanding, constraints, relevant patterns, approach notes.

2. **Phase 2 — Plan** (`subagent_type=swordy-agent-planner`):
   - `{skill_path}` = `/Users/swordfish/.claude/skills/swordy-plan-feature/SKILL.md`, `{artifact_template}` = `plan.md`
   - `{input_doc}` = "Use the exploration handover document from Phase 1 as your input context."
   - Produces: structured decomposition, milestone checklist (TASK-XX, TEST-XX, VERIFY-XX), acceptance criteria.
   - Team Lead validates the checklist section.

3. **Phase 3 — Execute** (`subagent_type=swordy-agent-execute`):
   - `{skill_path}` = `/Users/swordfish/.claude/skills/swordy-plan-execute/SKILL.md`, `{artifact_template}` = `solution.py`
   - `{input_doc}` = "Execute the plan handover document from Phase 2, following its checklist items sequentially."
   - Produces: solution on disk (code files, test files, updated plan with all `- [x]`).
   - Team Lead verifies solution files exist and plan has all checkboxes completed. If fails → go to Fix.

4. **Phase 4 — Review** (`subagent_type=swordy-agent-reviewer`):
   - `{skill_path}` = `/Users/swordfish/.claude/skills/swordy-review/SKILL.md`, `{artifact_template}` = `review.md`
   - `{input_doc}` = "Audit the solution for correctness, security, performance, and test coverage."
   - Produces: severity-ranked findings, verdict (Success/Fail), remediation guidance.
   - **Success → Deliver. Fail → Fix.**

5. **Phase 5 — Fix** (only if review failed, `subagent_type=swordy-agent-execute`):
   - Use this prompt (no SKILL.md needed):
     ```
     Your workspace directory is {workspace_dir}.

     Address each finding in the review handover document from Phase 4 and re-implement the solution. Execute the fixes directly using your own tools.
     ```
   - After fix, return to Phase 4. Repeat until Success or max iterations (default: 3).

6. **Phase 6 — Deliver** (`subagent_type=swordy-agent-git-commit-message`):
   - `{skill_path}` = `/Users/swordfish/.claude/skills/swordy-git-commit-message/SKILL.md`
   - `{input_doc}` = "Analyze the staged changes and produce a conventional commit message."
   - Team Lead compiles summary table: `| Challenge Name | Generation Time | Verification Status | Review Iterations |`
   - Present commit message and summary; shut down teammates and delete the team.

## Problem Statement

**The problem statement is provided as an argument to this command.**

- If the argument is a string, use it directly.
- If the argument is a file path, `Read` the file and use its content.

**Default Problem Statement (if no argument):** Perform deterministic topological sort on DAG `{"X":["Y","Z"],"Y":["W"],"Z":["W"],"W":[]}` with cycle detection, returning `["X","Z","Y","W"]`.

## Launching Sub-agents

When teammates are spawned, the following environment must be respected. Teammates must use `sonnet`:

```bash
export ANTHROPIC_BASE_URL=http://192.168.4.110:8080
export ANTHROPIC_AUTH_TOKEN=none
export CLAUDE_CODE_ENABLE_GATEWAY_MODEL_DISCOVERY=1
claude --permission-mode auto --model sonnet
```

## Reminders

- Use `sonnet` as model id/name — **never** `opus-4.8`.
- Team Lead monitors `TaskList` and responds to teammate updates immediately.
- **NEVER spawn multiple teammates in a single turn.** Each `Agent` call must be in its own turn.
- The Fix → Review loop continues until Review succeeds or max iterations (3) is reached.
- Always shut down teammates and delete the team after Deliver completes.
- **Agents execute directly; they do NOT invoke skills.** The `subagent_type` already encodes the role. SKILL.md is read for workflow knowledge only.
