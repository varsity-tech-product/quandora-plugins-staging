#!/usr/bin/env python3
"""Check Plugin MCP references against the reviewed Auth-owned contract lock."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "contracts" / "public-mcp-contract.v1.json"
USAGE_PATH = ROOT / "contracts" / "skill-mcp-usage.v1.json"
EVAL_PATH = ROOT / "evals" / "mcp-tool-selection.v1.json"
SKILLS_ROOT = ROOT / "plugins" / "quandora-staging" / "skills"
TOOL_REFERENCE = re.compile(r"(?<![A-Za-z0-9_])(?:fm|sb|pt|qd)_[a-z0-9_]+")


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _schema_allows_field(tool: dict[str, Any], field_path: str) -> bool:
    root = field_path.split(".", 1)[0].split("[", 1)[0]
    schema = tool["output_schema"]
    properties = schema.get("properties", {})
    return root in properties or schema.get("additionalProperties") is True


def verify() -> list[str]:
    errors: list[str] = []
    contract = _load(CONTRACT_PATH)
    usage = _load(USAGE_PATH)
    evaluations = _load(EVAL_PATH)
    tools = {tool["name"]: tool for tool in contract["tools"]}

    if usage.get("public_contract_revision") != contract.get("contract_revision"):
        errors.append("skill usage manifest is pinned to a different public contract revision")

    for skill_dir in sorted(path for path in SKILLS_ROOT.iterdir() if path.is_dir()):
        skill_name = skill_dir.name
        policy = usage.get("skills", {}).get(skill_name)
        if not isinstance(policy, dict):
            errors.append(f"{skill_name}: missing skill MCP usage policy")
            continue
        referenced: set[str] = set()
        for document in skill_dir.rglob("*.md"):
            referenced.update(TOOL_REFERENCE.findall(document.read_text(encoding="utf-8")))
        unknown_references = referenced - tools.keys()
        if unknown_references:
            errors.append(f"{skill_name}: unknown tool references {sorted(unknown_references)!r}")

        direct = set(policy.get("direct_tools", []))
        forbidden = set(policy.get("forbidden_tools", []))
        unknown_policy = (direct | forbidden) - tools.keys()
        if unknown_policy:
            errors.append(f"{skill_name}: unknown policy tools {sorted(unknown_policy)!r}")
        if direct - referenced:
            errors.append(f"{skill_name}: direct tools not documented {sorted(direct - referenced)!r}")
        if direct & forbidden:
            errors.append(f"{skill_name}: tools cannot be both direct and forbidden")
        prefixes = tuple(policy.get("allowed_prefixes", []))
        wrong_namespace = {name for name in direct if not name.startswith(prefixes)}
        if wrong_namespace:
            errors.append(f"{skill_name}: direct cross-namespace tools {sorted(wrong_namespace)!r}")

        required_fields = policy.get("required_response_fields", {})
        for tool_name, field_paths in required_fields.items():
            if tool_name not in direct:
                errors.append(f"{skill_name}: response fields declared for non-direct tool {tool_name}")
                continue
            for field_path in field_paths:
                if not _schema_allows_field(tools[tool_name], field_path):
                    errors.append(
                        f"{skill_name}: {tool_name} output schema does not allow {field_path}"
                    )

    for case in evaluations.get("cases", []):
        case_id = case.get("id", "<missing-id>")
        policy = usage.get("skills", {}).get(case.get("skill"), {})
        expected = set(case.get("expected_tools", []))
        forbidden = set(case.get("forbidden_tools", []))
        unknown = (expected | forbidden) - tools.keys()
        if unknown:
            errors.append(f"{case_id}: unknown evaluation tools {sorted(unknown)!r}")
        if expected - set(policy.get("direct_tools", [])):
            errors.append(f"{case_id}: expected calls escape the selected skill ownership")
        if expected & forbidden:
            errors.append(f"{case_id}: expected and forbidden calls overlap")
    return errors


def main() -> int:
    errors = verify()
    if errors:
        for error in errors:
            print(error)
        return 1
    print("Plugin MCP contract, namespace policies, response fields, and eval fixtures are valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
