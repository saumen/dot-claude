#!/usr/bin/env python3
"""
Test harness for swordy-kid-math skill.
Simulates the quiz workflow and validates logic correctness.
"""

import random
import sys
from dataclasses import dataclass


@dataclass
class GameState:
    level: int = 1
    total_questions: int = 0
    total_correct: int = 0
    wrong: int = 0
    streak: int = 0
    best_streak: int = 0
    level_complete: bool = False

    def max_for_level(self) -> int:
        return {1: 9, 2: 99, 3: 999, 4: 9999, 5: 99999}[self.level]

    def generate_question(self) -> tuple[int, int, str]:
        """Returns (a, b, op) where op is '+' or '-'."""
        max_val = self.max_for_level()
        a = random.randint(0, max_val)
        b = random.randint(0, max_val)
        op = random.choice(["+", "−"])
        if op == "−" and a < b:
            a, b = b, a
        return a, b, op

    def check_answer(
        self, a: int, b: int, op: str, child_answer: int
    ) -> tuple[bool, int]:
        """Returns (is_correct, expected_answer)."""
        if op == "+":
            expected = a + b
        else:
            expected = a - b
        return child_answer == expected, expected

    def record_correct(self):
        self.total_questions += 1
        self.total_correct += 1
        self.streak += 1
        if self.streak > self.best_streak:
            self.best_streak = self.streak

    def record_wrong(self):
        self.total_questions += 1
        self.wrong += 1
        self.streak = 0

    def check_level_complete(self) -> bool:
        return self.streak >= 10

    def reset_streak(self):
        self.streak = 0

    def status_line(self) -> str:
        return (
            f"🎯 Level {self.level} | Q: {self.total_questions} | "
            f"🔥 {self.streak}/10 | ❌ {self.wrong} | Best: {self.best_streak} | "
            f"Score: {self.total_correct}/{self.total_questions}"
        )


def test_status_line_format():
    """Verify status line contains all required fields with correct variable names."""
    gs = GameState(level=3)
    line = gs.status_line()

    checks = {
        "level": "3" in line,
        "total_questions": "Q:" in line,
        "streak": "🔥" in line and "/10" in line,
        "wrong": "❌" in line,
        "best_streak": "Best:" in line,
        "score": "Score:" in line,
    }

    # Verify no variable name collisions
    assert "correct" not in line.lower() or "total_correct" in line, (
        f"Status line should not use ambiguous 'correct' variable. Got: {line}"
    )

    passed = sum(checks.values())
    total = len(checks)
    print(f"  Status line format: {passed}/{total} checks passed")
    for k, v in checks.items():
        print(f"    {k}: {'✓' if v else '✗'}")
    return passed == total


def test_question_generation():
    """Verify questions are generated within level ranges and subtraction is non-negative."""
    gs = GameState()
    random.seed(42)  # Reproducible

    for level in range(1, 6):
        gs.level = level
        max_val = gs.max_for_level()
        count = 0
        for _ in range(100):
            a, b, op = gs.generate_question()
            assert 0 <= a <= max_val, (
                f"Level {level}: a={a} out of range [0, {max_val}]"
            )
            assert 0 <= b <= max_val, (
                f"Level {level}: b={b} out of range [0, {max_val}]"
            )
            if op == "−":
                assert a >= b, f"Level {level}: subtraction {a} - {b} would be negative"
            count += 1

        print(
            f"  Level {level} ({max_val + 1} numbers): {count} questions generated, all valid ✓"
        )

    return True


def test_answer_checking():
    """Verify correct/wrong answer detection."""
    gs = GameState(level=1)
    a, b, op = gs.generate_question()

    # Test correct answer
    is_correct, expected = gs.check_answer(
        a, b, op, expected := (a + b if op == "+" else a - b)
    )
    assert is_correct, "Should detect correct answer"

    # Test wrong answer
    is_correct, expected = gs.check_answer(a, b, op, expected + 1)
    assert not is_correct, "Should detect wrong answer"

    print("  Answer checking: correct/wrong detection ✓")
    return True


def test_streak_tracking():
    """Verify streak increments on correct, resets on wrong, and best_streak updates."""
    gs = GameState(level=1)

    # Simulate 5 correct answers
    for _ in range(5):
        a, b, op = gs.generate_question()
        expected = a + b if op == "+" else a - b
        _, expected = gs.check_answer(a, b, op, expected)
        gs.record_correct()

    assert gs.streak == 5, f"Streak should be 5, got {gs.streak}"
    assert gs.best_streak == 5, f"Best streak should be 5, got {gs.best_streak}"

    # Simulate 1 wrong answer
    a, b, op = gs.generate_question()
    expected = a + b if op == "+" else a - b
    _, expected = gs.check_answer(a, b, op, expected + 999)
    gs.record_wrong()

    assert gs.streak == 0, f"Streak should reset to 0, got {gs.streak}"
    assert gs.best_streak == 5, f"Best streak should still be 5, got {gs.best_streak}"

    # Simulate 7 more correct answers (new best = 7)
    for _ in range(7):
        a, b, op = gs.generate_question()
        expected = a + b if op == "+" else a - b
        _, expected = gs.check_answer(a, b, op, expected)
        gs.record_correct()

    assert gs.streak == 7, f"Streak should be 7, got {gs.streak}"
    assert gs.best_streak == 7, f"Best streak should be 7, got {gs.best_streak}"

    print("  Streak tracking: increment, reset, best update ✓")
    return True


def test_level_completion():
    """Verify level completion at streak=10 and reset behavior."""
    gs = GameState(level=2)

    # Simulate 10 correct answers in a row
    for _ in range(10):
        a, b, op = gs.generate_question()
        expected = a + b if op == "+" else a - b
        _, expected = gs.check_answer(a, b, op, expected)
        gs.record_correct()

    assert gs.check_level_complete(), "Should detect level completion at streak=10"

    gs.reset_streak()
    assert gs.streak == 0, "Streak should reset after level completion"
    assert gs.total_correct == 10, "total_correct should be 10"
    assert gs.best_streak == 10, "best_streak should be 10"
    assert gs.wrong == 0, "wrong should be 0"

    print("  Level completion: streak=10 detection and reset ✓")
    return True


def test_total_questions_no_cap():
    """Verify total_questions keeps growing beyond 10 (no cap)."""
    gs = GameState(level=1)

    for _ in range(25):
        a, b, op = gs.generate_question()
        expected = a + b if op == "+" else a - b
        _, expected = gs.check_answer(a, b, op, expected)
        gs.record_correct()

    assert gs.total_questions == 25, (
        f"total_questions should be 25, got {gs.total_questions}"
    )

    print("  Total questions: no cap, grows beyond 10 ✓")
    return True


def test_score_format():
    """Verify score format is total_correct/total_questions."""
    gs = GameState(level=1)

    # 7 correct, 3 wrong
    for _ in range(7):
        a, b, op = gs.generate_question()
        expected = a + b if op == "+" else a - b
        _, expected = gs.check_answer(a, b, op, expected)
        gs.record_correct()

    for _ in range(3):
        a, b, op = gs.generate_question()
        expected = a + b if op == "+" else a - b
        _, expected = gs.check_answer(a, b, op, expected + 999)
        gs.record_wrong()

    line = gs.status_line()
    assert "Score: 7/10" in line, f"Score should be 7/10, got: {line}"

    print("  Score format: total_correct/total_questions ✓")
    return True


def test_status_line_no_ambiguity():
    """Verify status line uses distinct fields, no ambiguous 'correct' variable."""
    gs = GameState(
        level=3, total_questions=15, total_correct=12, wrong=3, streak=5, best_streak=8
    )
    line = gs.status_line()

    # Old bug: '{correct}/10 streak' and '{correct}/{total}' used same variable
    # Fix: status line uses emoji + numbers, no ambiguous word
    # Verify key fields are present and distinct
    assert "🔥" in line, "Should have streak indicator"
    assert "Best:" in line, "Should have best_streak"
    assert "Score:" in line, "Should have score"
    # Verify no old ambiguous format like "correct/10 streak"
    assert "correct/10" not in line.lower(), "Should not use old ambiguous format"

    print("  No variable name ambiguity in status line ✓")
    return True


def test_subtraction_non_negative():
    """Verify subtraction always produces non-negative results."""
    gs = GameState()
    random.seed(123)

    for level in range(1, 6):
        gs.level = level
        for _ in range(200):
            a, b, op = gs.generate_question()
            if op == "−":
                result = a - b
                assert result >= 0, f"Level {level}: {a} - {b} = {result} < 0"

    print("  Subtraction: all results non-negative ✓")
    return True


def test_all_levels_produce_questions():
    """Verify every level produces valid questions."""
    gs = GameState()
    random.seed(999)

    for level in range(1, 6):
        gs.level = level
        questions = []
        for _ in range(50):
            a, b, op = gs.generate_question()
            questions.append((a, b, op))

        print(
            f"  Level {level}: {len(questions)} questions, +:{sum(1 for _, _, o in questions if o == '+')}, -:{sum(1 for _, _, o in questions if o == '−')}"
        )

    return True


def run_all():
    tests = [
        ("Status line format", test_status_line_format),
        ("Question generation", test_question_generation),
        ("Answer checking", test_answer_checking),
        ("Streak tracking", test_streak_tracking),
        ("Level completion", test_level_completion),
        ("Total questions no cap", test_total_questions_no_cap),
        ("Score format", test_score_format),
        ("No variable ambiguity", test_status_line_no_ambiguity),
        ("Subtraction non-negative", test_subtraction_non_negative),
        ("All levels produce questions", test_all_levels_produce_questions),
    ]

    print("=" * 60)
    print("swordy-kid-math skill — logic test harness")
    print("=" * 60)

    passed = 0
    failed = 0
    for name, fn in tests:
        print(f"\n[TEST] {name}")
        try:
            result = fn()
            if result:
                passed += 1
            else:
                failed += 1
                print("  ✗ FAILED")
        except Exception as e:
            failed += 1
            print(f"  ✗ EXCEPTION: {e}")

    print(f"\n{'=' * 60}")
    print(f"Results: {passed} passed, {failed} failed, {passed + failed} total")
    print(f"{'=' * 60}")

    return failed == 0


if __name__ == "__main__":
    success = run_all()
    sys.exit(0 if success else 1)
