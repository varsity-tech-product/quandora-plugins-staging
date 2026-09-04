# Ordinary Strategy Workflow

Load this reference after routing to a single ordinary cross-sectional Strategy.

## Capabilities and Factor Selection

For a bare available-factor request, call only `list_eligible_strategy_factors` with one bounded
page. Put a supplied name or keyword in `query`; put exact public status, task, universe, or bar
values in `filters`; use `include_factor_ids`, `factor_type`, or `tags` only when the user provided
that constraint. Omit search fields only for a browse request. Do not auto-page or call Factor
Mining inventory/status. A continuation preserves every search constraint and copies the opaque
page token byte-for-byte.

For composition, call `get_strategy_capabilities` once. Treat the live
`submit_adhoc_strategy_backtest` input schema and capability `caller_supplied_fields` as the sole
request boundary. Preserve only caller choices allowed by both, omit optional fields the user did
not choose, and treat metadata marked as not caller supplied as read-only server behavior. Do not
copy server-managed values into Skill guidance or confirmation, and do not add any field absent
from the live submit schema. Stop on any contract/schema mismatch.

Every selected Factor must be returned by `list_eligible_strategy_factors`. Display returned ID,
name, Task category, rating/grade status, Source, and CS Sharpe when present. Classify Source only
from `source_kind` and `shared`: Official, Mine, Shared, or Unavailable. Ratings do not determine
eligibility; Grade F remains selectable when returned as eligible.

Use `get_eligible_strategy_factor` only for a requested exact Factor or a small stated shortlist.
Ask the user to select unless they explicitly delegated selection.

For Shared candidates, call `list_shared_strategy_factor_candidates`. Before
`admit_shared_strategy_factor`, show and confirm the exact candidate, FactorVersion, and root-level
Factor backtest evidence. Then require the admitted Factor to appear in the eligible inventory.

An agent-mined/authored Factor follows the eligible inventory and is never re-imported. The
`import_strategy_factor` branch is allowed only for a complete external `plugin.py` supplied by the
user, explicitly requested for import, and supported by the current host schema. It requires a real
current-owner session and the approved import guidance; never invent lifecycle identifiers.

## Payload and Confirmation

For equal weights use distinct `factor_ids`; for custom weights use distinct positive finite
entries totaling 1 within the contract tolerance. Validate finite numeric values, ranking,
direction, dates, and rebalance bounds against the current contract. Preserve explicit caller
choices and omit optional fields the user did not choose. If the user requests a field absent from
the live submit schema, explain that it is not caller-configurable without guessing or quoting
server-managed values.

Choose the submitted name from a valid user name or the exact selected Factor themes and effective
configuration. Before `submit_adhoc_strategy_backtest`, show the complete safe name, factors or
weights, ranking, direction, dates, and rebalance choices that will actually be sent, then obtain
explicit confirmation. Do not display or ask for confirmation of server-managed fields.

Call the mutation once. Preserve returned `result.run.commandRequestId` only as the command
continuation handle. Once non-null, preserve `result.run.strategyRunId` as the canonical FM
StrategyRun handle for detail, result, artifact, rerun, and downstream reads. The two identifiers
are never interchangeable. `strategyFolderId`, `strategyId`, Factor IDs, rating provenance, and
downstream identifiers are not substitutes. An ambiguous response without a command handle does
not authorize resubmission.

## Observation and Failure

The submit response is the first snapshot. While no canonical `strategyRunId` is available, follow
returned retry guidance and use a bounded, user-visible sequence of
`continue_strategy_backtest(command_request_id=<commandRequestId>)` calls. It re-drives only that
command; do not pass the command id to `get_strategy_backtest`. Once `strategyRunId` exists, use it
as `run_id` for detail and result reads. If the run remains active after the bounded observation
window, report it and stop before archive or bundle work.

After terminal status, observe archive state on the same run with bounded reads and returned retry
guidance. Request a Result Bundle only after archive state is completed or partial.

`resultOutcome={status:"no_result",reasonCode:"zero_orders",orderCount:0}` is successful execution
with no orders and no performance/Paper eligibility. Do not continue or rerun it to manufacture
evidence.

For a failed terminal run, safe diagnostics and `fmRetryable` are advisory. A compile/Lean failure
or false/absent retryability means repetition risk, not a prohibition. Use
`rerun_strategy_backtest` only after the user requests a rerun, the exact failed source has the
required immutable run and StrategyVersion lineage, the repetition risk is shown, and a separate explicit
confirmation is obtained. Call it once; never resume the failed source or rebuild a new payload.
