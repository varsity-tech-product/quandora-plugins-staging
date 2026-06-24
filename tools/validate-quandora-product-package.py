#!/usr/bin/env python3
"""Validate that the Quandora product plugin package uses product endpoints."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PRODUCT_MCP_URL = "https://mcp.quandora.ai/factor-mining"
STAGING_MCP_HOST = "mcp-" "staging.varsity.lol"
STAGING_WEB_HOST = "quandora." "varsity.lol"
FORBIDDEN_STAGING_URLS = (
    f"https://{STAGING_MCP_HOST}/factor-mining",
    STAGING_MCP_HOST,
    f"https://{STAGING_WEB_HOST}",
    STAGING_WEB_HOST,
)

PRODUCT_FACING_FILES = (
    ".claude-plugin/marketplace.json",
    "plugins/quandora/.codex-plugin/plugin.json",
    "plugins/quandora/.claude-plugin/plugin.json",
    "plugins/quandora/.mcp.json",
    "plugins/quandora/skills/factor-mining/agents/openai.yaml",
    "plugins/quandora/README.md",
    "README.md",
    "install-openclaw.sh",
)

PRODUCT_URL_REQUIRED_FILES = (
    "plugins/quandora/.claude-plugin/plugin.json",
    "plugins/quandora/.mcp.json",
    "plugins/quandora/skills/factor-mining/agents/openai.yaml",
    "install-openclaw.sh",
)


def _read(relative_path: str) -> str:
    path = ROOT / relative_path
    if not path.is_file():
        raise AssertionError(f"Missing product package file: {relative_path}")
    return path.read_text()


def main() -> int:
    failures: list[str] = []

    for relative_path in PRODUCT_FACING_FILES:
        content = _read(relative_path)
        for forbidden in FORBIDDEN_STAGING_URLS:
            if forbidden in content:
                failures.append(f"{relative_path}: contains forbidden staging URL {forbidden}")

    for relative_path in PRODUCT_URL_REQUIRED_FILES:
        content = _read(relative_path)
        if PRODUCT_MCP_URL not in content:
            failures.append(f"{relative_path}: missing product MCP URL {PRODUCT_MCP_URL}")

    if failures:
        print("Quandora product package validation failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Quandora product package validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
