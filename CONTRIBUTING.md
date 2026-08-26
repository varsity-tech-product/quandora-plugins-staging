# Contributing

Before requesting review for a staging Plugin change, run the database-free package check:

```bash
python3 scripts/check-staging-plugin.py
```

The check verifies the declared Quandora Staging version across supported host manifests, required
Skill metadata, the bounded Codex staging entry examples, and portable Agent-facing instructions.
It permits additional Skills and explicit version-diagnostic guidance; it rejects mandatory
version probes in normal Skill entry paths.
