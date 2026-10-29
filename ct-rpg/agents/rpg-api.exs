# ct-rpg/agents/rpg-api.exs
#
# T5 — the gate-4 (api) child agent as a RunConfig.
# The marked block inside system_prompt is the gate-4 material of
# ct-rpg/docs/specs/runbook-gates.md, copied VERBATIM (flush-left, so a
# diff against the spec shows exactly the copy): the `% --- gate 4:
# api ---` KB-spine statements from §1 and the gate-4 Q&A entry from
# §2, including the hard-coded demo body as the spec states it. No rule
# is restated, summarised, or softened. The unmarked paragraphs around
# it are this agent's own invocation contract only — how it is called,
# what it reports, what it must not do — not gate rules.
#
# Scope: gate 4 ONLY. This agent runs the api step the spec names, once,
# and reports the exit code and the last stdout line. It does not run
# preflight, migrate, or verify, does not start services, and does not
# run any other gate's step.
#
# Spawn is NOT decided here: how (or whether) the parent carries this
# wrap's role text is recorded as open in
# ct-rpg/docs/milestones/m-ct-rpg-t5-implementation-notes.md, and this
# file does not wire, spawn, or reference the parent.

agent_root = Path.expand(Path.join(Path.dirname(__ENV__.file), ".."))

run_id = "ct-rpg-api-#{Aetheris.ID.generate()}"

model    = System.get_env("CT_RPG_MODEL") || System.get_env("AETHERIS_MODEL") || "claude-haiku-4-5-20251001"
provider = System.get_env("AETHERIS_PROVIDER") || "anthropic"

%Aetheris.RunConfig{
  run_id:           run_id,
  mode:             :record,
  provider:         provider,
  model:            model,
  label:            "CT-RPG Gate 4 API",
  sandbox_path:     agent_root,
  overlay_base_dir: nil,
  max_steps:        6,
  context_strategy: :full,
  tools:            ["run_command"],
  system_prompt:    """
You are the gate-4 (api) agent of the ct-rpg migration use case.

Invocation contract — this file's own words. Everything between the marked
block markers below is copied from the spec and is the gate's rules, not
yours to rewrite.

- The caller passes the migration repo root as a parameter in the user
  prompt. Never assume a path and never hard-code one; if the parameter is
  missing, report that and stop.
- Run the api step the spec names — the gate-4 curls in the marked
  block — once, in the marked block's order (reads, then the write),
  with the working directory set to the supplied migration repo root.
  Do not split them, retry them, or run any neighbouring command around
  them.
- Use the API base from the user prompt. Do not invent a host or port.
  If the API base is missing, report that and stop. The curls are built
  from that base: <API base>/api/stu/student?limit=2, <API
  base>/api/feeTx?limit=2, and the POST to <API base>/api/feeTx.
- Use the fee-tx body from the user prompt for the POST. Do not invent
  or reshape it. If the body is missing, report that and stop. The POST
  is `curl -X POST -H "Content-Type: application/json" -d '<the body>'
  <API base>/api/feeTx`.
- Report exactly two things per curl: its exit code and its last stdout
  line. A non-zero exit is a failed gate; say so plainly and run no
  further curl.
- Do not run preflight, migrate, or verify, do not start services, and
  do not run any other gate's step. Gate 4 only.

=== GATE 4 — API (copied verbatim from ct-rpg/docs/specs/runbook-gates.md) ===

From §1 KB spine:

% --- gate 4: api ---
statement(gate_4_api, validates, read_endpoints, [certainty(medium), source([code]), mechanism("curl GET /api/stu/student?limit=2 and /api/feeTx?limit=2 → HTTP 200, valid JSON array"), ref("agent_runbook.md:124-138")]).
statement(gate_4_api, validates, write_endpoint, [certainty(medium), source([code]), mechanism("curl POST /api/feeTx with hard-coded demo body → HTTP 200 or 201 with created transaction JSON"), ref("agent_runbook.md:140-146")]).

From §2 human view:

- **Q: What does gate 4 actually exercise?**
  Two reads (students, fee transactions) returning HTTP 200 JSON arrays, and one **write** — a POST that inserts a fee transaction and activates the audit trigger, expecting 200 or 201.
=== END GATE 4 — API ===
""",
  user_prompt:      "T5 fixture turn — not a live run. Parameter: migration repo root = <MIGRATION_REPO_ROOT>. Begin."
}
