#!/usr/bin/env python3
"""Static release-contract checks for the staging Paper Trading skill."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PLUGIN = ROOT / "plugins" / "quandora-staging"
SKILL = PLUGIN / "skills" / "paper-trading" / "SKILL.md"
RELEASE = "1.44"

EXPECTED_TOOLS = {
    "pt_create_strategy_portfolio",
    "pt_get_code",
    "pt_get_equity",
    "pt_get_portfolio",
    "pt_get_portfolio_backtest",
    "pt_get_portfolio_backtest_result",
    "pt_get_portfolio_paper",
    "pt_get_run",
    "pt_get_strategy_portfolio",
    "pt_get_strategy_portfolio_version",
    "pt_list_fills",
    "pt_list_funding",
    "pt_list_positions",
    "pt_list_runs",
    "pt_list_sources",
    "pt_revise_strategy_portfolio",
    "pt_stop_portfolio_paper",
    "pt_stop_run",
    "pt_submit_portfolio_backtest",
    "pt_submit_portfolio_paper",
    "pt_submit_run",
}

VERSION_FIELDS = (
    (ROOT / ".claude-plugin" / "marketplace.json", ("version",)),
    (ROOT / ".claude-plugin" / "marketplace.json", ("plugins", 0, "version")),
    (ROOT / ".codebuddy-plugin" / "marketplace.json", ("version",)),
    (ROOT / ".codebuddy-plugin" / "marketplace.json", ("plugins", 0, "version")),
    (PLUGIN / ".claude-plugin" / "plugin.json", ("version",)),
    (PLUGIN / ".codebuddy-plugin" / "plugin.json", ("version",)),
    (PLUGIN / ".codex-plugin" / "plugin.json", ("version",)),
    (PLUGIN / ".cursor-plugin" / "plugin.json", ("version",)),
    (ROOT / "kimi.plugin.json", ("version",)),
)

DESCRIPTION_MANIFESTS = (
    ROOT / ".claude-plugin" / "marketplace.json",
    ROOT / ".codebuddy-plugin" / "marketplace.json",
    ROOT / ".cursor-plugin" / "marketplace.json",
    PLUGIN / ".claude-plugin" / "plugin.json",
    PLUGIN / ".codebuddy-plugin" / "plugin.json",
    PLUGIN / ".codex-plugin" / "plugin.json",
    PLUGIN / ".cursor-plugin" / "plugin.json",
    ROOT / "kimi.plugin.json",
)


def _lookup(value: object, path: tuple[str | int, ...]) -> object:
    for key in path:
        value = value[key]  # type: ignore[index]
    return value


def main() -> int:
    failures: list[str] = []
    text = SKILL.read_text(encoding="utf-8")

    for path, field_path in VERSION_FIELDS:
        value = _lookup(json.loads(path.read_text(encoding="utf-8")), field_path)
        if value != RELEASE:
            failures.append(f"{path.relative_to(ROOT)}:{field_path} is {value!r}, expected {RELEASE!r}")

    for path in DESCRIPTION_MANIFESTS:
        serialized = json.dumps(json.loads(path.read_text(encoding="utf-8")))
        if "Paper Trading" not in serialized:
            failures.append(f"{path.relative_to(ROOT)} does not describe Paper Trading")

    for skill_name in ("factor-mining", "paper-trading", "strategy-building"):
        skill_text = (PLUGIN / "skills" / skill_name / "SKILL.md").read_text(encoding="utf-8")
        if f"Bundled plugin version: {RELEASE}" not in skill_text:
            failures.append(f"{skill_name} does not advertise bundled version {RELEASE}")

    discovered_tools = set(re.findall(r"`(pt_[a-z_]+)`", text))
    if discovered_tools != EXPECTED_TOOLS:
        failures.append(
            "Paper tool inventory mismatch: "
            f"missing={sorted(EXPECTED_TOOLS - discovered_tools)}, "
            f"unexpected={sorted(discovered_tools - EXPECTED_TOOLS)}"
        )

    forbidden_tools = sorted(set(re.findall(r"\bpt_(?:archive|unarchive|resume)[a-z_]*\b", text)))
    if forbidden_tools:
        failures.append(f"forbidden Paper tools are named as callable tools: {forbidden_tools}")

    prompt_smokes = {
        "normal submit": (
            "pt_list_sources",
            "explicit confirmation",
            "pt_submit_run",
        ),
        "optimizer submit": (
            "source run's exact authoritative FM initial",
            "config_source=caller",
            "new StrategyRun for the same StrategyVersion",
        ),
        "30D curve": ("`30D`", "`1.5h`", "480", "synthetic pre-live"),
        "positions and current PnL": (
            "Current assets/current PnL: call `pt_get_portfolio` once",
            "Historical positions: call `pt_list_positions`",
        ),
        "terminal stop": ("Before `pt_stop_run`", "stop is terminal", "Never call it pause"),
        "Portfolio Paper": (
            "independent static sleeve",
            "pt_submit_portfolio_paper",
            "Do not claim parent aggregate",
            "positions exist",
        ),
        "universe override": (
            "Never send `symbols`, `universe`, or `universe_policy`",
            "including null or empty values",
        ),
        "resume request": ("no Paper archive, unarchive, resume", "produces a new Paper run"),
    }
    for smoke, fragments in prompt_smokes.items():
        missing = [fragment for fragment in fragments if fragment not in text]
        if missing:
            failures.append(f"prompt smoke {smoke!r} lacks contract fragments: {missing}")

    downstream_contract = {
        "historical default optimizer evidence": "config_source=default",
        "invalid fallback optimizer evidence": "config_source=default_after_invalid",
        "authoritative/local capital mismatch": "source_capital_mismatch",
        "authoritative capital unavailable": "source_capital_unavailable",
        "optimizer execution unavailable": "optimizer_execution_unavailable",
        "bounded discovery validation": "source_validation_unavailable",
        "Paper config mismatch": "portfolio_optimizer_paper_config_mismatch",
    }
    for contract, fragment in downstream_contract.items():
        if fragment not in text:
            failures.append(f"missing {contract}: {fragment}")

    if "operation.paper_trade.submit" not in text or "Do not fetch or cite" not in text:
        failures.append("conflicting FM Paper submit guidance is not explicitly excluded")

    if failures:
        print("Paper Trading plugin validation failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print(
        "Paper Trading plugin validation passed: "
        "9 version fields, 21 tools, 8 prompt smokes, and downstream safety contracts."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
