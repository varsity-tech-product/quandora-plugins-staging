<p align="center">
  <img src="assets/banner.png" alt="Quandora" width="100%">
</p>

# Quandora Staging Plugins

<p align="center">
  <a href="https://quandora.ai"><img src="https://img.shields.io/badge/Built%20by-Quandora-F28C00?style=flat" alt="Built by Quandora"></a>
  <a href="https://discord.com/invite/9WshZMnjGE"><img src="https://img.shields.io/badge/Join-Discord-5865F2?style=flat&logo=discord&logoColor=white" alt="Join Discord"></a>
  <a href="https://x.com/quandora_labs"><img src="https://img.shields.io/badge/Follow-%40quandora__labs-000000?style=flat&logo=x&logoColor=white" alt="Follow on X"></a>
</p>

Quandora Staging is the public pre-release channel for Quandora agent workflows. It connects
supported hosts to Quandora's staging MCP server and must not be used for production research or
live-money trading. Production users should install
[`varsity-tech-product/quandora-plugins`](https://github.com/varsity-tech-product/quandora-plugins).

## Included workflows

| Skill | User goal |
| --- | --- |
| Factor Mining | Create, validate, backtest, continue, and export one Factor Mining result. |
| Factor Analysis | Diagnose an existing owned or active-official Factor result without submitting changes. |
| Strategy Building | Select eligible factors and create, revise, backtest, rerun, or export one Strategy. |
| Strategy Portfolio | Compose exact StrategyVersions and evaluate exact completed source runs. |
| Strategy Analysis | Diagnose one Strategy result and propose controlled experiments. |
| Paper Trading | Start, monitor, inspect, or terminally stop simulated execution after confirmation. |

The plugin exposes the same six Skill directories to each supported host. Authentication,
authorization, tool schemas, live data, and mutations remain server-owned. Skills provide routing,
safe sequencing, confirmation points, and result interpretation.

## Install

The package name is `quandora-staging@quandora-staging`.

### Codex

In Codex Desktop, add the marketplace source
`varsity-tech-product/quandora-plugins-staging`, leave Git ref blank, and install
`quandora-staging@quandora-staging`.

For Codex CLI:

```bash
codex plugin marketplace add varsity-tech-product/quandora-plugins-staging
codex plugin add quandora-staging@quandora-staging
```

If authorization does not open automatically:

```bash
codex mcp login quandora-staging
```

Start a new chat after installation or authorization.

### Claude

For Claude Code:

```bash
claude plugin marketplace add varsity-tech-product/quandora-plugins-staging
claude plugin install quandora-staging@quandora-staging
claude mcp login plugin:quandora-staging:quandora-staging
```

For the Claude Desktop Chat connector, add and authorize:

```text
Name: quandora-staging
URL: https://mcp-staging.varsity.lol/quant
```

These are separate host workflows. Do not create a duplicate MCP entry when the plugin-managed
connection is already present.

### Cursor Desktop

In a new Agent chat:

```text
/add-plugin quandora-staging@https://github.com/varsity-tech-product/quandora-plugins-staging
```

Authorize the plugin-provided `quandora-staging` connection in the browser, then start a new chat.

### CodeBuddy and WorkBuddy

Install `quandora-staging@quandora-staging` from this marketplace using the host's plugin or
custom-MCP interface. Reconnect the plugin-managed remote MCP server, complete the host-native
browser authorization flow, and start a new chat. No local MCP server or credential-paste flow is
required.

### Kimi Code CLI

```text
/plugins install https://github.com/varsity-tech-product/quandora-plugins-staging
/plugins info quandora-staging
/plugins reload
/mcp-config login plugin-quandora-staging:quandora-staging
/mcp
```

Complete browser authorization and start a new session.

## Use

Ask naturally or invoke a Skill explicitly when the host supports Skill commands:

```text
/quandora-staging:factor-mining show public factor tasks
/quandora-staging:factor-analysis analyze my latest factor result
/quandora-staging:strategy-building list eligible factors matching momentum
/quandora-staging:strategy-portfolio combine these StrategyVersions with 60/40 weights
/quandora-staging:strategy-analysis analyze my latest completed strategy
/quandora-staging:paper-trading show my current paper PnL
```

Mutating workflows show the exact safe request and require confirmation where the corresponding
Skill specifies it. A timeout or ambiguous response is never treated as permission to create a
replacement command.

## Result files

When the host supports local files and the user requests or reaches the relevant export step,
verified Result Bundles are saved relative to the active workspace:

```text
Quandora staging result/factor/<factor_slug>.zip
Quandora staging result/strategy/<strategy_slug>.zip
```

The verified archive is retained without automatic extraction or reconstruction. Server-returned
metadata and manifests remain authoritative for readiness, contents, omissions, and integrity.

## Connection recovery and security

If required tools are unavailable, update or reinstall the plugin, reconnect the existing
`quandora-staging` MCP server, complete the host-native browser authorization flow, and start a new
chat. The host owns OAuth and credentials. Never paste API keys, bearer tokens, authorization
codes, access or refresh tokens, PKCE verifiers, or service credentials into chat or local helper
scripts.

## License

Licensed under the Apache License 2.0. See [LICENSE](LICENSE).
