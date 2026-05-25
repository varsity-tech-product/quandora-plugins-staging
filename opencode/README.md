# Factor Mining OpenClaw/opencode Adapter

This directory is an adapter skeleton for OpenClaw/opencode. It documents the
Factor Mining external-agent contract and keeps a stable place for a future
verified manifest without claiming full target-tool support before the manifest
format is confirmed.

The adapter reuses the shared Python helpers in
`codex/plugins/factor-mining/scripts`. It must not duplicate the API client or
call Factor Mining endpoints directly.

## Structure

- `instructions/factor-mining.md` contains reusable agent instructions.
- `manifest/` is reserved for a verified OpenClaw/opencode manifest once the
  target schema is available.

## Security Rules

- Use only a delegated Factor Mining Agent API Key.
- Never ask the user to paste secrets into chat.
- Setup must call `/agent/status`.
- Continue only when `/agent/status` returns `key_purpose: external_agent`.
- Create task-backed sessions.
- Custom or free-form sessions require direct `task_payload`.
- Upload and wait through `factor_upload_backtest.py --wait`.
- Resume interrupted runs through `factor_api.py resume --client-run-id ... --wait`.

## Shared Helper Commands

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
