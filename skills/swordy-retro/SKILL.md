---
description: >
  Swordy Retro: Generate retrospective reports from run logs and artifacts.
  Analyze phase gaps, construct timelines, categorize findings, and produce
  a structured retro report. Use after a challenge run to extract lessons
  learned, audit performance, and identify improvements. Triggers on requests
  like "retro on the last run", "analyze that run", "create a retrospective",
  or "what went wrong in run {id}".
when_to_use: Use after a challenge run to generate a retrospective report analyzing phase gaps, agent performance, and lessons learned.
---

# Retro Skill

Generate retrospective reports based on run logs and artifacts, ensuring consistency and architecture compliance.

- **Must be executed by spawning the `swordy-agent-execute` sub-agent.** Do not execute inline.
- **Fallback:** If the `swordy-agent-execute` agent fails twice (stream disconnect or other error), run the workflow inline using this skill's steps. Do not retry the agent.

## Workflow

### 1. Context Identification
- Identify the run ID from the user's request or locate the most recent run in `docs/`.
- Locate relevant logs, handover documents, and artifacts for the run.
- Determine which phases were executed and which agents were spawned.

### 2. Gap Analysis
- Calculate time between handovers using file mtimes and spawn records.
- Identify gaps where agents were idle or waiting (threshold: >5 minutes flagged).
- Sum total productive work time vs. idle/wait time.

### 3. Timeline Construction
- Build an audit log of all events during the run.
- Use timestamps from file mtimes and spawn records.
- Flag events exceeding the 5-minute duration threshold with ⚠️ or 🔴.
- Track agent spawn/shutdown behavior and manual interventions.

### 4. Analysis
- Categorize findings into four sections:
  - **Compliance Audit:** Verify that all phase artifacts (`exploration.md`, `plan.md`, `review.md`, etc.) strictly follow the structure, sections, and tables defined in their respective skill templates. List any omissions or deviations.
  - **What Went Wrong:** Technical issues with the solution or process, root cause, impact, and proposed fixes.
  - **What Went Well:** Things that worked effectively.
  - **What Would Make It Faster:** Actionable improvements for next time.

### 5. Synthesis
- Formulate a single-sentence "Key Insight" capturing the most important lesson.
- Compile summary metrics: phases executed, agents spawned, protocol violations, wall-clock time, wasted time, largest gap.

### 6. Report Generation
- Copy the template from `references/retro_template.md` (sibling directory).
- Fill in all sections with the analysis findings.
- Save the final report to `docs/retros/{YYYYMMDDHHMM}__{challenge-slug}/retro.md` in the project repo.

## Agent Routing

- **Primary agent:** `swordy-agent-execute`
  - **Rationale:** The retro process requires both deep analysis of logs (read-only) and creation of a final report (write). `swordy-agent-execute` provides the necessary `workspace-write` permissions and general-purpose execution capabilities.

## Parallelization Guidance

Not Applicable. Retrospective analysis is a sequential process (Analysis → Synthesis → Writing).

## Scope

- **Use for:** Post-run analysis, performance auditing, and lesson extraction.
- **Do NOT use for:** Real-time monitoring of active runs or active project planning.
