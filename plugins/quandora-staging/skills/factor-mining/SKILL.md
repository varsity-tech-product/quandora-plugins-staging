---
name: factor-mining
description: Use when the user explicitly asks about caller-owned or reusable Factor Mining factor families or history, or asks to construct, submit, backtest, resume, or retrieve artifacts for a Factor Mining plugin.
---

# Quandora Staging Factor Mining

Use this skill to run Factor Mining through the authenticated Quandora Staging connection exposed by the host as `quandora-staging`.

The agent drafts a valid Factor Mining `plugin.py`, submits the complete source inline, waits for the backtest result, saves one verified FM-owned Result Bundle ZIP when the host allows it, and summarizes the outcome.

OAuth and all credentials are handled by the host. Quandora access tokens expire after one hour, and the host MCP client should use its stored rotating refresh token automatically. Never inspect, print, copy, store, or ask the user to paste API keys, bearer tokens, authorization codes, access tokens, refresh tokens, PKCE verifiers, service tokens, or other credentials.

If the required Quandora Staging tools are visible, continue automatically. If they are not visible, tell the user to update or reinstall the current staging plugin, then use the host's normal Quandora Staging reconnect and browser re-authorization path before stopping:

- Codex CLI/TUI: run `codex mcp login quandora-staging`. Wait for the user to complete the browser authorization flow, then check again for `fm_status`.
- Codex Desktop: the plugin provides the Quandora Staging connector. If the first use opens the authorization flow, wait for the user to authorize Quandora Staging in the browser, then continue in a new chat. If the tools still are not visible, tell the user to fully quit and reopen Codex Desktop.
- Kimi Code: run `/mcp-config login plugin-quandora-staging:quandora-staging`, complete the browser authorization flow, then start a new chat and check `/mcp`.
- Claude Code: open `/mcp`, authenticate `quandora-staging`, then start a new chat.
- Claude Desktop: the plugin alone is not enough. Tell the user to open Settings -> Connectors, add a Connector named `quandora-staging` with URL `https://mcp-staging.varsity.lol/quant`, click Connect, authorize Quandora Staging in the browser, then start a new chat.
- CodeBuddy and the WorkBuddy China edition: update or reinstall the `quandora-staging` plugin, reconnect its plugin-managed Remote MCP server, complete the host-native browser authorization flow, then start a new chat.

Do not start a new authorization flow merely because an access token reached its one-hour lifetime or because of a single authorization response while the host is refreshing. Reauthorize only when the host reports a terminal authorization failure or still requires authorization after refresh handling.

Do not ask for Quandora API keys, `vt_` keys, bearer tokens, authorization codes, access tokens, refresh tokens, PKCE verifiers, service tokens, or pasted credentials. Do not use raw HTTP calls, local helper scripts, direct internal service calls, local execution keys, or credential paste flows. The only permitted direct HTTP download is consuming a short-lived Remote MCP artifact URL returned by a Factor Mining download-ticket action; never construct, modify, reuse, or persist that URL.

## Available Actions

After routing has confirmed Factor Mining scope, use only the Factor Mining actions exposed by `quandora-staging`. The artifact-ticket download exception above is only for consuming returned artifact bytes; it is not permission to call a service API directly.

- `fm_status`
- `fm_list_factors`
- `fm_get_history`
- `fm_list_tasks`
- `fm_get_contract`
- `fm_task_session`
- `fm_custom_sess`
- `fm_validate`
- `fm_dedup_context`
- `fm_run_backtest`
- `fm_resume_run`
- `fm_bundle_ticket`
- `fm_bundle_chunk`
- `qd_get_guidance`

Some hosts may prefix action names with the server name, such as `quandora_staging__fm_status`. Treat those as the same actions.

## Plugin Construction Contract

Before writing `plugin.py`, call `fm_get_contract` and use the returned `plugin_contract` as the source of truth for Python inputs, C# runtime expressions, runtime globals, and horizon defaults.

- Use `plugin_contract.allowed_data` to decide which input columns the factor may use.
- Use `plugin_contract.fwd_period` after the contract is returned. For custom ideas, pass `fwd_period: 7` to `fm_custom_sess` unless the user explicitly asks for another supported horizon.
- Use `plugin_contract.data_columns[].python_kwarg` for `build_signal` parameters.
- Whenever C# reads a market-data column from `bar`, including every extra-buffer enqueue, use the matching `plugin_contract.data_columns[].csharp_double_expression`. Do not use `bar` expressions inside `__FACTOR_COMPUTE_BODY__`; that section can use only the variables listed by its contract, normally `prices`, canonical extra-buffer arrays, `rawSignal`, and factor-owned fields.
- Follow `plugin_contract.runtime_rules` for required globals, `FACTOR_SECTIONS`, runtime variant, leak rules, extra-buffer rules, and reserved identifiers.
- When an additional runtime column is needed, use its matching `plugin_contract.runtime_rules.extra_buffer.column_patterns` entry. Copy that entry's field, enqueue, dequeue, and to-array snippets exactly into the corresponding `FACTOR_SECTIONS` values; do not reconstruct or normalize the snippets.

C# naming rules have this strict precedence:

1. Copy every contract-generated field, enqueue, dequeue, and to-array snippet byte-for-byte. A general naming rule never rewrites an identifier inside a returned canonical snippet.
2. Name factor-owned class fields with the contract's current `_factor...` prefix/style.
3. Name compute-body locals created by the factor with a descriptive `factor...` prefix. Avoid broad names such as `n` or `past`, and avoid every returned reserved local or extra-array reserved identifier.

When `plugin_contract.runtime_rules.factor_sections.all_values_must_be_string_literals` is true, every `FACTOR_SECTIONS` value must be a static string literal. In particular, write `"__FACTOR_TYPE__": "my_factor_type"`, not `"__FACTOR_TYPE__": FACTOR_TYPE`. Keep the top-level `FACTOR_TYPE` literal and the duplicated `__FACTOR_TYPE__` literal byte-for-byte identical. Name factor-owned C# identifiers with `plugin_contract.runtime_rules.csharp_runtime_rules.factor_owned_identifier_prefix` when that rule is returned.

Do not send multiple selectors in one plugin-contract call. Do not retry an identical non-retryable request. Do not silently change the user's research mechanism after a non-retryable validation error.

Never infer C# bar fields, field types, decimal/double casts, runtime buffer expressions, or supported data columns from memory. The returned plugin construction contract wins.

## Workflow

Before entering a Factor Mining workflow, route the request:

- Bare “列出可用因子”, “可用因子”, “available factors”, “eligible factors”, “selectable factors”, “可用于策略的因子”, and requests for the Strategy factor pool exit this skill and hand off to the Strategy Building skill. That skill calls only `sb_list_eligible` for the request. Do not first call `fm_status` or `fm_list_factors`, do not call both lists, and do not ask a clarification question for a bare request.
- Requests explicitly about “我的 Factor Mining 因子”, caller-owned or reusable Factor Mining factor families, factor history, branches, versions, or previous Factor Mining runs remain in this skill and route to `fm_list_factors`.

After routing has confirmed Factor Mining scope, call `fm_status` exactly once at the start of the normal Factor Mining workflow. If authorization is missing or the tools are not exposed, use the host's Quandora Staging connection path: desktop hosts use their Connector settings, while CLI/TUI hosts use their MCP login command. Do not ask the user for direct keys.

Before routing to factor creation, recognize intentional reuse and history intent. If the user asks
about existing factors, stable versions, prior successful factors, factor evolution, or past runs,
follow the reuse workflow below. Otherwise keep the existing creation workflow unchanged.

### Approved Guidance

Use `qd_get_guidance` only when approved product semantics are needed. It accepts only a
known `guide_id`. Supply `sections` only for `operation.factor.history.read` or
`operation.result.read`; omit `sections` for the capability-only `metric.backtest.grade` guide.
Pass `if_guide_revision` when revalidating a previous response, and honor a not-modified response
without fabricating content. The known ids for this release are:

- `operation.factor.history.read`
- `operation.result.read`
- `metric.backtest.grade`

Use each guide only for its named factor-history, result, or grade operation. Do not browse for
Guidance or invent a guide id. Treat each returned
`mcp_invocation.tools.<tool>.caller_supplied_fields` list as
the only invocation boundary. Upstream sections marked semantic background may explain identity,
verification, privacy, results, or grades, but they never create a mutation/retest tool or an input
field. Service-level `Actor.idempotency_key` / `Idempotency-Key` is transport-managed and is never
an MCP tool argument.

### Intentional Reuse and History

1. `fm_list_factors` lists caller-owned reusable Factor Mining factor families; it is
   not the Strategy eligible-factor pool. Call it first and show compact factor-family rows. Omit
   `page_size` unless pagination is needed; when present it must be an integer from 1 through 20.
   Do not hydrate or fetch history for every row. A failed list call is an error, not an empty
   result. Never claim zero factors unless a successful response contains an empty `items` array.
   After a list error, stop that read workflow. Do not call
   `fm_get_history` as a fallback.
2. Ask the user to select an exact `factor_id` returned by a successful
   `fm_list_factors` response for the current caller. Only after that explicit selection
   call `fm_get_history`. Never substitute a backtest `run_id`, `job_id`,
   `plugin_id`, `session_id`, PB `intake_result.factor.factor_id`, Strategy top-level compatibility
   selector, Strategy admission ID, or any locally cached ID.
3. Start with the default `summary` view. Request only the controlled `branches`, `versions`, or
   `runs` view needed for the user's next decision. Use only these safe selector combinations:
   - `summary`: do not send `branch_id`, `version_id`, `page_size`, or `page_token`.
   - `branches`: either list with optional `page_size` / `page_token`, or select one exact
     `branch_id` without pagination; do not send `version_id`.
   - `versions`: list all or one `branch_id` with optional pagination, or select one exact
     `version_id` without `branch_id`, `page_size`, or `page_token`.
   - `runs`: may use `version_id` plus `page_size` / `page_token`; do not send `branch_id`.
4. Use only returned metadata and run summaries. Historical source reading and editing are not
   exposed in this release. Do not read a local cache, call another service, or devise a workaround.

When controlled history semantics are needed, call `qd_get_guidance` with
`operation.factor.history.read`, only the relevant `sections`, and `if_guide_revision` when
revalidating a previous response. Honor a not-modified response without fetching unrelated
Guidance.

When the reuse request is complete, stop unless the user also asked to create or backtest a new
factor. Never treat browsing history as permission to edit or resubmit historical source.

Determine whether the user wants a public task or a custom idea:

- For a public task: call `fm_list_tasks`, show concise choices, and select one exact public `task_id`, asking the user to pick unless they explicitly ask the agent to choose. Treat the selected Task's returned category as authoritative and do not replace or reinterpret it. Either call `fm_get_contract` with only that exact `task_id` before creating the task session and then create the session for that same task, or create the session first with `fm_task_session` and call `fm_get_contract` with only the returned `session_id`.
- For a custom idea: before choosing `category` and before `fm_custom_sess`, obtain one complete current `fm_list_tasks` response. Reuse a complete response already obtained in the same conversation and workflow; otherwise call once in the normal flow. If that read fails with a retryable transport error, the single bounded identical retry below is allowed, but never call it again after a complete success. Require exactly eight open public task references. Every row must have a unique non-empty `task_id`, one of the eight non-`Other` canonical categories, and non-empty `core_question`, `primary_alpha_source`, `economic_principle`, `microstructure_logic`, `crypto_specific_mechanism`, `research_directions`, and `target_behavior` arrays. Their categories must be exactly `Microstructure`, `Volatility`, `Imbalance`, `Order Flow`, `Auction`, `Momentum`, `Volume`, and `Liquidity`, once each. Any malformed row or duplicate, missing, or inconsistent task/category is a backend/plugin contract mismatch: stop before `fm_custom_sess`, report the mismatch, and do not fall back to a static classification guess, stale model memory, or invented content.

  Compare the user's thesis semantically with those returned research fields; never classify from task ID or title alone. Choose exactly the category returned by the matching public task reference when the economic mechanism honestly fits. If none of the eight references fits, use the explicit product fallback `Other`; `Other` has no public reference task and must not be fabricated as a ninth public row. The public list is only the custom branch's semantic reference: never copy a public `task_id` into a custom task/session and never turn this branch into `fm_task_session`.

  Separately, before creating the session, call `fm_get_contract({})` exactly once to read the global construction and data-column contract; the runtime classification read and this construction-contract read are both required. Validate the selected label against exactly `Microstructure`, `Volatility`, `Imbalance`, `Order Flow`, `Auction`, `Momentum`, `Volume`, `Liquidity`, or `Other`; this vocabulary validates the runtime result and never replaces the runtime reference read. Prepare a clear title, category, description, non-empty `allowed_data`, and `fwd_period` for `fm_custom_sess`, using only exact column names returned by the global contract's `plugin_contract.allowed_data`, including `close`, `volume`, `funding_rate_close`, or `open_interest_close` only when returned. Use `fwd_period: 7` unless the user explicitly asks for another supported horizon. Create the custom session, then call `fm_get_contract` with only the returned `session_id`; treat that scoped contract as authoritative for writing and validating `plugin.py`. Never send a hand-built custom `task_payload` to `fm_get_contract`.

  `fm_custom_sess` has only the canonical flat shape below. This example is valid only when the immediately preceding global contract returned `close` exactly:

  ```json
  {
    "title": "Funding-adjusted trend persistence",
    "description": "Test whether recent close-price persistence survives funding pressure.",
    "category": "Momentum",
    "allowed_data": ["close"],
    "fwd_period": 7
  }
  ```

  Never send `name`, `idea`, `task_id`, or `task_payload` to `fm_custom_sess`.

After either branch returns its scoped contract, continue through the single shared plugin.py writing,
deduplication, validation, upload, resume/polling, and terminal Result Bundle workflow below.

Do not write `plugin.py` until the plugin construction contract has been returned. If the contract cannot be fetched, stop and report that plugin authoring is blocked by missing contract metadata.

After a session exists, do not create a result archive or `artifacts/` directory. The result
directory is reserved for the task-created `.partial` and the final FM-owned ZIP. Use a stable
factor slug for that destination. Prefer the generated top-level `FACTOR_TYPE`; if it is missing,
convert `FACTOR_NAME` to lowercase snake_case. For example, `FACTOR_TYPE = "aggressive_flow_exhaustion_reversal"` uses:

```text
Quandora staging result/factor-mining/aggressive_flow_exhaustion_reversal/
```

Use only the factor slug as the destination directory. The latest run for a factor updates that
factor's folder. A pre-terminal pending diagnostic may retain the existing redacted summary
behavior, but never put downstream IDs in the user-facing directory name or response and never
create a second completed-result summary beside the FM ZIP.

After session creation, call `fm_dedup_context` with only the `session_id`. Use `query_mode`, `scope`, `memory_stats`, `similar_factors`, and `task_memory_pressure` only to select a fresher research hypothesis. A high `task_memory_pressure` must never stop the workflow, reject a draft, or trigger repeated rewrites.

Before drafting, form a concise research thesis. For public tasks, stay inside the task's economic direction and allowed data. For custom ideas, stay inside the user's stated idea. Consider two or three plausible mechanisms, then choose the one with the clearest economic rationale, the best fit to the plugin contract, and the least overlap with the returned task memory. Prefer genuinely different mechanisms over parameter variants of the same formula.

Treat Task `category` and plugin `FACTOR_TYPE` as separate but strictly aligned fields. `category` is exactly the chosen product label retained by the custom Task/session lineage; `FACTOR_TYPE` is an agent-authored, mechanism-specific, unique snake_case identifier. For every custom factor, the thesis, formula, selected inputs, `FACTOR_NAME`, and `FACTOR_TYPE` must all semantically belong to the category supplied to `fm_custom_sess`. Use a mechanism-specific value such as `funding_adjusted_trend_persistence` inside `Momentum`; `FACTOR_TYPE` must never be a bare category label such as `momentum`, and never infer or rewrite the category from `FACTOR_TYPE`, names, tags, or backtest performance.

Immediately before validation and again after any source repair, verify this category-to-mechanism alignment. For a public task, revise an out-of-category draft to remain inside the selected Task or start the appropriate different task/session; never relabel the published Task. For a custom idea, if the mechanism has changed so that it no longer belongs to the category bound at session creation, do not validate or upload it through that session. Create a new custom session with the correct canonical category and a new invocation identity, then repeat the scoped contract, deduplication, validation, and ordinary upload flow. Do not silently keep a mismatched category or coerce an unrelated mechanism into one of the eight named categories.

For named indicators or established formulas, use the canonical inputs when the plugin contract allows them. For example, MFI should use high, low, close, and volume when those columns are available. If required inputs are unavailable, clearly treat the factor as a variant and reflect that in `FACTOR_NAME`, `FACTOR_TYPE`, description, and formula.

Create or locate one `plugin.py` source:

- In local coding hosts with a writable workspace, keep the submitted source as `plugin.py` in the
  normal authoring workspace, read it back, and submit the full contents as inline `plugin_source`.
  Do not copy it into the result directory; the accepted FM-owned `plugin.py` is delivered in the
  Result Bundle ZIP.
- In chat-only hosts without file writes, keep the generated source in the conversation/tool-call context and submit it directly as inline `plugin_source`.

When writing `plugin.py`, keep `build_signal` inputs aligned with `plugin_contract.data_columns[].python_kwarg`. Keep `FACTOR_SECTIONS` runtime code aligned with the same columns. Use each column's `csharp_double_expression` only at runtime sites where `bar` is visible, such as canonical extra-buffer enqueue snippets; inside `__FACTOR_COMPUTE_BODY__`, use `prices` and canonical extra-buffer arrays instead.

After a concrete `plugin.py` exists and before validation or upload, call `fm_dedup_context` again with the `session_id`, source, and concise factor metadata:

```json
{
  "session_id": "<session_id>",
  "source": "<full plugin.py source>",
  "description": "<short natural-language thesis>",
  "formula": "<short formula summary>",
  "limit": 5
}
```

Use `draft_duplicate_risk` as the only duplicate-risk verdict. When it identifies a concrete overlap with an existing factor's core mechanism, revise the candidate so its economic hypothesis, inputs, or formula family are materially different, then check the revised draft again. A medium or high score is not a hard gate only when the candidate is already economically meaningful and materially distinct, and the returned similar factors do not establish a concrete core-mechanism overlap. Otherwise resolve the overlap before validation and upload. Treat `similar_factors` as evidence for this comparison, not as a hard-failure gate.

Never submit a filesystem path or ask Quandora to read local files. Validate the complete, exact source with `fm_validate`, inline `plugin_source`, and the same context used for the plugin construction contract. Normal public and custom workflows validate with `session_id` only after the scoped contract has been returned; do not author or validate a custom plugin from a hand-built `task_payload`.

The agent must not import, execute, eval, or shell-run generated factor code locally. The remote validator performs AST/static checks and may also execute `build_signal` with synthetic inputs in an isolated preflight, while leaving module-level code unexecuted. Therefore `build_signal` must satisfy the contract for both float inputs and numeric values stored with object dtype, must return an aligned float `DataFrame`, and must replace positive or negative infinity with `np.nan` or a finite fallback.

After every source edit, including a deduplication or validation repair, validate the complete,
exact source again. A retryable read, deduplication check, or validation transport failure may
receive at most one identical bounded retry. Never retry an unchanged rejected source, and
`invalid_backend_response` is not retried identically.

Validation diagnostics are prioritized and may expose only the highest-priority failure. The absence of a diagnostic on one attempt does not prove that subsystem is valid; repair the reported issue and revalidate until `accepted` is true. A known compatibility case is `error_code=build_signal_preflight_unsafe`, `operation=build_signal.module`, and `actual=module-scope executable Assign`: before changing `build_signal`, audit top-level metadata and require every `FACTOR_SECTIONS` value to be a string literal, especially `__FACTOR_TYPE__`. This diagnostic can otherwise misattribute a non-literal `FACTOR_SECTIONS` assignment to `build_signal`.

When validation rejects the source, repair it only from the returned safe structured diagnostics:
`schema_version`, `error_code`, `operation`, `dtype`, `expected`, `actual`, `field`,
`contract_key_path`, and `repair_hint`. Ignore arbitrary messages or unrecognized diagnostic
values. For C# type or cast failures, re-read the same plugin construction contract and replace
runtime expressions with the corresponding
`plugin_contract.data_columns[].csharp_double_expression`. If upload or admission fails, use only
the closed `recovery_action` policy below; never infer a mutation retry from `retryable`.

When the source is valid and the user is ready to submit, call `fm_run_backtest` with only `session_id` and the exact inline `plugin_source` that passed validation. Do not send `fwd_period`: the session/scoped contract already binds the horizon. Do not edit, regenerate, reformat, or re-read a different copy between successful validation and submission.

### Mutation Recovery Policy

Read mutation-recovery fields only from the safe error `details`. `retryable` describes service
availability, but `recovery_action` controls mutation behavior. Never use a generic retry rule to
upload, Start, create a replacement session, or change bound input.

- `repair_and_revalidate`: repair only allowlisted safe diagnostics and revalidate the complete
  source in the same session. Do not upload until that repaired source passes validation.
- `create_same_kind_session_after_input_change`: do not reuse the bound pending handle. Create the
  same kind of session with a new invocation identity: public/task-backed stays public/task-backed
  for the exact task, and custom stays custom.
- `retry_same_pending_request`: make at most one bounded replay with the exact same pending handle,
  exact bound request, persisted idempotency identity, and unchanged validated source. Never create
  a session or alter the request.
- `resume_known_run`: resume the exact returned known `run_id`; never upload or Start again.
- `stop_and_report_trace`: stop and report the safe `trace_id`. Do not automatically retry, rewrite
  source, create a session, or re-upload.
- `repair_then_create_same_kind_session`: make one allowlisted diagnostics-led repair, revalidate
  the complete repaired source, then create the same kind of session with a new invocation identity
  before following the ordinary validated upload path once.

Normal `running` with `next_action=resume` resumes only through `fm_resume_run`; it never
uploads or Starts again. Use `fm_resume_run` when a prior known run was interrupted.
These recovery actions do not add an automatic retry loop.

### Waiting Policy

If `upload_backtest_wait` returns `running`, call `fm_resume_run` at most 4 times in the current request.

If the run is still `running` after the fourth resume, stop waiting and treat the archive as a pending run snapshot, not a completed result. Save only files that are already true at that point, such as `plugin.py` and a redacted pending run summary. Do not request Result Bundle metadata or attempt ZIP delivery until a later `fm_resume_run` returns a terminal status. In the final response, clearly say the backtest is still running, the Result Bundle was not requested, and the user can ask to resume later. Always print the result folder path.

### Result Bundle Handling

Run bundle handling only after `fm_run_backtest` or `fm_resume_run` returns a terminal status such as `succeeded`, `failed`, or `cancelled`. If the run is still `running`, skip this section. Use the redacted terminal response for status and interpretation. For completed runs, the FM-owned ZIP is the only canonical completed-result archive; never create a second completed-result `run_summary.json` beside it.

For a terminal Factor run: issue one initial `fm_bundle_ticket` with the exact canonical backtest `job_id` from the terminal response. The returned closed metadata is authoritative for the FM-owned ZIP: use its `safe_filename`, `content_type`, `size_bytes`, whole-ZIP `sha256`, `snapshot_revision`, and safe manifest. Do not reconstruct `run_summary.json`, `factor_card_is.json`, `artifact_manifest.json`, PNGs, or parquet outside the ZIP. Keep the legacy `fm_window_cards`, `fm_png_ticket`, `fm_png_chunk`, and `fm_raw_ticket` actions only for explicit single-artifact compatibility or rollback.

Use this URL-first delivery once per request:

1. Validate `safe_filename` as a basename, require the ZIP content type, non-negative size, lowercase SHA-256, and a safe destination beneath `Quandora staging result/factor-mining/<factor_slug>/`. Never overwrite an existing verified ZIP or unrelated user file.
2. Stream the opaque Auth `download_url` directly to `<safe_filename>.partial`, maintaining byte count and SHA-256. Do not print, log, save, edit, or reuse the URL. Retry rule: after one transient URL failure, at most one fresh ticket may be issued for one retry; after that failure, move to MCP fallback; never reuse a single-use URL/ticket.
3. Verify exact size and SHA-256, ZIP magic/openability, and that every ZIP entry is a safe relative path contained by the archive. Atomically rename the verified `.partial` file to `<safe_filename>`.

If the URL is unavailable, blocked by local host network policy, expired, or fails after that one retry, automatically use `fm_bundle_chunk` with the same canonical `job_id` and `snapshot_revision`. This fallback uses the already-working authenticated MCP connection and requires no new host-native file sink or shell network access:

1. Start at offset `0` and request at most `256 KiB` (`262144`) raw bytes per call. Decode `content_b64` without printing or logging it, append to the same task-created `.partial`, and follow only the validated `next_offset`.
2. Enforce the 10 MiB ZIP cap and at most 40 chunk calls. Keep every response bound to the same kind, job ID, snapshot revision, filename, content type, size, and whole-object SHA. Never mix revisions or append an old partial.
3. Require the final call to consume the empty terminal marker. PB's `terminal: true` means PB consumed and validated FM's empty upstream final marker; it is the terminal continuation response, so there is no second public empty chunk to request. Then verify the assembled byte count, whole-ZIP SHA-256, ZIP magic/openability, and safe entry paths before atomic rename. On interruption or any terminal fallback failure, discard only the task-created unverified `.partial` and report that no verified ZIP was saved.

Use this standard local layout:

```text
Quandora staging result/factor-mining/<factor_slug>/
  <safe_filename>
```

If bundle metadata is `pending`, `not_available`, or `integrity_failure`, stop before URL/chunk/file creation: no URL, no chunk, no fabricated file. Preserve its safe status/reason. Do not save bearer tokens, download URLs, raw service metadata, artifact IDs, admission IDs, credentials, or any other downstream IDs. The only exception is the current `session_id` / `run_id` local-traceability allowlist described above. If the host does not support file writes, report that no local verified ZIP was saved.

### Result Insight and Optimization

Run this section only when the user asks for insight, diagnosis, explanation, or optimization. Do not add long reflection to ordinary mining requests.

When result or grade semantics are needed for that request, follow the approved Guidance rules
above and call `qd_get_guidance` with `operation.result.read` or
`metric.backtest.grade` as appropriate.

When interpreting a result:

- Use in-sample IC / Rank IC sign to understand the factor's natural direction. Do not decide to invert a factor only because the realized backtest was poor.
- Diagnose the economic mechanism first, then the implementation. Consider IC level and stability, ICIR, autocorrelation, group monotonicity, long-short behavior, long-only and short-only legs, drawdown, turnover, and whether the signal decay matches the requested horizon.
- If optimizing, propose a new hypothesis within the same task or user idea. Avoid merely changing window lengths, renaming the factor, or making a post-hoc sign flip.
- Use task-memory context to choose a fresher research hypothesis. Before upload, use draft duplicate risk to resolve any concrete overlap with an existing factor; do not reject an economically meaningful, materially distinct candidate solely because its similarity score is high.
- If the host has general web or research tools and the user asks for broader insight, use them only for public background research. Do not send private factor source, run IDs, credentials, or artifact contents to external tools.

## Final Response

Summarize status, factor name, safe diagnostics if the run failed, bundle state, and the one verified ZIP path when saved. Inspect `ok`, `status`, `terminal_status`, `failures`, sanitized job statuses, and bundle metadata. Do not mention internal implementation details or treat an optional bundle item omission recorded by FM as a failed run.

Never show job IDs, snapshot revisions, download URLs, bearer tokens, raw credentials, or full `plugin.py` source in user-facing summaries. It is safe to show the local result folder and verified ZIP path created by the current host.

At the end of every completed, failed, or interrupted run, show the result folder and the verified Result Bundle ZIP when saved. For a pending run, show `run_summary.json` only when that pending summary was saved. For a completed run, the FM-owned ZIP is the only canonical completed-result archive. If the ZIP could not be saved, say so accurately. Never show job IDs, snapshot revisions, download URLs, tickets, credentials, or bundle base64.

For GUI/Desktop hosts, use Markdown links with absolute local paths and angle-bracket link targets so paths with spaces work:

Result folder: [Open result folder](</absolute/path/to/Quandora staging result/factor-mining/<factor_slug>/>)
Result Bundle ZIP: [verified ZIP](</absolute/path/to/Quandora staging result/factor-mining/<factor_slug>/<safe_filename>)
Pending run summary: [run_summary.json](</absolute/path/to/Quandora staging result/factor-mining/<factor_slug>/run_summary.json>) when saved

For CLI/TUI hosts, use plain absolute paths, not Markdown links:

Result folder: /absolute/path/to/Quandora staging result/factor-mining/<factor_slug>/
Result Bundle ZIP: /absolute/path/to/Quandora staging result/factor-mining/<factor_slug>/<safe_filename>
Pending run summary: /absolute/path/to/Quandora staging result/factor-mining/<factor_slug>/run_summary.json when saved

If the host could not write files, print:

Result folder: not available in this host
Result Bundle ZIP: not available in this host

## plugin.py Contract

Use this minimum shape when the user has not supplied an existing plugin. The metadata values must be static top-level literals so Quandora can parse them without executing module-level code. The current cross-sectional runtime requires `__FACTOR_LOG__` to exist but does not inject it; keep it only as compatible metadata and do not depend on it for runtime diagnostics.

```python
from typing import Any, Dict

import numpy as np
import pandas as pd

FACTOR_TYPE = "snake_case_unique_factor_type"
FACTOR_NAME = "human_readable_factor_name"
FACTOR_DEFAULT_PARAMS = {"window": 7}

FACTOR_SECTIONS = {
    "__FACTOR_DESCRIPTION__": "Trailing close-to-close momentum.",
    "__FACTOR_FORMULA__": "close / close[window bars ago] - 1",
    "__FACTOR_TYPE__": "snake_case_unique_factor_type",
    "__FACTOR_PARAM_FIELDS__": "        private int _factorWindow;\n",
    "__FACTOR_INIT__": '            _factorWindow = GetIntParameter("window", 7);\n',
    "__FACTOR_LOG__": '            Log($"[INIT] window={_factorWindow}");\n',
    "__PRICE_WINDOW_EXPR__": "_factorWindow + 1",
    "__EXTRA_BUF_FIELDS__": "",
    "__EXTRA_BUF_ENQUEUE__": "",
    "__EXTRA_BUF_DEQUEUE__": "",
    "__EXTRA_BUF_TOARRAY__": "",
    "__FACTOR_COMPUTE_BODY__": """
            var factorPriceCount = prices.Length;
            if (_factorWindow < 1 || factorPriceCount < _factorWindow + 1) return false;
            var factorPastPrice = prices[factorPriceCount - _factorWindow - 1];
            if (Math.Abs(factorPastPrice) < 1e-12) return false;
            rawSignal = prices[factorPriceCount - 1] / factorPastPrice - 1.0;
            if (double.IsNaN(rawSignal) || double.IsInfinity(rawSignal)) return false;
            return true;
""",
}


def build_signal(close: pd.DataFrame, params: Dict[str, Any], **data: Any) -> pd.DataFrame:
    window = int(params.get("window", FACTOR_DEFAULT_PARAMS["window"]))
    values = close.apply(pd.to_numeric, errors="coerce").astype(float)
    if window < 1:
        return (values * np.nan).reindex_like(close)
    signal = values.pct_change(window)
    signal = signal.replace([np.inf, -np.inf], np.nan).astype(float)
    return signal.reindex_like(close)
```

Keep `build_signal` and `FACTOR_SECTIONS` compute logic aligned:

1. Defaults: each `GetIntParameter("k", N)` literal in `__FACTOR_INIT__` must equal the matching `FACTOR_DEFAULT_PARAMS` value. The composer inlines those literals, so a mismatch silently produces two different factors.
2. Window: consume the same number of bars as the matching Python rolling window, slicing the required trailing bars from the end of the C# array. Never assume `prices.Length` equals the factor's own window.
3. Missing data: Python must produce `NaN` under the same conditions in which C# returns `false`.

Return a float `pd.DataFrame` aligned with `close`, use only current and historical data, and keep all data columns within `plugin_contract.allowed_data`. The duplicated `FACTOR_TYPE` and `__FACTOR_TYPE__` strings must match exactly; never replace the section value with a reference to the top-level variable.

## Security

- Use only Quandora actions for formal product workflows, except for consuming a short-lived opaque Result Bundle URL returned by `fm_bundle_ticket` exactly once.
- Never ask for API keys, auth files, user credentials, local execution keys, `vt_` keys, bearer tokens, or service tokens.
- Never print, persist in logs, or summarize full credential values.
- Do not call hosted generation endpoints; the active agent generates factor source in its current host session.
- Do not call internal service URLs or generic URL/API surfaces, and never construct a download URL. The returned Remote MCP Result Bundle URL is the sole direct-download exception.
- Do not import, exec, eval, or otherwise execute generated `plugin.py`.
- Do not submit filesystem paths instead of inline `plugin_source`.
- Do not print generated `plugin.py` source in summaries.
- Treat downstream IDs, download URLs, and service metadata as private.
- Bundle states and safe reason codes are authoritative. Authentication, authorization, network, malformed response, and server errors must fail clearly with redacted messages.
