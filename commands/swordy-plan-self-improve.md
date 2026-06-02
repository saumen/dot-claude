# Command: Recursive self-improvise planner

Please execute a recursive plan-and-review cycle to finalize implementation plan.

Follow these strict agentic rules until the cycle breaks:
1. Use skill `swordy-review` to carefully review given implementation planning document.
2. Use checksum on the review file to verify `swordy-review` has stored the review document.
3. If the reviewer finds ANY actionable items or issues use `swordy-plan-feature` or `swordy-skill-manager` to address all issues and update the same planning document.
2. Use checksum on the plan file to verify the plan file has been updated.
4. If the reviewer finds absolutely NO actionable items and gives a 100% sign-off, exit the loop, present the final draft plan, and ask for user approval.

## Store audit events

- For each step, append audit events with timestamp, in Pacific timezone, in `audit.md` file in the planning directory.
- The audit event should include a metadata header (`Skill`, `Agent`, `Md5`, `Lines`), a finding summary line, and bulleted details (critical issues, warnings, test gaps, resolutions).
- Use checksum on the audit file to verify the audit file has been updated.

Example audit file content: 


# Audit Log: <skill-name> Implementation Plan

## Cycle 1

### 2026-06-01 17:00 PT — Review

**Skill:** `swordy-review` · **Agent:** `swordy-reviewer` · **Md5:** `ffb5236f` · **Lines:** 100

**Findings:** 3 critical · 8 warnings · 10 test gaps

**Critical issues**
- API contract mismatch with `<feature-flag>` — downstream consumers expect array, plan documents string
- Global vs per-block clustering contradiction — algorithm describes both approaches without resolution
- Underspecified heuristic — no tie-breaking rule when cluster scores are equal

**Warnings**
- Missing `--dry-run` semantics
- Empty line handling undefined in algorithm
- Tilde-fence support not mentioned in detection
- Error handling spec incomplete (atomic writes, encoding, path resolution)
- `<feature-flag>` structure not documented
- Tab character handling unspecified
- Escaped character rules missing
- TEST-05 overlaps with TEST-03 (redundant)

**Test gaps**
- No exit-code verification (TEST-05b)
- No `--dry-run` output comparison (TEST-11)
- No `--verbose` stdout capture (TEST-12)
- No `<feature-flag>` round-trip test (TEST-13)
- No diff-format validation (TEST-14)

Review written to `docs/reviews/<timestamp>__<skill-name>-skill/review.md`.

### 2026-06-01 17:01 PT — Fix

**Skill:** `swordy-skill-manager` · **Agent:** `swordy-planner` · **Md5:** `5e3c035c` · **Lines:** 224

**Resolutions**
- Documented `<feature-flag>` as intentional API extension (string format preserved)
- Changed "global canonical column cluster" → "per-block clustering"
- Added `--force` flag and tie-breaking heuristic rationale
- Defined `--dry-run` semantics (T08a): `--dry-run` prints diff to stdout, exits 0
- Specified empty line handling: preserved verbatim, never treated as block boundary
- Added tilde-fence support to diagram detection (`~~~` ↔ `````)
- Expanded error handling spec: atomic writes, UTF-8 encoding, path resolution
- Added tab/escaped-char rules: tabs → 4-space expansion, `\"` → `"` in output
- Removed TEST-05 redundancy; added 4 new tests (TEST-05b, TEST-11–TEST-14)

Plan updated to `docs/plans/<timestamp>__<skill-name>-skill/plan.md`. md5: `5e3c035c`. 224 lines.

## Cycle 2

### 2026-06-01 17:02 PT — Re-review

**Skill:** `swordy-review` · **Agent:** `swordy-reviewer` · **Md5:** `4f732670` · **Lines:** 224

**Verdict:** Approved for implementation — 0 critical · 0 warnings

**Cosmetic fixes applied**
- "10 tests" → "14 tests" in acceptance criteria
- TEST-07(b): "does not crash" → "exits clean without modifying the file"
- Added `#!/usr/bin/env python3` shebang mention to T07

Cycle breaks — no remaining actionable items.
