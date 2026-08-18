# Factor Result Bundle Contract

Use the canonical immutable ZIP as the primary completed-result evidence object.

## Acquisition

- Resolve one exact terminal `job_id` before requesting a bundle.
- Prefer `fm_bundle_ticket`; use `fm_bundle_chunk` only as the bounded fallback.
- Verify the whole downloaded byte sequence against the outer size and SHA-256 from MCP metadata.
- Keep the verified ZIP unchanged. Do not rebuild it or extract files beside it.

## Internal Integrity

The ZIP contains `artifact_manifest.json`. Its current schema is
`result_bundle.artifact_manifest.v1`. The manifest describes included, unavailable, pending, or
failed logical items. Every included item has a safe `zip_path`, exact `size_bytes`, and SHA-256.
The manifest intentionally does not contain the whole ZIP digest because that would be
self-referential.

Use `scripts/inspect_factor_bundle.py` to verify internal membership and digests. A successful
script result does not replace verification of the outer ticket or chunk digest.

## Canonical Product Contents

A Factor bundle can contain:

- `run_summary.json`;
- `factor_card_is.json`;
- exact executed `plugin.py` as inert source;
- optional `signal_raw.parquet`;
- `artifacts/is/group_return_plot.png`;
- `artifacts/is/cs_nav_curves.png`;
- `artifacts/is/cs_profile_4panel.png`;
- `artifact_manifest.json`.

Do not require every optional item. A partial bundle is valid evidence when its manifest truthfully
records omissions. Failed or cancelled runs may have less evidence.

## Embedded Health Evidence

`factor_card_is.json` may contain the QuantAI Factor Card `health_check` section and its nullable
fields. Factor Health is embedded compatibility evidence delivered through the existing canonical
bundle; it is not a separately invocable MCP or typed standalone capability. Use the preserved
values, thresholds, window, and basis without recomputing or filling omissions.

The card may also expose `cs_success`, `cs_fail_reasons`, `status`, `grade`, and `grade_score` for
rating-gate tracing. Do not require internal-only check collections that are absent from the
product-safe projection. External-agent evidence remains IS-only even if an upstream provider has
internal OOS or ALL cards.

## Trust Rules

- The external-agent Factor bundle is IS-only. Do not label any member OOS or ALL.
- Product JSON is a safe projection, not necessarily the provider's raw object.
- `plugin.py` is evidence of the executed factor source but must never be imported or executed.
- Missing, unavailable, and null values are not zero.
- Missing `health_check` or `health_check.passed=null` is not a pass. Preserve the distinction
  between an unknown Health outcome and any fail-closed outer rating behavior recorded by the card.
- Legacy loose files or extracted directories lack the complete immutable-bundle proof. State that
  limitation and narrow conclusions accordingly.
- Do not live-fetch a provider, storage URL, or internal service to fill an omission.
