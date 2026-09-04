# Connection and Security

Load this reference only when a required canonical Quandora Staging action is unavailable or the
host reports terminal authorization failure.

Use only the configured `quandora-staging` MCP connection and never ask the user to paste secrets
into chat. If the host is refreshing an expired session, do not start a duplicate authorization
flow.

Use only the host-native reconnect path:

- Codex CLI/TUI: `codex mcp login quandora-staging`.
- Codex Desktop: authorize the plugin connector, start a new chat, and fully restart Desktop only
  if tools remain unavailable.
- Kimi Code: `/mcp-config login plugin-quandora-staging:quandora-staging`, then start a new chat.
- Claude Code: authenticate `quandora-staging` from `/mcp`, then start a new chat.
- Claude Desktop: add the `quandora-staging` Connector at
  `https://mcp-staging.varsity.lol/quant`, authorize it, then start a new chat.
- CodeBuddy/WorkBuddy: update or reinstall the plugin, reconnect its managed MCP server, finish
  browser authorization, then start a new chat.

The package's two documented Claude Desktop Code launchers are authorization-only; they are not
Strategy-workflow tools. The sole direct HTTP exception is immediate consumption of the opaque
short-lived URL returned by `create_strategy_result_bundle_download`; never construct, modify,
persist, reuse, or summarize it.
