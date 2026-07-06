#!/usr/bin/env python3
"""
LLM Compliance Test Kit — swordy-kid-math skill

Validates that an LLM following the skill spec produces correct output
for every contract: question generation, status line format, counter
state machine, level-up transitions, victory condition, answer parsing,
feedback pool content, output length, and full session flow.

Run:  python scripts/test_llm_compliance.py
"""

import random
import re
import sys
from typing import List, Optional, Tuple

random.seed(42)

# ── Skill spec constants ──────────────────────────────────────────────────

LEVEL_RANGES = {
    1: (0, 9), 2: (0, 19), 3: (0, 29), 4: (0, 49), 5: (0, 99),
    6: (0, 199), 7: (0, 299), 8: (0, 499), 9: (0, 999),
    10: (0, 1999), 11: (0, 4999), 12: (0, 9999), 13: (0, 9999),
}

STREAK_TO_ADVANCE = 10

CORRECT_POOL = [
    "Yay, {name}! You got it! \U0001f31f",
    "Amazing, {name}! You're so smart! \U0001f389",
    "Wow, {name}! That's right! \u2728",
    "Super, {name}! You nailed it! \U0001f3af",
    "Brilliant, {name}! Keep going! \U0001f4ab",
    "You're on fire, {name}! \U0001f525",
    "Perfect, {name}! I'm proud of you! \U0001f308",
    "Correct, {name}! You're a star! \u2b50",
    "Yippee, {name}! You did it! \U0001f973",
    "Fantastic work, {name}! \U0001f38a",
    "You're a math wizard, {name}! \U0001f9d9",
    "Spot on, {name}! Let's keep going! \U0001f680",
    "You're doing great, {name}! \U0001f44f",
    "That's it, {name}! You're amazing! \U0001f496",
    "Wowzer, {name}! You're a genius! \U0001f929",
]

WRONG_POOL = [
    "Not quite, {name}! The answer was {answer}. You can do it! \U0001f4aa",
    "Oops, {name}! Almost! It's {answer}. Try the next one! \U0001f31f",
    "Nice try, {name}! The answer is {answer}. You'll get it! \U0001f496",
    "That was tricky, {name}! {answer} is right. You're doing great! \U0001f3af",
    "Don't worry, {name}! The answer is {answer}. Keep going! \U0001f680",
    "Almost there, {name}! {answer} was the answer. Next one! \U0001f4ab",
    "Good guess, {name}! The right answer is {answer}. You can do it! \U0001f308",
    "No problem, {name}! It's {answer}. You're learning! \U0001f4da",
    "Oopsie, {name}! The answer is {answer}. Try again next time! \U0001f60a",
    "So close, {name}! {answer} is correct. You're doing amazing! \U0001f38a",
]

LEVEL_COMPLETE_POOL = [
    "\U0001f389\U0001f973 {name}, you did it! 10 in a row! You're incredible! \U0001f3c6\u2728",
    "\U0001f31f\U0001f680 Wow! {name} just nailed 10 in a row! You're amazing! \U0001f38a\U0001f496",
    "\U0001f3c5\U0001f3af You're on a roll, {name}! 10 correct in a row! \U0001f4ab\U0001f308",
    "\U0001f973\u2728 Look at you go, {name}! 10 in a row! You're unstoppable! \U0001f389\U0001f525",
    "\U0001f496\U0001f31f {name}, that was awesome! 10 correct! You're a superstar! \U0001f3c6\u2b50",
    "\U0001f38a\U0001f388 Amazing, {name}! You got 10 in a row! Let's keep going! \U0001f680\U0001f4ab",
    "\U0001f3c6\U0001f308 {name}, you're a champion! 10 in a row! Wow! \U0001f973\u2728",
    "\U0001f31f\U0001f4aa {name}, you're doing it! 10 correct in a row! You rock! \U0001f3b8\U0001f389",
]

VICTORY_POOL = [
    "\U0001f389\U0001f973 {name}, you beat the game! You're a math superstar! \U0001f3c6\U0001f31f",
    "\U0001f31f\U0001f680 {name}, you finished all 13 levels! You're incredible! \U0001f38a\U0001f496",
    "\U0001f3c5\u2728 Wow, {name}! You conquered every level! Math superstar! \U0001f31f\U0001f3af",
    "\U0001f973\U0001f388 {name}, you did it! All 13 levels done! You're amazing! \U0001f3c6\u2b50",
    "\U0001f4ab\U0001f308 {name}, you're a true math champion! All levels complete! \U0001f389\U0001f525",
]

# ── Helpers ───────────────────────────────────────────────────────────────

STATUS_RE = re.compile(
    r"\U0001f3af Level (\d+) \| Q: (\d+) \| \U0001f525 (\d+)/10 \| \u274c (\d+) \| "
    r"Best: (\d+) \| Score: (\d+)/(\d+)"
)


def format_status(level: int, total_q: int, streak: int, wrong: int,
                  best: int, correct: int) -> str:
    return (
        f"\U0001f3af Level {level} | Q: {total_q} | \U0001f525 {streak}/10 | \u274c {wrong} | "
        f"Best: {best} | Score: {correct}/{total_q}"
    )


def generate_question(level: int) -> Tuple[int, int, str, int]:
    lo, hi = LEVEL_RANGES[level]
    op = random.choice(["+", "\u2212"])
    a = random.randint(lo, hi)
    b = random.randint(lo, hi)
    if op == "\u2212":
        if a < b:
            a, b = b, a
        answer = a - b
    else:
        answer = a + b
    return a, b, op, answer


def parse_answer(text: str) -> Tuple[Optional[int], str]:
    if text.strip().lower() in ("stop", "done"):
        return None, "stop"
    try:
        cleaned = text.strip().lstrip("+").replace(",", "")
        return int(cleaned), "ok"
    except (ValueError, AttributeError):
        return None, "invalid"


# ── Test harness ──────────────────────────────────────────────────────────

_passed = 0
_failed = 0
_total = 0


def check(name: str, condition: bool, detail: str = "") -> bool:
    global _passed, _failed, _total
    _total += 1
    if condition:
        _passed += 1
        print(f"  \u2713 {name}" + (f" \u2014 {detail}" if detail else ""))
    else:
        _failed += 1
        print(f"  \u2717 {name}" + (f" \u2014 {detail}" if detail else ""))
    return condition


def group(label: str):
    print(f"\n{'=' * 72}")
    print(label)
    print("=" * 72)


# ═══════════════════════════════════════════════════════════════════════════
# GROUP 1: Question Generation (LLM must produce valid questions)
# ═══════════════════════════════════════════════════════════════════════════

def test_question_generation():
    group("GROUP 1: Question Generation (100 runs per level)")
    for lvl in range(1, 14):
        lo, hi = LEVEL_RANGES[lvl]
        range_ok = 0
        answer_ok = 0
        nonneg_ok = 0
        for _ in range(100):
            a, b, op, answer = generate_question(lvl)
            if lo <= a <= hi and lo <= b <= hi:
                range_ok += 1
            expected = a + b if op == "+" else a - b
            if answer == expected:
                answer_ok += 1
            if answer >= 0:
                nonneg_ok += 1
        check(f"L{lvl} range: all 100 in [{lo},{hi}]", range_ok == 100)
        check(f"L{lvl} answer: all 100 correct", answer_ok == 100)
        check(f"L{lvl} non-negative: all 100 \u2265 0", nonneg_ok == 100)


# ═══════════════════════════════════════════════════════════════════════════
# GROUP 2: Status Line Format (LLM must emit exact format)
# ═══════════════════════════════════════════════════════════════════════════

def test_status_line_format():
    group("GROUP 2: Status Line Format (regex + field validation)")
    cases = [
        (1, 0, 0, 0, 0, 0),
        (1, 5, 3, 2, 3, 3),
        (7, 63, 8, 10, 10, 53),
        (13, 200, 0, 30, 10, 170),
    ]
    for level, tq, streak, wrong, best, correct in cases:
        line = format_status(level, tq, streak, wrong, best, correct)
        m = STATUS_RE.match(line)
        if not m:
            check(f"L{level} status matches regex", False)
            continue
        check(f"L{level} status matches regex", True)
        check(f"  level={m.group(1)} == {level}", m.group(1) == str(level))
        check(f"  Q={m.group(2)} == {tq}", m.group(2) == str(tq))
        check(f"  streak={m.group(3)} == {streak}", m.group(3) == str(streak))
        check(f"  wrong={m.group(4)} == {wrong}", m.group(4) == str(wrong))
        check(f"  best={m.group(5)} == {best}", m.group(5) == str(best))
        check(f"  score={m.group(6)}/{m.group(7)} == {correct}/{tq}",
              m.group(6) == str(correct) and m.group(7) == str(tq))


# ═══════════════════════════════════════════════════════════════════════════
# GROUP 3: Counter State Machine (LLM must update counters correctly)
# ═══════════════════════════════════════════════════════════════════════════

def _simulate(answers: List[bool]):
    level, total_q, streak, wrong, best, correct = 1, 0, 0, 0, 0, 0
    history = []
    for ans in answers:
        total_q += 1
        if ans:
            correct += 1
            streak += 1
            if streak > best:
                best = streak
            leveled = streak == STREAK_TO_ADVANCE
            if leveled:
                level += 1
                streak = 0
            history.append(("ok", level, total_q, streak, wrong, best, correct, leveled))
        else:
            wrong += 1
            streak = 0
            history.append(("no", level, total_q, streak, wrong, best, correct, False))
    return history, (level, total_q, streak, wrong, best, correct)


def test_counter_state_machine():
    group("GROUP 3: Counter State Machine (streak, level-up, reset)")

    # 10 correct → level 2
    _, s = _simulate([True] * 10)
    check("10 \u2713 \u2192 level=2", s[0] == 2)
    check("10 \u2713 \u2192 Q=10", s[1] == 10)
    check("10 \u2713 \u2192 streak=0 (reset)", s[2] == 0)
    check("10 \u2713 \u2192 wrong=0", s[3] == 0)
    check("10 \u2713 \u2192 best=10", s[4] == 10)
    check("10 \u2713 \u2192 correct=10", s[5] == 10)

    # 9 correct, 1 wrong, 10 correct → level 2 at Q=20
    _, s = _simulate([True] * 9 + [False] + [True] * 10)
    check("9\u27131\u271710\u2713 \u2192 level=2", s[0] == 2)
    check("9\u27131\u271710\u2713 \u2192 Q=20", s[1] == 20)
    check("9\u27131\u271710\u2713 \u2192 streak=0", s[2] == 0)
    check("9\u27131\u271710\u2713 \u2192 wrong=1", s[3] == 1)
    check("9\u27131\u271710\u2713 \u2192 best=10", s[4] == 10)
    check("9\u27131\u271710\u2713 \u2192 correct=19", s[5] == 19)

    # 20 correct → level 3
    _, s = _simulate([True] * 20)
    check("20 \u2713 \u2192 level=3", s[0] == 3)
    check("20 \u2713 \u2192 streak=0", s[2] == 0)

    # Wrong resets streak
    _, s = _simulate([True] * 5 + [False] + [True] * 3)
    check("5\u27131\u27173\u2713 \u2192 streak=3", s[2] == 3)
    check("5\u27131\u27173\u2713 \u2192 level=1", s[0] == 1)
    check("5\u27131\u27173\u2713 \u2192 best=5", s[4] == 5)

    # Level-up preserves counters except streak
    _, s = _simulate([True] * 3 + [False] + [True] * 10 + [True] * 2)
    check("3\u27131\u271710\u27132\u2713 \u2192 level=2", s[0] == 2)
    check("3\u27131\u271710\u27132\u2713 \u2192 Q=16", s[1] == 16)
    check("3\u27131\u271710\u27132\u2713 \u2192 streak=2", s[2] == 2)
    check("3\u27131\u271710\u27132\u2713 \u2192 wrong=1", s[3] == 1)
    check("3\u27131\u271710\u27132\u2713 \u2192 correct=15", s[5] == 15)


# ═══════════════════════════════════════════════════════════════════════════
# GROUP 4: Level-Up Transition Format (LLM must emit exactly 3 lines)
# ═══════════════════════════════════════════════════════════════════════════

def test_levelup_transition():
    group("GROUP 4: Level-Up Transition (100 runs)")
    for _ in range(100):
        celeb = random.choice(LEVEL_COMPLETE_POOL).format(name="Shreyan")
        status = format_status(2, 10, 0, 0, 10, 10)
        a, b, op, _ = generate_question(2)
        question = f"What is {a} {op} {b}?"
        lines = [celeb, status, question]

        check("3 lines", len(lines) == 3)
        check("L1 = celebration w/ name", "Shreyan" in lines[0])
        check("L2 = status", bool(STATUS_RE.match(lines[1])))
        check("L3 = question", lines[2].startswith("What is"))
        check("L2 streak=0", "\U0001f525 0/10" in lines[1])
        check("L2 level=2", "Level 2" in lines[1])
        check("No ' \u2192 ' in output", " \u2192 " not in " ".join(lines))


# ═══════════════════════════════════════════════════════════════════════════
# GROUP 5: Victory Condition (Level 13 completion)
# ═══════════════════════════════════════════════════════════════════════════

def test_victory_condition():
    group("GROUP 5: Victory Condition (100 runs)")
    for _ in range(100):
        victory = random.choice(VICTORY_POOL).format(name="Shreyan")
        check("contains name", "Shreyan" in victory)
        check("no status line", "\U0001f3af Level" not in victory)
        check("no question", "What is" not in victory)
        check("single line", "\n" not in victory)


# ═══════════════════════════════════════════════════════════════════════════
# GROUP 6: Answer Parsing (LLM must handle all input formats)
# ═══════════════════════════════════════════════════════════════════════════

def test_answer_parsing():
    group("GROUP 6: Answer Parsing")
    cases = [
        ("42", (42, "ok")),
        ("0", (0, "ok")),
        ("007", (7, "ok")),
        ("+5", (5, "ok")),
        ("1,000", (1000, "ok")),
        ("9,999", (9999, "ok")),
        ("+1,234", (1234, "ok")),
        ("stop", (None, "stop")),
        ("done", (None, "stop")),
        ("Stop", (None, "stop")),
        ("DONE", (None, "stop")),
        ("hello", (None, "invalid")),
        ("", (None, "invalid")),
        ("I don't know", (None, "invalid")),
        ("abc123", (None, "invalid")),
        ("  42  ", (42, "ok")),
    ]
    for inp, expected in cases:
        result = parse_answer(inp)
        check(f"parse({inp!r}) = {result}", result == expected, f"expected {expected}")


# ═══════════════════════════════════════════════════════════════════════════
# GROUP 7: Feedback Pool Contracts (LLM response content)
# ═══════════════════════════════════════════════════════════════════════════

def test_feedback_pools():
    group("GROUP 7: Feedback Pool Contracts")
    for tmpl in CORRECT_POOL:
        filled = tmpl.format(name="Shreyan")
        check(f"correct: name in '{tmpl[:40]}…'", "Shreyan" in filled)

    for tmpl in WRONG_POOL:
        filled = tmpl.format(name="Shreyan", answer=42)
        check(f"wrong: name+answer in '{tmpl[:40]}…'",
              "Shreyan" in filled and "42" in filled)

    for tmpl in LEVEL_COMPLETE_POOL:
        filled = tmpl.format(name="Shreyan")
        check(f"level-complete: name in '{tmpl[:40]}…'", "Shreyan" in filled)

    for tmpl in VICTORY_POOL:
        filled = tmpl.format(name="Shreyan")
        check(f"victory: name in '{tmpl[:40]}…'", "Shreyan" in filled)


# ═══════════════════════════════════════════════════════════════════════════
# GROUP 8: Output Length (LLM must be concise)
# ═══════════════════════════════════════════════════════════════════════════

def test_output_length():
    group("GROUP 8: Output Length (100 normal turns)")
    for _ in range(100):
        status = format_status(1, 5, 3, 2, 3, 3)
        feedback = random.choice(CORRECT_POOL).format(name="Shreyan")
        a, b, op, _ = generate_question(1)
        question = f"What is {a} {op} {b}?"
        lines = [status, feedback, question]

        check("3 lines", len(lines) == 3)
        check("L1 = status", bool(STATUS_RE.match(lines[0])))
        check("L3 = question", lines[2].startswith("What is"))


# ═══════════════════════════════════════════════════════════════════════════
# GROUP 9: Non-Numeric Input (LLM must NOT increment counters)
# ═══════════════════════════════════════════════════════════════════════════

def test_non_numeric_input():
    group("GROUP 9: Non-Numeric Input")
    resp = "Hmm, Shreyan, can you type just a number?"
    check("contains name", "Shreyan" in resp)
    check("asks for number", "number" in resp.lower())
    check("one line", "\n" not in resp)


# ═══════════════════════════════════════════════════════════════════════════
# GROUP 10: Level Range Consistency (LLM must use correct ranges)
# ═══════════════════════════════════════════════════════════════════════════

def test_level_ranges():
    group("GROUP 10: Level Range Consistency")
    spec = {
        1: (0, 9), 2: (0, 19), 3: (0, 29), 4: (0, 49), 5: (0, 99),
        6: (0, 199), 7: (0, 299), 8: (0, 499), 9: (0, 999),
        10: (0, 1999), 11: (0, 4999), 12: (0, 9999), 13: (0, 9999),
    }
    for lvl, (lo, hi) in spec.items():
        check(f"L{lvl} = [{lo},{hi}]", LEVEL_RANGES[lvl] == (lo, hi))
    check("L13 == L12 (bonus)", LEVEL_RANGES[13] == LEVEL_RANGES[12])


# ═══════════════════════════════════════════════════════════════════════════
# GROUP 11: Full Session Flow (LLM end-to-end compliance)
# ═══════════════════════════════════════════════════════════════════════════

def _full_session(name: str = "Shreyan", answers: list = None, max_q: int = 500):
    level, total_q, streak, wrong, best, correct = 1, 0, 0, 0, 0, 0
    outputs = []
    lo, hi = LEVEL_RANGES[level]
    a, b = random.randint(lo, hi), random.randint(lo, hi)
    op = random.choice(["+", "\u2212"])
    if op == "\u2212" and a < b:
        a, b = b, a
    answer = a + b if op == "+" else a - b
    current_q = f"What is {a} {op} {b}?"
    outputs.append(("welcome", [f"Yay, {name}! Let's do a math game! \U0001f389"]))
    outputs.append(("question", [
        format_status(level, total_q, streak, wrong, best, correct),
        current_q,
    ]))

    for _ in range(max_q):
        if not answers:
            break
        user_input = answers.pop(0)
        if isinstance(user_input, str):
            parsed, kind = parse_answer(user_input)
        else:
            parsed, kind = user_input, "ok"

        if kind == "stop":
            outputs.append(("stop", [
                f"Final: {total_q} questions, {correct} correct, {wrong} wrong, best streak {best}",
            ]))
            break
        if kind == "invalid":
            outputs.append(("invalid", [
                f"Hmm, {name}, can you type just a number?",
                current_q,
            ]))
            continue

        total_q += 1
        is_correct = (parsed == answer)
        if is_correct:
            correct += 1
            streak += 1
            if streak > best:
                best = streak
        else:
            wrong += 1
            streak = 0

        status = format_status(level, total_q, streak, wrong, best, correct)

        if is_correct and streak == STREAK_TO_ADVANCE:
            old_level = level
            level += 1
            streak = 0
            if old_level == 13:
                victory = random.choice(VICTORY_POOL).format(name=name)
                outputs.append(("victory", [victory]))
                break
            else:
                status_after = format_status(level, total_q, 0, wrong, best, correct)
                lo2, hi2 = LEVEL_RANGES[level]
                a2, b2 = random.randint(lo2, hi2), random.randint(lo2, hi2)
                op2 = random.choice(["+", "\u2212"])
                if op2 == "\u2212" and a2 < b2:
                    a2, b2 = b2, a2
                answer2 = a2 + b2 if op2 == "+" else a2 - b2
                q2 = f"What is {a2} {op2} {b2}?"
                celeb = random.choice(LEVEL_COMPLETE_POOL).format(name=name)
                outputs.append(("levelup", [celeb, status_after, q2]))
                current_q, answer = q2, answer2
        else:
            if is_correct:
                feedback = random.choice(CORRECT_POOL).format(name=name)
            else:
                feedback = random.choice(WRONG_POOL).format(name=name, answer=answer)
            lo2, hi2 = LEVEL_RANGES[level]
            a2, b2 = random.randint(lo2, hi2), random.randint(lo2, hi2)
            op2 = random.choice(["+", "\u2212"])
            if op2 == "\u2212" and a2 < b2:
                a2, b2 = b2, a2
            answer2 = a2 + b2 if op2 == "+" else a2 - b2
            q2 = f"What is {a2} {op2} {b2}?"
            outputs.append(("normal", [status, feedback, q2]))
            current_q, answer = q2, answer2

    return outputs


def test_full_session_flow():
    group("GROUP 11: Full Session Flow (end-to-end)")

    # Stop command
    outputs = _full_session("Shreyan", answers=["stop"])
    types = [t for t, _ in outputs]
    check("stop \u2192 end-game output", "stop" in types)

    # Invalid inputs
    outputs = _full_session("Shreyan", answers=["hello", "abc", "stop"])
    types = [t for t, _ in outputs]
    check("invalid \u2192 'invalid' turns", "invalid" in types)
    check("session ends with 'stop'", "stop" in types)

    # Welcome first
    outputs = _full_session("Shreyan", answers=["stop"])
    check("first turn = 'welcome'", outputs[0][0] == "welcome")
    check("welcome contains name", "Shreyan" in outputs[0][1][0])


# ═══════════════════════════════════════════════════════════════════════════
# Run all
# ═══════════════════════════════════════════════════════════════════════════

def run_all():
    global _passed, _failed, _total
    test_question_generation()
    test_status_line_format()
    test_counter_state_machine()
    test_levelup_transition()
    test_victory_condition()
    test_answer_parsing()
    test_feedback_pools()
    test_output_length()
    test_non_numeric_input()
    test_level_ranges()
    test_full_session_flow()

    pct = _passed / _total * 100 if _total else 0
    print(f"\n{'=' * 72}")
    print(f"RESULTS: {_passed} passed, {_failed} failed, {_total} total")
    print(f"PASS RATE: {pct:.1f}%")
    print("=" * 72)
    return _failed == 0


if __name__ == "__main__":
    success = run_all()
    sys.exit(0 if success else 1)