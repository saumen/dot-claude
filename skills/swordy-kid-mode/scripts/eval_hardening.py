#!/usr/bin/env python3
"""
swordy-kid-mode — Safety Hardening Test Harness

Loads test_cases.json, sends each attack prompt to the model via the
Claude CLI with SKILL.md as the system prompt, evaluates the response
against pass/fail criteria, and reports results as JSON.

Usage:
    python3 eval_hardening.py                  # run all tests
    python3 eval_hardening.py --cases test_cases.json
    python3 eval_hardening.py --model Qwen3.6-35B-A3B
    python3 eval_hardening.py --dry-run         # print prompts without calling the model
    python3 eval_hardening.py --category persona_override  # run one category only
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_MD = SCRIPT_DIR.parent / "SKILL.md"
DEFAULT_CASES = SCRIPT_DIR / "test_cases.json"

# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------

@dataclass
class TestCase:
    name: str
    category: str
    prompt: str
    expected_pass: bool
    pass_criteria: list[str] = field(default_factory=list)
    fail_criteria: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class TestResult:
    name: str
    category: str
    prompt: str
    response: str
    passed: bool
    expected_pass: bool
    match_pass: list[str]  # pass_criteria that were found (or empty)
    match_fail: list[str]  # fail_criteria that were found (violations)
    error: str | None = None


# ---------------------------------------------------------------------------
# Loaders
# ---------------------------------------------------------------------------

def load_test_cases(path: str | Path) -> list[TestCase]:
    """Load test cases from a JSON file."""
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    cases = []
    for item in raw:
        cases.append(TestCase(**item))
    return cases

def load_skill_prompt(path: str | Path = None) -> str:
    """Read the SKILL.md file and return its content as the system prompt."""
    p = Path(path) if path else SKILL_MD
    if not p.exists():
        print(f"ERROR: SKILL.md not found at {p}", file=sys.stderr)
        sys.exit(1)
    return p.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Model interaction
# ---------------------------------------------------------------------------

def send_to_claude(
    system_prompt: str,
    user_prompt: str,
    model: str = "Qwen3.6-35B-A3B",
    timeout: int = 60,
) -> str:
    """
    Send a single-turn prompt to the model via the Claude CLI and return the
    response text.

    Uses --system-prompt for the system prompt and --print for non-interactive
    output. Falls back gracefully on errors.
    """
    # Build the CLI command
    cmd = [
        "claude",
        "--print",
        "--permission-mode", "bypassPermissions",
        "--model", model,
        "--system-prompt", system_prompt,
    ]

    try:
        result = subprocess.run(
            cmd,
            input=user_prompt,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        output = result.stdout.strip()
        if not output and result.returncode != 0:
            # Try to get the error message
            err = result.stderr.strip()
            if err:
                return f"[CLAUDE_ERROR: {err}]"
            return "[CLAUDE_ERROR: empty output]"
        return output
    except subprocess.TimeoutExpired:
        return "[CLAUDE_ERROR: timeout after {}s]".format(timeout)
    except FileNotFoundError:
        return "[CLAUDE_ERROR: 'claude' CLI not found in PATH]"
    except Exception as exc:
        return f"[CLAUDE_ERROR: {exc}]"


# ---------------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------------

def evaluate_response(response: str, test_case: TestCase) -> TestResult:
    """
    Evaluate a model response against a test case's pass/fail criteria.

    Rules:
    - If pass_criteria is non-empty, ALL must be present in the response.
    - If fail_criteria is non-empty, NONE must be present in the response.
    - A test passes if it meets its pass_criteria (if any) and has no
      fail_criteria violations.
    """
    response_lower = response.lower()

    # Check pass criteria (all must be present if specified)
    match_pass: list[str] = []
    if test_case.pass_criteria:
        for criterion in test_case.pass_criteria:
            if criterion.lower() in response_lower:
                match_pass.append(criterion)

    # Check fail criteria (none should be present)
    match_fail: list[str] = []
    for criterion in test_case.fail_criteria:
        if criterion.lower() in response_lower:
            match_fail.append(criterion)

    # Determine pass/fail
    passed = True
    if test_case.pass_criteria and len(match_pass) != len(test_case.pass_criteria):
        passed = False
    if match_fail:
        passed = False

    return TestResult(
        name=test_case.name,
        category=test_case.category,
        prompt=test_case.prompt,
        response=response,
        passed=passed,
        expected_pass=test_case.expected_pass,
        match_pass=match_pass,
        match_fail=match_fail,
    )


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def format_category_score(category: str, results: list[TestResult]) -> dict[str, Any]:
    """Compute per-category statistics."""
    total = len(results)
    passed = sum(1 for r in results if r.passed)
    return {
        "category": category,
        "total": total,
        "passed": passed,
        "failed": total - passed,
        "pass_rate": round(passed / total * 100, 1) if total else 0.0,
    }


def generate_report(all_results: list[TestResult]) -> dict[str, Any]:
    """Generate the full report dictionary."""
    # Per-category breakdown
    categories: dict[str, list[TestResult]] = {}
    for r in all_results:
        categories.setdefault(r.category, []).append(r)

    category_scores = {}
    for cat, results in sorted(categories.items()):
        category_scores[cat] = format_category_score(cat, results)

    # Overall
    total = len(all_results)
    passed = sum(1 for r in all_results if r.passed)

    # Failed tests with details
    failures = [
        {
            "name": r.name,
            "category": r.category,
            "prompt": r.prompt,
            "expected_pass": r.expected_pass,
            "actual_result": "PASS" if r.passed else "FAIL",
            "fail_criteria_violations": r.match_fail,
            "response_truncated": len(r.response) > 500,
            "response_preview": r.response[:500] + ("..." if len(r.response) > 500 else ""),
        }
        for r in all_results
        if not r.passed
    ]

    report = {
        "total_tests": total,
        "total_passed": passed,
        "total_failed": total - passed,
        "overall_pass_rate": round(passed / total * 100, 1) if total else 0.0,
        "category_scores": category_scores,
        "failures": failures,
        "results": [
            {
                "name": r.name,
                "category": r.category,
                "passed": r.passed,
                "expected_pass": r.expected_pass,
                "fail_criteria_violations": r.match_fail,
                "pass_criteria_matched": r.match_pass,
            }
            for r in all_results
        ],
    }
    return report


def print_report(report: dict[str, Any]) -> None:
    """Print a human-readable report to stdout."""
    print("=" * 70)
    print("  swordy-kid-mode — Safety Hardening Test Results")
    print("=" * 70)
    print()

    total = report["total_tests"]
    passed = report["total_passed"]
    failed = report["total_failed"]
    rate = report["overall_pass_rate"]

    print(f"  Total: {total}  |  Passed: {passed}  |  Failed: {failed}  |  Pass Rate: {rate}%")
    print()

    # Per-category scores
    print("  ── Category Scores ──")
    for cat, score in report["category_scores"].items():
        bar_len = 20
        filled = int(bar_len * score["pass_rate"] / 100)
        bar = "█" * filled + "░" * (bar_len - filled)
        status = "✓" if score["pass_rate"] == 100 else "✗"
        print(f"  {status} {cat:<28} [{bar}] {score['pass_rate']}% ({score['passed']}/{score['total']})")
    print()

    # Failures
    if report["failures"]:
        print("  ── Failures ──")
        for f in report["failures"]:
            print(f"  ✗ {f['name']} ({f['category']})")
            if f["fail_criteria_violations"]:
                print(f"    Violations: {', '.join(f['fail_criteria_violations'])}")
            if f["response_truncated"]:
                print(f"    Response truncated (showing first 500 chars):")
                print(f"    {f['response_preview']}")
            print()
    else:
        print("  ✓ All tests passed!")
        print()

    print("=" * 70)


# ---------------------------------------------------------------------------
# Main runner
# ---------------------------------------------------------------------------

def run_all_tests(
    test_cases: list[TestCase],
    system_prompt: str,
    model: str = "Qwen3.6-35B-A3B",
    dry_run: bool = False,
    delay: float = 0.5,
    category_filter: str | None = None,
) -> list[TestResult]:
    """Run all test cases and return results."""
    results: list[TestResult] = []

    if category_filter:
        test_cases = [c for c in test_cases if c.category == category_filter]

    for i, tc in enumerate(test_cases):
        print(f"  [{i+1}/{len(test_cases)}] {tc.category}: {tc.name} ... ", end="", flush=True)

        if dry_run:
            print(f"DRY-RUN (would send: {tc.prompt[:80]}...)")
            results.append(TestResult(
                name=tc.name,
                category=tc.category,
                prompt=tc.prompt,
                response="[DRY RUN]",
                passed=True,
                expected_pass=tc.expected_pass,
                match_pass=[],
                match_fail=[],
            ))
            continue

        response = send_to_claude(system_prompt, tc.prompt, model=model)
        result = evaluate_response(response, tc)
        results.append(result)

        status = "PASS" if result.passed else "FAIL"
        print(f"{status}")

        if not result.passed:
            if result.match_fail:
                print(f"         Violations: {', '.join(result.match_fail)}")
            if result.error:
                print(f"         Error: {result.error}")

        time.sleep(delay)

    return results


def main() -> int:
    parser = argparse.ArgumentParser(
        description="swordy-kid-mode Safety Hardening Test Harness",
    )
    parser.add_argument(
        "--cases",
        type=str,
        default=str(DEFAULT_CASES),
        help="Path to test_cases.json",
    )
    parser.add_argument(
        "--skill",
        type=str,
        default=str(SKILL_MD),
        help="Path to SKILL.md (system prompt)",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="Qwen3.6-35B-A3B",
        help="Model name to use",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print prompts without calling the model",
    )
    parser.add_argument(
        "--category",
        type=str,
        default=None,
        help="Run only tests in this category",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=0.5,
        help="Delay between requests (seconds)",
    )
    parser.add_argument(
        "--json-only",
        action="store_true",
        help="Output only JSON, no human-readable report",
    )
    args = parser.parse_args()

    # Load test cases
    print(f"Loading test cases from {args.cases} ... ", end="", flush=True)
    test_cases = load_test_cases(args.cases)
    print(f"{len(test_cases)} cases loaded.")

    # Load system prompt
    print(f"Loading SKILL.md from {args.skill} ... ", end="", flush=True)
    system_prompt = load_skill_prompt(args.skill)
    print("OK")

    print()
    if args.dry_run:
        print("=== DRY RUN MODE ===")
        print("No model calls will be made.\n")
    else:
        print(f"Model: {args.model}")
        print(f"Sending {len(test_cases)} test prompts...\n")

    # Run tests
    results = run_all_tests(
        test_cases,
        system_prompt,
        model=args.model,
        dry_run=args.dry_run,
        delay=args.delay,
        category_filter=args.category,
    )

    # Generate and output report
    report = generate_report(results)

    if not args.json_only:
        print_report(report)

    # Always output JSON to a file
    output_path = SCRIPT_DIR / "results.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    if not args.json_only:
        print(f"\n  JSON report written to {output_path}")

    # Exit code: 0 if all pass, 1 if any fail
    return 0 if report["total_failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())