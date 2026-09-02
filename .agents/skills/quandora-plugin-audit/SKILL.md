---
name: quandora-plugin-audit
description: Audits the Quandora staging plugin package against current OpenAI and Anthropic Skill guidance, Quandora backend contracts, package hygiene, and observed Agent behavior. Use for plugin release reviews, changed-file checks, or investigations of Skill quality and drift; do not use to operate Quandora business workflows.
---

# Quandora Plugin Audit

Audit the repository-owned staging plugin without changing product behavior unless the user
explicitly asks for remediation. Separate official host requirements, Quandora product policy,
backend-contract facts, and heuristic review findings.

## Choose The Audit Mode

- Use `changed` for an ordinary pull request. Inspect the complete affected Skill or manifest, but
  block only regressions introduced by the diff.
- Use `full` before a plugin release or when the user asks for a comprehensive review. Inspect the
  entire package and require every error-level invariant to pass.

Read [Official authoring rules](references/official-authoring-rules.md) before changing audit
criteria. Read [Quandora sources of truth](references/quandora-sources.md) before making any claim
about tools, schemas, permissions, or runtime behavior. Read [Behavior evaluations](references/behavior-evaluations.md)
when the audit includes Agent activation, tool selection, confirmation, or recovery behavior.

## Workflow

1. Invoke `$quandora-development` and complete its refresh before evaluating current backend or
   cross-repository contract behavior.
2. Resolve the plugin repository, plugin root, base ref, and audit mode. Default to the repository
   containing this Skill and `plugins/quandora-staging`.
3. Run the deterministic audit:

   ```bash
   python3 .agents/skills/quandora-plugin-audit/scripts/audit_plugin.py \
     --repo-root . \
     --plugin-root plugins/quandora-staging \
     --mode full
   ```

   For a pull request, replace `full` with `changed` and add `--base-ref <base-sha>`. When an Auth
   checkout is available, add
   `--public-contract <auth-root>/contracts/public-mcp-contract.v1.json`.
4. Run the repository's existing package validator. Treat it as the authority for Quandora's
   exact manifest/version/tool-ownership invariants; do not duplicate or weaken those checks in
   this Skill.
5. Review every affected `SKILL.md` and its directly linked references semantically. Static matches
   identify candidates; they do not prove that wording is clear, routing is correct, or an example
   is safe.
6. For a full/release audit, execute fresh Codex and Claude behavior evaluations using a safe fake
   MCP server for mutation cases. Use live staging only for explicitly authorized, bounded reads.
7. Report findings with rule ID, source class, file/line evidence, impact, and the smallest repair.
   Record an explicit waiver with owner and rationale when a Quandora policy exception is accepted.

## Required Review Outcomes

The audit must establish:

- the package contains only installable product assets and intentionally referenced support files;
- each Skill has a focused trigger, clear non-trigger boundary, consistent English source text,
  direct references, and no release-history or implementation-changelog prose;
- every mentioned MCP action exists in the current Auth public contract and matches PB behavior;
- credentials, opaque identities, pagination tokens, confirmation, idempotency, and ambiguous
  outcomes remain fail-closed;
- representative direct, indirect, incomplete, negative, and recovery prompts were evaluated on
  every intended host/model family;
- expected/reference traces are never presented as observed Host evidence.

## Boundaries

- Do not modify Factor Mining. If a correct repair requires an FM contract or runtime change, stop
  and report the owner boundary.
- Do not fetch, print, or persist credentials, bearer tokens, opaque business identifiers, or live
  response bodies in audit artifacts.
- Do not run live mutations as an automated audit shortcut. Use a local fake MCP boundary unless
  the user explicitly authorizes a disposable staging mutation.
- Do not copy official documentation into public Skills. Keep source URLs and verification dates in
  this internal audit Skill.
- Do not fail a pull request on a heuristic alone. Promote a heuristic to an error only when it has
  an explicit official or Quandora policy rule and a deterministic false-positive boundary.

## Output

Lead with pass/fail and release readiness. Group actionable findings by severity, then list:

- static checks executed and their mode;
- backend contract refs used;
- Host/model observations completed or still missing;
- waivers and unresolved ownership blockers.

Do not report a full release pass when only changed-file checks or reviewed reference traces ran.

When maintaining this auditor, run
`python3 .agents/skills/quandora-plugin-audit/scripts/test_audit_plugin.py` and the official Skill
validator before committing.
