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

Before starting, confirm that the Quandora Staging connection is authenticated and check only the
actions needed for the requested path. A normal list, composition, submit, observe, and Result
Bundle workflow uses the relevant subset of `sb_get_contract`, `sb_list_eligible`,
`sb_factor_detail`, `sb_shared_list`, `sb_shared_add`, `sb_submit_run`, `sb_get_run`,
`sb_resume_run`, `sb_bundle_ticket`, and `sb_bundle_chunk`. `sb_get_artifact` and `sb_file_ticket`
remain legacy single-artifact compatibility actions. Use `qd_get_guidance` only for one of the
documented guidance branches below.

The normal Strategy workflow must not require or call `sb_import_factor`. Import-only actions are
not global prerequisites, and an ordinary Strategy task must continue when they are absent. Check
import-only tool availability only after the explicit user-supplied-file branch below has been
selected.

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

#### Agent-mined or Agent-authored Factor Selection

An agent mined or authored factor always follows the canonical eligible-factor inventory; it must
never call `sb_import_factor`. This includes `plugin.py` found inside an FM-owned Result Bundle,
which must not be re-imported.

- If the exact canonical factor id returned by the mining workflow is already known, make the
  supported `sb_list_eligible` query for that exact id and require that exact row.
- If only the exact returned factor name is known, make one bounded eligible-list query and require
  one unique exact-name match. Do not use fuzzy name inference, partial matching, or a locally
  cached guess.
- If the exact factor is not returned as eligible, stop and report that state. In particular, do
  not read its bundle or import its source as a workaround.

#### User-supplied External Import

Import is permitted only when all of these facts are true: the user explicitly supplied or
attached a complete `plugin.py`; the agent did not write or mine that file; the user explicitly
asked to use that supplied file in Strategy Building; and the current host exposes
`sb_import_factor` and its current schema. Otherwise stay on the normal eligible-factor path.

Only after this branch is selected, inspect the currently exposed schemas for `sb_import_factor`
and any Factor Mining session action it requires. Call only schema-declared arguments; do not copy
a backend request schema into this skill. If import semantics are needed, use the approved
`operation.strategy.factor.import` guidance and its current invocation boundary.

Before import, require a real current-owner `session_id` returned during the current workflow.
Never derive or guess a session id from a path, filename, factor name, job id, run id, Result
Bundle, or conversation history. If no session exists, follow the Factor Mining skill's existing
custom-session setup through the current exposed contracts to obtain one, or stop if that
prerequisite cannot be completed.

Use only real lifecycle identifiers returned by `sb_import_factor`. If its current response says
to resume, use only the exact returned run identifier with the current Factor Mining bounded resume
policy; never substitute another identifier or add an import poller. After import or resume,
require the exact returned factor to appear in the canonical eligible-factor inventory before
using it. Never submit a Strategy until that exact factor is returned as currently eligible.

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

After the Strategy main run is terminal and archive state permits bundle metadata, issue one initial
`sb_bundle_ticket` with the exact public `result.run.id`. Pass that public PB run handle unchanged
to `sb_bundle_ticket` and `sb_bundle_chunk`; never substitute `fmRunId` or any hidden upstream
selector. The returned closed metadata and runtime manifest are authoritative for the immutable
FM-owned ZIP. Treat both `available` and a persisted readable `partial` response as downloadable.
No individual artifact is a prerequisite, and an optional item that remains unsynchronized must
not block a readable partial. Never hardcode an artifact registry or count.

Validate the server-provided `safe_filename` as a basename and bind it consistently across the
selected ticket and every chunk response. It is transport metadata only and never determines the
local display filename. Likewise bind the bundle kind, public selector, snapshot revision, content
type, size, whole-ZIP SHA-256, and runtime manifest according to the existing closed response
contract.

Apply this one optional freshness step before downloading:

1. If the initial ticket is persisted readable `partial` and its runtime manifest reports one or
   more items with a pending status, wait at most 10 seconds with a short host-native wait or timer.
   Then issue exactly one fresh current `sb_bundle_ticket` with the same public selector and
   without `snapshot_revision`. Never loop or poll for freshness.
2. Do not consume, reuse, display, or log the superseded ticket URL; let it expire naturally. If
   the refresh returns a valid readable newer snapshot, select that response. If it has a transient
   transport failure, retain the initial valid readable partial. If it is a malformed contract
   response, fail closed instead of masking it.
3. If the selected response remains readable `partial`, download it normally, state clearly that
   the snapshot is partial, and report the exact runtime omissions and pending reasons from its
   selected manifest. If the initial partial reports no pending item, do not wait or refresh. A
   later independent user request may obtain a newer current snapshot after synchronization.

This optional freshness refresh is separate from the URL-delivery retry below and does not consume
that retry. Do not use legacy per-file tools to fill an omitted item or rebuild the selected
immutable ZIP. Do not loop over artifact names or issue one ticket per file. Keep
`sb_get_artifact` and `sb_file_ticket` only for a user request that explicitly asks for one
compatibility artifact; they are not bundle-completion tools.

Use this URL-first delivery once per request:

1. Require ZIP content type, non-negative size, lowercase SHA-256, and the exact safe local
   destination `Quandora staging result/<strategy_slug>.zip`. Write only to
   `Quandora staging result/<strategy_slug>.zip.partial` until verification finishes. If the final path
   already contains unrelated bytes or cannot be proven to match the selected ZIP, do not
   overwrite it silently: tell the user and use a different safe user-facing slug chosen with the
   user, never an internal backend identifier.
2. Stream the opaque Auth `download_url` directly to the task-created `.partial`, maintaining byte
   count and SHA-256. Do not print, log, save, edit, or reuse the URL. Retry rule: after one transient
   URL failure, at most one fresh ticket may be issued for one retry; after that failure, move to
   MCP fallback; never reuse a single-use URL/ticket.
3. Verify exact size and SHA-256, ZIP magic/openability, and safe relative ZIP entry paths, then
   atomically rename the verified `.partial` to `Quandora staging result/<strategy_slug>.zip`.

If the URL is unavailable, blocked by local host network policy, expired, or fails after that one retry, automatically use `sb_bundle_chunk` with the same exact public `result.run.id` and `snapshot_revision`. The fallback uses the already-working authenticated MCP connection and requires no new host-native file sink or shell network access. Start at offset `0`, request at most `262,144` raw bytes per call, decode `content_b64` without printing or logging it, append to the same task-created `.partial`, and follow only validated `next_offset`. Enforce the 10 MiB ZIP cap and at most 40 chunk calls. PB's `terminal: true` means PB consumed and validated FM's empty upstream final marker; it is the terminal continuation response, so there is no second public empty chunk to request. Require that terminal response and exact size/whole-ZIP SHA-256 before ZIP/path verification and atomic rename. Never mix revisions or append an old partial; on interruption or terminal fallback failure discard only the unverified task-created `.partial` and report that no verified ZIP was saved.

If bundle metadata is `pending`, `not_available`, or `integrity_failure`, stop before URL/chunk/file creation: no URL, no chunk, no fabricated file. Preserve its safe status/reason and do not invent a completed bundle.

Preserve the verified ZIP as the canonical local output. Do not automatically extract the ZIP,
delete it, re-ZIP it, or reconstruct a replacement archive from individual files. Do not modify ZIP
entry timestamps: deterministic entry timestamps belong to the FM-owned archive, and the agent must
not rebuild the ZIP to change how a file browser displays them.

## Local Result Destination

Do not assemble a separate local archive or extracted directory for the strategy. Build
`<strategy_slug>` only from the current user-facing submitted Strategy name, whether user-supplied
or generated: lowercase it, replace each run of non-`[a-z0-9]` characters with one underscore,
trim outer underscores, truncate it to at most 48 characters, and use `strategy` if the result is
empty. The slug must not contain a backend UUID, factor id, internal selector, snapshot revision,
remote filename prefix, fingerprint, or path separator.

The only canonical completed local path is:

```text
Quandora staging result/<strategy_slug>.zip
```

The slug is a local presentation label only and must not be sent in an action request. For a
non-terminal or archive-pending run, preserve the existing redacted run-summary behavior in the
normal authoring workspace when local writes are available. For a completed run, the FM-owned ZIP
is authoritative and no second canonical `run_summary.json` is written beside it. Never place a
ticket, URL, internal host, storage reference, credential, or bundle bytes in local metadata or
user-facing output.

## Final Response

State the submitted strategy name and whether it was user-supplied or factor-aware generated. State
the main-run status, archive status, safe diagnostics, and the one verified Result Bundle ZIP path
when saved. If it was not saved, say so accurately; do not print large artifact bodies or describe a
manually assembled archive.

For a selected partial snapshot, state that it is partial and report the exact omissions and pending
reasons from the runtime manifest without claiming completeness.

Never show run ids, download URLs, credentials, secret material, or internal service metadata in a
user-facing summary.

For a main run that remains non-terminal after the twelfth follow-up, clearly state that the
server-side run remains in progress and can be resumed later. State that terminal archive
observation and bundle retrieval were not started, and do not state that results or bundles are
available.

At the end of every completed, failed, or interrupted run, show the `Quandora staging result/` folder and
the exact `Quandora staging result/<strategy_slug>.zip` path when the ZIP was saved. For a non-terminal or
archive-pending run, mention `run_summary.json` only when the normal authoring workflow saved that
pending summary. For a completed run, the FM-owned ZIP is the only canonical completed-result
archive; never create a second completed-result `run_summary.json` beside it. If a specific file was
not created, say `not created`. Never show run IDs, snapshot revisions, tickets, download URLs,
credentials, or bundle base64.

For Desktop or GUI hosts, use Markdown links with absolute local paths and angle-bracket link
targets so paths with spaces work:

```text
Result folder: [Open result folder](</absolute/path/to/Quandora staging result/>)
Result Bundle ZIP: [verified ZIP](</absolute/path/to/Quandora staging result/<strategy_slug>.zip>)
```

For CLI or TUI hosts, use the same absolute paths as plain text, not Markdown links:

```text
Result folder: /absolute/path/to/Quandora staging result/
Result Bundle ZIP: /absolute/path/to/Quandora staging result/<strategy_slug>.zip
```

If the host cannot write files, state:

```text
Result folder: unavailable in this host
Result Bundle ZIP: unavailable in this host
Run summary: unavailable in this host
```
