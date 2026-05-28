# Quandora Factor Mining

Quandora Factor Mining is a Codex local-agent plugin for turning public factor
tasks or custom factor ideas into local `plugin.py` factors, then submitting
them to Quandora for validation, upload, backtesting, artifact retrieval, and
result summaries.

Codex uses the bundled Quandora MCP tools for formal Factor Mining actions.
The plugin does not expose generic API-call tools and does not ask users to
copy or paste full Factor Mining credential values.

## Buddy Requirement

Quandora Buddy is a separate required local desktop app for account connection
and backtesting. Plugin installation does not silently install, start, update,
bundle, or include Buddy.

Install, start, and connect Buddy explicitly through the official Quandora path:

```text
https://app.quandora.ai/download/buddy
```

If Buddy is missing, stopped, disconnected, or unable to provide the delegated
local-agent credential, Codex must stop authenticated Factor Mining work and
guide you to install, start, and connect Buddy.

## Codex CLI Install

Install from the public marketplace source:

```bash
codex plugin marketplace add varsity-tech-product/factor-mining-agent-plugins --ref main
codex plugin add factor-mining@factor-mining-marketplace
```

Or run the installer:

```bash
curl -fsSL https://raw.githubusercontent.com/varsity-tech-product/factor-mining-agent-plugins/main/install-codex.sh | bash
```

The installer checks Buddy readiness with:

```bash
quandora-buddy doctor --json --min-version 0.1.0
```

Codex starts only after Buddy is ready. If Buddy is unavailable, the installer
prints Buddy setup guidance and skips Codex startup.

## Codex Desktop Install

In Codex Desktop, add this marketplace:

```text
Marketplace source: varsity-tech-product/factor-mining-agent-plugins
Marketplace ref: main
Plugin: factor-mining@factor-mining-marketplace
```

You can also run:

```bash
./install-codex-desktop.sh
```

## First Prompts

```text
Show me the Factor Mining public task list.
Use Factor Mining with my custom factor idea.
Resume my Factor Mining run and summarize results.
```

## Security And Privacy

- Buddy is the local credential provider for authenticated Factor Mining work.
- No formal user path requires copying or pasting a full `vt_` key.
- The plugin should never print or persist full credential values.
- The bundled MCP server does not expose raw credentials, generic URL fetches,
  or generic API-call tools.
- Generated `plugin.py` source stays local until the user asks Codex to submit
  it through the bundled Factor Mining workflow.

## Troubleshooting

If Codex says Buddy is unavailable:

1. Install Quandora Buddy from the official download path.
2. Start Buddy.
3. Connect Quandora through Buddy.
4. Ask Codex to run Quandora status again.

If Buddy is installed but not ready, open Buddy and check its status. Codex will
not continue with upload, backtest, polling, session creation, or artifact
fetching until Buddy is connected and ready.
