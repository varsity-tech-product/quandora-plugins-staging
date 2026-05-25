# Factor Mining Claude Code Adapter

This adapter provides Claude Code instructions for the Factor Mining
external-agent workflow. It reuses the shared Python helper scripts in
`codex/plugins/factor-mining/scripts` and does not reimplement Factor Mining API
requests.

## Files

- `skills/factor-mining/SKILL.md` contains the Claude Code skill instructions.
- `../codex/plugins/factor-mining/scripts/` contains the shared setup, API,
  upload, polling, resume, and metadata helpers.

## Security Model

Use the same Factor Mining Agent API Key flow as the Codex plugin. Setup must
call `/health` and `/agent/status`, and work must continue only when
`/agent/status` returns `key_purpose: external_agent`.

Never ask the user to paste secrets into chat. Use the helper's non-echo
terminal prompt for interactive setup. For automation, use non-echo stdin with
`--api-key-stdin` or a short-lived `FACTOR_MINING_AGENT_API_KEY` environment
variable when that is appropriate for the execution context.

## Helper Commands

Run commands from `codex/plugins/factor-mining`:

```bash
python3 scripts/factor_setup.py
python3 scripts/factor_status.py
python3 scripts/factor_api.py tasks --limit 20 --status open
python3 scripts/factor_api.py create-session --task-id <task_id> --client-run-id <client_run_id>
python3 scripts/factor_api.py create-session --idea "<research idea>" --task-payload-file task_payload.json --client-run-id <client_run_id>
python3 scripts/factor_api.py metadata --plugin-path plugin.py
python3 scripts/factor_upload_backtest.py --session-id <session_id> --plugin-path plugin.py --client-run-id <client_run_id> --position-mode both --fwd-period 7 --wait
python3 scripts/factor_api.py resume --client-run-id <client_run_id> --wait
```

Worker sessions use a published `task_id`. Custom or free-form sessions require
a direct `task_payload` before upload. The payload must include `task_id`,
`title`, `category`, `description`, non-empty `allowed_data`, and `fwd_period`.

The upload command returns compact JSON with `ok`, `status`,
`terminal_status`, workflow state, jobs, artifact availability, and summary
fields. Report failed or cancelled terminal jobs clearly.
