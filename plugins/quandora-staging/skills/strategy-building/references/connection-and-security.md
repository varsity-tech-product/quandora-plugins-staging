# Connection and Security

Load this reference only when a required canonical Quandora Staging action is unavailable or the
host reports terminal authorization failure.

OAuth and credentials are host-managed. Never inspect, print, copy, store, or ask for API keys,
bearer/access/refresh tokens, authorization codes, PKCE verifiers, service tokens, or pasted
credentials. Do not reauthorize merely because an access token expired while the host is
refreshing.

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

Do not use raw HTTP, undocumented local helper scripts, internal service paths, or credential
paste. The package's two documented Claude Desktop Code launchers are a narrow
installation/authorization exception; they are not Strategy-workflow tools and never bypass the
plugin-managed MCP identity. The only direct HTTP exception is immediate consumption of the opaque
short-lived URL returned by `create_strategy_result_bundle_download`; never construct, modify,
persist, reuse, or summarize it.
