---
name: python-app-packaging
description: "Rule: Python apps must be packaged as proper packages with pyproject.toml, src/ layout, __main__.py entry point, and tests/"
metadata:
  type: feedback
---

**Rule:** When creating Python applications or scripts, package them as proper Python packages — not standalone `.py` files.

**Structure:**
```
<app-name>/
├── pyproject.toml              # Package config (stdlib-only where possible)
├── environment.yml             # Conda env (only if external/non-stdlib deps require it)
├── <wrapper>.sh                # Thin wrapper for non-Python callers
├── src/
│   └── <package_name>/
│       ├── __init__.py         # Package metadata
│       ├── __main__.py         # Entry point — reads stdin, dispatches
│       └── <core>.py           # Core logic modules
└── tests/
    └── test_<module>.py        # Unit tests
```

**Why:** Ensures clean entry points (`python -m`), testable structure, and proper dependency management. Avoids the fragility of standalone scripts with multiple fallback parsers.

**How to apply:**
- Every Python tool or hook that has logic worth testing → use this layout
- Use `pyproject.toml` with stdlib-only deps when possible
- Omit `environment.yml` when the package has zero external dependencies; use `PYTHONPATH` in shell wrappers instead
- Only use `environment.yml` + `conda run -n <env>` when external (non-stdlib) dependencies require it
- Tests live under `tests/`, not inline
