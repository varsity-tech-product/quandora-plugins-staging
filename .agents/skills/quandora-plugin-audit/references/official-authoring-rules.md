# Official Authoring Rules

Last verified: 2026-09-02

This file records review criteria, not copied product documentation. Re-verify the linked primary
sources before changing a rule or using it to block a release.

## Sources

- OpenAI, [Build skills](https://developers.openai.com/plugins/build/skills)
- OpenAI, [Package your plugin](https://developers.openai.com/plugins/build/plugins)
- OpenAI, [Build skills for Codex](https://developers.openai.com/codex/skills)
- OpenAI, [Connect and test your plugin](https://developers.openai.com/plugins/deploy/connect-chatgpt)
- Anthropic, [Agent Skills](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)
- Anthropic, [Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)

## Blocking Official Rules

| Rule | Requirement | Source class |
| --- | --- | --- |
| `OAI-SKILL-001` | Every Skill is a directory with a `SKILL.md`; frontmatter includes a focused `name` and discriminating `description`. | OpenAI |
| `OAI-SKILL-002` | The description states what the Skill does and when it applies; detailed workflow and safety rules stay in the body. | OpenAI |
| `OAI-SKILL-003` | Supporting files are added only for a concrete need and are linked from `SKILL.md` with instructions for when to read or run them. | OpenAI |
| `OAI-PLUGIN-001` | `.codex-plugin/plugin.json` is the manifest entry point; component paths are relative, begin with `./`, and remain inside the plugin root. | OpenAI |
| `OAI-PLUGIN-002` | Product components live at the plugin root: `skills/`, `hooks/`, `assets/`, `.mcp.json`, and `.app.json`; only `plugin.json` belongs in `.codex-plugin/`. | OpenAI |
| `ANT-SKILL-001` | Skill names use lowercase letters, digits, and hyphens, are at most 64 characters, and descriptions are non-empty and at most 1,024 characters. | Anthropic |
| `ANT-SKILL-002` | `SKILL.md` stays concise; split substantial conditional detail before 500 body lines. | Anthropic |
| `ANT-SKILL-003` | Keep reference traversal one level deep from `SKILL.md`; longer references need visible structure. | Anthropic |
| `ANT-SKILL-004` | Use consistent terminology and forward-slash paths; avoid current-date branches and other time-sensitive operational prose. | Anthropic |
| `ANT-SEC-001` | Audit every bundled file and flag unexpected network, filesystem, command, or data-exposure behavior that does not match the Skill purpose. | Anthropic |

## Testing Rules

- OpenAI requires representative direct, indirect, incomplete, negative, and edge-case prompts.
- For MCP-backed plugins, record selected tools, arguments, results, errors, and confirmation
  behavior. Re-run affected cases after tool metadata or Skill changes.
- Test the installed package in a fresh conversation; source-tree validation alone does not prove
  installed-path resolution or activation.
- Anthropic recommends evaluation-driven iteration, real usage, and every model family intended
  for deployment. A hand-authored expected trace is a useful oracle, not observed evidence.

## Quandora Product Rules

These are deliberate product-quality policies, not claims about the official file format:

| Rule | Requirement |
| --- | --- |
| `QD-PRODUCT-001` | Public plugin source prose is professional English; answer-language adaptation belongs in workflow instructions rather than mixed-language trigger examples. |
| `QD-PRODUCT-002` | Public Skills and package README files describe current user behavior only; release notes, PR sequencing, implementation chronology, and version-by-version migration narrative stay outside the installable package. |
| `QD-PRODUCT-003` | Skill instructions do not duplicate the package version. Version authority belongs to manifests and the server diagnostic surface. |
| `QD-PRODUCT-004` | Discovery descriptions lead with the capability, then state concrete activation and non-activation boundaries. |
| `QD-PACKAGE-001` | The installable plugin contains only documented components and files with a current runtime or user-support purpose. Root-level helper scripts are forbidden; host-specific MCP files are allowed only when an active host manifest references them. |
| `QD-CONTRACT-001` | Every named MCP action must exist in the current Auth public contract and have compatible PB behavior. Static name parity does not prove semantic parity. |

An exception to a Quandora rule must be explicit, owned, and documented in the audit result. Do not
silently weaken the rule to make an existing package pass.
