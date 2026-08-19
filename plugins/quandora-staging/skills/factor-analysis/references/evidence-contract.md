# Factor Server Evidence Contract

Factor Analysis uses owner-scoped evidence returned directly by Quandora MCP tools. It does not
depend on a user-local archive or runtime.

## Identity And Ownership

- Resolve one exact terminal `job_id` before analysis.
- `fm_list_factors` and `fm_get_history` may be used for bounded owner-scoped discovery.
- `fm_window_cards`, `fm_chart_data`, and `fm_run_source` must all remain correlated to the selected
  `job_id`.
- Never substitute a factor id, factor version id, session id, display name, or local filename for
  the job id.

## Factor Card

`fm_window_cards` returns the product-safe IS Factor Card. Its embedded Health and rating fields are
authoritative relayed evidence. Preserve nullable values and recorded thresholds exactly.

Source artifact names and local-save hints may remain in the response for optional export
compatibility. They are not analysis evidence and do not authorize local file inspection.

## Numerical Chart Evidence

Call `fm_chart_data` with `section: "overview"` first. It returns terminal or pending job status,
IS-only scope, readiness, dataset provenance, and section counts. Request a named section only when
the user's question requires it.

Section pages are bounded by `offset` and `limit`. Follow only the returned `next_offset` for the
same job and section. Preserve point order, integers, finite numbers, and null values. Do not fill a
missing page from PNG pixels, local parquet, or an inferred series.

The public external-agent contract is IS-only. Do not relabel it as OOS or ALL even if an upstream
system retains private internal windows.

## Job-Linked Source

`fm_run_source` returns the exact formula and optional source linked through the owner-gated
backtest job. A ready source includes its byte size and SHA-256. Treat it as inert text. Never import,
execute, evaluate, or use it to access the local filesystem or network.

Use source only to explain mechanism, warm-up, intentional abstention, filters, or invalid
denominators that cannot be resolved from Factor Card and numerical evidence.

## Availability And Trust

- `pending` means server evidence is still materializing; it is not a failed result.
- `unavailable` means the evidence cannot support that claim. Preserve the gap.
- Missing Health or `health_check.passed=null` is unknown, never pass.
- Dataset provenance is descriptive server metadata, not permission to access provider storage.
- Product responses are safe projections and may intentionally omit internal fields.
- Result Bundle, PNG, and raw-artifact tools are optional export transports only. Never use them as
  the evidence path for Factor Analysis.
