# Quandora Staging

This package contains six user-facing Skills and one authenticated staging MCP connection. It is
for pre-release Quandora workflow testing, not production research or live-money trading.

## Skills

| Skill | Owns | Does not own |
| --- | --- | --- |
| `factor-mining` | Factor creation, validation, backtests, continuation, history, and export | Deep result diagnosis or the Strategy eligible-factor pool |
| `factor-analysis` | Read-only diagnosis of owned or active-official Factor evidence | Factor submission or automatic optimization |
| `strategy-building` | One Strategy's factor selection, definition, backtests, reruns, and export | Multi-Strategy composition or Paper execution |
| `strategy-portfolio` | Multi-Strategy definition, exact source selection, evaluation, and result reads | Single-Strategy creation or Paper execution |
| `strategy-analysis` | Read-only diagnosis of one Strategy result | Strategy mutation or Paper execution |
| `paper-trading` | Confirmed simulated execution and monitoring | Strategy or Portfolio research creation |

Each Skill uses the minimum required MCP actions, preserves opaque identifiers and continuation
tokens exactly, and keeps observed evidence separate from inference. Tool schemas, authorization,
live defaults, and mutation authority remain server-owned.

## Connection

Supported hosts load the plugin's `quandora-staging` remote HTTP MCP declaration. Complete the
host-native browser authorization flow and start a new chat after installation or reconnection.
Do not create a local MCP server or paste credentials.

When a required action is unavailable, update or reinstall the plugin, reconnect the existing MCP
server, and retry only after the host reports a healthy authorized connection. Never bypass MCP
with raw internal HTTP requests.

### Claude Desktop Code authorization bridge

The plugin intentionally ships these two host-support assets:

```text
scripts/claude-mcp-login-macos.sh
scripts/claude-mcp-login-windows.ps1
```

They support the authorization step of the one-click Claude Desktop Code Agent installation flow,
where redirected command input/output cannot host the official interactive `claude mcp login`
prompt. Both launch only `plugin:quandora-staging:quandora-staging` in a native interactive
terminal, keep OAuth output out of status files, and require manual browser identity and consent.
They are not general shell utilities, local MCP servers, or credential helpers. Interactive Claude
Code users should use the direct host command instead.

## Search and pagination

Discovery actions use a user-provided name or keyword as `query`, exact public fields as
`filters`, and an empty search only for a browse or recent-items request. Continuation requests
must preserve the same query, filters, archive mode, and page size while copying the returned
opaque page token byte-for-byte.

## Result files

When local file writes are supported, verified Factor and Strategy bundles use these default
workspace-relative destinations:

```text
Quandora staging result/factor/<factor_slug>.zip
Quandora staging result/strategy/<strategy_slug>.zip
```

The validated Factor source's exact non-empty lowercase snake_case `FACTOR_TYPE` determines the
factor slug; it never silently falls back to a generic `factor` slug. The user-facing submitted
Strategy name determines the Strategy slug. The verified archive remains intact, and returned
metadata and manifests are authoritative for readiness, contents, omissions, and integrity.

## Safety boundary

- OAuth and credentials are host-managed and must never be requested, printed, copied, or stored.
- Mutations require the confirmation described by the owning Skill.
- An ambiguous response is not proof of failure and does not authorize a changed replacement.
- Paper Trading is simulated staging execution only; the package exposes no live-money workflow.
- User-facing answers follow the user's language while preserving tool names and schema fields
  exactly.
