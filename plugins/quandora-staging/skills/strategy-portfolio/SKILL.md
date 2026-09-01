---
name: strategy-portfolio
description: Use when the user asks to combine two or more exact Quandora StrategyVersions with target weights, create or revise a Strategy Portfolio, select exact completed source runs, evaluate the normalized weighted Portfolio result, or read that result. Do not use for single-Strategy construction or any Paper-trading execution.
---

# Quandora Staging Strategy Portfolio

Bundled plugin version: 1.59

Use this skill through the authenticated `quandora-staging` MCP connection. It owns immutable
multi-Strategy composition, versioning, exact source-run selection, source-reuse evaluation, and
aggregate result reads. It never starts, monitors, or stops Paper trading.

Portfolio definitions use `strategy:portfolios.read` or `strategy:portfolios.write`. Source
discovery and evaluation reads use `strategy:portfolio_evaluations.read`; evaluation submit uses
`strategy:portfolio_evaluations.create`. A later Paper operation is a separate workflow using
`paper_trading:runs.*`.

Route single-Strategy factor selection, Strategy authoring, and single-Strategy backtests to
`$strategy-building`. Route simulated execution from a completed Portfolio evaluation to
`$paper-trading`. A one-component request remains a Strategy workflow; do not create a Portfolio
to represent it.

OAuth and credentials are host-managed. Never inspect, print, copy, store, or ask the user to paste
API keys, bearer/access/refresh tokens, authorization codes, PKCE verifiers, service tokens, or
account credentials.

## Tools

Use only the minimum relevant subset:

- Discovery: `list_strategy_portfolios`.
- Definition/version reads: `get_strategy_portfolio`, `get_strategy_portfolio_version`.
- Definition mutations: `create_strategy_portfolio`, `revise_strategy_portfolio`.
- Evaluation source discovery: `list_eligible_strategy_portfolio_source_runs`.
- Evaluation lifecycle: `submit_strategy_portfolio_evaluation`,
  `get_strategy_portfolio_evaluation`, `get_strategy_portfolio_evaluation_result`.
- Authoritative guidance when a mutation is needed: `get_quandora_guidance` with
  `operation.strategy.portfolio.manage`, without `sections`.

Never call `start_strategy_portfolio_paper_trade`, `get_strategy_portfolio_paper_trade`, or
`stop_strategy_portfolio_paper_trade` in this skill. Never submit a single-Strategy run as an
implicit prerequisite.

Some hosts display a server-qualified current name such as
`quandora_staging__create_strategy_portfolio`. This is the same canonical tool, not an alias. If a
canonical tool is unavailable, report that exact state and use only the host-native
reconnect/update flow; do not bypass MCP with raw HTTP or pasted credentials.

## Portfolio Model

- A Strategy Portfolio contains at least two distinct exact `strategy_version_id` values.
- Every `target_weight` is a positive canonical decimal string whose exact sum is `1`.
- Show the shortest plain non-exponent decimal form with no leading `+` or trailing fractional
  zero; for example, show and submit `0.4`, `0.3`, `0.3`, never JSON numbers.
- A PortfolioVersion is immutable. A changed component or weight creates a new version.
- Components are independent capital sleeves. There is no signal fusion, shared margin, capital
  transfer, periodic rebalance, provider-order netting, or position netting.
- Evaluation reuses one exact completed, non-optimizer source StrategyRun per component. It does
  not create child StrategyRuns and does not call QuantAI or another provider.
- FM normalizes each source equity curve by that source's initial equity, then applies the
  Portfolio target-capital weights. The result is research evidence, not a Paper account.
- Treat Portfolio, PortfolioVersion, PortfolioRun, StrategyVersion, and source StrategyRun handles
  as distinct opaque owner-scoped identifiers.

## Workflow

### Discover, Create, or Revise

When no exact Portfolio handle is supplied, call `list_strategy_portfolios` once with a bounded
`page_size` and default `include_archived=false`. Preserve `next_page_token` byte-for-byte and use
it only when the user asks for another page.

For a new composition, require two or more exact StrategyVersion handles. Never guess versions
from similar names. If exact versions do not exist, hand off to `$strategy-building` and stop.

Before the first create or revise mutation, read the authoritative Portfolio guidance. Validate
weights with exact decimal arithmetic. Show the complete composition and independent-sleeve
semantics, then obtain explicit confirmation. A revise replaces the complete composition from one
exact base PortfolioVersion and requires its own confirmation.

A timeout or ambiguous mutation response is not proof of failure. Do not submit a changed request
or create a replacement. Reconcile only with an exact returned handle; otherwise report the
ambiguity and stop for user direction.

### Select Exact Source Runs

After selecting one exact PortfolioVersion, call
`list_eligible_strategy_portfolio_source_runs` with a bounded `per_component_limit`. It returns
each ordered component and its eligible completed, non-optimizer sources. Require exactly one
returned `source_strategy_run_id` for every component and preserve its paired
`strategy_version_id`.

Show the exact source mapping and let the user confirm the selection. Never invent, reuse across
components, or substitute an FM/internal identifier. If `complete=false`, a component has no
eligible source, or the selected source is absent from the returned component, do not submit an
evaluation. Hand that component to `$strategy-building` for a new Strategy backtest and stop.

### Evaluate and Read Result

Before `submit_strategy_portfolio_evaluation`, show and confirm:

- the exact PortfolioVersion;
- exact positive canonical `total_initial_cash`;
- one exact source selector for every component;
- that no Strategy is rerun and no provider is called.

Submit only `portfolio_version_id`, `total_initial_cash`, and `source_runs`. Do not send dates,
fees, optimizer fields, or execution overrides. PB verifies that selected source runs share the
required execution facts. Portfolio definition and evaluation are separate mutations with
separate confirmations.

Use the submit response as the first PortfolioRun snapshot. Observe only that exact run with
`get_strategy_portfolio_evaluation`; keep polling bounded and user-visible. Confirm each component
reports `execution_contract=source_reuse_v1` and preserves the selected owner-local source handle.

After completion, call `get_strategy_portfolio_evaluation_result`. Present normalized aggregate
metrics and `equity_curve.points[].ts/equity`. For new source-reuse results, preserve FM's QuantAI
metric names and units: `summary.net_profit_pct`, `annual_return_pct`, `annual_std`,
`max_drawdown_pct`, `start_equity`, `end_equity`, and any returned `sharpe`, `sortino`,
`total_fees`, or `funding_net_cash_flow`. Percentage-suffixed metrics are percentage values;
`annual_std` is the annualized standard deviation. Historical results may retain older metric
aliases; report them as historical evidence and do not relabel new metrics. Preserve a returned
unavailable/error reason and retryability exactly; do not manufacture an empty ready result.

There is no separate Portfolio-analysis skill. Aggregate Portfolio result reading stays here;
`$strategy-analysis` owns completed single-Strategy evidence.

### Handoff to Paper

If the user explicitly wants simulated execution after a completed source-reuse PortfolioRun
exists, stop this workflow and hand that exact run to `$paper-trading`. Paper start is a new
mutation with its own confirmation. Never start it merely because evaluation completed.

## Final Response

State whether the outcome is a Portfolio definition/version, source selection, PortfolioRun, or
aggregate result. Summarize the user-visible composition, source lineage, and independent-sleeve
model. When handing off, state that no Paper run has started. Do not expose credentials, provider
identifiers, internal topology, or raw downstream payloads.
