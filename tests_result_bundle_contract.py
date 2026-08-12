"""RED contract checks for one-ZIP Result Bundle delivery in staging skills."""

from pathlib import Path


ROOT = Path(__file__).parent
FACTOR = (ROOT / "plugins/quandora-staging/skills/factor-mining/SKILL.md").read_text()
STRATEGY = (ROOT / "plugins/quandora-staging/skills/strategy-building/SKILL.md").read_text()


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
    assert "per-file" not in STRATEGY.lower()


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
    assert "explicit single-artifact compatibility or rollback" in FACTOR
    assert "explicit single-artifact compatibility or rollback" in STRATEGY
    assert "Run summary: [run_summary.json]" not in FACTOR
    assert "Run summary: [run_summary.json]" not in STRATEGY
