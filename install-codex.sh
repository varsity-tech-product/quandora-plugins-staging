#!/usr/bin/env bash
set -euo pipefail

MARKETPLACE_SOURCE="${FACTOR_MINING_PLUGIN_SOURCE:-varsity-tech-product/factor-mining-agent-plugins}"
MARKETPLACE_REF="${FACTOR_MINING_PLUGIN_REF:-main}"
MARKETPLACE_NAME="${FACTOR_MINING_PLUGIN_MARKETPLACE:-factor-mining-marketplace}"
PLUGIN_NAME="${FACTOR_MINING_PLUGIN_NAME:-factor-mining}"
START_MODE="${FACTOR_MINING_START_MODE:-cli}"
INSTALL_ONLY="0"
WORKSPACE_PATH="${FACTOR_MINING_WORKSPACE:-.}"
CODEX_PROMPT="${FACTOR_MINING_CODEX_PROMPT:-Use Quandora Factor Mining. First use the bundled Quandora MCP tools to run quandora_status. If Buddy is missing, stopped, disconnected, or unavailable, stop and show the Buddy setup guidance including https://app.quandora.ai/download/buddy. Show me the Factor Mining public task list. Do not create a session until I choose a public task or provide a custom idea. Then write a valid plugin.py locally, upload it, wait for the backtest, fetch the default factor card if available, and summarize the result.}"
BUDDY_DOWNLOAD_URL="https://app.quandora.ai/download/buddy"

if [[ "${FACTOR_MINING_START_CODEX:-1}" == "0" ]]; then
  START_MODE="none"
fi

usage() {
  cat <<'USAGE'
Usage: install-codex.sh [options]

Options:
  --desktop             Install, print Buddy-required next steps, then open Codex Desktop.
  --no-start            Install and print Buddy-required next steps without starting Codex.
  --install-only        Install the Codex plugin and print Buddy-required next steps.
  -h, --help            Show this help.

Default flow:
  codex plugin marketplace add varsity-tech-product/factor-mining-agent-plugins --ref main
  codex plugin add factor-mining@factor-mining-marketplace
  codex "Show me the Factor Mining public task list."

Plugin installation never downloads or installs Buddy in the background. Buddy
is a separate required local desktop app installed, started, and connected
through an explicit user action.
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --desktop)
      START_MODE="desktop"
      ;;
    --no-start)
      START_MODE="none"
      ;;
    --install-only)
      START_MODE="none"
      INSTALL_ONLY="1"
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
  shift
done

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

plugin_root() {
  codex plugin list --marketplace "${MARKETPLACE_NAME}" 2>/dev/null \
    | awk -v plugin="${PLUGIN_NAME}@${MARKETPLACE_NAME}" '$1 == plugin { print $NF; exit }'
}

buddy_required_guidance() {
  echo "Quandora Buddy is required for account connection and backtesting."
  echo "Buddy is a separate required local desktop app."
  echo "Plugin installation never downloads or installs Buddy in the background."
  echo "Download Buddy explicitly: ${BUDDY_DOWNLOAD_URL}"
  echo "After Buddy is installed and running, connect Quandora through Buddy."
}

run_buddy_doctor() {
  if ! command -v quandora-buddy >/dev/null 2>&1; then
    echo "Quandora Buddy is required for account connection and backtesting and was not found on PATH."
    echo "Buddy is a separate required local desktop app."
    echo "Download Buddy explicitly: ${BUDDY_DOWNLOAD_URL}"
    echo "Connect Quandora through Buddy after installing and starting Buddy."
    return 1
  fi

  local output
  set +e
  output="$(quandora-buddy doctor --json --min-version 0.1.0 2>&1)"
  set -e

  if [[ -n "${output}" ]]; then
    echo "${output}"
  fi

  local doctor_status
  doctor_status="$(
    printf '%s' "${output}" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("status","unknown_error"))' 2>/dev/null \
      || printf '%s' "unknown_error"
  )"

  case "${doctor_status}" in
    ready)
      echo "Quandora Buddy is ready."
      return 0
      ;;
    missing_cli)
      echo "Quandora Buddy is required for account connection and backtesting and was not found on PATH."
      echo "Buddy is a separate required local desktop app."
      echo "Download Buddy explicitly: ${BUDDY_DOWNLOAD_URL}"
      echo "Connect Quandora through Buddy after installing and starting Buddy."
      ;;
    runtime_not_running)
      echo "Quandora Buddy is installed but the local runtime is not ready."
      echo "Buddy is a separate required local desktop app."
      echo "Start Buddy, then ask Codex to check Quandora status again."
      ;;
    disconnected)
      echo "Quandora Buddy is installed but not connected."
      echo "Buddy is a separate required local desktop app."
      echo "Connect Quandora through Buddy, then ask Codex to check Quandora status again."
      ;;
    outdated)
      echo "Quandora Buddy is installed but does not satisfy the required version."
      echo "Buddy is a separate required local desktop app."
      echo "Update Buddy from: ${BUDDY_DOWNLOAD_URL}"
      ;;
    *)
      echo "Quandora Buddy readiness could not be verified."
      echo "Buddy is a separate required local desktop app."
      echo "Open Buddy and check the official Buddy setup guidance."
      ;;
  esac

  return 1
}

print_buddy_first_next_steps() {
  echo "Codex plugin is installed."
  echo "Buddy is required for account connection and backtesting."
  echo "Buddy is a separate required local desktop app."
  echo "Plugin installation never downloads or installs Buddy in the background."
  echo "Download Buddy explicitly: ${BUDDY_DOWNLOAD_URL}"
  echo "Next steps:"
  echo "  1. Install and start Quandora Buddy."
  echo "  2. Connect Quandora through Buddy."
  echo "  3. Start Codex with:"
  printf '     codex %q\n' "${CODEX_PROMPT}"
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

PLUGIN_ROOT="$(plugin_root)"
if [[ -z "${PLUGIN_ROOT}" || ! -d "${PLUGIN_ROOT}" ]]; then
  echo "Could not locate installed plugin root for ${PLUGIN_NAME}@${MARKETPLACE_NAME}." >&2
  exit 1
fi

if ! run_buddy_doctor; then
  print_buddy_first_next_steps
  if [[ "${INSTALL_ONLY}" == "1" ]]; then
    echo "Codex startup was skipped because --install-only was used."
    exit 0
  fi
  echo "Codex startup was skipped until Buddy is ready."
  if [[ "${START_MODE}" == "desktop" || "${START_MODE}" == "none" ]]; then
    echo "For Codex Desktop, run:"
    printf 'codex app %q\n' "${WORKSPACE_PATH}"
  fi
  exit 0
fi

if [[ "${INSTALL_ONLY}" == "1" ]]; then
  print_buddy_first_next_steps
  echo "Codex startup was skipped because --install-only was used."
  exit 0
fi

if [[ "${START_MODE}" == "none" ]]; then
  print_buddy_first_next_steps
  echo "For Codex Desktop, run:"
  printf 'codex app %q\n' "${WORKSPACE_PATH}"
  exit 0
fi

if [[ "${START_MODE}" == "desktop" ]]; then
  echo "Opening Codex Desktop."
  print_buddy_first_next_steps
  exec codex app "${WORKSPACE_PATH}"
fi

echo "Starting Codex CLI."
print_buddy_first_next_steps
exec codex "${CODEX_PROMPT}"
