---
name: strategy
description: Use when an agent should compose, submit, inspect, or resume a cross-sectional Quandora Staging strategy from existing factors.
---

# Quandora Staging Strategy

Use this skill through the authenticated Quandora Staging connection exposed by the host as `quandora-staging`. It composes cross-sectional strategies from existing factor ids; use Factor Mining to create new factor source.

If the Strategy tools are visible, continue. Otherwise, use the host's normal Quandora Staging OAuth connection path:

- Codex CLI/TUI: run `codex mcp login quandora-staging`.
- Codex Desktop: authorize the plugin-provided Quandora Staging connector if prompted, then start a new chat. If the tools are still missing, fully quit and reopen Codex Desktop.
- Claude Code: open `/mcp`, authenticate `quandora-staging`, then start a new chat.
- Claude Desktop: open Settings -> Connectors, add a Connector named `quandora-staging` with URL `https://mcp-staging.varsity.lol/quant`, click Connect, authorize Quandora Staging in the browser, then start a new chat. Existing authorization for the old staging `/factor-mining` audience is not reused for `/quant`.
- OpenClaw: run `openclaw mcp login quandora-staging`, complete the printed authorization flow, then start a new chat.

Never ask for or accept API keys, access tokens, bearer tokens, service tokens, auth files, or credentials. Do not use raw HTTP, local helper scripts, direct internal-service calls, or credential-paste flows.

## Supported Workflow

Use only these Strategy actions in the normal workflow:

1. `strategy_list_eligible_factors`
2. `strategy_submit_run`
3. `strategy_get_run`
4. `strategy_resume_run`

Some hosts prefix the action names with the server name, such as `quandora_staging__strategy_submit_run`; treat those as the same actions.

## Scope and Submission Rules

- Cross-sectional strategies only. Do not send `ts` or `time_series`.
- Use factors returned by `strategy_list_eligible_factors` or exact factor ids supplied by the user.
- Supply exactly one selection form:
  - `factor_ids`: 1–20 factor ids.
  - `factor_weights`: 1–20 objects of the form `{ "factor_id": "<id>", "weight": <positive number> }`. Factor ids must be unique and weights must be positive.
- Supply `ranking` as `{ "mode": "N", "value": <positive integer> }` or `{ "mode": "percent", "value": <number in (0, 50]> }`.
- Supply `strategy_type` as `long_only`, `short_only`, or `neutral`.
- Optional supported submission fields are `start_date`, `end_date`, `initial_cash`, `taker_fee_rate`, `maker_fee_rate`, `rebalance_bars`, and `attribution`.
- `attribution` is an opaque optional boolean. Send `attribution: true` for a normal run unless the user explicitly requests otherwise.

## Run Workflow

1. Call `strategy_list_eligible_factors` to find eligible cross-sectional factors. Use its supported filters and pagination fields only when needed.
2. Choose factors with the user unless exact factors were supplied or the user explicitly asks the agent to choose.
3. Call `strategy_submit_run` with exactly one selection form, a ranking rule, a strategy type, and `attribution: true` unless the user requests otherwise.
4. Call `strategy_get_run` with `{"run_id":"<run_id>"}` to fetch the latest returned snapshot.
5. Call `strategy_resume_run` only with `{"run_id":"<run_id>"}` when resuming a run. Send no other fields.

## Final Response

Report only facts returned by `strategy_get_run` or `strategy_resume_run`:

- run status;
- selected factors and selection method;
- ranking and strategy type;
- safe summary fields, when present;
- that result artifacts are not yet available when the server does not provide them.
