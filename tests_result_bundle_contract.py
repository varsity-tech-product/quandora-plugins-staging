"""RED contract checks for one-ZIP Result Bundle delivery in staging skills."""

import re
from pathlib import Path


ROOT = Path(__file__).parent
FACTOR = " ".join(
    (ROOT / "plugins/quandora-staging/skills/factor-mining/SKILL.md").read_text().split()
)
STRATEGY = " ".join(
    (ROOT / "plugins/quandora-staging/skills/strategy-building/SKILL.md").read_text().split()
)
ROOT_README = " ".join((ROOT / "README.md").read_text().split())
PLUGIN_README = " ".join(
    (ROOT / "plugins/quandora-staging/README.md").read_text().split()
)
PUBLIC_TEXT = "\n".join((FACTOR, STRATEGY, ROOT_README, PLUGIN_README))


def test_factor_skill_uses_url_first_and_automatic_bounded_fallback():
    assert "fm_bundle_ticket" in FACTOR
    assert "fm_bundle_chunk" in FACTOR
    assert "256 KiB" in FACTOR or "262,144" in FACTOR
    assert ".partial" in FACTOR
    assert "atomic" in FACTOR.lower()


def test_strategy_skill_uses_bundle_manifest_instead_of_registry_loop():
    assert "sb_bundle_ticket" in STRATEGY
    assert "sb_bundle_chunk" in STRATEGY
    assert "manifest" in STRATEGY.lower()
    assert "Do not loop over artifact names or issue one ticket per file" in STRATEGY


def test_factor_skill_states_one_ticket_retry_then_fallback_without_contradiction():
    assert "issue one initial `fm_bundle_ticket`" in FACTOR
    assert "after one transient URL failure, at most one fresh ticket" in FACTOR
    assert "after that failure, move to MCP fallback" in FACTOR
    assert "never reuse a single-use URL/ticket" in FACTOR
    assert "call `fm_bundle_ticket` exactly once" not in FACTOR
    assert "call `fm_bundle_ticket` once" not in FACTOR


def test_strategy_skill_states_one_ticket_retry_then_fallback_without_contradiction():
    assert "issue one initial `sb_bundle_ticket`" in STRATEGY
    assert "after one transient URL failure, at most one fresh ticket" in STRATEGY
    assert "after that failure, move to MCP fallback" in STRATEGY
    assert "never reuse a single-use URL/ticket" in STRATEGY
    assert "call `sb_bundle_ticket` exactly once" not in STRATEGY
    assert "call `sb_bundle_ticket` once" not in STRATEGY


def test_factor_skill_has_independent_fallback_bounds_and_continuation_rules():
    assert "automatically use `fm_bundle_chunk`" in FACTOR
    assert "offset `0`" in FACTOR
    assert "262,144" in FACTOR or "262144" in FACTOR
    assert "10 MiB" in FACTOR
    assert "40 chunk calls" in FACTOR
    assert "validated `next_offset`" in FACTOR
    assert "snapshot_revision" in FACTOR


def test_strategy_skill_has_independent_fallback_bounds_and_continuation_rules():
    assert "automatically use `sb_bundle_chunk`" in STRATEGY
    assert "offset `0`" in STRATEGY
    assert "262,144" in STRATEGY
    assert "10 MiB" in STRATEGY
    assert "40 chunk calls" in STRATEGY
    assert "validated `next_offset`" in STRATEGY
    assert "snapshot_revision" in STRATEGY


def test_factor_skill_describes_pb_terminal_true_without_second_public_empty_chunk():
    assert "PB's `terminal: true`" in FACTOR
    assert "no second public empty chunk" in FACTOR


def test_strategy_skill_describes_pb_terminal_true_without_second_public_empty_chunk():
    assert "PB's `terminal: true`" in STRATEGY
    assert "no second public empty chunk" in STRATEGY


def test_factor_skill_stops_all_three_non_readable_statuses_before_delivery():
    for status in ("pending", "not_available", "integrity_failure"):
        assert status in FACTOR
    assert "no URL, no chunk, no fabricated file" in FACTOR


def test_strategy_skill_stops_all_three_non_readable_statuses_before_delivery():
    for status in ("pending", "not_available", "integrity_failure"):
        assert status in STRATEGY
    assert "no URL, no chunk, no fabricated file" in STRATEGY


def test_strategy_skill_uses_public_result_run_id_and_forbids_fm_selector():
    assert "public `result.run.id`" in STRATEGY
    assert "never substitute `fmRunId`" in STRATEGY


def test_each_skill_keeps_one_canonical_completed_zip_and_compatibility_only_file_tools():
    assert "FM-owned ZIP is the only canonical completed-result archive" in FACTOR
    assert "FM-owned ZIP is the only canonical completed-result archive" in STRATEGY
    assert "never create a second completed-result `run_summary.json`" in FACTOR
    assert "never create a second completed-result `run_summary.json`" in STRATEGY
    assert "user request that explicitly asks for one compatibility artifact" in FACTOR
    assert "user request that explicitly asks for one compatibility artifact" in STRATEGY
    assert "Run summary: [run_summary.json]" not in FACTOR
    assert "Run summary: [run_summary.json]" not in STRATEGY


def test_factor_completed_zip_uses_root_slug_name_and_atomic_partial_path():
    assert "Quandora staging/<factor_slug>.zip" in FACTOR
    assert "Quandora staging/<factor_slug>.zip.partial" in FACTOR
    assert "atomically rename" in FACTOR.lower()
    assert "Quandora staging result/factor-mining/" not in FACTOR


def test_strategy_completed_zip_uses_root_slug_name_and_atomic_partial_path():
    assert "Quandora staging/<strategy_slug>.zip" in STRATEGY
    assert "Quandora staging/<strategy_slug>.zip.partial" in STRATEGY
    assert "atomically rename" in STRATEGY.lower()
    assert "Quandora staging result/strategy/" not in STRATEGY


def test_remote_safe_filename_stays_bound_transport_metadata_not_local_name():
    for skill in (FACTOR, STRATEGY):
        assert "`safe_filename`" in skill
        assert "transport metadata only" in skill
        assert "never determines the local display filename" in skill


def test_verified_zip_is_retained_without_automatic_extraction_or_reconstruction():
    for skill in (FACTOR, STRATEGY):
        assert "Do not automatically extract" in skill
        assert "delete it" in skill
        assert "re-ZIP" in skill
        assert "reconstruct" in skill


def test_factor_readable_partial_gets_at_most_one_bounded_current_refresh():
    assert "persisted readable `partial`" in FACTOR
    assert "runtime manifest" in FACTOR
    assert "wait at most 10 seconds" in FACTOR
    assert "exactly one fresh current `fm_bundle_ticket`" in FACTOR
    assert "without `snapshot_revision`" in FACTOR
    assert "Never loop or poll for freshness" in FACTOR
    assert "let it expire naturally" in FACTOR


def test_strategy_readable_partial_gets_at_most_one_bounded_current_refresh():
    assert "persisted readable `partial`" in STRATEGY
    assert "runtime manifest" in STRATEGY
    assert "wait at most 10 seconds" in STRATEGY
    assert "exactly one fresh current `sb_bundle_ticket`" in STRATEGY
    assert "without `snapshot_revision`" in STRATEGY
    assert "Never loop or poll for freshness" in STRATEGY
    assert "let it expire naturally" in STRATEGY


def test_partial_refresh_failure_rules_preserve_valid_partial_and_fail_closed():
    for skill in (FACTOR, STRATEGY):
        assert "transient transport failure" in skill
        assert "retain the initial valid readable partial" in skill
        assert "malformed contract response" in skill
        assert "fail closed" in skill


def test_optional_artifact_never_blocks_readable_partial_delivery():
    assert "Raw Parquet is optional" in FACTOR
    assert "must not block a readable partial" in FACTOR
    assert "No individual artifact is a prerequisite" in STRATEGY
    assert "must not block a readable partial" in STRATEGY


def test_remaining_partial_is_downloaded_and_reports_runtime_omissions():
    for skill in (FACTOR, STRATEGY):
        assert "selected response remains readable `partial`" in skill
        assert "download it normally" in skill
        assert "exact runtime omissions and pending reasons" in skill
        assert "Do not use legacy per-file tools to fill" in skill


def test_freshness_refresh_is_distinct_from_url_retry_and_chunk_fallback():
    assert "freshness refresh is separate from" in FACTOR
    assert "freshness refresh is separate from" in STRATEGY
    assert "after one transient URL failure, at most one fresh ticket" in FACTOR
    assert "after one transient URL failure, at most one fresh ticket" in STRATEGY
    assert "automatically use `fm_bundle_chunk`" in FACTOR
    assert "automatically use `sb_bundle_chunk`" in STRATEGY


def test_agent_mined_or_authored_factor_never_uses_import():
    assert "agent mined or authored" in STRATEGY
    assert "must never call `sb_import_factor`" in STRATEGY
    assert "Result Bundle" in STRATEGY
    assert "must not be re-imported" in STRATEGY


def test_normal_strategy_path_resolves_agent_factor_through_eligible_inventory():
    assert "canonical eligible-factor inventory" in STRATEGY
    assert "exact canonical factor id" in STRATEGY
    assert "one bounded eligible-list query" in STRATEGY
    assert "one unique exact-name match" in STRATEGY
    assert "Do not use fuzzy name inference" in STRATEGY
    assert "do not read its bundle or import its source" in STRATEGY


def test_import_is_user_supplied_only_with_real_session_and_post_import_eligibility():
    for phrase in (
        "explicitly supplied or attached a complete `plugin.py`",
        "agent did not write or mine",
        "explicitly asked to use",
        "current host exposes `sb_import_factor` and its current schema",
        "real current-owner `session_id` returned during the current workflow",
        "Never derive or guess a session id",
        "canonical eligible-factor inventory before using it",
    ):
        assert phrase in STRATEGY


def test_import_tool_is_not_a_global_strategy_prerequisite():
    assert "normal Strategy workflow must not require or call `sb_import_factor`" in STRATEGY
    assert "Check import-only tool availability only after" in STRATEGY


def test_public_readmes_use_root_level_slug_zip_examples():
    for readme in (ROOT_README, PLUGIN_README):
        assert "Quandora staging/<factor_slug>.zip" in readme
        assert "Quandora staging/<strategy_slug>.zip" in readme
        assert "Quandora staging result/factor-mining/" not in readme
        assert "Quandora staging result/strategy/" not in readme


def test_public_guidance_does_not_freeze_mutable_backend_details():
    assert not re.search(r"\b[0-9]+-name registry\b", PUBLIC_TEXT)
    assert not re.search(r"\b(?:factor|strategy)-result-", PUBLIC_TEXT)
    assert "Do not make any individual artifact a prerequisite" in FACTOR
    assert "Never hardcode an artifact registry or count" in STRATEGY
    assert "orchestrator/" not in PUBLIC_TEXT
    assert "grpc_server.py" not in PUBLIC_TEXT
    assert "result_bundles.py" not in PUBLIC_TEXT
    assert "implementation commit" not in PUBLIC_TEXT.lower()
    assert not re.search(r"\b[0-9]+\.[0-9]+\.[0-9]+-staging\.[0-9]+\b", PUBLIC_TEXT)
    assert not re.search(r"\b[0-9a-f]{40}\b", PUBLIC_TEXT)
    assert "/Users/" not in PUBLIC_TEXT
    assert "/home/" not in PUBLIC_TEXT
