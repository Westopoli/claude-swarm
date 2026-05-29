#!/usr/bin/env bash
# claude-swarm installer
# Copies skills into ~/.claude/skills/ so Claude Code picks them up.
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/Westopoli/claude-swarm/main/install.sh | bash
#
# Or, after cloning the repo:
#   ./install.sh

set -euo pipefail

REPO_URL="https://github.com/Westopoli/claude-swarm"
RAW_BASE="https://raw.githubusercontent.com/Westopoli/claude-swarm/main"
SKILLS_DIR="${HOME}/.claude/skills"
SKILLS=(swarm swarm-shared)

echo "claude-swarm — installing to ${SKILLS_DIR}"
mkdir -p "${SKILLS_DIR}"

# Clean up absorbed skills from prior installs (pre-collapse cascade).
# These were folded into the unified /swarm in v2.
LEGACY=(swarm-spawn swarm-review swarm-post-review swarm-merge)
for legacy in "${LEGACY[@]}"; do
  if [[ -e "${SKILLS_DIR}/${legacy}" ]]; then
    backup="${SKILLS_DIR}/${legacy}.bak.$(date +%Y%m%d%H%M%S)"
    echo "  ${legacy}: legacy install found (absorbed into /swarm); backing up to $(basename "${backup}")"
    mv "${SKILLS_DIR}/${legacy}" "${backup}"
  fi
done

# Determine source: local checkout (if script run from repo) or fresh clone.
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]:-$0}" )" && pwd 2>/dev/null || pwd )"
if [[ -d "${SCRIPT_DIR}/skills" ]]; then
  SRC="${SCRIPT_DIR}/skills"
  echo "  source: local checkout (${SRC})"
else
  TMP="$(mktemp -d)"
  trap 'rm -rf "${TMP}"' EXIT
  echo "  source: cloning ${REPO_URL} to temp dir"
  git clone --depth 1 "${REPO_URL}" "${TMP}/repo" >/dev/null 2>&1
  SRC="${TMP}/repo/skills"
fi

for skill in "${SKILLS[@]}"; do
  dest="${SKILLS_DIR}/${skill}"
  if [[ -e "${dest}" ]]; then
    backup="${dest}.bak.$(date +%Y%m%d%H%M%S)"
    echo "  ${skill}: existing install found, backing up to $(basename "${backup}")"
    mv "${dest}" "${backup}"
  fi
  cp -R "${SRC}/${skill}" "${dest}"
  echo "  ${skill}: installed"
done

echo ""
echo "Done. Restart Claude Code, then try:"
echo "  /swarm"
