# Quandora Plugins

Quandora Plugins is the public marketplace for Quandora agent integrations. The current package is:

```text
quandora@quandora
```

Quandora Factor Mining lets local agents create `plugin.py`, submit it through the authenticated Quandora connection, run a backtest, retrieve available artifacts, and save the run files in the local workspace.

## Install

### Codex

Codex Desktop:

```text
Source: varsity-tech-product/quandora-plugins
Git ref: leave blank
Plugin: quandora@quandora
```

Codex CLI:

```bash
codex plugin marketplace add varsity-tech-product/quandora-plugins
codex plugin add quandora@quandora
```

Authorize when prompted. In Codex CLI, use:

```bash
codex mcp login quandora-mcp
```

Start a new chat after installation or authorization.

### Claude

Claude Code:

```bash
claude plugin marketplace add varsity-tech-product/quandora-plugins
claude plugin install quandora@quandora
```

Claude Desktop requires both the Quandora plugin and the Quandora connector. Use the Connectors page to connect your Quandora account, then start a new chat.

In Claude Code, open `/mcp` and authenticate `quandora-mcp`, then start a new chat.

### OpenClaw

```bash
curl -fsSL https://raw.githubusercontent.com/varsity-tech-product/quandora-plugins/HEAD/install-openclaw.sh | bash
```

Authorize Quandora:

```bash
openclaw mcp login quandora-mcp
```

Open the printed URL, approve access, then run the code command printed by OpenClaw:

```bash
openclaw mcp login quandora-mcp --code <code>
```

Start a new OpenClaw chat after installation or authorization.

## Use Factor Mining

Use the skill command when available:

```text
/factor-mining show public tasks
```

You can also ask naturally:

```text
Use Quandora Factor Mining to show public tasks.
Use Quandora Factor Mining with my custom factor idea.
Use Quandora Factor Mining to resume a run and summarize results.
```

When the host supports local files, each run is saved under:

```text
results/factor-mining/<session_id>/attempt-<n>/
```

The run folder contains the submitted `plugin.py`, a redacted `run_summary.json`, a `factor_card.json` when available, and safe artifacts returned by Quandora. The agent prints the result folder path at the end of each run.

## License

This repository is licensed under the Apache License 2.0. See [LICENSE](LICENSE).
