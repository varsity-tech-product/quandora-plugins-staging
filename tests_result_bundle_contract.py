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


def test_shared_fallback_is_bounded_and_snapshot_bound():
    text = FACTOR + STRATEGY
    assert "10 MiB" in text or "10 * 1024 * 1024" in text
    assert "40" in text
    assert "snapshot_revision" in text
