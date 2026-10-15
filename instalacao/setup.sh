#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.."
export PYTHONUTF8=1
if [[ -x .venv/bin/python ]]; then
    exec .venv/bin/python instalacao/install.py "$@"
fi
exec python3 instalacao/install.py "$@"
