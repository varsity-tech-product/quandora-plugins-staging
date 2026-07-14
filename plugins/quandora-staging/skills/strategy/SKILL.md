---
name: strategy
description: Use when an agent should compose, submit, inspect, or archive a cross-sectional Quandora Staging strategy from eligible factors.
---

# Quandora Staging Strategy

Use this skill through the authenticated Quandora Staging connection exposed by the host as `quandora-staging`. It composes cross-sectional strategies from eligible factor ids and retrieves the service-provided safe Strategy result artifacts.

## Connection and Tools

Before starting, confirm that the Quandora Staging connection is authenticated and that these five Strategy actions are visible:

1. `strategy_list_eligible_factors`
2. `strategy_submit_run`
3. `strategy_get_run`
4. `strategy_resume_run`
5. `strategy_get_artifact`

Some hosts prefix action names with the server name, such as `quandora_staging__strategy_submit_run`; treat those as the same actions. If the connection or actions are unavailable, use the host's normal Quandora Staging connection flow, then start a new chat before continuing.

## Submit One Cross-Sectional Run

1. Call `strategy_list_eligible_factors` and use its returned eligible cross-sectional factors.
2. If the user has not supplied factor ids or weighted factors, ask them to choose from those returned factors. Confirm optional weights when the user wants a weighted selection.
3. Call `strategy_submit_run` once with exactly one selection form:
   - `factor_ids`: 1–20 returned factor ids; or
   - `factor_weights`: 1–20 `{ "factor_id": "<id>", "weight": <positive number> }` objects.
4. Include a valid ranking rule and strategy type. Use `attribution: true` unless the user explicitly requests otherwise, and record whether it was enabled for this submission.

## Observe the Main Run

1. Call `strategy_get_run` with `{"run_id":"<strategy-run-id>"}` for the latest main-run snapshot.
2. While the main run is not terminal, use `strategy_resume_run` with that same `run_id` to continue observing it.
3. Once the main run is terminal, do not resubmit it to retrieve results.

The main run status remains separate from artifact availability, including after the main run is terminal. For `{"status":"pending","artifact_status":"pending"}` (or the legacy status-only pending response), record the artifact as pending and allow a later resume or check. For `{"status":"not_available","artifact_status":"failed"}` or `{"status":"not_available","artifact_status":"unavailable"}`, record the artifact as unavailable, do not continue polling it as pending, do not create its local artifact file, and report that the main-run status is unchanged.

## Read Safe Result Artifacts

After the main run reaches its terminal state, read `summary` first with:

```json
{"run_id":"<strategy-run-id>","artifact":"summary"}
```

When the user asks for the completed result archive, then read these safe artifacts as available:

1. `charts`
2. `equity_curve`
3. `drawdown_curve`
4. `turnover_curve`
5. `exposure_curve`

Read `trades` only when the user requests trade-level detail.

Read `attribution` and `signal_return_curves` only when attribution was enabled for this submission and the returned archive reports those artifacts ready. Describe attribution only as the safe Strategy attribution artifact returned by the service; do not describe it as PnL contribution analysis.

Each `strategy_get_artifact` call requires both `run_id` and one of these safe artifact names:

```text
summary
charts
equity_curve
drawdown_curve
turnover_curve
exposure_curve
trades
attribution
signal_return_curves
```

## Local Result Archive

When the host can write local files, save only safe returned content under this deterministic layout:

```text
Quandora staging result/
  strategy/
    <strategy-run-id>/
      run_summary.json
      artifacts/
        summary.json
        charts.json
        equity_curve.json
        drawdown_curve.json
        turnover_curve.json
        exposure_curve.json
        trades.json
        attribution.json
        signal_return_curves.json
      artifact_manifest.json
```

- Save `run_summary.json` from the final safe main-run snapshot.
- Create an artifact JSON file only when the corresponding safe artifact body is available.
- Create `artifact_manifest.json` with the run id, main-run status, each artifact's local state, and a relative filename only for saved artifacts.
- For every artifact, record exactly one local state: `ready`, `pending`, `unavailable`, or `not_requested`.
- Keep the manifest limited to those local archive facts and the returned safe content needed for the saved files.

In the final response, report the main-run status, which safe artifacts were ready or unavailable, and the local archive folder when files were written.
