# Quandora Staging

Quandora Staging is the public staging plugin package for pre-release Quandora agent workflow testing. It points to staging services and is not the production plugin.

## What Factor Mining Does

Quandora Staging Factor Mining helps an agent:

1. Connect to the user's staging Quandora account through the host's MCP authorization flow.
2. List public factor-mining tasks or create a custom factor session.
3. Generate a valid `plugin.py` in the local workspace when file writes are available.
4. Submit the factor source inline to Quandora Staging.
5. Wait for the backtest, retrieve available factor cards and chart artifacts, and summarize the result.
6. Save the local working files and returned results together.

## Result Files

When the host supports local files, Factor Mining archives each run under:

```text
Quandora staging result/factor-mining/aggressive_flow_exhaustion_reversal/
```

The archive is named from the factor slug, preferably the generated `FACTOR_TYPE`. It contains the submitted `plugin.py`, a redacted `run_summary.json`, `factor_card_is.json` and `factor_card_all.json` when available, `artifact_manifest.json`, and PNG charts under `artifacts/is/` and `artifacts/all/`. PNG API calls use the returned server `source_name`; local files are saved to `standard_local_path`, whose filenames intentionally remove the `default_` prefix and p2/p3 suffixes. The agent prints the result, artifact, and chart folder paths after each run so the user can open the files directly.

## Skills

```text
skills/
  factor-mining/
```
