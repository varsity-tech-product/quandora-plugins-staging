#!/usr/bin/env python3
"""Fail fast on portable, low-context Quandora Staging package invariants."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = PLUGIN_ROOT.parents[1]
SKILLS_ROOT = PLUGIN_ROOT / "skills"
EXPECTED_SKILLS = {
    "factor-analysis",
    "factor-mining",
    "paper-trading",
    "strategy-analysis",
    "strategy-building",
}
MANIFESTS = (
    REPOSITORY_ROOT / "kimi.plugin.json",
    REPOSITORY_ROOT / ".claude-plugin" / "marketplace.json",
    REPOSITORY_ROOT / ".codebuddy-plugin" / "marketplace.json",
    PLUGIN_ROOT / ".claude-plugin" / "plugin.json",
    PLUGIN_ROOT / ".codebuddy-plugin" / "plugin.json",
    PLUGIN_ROOT / ".codex-plugin" / "plugin.json",
    PLUGIN_ROOT / ".cursor-plugin" / "plugin.json",
)
FORBIDDEN_MARKDOWN = {
    "/Users/": "workstation-specific POSIX path",
    "C:\\Users\\": "workstation-specific Windows path",
    "10 MiB ZIP cap": "stale client-wide bundle cap",
    "at most 40 chunk calls": "stale fixed chunk-call cap",
}


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"{path.relative_to(REPOSITORY_ROOT)}: invalid JSON: {exc}") from exc


def _version_values(value: Any) -> list[str]:
    if isinstance(value, dict):
        versions: list[str] = []
        for key, item in value.items():
            if key == "version" and isinstance(item, str):
                versions.append(item)
            versions.extend(_version_values(item))
        return versions
    if isinstance(value, list):
        versions = []
        for item in value:
            versions.extend(_version_values(item))
        return versions
    return []


def _check_manifests(errors: list[str]) -> str | None:
    versions: dict[Path, list[str]] = {}
    for path in MANIFESTS:
        if not path.is_file():
            errors.append(f"missing manifest: {path.relative_to(REPOSITORY_ROOT)}")
            continue
        found = _version_values(_load_json(path))
        if not found:
            errors.append(f"{path.relative_to(REPOSITORY_ROOT)}: missing version")
            continue
        versions[path] = found

    distinct = {version for found in versions.values() for version in found}
    if len(distinct) != 1:
        rendered = ", ".join(
            f"{path.relative_to(REPOSITORY_ROOT)}={found}" for path, found in versions.items()
        )
        errors.append(f"manifest versions drift: {rendered}")
        return None

    codex = _load_json(PLUGIN_ROOT / ".codex-plugin" / "plugin.json")
    prompts = codex.get("interface", {}).get("defaultPrompt")
    if not isinstance(prompts, list) or not 1 <= len(prompts) <= 3:
        errors.append(".codex-plugin/plugin.json: defaultPrompt must contain 1-3 entries")
    elif not all(isinstance(prompt, str) and prompt.strip() for prompt in prompts):
        errors.append(".codex-plugin/plugin.json: defaultPrompt entries must be non-empty strings")

    return next(iter(distinct), None)


def _check_skills(errors: list[str], package_version: str | None) -> None:
    skill_files = {path.parent.name: path for path in SKILLS_ROOT.glob("*/SKILL.md")}
    if set(skill_files) != EXPECTED_SKILLS:
        errors.append(
            "skill set drift: expected "
            f"{sorted(EXPECTED_SKILLS)}, found {sorted(skill_files)}"
        )

    for skill_name, path in sorted(skill_files.items()):
        text = path.read_text(encoding="utf-8")
        if not text.startswith("---\n"):
            errors.append(f"{skill_name}/SKILL.md: missing YAML frontmatter")
        if f"name: {skill_name}\n" not in text[:1000]:
            errors.append(f"{skill_name}/SKILL.md: frontmatter name does not match directory")
        if "description:" not in text[:1000]:
            errors.append(f"{skill_name}/SKILL.md: missing frontmatter description")
        if "qd_plugin_ver" in text:
            errors.append(f"{skill_name}/SKILL.md: routine skill text must not invoke qd_plugin_ver")
        match = re.search(r"^Bundled plugin version: (\S+)$", text, re.MULTILINE)
        if package_version and (match is None or match.group(1) != package_version):
            actual = match.group(1) if match else "missing"
            errors.append(
                f"{skill_name}/SKILL.md: bundled version {actual!r} != {package_version!r}"
            )


def _check_markdown(errors: list[str]) -> None:
    for path in sorted(REPOSITORY_ROOT.rglob("*.md")):
        if ".git" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        for needle, meaning in FORBIDDEN_MARKDOWN.items():
            if needle in text:
                errors.append(
                    f"{path.relative_to(REPOSITORY_ROOT)}: contains {meaning}: {needle!r}"
                )


def main() -> int:
    errors: list[str] = []
    try:
        package_version = _check_manifests(errors)
        _check_skills(errors, package_version)
        _check_markdown(errors)
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
