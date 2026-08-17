# Strategy Result Bundle Contract

Pair the Product Backend run snapshot with the canonical immutable ZIP whenever both are available.

## Identity And Configuration

- `sb_list_runs` discovers one bounded owner-scoped page, newest first.
- `sb_get_run` is authoritative for canonical composition and effective parameters.
- `sb_bundle_ticket` and `sb_bundle_chunk` select the immutable bundle by exact `run_id`.
- Never substitute an FM run id, Strategy id, StrategyVersion id, name, or chart identity for the PB
  `run_id`.

## Integrity

Verify the entire downloaded byte sequence against MCP metadata. Inside the ZIP,
`artifact_manifest.json` records each logical source artifact and every included member's
product-facing `zip_path`, size, and SHA-256. The outer ZIP digest is intentionally not embedded in
the manifest.

Use `scripts/inspect_strategy_bundle.py` for bounded internal validation. Keep the verified ZIP
unchanged and do not extract files beside it.

## Current Product Layout

The bundle contains `run_summary.json`, `artifact_manifest.json`, and the included subset of 22
retained Strategy source artifacts under product-facing paths:

- JSON: status, summary, equity, drawdown, turnover, exposure, orders, charts, trades, performance,
  attribution, signal-return curves, result, and six-chart numeric data;
- text: logs and code;
- images: prediction quantiles, long/short style, style exposure, decay, prediction-style
  correlation, and daily turnover.

`six_charts_data.json` is available at `artifacts/six_charts_data.json` only when retained. Historical
21-artifact inventories remain truthful and must not be synthesized into 22.

## Partial And Offline Evidence

- A partial manifest is valid for included evidence. Name unavailable or failed items.
- JSON and each PNG are independent; one can be absent while another is present.
- Offline ZIP-only analysis may lack the PB-owned effective composition and parameters. Disclose the
  gap instead of guessing.
- Legacy extracted directories are partial evidence because they lack the complete immutable ZIP
  and outer-digest proof.
- Never execute `artifacts/code.txt`, logs, or any archive member.
