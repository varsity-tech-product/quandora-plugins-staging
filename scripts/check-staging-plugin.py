#!/usr/bin/env python3
"""Validate portable, Agent-facing invariants for the staging Plugin package."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
PLUGIN_ROOT = REPOSITORY_ROOT / "plugins" / "quandora-staging"
SKILLS_ROOT = PLUGIN_ROOT / "skills"
REQUIRED_SKILLS = {
    "factor-analysis",
    "factor-mining",
    "paper-trading",
    "strategy-analysis",
    "strategy-building",
    "strategy-portfolio",
}
MAX_MAIN_SKILL_LINES = 220
MAX_CODEX_DEFAULT_PROMPT_CHARS = 128
PORTFOLIO_RESULT_METRIC_MARKERS = (
    "net_profit_pct",
    "annual_return_pct",
    "annual_std",
    "max_drawdown_pct",
)
ROUTING_MARKERS = {
    "factor-analysis": ("Do not use for creating", "$factor-mining"),
    "factor-mining": ("Do not use for the Strategy", "$strategy-building", "$factor-analysis"),
    "paper-trading": ("Do not use to create", "$strategy-building", "$strategy-portfolio"),
    "strategy-analysis": ("Do not use to compose", "$strategy-building"),
    "strategy-building": (
        "Do not use for multi-Strategy Portfolio",
        "$strategy-portfolio",
        "$paper-trading",
        "$strategy-analysis",
    ),
    "strategy-portfolio": ("Do not use for single-Strategy", "$strategy-building", "$paper-trading"),
}
CANONICAL_TOOL_OWNERS = {
    "factor-mining": {
        "get_factor_mining_status",
        "list_factor_mining_tasks",
        "get_factor_plugin_contract",
        "create_factor_task_session",
        "create_custom_factor_session",
        "validate_factor_plugin",
        "get_factor_dedup_context",
        "submit_factor_backtest",
        "continue_factor_backtest",
        "create_factor_result_bundle_download",
        "read_factor_result_bundle_chunk",
        "list_owned_factor_families",
        "get_factor_family_history",
        "get_quandora_guidance",
        "check_quandora_plugin_version",
    },
    "factor-analysis": {
        "get_factor_backtest_window_cards",
        "get_factor_backtest_chart_data",
        "get_factor_backtest_source",
        "create_factor_chart_download",
        "create_factor_raw_artifact_download",
        "read_factor_chart_chunk",
        "get_official_factor_window_cards",
        "get_official_factor_chart_data",
        "get_official_factor_source",
        "create_official_factor_result_bundle_download",
        "read_official_factor_result_bundle_chunk",
    },
    "strategy-building": {
        "get_strategy_capabilities",
        "list_eligible_strategy_factors",
        "get_eligible_strategy_factor",
        "list_shared_strategy_factor_candidates",
        "admit_shared_strategy_factor",
        "import_strategy_factor",
        "submit_adhoc_strategy_backtest",
        "list_strategy_backtests",
        "get_strategy_backtest",
        "continue_strategy_backtest",
        "rerun_strategy_backtest",
        "create_strategy_result_bundle_download",
        "read_strategy_result_bundle_chunk",
        "create_strategy",
        "revise_strategy",
        "get_strategy",
        "get_strategy_version",
        "submit_strategy_backtest",
    },
    "strategy-analysis": {
        "get_strategy_backtest_artifact",
        "get_strategy_backtest_analysis_data",
        "create_strategy_artifact_download",
    },
    "strategy-portfolio": {
        "list_strategy_portfolios",
        "create_strategy_portfolio",
        "revise_strategy_portfolio",
        "get_strategy_portfolio",
        "get_strategy_portfolio_version",
        "list_eligible_strategy_portfolio_source_runs",
        "submit_strategy_portfolio_evaluation",
        "get_strategy_portfolio_evaluation",
        "get_strategy_portfolio_evaluation_result",
    },
    "paper-trading": {
        "list_paper_trade_sources",
        "get_paper_trade_source",
        "list_paper_trades",
        "get_paper_trade",
        "start_paper_trade",
        "refresh_paper_trade_account_snapshot",
        "list_closed_paper_trade_positions",
        "get_paper_trade_equity_curve",
        "list_paper_trade_fills",
        "list_paper_trade_funding",
        "get_paper_trade_strategy_code",
        "stop_paper_trade",
        "start_strategy_portfolio_paper_trade",
        "get_strategy_portfolio_paper_trade",
        "stop_strategy_portfolio_paper_trade",
    },
}
RETIRED_TOOL_NAMES = {
    "fm_status", "fm_list_tasks", "fm_get_contract", "fm_task_session",
    "fm_custom_sess", "fm_validate", "fm_dedup_context", "fm_run_backtest",
    "fm_resume_run", "fm_window_cards", "fm_chart_data", "fm_run_source",
    "fm_png_ticket", "fm_raw_ticket", "fm_bundle_ticket", "fm_bundle_chunk",
    "fm_png_chunk", "fm_list_factors", "fm_get_history", "of_window_cards",
    "of_chart_data", "of_run_source", "of_bundle_ticket", "of_bundle_chunk",
    "qd_get_guidance", "qd_plugin_ver", "sb_get_contract", "sb_list_eligible",
    "sb_factor_detail", "sb_shared_list", "sb_shared_add", "sb_import_factor",
    "sb_submit_run", "sb_list_runs", "sb_get_run", "sb_resume_run",
    "sb_rerun_run", "sb_get_artifact", "sb_analysis_data", "sb_file_ticket",
    "sb_bundle_ticket", "sb_bundle_chunk", "pt_src_create", "pt_src_revise",
    "pt_src_def_get", "pt_src_ver_get", "pt_src_bt_submit", "pt_list_sources",
    "pt_get_source", "pt_list_runs", "pt_get_run", "pt_submit_run",
    "pt_get_portfolio", "pt_list_pos", "pt_get_equity", "pt_list_fills",
    "pt_list_funding", "pt_get_code", "pt_stop_run", "pt_sp_list",
    "pt_sp_create", "pt_sp_revise", "pt_sp_get", "pt_sp_version",
    "pt_sp_bt_submit", "pt_sp_bt_get", "pt_sp_bt_result", "pt_sp_run_submit",
    "pt_sp_run_get", "pt_sp_run_stop",
    "submit_strategy_portfolio_backtest", "get_strategy_portfolio_backtest",
    "get_strategy_portfolio_backtest_result",
}
DIRECT_VERSION_MANIFESTS = (
    REPOSITORY_ROOT / "kimi.plugin.json",
    PLUGIN_ROOT / ".claude-plugin" / "plugin.json",
    PLUGIN_ROOT / ".codebuddy-plugin" / "plugin.json",
    PLUGIN_ROOT / ".codex-plugin" / "plugin.json",
    PLUGIN_ROOT / ".cursor-plugin" / "plugin.json",
)
MARKETPLACE_MANIFESTS = (
    REPOSITORY_ROOT / ".claude-plugin" / "marketplace.json",
    REPOSITORY_ROOT / ".codebuddy-plugin" / "marketplace.json",
)
FORBIDDEN_RUNTIME_MARKDOWN = {
    "/Users/": "workstation-specific POSIX path",
    "C:\\Users\\": "workstation-specific Windows path",
    "quandora-results/": "obsolete local result root",
    "10 MiB ZIP cap": "stale client-wide bundle cap",
    "at most 40 chunk calls": "stale fixed chunk-call cap",
}
REQUIRED_RESULT_DESTINATIONS = {
    PLUGIN_ROOT / "README.md": (
        "Quandora staging result/factor/<factor_slug>.zip",
        "Quandora staging result/strategy/<strategy_slug>.zip",
    ),
    SKILLS_ROOT / "factor-mining" / "SKILL.md": (
        "Quandora staging result/factor/<factor_slug>.zip",
        "never silently fall back to a generic `factor` slug",
    ),
    SKILLS_ROOT / "strategy-building" / "SKILL.md": (
        "Quandora staging result/strategy/<strategy_slug>.zip",
    ),
}
MANDATORY_VERSION_PROBE_PATTERNS = (
    re.compile(r"^##\s+Plugin Version Reminder\s*$", re.MULTILINE | re.IGNORECASE),
    re.compile(r"first entry.{0,400}check_quandora_plugin_version", re.DOTALL | re.IGNORECASE),
    re.compile(
        r"check_quandora_plugin_version.{0,240}(before the business entry point|before the business action)",
        re.DOTALL | re.IGNORECASE,
    ),
)


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"{path.relative_to(REPOSITORY_ROOT)}: invalid JSON: {exc}") from exc


def _direct_version(path: Path) -> str | None:
    document = _load_json(path)
    if not isinstance(document, dict):
        return None
    version = document.get("version")
    return version if isinstance(version, str) and version else None


def _marketplace_versions(path: Path) -> list[str]:
    document = _load_json(path)
    if not isinstance(document, dict):
        return []
    versions = []
    root_version = document.get("version")
    if isinstance(root_version, str) and root_version:
        versions.append(root_version)
    plugins = document.get("plugins")
    if isinstance(plugins, list):
        staging = [
            item
            for item in plugins
            if isinstance(item, dict) and item.get("name") == "quandora-staging"
        ]
        if len(staging) == 1 and isinstance(staging[0].get("version"), str):
            versions.append(staging[0]["version"])
    return versions


def _check_manifests(errors: list[str]) -> str | None:
    recorded: list[tuple[Path, str]] = []
    for path in DIRECT_VERSION_MANIFESTS:
        version = _direct_version(path)
        if version is None:
            errors.append(f"{path.relative_to(REPOSITORY_ROOT)}: missing top-level version")
        else:
            recorded.append((path, version))

    for path in MARKETPLACE_MANIFESTS:
        versions = _marketplace_versions(path)
        if len(versions) != 2:
            errors.append(
                f"{path.relative_to(REPOSITORY_ROOT)}: expected marketplace and "
                "quandora-staging versions"
            )
        else:
            recorded.extend((path, version) for version in versions)

    distinct = {version for _, version in recorded}
    if len(distinct) != 1:
        rendered = ", ".join(
            f"{path.relative_to(REPOSITORY_ROOT)}={version}" for path, version in recorded
        )
        errors.append(f"Plugin version drift: {rendered}")
        return None

    codex = _load_json(PLUGIN_ROOT / ".codex-plugin" / "plugin.json")
    prompts = codex.get("interface", {}).get("defaultPrompt") if isinstance(codex, dict) else None
    if not isinstance(prompts, list) or not 1 <= len(prompts) <= 3:
        errors.append(
            "plugins/quandora-staging/.codex-plugin/plugin.json: "
            "defaultPrompt must contain 1-3 staging entry examples"
        )
    elif not all(isinstance(prompt, str) and prompt.strip() for prompt in prompts):
        errors.append("Codex defaultPrompt entries must be non-empty strings")
    else:
        for index, prompt in enumerate(prompts):
            if len(prompt) > MAX_CODEX_DEFAULT_PROMPT_CHARS:
                errors.append(
                    "plugins/quandora-staging/.codex-plugin/plugin.json: "
                    f"defaultPrompt[{index}] exceeds the "
                    f"{MAX_CODEX_DEFAULT_PROMPT_CHARS}-character Codex limit"
                )

    return next(iter(distinct), None)


def _skill_files(errors: list[str]) -> dict[str, Path]:
    files = {path.parent.name: path for path in SKILLS_ROOT.glob("*/SKILL.md")}
    missing = REQUIRED_SKILLS - set(files)
    if missing:
        errors.append(f"missing required staging Skills: {sorted(missing)}")
    unexpected = set(files) - REQUIRED_SKILLS
    if unexpected:
        errors.append(f"unexpected staging Skills: {sorted(unexpected)}")
    return files


def _check_skills(
    errors: list[str],
    package_version: str | None,
    skill_files: dict[str, Path],
) -> None:
    for skill_name, path in sorted(skill_files.items()):
        text = path.read_text(encoding="utf-8")
        line_count = len(text.splitlines())
        if line_count > MAX_MAIN_SKILL_LINES:
            errors.append(
                f"{skill_name}/SKILL.md: {line_count} lines exceeds the "
                f"{MAX_MAIN_SKILL_LINES}-line progressive-disclosure limit"
            )
        if not text.startswith("---\n"):
            errors.append(f"{skill_name}/SKILL.md: missing YAML frontmatter")
        if f"name: {skill_name}\n" not in text[:1000]:
            errors.append(f"{skill_name}/SKILL.md: frontmatter name does not match directory")
        if "description:" not in text[:1000]:
            errors.append(f"{skill_name}/SKILL.md: missing frontmatter description")
        for marker in ROUTING_MARKERS.get(skill_name, ()):
            if marker not in text:
                errors.append(f"{skill_name}/SKILL.md: missing routing boundary {marker!r}")
        if any(pattern.search(text) for pattern in MANDATORY_VERSION_PROBE_PATTERNS):
            errors.append(
                f"{skill_name}/SKILL.md: version checks must remain explicit diagnostics, "
                "not a mandatory entry probe"
            )
        match = re.search(r"^Bundled plugin version: (\S+)$", text, re.MULTILINE)
        if package_version and (match is None or match.group(1) != package_version):
            actual = match.group(1) if match else "missing"
            errors.append(
                f"{skill_name}/SKILL.md: bundled version {actual!r} != {package_version!r}"
            )

        agent_file = path.parent / "agents" / "openai.yaml"
        if not agent_file.is_file():
            errors.append(f"{skill_name}: missing agents/openai.yaml")
        else:
            agent_text = agent_file.read_text(encoding="utf-8")
            if f"${skill_name}" not in agent_text:
                errors.append(
                    f"{skill_name}/agents/openai.yaml: default prompt must name ${skill_name}"
                )
            if 'value: "quandora-staging"' not in agent_text:
                errors.append(
                    f"{skill_name}/agents/openai.yaml: missing Quandora Staging MCP dependency"
                )

        for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
            if target.startswith(("http://", "https://", "#")):
                continue
            local_target = (path.parent / target.split("#", 1)[0]).resolve()
            if not local_target.exists():
                errors.append(f"{skill_name}/SKILL.md: broken local reference {target!r}")

        reference_dir = path.parent / "references"
        if reference_dir.is_dir():
            linked = {
                (path.parent / target.split("#", 1)[0]).resolve()
                for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text)
                if not target.startswith(("http://", "https://", "#"))
            }
            for reference in reference_dir.glob("*.md"):
                if reference.resolve() not in linked:
                    errors.append(
                        f"{skill_name}/references/{reference.name}: supporting material is not "
                        "linked from its primary SKILL.md"
                    )

    all_tools = [
        tool for owned_tools in CANONICAL_TOOL_OWNERS.values() for tool in owned_tools
    ]
    if len(all_tools) != len(set(all_tools)):
        errors.append("canonical tool ownership map contains duplicate primary owners")
    if len(all_tools) != 71:
        errors.append(f"canonical tool ownership map must contain 71 tools, got {len(all_tools)}")
    for owner, owned_tools in CANONICAL_TOOL_OWNERS.items():
        owner_path = skill_files.get(owner)
        if owner_path is None:
            continue
        owner_text = owner_path.read_text(encoding="utf-8")
        for tool in sorted(owned_tools):
            if f"`{tool}`" not in owner_text:
                errors.append(f"{owner}/SKILL.md: missing primary tool ownership for {tool}")

    for skill_name, path in sorted(skill_files.items()):
        text = path.read_text(encoding="utf-8")
        for retired in sorted(RETIRED_TOOL_NAMES):
            if re.search(rf"(?<![A-Za-z0-9_]){re.escape(retired)}(?![A-Za-z0-9_])", text):
                errors.append(f"{skill_name}/SKILL.md: retired tool name remains: {retired}")

    portfolio_path = skill_files.get("strategy-portfolio")
    if portfolio_path is not None:
        portfolio_text = portfolio_path.read_text(encoding="utf-8")
        for marker in PORTFOLIO_RESULT_METRIC_MARKERS:
            if marker not in portfolio_text:
                errors.append(
                    "strategy-portfolio/SKILL.md: missing canonical Portfolio result metric "
                    f"{marker!r}"
                )


def _check_runtime_markdown(errors: list[str], skill_files: dict[str, Path]) -> None:
    references = sorted(SKILLS_ROOT.glob("*/references/*.md"))
    paths = [
        REPOSITORY_ROOT / "README.md",
        PLUGIN_ROOT / "README.md",
        *skill_files.values(),
        *references,
    ]
    for path in sorted(paths):
        text = path.read_text(encoding="utf-8")
        for needle, meaning in FORBIDDEN_RUNTIME_MARKDOWN.items():
            if needle in text:
                errors.append(
                    f"{path.relative_to(REPOSITORY_ROOT)}: contains {meaning}: {needle!r}"
                )
        for retired in sorted(RETIRED_TOOL_NAMES):
            if re.search(rf"(?<![A-Za-z0-9_]){re.escape(retired)}(?![A-Za-z0-9_])", text):
                errors.append(
                    f"{path.relative_to(REPOSITORY_ROOT)}: retired tool name remains: {retired}"
                )

    for path, required_fragments in REQUIRED_RESULT_DESTINATIONS.items():
        text = path.read_text(encoding="utf-8")
        for fragment in required_fragments:
            if fragment not in text:
                errors.append(
                    f"{path.relative_to(REPOSITORY_ROOT)}: "
                    f"missing portable result-destination contract: {fragment!r}"
                )


def main() -> int:
    errors: list[str] = []
    try:
        package_version = _check_manifests(errors)
        skills = _skill_files(errors)
        _check_skills(errors, package_version, skills)
        _check_runtime_markdown(errors, skills)
    except ValueError as exc:
        errors.append(str(exc))

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(f"Quandora Staging package checks passed for version {package_version}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
