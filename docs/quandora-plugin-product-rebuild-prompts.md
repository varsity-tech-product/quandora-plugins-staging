# Quandora Plugin Product Rebuild Prompts

Use one prompt per fresh Codex window. Do not skip Phase 0 if
`varsity-tech-product/quandora-plugins` still has `feat/batch-test-local-mcp`.
Do not leave long-lived product repo feature branches after release.

## Phase 0 Prompt — Archive Existing Local-MCP Feature Branch

```text
You are preserving the existing local-MCP batch-test feature branch before the
public product repository is rebuilt into a clean Remote MCP product.

Repositories:
- Product repo: /Users/richsion/Desktop/quandora/quandora-plugins
- Demo/reference repo: /Users/richsion/Desktop/quandora/factor-mining-demo

Read first:
- /Users/richsion/Desktop/quandora/quandora-plugins/docs/quandora-plugin-product-rebuild-plan.md

Objective:
- Preserve the complete current product repo branch
  varsity-tech-product/quandora-plugins:feat/batch-test-local-mcp
  in the demo/reference repo as:
  varsity-tech-product/factor-mining-demo:archive/quandora-plugins-local-mcp-batch-test-2026-06-22
- Do not merge anything into factor-mining-demo/main.
- Do not modify product repo main.
- Do not delete the product feature branch unless the archive branch is pushed
  and verified.

Steps:
1. In /Users/richsion/Desktop/quandora/quandora-plugins:
   - git fetch origin feat/batch-test-local-mcp
   - record `git rev-parse origin/feat/batch-test-local-mcp`
   - confirm this is the branch to archive.

2. In /Users/richsion/Desktop/quandora/factor-mining-demo:
   - ensure main is clean.
   - add or update a remote named quandora-plugins pointing to
     https://github.com/varsity-tech-product/quandora-plugins.git.
   - fetch quandora-plugins feat/batch-test-local-mcp.
   - create branch archive/quandora-plugins-local-mcp-batch-test-2026-06-22
     from FETCH_HEAD.
   - push that branch to origin.

3. Verify:
   - `git ls-remote origin refs/heads/archive/quandora-plugins-local-mcp-batch-test-2026-06-22`
   - inspect README and marketplace manifest on the archive branch to confirm
     it is the product repo's local-MCP batch-test content.

4. Report:
   - source product branch commit hash
   - archive branch commit hash
   - archive branch URL
   - whether deletion of the product repo feature branch is now safe

Do not delete any branch in this phase unless explicitly instructed after reporting.
```

## Phase 1 Prompt — Rebuild Product Repo As One Remote MCP Quandora Plugin

```text
You are rebuilding the public product repository into the formal Quandora plugin marketplace.

Repositories:
- Product repo: /Users/richsion/Desktop/quandora/quandora-plugins
- Packaging reference repo: /Users/richsion/Desktop/quandora/factor-mining-demo

Read first:
- /Users/richsion/Desktop/quandora/quandora-plugins/docs/quandora-plugin-product-rebuild-plan.md

Reference:
- factor-mining-demo main is the proven three-platform packaging reference.
- The product repo should match its high-level organization:
  root marketplace manifests, one plugin package under plugins/, one skill tree,
  platform install docs, and platform validators.
- Do not copy the demo's local Python stdio MCP runtime into the product repo.

Objective:
- Replace the current service-specific product package with one all-in-one
  plugin package:
  plugins/quandora
- Use Remote MCP only.
- Keep Factor Mining as the first skill:
  plugins/quandora/skills/factor-mining
- Do not include a batch skill in v0.4.0.
- Keep the repo ready for future skills and services under the same plugin.
- Use version 0.4.0 everywhere.
- Make stable install docs pin to tag v0.4.0, not main.

Hard boundaries:
- Do not add local Python MCP servers.
- Do not add stdio MCP as a product path.
- Do not include mcp/server.py, mcp/launch.py, factor_mining_agent_lib, scripts,
  local browser vt_ setup, or direct Agent API Key setup.
- Do not ask users for vt_ keys.
- Do not call Product Backend directly from the plugin/local agent.
- Do not call Factor Mining directly from the plugin/local agent.
- Do not include factor-mining-batch-test or factor-mining-demo package content.
- Do not create an empty factor-mining-batch skill.
- Do not modify quandora-auth-service or factor_mining.

Prepare:
cd /Users/richsion/Desktop/quandora/quandora-plugins
git switch main
git pull --ff-only origin main
git status --short

If the worktree is dirty, stop and report. Do not stash, reset, or overwrite user changes.

Create a short implementation branch:
git switch -c rebuild/quandora-remote-mcp-v0.4.0

Implementation requirements:
1. Root marketplace:
   - .agents/plugins/marketplace.json has name "quandora".
   - .agents/plugins/marketplace.json lists one plugin named "quandora" sourced
     from ./plugins/quandora.
   - .claude-plugin/marketplace.json has name "quandora" and lists one plugin
     named "quandora" sourced from ./plugins/quandora.

2. Product package:
   - Create plugins/quandora.
   - Create plugins/quandora/.codex-plugin/plugin.json.
   - Create plugins/quandora/.claude-plugin/plugin.json.
   - Both plugin manifests use:
     name: quandora
     version: 0.4.0
     repository/homepage: https://github.com/varsity-tech-product/quandora-plugins
     display name: Quandora
   - Remove or replace plugins/factor-mining from the product surface.

3. Remote MCP:
   - Configure Factor Mining Remote MCP using platform-supported remote HTTP MCP
     declarations.
   - Production URL: https://mcp.quandora.ai/factor-mining
   - Staging URL may be documented for internal validation:
     https://mcp-staging.varsity.lol/factor-mining
   - Server/resource name: quandora-factor-mining.
   - Do not include a stdio command, local python command, cwd, args, or local
     MCP launcher in production manifests.
   - Validate exact manifest syntax with installed CLIs or official docs.
   - If a platform cannot auto-register remote MCP from plugin metadata,
     implement a platform-specific installer command using that platform's
     supported MCP CLI. Keep this as Remote MCP, not stdio.

Known supported CLI forms on this machine:
codex mcp add quandora-factor-mining --url https://mcp.quandora.ai/factor-mining --oauth-resource https://mcp.quandora.ai/factor-mining
codex mcp login quandora-factor-mining
claude mcp add --transport http quandora-factor-mining https://mcp.quandora.ai/factor-mining
openclaw mcp add quandora-factor-mining --transport streamable-http --url https://mcp.quandora.ai/factor-mining --auth oauth

4. Skill:
   - Create plugins/quandora/skills/factor-mining/SKILL.md.
   - Create plugins/quandora/skills/factor-mining/agents/openai.yaml.
   - Use the demo skill as the workflow reference, but rewrite tool names and
     auth guidance for production Remote MCP.
   - The skill must start with status, trigger MCP OAuth when needed, list public
     tasks, support custom ideas, request dedup context, submit inline
     plugin_source, upload/backtest/wait/resume through Remote MCP, fetch safe
     artifacts, and summarize results.
   - The skill must prohibit raw HTTP fallback, local scripts, direct Product
     Backend calls, direct Factor Mining calls, plugin_path upload, local
     execution keys, and vt_ key paste flows.
   - The skill must not advertise batch mining in v0.4.0.

5. README/installers:
   - Root README must describe Quandora Plugins as the marketplace and Quandora
     as one all-in-one plugin.
   - Stable install commands must use v0.4.0:
     codex plugin marketplace add varsity-tech-product/quandora-plugins --ref v0.4.0
     codex plugin add quandora@quandora
     claude plugin marketplace add varsity-tech-product/quandora-plugins@v0.4.0
     claude plugin install quandora@quandora
     openclaw plugins install quandora --marketplace https://github.com/varsity-tech-product/quandora-plugins.git#v0.4.0 --force
   - install-codex.sh defaults to source varsity-tech-product/quandora-plugins,
     ref v0.4.0, marketplace quandora, plugin quandora.
   - install-openclaw.sh, if present, installs the plugin and registers Remote
     MCP through OpenClaw's HTTP/OAuth MCP config. It must not configure a local
     python stdio MCP server.

6. Validation tooling:
   - Add or update a validator that checks:
     one plugin package under plugins/quandora;
     no plugins/factor-mining local package remains;
     no demo/batch package is exposed;
     no local Python MCP files exist in plugins/quandora;
     no stdio MCP production config exists;
     manifests parse;
     version is 0.4.0 everywhere;
     user-facing install docs pin v0.4.0.

Validation:
- python3 -m json.tool .agents/plugins/marketplace.json >/dev/null
- python3 -m json.tool .claude-plugin/marketplace.json >/dev/null
- python3 -m json.tool plugins/quandora/.codex-plugin/plugin.json >/dev/null
- python3 -m json.tool plugins/quandora/.claude-plugin/plugin.json >/dev/null
- bash -n install-codex.sh
- bash -n install-codex-desktop.sh
- bash -n install-openclaw.sh, if the file exists
- python3 tools/validate-quandora-product-package.py, if created
- claude plugin validate .
- claude plugin validate plugins/quandora
- claude plugin tag plugins/quandora --dry-run
- Codex install smoke with temporary CODEX_HOME:
  TMP_CODEX_HOME="$(mktemp -d)"
  CODEX_HOME="$TMP_CODEX_HOME" codex plugin marketplace add "$(pwd)"
  CODEX_HOME="$TMP_CODEX_HOME" codex plugin add quandora@quandora
  CODEX_HOME="$TMP_CODEX_HOME" codex plugin list --marketplace quandora
- OpenClaw install/inspect/skills check if openclaw is installed.
- git diff --check

Product-facing pollution scan:
rg -n "factor-mining-agent-plugins|factor-mining-marketplace|factor-mining-batch-test|factor-mining-demo|vt_|stdio|python3|python|mcp/server.py|mcp/launch.py|factor_mining_agent_lib|plugin_path|direct Product Backend|direct Factor Mining|d25q1jf66e8y4g|CloudFront|/api/cast" README.md install-codex.sh install-openclaw.sh .agents .claude-plugin plugins/quandora

Review every product-facing hit. Remove setup paths and implementation leaks.
Explicit prohibition language is allowed in the skill. Developer docs may
mention archived branch names and historical context, but user-facing install
docs must not expose old repo names or local-MCP setup paths.

Developer-doc install-reference scan:
rg -n "varsity-tech-product/factor-mining-agent-plugins|factor-mining-marketplace|--ref main|@main|/main/" docs

Every docs hit must be intentional historical/archive guidance or removed.

Commit and push:
git status --short
git add README.md LICENSE install-codex.sh install-codex-desktop.sh install-openclaw.sh .agents .claude-plugin plugins/quandora tools docs
git commit -m "Rebuild Quandora plugin for Remote MCP"
git push origin HEAD

Report:
- branch
- commit
- changed files
- exact validation output
- Remote MCP declaration format used per platform
- whether any platform needs installer-based Remote MCP registration
- whether v0.4.0 tag is ready to create after review
```

## Phase 2 Prompt — Merge, Tag, And Clean Product Branches

```text
You are finalizing the public Quandora plugin product release after Phase 1 review.

Repository:
- /Users/richsion/Desktop/quandora/quandora-plugins

Read first:
- docs/quandora-plugin-product-rebuild-plan.md
- docs/quandora-plugin-product-rebuild-prompts.md

Objective:
- Merge the reviewed rebuild branch into main.
- Create and push release tag v0.4.0.
- Ensure stable install commands use v0.4.0.
- Delete temporary product repo feature branches so the product repo has only
  main as an active branch plus release tags.

Prerequisites:
- Phase 0 archive branch exists in factor-mining-demo:
  archive/quandora-plugins-local-mcp-batch-test-2026-06-22
- Phase 1 rebuild branch has passed review.
- The working tree is clean.
- The owner has approved release/tagging.

Steps:
1. Verify archive branch:
   gh repo view varsity-tech-product/factor-mining-demo --json defaultBranchRef
   git ls-remote https://github.com/varsity-tech-product/factor-mining-demo.git refs/heads/archive/quandora-plugins-local-mcp-batch-test-2026-06-22

2. Verify product repo branch state:
   cd /Users/richsion/Desktop/quandora/quandora-plugins
   git fetch origin
   git status --short
   git branch --show-current

3. Re-run validation from Phase 1 on the rebuild branch.

4. Merge:
   git switch main
   git pull --ff-only origin main
   git merge --ff-only rebuild/quandora-remote-mcp-v0.4.0

5. Re-run validation on main.

6. Tag:
   git tag -a v0.4.0 -m "Quandora plugin v0.4.0"
   git push origin main
   git push origin v0.4.0

7. Delete product repo temporary branches only after push succeeds:
   git branch -d rebuild/quandora-remote-mcp-v0.4.0
   git push origin --delete rebuild/quandora-remote-mcp-v0.4.0 || true
   git push origin --delete feat/batch-test-local-mcp

8. Verify product repo has only main as active branch:
   git ls-remote --heads origin

9. Verify version-pinned install docs:
   rg -n "--ref main|@main|/main/" README.md install-codex.sh install-openclaw.sh plugins/quandora docs
   rg -n "v0.4.0|quandora@quandora|varsity-tech-product/quandora-plugins" README.md install-codex.sh install-openclaw.sh plugins/quandora docs

Report:
- final main commit
- release tag
- deleted branches
- remaining remote branches
- whether stable install commands are tag-pinned
- whether Codex, Claude Code, and OpenClaw validations passed
```
