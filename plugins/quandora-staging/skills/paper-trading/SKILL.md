---
name: paper-trading
description: Use when the user asks for simulated trading, paper trading, 模拟盘, 纸交易, current Paper PnL or assets, Paper positions/fills/funding/equity/code, stopping a Paper run, or a Strategy Portfolio Paper workflow on Quandora Staging.
---

# Quandora Staging Paper Trading

Bundled plugin version: 1.45

Use this skill through the authenticated `quandora-staging` MCP connection. It operates only on
the current user's product-safe StrategyRun, Paper run, and Strategy Portfolio handles. It is a
staging capability and must never be described as production or live-money trading.

When the user asks for “模拟盘”, “纸交易”, “paper trading”, current Paper assets/PnL, Paper
history, or Portfolio Paper, route here directly. Do not repeat Factor Mining or mature Strategy
Building introductions and do not call their tools unless the user separately asks for those
workflows.

OAuth and credentials are host-managed. Never inspect, print, copy, store, or ask the user to paste
API keys, bearer/access/refresh tokens, authorization codes, PKCE verifiers, service tokens, account
credentials, or any other secret.

## Plugin Version Reminder

On the first entry into any Quandora skill in the current conversation, if the conversation history
does not already contain one successful `qd_check_plugin_version` call and no earlier version-check
attempt has occurred, call it once before the business entry point. Pass `1.45` verbatim as
`installed_version`; treat it as an opaque release label and never parse, order, or normalize it.

- If `update_available=false`, continue silently.
- If `update_available=true`, say exactly: `The latest Quandora plugin version is <latest_version>. Please update the plugin.` Then say: `A Quandora Staging MCP access token is valid for 7 days. After 7 days, use the prompt below to ask your agent to refresh the connection; it should use automatic refresh first and CLI re-authentication only if required.` Then provide this exact copyable prompt in a fenced `text` block: `Refresh the Quandora Staging MCP connection. If automatic refresh fails, re-authenticate it with the CLI.` Then immediately continue the original request.
- If the version tool is missing, invisible, disabled, or fails, do not retry it later in the
  conversation and do not claim the plugin is outdated. Continue the business workflow.
- Never install, update, reload, or reauthorize merely because of this reminder.
- A later entry into Factor Mining, Strategy Building, or Paper Trading recognizes the first check
  and does not call it again.

## Tools and Routing

Use only the minimum relevant subset of these Paper tools:

- Source preparation and discovery: `pt_list_sources`, `pt_create_source_strategy`,
  `pt_revise_source_strategy`, `pt_get_source_strategy`, `pt_get_source_strategy_version`,
  `pt_submit_source_backtest`, `pt_get_source`.
- Single runs: `pt_list_runs`, `pt_get_run`, `pt_submit_run`, `pt_stop_run`.
- Single-run data: `pt_get_portfolio`, `pt_list_positions`, `pt_get_equity`, `pt_list_fills`,
  `pt_list_funding`, `pt_get_code`.
- Strategy Portfolio setup and backtest: `pt_create_strategy_portfolio`,
  `pt_revise_strategy_portfolio`, `pt_get_strategy_portfolio`,
  `pt_get_strategy_portfolio_version`, `pt_submit_portfolio_backtest`,
  `pt_get_portfolio_backtest`, `pt_get_portfolio_backtest_result`.
- Portfolio Paper: `pt_submit_portfolio_paper`, `pt_get_portfolio_paper`,
  `pt_stop_portfolio_paper`.

Some hosts prefix names with the server name, for example
`quandora_staging__pt_get_run`; treat it as the same tool. If no `pt_*` tools are visible, do not
infer the cause. Paper/versioned-source service gates or the deployment may not be active, in which
case OAuth retries cannot fix the absence. Alternatively, when an authoritative safe error or tool signal
proves those gates are active but the token lacks newly advertised Paper scopes, fresh
staging consent is required because existing and refreshed old tokens do not gain scopes
automatically. Without that authoritative signal, state both safe possibilities and do not assert which case occurred.
Do not loop authorization. Use only the host-native reconnect/browser consent
flow; never bypass MCP with raw HTTP, inspect credentials, or ask for pasted tokens.

The exact Paper OAuth scope set is `paper_trading:sources.read`,
`paper_trading:sources.write`, `paper_trading:runs.read`, `paper_trading:runs.create`,
`paper_trading:runs.stop`, `paper_trading:code.read`, `paper_trading:portfolios.read`, and
`paper_trading:portfolios.write`. Source create, revise, and source-backtest submit require source
write; source Strategy, StrategyVersion, list, and lifecycle reads require source read. Tools remain
invisible when the Paper or versioned-source gate is closed or the token lacks their exact scope.

There is deliberately no Paper archive, unarchive, resume, parent Portfolio list, parent aggregate
positions, parent net position, or parent Paper equity tool. Never invent or imply these abilities.
Do not use `sb_submit_run` as a versioned Strategy or Paper substitute; its legacy Strategy behavior
is separate and unchanged.

## Global Safety Rules

- Never request, display, store, or infer FM/QuantAI/provider/account identifiers, raw provider
  payloads, downstream/effective YAML, internal URLs, hostnames, ports, topology, database details,
  or credentials. The sole YAML input is bounded caller-authored `policy_yaml` for an optimizer
  source StrategyVersion; send it only to the source create/revise tool and never echo it.
- Treat `source_strategy_run_id`, `paper_run_id`, Portfolio ids, child Paper handles, and cursors as
  opaque product handles. Return cursors byte-for-byte and never parse them.
- Never send `symbols`, `universe`, or `universe_policy`, including null or empty values. Quandora
  chooses and freezes the Paper universe downstream.
- Money, leverage, optimizer capital, component weights, and allocated cash are exact decimal
  strings. Never convert them through a binary float or send them as JSON numbers.
- Never automatically stop, reopen, resubmit, change a strategy, change capital, change an
  optimizer, mine another factor, or trigger another module because of losses or performance.
- A mutation timeout or ambiguous response is not proof of failure. Do not issue a fresh mutation
  or altered request. If a product handle was returned, reconcile with its get tool. If none was
  returned, report the ambiguity and stop; the user must decide after authoritative reconciliation.
- Treat Product Backend preflight as conservative guidance. FM submit remains the final eligibility
  authority, and another owner's handle must look nonexistent rather than distinguishable.

## Single-Strategy Workflow

### 1. Prepare an Optimizer Source When Needed

Skip this step for an ordinary source that already exists. When the user explicitly wants a new
optimizer-backed Paper source, use this bounded sequence only:

1. Obtain the exact eligible `factor_id`, `factor_version_id`, and `job_id` triplets. Reuse exact
   references already returned in the current workflow. If they are absent, use only the minimum
   relevant Factor/Strategy reads needed to select and verify those references; do not give a
   general tutorial, mine/import/retest another factor, or invent an id.
2. For a new source call `pt_create_source_strategy`. Call `pt_revise_source_strategy` only when the
   user explicitly revises a returned Strategy using its exact `strategy_id` and base
   `strategy_version_id`. The specification is CS-only and closed: valid ranking, weighting,
   strategy type, rebalance bars, exact unique factor references, and optional optimizer version
   `base` or `pro` with bounded valid caller-authored `policy_yaml` that must not contain
   `portfolio_value`. Never send symbols, a universe, provider identity, transport identity, or an
   idempotency field.
3. Read back with `pt_get_source_strategy` or `pt_get_source_strategy_version` only when needed.
   These are closed Product projections and never return policy YAML or downstream identifiers.
4. Call `pt_submit_source_backtest` once with the exact StrategyVersion, a positive canonical
   Decimal-string `initial_cash`, optional ordered dates, and optional canonical Decimal-string fee
   rates. Treat a timeout as ambiguous and do not change or repeat the mutation. The successful
   response returns the owner-local opaque `source_strategy_run_id` and the first source snapshot.
5. Monitor only that handle with bounded `pt_get_source` reads. A normal lifecycle is `submitted`
   (shown as accepted), then `running`, then `completed`; terminal source states never reopen. Stop
   polling when terminal. Never use mature Strategy history to monitor this source lifecycle. A
   malformed, unavailable, or cross-wired read fails closed and never justifies probing another
   handle.

After `pt_get_source` reports `completed` and `paper_eligibility=eligible`, continue to explicit
Paper confirmation. Creating or revising the source never starts Paper automatically.

### 2. Select a Source

If the user did not provide an exact source StrategyRun handle, call `pt_list_sources`. Show a
compact table with source handle, lifecycle/submit state, strategy kind, initial cash, safe
strategy/version information, whether it is optimizer-backed, `paper_eligibility`, and the returned
closed `eligibility_reasons`.

Ask the user to select one exact returned source. Never probe guessed handles. Explain eligibility
without downstream internals:

- `eligible`: local and safe execution evidence passed preflight; final submit validation still
  belongs to FM.
- `provider_validation_required`: source validation could not be completed; it is not guaranteed
  eligible.
- `ineligible`: use the returned closed reason codes, such as incomplete/unsubmitted source,
  unsupported strategy kind, missing semantic lineage, or non-caller optimizer configuration.

A source must ultimately be owner-scoped, completed, successfully submitted, cross-sectional, and
semantically reconstructable. Interpret the additional closed reasons without asking for or
revealing raw source parameters:

- `optimizer_config_not_caller`: `optimizer_execution.config_source=default` is safe historical
  evidence but remains ineligible, as does `config_source=default_after_invalid`. Only `caller` is
  eligible. One historical ineligible item does not invalidate the other source-list entries.
- `optimizer_execution_unavailable`: required optimizer execution evidence is absent or invalid;
  treat the source as `provider_validation_required`, not as caller-configured success.
- `source_capital_mismatch`: final source/Paper validation rejected the exact capital binding. Do
  not choose another numeric representation or retry with a rounded value.
- `source_capital_unavailable`: an optimizer source has no trusted, request-hash-bound exact Product
  capital snapshot. This is expected for historical or external optimizer sources created outside
  the bounded PB source-binding path; Agent Paper does not support them and must not guess.
- `source_validation_unavailable`: the bounded source read failed or exhausted its deadline. Keep
  the item and its list position, describe validation as incomplete, and retry only the read later
  if the user asks.

Provider fallback is not optimizer success. Unknown reason or execution-evidence values fail
closed; do not infer their meaning or request downstream payloads.

Missing displayed capital does not make an ordinary non-optimizer source ineligible or require
provider validation. Display capital only when the source projection declares a safe exact source.

### 3. Confirm and Submit

Before `pt_submit_run`, display and obtain explicit confirmation for:

- exact source StrategyRun handle and safe strategy/version label;
- exact `initial_balance` (when present or required);
- optional ISO `start_date`;
- optional exact `leverage`;
- whether the source is optimizer-backed.

Send only `source_strategy_run_id`, `start_date`, `initial_balance`, and `leverage`, omitting optional
fields the user did not choose. Never send an optimizer override.

For a PB-bound optimizer source, preserve the exact frozen Product source-run capital from the
immutable request-hash-bound snapshot. If `initial_balance` is sent, it must be the exact same
canonical Decimal value; it may otherwise be omitted so PB uses that exact snapshot. Never compare
or reconstruct it from FM's current binary64 parameters. FM remains the final Paper submit
authority and rejects an actual source/config/capital mismatch. Do not suggest changing optimizer
policy or capital at Paper time. If the user wants different capital, first complete a new source
backtest for the same StrategyVersion at that exact capital, then use its new owner-local source
handle. Only
`optimizer_execution.config_source=caller` is eligible; historical `config_source=default`,
`config_source=default_after_invalid`, provider fallback, or missing evidence is not optimizer
success.

For an ordinary non-optimizer strategy, an explicit contract-valid `initial_balance` may be used.
When the caller omits it, omit it from `pt_submit_run` even if display capital is absent; FM retains
its existing default.

### 4. Observe Lifecycle and Read Data

Use the submit response as the first snapshot. For lifecycle monitoring, call `pt_get_run`; never
poll `pt_get_portfolio`. Keep polling bounded and user-visible, and stop when terminal. If a caller
asks only for current state, make one detail call.

Use each data tool for its distinct meaning:

- Current assets/current PnL: call `pt_get_portfolio` once. Report `freshness.age_ms`, `stale`, and
  `retry_after_s`; explain cached or stale data without forcing refresh. This is a live manual
  collection protected by a PB 60-second per-run guard, and failed downstream attempts also consume
  that window.
- Historical positions: call `pt_list_positions`. Honor symbol, side, open/close time filters,
  sort/order, bounded limit, and opaque cursor exactly. Closed-position realized return and current
  PnL are different semantics; never rename or derive one from the other.
- Execution records: use `pt_list_fills` for fills and `pt_list_funding` for funding cash flows.
  Do not infer closed-position semantics from fills.
- Strategy code: use `pt_get_code` only when asked and present only its bounded text/content type.
  Never treat it as raw YAML or expose any rejected internal reference.

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

Use `pt_create_strategy_portfolio` for the first exact composition and
`pt_revise_strategy_portfolio` only when the user explicitly changes the version. Display and
confirm every StrategyVersion handle and weight before either mutation. Read exact parent/version
state with `pt_get_strategy_portfolio` and `pt_get_strategy_portfolio_version`.

Before `pt_submit_portfolio_backtest`, confirm the exact PortfolioVersion, total initial cash, dates,
and optional fee strings. The total cash is allocated exactly across sleeves; child StrategyRuns
are ordinary independent runs. Observe with `pt_get_portfolio_backtest` and read the completed
aggregate backtest result with `pt_get_portfolio_backtest_result`.

Portfolio Paper can start only from one completed PortfolioRun. Before
`pt_submit_portfolio_paper`, display and confirm the source PortfolioRun, its exact total/source
capital, start date, leverage, and that every child is an independent static sleeve. Do not offer a
Paper-time capital override. To change total Paper capital, first complete a new PortfolioRun at
that capital.

Use `pt_get_portfolio_paper` for the parent lifecycle and ordered child handles/status. Present child
status in component order and label every child `independent sleeve`. Do not claim parent aggregate
positions exist. Do not claim parent net positions, shared margin, or a parent real-time/equity
curve exists.

Before `pt_stop_portfolio_paper`, show the exact parent handle, explain that stop fans out to its
children and is terminal, and obtain explicit confirmation. Call stop once, then reconcile with
`pt_get_portfolio_paper`; never retry automatically or offer resume.

## Safe Errors

Explain safe failures as actionable product states without exposing downstream text:

- `source_strategy_ineligible`: choose another eligible completed source or complete the missing
  source prerequisite. Use only its returned closed `eligibility_reasons` as described above.
- `paper_initial_balance_unavailable`: the requested ordinary Paper balance cannot be used safely;
  omit an override only when the user intended FM's ordinary default.
- `source_capital_unavailable`: an optimizer source lacks a trusted exact Product capital binding;
  use a PB-created versioned source and never guess from FM binary64 parameters.
- `source_capital_mismatch`: final FM validation rejected the exact bound capital; stop rather than
  rounding, quantizing, choosing another value, or resubmitting automatically.
- `optimizer_execution_unavailable` or `optimizer_config_not_caller`: use another completed source
  with closed caller-effective optimizer evidence.
- `portfolio_optimizer_portfolio_value_mismatch`: create a new source backtest at the desired
  capital; do not override Paper capital.
- `portfolio_optimizer_backtest_config_mismatch`: the frozen source execution does not match the
  approved optimizer intent; use an eligible caller-effective run.
- `portfolio_optimizer_paper_config_mismatch`: the Paper execution does not match the source run's
  frozen optimizer configuration; reconcile with the run detail and do not resubmit automatically.
- `source_validation_unavailable`: source discovery could not complete its bounded FM validation;
  keep the item visible as `provider_validation_required` and do not describe it as eligible.
- `quantai_unavailable` or another retryable mutation error: the safe reason may be actionable, but
  the mutation can still be ambiguous. Reconcile authoritatively and never change its idempotency
  identity or blindly submit again.
- authoritative authorization/scope failure with active gates: complete fresh staging consent for
  the minimum required Paper scopes.
- rate/freshness response: honor returned cache, stale, and retry-after information.

If the response contains no recognized closed reason, report only the generic safe error code and
retryability. Never quote, reinterpret, or ask for a hidden provider message.

Do not fetch or cite `operation.paper_trade.submit` or an optimizer Paper guidance entry in this
release. Its upstream catalog wording may conflict with the current implementation. The tools,
current product contract, and this skill are authoritative until that catalog is corrected.
