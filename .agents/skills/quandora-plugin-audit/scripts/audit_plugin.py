#!/usr/bin/env python3
"""Deterministically audit Skill authoring and package-hygiene invariants."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

SKILL_NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
CJK = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")
LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
INLINE_CODE = re.compile(r"`([a-z][a-z0-9_]+)`")
TOOL_SECTION = re.compile(
    r"^##\s+(?:Tools|Available Actions)\s*$\n(.*?)(?=^##\s|\Z)",
    re.IGNORECASE | re.MULTILINE | re.DOTALL,
)
TOOL_PREFIXES = (
    "admit_",
    "check_",
    "continue_",
    "create_",
    "get_",
    "import_",
    "list_",
    "read_",
    "refresh_",
    "rerun_",
    "revise_",
    "start_",
    "stop_",
    "submit_",
    "validate_",
)
ALLOWED_PLUGIN_ENTRIES = {
    ".app.json",
    ".claude-plugin",
    ".codebuddy-plugin",
    ".codex-plugin",
    ".cursor-plugin",
    ".mcp.json",
    "LICENSE",
    "README.md",
    "assets",
    "hooks",
    "mcp.json",
    "skills",
}
RELEASE_HISTORY_PATTERNS = (
    re.compile(r"^#{1,3}\s+Release (?:Order|History|Notes)\s*$", re.IGNORECASE | re.MULTILINE),
    re.compile(r"\bPlugin\s+\d+\.\d+(?:\.\d+)?\b"),
    re.compile(r"\b(?:PR|pull request|issue)\s+#?\d+\b", re.IGNORECASE),
    re.compile(r"\bdeploy\b.{0,100}\bbefore publishing\b", re.IGNORECASE | re.DOTALL),
)
WINDOWS_PATH = re.compile(r"(?:[A-Za-z]:\\|(?:scripts|references|assets)\\)")


@dataclass(frozen=True)
class Finding:
    rule_id: str
    severity: str
    path: str
    line: int | None
    message: str
    source_class: str


def _line_number(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def _frontmatter(path: Path, text: str) -> tuple[dict[str, str], list[Finding]]:
    findings: list[Finding] = []
    relative = path.as_posix()
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        return {}, [
            Finding("OAI-SKILL-001", "error", relative, 1, "missing YAML frontmatter", "official")
        ]
    try:
        end = lines.index("---", 1)
    except ValueError:
        return {}, [
            Finding("OAI-SKILL-001", "error", relative, 1, "unterminated YAML frontmatter", "official")
        ]

    values: dict[str, str] = {}
    index = 1
    while index < end:
        match = re.match(r"^([A-Za-z_][A-Za-z0-9_-]*):\s*(.*)$", lines[index])
        if not match:
            index += 1
            continue
        key, value = match.groups()
        if value in {">", "|"}:
            collected: list[str] = []
            index += 1
            while index < end and (not lines[index] or lines[index][0].isspace()):
                collected.append(lines[index].strip())
                index += 1
            values[key] = " ".join(part for part in collected if part)
            continue
        values[key] = value.strip().strip('"').strip("'")
        index += 1
    return values, findings


def _local_links(path: Path, text: str) -> list[str]:
    return [
        target.split("#", 1)[0]
        for target in LINK.findall(text)
        if target and not target.startswith(("#", "http://", "https://", "mailto:"))
    ]


def _changed_paths(repo_root: Path, base_ref: str) -> set[str]:
    command = ["git", "diff", "--name-only", "--diff-filter=ACMR", f"{base_ref}...HEAD"]
    completed = subprocess.run(
        command,
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        detail = completed.stderr.strip() or "git diff failed"
        raise ValueError(f"cannot resolve changed-file base {base_ref!r}: {detail}")
    return {line for line in completed.stdout.splitlines() if line}


def _contract_tools(path: Path | None) -> set[str] | None:
    if path is None:
        return None
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"invalid public MCP contract {path}: {exc}") from exc
    tools = document.get("tools") if isinstance(document, dict) else None
    if not isinstance(tools, list):
        raise ValueError(f"invalid public MCP contract {path}: tools must be a list")
    names = {
        item.get("name")
        for item in tools
        if isinstance(item, dict) and isinstance(item.get("name"), str)
    }
    if not names:
        raise ValueError(f"invalid public MCP contract {path}: no named tools")
    return names


def audit_repository(
    repo_root: Path,
    plugin_root: Path,
    *,
    mode: str,
    changed_paths: set[str] | None = None,
    public_tools: set[str] | None = None,
) -> list[Finding]:
    repo_root = repo_root.resolve()
    plugin_root = plugin_root.resolve()
    if not plugin_root.is_relative_to(repo_root):
        raise ValueError("plugin root must remain inside repository root")
    if not plugin_root.is_dir():
        raise ValueError(f"plugin root does not exist: {plugin_root}")

    selected = changed_paths or set()

    def in_scope(path: Path) -> bool:
        if mode == "full":
            return True
        relative = path.relative_to(repo_root).as_posix()
        return relative in selected or any(item.startswith(f"{relative}/") for item in selected)

    findings: list[Finding] = []

    def add(
        rule_id: str,
        severity: str,
        path: Path,
        message: str,
        source_class: str,
        line: int | None = None,
    ) -> None:
        findings.append(
            Finding(
                rule_id,
                severity,
                path.relative_to(repo_root).as_posix(),
                line,
                message,
                source_class,
            )
        )

    manifest = plugin_root / ".codex-plugin" / "plugin.json"
    if in_scope(manifest) and not manifest.is_file():
        add("OAI-PLUGIN-001", "error", plugin_root, "missing .codex-plugin/plugin.json", "official")

    for entry in sorted(plugin_root.iterdir(), key=lambda item: item.name):
        if not in_scope(entry):
            continue
        if entry.name not in ALLOWED_PLUGIN_ENTRIES:
            add(
                "QD-PACKAGE-001",
                "error",
                entry,
                f"unsupported plugin-root entry {entry.name!r}; remove it or place the capability in an official component",
                "quandora_policy",
            )

    skills_root = plugin_root / "skills"
    skill_files = sorted(skills_root.glob("*/SKILL.md")) if skills_root.is_dir() else []
    for skill_file in skill_files:
        if not in_scope(skill_file.parent):
            continue
        text = skill_file.read_text(encoding="utf-8")
        relative_skill = skill_file.relative_to(repo_root)
        metadata, metadata_findings = _frontmatter(relative_skill, text)
        findings.extend(metadata_findings)
        name = metadata.get("name", "")
        description = metadata.get("description", "")
        if (
            not SKILL_NAME.fullmatch(name)
            or len(name) > 64
            or name != skill_file.parent.name
        ):
            add(
                "ANT-SKILL-001",
                "error",
                skill_file,
                "frontmatter name must match the directory and use at most 64 lowercase letters, digits, or hyphens",
                "official",
                2,
            )
        if not description or len(description) > 1024:
            add(
                "ANT-SKILL-001",
                "error",
                skill_file,
                "frontmatter description must contain 1-1024 characters",
                "official",
                3,
            )
        elif description.lower().startswith(("use when", "use this skill")):
            add(
                "QD-PRODUCT-004",
                "error",
                skill_file,
                "description must lead with what the Skill does before its activation condition",
                "quandora_policy",
                3,
            )
        elif not re.search(r"\b(?:use when|when (?:a|the) user|for requests? that)\b", description, re.IGNORECASE):
            add(
                "OAI-SKILL-002",
                "warning",
                skill_file,
                "description may not state a concrete activation condition",
                "official",
                3,
            )

        if len(text.splitlines()) > 500:
            add(
                "ANT-SKILL-002",
                "error",
                skill_file,
                "SKILL.md exceeds the 500-line progressive-disclosure boundary",
                "official",
            )

        links = _local_links(skill_file, text)
        resolved_links = {(skill_file.parent / target).resolve() for target in links}
        for target in links:
            resolved = (skill_file.parent / target).resolve()
            if not resolved.is_relative_to(skill_file.parent.resolve()):
                add(
                    "OAI-SKILL-003",
                    "error",
                    skill_file,
                    f"local reference escapes the Skill directory: {target!r}",
                    "official",
                )
            elif not resolved.exists():
                add(
                    "OAI-SKILL-003",
                    "error",
                    skill_file,
                    f"broken local reference: {target!r}",
                    "official",
                )

        reference_root = skill_file.parent / "references"
        if reference_root.is_dir():
            for reference in sorted(reference_root.rglob("*.md")):
                if reference.resolve() not in resolved_links:
                    add(
                        "ANT-SKILL-003",
                        "error",
                        reference,
                        "reference is not linked directly from SKILL.md",
                        "official",
                    )
                reference_text = reference.read_text(encoding="utf-8")
                nested = [target for target in _local_links(reference, reference_text) if target.endswith(".md")]
                if nested:
                    add(
                        "ANT-SKILL-003",
                        "error",
                        reference,
                        f"reference chains to another local Markdown file: {nested!r}",
                        "official",
                    )

        scripts_root = skill_file.parent / "scripts"
        if scripts_root.is_dir():
            for script in sorted(path for path in scripts_root.rglob("*") if path.is_file()):
                if script.resolve() not in resolved_links:
                    add(
                        "OAI-SKILL-003",
                        "error",
                        script,
                        "bundled script is not linked directly from SKILL.md",
                        "official",
                    )
                script_text = script.read_text(encoding="utf-8", errors="replace")
                if re.search(r"\b(?:curl|wget|requests\.|urllib\.|socket\.|httpx\.)", script_text):
                    add(
                        "ANT-SEC-001",
                        "warning",
                        script,
                        "script contains network-capable code; verify it is necessary and bounded",
                        "official",
                    )

        agent_file = skill_file.parent / "agents" / "openai.yaml"
        if agent_file.is_file():
            agent_text = agent_file.read_text(encoding="utf-8")
            if f"${name}" not in agent_text:
                add(
                    "OAI-SKILL-003",
                    "error",
                    agent_file,
                    "default_prompt must explicitly mention the Skill",
                    "official",
                )

        for match in WINDOWS_PATH.finditer(text):
            add(
                "ANT-SKILL-004",
                "error",
                skill_file,
                "use forward-slash paths in Skill instructions",
                "official",
                _line_number(text, match.start()),
            )

        tool_sections = "\n".join(TOOL_SECTION.findall(text))
        mentioned_tools = {
            token
            for token in INLINE_CODE.findall(tool_sections)
            if token.startswith(TOOL_PREFIXES)
        }
        if public_tools is not None:
            for tool in sorted(mentioned_tools - public_tools):
                offset = text.find(f"`{tool}`")
                add(
                    "QD-CONTRACT-001",
                    "error",
                    skill_file,
                    f"MCP action is absent from the supplied Auth public contract: {tool}",
                    "backend_contract",
                    _line_number(text, offset),
                )

    markdown_paths = [repo_root / "README.md", plugin_root / "README.md"]
    markdown_paths.extend(skill_files)
    markdown_paths.extend(sorted(skills_root.glob("*/references/*.md")))
    for path in markdown_paths:
        if not path.is_file() or not in_scope(path):
            continue
        text = path.read_text(encoding="utf-8")
        match = CJK.search(text)
        if match:
            add(
                "QD-PRODUCT-001",
                "error",
                path,
                "public package prose contains CJK text; keep source instructions in consistent English",
                "quandora_policy",
                _line_number(text, match.start()),
            )
        for pattern in RELEASE_HISTORY_PATTERNS:
            match = pattern.search(text)
            if match:
                add(
                    "QD-PRODUCT-002",
                    "error",
                    path,
                    "public package prose contains release or implementation history",
                    "quandora_policy",
                    _line_number(text, match.start()),
                )
                break
        match = re.search(r"^Bundled plugin version:\s*\S+\s*$", text, re.MULTILINE)
        if match:
            add(
                "QD-PRODUCT-003",
                "error",
                path,
                "Skill instructions duplicate the package version",
                "quandora_policy",
                _line_number(text, match.start()),
            )

    if public_tools is not None and mode == "full":
        all_skill_text = "\n".join(path.read_text(encoding="utf-8") for path in skill_files)
        mentioned = {
            token
            for token in INLINE_CODE.findall(all_skill_text)
            if token in public_tools
        }
        for tool in sorted(public_tools - mentioned):
            add(
                "QD-CONTRACT-001",
                "warning",
                plugin_root / "skills",
                f"public MCP action is not named by any packaged Skill: {tool}",
                "backend_contract",
            )

    return sorted(
        findings,
        key=lambda item: (item.severity != "error", item.path, item.line or 0, item.rule_id),
    )


def _render_text(findings: Iterable[Finding]) -> None:
    findings = list(findings)
    if not findings:
        print("Quandora plugin audit passed with no findings.")
        return
    for finding in findings:
        location = finding.path
        if finding.line is not None:
            location = f"{location}:{finding.line}"
        print(
            f"{finding.severity.upper()} {finding.rule_id} [{finding.source_class}] "
            f"{location}: {finding.message}"
        )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--plugin-root", type=Path, default=Path("plugins/quandora-staging"))
    parser.add_argument("--mode", choices=("changed", "full"), default="changed")
    parser.add_argument("--base-ref")
    parser.add_argument("--public-contract", type=Path)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument("--fail-on", choices=("error", "warning", "never"), default="error")
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    plugin_root = args.plugin_root
    if not plugin_root.is_absolute():
        plugin_root = repo_root / plugin_root
    if args.mode == "changed" and not args.base_ref:
        parser.error("--base-ref is required in changed mode")

    try:
        changed = _changed_paths(repo_root, args.base_ref) if args.mode == "changed" else None
        tools = _contract_tools(args.public_contract)
        findings = audit_repository(
            repo_root,
            plugin_root,
            mode=args.mode,
            changed_paths=changed,
            public_tools=tools,
        )
    except ValueError as exc:
        print(f"ERROR QD-AUDIT-INPUT [audit] {exc}", file=sys.stderr)
        return 2

    if args.format == "json":
        print(json.dumps([asdict(item) for item in findings], indent=2, ensure_ascii=False))
    else:
        _render_text(findings)

    if args.fail_on == "never":
        return 0
    if args.fail_on == "warning":
        return 1 if findings else 0
    return 1 if any(item.severity == "error" for item in findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
