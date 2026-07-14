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

## Submit One Cross-Sectional Run

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

1. Call `strategy_list_eligible_factors` to discover eligible cross-sectional factors when needed.
2. If the user explicitly asks the agent to choose factors, select eligible returned factors and
   continue. Ask the user to choose only when they supplied neither factors nor weights and did not
   authorize the agent to choose.
3. Call `strategy_submit_run` once with a valid selection, ranking, strategy type, and normal
   attribution default.

## Observe the Main Run

1. Call `strategy_get_run` with `{"run_id":"<strategy-run-id>"}` for the latest main-run snapshot.
2. While the main run is not terminal, use `strategy_resume_run` with that same `run_id` to continue
   observing it.
3. Once the main run is terminal, do not resubmit it to retrieve results.

The main-run status is separate from archive artifact availability. Use each artifact's returned
manifest as authoritative; never invent a replacement artifact state.

## Read Strategy Archive Artifacts

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

When the host can write local files, save returned content under this deterministic layout:

```text
Quandora staging result/
  strategy/
    <strategy-run-id>/
      run_summary.json
      artifacts/
        <artifact>.json
        logs.txt
        code.txt
      artifact_manifest.json
```

- Save `run_summary.json` from the final main-run snapshot.
- Save a JSON artifact as `artifacts/<artifact>.json` only when its manifest permits its body.
- Save text artifacts as `artifacts/logs.txt` and `artifacts/code.txt` only when their manifests
  permit their text.
- Create `artifact_manifest.json` with the run id, main-run status, and the returned four-field
  manifest for every requested artifact. Include a relative filename only for content that was
  saved.
- Record `pending` and `failed` exactly as returned. Do not create placeholder body files.

In the final response, report the main-run status, manifests and saved artifacts requested by the
user, and the local archive folder when files were written.
