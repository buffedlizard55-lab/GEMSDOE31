#!/usr/bin/env bash
# Restore every competition and external-layer input this project needs into data/.
#
# Every file is fetched from a *public GitHub mirror owned by this project* and verified against a
# pinned SHA-256 in registry/data_manifest.json. A hash match proves the bytes match the registered
# mirror; it does NOT authenticate the file to DrivenData. This script never contacts DrivenData,
# never logs in, and never uploads anything.
#
#   bash scripts/download_competition_data.sh            # restore + verify + prepare
#   bash scripts/download_competition_data.sh --verify-only
#
# Requires: git or gh (for the GitHub API) + python3 with `rasterio` and `numpy`.
set -euo pipefail
cd "$(dirname "$0")/.."
PY="${PYTHON:-python3}"

if [[ "${1:-}" == "--verify-only" ]]; then
  "$PY" scripts/prepare_data.py --verify-only
  exit 0
fi

"$PY" scripts/download_competition_data.py --data-dir data
"$PY" scripts/prepare_data.py --verify-only
"$PY" scripts/prepare_shared_cache.py
echo
echo "Inputs restored and verified. Next:"
echo "  python scripts/prepare_shared_cache.py"
echo "  python scripts/verify_tgj31.py --rebuild-surface  # verify the closed negative result; no retuning"
echo "  python scripts/build_submission.py --help"
