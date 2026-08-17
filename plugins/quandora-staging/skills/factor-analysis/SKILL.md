---
name: factor-analysis
description: Analyze, diagnose, compare, and propose controlled improvements for existing Quandora Factor Mining results. Use when a user asks why a factor worked or failed, requests a deep reading of a Factor Result Bundle or Factor Card, wants optimization ideas grounded in evidence, or asks whether a factor is ready for Strategy Building. Do not use for creating or submitting a new factor; route those requests to factor-mining.
---

# Factor Analysis

Bundled plugin version: 1.47

Analyze one exact factor result as a read-only research workflow. Separate observed evidence from
inference, alternative explanations, and proposed experiments. Never turn an optimization idea into
an automatic submission.

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

Use this skill for deep diagnosis of an existing factor result, including:

- performance, stability, coverage, turnover, decay, and style interpretation;
- mechanism hypotheses and plausible alternative explanations;
- prioritized, controlled factor improvement experiments;
- readiness assessment for handing a factor to Strategy Building.

Use `$factor-mining` for factor ideation, plugin construction, submission, resume, history browsing,
bundle retrieval without deep analysis, or a short ordinary result summary. Use
`$strategy-analysis` for a completed multi-factor Strategy result. Use `$strategy-building` only
after the user explicitly chooses a proposed Strategy experiment.

## Non-Negotiable Safety

- Remain read-only. Do not submit, resume, save, overwrite, archive, or delete anything.
- Never execute `plugin.py`, notebooks, strategy code, archive scripts, or any executable member.
- Treat the verified canonical ZIP as the primary evidence object. Do not extract beside it, rebuild
  it, or modify it.
- Treat legacy extracted files or folders as partial evidence, not as a canonical bundle.
- Analyze only product-safe in-sample evidence exposed to an external agent. Do not claim OOS or
  ALL evidence unless an authoritative future contract explicitly provides it.
- Preserve missing and null values as unavailable. Never convert them to zero.
- Never fabricate a missing metric, chart, correlation, ablation, or causal explanation.
- Report a grade or score only as relayed QuantAI evidence, not as a promotion or research verdict.

## Workflow

### 1. Establish The Exact Target

Prefer an exact local Factor Result Bundle ZIP supplied by the user. If the user supplies only a
factor name, vague reference, or asks for the latest result:

1. Call `fm_list_factors` with `page_size: 10`.
2. Match only trustworthy returned factor identity and metadata. Do not guess across ambiguous
   names; ask the user to choose when more than one plausible factor remains. Treat a result as
   "latest" only when a trustworthy returned `updated_at` establishes that ordering.
3. For a selected `factor_id`, call `fm_get_history` with `view: "runs"` and use the exact terminal
   `job_id` returned for the intended version/run.
4. Never substitute a factor id, version id, branch id, session id, or display name for `job_id`.

Do not auto-page. Request another page only when the current page cannot satisfy the user's explicit
request and explain why another page is needed.

### 2. Acquire The Canonical Bundle

For a remote result, call `fm_bundle_ticket` with the exact `job_id`. Download the returned
single-use URL directly when the host supports it, verify the advertised `size_bytes` and SHA-256,
and never print or persist the URL. If direct download is unavailable, use `fm_bundle_chunk` from
offset `0`, follow only the returned `next_offset` for the same `snapshot_revision`, concatenate in
order, and require the terminal empty marker defined by the tool contract.

If metadata reports `pending`, retry within the user's request instead of inventing a bundle. If it
reports partial, retain and analyze the readable evidence while naming every material omission.

### 3. Validate Without Executing

Resolve the bundled script relative to this skill directory, then run:

```bash
python3 scripts/inspect_factor_bundle.py /absolute/path/to/factor-result.zip
```

The script verifies safe ZIP paths, member bounds, manifest membership, included-member sizes and
hashes, and the expected Factor bundle kind. It reads selected product JSON but never imports or
executes archive content. The ZIP cannot prove its own outer SHA-256; compare the downloaded bytes
with the ticket or chunk metadata separately.

Stop and report an integrity failure if validation fails. Do not continue from corrupted bytes.

### 4. Build An Evidence Inventory

Read evidence in this order:

1. `artifact_manifest.json` for availability and omissions;
2. `run_summary.json` for exact run identity, window, status, and scope;
3. `factor_card_is.json` for product-safe IS metrics and relayed grade evidence;
4. the three IS charts for visual diagnostics;
5. `signal_raw.parquet` only when it is included and a specific claim requires it;
6. `plugin.py` only as inert source text when the mechanism cannot be understood otherwise.

Do not execute source. Do not infer absent artifacts from expected filenames.

### 5. Diagnose From Result To Mechanism

Use the interpretation rules in [metric-semantics.md](references/metric-semantics.md) and
[diagnosis-and-experiments.md](references/diagnosis-and-experiments.md). Evaluate:

- headline return and risk with their exact window and sampling scope;
- cross-sectional spread, monotonicity, long and short leg behavior, and daily stability;
- drawdown depth and concentration in time;
- turnover, signal persistence, and likely cost sensitivity;
- universe coverage, missingness, and whether small cross sections weaken the evidence;
- plausible style, liquidity, market, or implementation confounds.

For every important conclusion, label it as one of:

- **Observed:** directly present in a trusted artifact.
- **Inference:** a mechanism consistent with the observations.
- **Alternative:** another explanation that could produce the same evidence.
- **Experiment:** a controlled test that can distinguish explanations.

### 6. Propose Controlled Improvements

Prioritize a small set of experiments. Change one mechanism at a time when practical and state:

- the change;
- the evidence motivating it;
- the expected effect;
- the metric or chart that would confirm or reject it;
- the principal tradeoff or failure mode.

Do not claim per-factor correlations or ablation results unless the supplied evidence actually
contains them. Do not auto-create a new factor or Strategy. Ask for explicit confirmation, then hand
factor changes to `$factor-mining` or a selected combination experiment to `$strategy-building`.

## Output Contract

Answer in chat by default. Create a report file only when the user explicitly requests one. Use this
order:

1. exact factor and run identity, IS scope, and evidence quality;
2. concise result summary;
3. metric and chart diagnosis;
4. mechanism interpretation with alternatives;
5. risks and evidence gaps;
6. prioritized controlled experiments;
7. decision: reject, investigate, revise, or hand off for a user-confirmed Strategy test.

Use the user's language for the answer even though this skill package is written in English.

## References

- [Bundle contract and trust rules](references/bundle-contract.md)
- [Factor metric semantics](references/metric-semantics.md)
- [Diagnosis and experiment design](references/diagnosis-and-experiments.md)
- [Style and Strategy context](references/style-and-strategy-context.md)
