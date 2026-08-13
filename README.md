<p align="center">
  <img src="assets/banner.png" alt="Quandora" width="100%">
</p>

# Quandora Staging Plugins

<p align="center">
  <a href="https://quandora.ai"><img src="https://img.shields.io/badge/Built%20by-Quandora-F28C00?style=flat" alt="Built by Quandora"></a>
  <a href="https://discord.com/invite/9WshZMnjGE"><img src="https://img.shields.io/badge/Join-Discord-5865F2?style=flat&logo=discord&logoColor=white" alt="Join Discord"></a>
  <a href="https://x.com/quandora_labs"><img src="https://img.shields.io/badge/Follow-%40quandora__labs-000000?style=flat&logo=x&logoColor=white" alt="Follow on X"></a>
</p>

### Public staging plugin channel for Quandora agent integration testing.

This repository is for staging validation only. It points to Quandora staging services and should not be used for production workflows. Production users should install `varsity-tech-product/quandora-plugins`.

<table>
<tr><td><b>AI-Native Research Workflow</b></td><td>Run the full quant research loop directly from CLI, Codex, Claude Code, or Cursor Desktop: autonomous research, backtesting, strategy creation, and deployment-ready workflow.</td></tr>
<tr><td><b>Institutional Quant Infrastructure</b></td><td>Quandora provides end-to-end infrastructure for your agent: task cards, supported data, evaluation rails, and backtesting, while your agent focuses on writing Python factor logic.</td></tr>
<tr><td><b>Real Performance Evidence with Explanations</b></td><td>Get structured Factor and Strategy Reports with verdicts, metrics, risks, assumptions, and plain-English explanations.</td></tr>
<tr><td><b>Closed-Loop Learning</b></td><td>Agent-curated memory tracks iterations, failures, accepted factors, duplicates, and improvements to build a reusable factor library over time.</td></tr>
<tr><td><b>AI Mentor</b></td><td>Learn while you build through educational links, step-by-step workflow explanations, and clear reasoning behind each action.</td></tr>
</table>

<br>

## How It Works

```text
        +----------------------+
        | factor mining        |<----------------+
        +----------------------+                 |
                  |                              |
                  v                              |
        +----------------------+                 |
        | factor evaluation    |                 |
        +----------------------+                 |
                  |                              |
                  v                              |
        +----------------------+                 |
        | factor / strategy    |                 |
        | card                 |                 |
        +----------------------+                 |
                  |                              |
                  |                              |
                  |                              | user reviews decay
                  |                              | and chooses next step
                  |                              |
                  v                              |
        +----------------------+                 |
        | strategy             |                 |
        | construction         |                 |
        +----------------------+                 |
                  |                              |
                  v                              |
        +----------------------+                 |
        | strategy evaluation  |                 |
        +----------------------+                 |
                  |                              |
                  v                              |
        +----------------------+                 |
        | paper trading /      |-----------------+
        | monitoring           |
        +----------------------+
                  |
                  | stable
                  |
                  v
        +----------------------+
        | supervised           |
        | deployment           |
        +----------------------+
                  |
                  v
        +----------------------+
        | optional live        |
        | trading              |
        +----------------------+
```

<br>

## Agents

Each agent is named for the workflow stage it runs.

| Agent | What it does |
|---|---|
| **Factor Mining Agent** | Turns an alpha-mining task into Python factor logic, checks memory for duplicates, and prepares candidates for evaluation. |
| **Factor Evaluation Agent** | Submits factors to Quandora, tracks server-side validation and backtests, and summarizes pass/fail results. |
| **Factor / Strategy Card Agent** | Produces structured cards with formulas, metrics, risks, assumptions, verdicts, and plain-English explanations. |
| **Strategy Construction Agent** | Combines accepted factors into strategy candidates with portfolio logic, sizing rules, and risk constraints. |
| **Strategy Evaluation Agent** | Evaluates strategy performance, drawdown, turnover, cost viability, and robustness before monitoring. |
| **Paper Trading Monitor Agent** | Starts and monitors confirmed staging Paper runs, reads current and historical performance, and terminally stops a selected run only after user confirmation. It never changes strategies or restarts mining automatically. |
| **Deployment Supervisor Agent** | Keeps users in the loop for approvals, guardrails, deployment checks, and supervised rollout. |

<br>

Quandora Staging Plugins is the public marketplace for testing Quandora agent integrations before production release. The current package is:

```text
quandora-staging@quandora-staging
```

Quandora Staging Factor Mining lets local agents create `plugin.py`, submit it through the authenticated staging Quandora connection, run a backtest, and save one verified FM-owned Result Bundle ZIP in the local workspace.

Quandora Staging Paper Trading lets agents discover the user's eligible StrategyRun sources, start
and monitor single-strategy or static-sleeve Strategy Portfolio Paper runs after confirmation, read
current PnL and historical execution data, and terminally stop selected runs. It is staging-only and
does not place live-money trades.

## Install

### Codex

Codex Desktop:

```text
Source: varsity-tech-product/quandora-plugins-staging
Git ref: leave blank
Plugin: quandora-staging@quandora-staging
```

You can also ask Codex Desktop to install and connect Quandora for you:

```text
Install Quandora Staging from varsity-tech-product/quandora-plugins-staging, then connect Quandora Staging.
```

Codex may ask before running the Codex CLI setup commands. These commands install the Quandora Staging plugin into Codex, write Codex plugin/MCP configuration, and open Quandora staging OAuth. They do not grant Quandora access to your local files.

Codex CLI:

```bash
codex plugin marketplace add varsity-tech-product/quandora-plugins-staging
codex plugin add quandora-staging@quandora-staging
```

Authorize when prompted. If Codex does not open the authorization flow automatically, use:

```bash
codex mcp login quandora-staging
```

After installation or authorization, open a new chat. If Codex Desktop still does not expose Quandora Staging tools, fully quit and reopen Codex Desktop.

When a Quandora Staging connection is unavailable, update or reinstall the staging plugin, reconnect the `quandora-staging` Remote MCP server, and complete the host-native browser authorization flow again. OAuth and credentials remain host-managed: agents must never request API keys, bearer tokens, authorization codes, access tokens, refresh tokens, PKCE verifiers, or pasted credentials.

### Claude

Claude Desktop Code supports an Agent-readable one-sentence installation guide. Publish and verify that guide before advertising its URL. The planned hosted request, once `https://quandora.ai/agent/claude` returns the reviewed plain text successfully, is:

```text
Read https://quandora.ai/agent/claude completely, then install and authorize Quandora Staging for me. I will complete the single browser Authenticate or Allow action when it opens.
```

The guide tells the Desktop Agent to install the exact staging marketplace/plugin and launch its remote MCP OAuth flow. The plugin includes narrowly scoped native launchers because Desktop Agent commands do not normally have an interactive TTY: macOS uses the built-in `/usr/bin/script`, while Windows uses Windows PowerShell 5.1 to create a native console. This is a Quandora compatibility bridge around the official Claude login command, not an Anthropic-guaranteed Desktop automation API. Neither path requires Python, Node.js, Homebrew, PowerShell 7, Windows Terminal, or a local MCP server. The user keeps control of browser sign-in, MFA, and consent; normal Claude permission prompts and enterprise policy still apply.

Claude Code in an interactive terminal:

```bash
claude plugin marketplace add varsity-tech-product/quandora-plugins-staging
claude plugin install quandora-staging@quandora-staging
claude mcp login plugin:quandora-staging:quandora-staging
```

The bare `claude mcp login` command above is for a real interactive terminal/TUI. A Claude Desktop Code Agent must use the installed platform launcher described in the agent guide instead of running the bare command in its redirected command environment.

Claude Desktop's normal Chat tab is a separate Connector workflow and cannot install or load this local Claude Code plugin. If you intentionally want the Chat-tab Connector instead, add and connect it manually:

```text
Name: quandora-staging
URL: https://mcp-staging.varsity.lol/quant
```

Use Settings -> Connectors, add the Connector above, click Connect, authorize Quandora Staging in the browser, then start a new chat.

If an older Claude Code client does not provide `claude mcp login`, update Claude Desktop through its official updater. If the command remains unavailable, use the exact staging **Authenticate** control; do not install a second CLI or create a duplicate MCP entry.

Claude Desktop can use the connected Quandora Staging tools in chat, but local result-folder archiving is only guaranteed in local agent environments such as Claude Code and Codex. Claude Desktop's built-in file creation uses Claude's sandbox and may provide downloadable files rather than writing directly to a chosen local folder.

Factor Mining chart downloads use returned server `source_name` values for API calls and save local PNGs to returned `standard_local_path` values.

### Cursor Desktop

In a new Cursor Desktop Agent chat, enter the complete host command:

```text
/add-plugin quandora-staging@https://github.com/varsity-tech-product/quandora-plugins-staging
```

After Cursor Desktop installs the plugin, authenticate the plugin-provided `quandora-staging` remote MCP server and complete Quandora Staging authorization in the browser. Then start a new Agent chat before invoking the Factor Mining, Strategy Building, or Paper Trading skill.

### CodeBuddy CLI

CodeBuddy CLI can install and connect Quandora Staging through its official plugin manager. First check whether `codebuddy` is available and install the official standalone CLI when it is absent.

macOS and Linux:

```bash
curl -fsSL https://www.codebuddy.cn/cli/install.sh | bash
export PATH="$HOME/.local/bin:$PATH"
```

Windows PowerShell:

```powershell
irm https://www.codebuddy.cn/cli/install.ps1 | iex
$env:Path = "$env:USERPROFILE\AppData\Local\codebuddy\bin;$env:Path"
```

The Agent then uses the non-interactive plugin manager:

```bash
codebuddy plugin marketplace add varsity-tech-product/quandora-plugins-staging --name quandora-staging
codebuddy plugin install quandora-staging@quandora-staging --scope user
codebuddy plugin list --json
```

Quandora Staging uses the plugin-provided remote HTTP MCP server. CodeBuddy CLI opens its native authorization flow when the server connects; the user reviews the browser page and completes the **Authenticate**, **Authorize**, or **Allow** action. No Python, Node.js, local MCP server, or Quandora API key is required.

### WorkBuddy China edition

The WorkBuddy China edition consumes the CodeBuddy-compatible marketplace and plugin manifests together with the plugin-managed `quandora-staging` remote HTTP MCP declaration. Install or update the staging plugin through its plugin or custom-MCP interface, reconnect it, complete the host-native browser authorization flow, and start a new chat. Do not create a local MCP server or paste credentials.

### Kimi Code CLI

In Kimi Code CLI, install the staging plugin directly from GitHub:

```text
/plugins install https://github.com/varsity-tech-product/quandora-plugins-staging
```

Confirm that you trust the third-party source, then inspect the installation and reload plugins:

```text
/plugins info quandora-staging
/plugins reload
```

Start a new session, authorize the plugin-provided staging MCP server, and verify its connection:

```text
/mcp-config login plugin-quandora-staging:quandora-staging
/mcp
```

Complete Quandora Staging authorization in the browser when prompted. After authorization, start a new session before invoking the Factor Mining, Strategy Building, or Paper Trading skill.

## Use Factor Mining

Use the skill command when available:

```text
/quandora-staging:factor-mining show public tasks
```

You can also ask naturally:

```text
show public tasks.
mine a factor with custom idea
```

When the host supports local files, the verified FM-owned archive is saved with a local name derived
from the current user-facing factor name:

```text
Quandora staging result/<factor_slug>.zip
```

The remote filename remains transport metadata. The verified ZIP is retained as the canonical local
output and is not automatically extracted, deleted, or rebuilt. A readable partial ZIP remains
downloadable; its runtime manifest is authoritative for the exact included, pending, and omitted
items.

## Use Strategy Building

Use the skill command when available:

```text
/quandora-staging:strategy-building list available factors
/quandora-staging:strategy-building help me build a strategy
```

You can also ask naturally:

```text
list available factors.
help me build a strategy.
```

When a completed Strategy Result Bundle is saved locally, its path is derived from the current
user-facing submitted Strategy name:

```text
Quandora staging result/<strategy_slug>.zip
```

The verified FM-owned Strategy ZIP is retained without automatic extraction or reconstruction.

## Use Paper Trading

Use the skill command when available:

```text
/quandora-staging:paper-trading start a paper run
/quandora-staging:paper-trading show my current paper PnL
```

You can also ask naturally:

```text
start paper trading from one of my eligible strategy runs.
show the 30D paper equity curve.
stop my paper run.
```

The skill lists owner-scoped sources when needed and asks for explicit confirmation before submit
or terminal stop. Lifecycle monitoring uses Paper detail rather than repeatedly collecting the
live portfolio. Strategy Portfolio Paper is presented as ordered, static independent sleeves; no
parent aggregate position or parent Paper equity capability is implied.

## License

This repository is licensed under the Apache License 2.0. See [LICENSE](LICENSE).
