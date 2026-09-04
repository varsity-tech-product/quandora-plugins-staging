# Connection and Security

Load this reference only when Quandora Staging tools are unavailable, authentication is terminally
failed, or a host-specific reconnect is required.

Use only the configured `quandora-staging` MCP connection and never ask the user to paste secrets
into chat. If the host is refreshing an expired session, do not start a duplicate authorization
flow.

Use the host-native recovery path:

- Codex CLI/TUI: `codex mcp login quandora-staging`, complete browser authorization, then check for
  the required canonical action.
- Codex Desktop: authorize the plugin-provided Quandora Staging connector. Start a new chat after
  authorization; fully quit and reopen Desktop only if the tools remain unavailable.
- Kimi Code: `/mcp-config login plugin-quandora-staging:quandora-staging`, then start a new chat and
  check `/mcp`.
- Claude Code: open `/mcp`, authenticate `quandora-staging`, then start a new chat.
- Claude Desktop: add a Connector named `quandora-staging` with
  `https://mcp-staging.varsity.lol/quant`, authorize it, then start a new chat.
- CodeBuddy/WorkBuddy: update or reinstall the plugin, reconnect its managed Remote MCP server,
  finish browser authorization, then start a new chat.

The package's two documented Claude Desktop Code launchers are authorization-only; they are not
business-workflow tools. The sole direct HTTP exception is immediate consumption of an unmodified,
short-lived Result Bundle URL returned by the canonical bundle-ticket action. Never construct,
persist, log, reuse, or summarize that URL.
