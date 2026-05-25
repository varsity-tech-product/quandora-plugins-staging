#!/usr/bin/env bash
set -euo pipefail

MARKETPLACE_SOURCE="${FACTOR_MINING_PLUGIN_SOURCE:-varsity-tech-product/factor-mining-agent-plugins}"
MARKETPLACE_REF="${FACTOR_MINING_PLUGIN_REF:-main}"
MARKETPLACE_NAME="${FACTOR_MINING_PLUGIN_MARKETPLACE:-factor-mining-marketplace}"
PLUGIN_NAME="${FACTOR_MINING_PLUGIN_NAME:-factor-mining}"
START_CODEX="${FACTOR_MINING_START_CODEX:-1}"
CODEX_PROMPT="${FACTOR_MINING_CODEX_PROMPT:-Use the Factor Mining plugin. Set up Factor Mining with my Agent API Key through the secure setup prompt. Do not ask me to paste the key into chat. Then choose an open task, write a valid plugin.py, upload it, wait for the backtest, fetch the default factor card if available, and summarize the result.}"

if ! command -v codex >/dev/null 2>&1; then
  echo "Codex CLI is required. Install or update Codex, then run this script again." >&2
  exit 1
fi

marketplace_configured() {
  codex plugin marketplace list 2>/dev/null | awk 'NR > 1 { print $1 }' | grep -Fxq "${MARKETPLACE_NAME}"
}

plugin_installed() {
  codex plugin list --marketplace "${MARKETPLACE_NAME}" 2>/dev/null \
    | grep -E "^${PLUGIN_NAME}@${MARKETPLACE_NAME}[[:space:]]+installed, enabled" >/dev/null
}

echo "Configuring Codex marketplace: ${MARKETPLACE_NAME}"
if marketplace_configured; then
  echo "Marketplace already configured; refreshing if it is Git-backed."
  codex plugin marketplace upgrade "${MARKETPLACE_NAME}" >/dev/null 2>&1 || true
else
  if [[ -d "${MARKETPLACE_SOURCE}" ]]; then
    codex plugin marketplace add "${MARKETPLACE_SOURCE}"
  else
    codex plugin marketplace add "${MARKETPLACE_SOURCE}" --ref "${MARKETPLACE_REF}"
  fi
fi

echo "Installing Codex plugin: ${PLUGIN_NAME}@${MARKETPLACE_NAME}"
if plugin_installed; then
  echo "Plugin already installed."
else
  codex plugin add "${PLUGIN_NAME}@${MARKETPLACE_NAME}"
fi

if [[ "${START_CODEX}" == "0" ]]; then
  echo "Codex plugin is installed. Start it with:"
  printf 'codex %q\n' "${CODEX_PROMPT}"
  exit 0
fi

echo "Starting Codex. Enter the Factor Mining Agent API Key only when the setup helper prompts securely."
exec codex "${CODEX_PROMPT}"
