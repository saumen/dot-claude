---
description: "Swordy Plan Feature: Plan new features with decomposition and milestone tracking. Plan new features with structured decomposition, API design, data model changes, and milestone tracking. Use when the user wants to add a feature, build a new capability, or extend existing functionality. Do NOT use for refactoring (use refactoring), removing dead code (use code-cleanup), or fixing bugs."
when_to_use: Use when planning a new feature with structured milestones, API design, or data model changes.
---

# Feature Planning Skill

Plans new features with structured decomposition, API design, data model changes, and milestone tracking. This skill **only plans** — implementation requires explicit approval.

## Agent Routing
- **Must be executed by spawning the planner sub-agent using the Agent tool with subagent_type: swordy-agent-planner. Do not execute inline.**
- **Fallback:** If the planner agent fails twice (stream disconnect or other error), write the plan inline using this skill's template. Do not retry the planner.

## Parallelization Guidance
- When multiple features span independent modules, analysis and design can proceed in parallel.
- Plan generation must be sequential since it shares implementation conventions.
## Scope

**Use for:**
- Adding new user-facing features or capabilities
- Designing new APIs, endpoints, or interfaces
- Extending existing functionality with new behavior
- Planning database schema migrations for new data models
- Breaking down complex features into ordered milestones

**Do NOT use for:**
- Restructuring existing code (use refactoring)
- Removing dead/unused code (use code-cleanup)
- Fixing bugs or regressions

## Workflow

### 1. Analyze the codebase
- Understand current architecture, patterns, and conventions
- Identify where new code will integrate (modules, services, routes)
- Map existing data models and how they relate to the feature
- Review existing test structure and coverage for adjacent areas
- Note any constraints: framework limits, API contracts, deployment requirements

### 2. Design the feature
- Define user stories or acceptance criteria
- Sketch API/interface signatures (functions, endpoints, types)
- Plan data model changes (new tables, fields, indexes, migrations)
- Identify dependencies on external services or third-party APIs
- Consider backward compatibility and migration paths

### 3. Present findings to user (checkpoint)
- Show a summary of analysis and design decisions from Steps 1–2
- **Wait for user acknowledgment** before generating any plan file

### 4. Generate a feature plan
- Copy the plan template from this skill's `references/plan_template.md`
- Fill in the template with findings from analysis and design
- Write the plan to `docs/plans/features/{YYYYMMDDHHMM}__{feature-slug}/` in the project repo
- Use the checklist categories from the template:
  - **🛠 Production Code** — implementation steps ordered by dependency
  - **🧪 Unit & Integration Tests** — tests for each component
  - **📝 Documentation** — API docs, README updates, migration guides
  - **🔍 Verification** — end-to-end validation and acceptance criteria

### 5. Await approval
- Present the generated plan to the user
- **Do not implement anything until the user explicitly approves the plan**

### 6. Implement (after approval)
- Follow the ordered steps in the plan, respecting dependencies
- Write tests alongside or before implementation (TDD where applicable)
- Run the full test suite after each milestone
- Update documentation as you go
- Verify all acceptance criteria are met
