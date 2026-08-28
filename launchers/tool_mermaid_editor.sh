#!/usr/bin/env sh
set -eu
# Tool launcher for Mermaid Editor.
# Args:
#   1) project_root (optional): target project root. Defaults to current working directory.
#   2) tool_args... (optional): extra arguments passed to the tool entry.
# Behavior:
#   - No args: run against current working directory with default "launch" action.
#   - To pass tool args while using current directory, call: tool_mermaid_editor.sh . <tool_args...>
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
  set -- launch
fi

cd "$PROJECT_ROOT"
"$PYTHON_EXE" "$PYTOOL_REPO/tools/mermaid_editor/run.py" "$@" --project-root "$PROJECT_ROOT"
