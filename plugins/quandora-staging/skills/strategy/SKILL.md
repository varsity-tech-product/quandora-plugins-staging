---
name: strategy
description: Use when an agent should compose, submit, inspect, or archive a cross-sectional Quandora Staging strategy from eligible factors.
---

# Quandora Staging Strategy

Use this skill through the authenticated Quandora Staging connection exposed by the host as
`quandora-staging`. It composes cross-sectional strategies from eligible factor ids and includes
the complete Strategy archive workflow.

## Connection and Tools

Before starting, confirm that the Quandora Staging connection is authenticated and that these seven
Strategy actions are visible:

1. `strategy_get_contract`
2. `strategy_list_eligible_factors`
3. `strategy_submit_run`
4. `strategy_get_run`
5. `strategy_resume_run`
6. `strategy_get_artifact`
7. `strategy_create_artifact_download_ticket`

Some hosts prefix action names with the server name, such as
`quandora_staging__strategy_submit_run`; treat those as the same actions.

If the connection or actions are unavailable, use the host-specific OAuth flow, then start a new
chat before continuing:

- Codex CLI/TUI: run `codex mcp login quandora-staging`.
- Codex Desktop: authorize the plugin-provided connector, start a new chat, and fully quit and
  reopen Codex Desktop if the tools remain unavailable.
- Claude Code: open `/mcp`, authenticate `quandora-staging`, then start a new chat.
- Claude Desktop: add a connector named `quandora-staging` with URL
  `https://mcp-staging.varsity.lol/quant`, click Connect, complete browser authorization, then
  start a new chat.
- OpenClaw: run `openclaw mcp login quandora-staging`, complete authorization, then start a new
  chat.

The normal workflow uses only these seven exposed Strategy MCP actions. Never ask for or accept
credentials or use an alternative service path. Use host-native HTTP only for the one opaque
`download_url` returned by
`strategy_create_artifact_download_ticket`; never use it for internal-service calls, raw storage,
or credential-paste flows.

## Workflow

### 1. Prepare a Valid Submission

- Call `strategy_get_contract` exactly once at the start of each Strategy operation. Treat its
  `contract` as the current capability boundary and its separately labeled `product_defaults` as
  the effective defaults used when corresponding submit fields are omitted.
- Submit only a strategy kind whose contract entry has `submit_supported: true`. The current
  supported submission kind is cross-sectional Strategy; stop if the requested kind is unsupported.
- Call `strategy_list_eligible_factors` for eligible cross-sectional factors. The public action is
  already cross-sectional-scoped, so do not fabricate an unsupported kind field. Submit only
  factors verified through that tool, whether the agent selected them or the user supplied exact
  ids or weights.
- Use the returned exact `factorId` as selector identity. A display `name` is descriptive only and
  must never be substituted for an id.
- Treat factor ratings as informational and independent of eligibility:
  - `rated` has an observed grade and score; Grade F remains eligible when the factor is returned.
  - `unrated` means no rating is present; do not infer a grade.
  - `unavailable` means the rating cannot be supplied; do not infer a grade.
  - An exact `factor_backtest_run_id` is rating provenance only, never factor identity or a Strategy
    run id.
- Use exactly one selection form and obey the current contract's factor-count bounds (currently
  1–20):
  - `factor_ids`: unique factor ids.
  - `factor_weights`: unique `{ "factor_id": "...", "weight": <finite positive number> }` objects.
- If the user does not choose custom allocations, send `factor_ids` and omit `factor_weights`; equal
  weighting then comes from the advertised product behavior. If the user chooses custom weights,
  preserve them after validating that ids are unique, every weight is finite and positive, and the
  total is `1.0` within `1e-6`.
- If the user does not choose direction, ranking, or attribution, omit `strategy_type`, `ranking`,
  and `attribution` so the advertised product defaults apply. Do not copy those defaults into the
  request merely because they were advertised.
- Preserve every user-selected option exactly after validating it against the current contract.
  Do not invent a date range, cash value, fee rate, or rebalance interval.

Call `strategy_list_eligible_factors` to discover eligible cross-sectional factors and their
returned display names before finalizing the factor selection or a local result folder. If the user
explicitly asks the agent to choose factors, select eligible returned factors, retain the returned
`name` for each selected `factorId`, and continue. Ask the user to choose only when they
supplied neither factors nor weights and did not authorize the agent to choose.

When the user supplied `factor_ids` or `factor_weights`, extract the unique selected factor ids and
call `strategy_list_eligible_factors` with `include_factor_ids` containing exactly those ids before
submission or local-folder construction. Match the returned factors by exact `factorId`, not by name or
result order, and use only their returned `name` values. If any requested factor id is not
returned, do not invent a display name and do not submit the strategy. Report that the selected
factor could not be resolved as eligible for the current user.

Choose the submitted `name` before calling `strategy_submit_run`. Preserve a user-supplied name
after validating it against the submit tool schema: trim it, require a non-empty result, and keep it
within 255 characters. Otherwise derive a concise factor-aware name from the selected returned
display names plus the effective profile: use explicit user-selected options where present and the
advertised `product_defaults` only where omitted. Send it as `name`. Do not use a generic name that
omits factor context.

Call `strategy_submit_run` exactly once with the validated selection, generated or user-supplied
`name`, and only the options the user selected. Then observe and archive only the returned run.

After a valid submit response, store `result.run.id` as the sole Strategy `run_id`. Pass that exact
value to `strategy_get_run`, `strategy_resume_run`, and `strategy_get_artifact`. Treat
`result.run.strategyId` only as the saved Quandora Strategy identity visible in the web UI; it is
never a `run_id` and must never be used in a Strategy run action.

If a submit result contains a valid `run.id`, do not submit a modified fallback payload because the
run is `pending`, `running`, or `submit_unknown`; observe that existing run. A submit error without
`run.id` means that no trackable run identifier was returned; it does not prove that the server did
not record a Strategy or StrategyRun. Do not automatically resubmit or mutate the payload after an
ambiguous submit response, bridge error, or transport error. Correct and retry a weight-total error
only when the tool explicitly returns the preflight `invalid_payload` validation
error; otherwise report that submission confirmation failed to avoid duplicate strategy experiments.

### 2. Observe the Main Run

The successful `strategy_submit_run` response is the initial main-run snapshot; it is not a
follow-up poll. If that snapshot is terminal, immediately continue with the terminal result and
archive workflow below. Once the main run is terminal, do not resubmit it to retrieve results.

When the submitted run is non-terminal, make at most twelve main-run follow-up polls. Before each
follow-up, wait 30 seconds with a host-native wait or timer, then call `strategy_resume_run` once
with the stored `run_id`. Each resume response is the latest main-run snapshot. If any resume
response is terminal, immediately continue with the terminal result and archive workflow below.
Do not call `strategy_get_run` during these main-run follow-ups or between them.

If the twelfth `strategy_resume_run` response is still non-terminal, do not submit the strategy
again. Save that latest safe run snapshot as `run_summary.json`, do not begin terminal archive
observation or artifact retrieval, and clearly report that the server-side run remains in progress
and can be resumed later. Do not claim that results or artifacts are available.

The main-run status is separate from archive completion. After the main run becomes terminal, use
only the same stored `run_id` for archive observation. Before each of at most five
`strategy_get_run` archive-status follow-ups, wait 30 seconds with a host-native wait or timer. That
delay is observation only: do not use a local helper script, credentials, or an alternative service
path, and do not call `strategy_resume_run` or resubmit merely to wait for archiving.

If `archiveStatus` is `completed` or `partial` in the terminal snapshot or a follow-up, stop waiting
and follow the matching retrieval procedure below. If it remains `pending` or `running` after the
bounded wait, save the final observed run snapshot and an archive-level incomplete state only in
`artifact_manifest.json`; do not manufacture per-artifact availability or claim a complete archive.
For any other non-`completed` terminal archive status, likewise record only the archive-level state
and safe diagnostics. The final observed main-run snapshot remains the source for `run_summary.json`.

### Terminal Diagnostics and Saved Strategy

An accepted Agent Strategy submission is saved as a normal Quandora Strategy and appears in the
user's existing Strategy library. Do not expose internal identifiers in the user-facing summary.

For a terminal failure, use only the safe `failureDiagnostics` envelope when it is returned:

- When `failureDiagnostics.diagnosticStatus` is `ready`, summarize the available
  `errorCode`, `errorMessage`, `failureStage`, and `retryable` values. If its nested `failure`
  object is present, summarize only its provider, provider code, basename, line or column,
  captured time, and at most one affected factor.
- When it is `pending`, explain that safe diagnostic archival is incomplete. Do not fabricate a
  cause.
- When it is `unavailable`, or no `failureDiagnostics` envelope is returned, state that the
  server supplied no safe terminal diagnostic.

Do not infer a source-code repair from a diagnostic and do not automatically resubmit a failed run.

### 3. Read Requested Archive Artifacts

Each `strategy_get_artifact` call requires the stored `result.run.id` as `run_id` and exactly one
of these Factor Mining archive names:

```text
status
summary
equity_curve
drawdown_curve
turnover_curve
exposure_curve
orders
charts
trades
performance
attribution
signal_return_curves
result
logs
code
```

When `archiveStatus == completed`, perform one complete 15-artifact retrieval pass with the same
`run_id`; visit every name above exactly once for its artifact-state retrieval. When
`archiveStatus == partial`, perform one bounded artifact-state pass over those same fifteen names,
also exactly once each. In either case, do not resubmit the Strategy run to retrieve the archive.

1. Use `strategy_get_artifact` first for concise artifacts: `status`, `summary`, `performance`,
   `charts`, `equity_curve`, `drawdown_curve`, `turnover_curve`, `exposure_curve`, `attribution`,
   and `signal_return_curves`.
2. Use `strategy_create_artifact_download_ticket` first for `orders`, `trades`, `result`, `logs`,
   and `code`.
3. If a concise direct read returns `ready`, use it only as the state result: obtain one download
   ticket for that same artifact and use the ticketed bytes for the local archive rather than saving
   the unary body. If it returns `too_large`, request that one ticket as its download fallback. Do
   not make another unary read for it.

`attribution` describes predictive style exposure, not PnL contribution.

For every artifact, use its returned source state as authoritative. A complete ticket response with
`download_url`, `local_name`, `size_bytes`, and `sha256_hex` is the ready/downloadable state. For
`pending`, `not_available`, `sync_failed`, `integrity_failed`, or retryable backend errors, record
that exact source state or a bounded safe failure class and do not claim that an artifact was saved.
During a partial archive pass, download and save only ready/downloadable artifacts; do not blindly
retry any non-ready artifact or create a placeholder content file.

`logs` and `code` are text artifacts. All other names are JSON artifacts. Do not print large
artifact bodies into chat.

If `strategy_get_artifact` returns `RESOURCE_EXHAUSTED`, treat it as `too_large` and use the
single ticket fallback. Never invent a download URL.

### Ticket Download Procedure

For every initially ready artifact, use exactly one newly issued ticket: a ticket-first call is that
issuance; a direct-read `ready` or `too_large` needs one call to
`strategy_create_artifact_download_ticket` with the stored `run_id` and archive name. Then:

1. Only when that ticket response contains complete download metadata (including its opaque
   `download_url`), download it with host-native HTTP. Do not edit the URL, follow it to any other
   host, print it, or store it in a local file.
2. Write bytes to `artifacts/<local_name>.partial` beside the final file.
3. Verify the `.partial` file's byte count and SHA-256 against `size_bytes` and `sha256_hex` from
   the ticket response.
4. Atomically rename the verified `.partial` file to `artifacts/<local_name>`. On any download,
   size, or hash failure, delete the `.partial` file and record only a bounded safe failure class.
5. Never reuse a ticket after any attempt. For one transient failure before a verified rename,
   delete the `.partial` file, request one new ticket for that artifact, and make at most one bounded
   download retry. A second failure, an integrity mismatch, or any non-transient failure is final for
   this archive pass.

The ticket is short-lived and single-use. Never place its value, `download_url`, internal host,
storage details, or a credential in `artifact_manifest.json`, `run_summary.json`, chat output, or a
user-facing summary.

## Local Result Archive

When the host can write local files, create one deterministic local archive for the strategy.
Build its local-only `<strategy_slug>` only after the selected eligible factors and final
`strategy_submit_run` parameters are known. Use the actual display names returned for the selected
eligible factors; never invent factor labels.

Normalize each readable name to a lowercase ASCII filesystem slug by replacing each run of
non-`[a-z0-9]` characters with one underscore and trimming outer underscores. Truncate every
readable slug segment to at most 48 characters after normalization. Use one selected factor-name
slug when one factor is submitted, or the first two selected factor-name slugs in final submission
order when multiple factors are submitted. If a selected factor display name normalizes to an empty
slug, use `factor_1` or `factor_2` according to its displayed folder position. Never use a factor id
as a readable slug or place one anywhere in the visible directory name.

Create a local-only canonical fingerprint descriptor containing:

- an exact copy of the final `strategy_submit_run` payload as sent;
- the exact `contract.contract_revision` returned by this operation's single
  `strategy_get_contract` call; and
- the complete effective profile resolved locally for `weighting`, `ranking`, `strategy_type`,
  `start_date`, `end_date`, `initial_cash`, `taker_fee_rate`, `maker_fee_rate`, `rebalance_bars`, and
  `attribution`. For each field, use the validated explicit submit value when present and
  `product_defaults` when omitted. With `factor_ids`, use the advertised equal-weighting default;
  with `factor_weights`, use a custom-weighting value containing every exact factor id and weight.

For canonical encoding, recursively sort object keys, use one consistent JSON numeric
representation, and canonically sort each factor-selection copy by `factor_id`. Preserve every
factor id and custom weight in the hashed descriptor. Hash the canonical UTF-8 JSON with SHA-256 and
use the first 16 lowercase hexadecimal characters as `<fingerprint>`.

The descriptor, contract revision, resolved defaults, and assembled effective-profile object exist
only for local fingerprinting. Never send any of them to `strategy_submit_run`, and never pass
`contract_revision` as a tool argument. The submit payload continues to contain only supported
options the user explicitly selected, so never copy an omitted default into it. Never expose the
descriptor, contract revision, or factor ids in the directory name, a user-facing path, or a
user-facing summary.
Do not include credentials, OAuth material, URLs, raw source, server filesystem paths, or any other
internal id in the directory name or local fingerprint input.

Use this folder-name format:

```text
<strategy_name_slug>__<factor_slug_1>__<factor_slug_2>__<fingerprint>
```

Build `<strategy_name_slug>` from the final submitted `name`, whether user-supplied or generated,
and truncate it to at most 48 characters. For a one-factor strategy, omit the `<factor_slug_2>`
segment.

Bound the complete `<strategy_slug>` directory component to at most 180 ASCII characters. If
additional truncation is necessary after composing it, remove trailing characters from the leading
strategy segment first, then `<factor_slug_2>`, then `<factor_slug_1>`, trimming any newly exposed
outer underscores and preserving at least one character in each displayed segment. Preserve the
complete final `__<fingerprint>` suffix unchanged. The canonical fingerprint includes the final
payload and its effective contract context, so different selections, submitted values, contract
revisions, or resolved Product defaults produce different fingerprints. Reuse an existing
deterministic directory only when both the final payload and effective contract context are
unchanged.

The slug is a local archive label only. Do not send the slug in an action request. Use it only in
the local archive folder and the user-facing local paths.

```text
Quandora staging result/
  strategy/
    <strategy_slug>/
      run_summary.json
      artifacts/
        status.json
        summary.json
        equity_curve.json
        drawdown_curve.json
        turnover_curve.json
        exposure_curve.json
        orders.json
        charts.json
        trades.json
        performance.json
        attribution.json
        signal_return_curves.json
        result.json
        logs.txt
        code.txt
      artifact_manifest.json
```

Save `run_summary.json` from the final main-run snapshot. Verified ticket downloads use the closed
`local_name` returned by the ticket response.

After a completed archive retrieval pass, create `artifact_manifest.json` with the run id, main-run
status, `archiveStatus: completed`, and exactly one entry for every archive name. Each entry contains
only the artifact name, terminal/source state, relative local path when saved, content type, size,
SHA-256, and a bounded safe failure class when needed. State that this archive pass completed; do not
claim that every artifact contained data.

After a partial archive pass, create the same fifteen per-artifact entries with
`archiveStatus: partial`, preserving every returned state and the local path only for verified ready
downloads. Clearly mark the archive as partial and never claim that the full archive was fetched.
For a pending/running bounded-wait exhaustion or any other non-`completed` terminal archive state,
record only the archive-level state and observed `archiveStatus` without manufacturing per-artifact
`not_available` entries. Never include a ticket, download URL, internal URL, storage reference, or
credential.
Keep run ids only in `run_summary.json` and `artifact_manifest.json` when traceability requires
them; never use a run id in a directory name or user-facing summary.

For each artifact attempted during a completed or partial archive pass, update its local file only
after a verified ticket download. For every non-ready state, record that state exactly as returned.
Do not create a placeholder body file, or delete or overwrite an existing final body file.

## Final Response

State the submitted strategy name and whether it was user-supplied or factor-aware generated. State
the main-run status, archive status, and safe diagnostics. State all fifteen archive
artifact states after a completed or partial archive pass; for a partial pass, clearly state that the
archive is partial and that the full archive was not fetched. Otherwise clearly state that the archive
is incomplete and that no full artifact retrieval was claimed. For artifacts without a local body
file, state `not created` and its returned state. Do not print large artifact bodies.

Never show run ids, download URLs, credentials, secret material, or internal service metadata in a
user-facing summary.

For a main run that remains non-terminal after the twelfth follow-up, clearly state that the
server-side run remains in progress and can be resumed later. State that terminal archive
observation and artifact retrieval were not started, and do not state that results or artifacts are
available.

At the end of every completed, failed, or interrupted run, show the result folder, artifact folder,
`run_summary.json`, and `artifact_manifest.json`. If a specific file was not created, say
`not created` for that line.

For Desktop or GUI hosts, use Markdown links with absolute local paths and angle-bracket link
targets so paths with spaces work:

```text
Result folder: [Open result folder](</absolute/path/to/Quandora staging result/strategy/<strategy_slug>/>)
Artifact folder: [Open artifact folder](</absolute/path/to/Quandora staging result/strategy/<strategy_slug>/artifacts/>)
Run summary: [run_summary.json](</absolute/path/to/Quandora staging result/strategy/<strategy_slug>/run_summary.json>)
Artifact manifest: [artifact_manifest.json](</absolute/path/to/Quandora staging result/strategy/<strategy_slug>/artifact_manifest.json>)
```

For CLI or TUI hosts, use the same absolute paths as plain text, not Markdown links:

```text
Result folder: /absolute/path/to/Quandora staging result/strategy/<strategy_slug>/
Artifact folder: /absolute/path/to/Quandora staging result/strategy/<strategy_slug>/artifacts/
Run summary: /absolute/path/to/Quandora staging result/strategy/<strategy_slug>/run_summary.json
Artifact manifest: /absolute/path/to/Quandora staging result/strategy/<strategy_slug>/artifact_manifest.json
```

If the host cannot write files, state:

```text
Result folder: unavailable in this host
Artifact folder: unavailable in this host
```
