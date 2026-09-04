---
name: paper-trading
description: Starts, monitors, inspects, or terminally stops simulated Quandora Paper execution. Use when the user asks about Paper PnL, positions, equity, fills, funding, code, or a completed Portfolio handoff. Do not use to create or backtest Strategies or Portfolios.
---

# Quandora Staging Paper Trading

Use this skill through the authenticated `quandora-staging` MCP connection. It owns simulated
execution only: eligible-source discovery, Paper start, lifecycle monitoring, execution data, and
terminal stop. It is staging-only and never represents live-money trading.

Route single-Strategy authoring/backtests to `$strategy-building`. Route multi-Strategy Portfolio
composition, source selection, evaluation, and aggregate result reads to `$strategy-portfolio`.
Route deep diagnosis of a completed single-Strategy result to `$strategy-analysis`. If no eligible
source exists, hand off and stop before any Paper mutation.

Use only the configured `quandora-staging` MCP connection. Never ask the user to paste secrets into
chat.

## Tools

Use only the minimum relevant subset:

- Source discovery: `list_paper_trade_sources`, `get_paper_trade_source`.
- Single Paper lifecycle: `list_paper_trades`, `get_paper_trade`, `start_paper_trade`,
  `stop_paper_trade`.
- Single Paper data: `refresh_paper_trade_account_snapshot`,
  `list_closed_paper_trade_positions`, `get_paper_trade_equity_curve`,
  `list_paper_trade_fills`, `list_paper_trade_funding`, `get_paper_trade_strategy_code`.
- Portfolio Paper lifecycle: `start_strategy_portfolio_paper_trade`,
  `get_strategy_portfolio_paper_trade`, `stop_strategy_portfolio_paper_trade`.
- Authoritative guidance when needed: `get_quandora_guidance` with
  `operation.paper_trade.submit`, without `sections`.

Never call Strategy or Portfolio definition/evaluation tools here. In particular, do not call
`create_strategy`, `revise_strategy`, `submit_strategy_backtest`,
`create_strategy_portfolio`, `revise_strategy_portfolio`, or
`submit_strategy_portfolio_evaluation`.

Tool names in this Skill are canonical actions on the configured `quandora-staging` MCP
dependency. Let the host resolve its required server-qualified form. If an action is unavailable,
use only the host-native update/reconnect/browser-consent flow. Never invent an alias or bypass the
configured MCP connection.

For list actions, use a supplied name or keyword as `query` and exact public status, submit state,
source kind, or Strategy kind as `filters`. Omit search fields only for browse or recent-items
requests. Preserve the same query, filters, archive mode, and page size on continuation and copy
opaque page tokens byte-for-byte. Never combine legacy `limit`/`offset` fields with cursor search.

## Safety and Data Model

- Treat canonical FM StrategyRun, Portfolio-local source selectors, PaperTradeRun, PortfolioRun,
  PortfolioPaperRun, child Paper handles, and cursors as distinct opaque owner-scoped identifiers.
  A PB command id is never a Paper source, and a Portfolio-local selector is not a canonical FM
  StrategyRun identifier.
- Money, leverage, and allocated cash are canonical decimal strings. Never send JSON numbers.
- Paper inherits its source Strategy universe; it is not caller-configurable.
- A mutation timeout or ambiguous response is not proof of failure. Do not retry with a fresh or
  changed request. Reconcile only through an exact returned handle.
- Never automatically stop, restart, resubmit, revise, change capital, mine a factor, or trigger
  another workflow because of PnL or losses.
- Stop is terminal, not pause. There is no Paper resume, archive/unarchive, parent aggregate
  position, parent net position, or parent Portfolio Paper equity capability.
- `paper_read_unavailable` is retryable according to the returned error; `paper_read_rejected` is
  non-retryable. Unknown or extended reasons fail closed and must not be reclassified.

## Single-Strategy Paper

### Select an Eligible Source

Paper starts from one exact existing completed canonical FM StrategyRun returned by
`list_paper_trade_sources` or supplied by the user. This skill must not create or revise the source.
Use the returned `source_strategy_run_id` unchanged for source detail and Paper start; never
substitute a StrategyFolder, Strategy, StrategyVersion, PB command, or Paper run id. If no handle
is supplied, list one bounded page and show the safe Strategy label/version,
lifecycle and submit state, source capital, eligibility, and closed `eligibility_reasons`. Ask the
user to select one exact source.

`eligible` is a conservative server preflight; final submit authority remains the submit action.
`provider_validation_required` is not proof of eligibility. Unknown, missing, contradictory, or
unsupported evidence fails closed.

Historical optimizer-backed sources may remain visible for read compatibility. They are never
eligible for new Paper execution. If `strategy_optimizer_not_supported` is returned, do not call
`start_paper_trade`, do not retry, and do not attempt to repair or override the source. Offer a new
non-optimizer Strategy experiment through `$strategy-building` after explicit user direction.

When `source_strategy_no_result` is present, the completed source produced zero orders and is
ineligible for Paper. Do not submit, retry, or manufacture performance evidence. Offer a handoff
to `$strategy-analysis` or a controlled new Strategy experiment.

### Confirm and Start

Before `start_paper_trade`, show the exact selected eligible non-optimizer source, safe
label/version, optional ISO `start_date`, optional canonical `initial_balance`, and optional exact
leverage. Obtain explicit confirmation and omit every optional field the user did not choose.

### Monitor and Read Data

Use the start response as the first snapshot. Use `get_paper_trade` for lifecycle monitoring; keep
polling bounded and user-visible. Do not poll the account-snapshot refresh tool.

- `refresh_paper_trade_account_snapshot`: one current assets/PnL collection. Report freshness,
  stale state, and retry delay. It consumes the per-run manual refresh gate even on downstream
  failure, so never loop it.
- `list_closed_paper_trade_positions`: closed net-position lifecycle history only.
- `get_paper_trade_equity_curve`: choose exactly one lookback, bounded-sampling, or legacy mode.
  Label pre-live padding as synthetic, not observed performance.
- `list_paper_trade_fills` and `list_paper_trade_funding`: execution and funding records.
- `get_paper_trade_strategy_code`: use only when explicitly requested and present bounded text.

Preserve opaque cursors byte-for-byte. Never infer a Strategy name from PnL, time, direction,
code, or neighboring records.

### Stop

Before `stop_paper_trade`, show the exact run and current known state, explain that stop is
terminal, and obtain explicit confirmation. Call stop once, then reconcile with
`get_paper_trade`. Never retry automatically or offer resume.

## Strategy Portfolio Paper

Portfolio Paper starts only from one exact completed source-reuse PortfolioRun produced by
`$strategy-portfolio`. This skill does not create, revise, or evaluate the Portfolio. If no
completed evaluation exists, hand off and stop.

Before `start_strategy_portfolio_paper_trade`, show the exact PortfolioRun, start date, leverage,
each component's selected owner-local `source_strategy_run_id`, and allocated cash. Explain that
each child is an independent static sleeve and its `initial_balance` equals that component's
`allocated_cash`. The Paper command has no capital override. To change total capital, create a new
Portfolio through `$strategy-portfolio`; evaluation and Paper both inherit creation-time capital.
Then obtain a new Portfolio evaluation and Paper confirmation.

Use `get_strategy_portfolio_paper_trade` for the parent lifecycle and ordered children. Verify and
present the exact source lineage, safe Strategy/StrategyVersion identity, child Paper handle,
allocated cash, and state for each sleeve.

For a child sleeve with a non-null exact `child_paper_run_id`, ordinary single-Paper read actions
may read that child. Use `get_paper_trade` for lifecycle, at most one
`refresh_paper_trade_account_snapshot` call for current assets, positions, and PnL, and the equity,
closed-position, fill, or funding action only when requested. Apply the same freshness and
no-polling rules to every child. Never pass the parent PortfolioPaperRun identifier to a child
Paper read.

When the user asks which child contributes the most current profit, compare child Paper PnL on one
consistent observation pass and report each snapshot's freshness. This is Paper PnL contribution,
not historical backtest return. The parent Portfolio projection is authoritative for each
component's safe Strategy and StrategyVersion lineage. Do not pass its Portfolio-local
`source_strategy_run_id` to ordinary `get_paper_trade_source` or Strategy tools. Hand off to
`$strategy-analysis` or `$strategy-building` for historical evidence only when a separate exact
canonical FM `strategyRunId` is explicitly returned; never substitute a Portfolio-local selector,
StrategyVersion, child Paper, or downstream identifier.

Never claim shared margin, capital transfer, signal fusion, order netting, parent aggregate
positions, parent real-time PnL, or a parent equity curve.

Before `stop_strategy_portfolio_paper_trade`, show the exact parent handle, explain that terminal
stop fans out to children, and obtain explicit confirmation. Call stop once, then reconcile with
`get_strategy_portfolio_paper_trade`; never retry automatically or offer resume.

## Final Response

State whether the result concerns one Paper trade or Portfolio Paper, its lifecycle state, and the
relevant freshness or lineage semantics. If a handoff is needed, state that no Paper mutation was
performed.

Use the user's language for the answer while preserving tool names, schema fields, and returned
identifiers exactly.
