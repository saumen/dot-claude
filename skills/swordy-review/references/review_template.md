# Review Report: [Feature/Area Name]
**Date:** YYYY-MM-DD HH:MM UTC
**Project:** <project-path>
**Branch:** <branch-name>
**Plan Reference:** <path-to-plan-file>

## Scope
[What was reviewed — files, modules, or changes under audit]

## Summary
[Overall assessment in 2-3 sentences]

## Findings by Severity

### Critical (must fix)
| # | File:Line | Issue | Suggested Fix |
|---|-----------|-------|---------------|
| 1 | `src/auth/oauth2.rs:45` | Token not validated on refresh | Add expiry check before using token |

### Warning (should fix)
- [Finding] — [Why it matters] — [Suggestion]

### Info (nice to have)
- [Finding] — [Context]

## Test Coverage Assessment
- [What's covered well]
- [Gaps or missing edge cases]

## Security Notes
- [Auth, injection, credential handling observations]

## Final Verdict
[Approved / Approved with changes / Needs rework]

## Action Items for Author
1. [Specific change required]
2. [Optional improvement]
