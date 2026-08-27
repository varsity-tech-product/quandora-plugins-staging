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
    re.compile(r"first entry.{0,400}qd_plugin_ver", re.DOTALL | re.IGNORECASE),
    re.compile(
        r"qd_plugin_ver.{0,240}(before the business entry point|before the business action)",
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

    return next(iter(distinct), None)


def _skill_files(errors: list[str]) -> dict[str, Path]:
    files = {path.parent.name: path for path in SKILLS_ROOT.glob("*/SKILL.md")}
    missing = REQUIRED_SKILLS - set(files)
    if missing:
        errors.append(f"missing required staging Skills: {sorted(missing)}")
    return files


def _check_skills(
    errors: list[str],
    package_version: str | None,
    skill_files: dict[str, Path],
) -> None:
    for skill_name, path in sorted(skill_files.items()):
        text = path.read_text(encoding="utf-8")
        if not text.startswith("---\n"):
            errors.append(f"{skill_name}/SKILL.md: missing YAML frontmatter")
        if f"name: {skill_name}\n" not in text[:1000]:
            errors.append(f"{skill_name}/SKILL.md: frontmatter name does not match directory")
        if "description:" not in text[:1000]:
            errors.append(f"{skill_name}/SKILL.md: missing frontmatter description")
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


def _check_runtime_markdown(errors: list[str], skill_files: dict[str, Path]) -> None:
    paths = [PLUGIN_ROOT / "README.md", *skill_files.values()]
    for path in sorted(paths):
        text = path.read_text(encoding="utf-8")
        for needle, meaning in FORBIDDEN_RUNTIME_MARKDOWN.items():
            if needle in text:
                errors.append(
                    f"{path.relative_to(REPOSITORY_ROOT)}: contains {meaning}: {needle!r}"
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
