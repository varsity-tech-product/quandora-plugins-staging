# Quandora

Quandora is the all-in-one plugin package in the Quandora plugin marketplace.
Factor Mining is the first bundled skill.

## Remote MCP

The Factor Mining skill uses the `quandora-mcp` Remote MCP server:

```text
https://mcp-staging.varsity.lol/factor-mining
```

Internal validation may use:

```text
https://mcp-staging.varsity.lol/factor-mining
```

The plugin package includes a shared `.mcp.json` for Codex-compatible bundled
MCP loading and an HTTP MCP declaration in the Claude Code manifest. OpenClaw
registration is handled by the repository installer because OpenClaw stores
Remote MCP definitions in its own registry.

## Codex

### Install

Codex Desktop uses repository source `varsity-tech-product/quandora-plugins`,
plugin `quandora@quandora`. Leave Git ref blank when possible so the
marketplace follows the repository default branch.

Codex CLI:

```bash
codex plugin marketplace add varsity-tech-product/quandora-plugins
codex plugin add quandora@quandora
```

### Authorize

Codex Desktop can open the Quandora OAuth page during first use.

Codex CLI:

```bash
codex mcp login quandora-mcp
```

### Use

Use `/factor-mining show public tasks`, or ask directly for Quandora Factor
Mining.

## Claude Code

### Install

```bash
claude plugin marketplace add varsity-tech-product/quandora-plugins
claude plugin install quandora@quandora
```

If a previous marketplace was added with a version suffix, remove and add it
again without a ref before updating.

### Authorize

Open `/mcp` in Claude Code and authenticate `quandora-mcp`.

### Use

Use `/factor-mining show public tasks`, or ask directly for Quandora Factor
Mining.

## OpenClaw

### Install

```bash
curl -fsSL https://raw.githubusercontent.com/varsity-tech-product/quandora-plugins/HEAD/install-openclaw.sh | bash
```

If the installer reports `Excluded by agent allowlist`:

```bash
curl -fsSL https://raw.githubusercontent.com/varsity-tech-product/quandora-plugins/HEAD/install-openclaw.sh | bash -s -- --allow-skill
```

### Authorize

```bash
openclaw mcp login quandora-mcp
```

Open the printed URL, approve access, then finish with the `--code` command
printed by OpenClaw.

### Use

```bash
openclaw chat
```

Then run `/factor-mining show public tasks`, or ask directly for Quandora
Factor Mining.

All hosts submit factors as inline `plugin_source`. Local coding agents such as
Codex CLI and Claude Code may write a local `plugin.py` working copy first, but
the Remote MCP server never reads a local file path.

## Skills

```text
skills/
  factor-mining/
```
