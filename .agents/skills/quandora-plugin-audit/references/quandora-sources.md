# Quandora Sources Of Truth

Use `$quandora-development` before reading these sources so `origin/main` is current. Work from the
exact requested PR/ref when one is named; otherwise use `origin/main`.

## Plugin Package

- `.agents/plugins/marketplace.json` and host marketplace manifests: install routing.
- `plugins/quandora-staging/.codex-plugin/plugin.json`: Codex package metadata and component paths.
- Other host manifests under `plugins/quandora-staging/`: host-specific compatibility metadata.
- `plugins/quandora-staging/.mcp.json`: remote MCP connection authority.
- `plugins/quandora-staging/skills/*/SKILL.md`: activation, routing, workflow, safety, and output behavior.
- `.github/workflows/validate-plugin.yml` and `scripts/check-staging-plugin.py`: deterministic package policy.

Do not treat README release notes, an installed cache, or a prior audit as current package truth.

## Auth Public MCP

- `contracts/public-mcp-contract.v1.json`: generated public tool names, input/output schemas,
  annotations, scopes, and contract revision.
- `app/modules/remote_mcp/tool_metadata.py`, `tools.py`, and `contract.py`: executable tool metadata
  and contract generation.
- `contracts/mcp-agent-evals.v1.json`: reviewed behavior cases.
- `contracts/mcp-agent-eval-baseline.v1.json`: expected reference oracle only unless its evidence
  metadata explicitly records a real Host observation.
- `docs/remote-mcp-tools.md`: human-readable current surface.

## Product Backend

- `contracts/public-mcp-contract.v1.json`: consumer-side contract copy when present.
- `app/modules/remote_mcp/actions/`: action inputs, outputs, routing, and recovery behavior.
- `app/api/remote_mcp.py`: trusted Auth-to-PB request boundary.
- Focused `tests/test_remote_mcp_*.py`: executable behavior evidence.

Compare Auth and PB generated contracts byte-for-byte when both repositories claim the same public
surface. Resolve a mismatch before changing a Skill to match only one side.

## Factor Mining Boundary

Factor Mining owns provider/runtime behavior and protobuf contracts, but it is outside this audit's
write scope. Inspect its current proto, service code, and tests only when Auth/PB behavior cannot be
established without the provider contract. If the necessary repair belongs to FM, stop and report
the owner, exact contract gap, and downstream impact; do not patch FM.

## Evidence Precedence

1. Current executable code, generated contracts, schemas/protos, and focused tests.
2. Focused current architecture and interface documents.
3. Current PR/issue acceptance criteria and deployment evidence.
4. Broad README summaries and historical notes.

Observed staging behavior is evidence about a deployed revision. It is not authority to change a
contract, and it must be correlated to the deployed SHA before use.
