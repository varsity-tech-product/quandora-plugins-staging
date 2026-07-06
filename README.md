<p align="center">
  <img src="assets/banner.png" alt="Quandora" width="100%">
</p>

# Quandora Staging Plugins

<p align="center">
  <a href="https://quandora.ai"><img src="https://img.shields.io/badge/Built%20by-Quandora-F28C00?style=flat" alt="Built by Quandora"></a>
  <a href="https://discord.com/invite/SMVW6pKYmg"><img src="https://img.shields.io/badge/Join-Discord-5865F2?style=flat&logo=discord&logoColor=white" alt="Join Discord"></a>
  <a href="https://x.com/quandora_labs"><img src="https://img.shields.io/badge/Follow-%40quandora__labs-000000?style=flat&logo=x&logoColor=white" alt="Follow on X"></a>
</p>

### Public staging plugin channel for Quandora agent integration testing.

This repository is for staging validation only. It points to Quandora staging services and should not be used for production workflows. Production users should install `varsity-tech-product/quandora-plugins`.

<table>
<tr><td><b>AI-Native Research Workflow</b></td><td>Run the full quant research loop directly from CLI, Codex, Claude Code, or Cursor: autonomous research, backtesting, strategy creation, and deployment-ready workflow.</td></tr>
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
                  |                              | performance decay
                  |                              | restarts mining
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
| **Paper Trading Monitor Agent** | Monitors paper performance and restarts factor mining when performance decay is detected. |
| **Deployment Supervisor Agent** | Keeps users in the loop for approvals, guardrails, deployment checks, and supervised rollout. |

<br>

Quandora Staging Plugins is the public marketplace for testing Quandora agent integrations before production release. The current package is:

```text
quandora-staging@quandora-staging
```

Quandora Staging Factor Mining lets local agents create `plugin.py`, submit it through the authenticated staging Quandora connection, run a backtest, retrieve available factor cards and chart artifacts, and save the run files in the local workspace.

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
Install Quandora Staging from varsity-tech-product/quandora-plugins-staging, then connect Quandora Staging Factor Mining.
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

### Claude

Claude Code:

```bash
claude plugin marketplace add varsity-tech-product/quandora-plugins-staging
claude plugin install quandora-staging@quandora-staging
```

Claude Desktop requires both the Quandora Staging plugin and the Quandora Staging connector. After installing the plugin, manually add and connect the Connector in Claude Desktop:

```text
Name: quandora-staging
URL: https://mcp-staging.varsity.lol/factor-mining
```

Use Settings -> Connectors, add the Connector above, click Connect, authorize Quandora Staging in the browser, then start a new chat.

In Claude Code, open `/mcp` and authenticate `quandora-staging`, then start a new chat.

Claude Desktop can use the connected Quandora Staging tools in chat, but local result-folder archiving is only guaranteed in local agent environments such as Claude Code, Codex, and OpenClaw. Claude Desktop's built-in file creation uses Claude's sandbox and may provide downloadable files rather than writing directly to a chosen local folder.

Factor Mining chart downloads use returned server `source_name` values for API calls and save local PNGs to returned `standard_local_path` values.

### OpenClaw

```bash
curl -fsSL https://raw.githubusercontent.com/varsity-tech-product/quandora-plugins-staging/HEAD/install-openclaw.sh | bash
```

Authorize Quandora Staging:

```bash
openclaw mcp login quandora-staging
```

Open the printed URL, approve access, then run the code command printed by OpenClaw:

```bash
openclaw mcp login quandora-staging --code <code>
```

Start a new OpenClaw chat after installation or authorization.

## Use Factor Mining

Use the skill command when available:

```text
/quandora-staging:factor-mining show public tasks
```

You can also ask naturally:

```text
Use Quandora Staging Factor Mining to show public tasks.
Use Quandora Staging Factor Mining with my custom factor idea.
Use Quandora Staging Factor Mining to resume a run and summarize results.
```

When the host supports local files, each run is saved under a stable folder named after the factor slug:

```text
Quandora staging result/factor-mining/aggressive_flow_exhaustion_reversal/
```

The run folder contains the submitted `plugin.py`, a redacted `run_summary.json`, `factor_card_is.json` and `factor_card_all.json` when available, `artifact_manifest.json`, and PNG charts under `artifacts/is/` and `artifacts/all/`. The agent prints the result, artifact, and chart folder paths at the end of each run.

## License

This repository is licensed under the Apache License 2.0. See [LICENSE](LICENSE).
