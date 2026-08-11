# Quandora Staging

Quandora Staging is the public staging plugin package for pre-release Quandora agent workflow testing. It includes Factor Mining and Strategy Building skills, points to staging services, and is not the production plugin.

## What Factor Mining Does

Quandora Staging Factor Mining helps an agent:

1. Connect to the user's staging Quandora account through the host's MCP authorization flow.
2. List public factor-mining tasks or create a custom factor session.
3. Generate a valid `plugin.py` in the local workspace when file writes are available.
4. Submit the factor source inline to Quandora Staging.
5. Wait for the backtest, retrieve one verified FM-owned Result Bundle ZIP, and summarize the result.
6. Save the local working files and returned results together.

## Result Files

When the host supports local files, Factor Mining archives each run under:

```text
Quandora staging result/factor-mining/aggressive_flow_exhaustion_reversal/
```

The result directory is named from the factor slug, preferably the generated `FACTOR_TYPE`, and contains one verified FM-owned Result Bundle ZIP. The bundle's safe manifest is authoritative for its canonical JSON, PNG, parquet, partial, and omitted items. The agent prints the result folder and one verified ZIP path after each run.

## Skills

```text
skills/
  factor-mining/
  strategy-building/
```

## CodeBuddy and the WorkBuddy China edition

The CodeBuddy-compatible plugin manifest registers both skills and the plugin-managed `quandora-staging` remote HTTP MCP server. CodeBuddy and the WorkBuddy China edition handle the MCP connection and browser OAuth authorization natively. The package requires no local MCP process, Python, Node.js, API key, or credential-paste flow.

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
