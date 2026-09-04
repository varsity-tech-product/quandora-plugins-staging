# Deferred Plugin Audit Blockers

Recorded from the strict audit on 2026-09-04. These items are outside the current Skill-boundary
cleanup and do not change product workflow behavior.

1. **Public contract convergence** — Auth `origin/main` (`2374742`) and Product Backend
   `origin/main` (`83a3a69`) publish the same 71 tool names but different generated contract
   revisions and hashes. Seven input schemas and all output schemas differ. Regenerate and verify
   the shared contract in the owning repositories before release certification.
2. **Plugin package-policy convergence** — the strict auditor reports `QD-PACKAGE-001` because
   `plugins/quandora-staging/scripts` exists, while the repository validator intentionally allows
   exactly the two reviewed Claude OAuth launchers. Align the central audit policy, waiver, or
   package layout after the staging-plugin repair.
3. **Observed host acceptance evidence** — the 13-case Agent evaluation contract currently has a
   reviewed reference-policy baseline, but no fresh observed Codex and Claude host runs for this
   package state. Capture both before treating the package as fully release-certified.
