# Math Quiz for Kids

A kid-friendly math quiz skill — addition and subtraction practice with progressive difficulty levels. Designed for children ages 5–10.

## Setup

No installation required. This is a Claude Code skill — it loads automatically when invoked.

### Shared Memory

This skill shares a memory file with the `swordy-kid-mode` skill at `skills/swordy-kid-mode/memory/child.json`. The file stores the child's name, AI name, gender, birth year, and preferences. Both skills read from this file so the AI can use the child's name and preferences consistently across the quiz and general conversation.

## Usage

Start a quiz session by activating the skill. The AI companion will:

1. Welcome the child and automatically start at Level 1 (no level selection prompt).
2. Present one question at a time with a running status line
3. Give immediate feedback on each answer
4. Track streaks, scores, and best performance
5. Celebrate when a level is mastered (10 correct in a row)
6. Keep going until the child says "stop" or "done"

### Levels

| Level | Number Range | Example |
|---|---|---|
| 1 | 0–9 | What is 3 + 7? |
| 2 | 0–19 | What is 12 − 5? |
| 3 | 0–29 | What is 25 + 4? |
| 4 | 0–49 | What is 37 − 18? |
| 5 | 0–99 | What is 45 − 12? |
| 6 | 0–199 | What is 156 + 37? |
| 7 | 0–299 | What is 283 − 97? |
| 8 | 0–499 | What is 412 + 88? |
| 9 | 0–999 | What is 834 + 166? |
| 10 | 0–1999 | What is 1543 − 210? |
| 11 | 0–4999 | What is 3456 + 1543? |
| 12 | 0–9999 | What is 5432 − 2100? |
| 13 | 0–99999 | What is 67890 − 12345? |

### Status Line

Every turn shows a status line at the top:

```text
🎯 Level 3 | Q: 15 | 🔥 7/10 | ❌ 2 | Best: 9 | Score: 13/15
```

- **Level** — current difficulty
- **Q** — total questions asked
- **🔥** — current streak of correct answers (resets on wrong)
- **❌** — total wrong answers
- **Best** — highest streak ever this session
- **Score** — correct answers / total questions

### Level Completion

When a child answers 10 questions correctly in a row, they master the level and automatically advance to the next one.

### Ending the Quiz

The child says "stop" or "done" to end. A final summary shows total questions, correct, wrong, and best streak.

### What's Included

- Addition and subtraction only
- Non-negative results (no negative answers)
- Progressive difficulty across 13 levels
- Streak-based mastery tracking
- Non-numeric input (e.g., "hello") triggers a friendly re-prompt without penalizing the score
- AI responds in exactly one line per turn (status line displayed separately above)

### What's Not Included

- Multiplication or division
- Fractions, decimals, or algebra
- Adult-level math

---

_Note: This directory is managed by the docs-sync prompt. Manual edits should be handled with care to avoid disrupting system-managed files._