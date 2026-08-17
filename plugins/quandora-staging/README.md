# Quandora Staging

Quandora Staging is the public staging plugin package for pre-release Quandora agent workflow testing. It includes Factor Mining, Strategy Building, and Paper Trading skills, points to staging services, and is not the production plugin.

## What Factor Mining Does

Quandora Staging Factor Mining helps an agent:

1. Connect to the user's staging Quandora account through the host's MCP authorization flow.
2. List public factor-mining tasks or create a custom factor session.
3. Generate a valid `plugin.py` in the local workspace when file writes are available.
4. Submit the factor source inline to Quandora Staging.
5. Wait for the backtest, retrieve one verified FM-owned Result Bundle ZIP, and summarize the result.
6. Retain the verified ZIP as the canonical completed local result without automatic extraction.

## Result Files

When the host supports local files, Factor Mining saves the verified FM-owned archive as:

```text
/Users/richsion/Quandora staging result/factor/<factor_slug>.zip
```

The factor slug is derived from the current user-facing factor name. The remote filename remains
transport metadata, and the bundle's runtime manifest is authoritative for included, pending, and
omitted items. A readable partial remains downloadable. The verified ZIP is not automatically
extracted, deleted, or rebuilt.

Completed Strategy bundles use the dedicated Strategy subdirectory:

```text
/Users/richsion/Quandora staging result/strategy/<strategy_slug>.zip
```

The strategy slug is derived from the current user-facing submitted Strategy name.

## What Paper Trading Does

Quandora Staging Paper Trading helps an agent discover the current user's eligible sources and
prepare a bounded optimizer-backed source StrategyVersion from exact factor/version/job references.
It submits and monitors the source backtest with the Paper-owned source detail, obtains explicit
Paper submit/stop confirmation, and reads live current PnL, position history, fills, funding, equity
curves, and bounded strategy code. It also supports static independent-sleeve Strategy Portfolio
backtests and Paper runs. It does not expose production trading, universe overrides, Paper
archive/resume, or nonexistent parent aggregate positions/equity.

## Skills

```text
skills/
  factor-mining/
  paper-trading/
  strategy-building/
```

## CodeBuddy and the WorkBuddy China edition

The CodeBuddy-compatible plugin manifest registers all three skills and the plugin-managed `quandora-staging` remote HTTP MCP server. CodeBuddy and the WorkBuddy China edition handle the MCP connection and browser OAuth authorization natively. The package requires no local MCP process, Python, Node.js, API key, or credential-paste flow.

## Claude Desktop Code OAuth launchers

Claude Desktop Code Agents normally run commands with redirected input and output, while the official `claude mcp login` flow requires an interactive terminal. This plugin therefore ships two fixed-purpose launchers under `scripts/`:

```text
scripts/
  claude-mcp-login-macos.sh
  claude-mcp-login-windows.ps1
```

The macOS launcher uses the operating system's `/usr/bin/script` PTY. The Windows launcher uses Windows PowerShell 5.1 to start a native console. Both invoke only `plugin:quandora-staging:quandora-staging`, retain the remote MCP transport, avoid OAuth output logging, and require no Python, Node.js, or third-party terminal package. Browser identity and consent remain manual user actions.

The Windows path is statically validated; smoke-test it on Windows 10/11 x64 and Windows 11 ARM64 before promotion outside staging.

## Connection Recovery

If the `quandora-staging` connection is unavailable, update or reinstall the staging plugin, reconnect the plugin-managed Remote MCP server, and complete the host-native browser authorization flow again. The host owns OAuth and credentials; agents never request API keys, bearer tokens, authorization codes, access tokens, refresh tokens, PKCE verifiers, or pasted credentials.

## Paper Trading Release Order

Merged prerequisite Plugin 1.44 precedes this semantic superset. Plugin 1.46 must be published and
confirmed installable from every supported staging manifest before the Auth service advertises
`1.46`. PB and Auth Paper code deploys keep their independent Paper and versioned-source gates
closed and omit the eight Paper OAuth scopes during that interval. A later, separately auditable
staging rollout enables the gates, adds the scopes, and changes the Auth latest label together.
Production plugin metadata and production service configuration are outside this staging release
and remain unchanged.

Before publishing the staging package, run the repository-local static contract check:

```bash
python plugins/quandora-staging/scripts/validate-paper-trading.py
```

It verifies the nine release-version fields, all 27 Paper tool names, all eight documented scopes,
forbidden-tool absence, downstream safety reason text, required prompt-routing scenarios, and the
merged Plugin 1.44 Technical/materialization/Strategy-default behavior without calling a service or
performing a mutation.
