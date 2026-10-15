#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
export PYTHONUTF8=1
if [[ ! -x .venv/bin/python ]]; then
    printf '%s\n' 'Ambiente ausente. Execute: bash instalacao/setup.sh' >&2
    exit 1
fi
exec .venv/bin/python run.py "$@"
