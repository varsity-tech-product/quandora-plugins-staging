---
name: strategy-building
description: Builds one non-optimizer Quandora Strategy and lists available, eligible, or selectable factors. Use when the user asks to create, revise, backtest, continue, rerun, retrieve, or export that Strategy. Do not use for multi-Strategy Portfolio composition, Paper execution, or deep diagnosis.
---

# Quandora Staging Strategy Building

This skill owns one Strategy: eligible-factor selection, ordinary Strategy submission, immutable
versioned Strategy definitions, single-Strategy backtests, reruns, and ordinary Strategy Result
Bundle delivery through `quandora-staging`.

New optimizer authoring and execution are retired. Never send `portfolio_optimizer`, including
explicit null, in Strategy create, revise, or run inputs. Historical optimizer-backed versions may
be read through safe classification only and cannot start a new Strategy, Portfolio, or Paper run.

Route two-or-more StrategyVersion composition and source-reuse evaluation to
`$strategy-portfolio`, simulated execution to `$paper-trading`, and deep diagnosis of completed
evidence to `$strategy-analysis`.

## Tools

Use only the minimum relevant subset:

- Capability and eligible factors: `get_strategy_capabilities`,
  `list_eligible_strategy_factors`, `get_eligible_strategy_factor`.
- Shared/external admission: `list_shared_strategy_factor_candidates`,
  `admit_shared_strategy_factor`, `import_strategy_factor`.
- Ordinary run lifecycle: `submit_adhoc_strategy_backtest`, `list_strategy_backtests`,
  `get_strategy_backtest`, `continue_strategy_backtest`, `rerun_strategy_backtest`.
- Ordinary Result Bundle: `create_strategy_result_bundle_download`,
  `read_strategy_result_bundle_chunk`.
- Versioned definition/source: `create_strategy`, `revise_strategy`, `get_strategy`,
  `get_strategy_version`, `submit_strategy_backtest`.

Use `get_quandora_guidance` only for the exact approved workflow described in supporting material.
`get_paper_trade_source` is a read-only handoff used only to observe an explicit versioned source;
its primary owner remains `$paper-trading`.

Tool names in this Skill are canonical actions on the configured `quandora-staging` MCP
dependency. Let the host resolve its required server-qualified form. If an action is unavailable,
do not invent another name or use an alternate service.

## Load Supporting Material Selectively

- If authentication or tool exposure is blocked, load
  [Connection and Security](references/connection-and-security.md).
- For ordinary factor selection, submission, observation, or rerun, load
  [Ordinary Strategy Workflow](references/ordinary-strategy-workflow.md).
- For an immutable versioned definition/source or a historical optimizer read, load
  [Versioned Strategy Workflow](references/versioned-strategy-workflow.md).
- Only after an ordinary terminal run/archive or an export request, load
  [Strategy Result Bundle Delivery](references/result-bundle-delivery.md).

Do not load versioned-source or Result Bundle transport instructions for a bare factor-list request.

## Route First

- Bare requests for available, eligible, or selectable factors call only
  `list_eligible_strategy_factors`, one bounded page, then stop. Use a supplied name or keyword as
  `query`; use exact public status, task, universe, or bar values as `filters`; use
  `include_factor_ids`, `factor_type`, or `tags` only when the user provided that constraint.
- Requests for caller-owned Factor Mining families/history route to `$factor-mining`.
- One ordinary Strategy uses the ordinary workflow.
- An immutable versioned Strategy definition/source uses the versioned workflow.
- Two to five exact StrategyVersions requested as one Portfolio route to `$strategy-portfolio`;
  Portfolio weights are backend-derived and are not Strategy-building input.
- “Optimize this result” routes to `$strategy-analysis`, not optimizer authoring.

## Ordinary Strategy

Follow [Ordinary Strategy Workflow](references/ordinary-strategy-workflow.md):

1. read the current capability contract once;
2. verify exact selected Factors in the eligible inventory;
3. validate one canonical equal- or custom-weight payload;
4. show caller-controlled choices plus the backend-fixed run assumptions and obtain explicit
   confirmation;
5. submit once and observe only the returned run;
6. treat terminal rerun as a separate explicitly confirmed mutation.

Do not create a Strategy Portfolio for one Strategy. Do not call Paper start tools here.

## Versioned Strategy Source

Follow [Versioned Strategy Workflow](references/versioned-strategy-workflow.md). Definition or
revision and source backtest are separate mutations requiring separate confirmations. Every new
specification is non-optimizer and source run capital belongs to `submit_strategy_backtest`.

This path ends with bounded source lifecycle/eligibility evidence. A later Paper request hands the
exact eligible completed source to `$paper-trading`; no Paper mutation occurs here.

## Result Delivery

The ordinary Strategy main run must be terminal and archive state completed or partial before
bundle delivery. Follow
[Strategy Result Bundle Delivery](references/result-bundle-delivery.md).

The default completed local path is
`Quandora staging result/strategy/<strategy_slug>.zip`. Never save a Strategy ZIP in the Factor
directory or treat the exported ZIP as server-side analysis evidence.

## Safety

- Treat Strategy, StrategyVersion, StrategyRun, downstream lineage, Paper source, and Portfolio
  handles as distinct opaque owner-scoped identifiers.
- An ambiguous mutation response is not permission to resubmit, revise, rerun, or switch payloads.
- `continue_strategy_backtest` re-drives only a known non-terminal run.
- `fmRetryable` is advisory. A failed immutable run may be rerun only after exact lineage checks,
  repetition-risk disclosure, and explicit confirmation.
- Never infer Paper authority from completed research or start Paper from this skill.
- Never expose credentials, historical policy content, provider identities, internal URLs, or raw
  downstream payloads.

## Final Response

State the submitted Strategy name, workflow type, main-run/archive state, safe diagnostics, and the
verified Result Bundle path when saved. If a run remains in progress, state that bundle delivery
was not started. If handing off, state clearly that no Portfolio or Paper mutation occurred.

Never expose run handles in a general summary, tickets, download URLs, credentials, base64, or
internal service metadata.

Use the user's language for the answer while preserving tool names, schema fields, and returned
identifiers exactly.
