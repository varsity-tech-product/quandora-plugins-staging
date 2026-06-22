# Quandora Plugin Product Rebuild Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild the public `varsity-tech-product/quandora-plugins` repository into a clean, version-pinned, multi-platform Quandora plugin marketplace that ships one all-in-one plugin and uses Remote MCP rather than local stdio MCP.

**Architecture:** Use `varsity-tech-product/factor-mining-demo` `main` as the proven three-platform packaging reference. Keep the same high-level marketplace/package/skill organization, but replace the demo's local Python stdio MCP implementation with Remote MCP declarations and OAuth flow. The product repository should expose one plugin package named `quandora`; Factor Mining is the first skill inside that plugin, and future sibling services or batch workflows are added as more skills later.

**Tech Stack:** Codex plugin marketplace, Claude Code plugin marketplace, OpenClaw Claude-compatible bundle support, Remote MCP over streamable HTTP, MCP OAuth, Markdown skills, JSON manifests, shell installers, version tags.

---

## Current Reference State

The demo repository is the implementation reference:

```text
repo:   varsity-tech-product/factor-mining-demo
branch: main
commit: 8c5d2dea6fe27d3e26a091e88370290d1423bba7
```

The demo repo has already validated:

- Codex CLI and Codex Desktop install from a marketplace.
- Claude Code install from a marketplace.
- OpenClaw install through a Claude-compatible bundle and installer.
- One plugin package under `plugins/factor-mining-demo`.
- One skill under `plugins/factor-mining-demo/skills/factor-mining-demo`.
- One shared MCP server used by all three platforms.

The product repository must preserve that packaging shape, not the demo's local
MCP runtime. Product differences are limited to:

- Remote MCP instead of local stdio Python MCP.
- Quandora naming.
- One all-in-one plugin package for future services.
- Version-pinned installation and release tags.
- No first-release batch skill.

## Product Naming Model

Use these names consistently:

| Layer | Name |
| --- | --- |
| GitHub repo | `varsity-tech-product/quandora-plugins` |
| Marketplace id | `quandora` |
| Single product plugin package | `quandora` |
| First service skill | `factor-mining` |
| First Remote MCP server/resource name | `quandora-factor-mining` |
| Production Remote MCP URL | `https://mcp.quandora.ai/factor-mining` |
| Staging Remote MCP URL | `https://mcp-staging.varsity.lol/factor-mining` |
| First release version | `0.4.0` |
| First release Git tag | `v0.4.0` |

Do not use service-specific repository names such as
`factor-mining-agent-plugins` in product docs or install commands.

Do not keep `factor-mining` as the plugin package name in the rebuilt product.
`factor-mining` is a service/skill inside the all-in-one `quandora` plugin.

## Target Repository Shape

The final product `main` branch should contain one plugin package:

```text
quandora-plugins/
  README.md
  LICENSE
  install-codex.sh
  install-codex-desktop.sh
  install-openclaw.sh

  .agents/plugins/marketplace.json
  .claude-plugin/marketplace.json

  plugins/
    quandora/
      README.md
      .codex-plugin/plugin.json
      .claude-plugin/plugin.json
      .mcp.json or platform-supported Remote MCP declaration
      assets/
        .gitkeep
      skills/
        factor-mining/
          SKILL.md
          agents/
            openai.yaml

  docs/
    quandora-plugin-product-rebuild-plan.md
    quandora-plugin-product-rebuild-prompts.md
    release-checklist.md
```

The final product `main` branch must not contain:

- `plugins/factor-mining-batch-test`
- `plugins/factor-mining-demo`
- `plugins/factor-mining` as the top-level product package
- local Python MCP server code
- `mcp/server.py`
- `mcp/launch.py`
- `factor_mining_agent_lib`
- local browser setup for `vt_` keys
- direct `vt_` Agent API Key setup docs
- local stdio MCP as a product fallback
- test fixtures for demo/local MCP flows
- branch-specific install instructions for stable users

## Batch Skill Policy

Do not include a batch skill in the first rebuilt product release.

The product must still be organized so batch can be added later as a second
skill under the same `quandora` plugin:

```text
plugins/quandora/skills/
  factor-mining/
  factor-mining-batch/   # future, not present in v0.4.0
```

Do not create an empty `factor-mining-batch` skill. Empty or placeholder skills
can become visible to agent platforms and confuse users. Reserve the future
skill only in docs.

## Remote MCP Policy

The rebuilt product package uses Remote MCP only.

Allowed:

- Remote MCP over streamable HTTP.
- MCP OAuth login/authorization handled by the agent platform.
- Remote MCP tools exposed by `https://mcp.quandora.ai/factor-mining`.
- Local agent writes `plugin.py` in the user's workspace, then sends inline
  `plugin_source` through Remote MCP tools.

Forbidden:

- Local Python MCP servers.
- Stdio MCP in production manifests.
- Writing a Python MCP launcher into the user's machine.
- Asking users for `vt_` keys.
- Storing `vt_` keys locally.
- Direct calls from the plugin/local agent to Product Backend.
- Direct calls from the plugin/local agent to Factor Mining.
- Raw HTTP fallback when MCP tools are unavailable.

If a platform cannot auto-register Remote MCP from plugin metadata, provide a
platform-specific installer command that registers the Remote MCP server through
the platform's supported CLI. Do not reintroduce local stdio MCP to work around
platform gaps.

Shared MCP configuration is the preferred first implementation shape, but it is
not assumed to be release-proven before testing. Start with a shared
`plugins/quandora/.mcp.json` as the logical source of the Factor Mining Remote
MCP declaration where platform manifests support it. If Codex, Claude Code, or
OpenClaw cannot consume that shared declaration directly, keep the shared file
as documentation/source-of-truth and add the smallest platform-specific Remote
MCP declaration or installer registration required by that platform. This is a
validation feedback item, not permission to add stdio or local MCP.

User-facing installation must not require a separate login/auth command.
Authorization should be triggered by the agent platform when the skill first
uses the Remote MCP server or when the platform's MCP UI requests connection.
CLI login commands may be used only as internal validation aids and must not be
listed as stable install steps unless the product owner explicitly changes this
policy.

Do not invent production MCP tool names by mechanically renaming demo tools.
Before release, discover or confirm the actual `quandora-factor-mining` Remote
MCP tool names from the deployed server contract, `tools/list`, or backend
owner confirmation, then update the skill to reference those names. A package
that installs successfully but contains unverified tool names is not release
complete.

Known CLI capabilities on this machine:

```bash
codex mcp add quandora-factor-mining --url https://mcp.quandora.ai/factor-mining --oauth-resource https://mcp.quandora.ai/factor-mining

claude mcp add --transport http quandora-factor-mining https://mcp.quandora.ai/factor-mining

openclaw mcp add quandora-factor-mining \
  --transport streamable-http \
  --url https://mcp.quandora.ai/factor-mining \
  --auth oauth
```

The implementation must validate the exact plugin-bundled Remote MCP declaration
format for Codex, Claude Code, and OpenClaw before release.

## Cursor Policy

Cursor is not part of the v0.4.0 release acceptance matrix.

Do not add Cursor install commands, Cursor marketplace claims, or Cursor local
copy instructions to the stable user-facing v0.4.0 README. Cursor support can
be researched and tested separately after the Codex, Claude Code, and OpenClaw
Remote MCP product flow is validated. If Cursor artifacts are added later, they
must not change the v0.4.0 scope or reintroduce local MCP.

## Version-Pinned Install Policy

Stable user install docs must pin to a release tag, not a moving branch.

For v0.4.0:

```bash
codex plugin marketplace add varsity-tech-product/quandora-plugins --ref v0.4.0
codex plugin add quandora@quandora
```

```bash
claude plugin marketplace add varsity-tech-product/quandora-plugins@v0.4.0
claude plugin install quandora@quandora
```

```bash
openclaw plugins install quandora --marketplace https://github.com/varsity-tech-product/quandora-plugins.git#v0.4.0 --force
```

Install scripts must default to `v0.4.0`, not `main`. Internal development
instructions may show branch refs, but user-facing README content must use the
release tag.

After validation, create and push:

```bash
git tag -a v0.4.0 -m "Quandora plugin v0.4.0"
git push origin v0.4.0
```

## Branch Policy

The public product repository should be clean after release:

- Default branch: `main`.
- Release references: version tags.
- No long-lived feature branches in `varsity-tech-product/quandora-plugins`.

Short implementation branches are allowed while work is in progress, but they
must be deleted after merge and tag.

The existing product feature branch with local-MCP batch-test content should be
preserved outside the product repo before deletion:

```text
source repo:   varsity-tech-product/quandora-plugins
source branch: feat/batch-test-local-mcp
source commit: b87403319a5873f56e10003b02a7d789bb1ee6a1

archive repo:  varsity-tech-product/factor-mining-demo
archive branch: archive/quandora-plugins-local-mcp-batch-test-2026-06-22
```

This keeps the product repo clean while preserving the old local-MCP batch-test
implementation in the demo/reference repository. The archive branch must never
be merged into `factor-mining-demo/main`.

## Phase 0: Archive Existing Local-MCP Product Feature Branch

**Files:** No file changes expected.

- [ ] In `quandora-plugins`, record the current source branch commit:

```bash
git fetch origin feat/batch-test-local-mcp
git rev-parse origin/feat/batch-test-local-mcp
```

- [ ] In `factor-mining-demo`, fetch the product feature branch as an external
      source and create an archive branch:

```bash
cd /Users/richsion/Desktop/quandora/factor-mining-demo
git remote add quandora-plugins https://github.com/varsity-tech-product/quandora-plugins.git 2>/dev/null || true
git fetch quandora-plugins feat/batch-test-local-mcp
git switch -c archive/quandora-plugins-local-mcp-batch-test-2026-06-22 FETCH_HEAD
git push origin archive/quandora-plugins-local-mcp-batch-test-2026-06-22
```

- [ ] Verify the archive branch exists:

```bash
git ls-remote origin refs/heads/archive/quandora-plugins-local-mcp-batch-test-2026-06-22
```

- [ ] Return to `quandora-plugins`. Do not delete the product feature branch
      until the archive branch is pushed and verified.

## Phase 1: Rebuild Product Package On A Short Branch

**Files:**

- Modify: `README.md`
- Modify: `.agents/plugins/marketplace.json`
- Create/modify: `.claude-plugin/marketplace.json`
- Remove/replace: `plugins/factor-mining`
- Create: `plugins/quandora/**`
- Modify: `install-codex.sh`
- Modify/create: `install-openclaw.sh`
- Create/modify: validation tooling as needed
- Modify: docs in `docs/`

- [ ] Start from latest `main`:

```bash
cd /Users/richsion/Desktop/quandora/quandora-plugins
git switch main
git pull --ff-only origin main
git switch -c rebuild/quandora-remote-mcp-v0.4.0
```

- [ ] Use the demo repo `main` as the packaging reference:

```bash
cd /Users/richsion/Desktop/quandora/factor-mining-demo
git fetch origin main
git switch main
git pull --ff-only origin main
```

- [ ] In `quandora-plugins`, create one product package:

```text
plugins/quandora/
```

- [ ] Remove the old service-specific package from the product surface:

```text
plugins/factor-mining/
```

- [ ] Implement product manifests:

```text
.agents/plugins/marketplace.json
.claude-plugin/marketplace.json
plugins/quandora/.codex-plugin/plugin.json
plugins/quandora/.claude-plugin/plugin.json
```

Required values:

```text
marketplace id: quandora
plugin name: quandora
plugin version: 0.4.0
display name: Quandora
first skill: factor-mining
repository: https://github.com/varsity-tech-product/quandora-plugins
```

- [ ] Implement Remote MCP declaration for Factor Mining with no local stdio
      server. Prefer a shared `plugins/quandora/.mcp.json` as the logical
      source. If testing shows a platform cannot consume the shared declaration,
      add the smallest platform-specific Remote MCP declaration or installer
      registration for that platform. Use only Remote MCP over HTTP/OAuth.

- [ ] Implement one skill:

```text
plugins/quandora/skills/factor-mining/SKILL.md
plugins/quandora/skills/factor-mining/agents/openai.yaml
```

The skill must:

- call Remote MCP tools only
- trigger MCP OAuth when authorization is missing
- avoid requiring users to run a separate login command during installation
- support public task flow
- support custom idea flow
- send inline `plugin_source`
- request dedup context before upload
- upload/backtest/wait/resume through Remote MCP
- fetch and summarize safe artifacts
- save workspace outputs under `.quandora/factor-mining/runs/<run_id>/` when the host permits file writes
- avoid raw HTTP, local scripts, direct Product Backend, direct Factor Mining,
  and `vt_` key flows

Before release, the skill's tool names must be verified against the production
or staging Remote MCP server. Do not ship tool names copied from the demo unless
the Remote MCP server confirms the same names.

- [ ] Do not include batch skill files in v0.4.0.

- [ ] Update README and installers with version-pinned commands using `v0.4.0`.

## Phase 2: Validate, Tag, And Clean Branches

- [ ] Validate JSON:

```bash
python3 -m json.tool .agents/plugins/marketplace.json >/dev/null
python3 -m json.tool .claude-plugin/marketplace.json >/dev/null
python3 -m json.tool plugins/quandora/.codex-plugin/plugin.json >/dev/null
python3 -m json.tool plugins/quandora/.claude-plugin/plugin.json >/dev/null
```

- [ ] Validate product-facing pollution:

```bash
rg -n "factor-mining-agent-plugins|factor-mining-marketplace|factor-mining-batch-test|factor-mining-demo|vt_|stdio|python3|python|mcp/server.py|mcp/launch.py|factor_mining_agent_lib|plugin_path|direct Product Backend|direct Factor Mining|d25q1jf66e8y4g|CloudFront|/api/cast|codex mcp login|claude mcp login|openclaw mcp login|Cursor|cursor" README.md install-codex.sh install-openclaw.sh .agents .claude-plugin plugins/quandora
```

Every hit must be removed unless it is an explicit prohibition in the skill.
User-facing install docs must not contain these terms as setup paths, separate
login steps, or Cursor stable-install claims.

- [ ] Validate developer docs for old install commands:

```bash
rg -n "varsity-tech-product/factor-mining-agent-plugins|factor-mining-marketplace|--ref main|@main|/main/" docs
```

Every hit must be intentional historical/archive guidance or removed.

- [ ] Validate Codex:

```bash
TMP_CODEX_HOME="$(mktemp -d)"
CODEX_HOME="$TMP_CODEX_HOME" codex plugin marketplace add "$(pwd)"
CODEX_HOME="$TMP_CODEX_HOME" codex plugin add quandora@quandora
CODEX_HOME="$TMP_CODEX_HOME" codex plugin list --marketplace quandora
```

- [ ] Validate Claude Code:

```bash
claude plugin validate .
claude plugin validate plugins/quandora
claude plugin tag plugins/quandora --dry-run
```

- [ ] Validate OpenClaw:

```bash
openclaw plugins install quandora --marketplace "$(pwd)" --force
openclaw plugins inspect quandora --runtime
openclaw skills check
```

- [ ] Validate Remote MCP registration path for each platform. The expected
      result is that the host can see the Factor Mining Remote MCP tools or can
      start the platform's OAuth flow. If a platform cannot auto-register Remote
      MCP through plugin metadata, the installer must register it through that
      platform's supported MCP CLI and document the command. Record whether the
      platform consumed the shared `.mcp.json`, required a platform-specific
      declaration, or required installer-based registration.

- [ ] Validate production/staging Remote MCP tool names. Fetch or confirm the
      `quandora-factor-mining` tool list, update the skill if needed, and record
      the confirmed tool names in the Phase 1 report.

- [ ] Merge to `main`, tag, and push:

```bash
git switch main
git merge --ff-only rebuild/quandora-remote-mcp-v0.4.0
git tag -a v0.4.0 -m "Quandora plugin v0.4.0"
git push origin main
git push origin v0.4.0
```

- [ ] Delete temporary product branches after successful release:

```bash
git branch -d rebuild/quandora-remote-mcp-v0.4.0
git push origin --delete rebuild/quandora-remote-mcp-v0.4.0 || true
git push origin --delete feat/batch-test-local-mcp
```

- [ ] Confirm the product repo has only `main` as an active branch:

```bash
git ls-remote --heads origin
```

Expected output should list only `refs/heads/main`.

## Acceptance Criteria

- Product repo is named `quandora-plugins`.
- Product repo default branch is `main`.
- Product repo has one product plugin package: `plugins/quandora`.
- Marketplace id is `quandora`.
- Plugin package name is `quandora`.
- Plugin version is `0.4.0`.
- User-facing install docs pin to `v0.4.0`.
- Factor Mining is a skill inside Quandora, not the repo or plugin package name.
- No batch skill ships in v0.4.0.
- Future batch/service expansion is documented but not visible as empty skills.
- No local Python/stdio MCP product path exists.
- No direct `vt_` key setup exists.
- Codex, Claude Code, and OpenClaw can install the package or have a documented
  supported Remote MCP registration command.
- User-facing install docs do not require a separate login/auth command.
- Factor Mining skill tool names are confirmed against the Remote MCP server
  before release.
- Cursor is not included in the v0.4.0 stable release scope.
- The previous local-MCP batch feature branch is archived in
  `factor-mining-demo` and removed from the product repo after release.
