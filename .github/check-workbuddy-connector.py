#!/usr/bin/env python3
"""Validate the isolated WorkBuddy Connector submission candidate."""

from __future__ import annotations

import json
import re
import struct
import sys
from pathlib import Path
from typing import Any

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
CONNECTOR_ROOT = REPOSITORY_ROOT / "connectors" / "workbuddy" / "quandora-staging"
SOURCE_SKILLS_ROOT = REPOSITORY_ROOT / "plugins" / "quandora-staging" / "skills"
REQUIRED_SKILLS = {
    "factor-analysis",
    "factor-mining",
    "paper-trading",
    "strategy-analysis",
    "strategy-building",
    "strategy-portfolio",
}
EXPECTED_ROOT_ENTRIES = {"connector-meta.json", "mcp.json", "icon.png", "skills"}
EXPECTED_SERVER = {
    "type": "streamableHttp",
    "url": "https://mcp-staging.varsity.lol/quant",
    "timeout": 30000,
}


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"{path.relative_to(REPOSITORY_ROOT)}: invalid JSON: {exc}") from exc


def _check_metadata(errors: list[str]) -> None:
    path = CONNECTOR_ROOT / "connector-meta.json"
    document = _load_json(path)
    if not isinstance(document, dict):
        errors.append("connector-meta.json must contain one JSON object")
        return

    required_strings = {
        "name",
        "name_zh",
        "name_en",
        "description",
        "description_zh",
        "description_en",
    }
    for field in required_strings:
        if not isinstance(document.get(field), str) or not document[field].strip():
            errors.append(f"connector-meta.json: {field} must be a non-empty string")

    if document.get("source") != "quandora-staging":
        errors.append("connector-meta.json: source must be quandora-staging")
    if document.get("type") != "mcp":
        errors.append("connector-meta.json: type must be mcp")
    if document.get("minWorkbuddyVersion") != "4.24.0":
        errors.append("connector-meta.json: localized examples require minWorkbuddyVersion 4.24.0")
    for forbidden in ("auth_mode", "maxWorkbuddyVersion", "version"):
        if forbidden in document:
            errors.append(f"connector-meta.json: omit unnecessary field {forbidden}")

    for field in ("examples_zh", "examples_en"):
        examples = document.get(field)
        if (
            not isinstance(examples, list)
            or not 2 <= len(examples) <= 5
            or any(not isinstance(item, str) or not item.strip() for item in examples)
        ):
            errors.append(f"connector-meta.json: {field} must contain 2-5 non-empty strings")


def _check_mcp(errors: list[str]) -> None:
    document = _load_json(CONNECTOR_ROOT / "mcp.json")
    expected = {"mcpServers": {"quandora-staging": EXPECTED_SERVER}}
    if document != expected:
        errors.append("mcp.json must declare exactly the approved single HTTPS streamableHttp server")


def _check_icon(errors: list[str]) -> None:
    path = CONNECTOR_ROOT / "icon.png"
    try:
        data = path.read_bytes()
    except OSError as exc:
        errors.append(f"icon.png cannot be read: {exc}")
        return
    if len(data) < 33 or data[:8] != b"\x89PNG\r\n\x1a\n" or data[12:16] != b"IHDR":
        errors.append("icon.png must be a valid PNG")
        return
    width, height, _depth, color_type = struct.unpack(">IIBB", data[16:26])
    if width < 64 or height < 64:
        errors.append("icon.png must be at least 64x64")
    if color_type not in {4, 6}:
        errors.append("icon.png must include an alpha channel")


def _markdown_files(root: Path) -> dict[Path, Path]:
    return {path.relative_to(root): path for path in root.rglob("*.md")}


def _check_skills(errors: list[str]) -> None:
    skills_root = CONNECTOR_ROOT / "skills"
    actual_skills = {path.name for path in skills_root.iterdir() if path.is_dir()}
    if actual_skills != REQUIRED_SKILLS:
        errors.append(f"skills must be exactly {sorted(REQUIRED_SKILLS)}")

    source_files = _markdown_files(SOURCE_SKILLS_ROOT)
    connector_files = _markdown_files(skills_root)
    if connector_files.keys() != source_files.keys():
        errors.append("Connector markdown files must exactly mirror the canonical staging skills")
        return

    for relative_path, connector_path in connector_files.items():
        if connector_path.read_bytes() != source_files[relative_path].read_bytes():
            errors.append(f"skills/{relative_path}: differs from the canonical staging skill")

    for skill_name in REQUIRED_SKILLS:
        skill_path = skills_root / skill_name / "SKILL.md"
        if not skill_path.is_file():
            errors.append(f"skills/{skill_name}/SKILL.md is required")
            continue
        text = skill_path.read_text(encoding="utf-8")
        if not re.match(rf"---\s*\nname:\s*{re.escape(skill_name)}\s*\n", text):
            errors.append(f"skills/{skill_name}/SKILL.md must start with matching frontmatter name")
        if "\ndescription:" not in text.split("---", 2)[1]:
            errors.append(f"skills/{skill_name}/SKILL.md must declare a frontmatter description")


def main() -> int:
    errors: list[str] = []
    if not CONNECTOR_ROOT.is_dir():
        errors.append("WorkBuddy Connector root is missing")
    else:
        entries = {path.name for path in CONNECTOR_ROOT.iterdir()}
        if entries != EXPECTED_ROOT_ENTRIES:
            errors.append(f"Connector root entries must be exactly {sorted(EXPECTED_ROOT_ENTRIES)}")
        if any(path.name == "scripts" for path in CONNECTOR_ROOT.rglob("scripts")):
            errors.append("Connector submission must not contain scripts")
        _check_metadata(errors)
        _check_mcp(errors)
        _check_icon(errors)
        _check_skills(errors)

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("WorkBuddy staging Connector contract OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
