---
name: strategy
description: Use when an agent should compose, submit, inspect, or archive a cross-sectional Quandora Staging strategy from eligible factors.
---

# Quandora Staging Strategy

Use this skill through the authenticated Quandora Staging connection exposed by the host as
`quandora-staging`. It composes cross-sectional strategies from eligible factor ids and includes
the complete Strategy archive workflow.

## Connection and Tools

Before starting, confirm that the Quandora Staging connection is authenticated and that these five
Strategy actions are visible:

1. `strategy_list_eligible_factors`
2. `strategy_submit_run`
3. `strategy_get_run`
4. `strategy_resume_run`
5. `strategy_get_artifact`

Some hosts prefix action names with the server name, such as
`quandora_staging__strategy_submit_run`; treat those as the same actions.

If the connection or actions are unavailable, use the host-specific OAuth flow, then start a new
chat before continuing:

- Codex CLI/TUI: run `codex mcp login quandora-staging`.
- Codex Desktop: authorize the plugin-provided connector, start a new chat, and fully quit and
  reopen Codex Desktop if the tools remain unavailable.
- Claude Code: open `/mcp`, authenticate `quandora-staging`, then start a new chat.
- Claude Desktop: add a connector named `quandora-staging` with URL
  `https://mcp-staging.varsity.lol/quant`, click Connect, complete browser authorization, then
  start a new chat.
- OpenClaw: run `openclaw mcp login quandora-staging`, complete authorization, then start a new
  chat.

The normal workflow uses only these five exposed Strategy MCP actions. Never ask for or accept API
keys, access tokens, bearer tokens, service tokens, auth files, or credentials. Do not use raw
HTTP, local helper scripts, direct internal-service calls, or credential-paste flows as a fallback.

## Workflow

### 1. Prepare a Valid Submission

- Cross-sectional strategies only; never send `ts` or `time_series`.
- Use factors returned by `strategy_list_eligible_factors`, or exact factor ids or weights supplied
  by the user.
- Use exactly one selection form:
  - `factor_ids`: 1–20 unique factor ids.
  - `factor_weights`: 1–20 unique `{ "factor_id": "...", "weight": <positive number> }` objects.
- `ranking` must be `{ "mode": "N", "value": <positive integer> }` or
  `{ "mode": "percent", "value": <number in (0, 50]> }`.
- `strategy_type` must be `long_only`, `short_only`, or `neutral`.
- Supported optional fields are `start_date`, `end_date`, `initial_cash`, `taker_fee_rate`,
  `maker_fee_rate`, `rebalance_bars`, and `attribution`.
- Use `attribution: true` unless the user explicitly requests otherwise.

Call `strategy_list_eligible_factors` to discover eligible cross-sectional factors when needed. If
the user explicitly asks the agent to choose factors, select eligible returned factors and
continue. Ask the user to choose only when they supplied neither factors nor weights and did not
authorize the agent to choose.

Call `strategy_submit_run` once with a valid selection, ranking, strategy type, and normal
attribution default. Never send `name` or `strategy_name` to `strategy_submit_run`; its schema
has `additionalProperties: false`.

### 2. Observe the Main Run

Call `strategy_get_run` with `{"run_id":"<strategy-run-id>"}` for the latest main-run snapshot.
While the main run is not terminal, use `strategy_resume_run` with that same `run_id` to continue
observing it. Once the main run is terminal, do not resubmit it to retrieve results.

The main-run status is separate from archive artifact availability. Use each artifact's returned
manifest as authoritative; never invent a replacement artifact state.

### 3. Read Requested Archive Artifacts

Each `strategy_get_artifact` call requires both `run_id` and exactly one of these Factor Mining
archive names:

```text
status
summary
equity_curve
drawdown_curve
turnover_curve
exposure_curve
orders
charts
trades
performance
attribution
signal_return_curves
result
logs
code
```

After the main run is terminal, retrieve selectively in this order:

1. `status`, `summary`, `performance`.
2. `charts`, `equity_curve`, `drawdown_curve`, `turnover_curve`, `exposure_curve`.
3. `attribution` and `signal_return_curves` only when attribution was enabled or the user requests
   style exposure.
4. `orders`, `trades`, `result`, `logs`, and `code` only when the user explicitly requests them or
   they are required to investigate a failed or unfinished result.

`attribution` describes predictive style exposure, not PnL contribution.

For every artifact, retain only the returned manifest fields `name`, `content_type`, `available`,
and `sync_status`. Persist body or text only when `available` is `true` and `sync_status` is
`"synced"`. For `pending` or `failed`, record the manifest and do not create a local body file.

`logs` and `code` are text artifacts. All other names are JSON artifacts. Do not print large
artifact bodies into chat.

If `strategy_get_artifact` returns `RESOURCE_EXHAUSTED`, report that the requested archive exceeds
the current 32 MiB unary Factor Mining artifact contract. Do not retry, truncate the artifact, or
invent a download URL.

## Local Result Archive

When the host can write local files, create one deterministic local archive for the strategy.
Choose its local-only `<strategy_slug>` before submitting the run:

- If the user supplied a strategy name, lowercase it, replace each run of non-`[a-z0-9]` characters
  with one underscore, and trim leading and trailing underscores. This is the strategy slug.
- If the user did not supply a name, use
  `<strategy_type>_<ranking_mode>_<ranking_value>_strategy`, with each component normalized to the
  same lowercase safe snake_case form.
- If a supplied name normalizes to an empty slug, use the generated form.

The slug is a local archive label only. Do not send it, `name`, or `strategy_name` in an action
request. Use it only in the local archive folder and the user-facing local paths. The latest run
for the same slug updates that strategy folder.

```text
Quandora staging result/
  strategy/
    <strategy_slug>/
      run_summary.json
      artifacts/
        <artifact>.json
        logs.txt
        code.txt
      artifact_manifest.json
```

Save `run_summary.json` from the final main-run snapshot. Save a JSON artifact as
`artifacts/<artifact>.json` only when its manifest permits its body. Save text artifacts as
`artifacts/logs.txt` and `artifacts/code.txt` only when their manifests permit their text.

Create `artifact_manifest.json` with the run id, main-run status, and the returned four-field
manifest for every requested artifact. Include a relative filename only for content that was saved.
Keep run ids only in `run_summary.json` and `artifact_manifest.json` when traceability requires
them; never use a run id in a directory name or user-facing summary.

For each requested artifact, update its local file with the latest returned body when its manifest
permits it. For `pending` or `failed`, record its manifest exactly as returned. Do not create a
placeholder body file, or delete or overwrite any existing local body file.

## Final Response

State the strategy name when the user supplied one; otherwise say that no strategy name was
supplied. State the main-run status, each requested artifact that is available, and safe diagnostics.
For requested artifacts without a local body file, state `not created` and its returned availability
or sync status. Do not print large artifact bodies.

Never show run ids, download URLs, credentials, secret material, or internal service metadata in a
user-facing summary.

At the end of every completed, failed, or interrupted run, show the result folder, artifact folder,
`run_summary.json`, and `artifact_manifest.json`. If a specific file was not created, say
`not created` for that line.

For Desktop or GUI hosts, use Markdown links with absolute local paths and angle-bracket link
targets so paths with spaces work:

```text
Result folder: [Open result folder](</absolute/path/to/Quandora staging result/strategy/<strategy_slug>/>)
Artifact folder: [Open artifact folder](</absolute/path/to/Quandora staging result/strategy/<strategy_slug>/artifacts/>)
Run summary: [run_summary.json](</absolute/path/to/Quandora staging result/strategy/<strategy_slug>/run_summary.json>)
Artifact manifest: [artifact_manifest.json](</absolute/path/to/Quandora staging result/strategy/<strategy_slug>/artifact_manifest.json>)
```

For CLI or TUI hosts, use the same absolute paths as plain text, not Markdown links:

```text
Result folder: /absolute/path/to/Quandora staging result/strategy/<strategy_slug>/
Artifact folder: /absolute/path/to/Quandora staging result/strategy/<strategy_slug>/artifacts/
Run summary: /absolute/path/to/Quandora staging result/strategy/<strategy_slug>/run_summary.json
Artifact manifest: /absolute/path/to/Quandora staging result/strategy/<strategy_slug>/artifact_manifest.json
```

If the host cannot write files, state:

```text
Result folder: unavailable in this host
Artifact folder: unavailable in this host
```
