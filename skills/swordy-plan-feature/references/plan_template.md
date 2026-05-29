# Feature Plan: [Feature Name]

## Problem Statement
[Describe the user need or business problem this feature addresses. Who benefits and why?]

## Objective
[Define the clear, measurable goal. What does success look like? List acceptance criteria.]

## Design Overview

### User Stories / Acceptance Criteria
- As a [user], I want to [action] so that [benefit].
- As a [user], I want to [action] so that [benefit].

### API / Interface Changes
```
[New or modified function signatures, endpoints, types, or interfaces]
```

### Data Model Changes
| Table/Collection | Field | Type | Notes |
|---|---|---|---|
| [name] | [field] | [type] | [description] |

**Migration strategy:** [Describe how existing data is handled — backfill, default values, or no migration needed.]

### Dependencies & Integration Points
- **Internal modules affected:** [list modules/services that need changes]
- **External services:** [third-party APIs, databases, message queues]
- **New dependencies to add:** [packages, libraries, tools]

## Implementation Strategy: [Approach Name, e.g., Incremental Rollout]

### Summary of Findings
*   [Key architectural decisions and rationale]
*   [Integration points identified during analysis]

### Milestones (Ordered by Dependency)
1. **[M1]** [Foundation — data models, migrations, core types]
2. **[M2]** [Core logic — business rules, service layer]
3. **[M3]** [Interface — API endpoints, CLI commands, UI components]
4. **[M4]** [Integration — wiring, error handling, logging]

## 📋 Feature Checklist

### 🛠 Production Code (The Core Work)
- [ ] **[TASK-01]** [Data model and migration setup]
- [ ] **[TASK-02]** [Core business logic implementation]
- [ ] **[TASK-03]** [API/interface layer]
- [ ] **[TASK-04]** [Integration with existing modules]

### 🧪 Unit & Integration Tests (The Safety Net)
- [ ] **[TEST-01]** [Unit tests for core logic]
- [ ] **[TEST-02]** [Integration tests for API endpoints]
- [ ] **[TEST-03]** [End-to-end test covering user stories]

### 📝 Documentation (The User Guide)
- [ ] **[DOC-01]** [API documentation or OpenAPI spec update]
- [ ] **[DOC-02]** [README / changelog entry]
- [ ] **[DOC-03]** [Migration guide if schema changes affect users]

### 🔍 Verification (The Final Check)
- [ ] **[VERIFY-01]** [Run full test suite — all existing + new tests pass]
- [ ] **[VERIFY-02]** [Manual smoke test of user stories]
- [ ] **[VERIFY-03]** [Performance check on critical paths]

---
