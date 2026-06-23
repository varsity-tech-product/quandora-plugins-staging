# Quandora Plugins

Quandora Plugins is the public marketplace for Quandora agent integrations.
Version 0.4.9 ships one all-in-one plugin package for staging Remote MCP testing:

```text
quandora@quandora
```

Factor Mining is the first bundled skill. It uses Quandora Remote MCP over
HTTP/OAuth for public task listing, custom factor sessions, inline
`plugin_source` submission, backtesting, artifact retrieval, and result
summaries.

The Remote MCP server is named:

```text
quandora-mcp
```

The current Quandora Remote MCP endpoint is:

```text
https://mcp-staging.varsity.lol/factor-mining
```

## Codex

### Install

Use these fields in Codex Desktop:

```text
Source: varsity-tech-product/quandora-plugins
Git ref: leave blank when possible; use the default branch marketplace source
Plugin: quandora@quandora
```

Codex CLI:

```bash
codex plugin marketplace add varsity-tech-product/quandora-plugins
codex plugin add quandora@quandora
```

If an older pinned marketplace already exists, remove and add it again without
a Git ref:

```bash
codex plugin marketplace remove quandora || true
codex plugin marketplace add varsity-tech-product/quandora-plugins
```

### Authorize

Codex Desktop can open the Quandora OAuth page during first use.

Codex CLI uses:

```bash
codex mcp login quandora-mcp
```

After installing or authorizing the plugin, start a new Codex chat before using
Factor Mining. If the tools still do not appear, fully quit and reopen Codex
Desktop, then start a new chat.

### Use

Use the skill command when available:

```text
/factor-mining show public tasks
```

You can also ask directly:

```text
Use Quandora Factor Mining to show public tasks.
Use Quandora Factor Mining with my custom factor idea.
Use Quandora Factor Mining to resume a run and summarize results.
```

## Claude Code

### Install

```bash
claude plugin marketplace add varsity-tech-product/quandora-plugins
claude plugin install quandora@quandora
```

If a previous marketplace was added with a version suffix, remove and add it
again without a ref so Claude tracks the repository default branch:

```bash
claude plugin marketplace remove quandora
claude plugin marketplace add varsity-tech-product/quandora-plugins
claude plugin update quandora@quandora
```

### Authorize

Open `/mcp` in Claude Code and authenticate `quandora-mcp`.

After installing or authorizing the plugin, start a new Claude chat before
using Factor Mining. If the tools still do not appear, fully quit and reopen
Claude Desktop or Claude Code, then start a new chat.

### Use

Use the skill command when available:

```text
/factor-mining show public tasks
```

You can also ask directly:

```text
Use Quandora Factor Mining to show public tasks.
Use Quandora Factor Mining with my custom factor idea.
Use Quandora Factor Mining to resume a run and summarize results.
```

## OpenClaw

### Install

Install and verify the plugin bundle and Remote MCP server:

```bash
curl -fsSL https://raw.githubusercontent.com/varsity-tech-product/quandora-plugins/HEAD/install-openclaw.sh | bash
```

If the installer reports `Excluded by agent allowlist`, allow the skill and
verify again:

```bash
curl -fsSL https://raw.githubusercontent.com/varsity-tech-product/quandora-plugins/HEAD/install-openclaw.sh | bash -s -- --allow-skill
```

### Authorize

Run:

```bash
openclaw mcp login quandora-mcp
```

Open the printed URL, approve access, then run the code command printed by
OpenClaw:

```bash
openclaw mcp login quandora-mcp --code <code>
```

Verify the authorized MCP connection:

```bash
openclaw mcp doctor quandora-mcp --probe
```

After installing or authorizing the plugin, start a new OpenClaw chat before
using Factor Mining. If the tools still do not appear, restart the OpenClaw
gateway and start a new chat.

### Use

Start OpenClaw:

```bash
openclaw chat
```

Then run:

```text
/factor-mining show public tasks
```

You can also ask directly:

```text
Use Quandora Factor Mining to show public tasks.
Use Quandora Factor Mining with my custom factor idea.
Use Quandora Factor Mining to resume a run and summarize results.
```

## License

This repository is licensed under the Apache License 2.0. See [LICENSE](LICENSE).
