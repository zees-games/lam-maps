#!/usr/bin/env bash
# Publishes this pack to the CDN. Not run until the licence question for the credited source map is settled; tools/ and the plans stay out.
#   heavy -- env GS_SITE=https://tmcdev.net tools/publish.sh --version 1.0.0 --token-file ~/.config/dot/creator-token-dev --lock <lock> [--dry-run]
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PUB="${GS_CLOUD_PATH:-$ROOT/../gs-cloud}/tools/publish_pack.sh"
[ -x "$PUB" ] || { echo "publish.sh: gs-cloud not found beside this repository (set GS_CLOUD_PATH)" >&2; exit 1; }
exec "$PUB" --source "$ROOT" --id lam-maps --exclude-dir tools --lock "$ROOT/content.lock.json" "$@"
