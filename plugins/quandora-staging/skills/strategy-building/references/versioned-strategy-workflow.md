# Versioned Strategy Workflow

Load this reference when the user explicitly asks for an immutable versioned Strategy definition,
a versioned Paper source, or a safe read of a historical optimizer-backed version. Analytical
optimization of an existing result belongs to `$strategy-analysis`.

Before the first source mutation, read `operation.strategy.version.manage` through
`get_quandora_guidance`. Unknown or contradictory guidance fails closed.

Select 1–20 exact admitted rows from `list_eligible_strategy_factors`. Copy only each row's exact
`admission.factor_id`, `admission.factor_version_id`, and `admission.job_id` into
`factor_references`. Stop when any triple is absent.

Build one closed non-optimizer cross-sectional specification:

- strategy kind `cs`;
- optional equal/custom weighting aligned with the Factor references;
- required top/bottom N or percentage ranking;
- optional long-only, short-only, or neutral direction;
- optional rebalance bars.

Never include `portfolio_optimizer`, including explicit null.

Show exact Factors and the complete specification, then obtain confirmation. Use `create_strategy`
for a new definition or read the exact base with `get_strategy` and `get_strategy_version` before
`revise_strategy`. A new version is immutable.

Definition and backtest are separate mutations with separate confirmations. Before
`submit_strategy_backtest`, confirm the exact StrategyVersion, canonical decimal-string
`initial_cash`, dates, and optional fee strings. Capital belongs to the run and never creates a new
StrategyVersion.

Monitor the returned owner-local source only with `get_paper_trade_source`. Require an eligible,
completed non-optimizer source before handing off to `$paper-trading`.

Historical optimizer-backed StrategyVersions remain readable through the safe
`portfolio_optimizer={version,enabled}` classification, without raw policy. They are read-only:
do not revise or fork them into optimizer intent and do not submit a new Strategy backtest,
Portfolio evaluation, or Paper run. Treat `strategy_optimizer_not_supported` as non-retryable and
offer a new non-optimizer definition only after explicit user direction.
