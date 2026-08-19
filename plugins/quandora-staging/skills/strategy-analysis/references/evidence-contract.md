# Strategy Server Evidence Contract

Strategy Analysis pairs Product Backend's owner-scoped run snapshot with server-retained artifacts
and bounded six-chart numerical evidence. It does not depend on a user-local archive or runtime.

## Identity And Configuration

- `sb_list_runs` discovers one bounded owner-scoped page, newest first.
- `sb_get_run` is authoritative for canonical composition and effective parameters.
- `sb_get_artifact` and `sb_analysis_data` must remain correlated to the exact selected `run_id`.
- Never substitute an FM run id, Strategy id, StrategyVersion id, name, local filename, or chart
  identity for the Product Backend run id.

## Core Artifacts

`sb_get_artifact` provides safe server-persisted artifacts independently. Summary and performance
are the headline result sources. Curves, attribution, signal-return evidence, orders, and trades
support narrower claims only when the corresponding artifact is ready.

An unavailable artifact does not invalidate independent ready artifacts, but it narrows the claims
that can be made. Preserve each status and all null fields. Never infer a missing artifact from an
expected name or from a local file.

## Six-Chart Evidence

`sb_analysis_data` reads the owner-gated retained `six_charts_data.json` through the server and
returns a closed bounded projection. Start with `chart: "overview"`; request individual chart pages
only when needed.

The overview reports artifact size and SHA-256, declared window and parameters, cross-section
summary, missing styles, and a chart catalog. Each chart page reports its offset, limit, total,
next offset, x-axis page, plotted series, legend, and colors. Preserve integer and null values
exactly.

The possible non-ready states are meaningful:

- `pending`: the retained result is still materializing;
- `not_available`: the artifact or selected chart is absent;
- `too_large`: the server refused analysis projection at its configured safety bound;
- `integrity_failed`: the retained stream did not pass server integrity checks.

Do not replace any of these states with PNG interpretation, local extraction, or reconstructed
data.

## Trust And Export Boundary

- Product responses are safe projections and may omit private provider or storage fields.
- Actual Strategy selection comes from `sb_get_run`, never from adaptive diagnostic chart buckets.
- `ALL` includes IS and is not pure OOS.
- Code and logs, when explicitly requested, are inert text and must never be executed.
- Result Bundle and artifact download tools are optional export transports only. Never use them as
  the evidence path for Strategy Analysis.
