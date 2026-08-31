#!/usr/bin/env sh
set -eu
# Dashboard launcher.
# Args:
#   1) project_root (optional): target project root. Defaults to current working directory.
#   2) dashboard_args... (optional): extra arguments passed to the dashboard entry.
# Behavior:
#   - No args: run against current working directory with default "host" action.
#   - To pass dashboard args while using current directory, call: dashboard.sh . <dashboard_args...>
# Env:
#   - PYTHON_EXE (optional): Python executable path. Default is "python".

if [ $# -eq 0 ]; then
  PROJECT_ROOT="$(pwd)"
else
  PROJECT_ROOT="$1"
  shift || true
fi

PYTHON_EXE="${PYTHON_EXE:-python}"
SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
PYTOOL_REPO="$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)"

if [ ! -d "$PROJECT_ROOT" ]; then
  echo "Project root not found: $PROJECT_ROOT" >&2
  exit 3
fi

if [ $# -eq 0 ]; then
  set -- host
fi

cd "$PROJECT_ROOT"
"$PYTHON_EXE" "$PYTOOL_REPO/dashboard/src/ptd_dashboard/app/main.py" "$@" --project-root "$PROJECT_ROOT"
