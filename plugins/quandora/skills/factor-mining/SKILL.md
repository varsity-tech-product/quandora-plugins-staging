---
name: factor-mining
description: Use when an agent should create or submit a Quandora Factor Mining plugin.py, run a user-scoped backtest, wait for workflow results, fetch safe artifacts, summarize outcomes, or resume a run through Quandora Remote MCP.
---

# Quandora Factor Mining

Use this skill for Factor Mining through the Quandora Remote MCP server
`quandora-mcp`. The agent drafts a valid Factor Mining `plugin.py`
source, submits that source inline through Remote MCP, waits for the backtest
result, fetches safe artifacts, and summarizes the outcome.

The host should expose `quandora-mcp` tools through the installed Quandora
plugin or connector. If the tools are visible, continue automatically. If the
tools are not visible in a Codex host, first check whether the host can run
`codex mcp login quandora-mcp`; use that command to start the official OAuth
connection flow when available. After authorization, tell the user to start a
new chat; if tools still do not appear, tell them to fully quit and reopen
Codex Desktop, then start a new chat. In non-Codex hosts where no MCP login
command or connector UI is available, stop with a concise connection-required
message naming `quandora-mcp`. Do not treat `factor_mining_status` as a
bootstrap tool because it is only callable after the host exposes the Remote
MCP tools.

Do not use raw HTTP calls, local helper scripts, direct Product Backend calls,
direct Factor Mining calls, local execution keys, `vt_` keys, or credential
paste flows as a fallback.

## Remote MCP Tools

Use only these v0.4.10 Factor Mining tools:

- `factor_mining_status`
- `factor_mining_list_public_tasks`
- `factor_mining_create_task_session`
- `factor_mining_create_custom_session`
- `factor_mining_validate_plugin_source`
- `factor_mining_request_dedup_context`
- `factor_mining_upload_backtest_wait`
- `factor_mining_resume_run`
- `factor_mining_get_artifact`

Some hosts may prefix tool names with the server name, such as
`quandora-mcp__factor_mining_status`. Treat those as the same tools.

Do not use or advertise batch mining in v0.4.10.

## Workflow

Start with `factor_mining_status`. If the tool call reports missing
authorization, use the host's MCP OAuth path. Do not ask for Quandora API keys
or `vt_` keys.

Determine whether the user wants a public task or a custom idea:

- For public tasks, call `factor_mining_list_public_tasks`, show concise
  choices, and ask the user to pick one unless they explicitly ask the agent to
  choose. Then call `factor_mining_create_task_session`.
- For a custom idea, call `factor_mining_create_custom_session` with a clear
  title, category, description, non-empty `allowed_data`, and `fwd_period`.
  Include every input column the generated factor needs, such as `close`,
  `volume`, `funding_rate_close`, or `open_interest_close`.

Before submission, call `factor_mining_request_dedup_context` with the session
context and revise the factor if the returned similar-factor guidance shows a
near duplicate.

Create or locate one `plugin.py` source. In local coding hosts with a writable
workspace, save the working copy as `plugin.py`, read it back, and send the
complete contents as inline `plugin_source`. In chat-only hosts such as Claude
Desktop, keep the generated source in the conversation/tool-call context and
submit it directly as inline `plugin_source`; do not require a local file.
Never submit a filesystem path or ask the Remote MCP server to read local
files. Validate the source with `factor_mining_validate_plugin_source`. The
validation step is static; do not import, execute, eval, or shell-run generated
factor code.

When the source is valid and the user is ready to submit, call
`factor_mining_upload_backtest_wait` with `session_id`, inline `plugin_source`,
and the selected `fwd_period` when required. Use `fwd_period=7` only when
neither the task nor the user specifies a horizon.

When a session is created in a local coding host with a writable workspace,
create a run archive before writing `plugin.py`. Use this path shape:

```text
results/factor-mining/<session_id>/attempt-<n>/
```

Use `attempt-1` for the first submission in a session and increment it only
when submitting a revised factor in the same session. If a session has not been
created yet but a local folder is needed, use
`results/factor-mining/local-YYYYMMDD-HHMMSS/` and move or copy the files into
the session folder after the session exists.

In local coding hosts, save the submitted source as `plugin.py` inside the run
archive before validation and upload. Read the file back and submit the full
contents as inline `plugin_source`; never submit a filesystem path. After each
tool result, save safe result files into the same run archive:

- `run_summary.json` for the redacted structured run summary.
- `factor_card.json` for factor-card metrics when available.
- `artifacts/<artifact_name>` for safe artifacts fetched with
  `factor_mining_get_artifact`.

Use `factor_mining_resume_run` when a prior run was interrupted. Use
`factor_mining_get_artifact` only for artifact identifiers returned by Remote
MCP. Do not save bearer tokens, presigned URLs, raw service metadata, hidden
backend IDs, or credentials. If a host does not support file writes, continue
the Remote MCP workflow and say that local archiving is not available in that
host.

## Summary Rules

Always inspect `ok`, `status`, `terminal_status`, `failures`, sanitized job
statuses, artifact availability, and factor-card metrics. If `ok` is false or
failures are present, report the failed or cancelled terminal status clearly.

Never show backend job IDs, presigned URLs, bearer tokens, raw credentials, or
full `plugin.py` source in user-facing summaries. Use concise filenames for
saved artifacts instead of local absolute paths.

At the end of every completed, failed, or interrupted run, explicitly print a
short line with the local result path when a run archive was created:

```text
Result folder: results/factor-mining/<session_id>/attempt-<n>/
```

This line is required even when the rest of the answer contains analysis,
metrics, or next-step guidance. If the host could not write files, print:

```text
Result folder: not available in this host
```

## plugin.py Contract

Use this minimum shape when the user has not supplied an existing plugin. The
metadata values must be static top-level literals so Quandora can parse them
without executing source code.

```text
from typing import Any, Dict

import pandas as pd

FACTOR_TYPE = "snake_case_unique_factor_type"
FACTOR_NAME = "human_readable_factor_name"
FACTOR_DEFAULT_PARAMS = {"window": 7}

FACTOR_SECTIONS = {
    "__FACTOR_DESCRIPTION__": "Trailing close-to-close momentum.",
    "__FACTOR_FORMULA__": "close / close[window bars ago] - 1",
    "__FACTOR_TYPE__": FACTOR_TYPE,
    "__FACTOR_PARAM_FIELDS__": "        private int _window;\n",
    "__FACTOR_INIT__": '            _window = GetIntParameter("window", 7);\n',
    "__FACTOR_LOG__": '            Log($"[INIT] window={_window}");\n',
    "__PRICE_WINDOW_EXPR__": "_window + 1",
    "__EXTRA_BUF_FIELDS__": "",
    "__EXTRA_BUF_ENQUEUE__": "",
    "__EXTRA_BUF_DEQUEUE__": "",
    "__EXTRA_BUF_TOARRAY__": "",
    "__FACTOR_COMPUTE_BODY__": """
            var n = prices.Length;
            if (n < _window + 1) return false;
            var past = prices[n - _window - 1];
            if (past == 0) return false;
            rawSignal = prices[n - 1] / past - 1.0;
            return true;
""",
}


def build_signal(close: pd.DataFrame, params: Dict[str, Any], **data: Any) -> pd.DataFrame:
    window = int(params.get("window", FACTOR_DEFAULT_PARAMS["window"]))
    signal = close.pct_change(window)
    return signal.reindex_like(close)
```

Keep `build_signal` and `FACTOR_SECTIONS` compute logic aligned. Return a
`pd.DataFrame` aligned with `close`, use only current and historical data, and
keep all data columns within the session `allowed_data` contract.

## Security

- Use only Quandora Remote MCP tools for formal product actions.
- Never ask for OpenAI API keys, Codex auth files, BYOK secrets, frontend user
  credentials, raw Factor Mining credentials, local execution keys, or `vt_`
  keys.
- Never print, persist in logs, or summarize full credential values.
- Do not call hosted generation endpoints; the active agent generates factor
  source in its current host session.
- Do not call frontend-user credential management, BYOK, Codex profile, task
  publishing, Product Backend URLs, Factor Mining URLs, or generic URL/API
  surfaces.
- Do not import, exec, eval, or otherwise execute generated `plugin.py`.
- Do not submit filesystem paths instead of inline `plugin_source`.
- Do not print generated `plugin.py` source in summaries.
- Treat downstream IDs, presigned URLs, and service metadata as internal.
- Artifact `404` and `410` responses mean unavailable. Authentication,
  authorization, network, malformed response, and server errors must fail
  clearly with redacted messages.
