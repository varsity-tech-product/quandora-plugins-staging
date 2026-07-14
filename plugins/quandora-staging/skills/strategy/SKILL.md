---
name: strategy
description: Use when an agent should compose, submit, inspect, or archive a cross-sectional Quandora Staging strategy from eligible factors.
---

# Quandora Staging Strategy

Use this skill through the authenticated Quandora Staging connection exposed by the host as
`quandora-staging`. It composes cross-sectional strategies from eligible factor ids and reads the
Factor Mining-owned Strategy archive contract.

## Connection and Tools

Before starting, confirm that the Quandora Staging connection is authenticated and that these five
Strategy actions are visible:

1. `strategy_list_eligible_factors`
2. `strategy_submit_run`
3. `strategy_get_run`
4. `strategy_resume_run`
5. `strategy_get_artifact`

Some hosts prefix action names with the server name, such as
`quandora_staging__strategy_submit_run`; treat those as the same actions. If the connection or
actions are unavailable, use the host's normal Quandora Staging connection flow, then start a new
chat before continuing.

## Submit One Cross-Sectional Run

1. Call `strategy_list_eligible_factors` and use its returned eligible cross-sectional factors.
2. If the user has not supplied factor ids or weighted factors, ask them to choose from those
   returned factors. Confirm optional weights when the user wants a weighted selection.
3. Call `strategy_submit_run` once with exactly one selection form:
   - `factor_ids`: 1–20 returned factor ids; or
   - `factor_weights`: 1–20 `{ "factor_id": "<id>", "weight": <positive number> }` objects.
4. Include a valid ranking rule and strategy type. Use `attribution: true` unless the user
   explicitly requests otherwise, and record whether it was enabled for this submission.

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
