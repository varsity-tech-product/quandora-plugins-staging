# Contributing

Before requesting review for a staging Plugin change, run the database-free package check:

```bash
python3 scripts/check-staging-plugin.py
```

The check verifies the declared Quandora Staging version across supported host manifests, the
public package allowlist, required Skill metadata and assets, bounded Codex entry examples,
portable Agent-facing instructions, explicit routing boundaries, user-language output policy, and
search/pagination guidance. It also rejects orphaned Skill scripts, release-process history in
runtime documentation, per-Skill bundled-version copy, retired tool names, and mandatory version
probes in normal entry paths.

The check is database-free and must remain suitable for pull-request CI.
