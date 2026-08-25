# Quandora Staging

Quandora Staging is the public staging plugin package for pre-release Quandora agent workflow testing. It includes Factor Mining, Factor Analysis, Strategy Building, Strategy Analysis, and Paper Trading skills, points to staging services, and is not the production plugin.

## What Factor Mining Does

Quandora Staging Factor Mining helps an agent:

1. Connect to the user's staging Quandora account through the host's MCP authorization flow.
2. List public factor-mining tasks or create a custom factor session.
3. Generate a valid `plugin.py` in the local workspace when file writes are available.
4. Submit the factor source inline to Quandora Staging.
5. Wait for the backtest, retrieve one verified FM-owned Result Bundle ZIP, and summarize the result.
6. Retain the verified ZIP as the canonical completed local result without automatic extraction.

## Result Files

When the host supports local files, Factor Mining saves the verified FM-owned archive at a
user-requested destination or, by default, relative to the active workspace:

```text
quandora-results/factor/<factor_slug>.zip
```

The factor slug is derived from the current user-facing factor name. The remote filename remains
transport metadata, and the bundle's runtime manifest is authoritative for included, pending, and
omitted items. A readable partial remains downloadable. The verified ZIP is not automatically
extracted, deleted, or rebuilt.

Completed Strategy bundles use the dedicated Strategy subdirectory:

```text
quandora-results/strategy/<strategy_slug>.zip
```

The strategy slug is derived from the current user-facing submitted Strategy name.

## Package Validation

Run the database-free package contract before review:

```text
python3 plugins/quandora-staging/scripts/check-package.py
```

The check keeps manifest and bundled Skill versions aligned, limits Codex default prompts, and
rejects routine version probes, workstation-specific paths, and stale global bundle limits.

## What Analysis Does

Factor Analysis and Strategy Analysis read owner-scoped server-persisted evidence, diagnose
product-safe metrics and charts, separate observations from inference, and propose controlled
experiments. Strategy Analysis pairs the Product Backend run snapshot with retained artifacts and
bounded six-chart data and can assess Paper readiness. Factor Analysis reads the server Factor Card,
chart data, and inert job-linked source when needed. Neither analysis skill submits or mutates a run.

## What Paper Trading Does

Quandora Staging Paper Trading helps an agent discover the current user's eligible sources and
prepare a bounded ordinary source StrategyVersion from exact factor/version/job references.
It submits and monitors the source backtest with the Paper-owned source detail, obtains explicit
Paper submit/stop confirmation, and reads live current PnL, position history, fills, funding, equity
curves, and bounded strategy code. It also supports static independent-sleeve Strategy Portfolio
backtests and Paper runs. It does not expose production trading, universe overrides, Paper
archive/resume, or nonexistent parent aggregate positions/equity.

## Skills

```text
skills/
  factor-analysis/
  factor-mining/
  paper-trading/
  strategy-analysis/
  strategy-building/
```

## CodeBuddy and the WorkBuddy China edition

The CodeBuddy-compatible plugin manifest registers all five skills and the plugin-managed `quandora-staging` remote HTTP MCP server. CodeBuddy and the WorkBuddy China edition handle the MCP connection and browser OAuth authorization natively. MCP setup and analysis require no local process, Python, Node.js, API key, credential-paste flow, or local Result Bundle inspection.

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

## Release Order

Plugin 1.50 adds authoritative Official/Mine source labels to eligible Strategy factor lists on
merged Plugin 1.49. Deploy the Product Backend projection and Auth public MCP normalization before
publishing Plugin 1.50. After the unique staging Plugin 1.50 artifact is confirmed installable from
every supported manifest, advertise `1.50` through the separate Auth staging version configuration.
No new tool or OAuth scope is required. Factor Mining runtime, production plugin metadata, and
production service configuration remain unchanged.

Plugin 1.51 preserves the five Plugin 1.50 skills, uses the bounded Paper/version-check MCP names,
and consumes nullable owner-scoped Paper strategy names with a bounded mixed-rollout fallback.
Deploy FM, Auth, and PB in that order before publishing Plugin 1.51. Keep the Auth latest-version
label unchanged until the 1.51 artifact is confirmed installable from every supported manifest,
then advance the label through a separate reviewed staging configuration change. OAuth scopes and
production remain unchanged.

Plugin 1.52 keeps the same tools and scopes while aligning Agent decisions with the deployed FM/PB
contracts: terminal retryability creates a new run rather than reviving a failed one, Paper
position history contains only closed net-position lifecycles, and Official-factor Strategy sources
use exact admission triples through top-level `factor_references`. No backend or deployment change
is part of this plugin release.
