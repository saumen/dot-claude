---
description: >
  Swordy Plan Refactor: Plan code restructuring and architectural improvements.
  Plan and execute code restructuring without changing external behavior.
  Use when the user wants to refactor, restructure, extract methods/classes,
  consolidate duplicate code paths, change internal architecture while
  preserving the public API, or improve code organization and naming.
  Do NOT use for adding new features (use a feature plan), removing dead
  code (use code-cleanup), or fixing bugs.
when_to_use: Use when planning code refactoring, restructuring, or architectural improvements. Triggers on requests like "refactor this", "restructure the code", "plan a refactor", "extract methods", or "consolidate duplicate code".
---

# Refactoring Planning Skill

Plans and executes code restructuring in small, verified steps — always preserving external behavior. This skill **only plans** until the user explicitly approves; implementation requires explicit approval.

## Agent Routing
- **Must be executed by spawning the planner sub-agent using the Agent tool with subagent_type: swordy-agent-planner. Do not execute inline.**
- **Fallback:** If the planner agent fails twice (stream disconnect or other error), write the plan inline using this skill's template. Do not retry the planner.

## Parallelization Guidance
- When multiple files have refactoring targets, analysis can proceed in parallel.
- Plan generation must be sequential since it shares conventions.

## Scope

**Use for:**
- Extracting methods, classes, or modules
- Consolidating duplicate code paths
- Changing internal architecture while preserving the public API
- Improving code organization, naming, or readability
- Splitting large files or functions into smaller units

**Do NOT use for:**
- Adding new features (use a feature plan)
- Removing dead/unused code (use code-cleanup)
- Fixing bugs

## Workflow

### 1. Analyze the codebase
- Identify refactoring targets: duplicated logic, large functions/classes, poor naming, tight coupling
- Map dependencies and callers of the code being restructured
- Audit existing test coverage for the affected areas
- **When extracting or moving tests between files:** audit base class and inherited behavior coverage first — skip tests that verify inherited methods already covered by base class mocks. This prevents duplicating tests across multiple files for behavior that is exercised once through a shared parent.
- Identify affected external documentation

### 2. Add guardrail tests (if needed)
- Write tests that capture **current behavior** before any changes
- These are a safety net, not a specification
- If no tests exist at all, add at least one integration test exercising the main code path
- Place guardrail tests in the appropriate test file

### 3. Present findings to user (checkpoint)
- Show a summary of refactoring targets, guardrail test results from Steps 1–2
- **Wait for user acknowledgment** before generating any plan file

### 4. Generate a refactoring plan
- Copy the plan template from this skill's `references/plan_template.md`
- Fill in the template with findings from the analysis
- Write the plan to `docs/refactoring/{YYYYMMDDHHMM}__{feature-slug}/refactor.md` in the project repo
- Use the checklist categories from the template:
  - **🛠 Production Code** — restructuring steps (one logical change at a time)
  - **🧪 Unit & Integration Tests (The Safety Net)** — guardrail tests added before changes
  - **📝 Documentation** — affected docs
  - **🔍 Verification (The Final Check)** — final test runs

### 5. Await approval
- Present the generated plan to the user
- **Do not implement anything until the user explicitly approves the plan**

### 6. Implement (after approval)
- Make one logical change at a time
- Run the full test suite after each step
- If tests fail, either fix the bug or update the test (if behavior was intentionally changed)
- Commit after each successful step (if using version control)
- Confirm all existing tests still pass and guardrail tests confirm unchanged behavior
