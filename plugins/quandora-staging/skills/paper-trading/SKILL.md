---
name: paper-trading
description: Use when the user asks for simulated trading, paper trading, 模拟盘, 纸交易, current Paper PnL or assets, Paper positions/fills/funding/equity/code, stopping a Paper run, or a Strategy Portfolio Paper workflow on Quandora Staging. Use strategy-building for factor selection and Strategy creation or backtests.
---

# Quandora Staging Paper Trading

Bundled plugin version: 1.54

Use this skill through the authenticated `quandora-staging` MCP connection. It operates only on
the current user's product-safe StrategyRun, Paper run, and Strategy Portfolio handles. It is a
staging capability and must never be described as production or live-money trading.

Route requests for “模拟盘”, “纸交易”, “paper trading”, current Paper assets/PnL, Paper history,
or Portfolio Paper here directly. Factor selection, Strategy composition/revision, and Strategy
backtests belong to `$strategy-building`: ordinary work uses `sb_*`, while an explicitly requested
optimizer/versioned source uses its bounded `pt_src_*` workflow. If no eligible source exists, hand
off to Strategy Building; do not prepare one in this skill.

OAuth and credentials are host-managed. Never inspect, print, copy, store, or ask the user to paste
API keys, bearer/access/refresh tokens, authorization codes, PKCE verifiers, service tokens,
account credentials, or any other secret.

## Tools and Routing

Route read-only diagnosis of a completed Strategy result or Paper-readiness assessment to
`$strategy-analysis`. Keep actual Paper discovery, start, monitoring, data reads, and stop here.

Use only the minimum relevant subset of these Paper tools:

- Existing-source discovery: `pt_list_sources`, `pt_get_source`.
- Single runs: `pt_list_runs`, `pt_get_run`, `pt_submit_run`, `pt_stop_run`.
- Single-run data: `pt_get_portfolio`, `pt_list_pos`, `pt_get_equity`, `pt_list_fills`,
  `pt_list_funding`, `pt_get_code`.
- Strategy Portfolio discovery, setup and backtest: `pt_sp_list`, `pt_sp_create`,
  `pt_sp_revise`, `pt_sp_get`,
  `pt_sp_version`, `pt_sp_bt_submit`,
  `pt_sp_bt_get`, `pt_sp_bt_result`.
- Portfolio Paper: `pt_sp_run_submit`, `pt_sp_run_get`,
  `pt_sp_run_stop`.
- Authoritative strategy/Paper guidance when needed: `qd_get_guidance` with
  `operation.paper_trade.submit` or `operation.strategy.portfolio.manage`, always without
  `sections`.

Some hosts prefix names with the server name, for example
`quandora_staging__pt_get_run`; treat it as the same tool. If no `pt_*` tools are visible, do not
infer the cause. Paper/versioned-source service gates or the deployment may not be active, in which
case OAuth retries cannot fix the absence. When an authoritative safe error or tool signal proves
the gates are active but the token lacks newly advertised Paper scopes, fresh staging consent is
required because refreshed old tokens do not gain scopes automatically. Without that signal, state
both safe possibilities and do not assert which occurred. Do not loop authorization. Use only the
host-native reconnect/browser consent flow; never bypass MCP with raw HTTP, inspect credentials, or
ask for pasted tokens.

The exact Paper OAuth scope set is `paper_trading:sources.read`,
`paper_trading:sources.write`, `paper_trading:runs.read`, `paper_trading:runs.create`,
`paper_trading:runs.stop`, `paper_trading:code.read`, `paper_trading:portfolios.read`, and
`paper_trading:portfolios.write`. This skill uses source read only to discover and monitor an
existing Paper-eligible source. Tool visibility does not authorize this skill to compose, create,
revise, or backtest a Strategy. Tools remain invisible when the relevant gate is closed or the
token lacks their exact scope.

There is deliberately no Paper archive, unarchive, resume, parent aggregate positions, parent net
position, or parent Paper equity tool. Never invent or imply these abilities.
Do not call `sb_submit_run` from this skill. Hand Strategy work to `$strategy-building`; use Paper
tools here only after an eligible source exists.

## Global Safety Rules

- Never request, display, store, or infer FM/QuantAI/provider/account identifiers, raw provider
  payloads, downstream configuration, internal URLs, hostnames, ports, topology, database details,
  or credentials.
- Treat `source_strategy_run_id`, `paper_run_id`, Portfolio ids, child Paper handles, and cursors as
  opaque product handles. Return cursors byte-for-byte and never parse them.
- Never send `symbols`, `universe`, or `universe_policy`, including null or empty values. Quandora
  chooses and freezes the Paper universe downstream.
- Money, leverage, component weights, and allocated cash are exact decimal strings. Never convert
  them through a binary float or send them as JSON numbers.
- Never automatically stop, reopen, resubmit, change a strategy, change capital, mine another
  factor, or trigger another module because of losses or performance.
- A mutation timeout or ambiguous response is not proof of failure. Do not issue a fresh mutation
  or altered request. If a product handle was returned, reconcile with its get tool. If none was
  returned, report the ambiguity and stop; the user must decide after authoritative reconciliation.
- Treat Product Backend preflight as conservative guidance. FM submit remains the final eligibility
  authority, and another owner's handle must look nonexistent rather than distinguishable.

## Single-Strategy Workflow

### 1. Require an Existing Eligible Source

Paper Trading begins with an exact existing source StrategyRun supplied by the user or returned by
`pt_list_sources`. This skill must not list or choose factors, create or revise a Strategy, inspect a
prepared StrategyVersion, or submit a Strategy backtest.

If no suitable eligible source exists, or the user asks to create, change, or backtest a Strategy,
hand that work to `$strategy-building` and stop before any Paper mutation. Strategy Building uses
its ordinary `sb_*` path or, only for explicit optimizer/versioned-source intent, its bounded
`pt_src_*` path. After it produces a completed source with `paper_eligibility=eligible`,
continue only when the user still wants Paper, then select the exact source and obtain the separate
Paper confirmation below.

### 2. Select a Source

If the user did not provide an exact source StrategyRun handle, call `pt_list_sources`. Show a
compact table with source handle, lifecycle/submit state, strategy kind, initial cash, safe
strategy/version information, `is_optimizer`, safe `optimizer_execution` version/config source/
warning code when present, `paper_eligibility`, and the returned closed `eligibility_reasons`.
When `source_strategy_no_result` is present, the completed source produced zero orders and is
ineligible for Paper. Do not submit or retry it. Offer a handoff to `$strategy-analysis` or, after
explicit user confirmation, a new controlled Strategy experiment through `$strategy-building`.

Ask the user to select one exact returned source. Never probe guessed handles. Explain eligibility
without downstream internals:

- `eligible`: local and safe execution evidence passed preflight; final submit validation still
  belongs to FM.
- `provider_validation_required`: source validation could not be completed; it is not guaranteed
  eligible.
- `ineligible`: use only the returned closed reason codes, such as incomplete/unsubmitted source,
  unsupported strategy kind, or missing semantic lineage.

For an optimizer source, `is_optimizer=true` is classification only. Require exact positive
`initial_cash`, `optimizer_execution.version` of `base` or `pro`, and
`optimizer_execution.config_source=caller`. Treat `optimizer_config_not_caller` as ineligible.
Treat `optimizer_execution_unavailable` or `source_capital_unavailable` as
`provider_validation_required`, not as permission to submit. `default`, `default_after_invalid`,
missing evidence, unknown values, or contradictory eligibility fail closed. Never request raw
policy YAML or provider state to repair a source.

A source must ultimately be owner-scoped, completed, successfully submitted, cross-sectional, and
semantically reconstructable. `source_validation_unavailable` means the bounded source read failed
or exhausted its deadline. Describe validation as incomplete and retry only the read later if the
user asks. Unknown reason values fail closed; do not infer their meaning or request downstream
payloads. Missing displayed capital does not by itself make an ordinary source ineligible.

### 3. Confirm and Submit

Before `pt_submit_run`, display and obtain explicit confirmation for:

- exact source StrategyRun handle and safe strategy/version label;
- exact `initial_balance` when the user supplies one for an ordinary source;
- optional ISO `start_date`;
- optional exact `leverage`.

For an eligible optimizer source, first read `operation.paper_trade.submit` with
`qd_get_guidance` without `sections`, show the source's exact `initial_cash` as the locked Paper
balance, and include it in the confirmation. Do not ask for, offer, or send an `initial_balance`
override; omit that field so PB binds the exact source StrategyRun capital. To change optimizer
capital, hand back to
`$strategy-building` to create another StrategyRun for the same StrategyVersion, then obtain a new
Paper confirmation for that returned source.

For an ordinary source, send only `source_strategy_run_id`, `start_date`, optional
`initial_balance`, and optional `leverage`, omitting fields the user did not choose. When the caller
omits ordinary `initial_balance`, omit it from the tool call and FM retains its existing default.
Creating/revising a source, completing its backtest, and submitting Paper are separate mutations;
each requires its own explicit confirmation.

### 4. Observe Lifecycle and Read Data

Use the submit response as the first snapshot. For lifecycle monitoring, call `pt_get_run`; never
poll `pt_get_portfolio`. Keep polling bounded and user-visible, and stop when terminal. If a caller
asks only for current state, make one detail call.

When presenting `pt_list_runs` or `pt_get_run`, use the returned `strategy_name` when it is present.
During a mixed-version staging rollout it may be null. Reuse a safe source name already returned in
the current workflow; if the user specifically needs missing names, resolve only the distinct
returned source handles with bounded `pt_get_source` reads (at most 20 per request) and use
`source.strategy.name` when present. Otherwise label the name unavailable. Never infer a name from
submission time, PnL, ROI, direction, code, or neighboring rows, and never probe a guessed handle.

Use each data tool for its distinct meaning:

- Current assets/current PnL: call `pt_get_portfolio` once. Report `freshness.age_ms`, `stale`, and
  `retry_after_s`; explain cached or stale data without forcing refresh. This is a live manual
  collection protected by a PB 60-second per-run guard, and failed downstream attempts also consume
  that window.
- Historical positions: call `pt_list_pos`. This is a history of closed net-position lifecycles
  only: an item appears after the net position returns from nonzero to zero. Open positions and
  positions that were partially closed but remain nonzero are absent from this history and remain
  visible only through the current `pt_get_portfolio` snapshot. Honor symbol, side, open/close time
  filters, sort/order, bounded limit, and opaque cursor exactly. Closed-position realized return
  and current PnL are different semantics; never rename or derive one from the other, and never
  describe this list as arbitrary point-in-time portfolio replay.
- Execution records: use `pt_list_fills` for fills and `pt_list_funding` for funding cash flows.
  Do not infer closed-position semantics from fills.
- Strategy code: use `pt_get_code` only when asked and present only its bounded text/content type.
  Never expose a rejected internal reference.

### 5. Equity Curves

Choose exactly one mode from the user's intent and never mix their parameters:

- Legacy/full mode: omit lookback/bounds/sampling, or use only a bounded legacy `limit`.
- Bounded mode: use `max_points` and optional `started_at`/`ended_at`; do not send `limit` or
  `lookback`.
- Fixed lookback: send only one `lookback` plus `paper_run_id`.

| lookback | interval | total points |
|---|---:|---:|
| `7D` | `30m` | 336 |
| `30D` | `1.5h` | 480 |
| `90D` | `6h` | 360 |
| `180D` | `12h` | 360 |
| `1Y` | `1d` | 365 |
| `3Y` | `3d` | 365 |

Fixed windows return ROI values, `interval`, `total_points`, `live_start_index`, and `is_live` per
point. Explicitly label points before `live_start_index` as synthetic pre-live zero padding. Never
describe those zeros as observed returns or imply the strategy existed during that interval.

### 6. Stop

Before `pt_stop_run`, show the exact run handle and current known status, state that stop is terminal,
and obtain explicit confirmation. Make one stop call; do not automatically retry it. Then use
`pt_get_run` to observe authoritative state. Never call it pause and never offer resume. Running the
same strategy again requires a new user-confirmed submit and produces a new Paper run from a flat
book.

## Strategy Portfolio and Portfolio Paper

A Strategy Portfolio contains at least two exact StrategyVersion sleeves. Every weight is a
positive canonical Decimal string and the exact decimal sum must equal `1`. A version is a static
composition: no capital transfer, periodic rebalance, shared margin, signal fusion, order netting,
or execution-level netting exists.

Before the first Strategy Portfolio create/revise/backtest/Paper mutation in a request, read
`operation.strategy.portfolio.manage` with `qd_get_guidance` without `sections`. If that
authoritative contract contradicts this bundled workflow, fail closed and report the revision
mismatch instead of mutating.

If the user did not provide an exact Portfolio handle, call `pt_sp_list` once with a bounded
`page_size` and the default `include_archived=false`. Show the returned name, status, metadata,
latest version, version number, and `archived_at` without guessing missing values. Treat
`next_page_token` as opaque and pass it back byte-for-byte only when the user asks for another page.
Use `include_archived=true` only when the user explicitly asks to include archived Portfolios. An
invalid or owner/archive-mismatched token is a caller-correctable invalid request: discard it and
restart from the first page with the intended filters; never parse or modify it.

Use `pt_sp_create` for the first exact composition and
`pt_sp_revise` only when the user explicitly changes the version. Display and
confirm every StrategyVersion handle and weight before either mutation. Read exact parent/version
state with `pt_sp_get` and `pt_sp_version`.

Before `pt_sp_bt_submit`, confirm the exact PortfolioVersion, total initial cash, dates,
and optional fee strings. The total cash is allocated exactly across sleeves; child StrategyRuns
are ordinary independent runs. Observe with `pt_sp_bt_get` and read the completed
aggregate backtest result with `pt_sp_bt_result`.

Portfolio Paper can start only from one completed PortfolioRun. Before
`pt_sp_run_submit`, display and confirm the source PortfolioRun, its exact total/source
capital, start date, leverage, and that every child is an independent static sleeve. Do not offer a
Paper-time capital override. To change total Paper capital, first complete a new PortfolioRun at
that capital.

Use `pt_sp_run_get` for the parent lifecycle and ordered child handles/status. Present child
status in component order and label every child `independent sleeve`. Do not claim parent aggregate
positions exist. Do not claim parent net positions, shared margin, or a parent real-time/equity
curve exists.

Before `pt_sp_run_stop`, show the exact parent handle, explain that stop fans out to its
children and is terminal, and obtain explicit confirmation. Call stop once, then reconcile with
`pt_sp_run_get`; never retry automatically or offer resume.

## Safe Errors

Explain safe failures as actionable product states without exposing downstream text:

- `source_strategy_ineligible`: choose another eligible completed source or complete the missing
  source prerequisite. Use only its returned closed `eligibility_reasons`.
- `source_strategy_no_result`: the completed source produced zero orders, so no Paper mutation was
  admitted. Do not retry Paper or reinterpret the run as failed; use Strategy Analysis or a newly
  confirmed controlled Strategy experiment.
- `optimizer_source_capital_mismatch`: no Paper mutation was admitted with the requested balance.
  Re-read the exact source and show `required_initial_balance`; never expose it as a selectable
  override. Continue only through a fresh user-confirmed submit that omits `initial_balance`, or
  return to Strategy Building for a new same-version StrategyRun at different capital.
- `optimizer_config_not_caller`: the source did not execute the caller-frozen optimizer policy and
  is ineligible; do not retry Paper or fall back to an ordinary/default optimizer.
- `optimizer_execution_unavailable` or `source_capital_unavailable`: optimizer readiness cannot be
  proven. Do not submit; retry only the bounded source read later when the user asks.
- `paper_initial_balance_unavailable`: the requested Paper balance cannot be used safely; omit an
  override only when the user intended FM's default.
- `source_validation_unavailable`: source discovery could not complete its bounded FM validation;
  do not describe the source as eligible.
- `quantai_unavailable` or another retryable mutation error: the mutation can still be ambiguous.
  Reconcile authoritatively and never change its idempotency identity or blindly submit again.
- `paper_read_unavailable`: the provider read was unavailable and the error is retryable, but a
  manual portfolio attempt that entered the provider path has already consumed the 60-second
  per-run window. Honor returned stale/cache/retry-after guidance instead of forcing another read.
- `paper_read_rejected`: the provider rejected an otherwise ordinary read. It is not retryable;
  report the safe state and do not loop.
- Authoritative authorization/scope failure with active gates: complete fresh staging consent for
  the minimum required Paper scopes.
- Rate/freshness response: honor returned cache, stale, and retry-after information.

If the response contains no recognized closed reason, report only the generic safe error code and
retryability. Never quote, reinterpret, or ask for a hidden provider message.
