# Behavior Evaluations

Use behavior evaluations to test decisions that static files cannot prove: Skill activation,
cross-Skill routing, tool selection, confirmation, recovery, stopping behavior, and final output.

## Case Inventory

For every changed Skill include, where applicable:

1. a direct request that should activate it;
2. an indirect request with the same user goal;
3. an incomplete request that requires clarification or bounded discovery;
4. a near-neighbor request that must route to another Skill;
5. an unsupported request that must not activate or call a tool;
6. a follow-up that reuses an exact returned identifier;
7. a write request that must display and confirm the exact mutation;
8. a lost-response or ambiguous outcome that must not create a second command.

## Safe Execution Environments

- Use a local recording/fake MCP server for mutation, timeout, ambiguous-response, and destructive
  cases. It must expose the current public schemas but perform no business action.
- Use live staging only for bounded read cases unless the user explicitly authorizes a disposable
  mutation and its cost/cleanup boundary.
- Start every case in a fresh Host conversation with the exact packaged Skill revision under test.
- Test both Codex and Claude and every model family intended for release. A pass on one Host or one
  model is not portable evidence.

## Observation Record

Record at minimum:

- case ID and exact prompt;
- Host product/version and model identifier;
- plugin/Skill git SHA and public-contract digest;
- start time and isolated run identifier;
- ordered tool names and redacted argument shapes;
- confirmation/clarification events;
- terminal response status and a SHA-256 digest of the redacted transcript;
- reviewer judgments for semantic facts that cannot be derived from the tool trace.

Never record credentials, authorization material, opaque pagination tokens, download URLs, or live
business identifiers. Store a redacted transcript outside the installable plugin package.

## Evidence Classes

- `reference_oracle`: hand-reviewed expected tools and facts. It defines acceptance but proves no
  Host behavior.
- `observed_host_run`: output from a real Codex or Claude process using the packaged Skill and a
  recording MCP boundary.
- `live_staging_read`: observed Host run against deployed staging, limited to authorized reads.

Only the latter two may close Host acceptance. Keep the reference oracle in CI so contract drift is
detected even when model execution is not available.

## Review

The automated checker should validate trace ordering, forbidden calls, maximum call counts,
contract digests, Host metadata, and evidence class. A human reviewer should judge ambiguous final
language, whether confirmation was genuinely obtained, and whether the answer exposed or inferred
unsupported facts. Preserve the distinction in the result file.
