"""Entry point — reads stdin, dispatches hook logic."""

import sys

from skill_guard.guard import run


def main() -> None:
    sys.exit(run())


if __name__ == "__main__":
    main()
