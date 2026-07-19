#!/usr/bin/env bash
# One-command boot: install aidentity from this checkout and run the full
# init -> validate -> status -> boot flow against a throwaway demo directory.
#
# Usage:
#   ./bootstrap.sh
set -euo pipefail
cd "$(dirname "$0")"

if ! command -v python3 >/dev/null 2>&1; then
  echo "error: python3 not found. aidentity requires Python 3.10+." >&2
  exit 1
fi

VENV_DIR=".venv-bootstrap"
if [ ! -x "${VENV_DIR}/bin/pip" ]; then
  echo "==> creating ${VENV_DIR}"
  python3 -m venv "${VENV_DIR}"
  "${VENV_DIR}/bin/python" -m ensurepip --upgrade >/dev/null 2>&1 || true
fi

echo "==> installing aidentity (editable)"
"${VENV_DIR}/bin/pip" install -q -e .

DEMO_DIR="$(mktemp -d)"
echo "==> running init -> validate -> status -> boot in ${DEMO_DIR}"
(
  cd "${DEMO_DIR}"
  "${OLDPWD}/${VENV_DIR}/bin/aidentity" init
  echo
  "${OLDPWD}/${VENV_DIR}/bin/aidentity" validate ./identity/
  echo
  "${OLDPWD}/${VENV_DIR}/bin/aidentity" status ./identity/
  echo
  "${OLDPWD}/${VENV_DIR}/bin/aidentity" boot --mode lite ./identity/
)

echo
echo "==> aidentity works. Next: docs/QUICKSTART.md to write your first real iframe."
