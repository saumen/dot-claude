# Retro: {challenge_name}

**Run ID:** {YYYYMMDDHHMM}__{slug}
**Date:** {YYYY-MM-DD}
**Model:** {model_id}
**Phase:** Retro
**Scope:** {focus_area}

---

## Phase Gaps (Time Between Handovers)

| From → To | Gap | Indicator | Notes |
|-----------|-----|-----------|-------|
| {phase_A} → {phase_B} | {duration} | ✅/🔴/⚠️ | {details} |

**Total productive work:** {time}
**Total idle/wait time:** {time}
**{phase} output:** {result}

---

## Timeline

Audit log of all events during the run. Timestamps from file mtimes and spawn records. Duration is time since the previous event. Threshold: >5 min = flagged.

| Time | Phase | Actor | Event | Duration | Status |
|------|-------|-------|-------|----------|--------|
| {timestamp} | {phase} | {actor} | {event} | {mm:ss} | ✅/🔴/⚠️ |

**Total wall-clock:** {duration} ({start} → {end})
**Expected:** {expected_duration}
**Wasted:** {wasted_time} ({pct}%)

**Agents spawned:** {count} ({names})
**Agents that self-shutdown:** {count}/{total} (threshold: within 30s of artifact write)
**Manual interventions required:** {count} ({list})

---

## What Went Wrong

### Compliance Audit
| Artifact | Status | Missing/Incorrect Elements |
|-----------|--------|----------------------------|
| `exploration.md` | ✅/❌ | |
| `plan.md` | ✅/❌ | |
| `review.md` | ✅/❌ | |
| `handover.md` | ✅/❌ | |

### {N}. {short_title}

{description of what happened}

**Root cause:** {why it happened}

**Impact:** {what was lost}

**Fix:** {what to do differently}

---

## What Went Well

### {N}. {short_title}

{brief description}

---

## What Would Make It Faster

### {N}. {action_item}

{description of the fix}

---

## Key Insight

{single sentence that captures the most important lesson}

---

## Summary Metrics

| Metric | Value |
|--------|-------|
| Phases executed | {count} ({names}) |
| Agents spawned | {count} |
| Agents that self-shutdown | {count}/{total} |
| Manual shutdowns required | {count} |
| Manual interventions (non-shutdown) | {count} ({list}) |
| Protocol violations | {count} ({list}) |
| Tmux panes leaked | {count} |
| TeamDelete success | Yes/No ({reason}) |
| Wall-clock time | {duration} (should have been {expected}) |
| Time wasted on agent management | {time} ({pct}%) |
| Largest single gap | {duration} ({phase_A} → {phase_B}) |
| {phase} phase output | {result} |
