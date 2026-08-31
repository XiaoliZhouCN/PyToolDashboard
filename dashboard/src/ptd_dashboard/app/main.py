from __future__ import annotations

import sys
from pathlib import Path

SRC_ROOT = Path(__file__).resolve().parents[2]
if str(SRC_ROOT) not in sys.path:
    # Support direct execution from launcher templates that call this file path.
    sys.path.insert(0, str(SRC_ROOT))


def run() -> int:
    """Run the dashboard CLI from the launcher-compatible file entrypoint."""

    from ptd_dashboard.app.cli import main

    return main()


if __name__ == "__main__":
    raise SystemExit(run())
