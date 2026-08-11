---
name: strategy-building
description: Use when the user asks to list available, eligible, or selectable Strategy factors, including the bare Chinese request “列出可用因子”, or asks to compose, submit, inspect, or archive a cross-sectional Quandora Staging strategy.
---

# Quandora Staging Strategy Building

Use this skill through the authenticated Quandora Staging connection exposed by the host as
`quandora-staging`. It composes cross-sectional strategies from eligible factor ids and includes
the complete Strategy Result Bundle workflow.

OAuth and all credentials are handled by the host. Quandora access tokens expire after one hour, and the host MCP client should use its stored rotating refresh token automatically. Never inspect, print, copy, store, or ask the user to paste API keys, bearer tokens, authorization codes, access tokens, refresh tokens, PKCE verifiers, service tokens, or other credentials.

## Connection and Tools

Before starting, confirm that the Quandora Staging connection is authenticated and that the actions
needed for the requested path are visible:

1. `sb_get_contract`
2. `sb_list_eligible`
3. `sb_factor_detail`
4. `sb_shared_list`
5. `sb_shared_add`
6. `sb_import_factor`
7. `sb_submit_run`
8. `sb_get_run`
9. `sb_resume_run`
10. `sb_bundle_ticket`
11. `sb_bundle_chunk`
12. `sb_get_artifact` (legacy single-artifact compatibility)
13. `sb_file_ticket` (legacy single-artifact compatibility)
14. `fm_custom_sess`
15. `fm_resume_run`
16. `qd_get_guidance`

Some hosts prefix action names with the server name, such as
`quandora_staging__sb_submit_run`; treat those as the same actions.

If the connection or actions are unavailable, tell the user to update or reinstall the current
staging plugin, use the host-specific reconnect and browser OAuth flow, then start a new chat
before continuing:

- Codex CLI/TUI: run `codex mcp login quandora-staging`.
- Codex Desktop: authorize the plugin-provided connector, start a new chat, and fully quit and
  reopen Codex Desktop if the tools remain unavailable.
- Kimi Code: run `/mcp-config login plugin-quandora-staging:quandora-staging`, complete browser authorization, then start
  a new chat and check `/mcp`.
- Claude Code: open `/mcp`, authenticate `quandora-staging`, then start a new chat.
- Claude Desktop: add a connector named `quandora-staging` with URL
  `https://mcp-staging.varsity.lol/quant`, click Connect, complete browser authorization, then
  start a new chat.
- CodeBuddy and the WorkBuddy China edition: update or reinstall the `quandora-staging` plugin, reconnect its plugin-managed
  Remote MCP server, complete the host-native browser authorization flow, then start a new chat.

Do not start a new authorization flow merely because an access token reached its one-hour lifetime
or because of a single authorization response while the host is refreshing. Reauthorize only when
the host reports a terminal authorization failure or still requires authorization after refresh
handling.

The normal workflow uses only the exposed MCP actions above. Never ask for or accept API keys,
bearer tokens, authorization codes, access tokens, refresh tokens, PKCE verifiers, service tokens,
or pasted credentials, and never
use an alternative service path. Use host-native HTTP only for the one opaque
`download_url` returned by
`sb_bundle_ticket`; never use it for internal-service calls, raw storage,
or credential-paste flows.

## Workflow

Bare “列出可用因子”, “可用因子”, “available factors”, “eligible factors”, “selectable
factors”, “可用于策略的因子”, and equivalent Strategy factor-pool intent calls only
`sb_list_eligible`. This action lists currently eligible/selectable cross-sectional
Strategy factors.

For that bare available/eligible/selectable intent:

- When the user does not specify a count, make exactly one call with `page_size: 10` and display
  only that returned page.
- Honor an explicit valid `page_size` from 1 through 100 by making exactly one call with that value
  and displaying only the returned page.
- Only when `next_page_token` is non-empty, retain that opaque value byte-for-byte and tell the user
  that more results can be requested. Do not use it unless the user later asks for another page.

Do not auto-page. Do not call `sb_get_contract`, do not call `fm_status`, and do
not call `fm_list_factors`; do not make a second list call, and do not ask a
clarification question for a bare request. Requests explicitly about “我的 Factor Mining 因子”,
caller-owned or reusable Factor Mining factor families, stable factor history, branches, versions,
or previous factor runs route to `fm_list_factors` through the Factor Mining skill; that
list is not a substitute for Strategy eligibility.

### 1. Prepare a Valid Submission

- For composition and submission operations, call `sb_get_contract` exactly once. Treat its
  `contract` as the current capability boundary and its separately labeled `product_defaults` as
  the effective defaults used when corresponding submit fields are omitted. A bare factor-list
  request does not call this action.
- Immediately after that contract response and before constructing any payload, use this exact
  `sb_submit_run` upload whitelist:
  `name`, `factor_ids`, `factor_weights`, `ranking`, `strategy_type`, `start_date`, `end_date`,
  `initial_cash`, `taker_fee_rate`, `maker_fee_rate`, `rebalance_bars`, `attribution`.
  Send exactly one of `factor_ids` or `factor_weights`. Never send `idempotency_key`, `kind`,
  `strategy_kind`, `weighting`, `contract_revision`, `product_defaults`, `effective_profile`,
  `composition`, or `parameters`. Idempotency is generated from trusted Auth/gateway context;
  `kind` / `strategy_kind` are fixed to `cs`; the remaining names are semantic, response-only, or
  local-only. If `contract.submission.caller_supplied_fields` differs from this whitelist or from
  the tool schema, stop with a contract mismatch before constructing a payload.
- Submit only a strategy kind whose contract entry has `submit_supported: true`. The current
  supported submission kind is cross-sectional Strategy; stop if the requested kind is unsupported.
- Call `sb_list_eligible` for eligible cross-sectional factors. The public action is
  already cross-sectional-scoped, so do not fabricate an unsupported kind field. Submit only
  factors verified through that tool, whether the agent selected them or the user supplied exact
  ids or weights.
- Use the returned exact `factor_id` as selector identity. A display `name` is descriptive only and
  must never be substituted for an id.
- Treat factor ratings as informational and independent of eligibility:
  - `rated` has an observed grade and score; Grade F remains eligible when the factor is returned.
  - `unrated` means no rating is present; do not infer a grade.
  - `unavailable` means the rating cannot be supplied; do not infer a grade.
  - `rating.factor_backtest_run_id` is rating provenance only. It is never factor identity and
    never a Strategy run id.
- Use exactly one selection form and obey the current contract's factor-count bounds (currently
  1–20):
  - `factor_ids`: unique factor ids.
  - `factor_weights`: unique `{ "factor_id": "...", "weight": <finite positive number> }` objects.
- When configuration is omitted, leave optional caller fields omitted. Interpret the current
  Product defaults only for effective behavior and local description: equal weights use the
  `factor_ids` selection form, the default direction is neutral, and omitted ranking uses N=5. Read
  exact field names, value shapes, and omission semantics from the single returned contract, its
  `product_defaults`, and the exposed submit schema; never invent a request field or enum value.
- A user-supplied weight, direction, top/bottom count, or top/bottom percentage overrides the
  corresponding default. For custom weights, validate that ids are unique, every weight is finite
  and positive, and the total is `1.0` within `1e-6`. Preserve every other explicit supported
  option.
- Validate every numeric value as finite and every integer as binary64-safe. Each fee rate is in
  `[0, 0.01]`; `rebalance_bars` is an integer in `1..10000`; ranking is exactly mode `N` with a
  positive integer value or mode `percent` with a value in `(0, 50]`. Dates are exact ISO
  `YYYY-MM-DD` strings and explicit `end_date` must be later than the effective `start_date`.
  Omitted `end_date` means Factor Mining's latest-data default, not a fixed or locally invented
  date.
- Preserve every user-selected option exactly after validating it against the current contract.
  Do not invent a date range, cash value, fee rate, or rebalance interval.

#### Manual Selection

Call `sb_list_eligible` with the requested filters and bounded pagination. Display a
compact comparison table with only factor id, name, authoritative FM Task category, rating/grade
status, and exact `cs_sharpe` labeled CS Sharpe when available. Do not include Median Sharpe,
cross-sectional/time-series capability flags, or eligibility status in the default table, and never
substitute `median_sharpe` for `cs_sharpe`. Treat the returned category as authoritative and an
unavailable category as unavailable; never infer it from name, type, or tags. Grade F remains
selectable when the returned eligibility status says the factor is eligible.

Call `sb_factor_detail` only for an exact factor id the user requests or for a
small, stated shortlist. Do not fetch detail for every list row. If the user supplied neither
factors nor weights and did not explicitly ask the agent to choose, show the compact choices and ask
the user to select.

#### Shared Selection

Call `sb_shared_list` and show the same compact comparison columns used for
manual selection wherever fields are available. If admission semantics are needed, call
`qd_get_guidance` with the known guide id
`operation.strategy.factor.shared_admission` without `sections`, and safely use
`if_guide_revision` when revalidating a previous response. This is a capability-only guide.

The root-level `factor_backtest_run_id` returned by
`sb_shared_list`, together with the exact `factor_version_id`, is the
evidence required for shared-factor admission. Do not substitute
`rating.factor_backtest_run_id`. Before calling `sb_shared_add`, show the user
the exact candidate name, `factor_version_id`, and root-level `factor_backtest_run_id`, then obtain
explicit confirmation for that exact candidate and pair. Verify the returned admission evidence,
then call `sb_list_eligible` with `include_factor_ids` containing exactly the newly
admitted `factor_id`. Do not submit a Strategy unless that exact id is returned as currently
eligible.

#### Import

Import only complete inline `plugin.py` source. Reuse a real existing Factor Mining `session_id`, or
create the appropriate custom session with `fm_custom_sess` using its exposed
schema. Call `sb_import_factor` with only schema-declared arguments. If import semantics are
needed, call `qd_get_guidance` with the known guide id
`operation.strategy.factor.import` without `sections`, and include `if_guide_revision` only when
revalidating an available prior revision. This is a capability-only guide.

The minimum legal import request uses the Auth/PB defaults `filename="plugin.py"` and
`params_json="{}"` by omitting those two optional fields:

```json
{
  "session_id": "<session_id>",
  "plugin_source": "<complete inline plugin.py source>",
  "factor_type": "<factor_type>",
  "factor_name": "<factor_name>",
  "fwd_period": 7
}
```

If `params_json` is explicit, it is a string that parses as a finite JSON object, for example
`"{}"`; never send a `params` object or mix `params` with `params_json`. If `filename` is explicit,
send the non-empty source filename. Never send `Idempotency-Key`, `Actor.idempotency_key`, or
`idempotency_key`; Auth supplies the transport identity. For Guidance, the PB-owned
`mcp_invocation` metadata is the request-shape authority and upstream service-level sections are
semantic background only.

Use only real lifecycle identifiers returned by `sb_import_factor`. If `next_action` requires
resume, require the canonical returned `run_id` for `fm_resume_run` and follow the Factor
Mining bounded policy of at most four resumes in the current request. Treat a returned
`backtest_job_id` as lifecycle evidence only; if `run_id` is absent, stop rather than substitute or
map that value. Do not invent an id mapping or add an import-status poller. Whether the factor was
newly verified or reused, call `sb_list_eligible` with
`include_factor_ids` containing exactly its returned factor id. Never submit a Strategy until that
exact id appears in the current eligible list.

#### Agent Selection

Automatically choose factors only when the user explicitly asks the agent to choose. Retain each
selected row's returned `name`; before submission, state the rationale and the exact factor ids.
Otherwise ask the user to select from the manual, shared, or import path.

When the user supplied `factor_ids` or `factor_weights`, extract the unique selected factor ids and
call `sb_list_eligible` with `include_factor_ids` containing exactly those ids before
submission or local-folder construction. Match the returned factors by exact `factor_id`, not by name or
result order, and use only their returned `name` values. If any requested factor id is not
returned, do not invent a display name and do not submit the strategy. Report that the selected
factor could not be resolved as eligible for the current user.

Choose the submitted `name` before calling `sb_submit_run`. Preserve a user-supplied name
after validating it against the submit tool schema: trim it, require a non-empty result, and keep it
within 255 characters. Otherwise derive a concise, distinguishable name from themes present in the
selected returned display names plus the actual effective configuration: use explicit user-selected
options where present and the advertised `product_defaults` only where omitted. For example,
`liquidation_continuation_ls_neutral_tb5` represents returned liquidation/continuation themes,
long-short neutral direction, and top/bottom count 5. Never invent a factor label or use a generic
name such as `agent_neutral_percent_N_strategy`. Send the generated name as `name` and use the same
name in the existing deterministic destination-slug logic.

Call `sb_submit_run` exactly once with the validated selection, generated or user-supplied
`name`, every explicit user option, and only the omitted-field default representation required by
the returned contract and submit schema. Then observe and archive only the returned run.

A minimum equal-weight submission is:

```json
{
  "name": "Momentum neutral strategy",
  "factor_ids": ["<exact eligible factor_id>"]
}
```

After a valid submit response, store `result.run.id` as the sole Strategy `run_id`. Pass that exact
value to `sb_get_run`, `sb_resume_run`, and `sb_get_artifact`. Treat
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

The successful `sb_submit_run` response is the initial main-run snapshot; it is not a
follow-up poll. If that snapshot is terminal, immediately continue with the terminal result and
archive workflow below. Once the main run is terminal, do not resubmit it to retrieve results.

When the submitted run is non-terminal, make at most twelve main-run follow-up polls. Before each
follow-up, wait 30 seconds with a host-native wait or timer, then call `sb_resume_run` once
with the stored `run_id`. Each resume response is the latest main-run snapshot. If any resume
response is terminal, immediately continue with the terminal result and archive workflow below.
Do not call `sb_get_run` during these main-run follow-ups or between them.

If the twelfth `sb_resume_run` response is still non-terminal, do not submit the strategy
again. Save that latest safe run snapshot as `run_summary.json`, do not begin terminal archive
observation or artifact retrieval, and clearly report that the server-side run remains in progress
and can be resumed later. Do not claim that results or artifacts are available.

The main-run status is separate from archive completion. After the main run becomes terminal, use
only the same stored `run_id` for archive observation. Before each of at most five
`sb_get_run` archive-status follow-ups, wait 30 seconds with a host-native wait or timer. That
delay is observation only: do not use a local helper script, credentials, or an alternative service
path, and do not call `sb_resume_run` or resubmit merely to wait for archiving.

If `archiveStatus` is `completed` or `partial` in the terminal snapshot or a follow-up, stop waiting
and request bundle metadata. If it remains `pending` or `running` after the bounded wait, save the
final observed run snapshot and an archive-level incomplete state only; do not request a bundle or
manufacture item availability.
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

### 3. Save the Strategy Result Bundle

After the Strategy main run is terminal and archive state permits bundle metadata, call `sb_bundle_ticket` exactly once with the exact canonical `run_id` from `result.run.id`. The returned closed metadata and safe manifest are authoritative for the FM-owned Strategy ZIP, including the current 22-name registry, partial/unavailable items, and unsafe text omissions. Do not loop over artifact names, issue one ticket per file, or recreate canonical files outside the ZIP. Keep `sb_get_artifact` and `sb_file_ticket` only for explicit single-artifact compatibility or rollback.

Use this URL-first delivery once per request:

1. Validate `safe_filename` as a basename, require ZIP content type, non-negative size, lowercase SHA-256, and a safe destination beneath `Quandora staging result/strategy/<strategy_slug>/`. Never overwrite an existing verified ZIP or unrelated user file.
2. Stream the opaque Auth `download_url` directly to `<safe_filename>.partial`, maintaining byte count and SHA-256. Do not print, log, save, edit, or reuse the URL. A transient URL failure may request one fresh `sb_bundle_ticket` and retry once; a ticket is single-use.
3. Verify exact size and SHA-256, ZIP magic/openability, and safe relative ZIP entry paths, then atomically rename the verified `.partial` to `<safe_filename>`.

If the URL is unavailable, blocked by local host network policy, expired, or fails after that one retry, automatically use `sb_bundle_chunk` with the same exact `run_id` and `snapshot_revision`. The fallback uses the already-working authenticated MCP connection and requires no new host-native file sink or shell network access. Start at offset `0`, request at most `256 KiB` (`262144`) raw bytes per call, decode `content_b64` without printing or logging it, append to the same task-created `.partial`, and follow only validated `next_offset`. Enforce the 10 MiB ZIP cap and at most 40 calls. Require the final empty terminal marker and exact size/whole-ZIP SHA-256 before ZIP/path verification and atomic rename. Never mix revisions or append an old partial; on interruption or terminal fallback failure discard only the unverified task-created `.partial` and report that no verified ZIP was saved.

## Local Result Destination

Do not assemble a separate local archive of individual files for the strategy. When the host can write local files,
create only the deterministic destination slug for the FM-owned Result Bundle ZIP.
Build its local-only `<strategy_slug>` only after the selected eligible factors and final
`sb_submit_run` parameters are known. Use the actual display names returned for the selected
eligible factors; never invent factor labels.

Normalize each readable name to a lowercase ASCII filesystem slug by replacing each run of
non-`[a-z0-9]` characters with one underscore and trimming outer underscores. Truncate every
readable slug segment to at most 48 characters after normalization. Use one selected factor-name
slug when one factor is submitted, or the first two selected factor-name slugs in final submission
order when multiple factors are submitted. If a selected factor display name normalizes to an empty
slug, use `factor_1` or `factor_2` according to its displayed folder position. Never use a factor id
as a readable slug or place one anywhere in the visible directory name.

Create exactly this local-only fingerprint descriptor:

```json
{
  "submit_payload": <canonical semantic copy of the exact final sb_submit_run payload>,
  "contract_revision": "<exact contract.contract_revision>",
  "effective_profile": {
    "weighting": <canonical weighting object>,
    "ranking": <resolved ranking object>,
    "strategy_type": "<resolved value>",
    "start_date": "<resolved value>",
    "end_date": {"value": "<exact explicit end_date>", "source": "caller"},
    "initial_cash": <resolved value>,
    "taker_fee_rate": <resolved value>,
    "maker_fee_rate": <resolved value>,
    "rebalance_bars": <resolved value>,
    "attribution": <resolved value>
  }
}
```

`submit_payload` contains exactly the fields and semantic values sent to `sb_submit_run`; it
must not gain omitted Product defaults. Copy `contract_revision` exactly from the single
`sb_get_contract` response used for this operation. For every effective-profile field except
`end_date`, use the validated explicit submit value when present and the corresponding
`product_defaults` value when omitted. For an explicit `end_date`, preserve the exact submitted
string as the `value` with `source: "caller"`. When `end_date` is omitted, use exactly
`{"value": null, "source": "factor_mining_latest_data_default"}`. Never invent or resolve a
calendar date locally. This marker is local-only: never send it to `sb_submit_run`, and it must not
alter the PB request hash, FM request, run window, or result.

When `factor_ids` is submitted, use exactly this effective weighting:

```json
{
  "mode": "equal"
}
```

When `factor_weights` is submitted, preserve every validated factor id and weight in exactly this
effective weighting shape:

```json
{
  "mode": "custom",
  "factor_weights": [
    {
      "factor_id": "<exact factor id>",
      "weight": <exact validated weight>
    }
  ]
}
```

Canonicalize only a local hashing copy as follows; none of these operations may alter the payload
sent to the MCP tool:

- Recursively sort all JSON object keys lexicographically.
- Sort `submit_payload.factor_ids` by the factor-id string in ascending lexical order.
- Sort `submit_payload.factor_weights` by `item.factor_id` in ascending lexical order.
- Sort `effective_profile.weighting.factor_weights` by `item.factor_id` in ascending lexical order.
- Do not reorder unrelated arrays. Preserve strings and booleans exactly.
- Reject non-finite numeric values before fingerprinting. Treat each finite numeric leaf as an exact
  decimal value and encode it as a canonical plain-decimal JSON number: no leading plus sign; no
  exponent notation; no redundant leading zeros; no redundant trailing fractional zeros. Normalize
  an integral value such as `5.0` to `5`, and normalize negative zero to `0`.
- Encode the canonical descriptor as compact UTF-8 JSON with no insignificant whitespace. Hash
  those exact bytes with SHA-256 and use the first 16 lowercase hexadecimal characters as
  `<fingerprint>`.

The descriptor, effective profile, resolved Product defaults, and contract revision exist only for
local fingerprinting. Never send them to `sb_submit_run`, never pass `contract_revision` as a
tool argument, and never add `weighting`, a resolved default, or `contract_revision` to the actual
request. Factor ids remain in the hashed descriptor but never appear in the visible directory name,
a user-facing path, or a user-facing summary. Beyond the required contract revision and selector
factor ids, never include credentials, OAuth material, URLs, source code, internal filesystem paths,
run ids, or other internal identifiers in the fingerprint descriptor.

The same final payload, contract revision, and effective profile must produce the same fingerprint
across agents and hosts. A changed factor selection, custom weight, explicit option, resolved
Product default, or contract revision must change it. Reordering `factor_ids`, reordering either
factor-weights array, changing JSON object-key order, or representing an integral number as `5`
instead of `5.0` must not change it. Explicitly supplying a value and omitting it may produce
different fingerprints even when both resolve to the same effective behavior because the exact
final submit payload is part of the descriptor. These local rules do not change any server request
or remote behavior.

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
complete final `__<fingerprint>` suffix unchanged. Reuse an existing deterministic directory only
when both the final payload and effective contract context are unchanged.

The slug is a local destination label only. Do not send it in an action request. Use it only in the
Result Bundle folder and the user-facing local path.

```text
Quandora staging result/
  strategy/
    <strategy_slug>/
      <safe_filename>
```

For a non-terminal or archive-pending run, preserve the existing redacted run-summary behavior
when local writes are available. For a completed run, the FM-owned ZIP is authoritative and no
second canonical `run_summary.json` is written beside it. Never place a ticket, URL, internal host,
storage reference, credential, or bundle bytes in local metadata or user-facing output.

## Final Response

State the submitted strategy name and whether it was user-supplied or factor-aware generated. State
the main-run status, archive status, safe diagnostics, and the one verified Result Bundle ZIP path
when saved. If it was not saved, say so accurately; do not print large artifact bodies or describe a
manually assembled archive.

Never show run ids, download URLs, credentials, secret material, or internal service metadata in a
user-facing summary.

For a main run that remains non-terminal after the twelfth follow-up, clearly state that the
server-side run remains in progress and can be resumed later. State that terminal archive
observation and bundle retrieval were not started, and do not state that results or bundles are
available.

At the end of every completed, failed, or interrupted run, show the result folder, verified Result
Bundle ZIP when saved, and `run_summary.json` when saved. If a specific file was not created, say
`not created`. Never show run IDs, snapshot revisions, tickets, download URLs, credentials, or
bundle base64.

For Desktop or GUI hosts, use Markdown links with absolute local paths and angle-bracket link
targets so paths with spaces work:

```text
Result folder: [Open result folder](</absolute/path/to/Quandora staging result/strategy/<strategy_slug>/>)
Result Bundle ZIP: [verified ZIP](</absolute/path/to/Quandora staging result/strategy/<strategy_slug>/<safe_filename>)
Run summary: [run_summary.json](</absolute/path/to/Quandora staging result/strategy/<strategy_slug>/run_summary.json>)
```

For CLI or TUI hosts, use the same absolute paths as plain text, not Markdown links:

```text
Result folder: /absolute/path/to/Quandora staging result/strategy/<strategy_slug>/
Result Bundle ZIP: /absolute/path/to/Quandora staging result/strategy/<strategy_slug>/<safe_filename>
Run summary: /absolute/path/to/Quandora staging result/strategy/<strategy_slug>/run_summary.json
```

If the host cannot write files, state:

```text
Result folder: unavailable in this host
Result Bundle ZIP: unavailable in this host
Run summary: unavailable in this host
```
