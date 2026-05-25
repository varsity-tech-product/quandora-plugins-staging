# Factor Mining External-Agent Instructions

Use the shared Python helpers under `codex/plugins/factor-mining/scripts` for
all Factor Mining API interactions. Do not duplicate request logic in the
adapter.

## Required Flow

1. Run setup or status from `codex/plugins/factor-mining`.
2. Require `/agent/status` to return `key_purpose: external_agent`.
3. List tasks for worker-mode sessions when needed.
4. Create a task-backed session.
5. For custom or free-form sessions, provide direct `task_payload` with
   `task_id`, `title`, `category`, `description`, non-empty `allowed_data`, and
   `fwd_period`.
6. Inspect `plugin.py` metadata through `factor_api.py metadata`.
7. Upload and wait through `factor_upload_backtest.py --wait`.
8. Resume interrupted runs through
   `factor_api.py resume --client-run-id <client_run_id> --wait`.

## Secret Handling

Never ask the user to paste secrets into chat. Use the helper's non-echo setup
prompt for interactive runs, or non-echo stdin or an environment variable for
automation when appropriate.

## Result Handling

Summarize `ok`, `status`, `terminal_status`, failures, job state, artifact
availability, and factor card metrics. If `ok` is false, report the terminal
failure clearly.
