---
name: strategy-portfolio
description: Composes two to five exact Quandora StrategyVersions into a backend-enforced equal-weight Portfolio and evaluates one compatible completed source set. Use when the user asks to create, revise, inspect, or evaluate a Strategy Portfolio. Do not use for single-Strategy construction or Paper execution.
---

# Quandora Staging Strategy Portfolio

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

Tool names in this Skill are canonical actions on the configured `quandora-staging` MCP
dependency. Let the host resolve its required server-qualified form. If an action is unavailable,
use only the host-native reconnect/update flow; never invent an alias, bypass MCP with raw HTTP,
or paste credentials.

## Portfolio Model

- The executable contract accepts two to five distinct exact `strategy_version_id` values. Route
  one Strategy to `$strategy-building`; do not advertise a one-sleeve Portfolio.
- Public create and revise inputs contain only exact component `strategy_version_id` values. Do
  not ask for, calculate, or submit `target_weight`; the backend derives equal weights and the
  returned PortfolioVersion is authoritative.
- Creation may include `initial_cash`; omission uses the backend default. Treat the schema and
  returned validation as authority for the minimum and increment, and never repair an invalid
  value silently.
- A PortfolioVersion is immutable. A changed component creates a new version. Creation-time
  capital is frozen for the Portfolio; changing it requires a new Portfolio rather than an
  evaluation or Paper override.
- A legacy Portfolio with `initial_cash=null` remains readable but cannot be evaluated or deployed.
  Report the backend migration requirement instead of substituting a default.
- Components are independent capital sleeves. There is no signal fusion, shared margin, capital
  transfer, periodic rebalance, provider-order netting, or position netting.
- Evaluation reuses one exact completed, non-optimizer source StrategyRun per component. It does
  not create child StrategyRuns and does not call QuantAI or another provider.
- The evaluation normalizes each source equity curve by that source's initial equity, then applies
  the Portfolio target-capital weights. The result is research evidence, not a Paper account.
- Treat Portfolio, PortfolioVersion, PortfolioRun, StrategyVersion, and source StrategyRun handles
  as distinct opaque owner-scoped identifiers.

## Workflow

### Discover, Create, or Revise

When no exact Portfolio handle is supplied, call `list_strategy_portfolios` once with a bounded
`page_size` and `include_archived=false` unless archived records were requested. Send a supplied
name or keyword as `query` and an exact public status through `filters`; omit search fields only
for browse or recent-items requests. Use another page only when the user requests it, preserving
the same query, filters, archive mode, and page size and copying `next_page_token` byte-for-byte.

For a new composition, require two to five exact StrategyVersion handles. Never guess versions
from similar names. If exact versions do not exist, hand off to `$strategy-building` and stop.

Before the first create or revise mutation, read the authoritative Portfolio guidance. Show the
complete StrategyVersion selection, optional name, creation-time capital, and independent-sleeve
semantics, then obtain explicit confirmation. Do not add weights to the payload. A revise replaces
the complete StrategyVersion selection from one exact base PortfolioVersion, retains the frozen
Portfolio capital, and requires its own confirmation.

A timeout or ambiguous mutation response is not proof of failure. Do not submit a changed request
or create a replacement. Reconcile only with an exact returned handle; otherwise report the
ambiguity and stop for user direction.

### Select Exact Source Runs

After selecting one exact PortfolioVersion, call
`list_eligible_strategy_portfolio_source_runs` with a bounded `per_component_limit`. It returns
each ordered component, eligible completed non-optimizer sources, each source's exact
`backtest_period`, and an `alignment` decision.

- `alignment.status=compatible`: require `complete=true` and choose one exact returned
  `alignment.compatible_source_sets[]` mapping. Preserve every paired `strategy_version_id` and
  `source_strategy_run_id`; never combine rows from different returned sets.
- `alignment.status=alignment_required`: each component has eligible evidence but no common
  execution window. Do not submit or trigger replacement backtests. Report that automatic
  full-window preparation is unavailable until the upstream mutation contract exists.
- `alignment.status=source_evidence_incomplete`: make one bounded re-read because retained `summary` or
  `equity_curve` evidence may still be synchronizing, then report the incomplete state.
- `alignment.status=alignment_unknown`: fail closed during a rolling backend deployment and do not
  submit.

Do not ask the user to customize source selectors. If several compatible sets are returned without
an authoritative backend default, report ambiguous readiness and stop. Never invent, reuse across
components, or substitute a downstream/internal identifier.

### Evaluate and Read Result

Before `submit_strategy_portfolio_evaluation`, show and confirm:

- the exact PortfolioVersion;
- the exact creation-time `initial_cash` returned by the Portfolio read;
- one intact compatible source set;
- that the aligned sources are reused without rerunning a Strategy or calling a provider.

Submit only `portfolio_version_id` and the exact returned compatible `source_runs` set. Do not send
capital, dates, fees, weights, optimizer fields, or execution overrides. The server obtains frozen
Portfolio capital and re-verifies the selected sources' execution facts. Portfolio definition and
evaluation are separate mutations with separate confirmations.

If submit returns retryable `source_result_evidence_unavailable`, treat it as retained-evidence
synchronization, not proof that the StrategyRun failed. Do not resubmit automatically and do not
start a replacement backtest. Re-read eligible sources once with the same exact PortfolioVersion,
then report the remaining unavailable state for user direction.

Use the submit response as the first PortfolioRun snapshot. Observe only that exact run with
`get_strategy_portfolio_evaluation`; keep polling bounded and user-visible. Confirm each component
reports `execution_contract=source_reuse_v1` and preserves the selected owner-local source handle.

After completion, call `get_strategy_portfolio_evaluation_result`. Present normalized aggregate
metrics and `equity_curve.points[].ts/equity`. For new source-reuse results, preserve the returned
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

Use the user's language for the answer while preserving tool names, schema fields, and returned
identifiers exactly.
