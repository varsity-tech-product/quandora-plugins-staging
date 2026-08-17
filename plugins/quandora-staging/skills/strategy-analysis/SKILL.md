---
name: strategy-analysis
description: Analyze, diagnose, compare, and propose controlled improvements for existing Quandora cross-sectional Strategy results. Use when a user asks why a Strategy worked or failed, wants a deep reading of a Strategy Result Bundle or six-chart diagnostics, requests factor-combination optimization ideas, or asks whether a completed backtest is ready for Paper Trading. Do not use to compose or submit a Strategy; route those requests to strategy-building.
---

# Strategy Analysis

Bundled plugin version: 1.47

Analyze one exact cross-sectional Strategy run as a read-only research workflow. Pair Product
Backend's canonical run snapshot with the immutable Strategy Result Bundle whenever remote access is
available. Distinguish observed evidence from inference and proposed experiments.

OAuth and all credentials are handled by the host. Quandora access tokens expire after 7 days, and
the host MCP client should use its stored rotating refresh token automatically. Never inspect,
print, copy, store, or ask the user to paste API keys, bearer tokens, authorization codes, access
tokens, refresh tokens, PKCE verifiers, service tokens, or other credentials.

## Plugin Version Reminder

On the first entry into any Quandora skill in the current conversation, if the conversation history
does not already contain one successful `qd_check_plugin_version` call and no earlier version-check
attempt has occurred, call it once before the business entry point. Pass the bundled plugin version
declared by the current skill verbatim as `installed_version`; never infer it from memory, the
remote latest version, or the host name.

Treat the bundled version as an opaque release label: pass it verbatim and never parse, order, or
normalize it.

- If `update_available=false`, continue silently.
- If `update_available=true`, say exactly: `The latest Quandora plugin version is <latest_version>.
  Please update the plugin.` Then say: `A Quandora Staging MCP access token is valid for 7 days.
  After 7 days, use the prompt below to ask your agent to refresh the connection; it should use
  automatic refresh first and CLI re-authentication only if required.` Then provide this exact
  copyable prompt in a fenced `text` block: `Refresh the Quandora Staging MCP connection. If
  automatic refresh fails, re-authenticate it with the CLI.` Then immediately continue the user's
  original request.
- If `qd_check_plugin_version` is missing, disabled, invisible, or fails, do not report that the
  plugin is outdated, do not retry the check anywhere later in the current conversation, and
  continue the original request without a version message or any change to the business workflow.
  OAuth or connection failures continue through the existing safe connection-handling path; never
  bypass MCP with raw HTTP.
- Never install, update, uninstall, or reload a plugin; execute an update command; ask whether to
  update; immediately start OAuth or reauthorize merely because of the version result; provide a
  platform-specific command in the version reminder; or delay the original request. The copyable
  prompt is information for the user to invoke after 7 days, not permission to run it during the
  version check.
- A later entry into Factor Mining, Factor Analysis, Strategy Building, Strategy Analysis, or Paper
  Trading in the same conversation recognizes the prior successful version check and does not call
  it or remind again.
- Treat `qd_check_plugin_version` as optional for connection readiness. Its absence alone never
  triggers connection recovery or changes the required business-tool set.

The version check is not a business action and does not change any exact call-count, pagination, or
mutation constraint below.

<!-- end-plugin-version-reminder -->

## Scope And Routing

Use this skill for:

- performance, risk, turnover, exposure, and stability diagnosis;
- the six QuantAI cross-sectional diagnostic charts and their retained numeric data;
- factor-combination and style interpretation;
- controlled Strategy experiment design;
- Paper readiness assessment without starting or managing Paper Trading.

Use `$strategy-building` to list eligible factors, compose, submit, resume, retrieve, or archive a
Strategy. Use `$factor-analysis` for one Factor Mining result. Use `$paper-trading` only after the
user explicitly asks to start, monitor, inspect, or stop Paper Trading.

## Non-Negotiable Safety

- Remain read-only. Do not submit, resume, save, overwrite, archive, or mutate any run.
- Do not automatically create ablations, reruns, or Paper Trading runs.
- Never execute bundled code, logs, notebooks, scripts, or archive members.
- Treat the verified canonical ZIP as primary bundle evidence. Do not extract beside it, rebuild it,
  or modify it.
- Preserve null and missing values as unavailable, not zero.
- Never fabricate factor correlations, contributions, ablations, or causal claims.
- Treat grade and score as QuantAI-relayed evidence, not as a promotion or research verdict.
- Treat `ALL` as a combined scope that includes IS. Never describe it as pure OOS.

## Workflow

### 1. Establish The Exact Run

Prefer an exact `run_id` or local Strategy Result Bundle supplied by the user. When remote access is
available and no exact run id is supplied:

1. Call `sb_list_runs` once with `{}`. It returns the owner's newest-first page with default
   `limit: 10` and `offset: 0`.
2. Use returned identity, name, timestamps, status, and optional summary only to select a run.
3. If more than one plausible run remains, ask the user to choose. Do not guess.
4. Do not auto-page. Request another page only for an explicit older-run request that the first page
   cannot satisfy.

If an exact run id is supplied, skip discovery.

### 2. Read Canonical Composition And Parameters

Call `sb_get_run` with the exact `run_id`. Treat its canonical `composition` and `parameters` as the
authority for factor ids or weights, ranking, strategy type, window, capital, fees, rebalance bars,
and attribution.

If ranking was omitted at submission, the current Strategy default is neutral Top/Bottom 20%:
`ranking: {mode: "percent", value: 20}` with `strategy_type: "neutral"`. Report the effective
snapshot returned by `sb_get_run`; do not infer parameters from chart labels.

### 3. Acquire The Canonical Bundle

Call `sb_bundle_ticket` with the exact `run_id`. Download the single-use URL directly when supported,
verify the advertised `size_bytes` and SHA-256, and never print or persist the URL. Otherwise use
`sb_bundle_chunk` from offset `0`, follow only `next_offset` for the same `snapshot_revision`,
concatenate in order, and require the terminal empty marker.

The canonical bundle is the numerical analysis path and can include `artifacts/six_charts_data.json`.
Do not request that file through `sb_file_ticket`; the targeted artifact registry intentionally
keeps it bundle-only.

### 4. Validate Without Executing

Resolve the bundled script relative to this skill directory, then run:

```bash
python3 scripts/inspect_strategy_bundle.py /absolute/path/to/strategy-result.zip
```

The script validates safe paths, bounds, exact manifest membership, included-member sizes and
hashes, and the Strategy bundle kind. It summarizes selected product JSON and six-chart series
without extracting or executing archive content. Verify the whole ZIP separately against MCP
metadata because the internal manifest cannot contain its own outer digest.

Stop on integrity failure. A partial bundle remains usable only for the evidence that is actually
included; name omissions explicitly.

### 5. Pair Snapshot And Bundle

Use both sources:

- `sb_get_run` owns effective composition and parameters;
- the bundle owns immutable result artifacts and diagnostic evidence.

If only an offline ZIP is available, disclose that saved Strategy name, effective composition, or
parameters may be incomplete. Never fill them from assumptions. If only a run snapshot is available,
do not claim chart or performance evidence that requires the bundle.

### 6. Diagnose The Result

Read [artifacts-and-metrics.md](references/artifacts-and-metrics.md) and
[six-chart-diagnostics.md](references/six-chart-diagnostics.md). Evaluate:

- headline return, Sharpe, Sortino, drawdown, win/loss behavior, and fees;
- equity and drawdown shape, time concentration, and recovery;
- daily turnover using the Strategy single-sided `/2` convention;
- gross/net exposure and whether nominal neutrality held in practice;
- factor composition and whether explicit weights created concentration;
- all six chart families, including quantile ordering, long/short style, exposure, decay,
  prediction-style correlation, and turnover;
- evidence gaps and plausible market, liquidity, size, or implementation alternatives.

For every consequential conclusion, label it **Observed**, **Inference**, **Alternative**, or
**Experiment**.

### 7. Keep Portfolio Selection Separate From Diagnostic Buckets

Actual Strategy selection comes only from `sb_get_run.parameters.ranking`. Six-chart diagnostics use
an adaptive grouping scheme based on the median daily cross-section:

- median at least 20: 10 quantiles, minimum cross-section 20, diagnostic `top_pct: 0.10`;
- median at least 15: 5 quantiles, minimum 10, diagnostic `top_pct: 0.20`;
- median at least 9: 3 quantiles, minimum 6, diagnostic `top_pct: 0.30`;
- median below 9: 2 quantiles, minimum `max(2, min(4, median))`, diagnostic `top_pct: 0.50`.

`Q1` is the lowest prediction group and `QN` the highest. The diagnostic spread is
`(QN - Q1) / 2`. Do not call these adaptive buckets the actual Top/Bottom 20% portfolio unless the
effective run snapshot independently confirms a 20% ranking.

### 8. Propose Controlled Experiments

Prioritize a small number of changes. Each proposal must state the changed variable, motivating
evidence, expected effect, confirmation metric, and tradeoff. Favor one-variable changes when
possible. Examples include factor removal or reweighting, ranking breadth, rebalance cadence, fee
sensitivity, and one suspected style control.

Do not claim an automatic ablation or correlation matrix: the current bundle does not guarantee
per-factor correlations or precomputed ablations. Ask for explicit confirmation, then hand the
chosen test to `$strategy-building`.

### 9. Assess Paper Readiness Without Paper Mutation

Use [experiments-and-paper-readiness.md](references/experiments-and-paper-readiness.md). State whether
the evidence supports rejection, further research, a controlled rerun, or consideration for Paper.
Do not start Paper Trading. After explicit user confirmation, hand actual Paper operations to
`$paper-trading`.

## Output Contract

Answer in chat by default. Create a report file only when explicitly requested. Use this order:

1. exact run identity, effective composition/parameters, and evidence quality;
2. concise performance and risk summary;
3. metric, curve, and six-chart diagnosis;
4. factor-combination and style mechanism with alternatives;
5. risks and evidence gaps;
6. prioritized controlled experiments;
7. decision and optional user-confirmed handoff.

Use the user's language for the answer even though this skill package is written in English.

## References

- [Bundle contract and evidence pairing](references/bundle-contract.md)
- [Strategy artifacts and metric semantics](references/artifacts-and-metrics.md)
- [Six-chart diagnostics](references/six-chart-diagnostics.md)
- [Experiments and Paper readiness](references/experiments-and-paper-readiness.md)
