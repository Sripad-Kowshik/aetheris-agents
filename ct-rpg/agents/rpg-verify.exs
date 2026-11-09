# ct-rpg/agents/rpg-verify.exs
#
# T4 — the gate-3 (verify) child agent as a RunConfig.
# T-follow-up: the marked gate section is DELETED from the prompt — the KB
# statements and the human-view Q&A were residual spec and did not change
# what this agent runs or how it reports. The prompt is the invocation
# contract only; the gate's rules live in ct-rpg/docs/specs/
# runbook-gates.md (§verify), not here. Nothing is restated.
#
# Scope: gate 3 ONLY. This agent runs the verify step the spec names,
# once, and reports the exit code and the last stdout line. It does not
# run preflight, migrate, or api, does not start services, and does not
# run any other gate's step.
#
# Spawn is NOT decided here: how (or whether) the parent carries this
# wrap's role text is recorded as open in
# ct-rpg/docs/milestones/m-ct-rpg-t4-implementation-notes.md, and this
# file does not wire, spawn, or reference the parent.

agent_root = Path.expand(Path.join(Path.dirname(__ENV__.file), ".."))

run_id = "ct-rpg-verify-#{Aetheris.ID.generate()}"

model    = System.get_env("CT_RPG_MODEL") || System.get_env("AETHERIS_MODEL") || "claude-haiku-4-5-20251001"
provider = System.get_env("AETHERIS_PROVIDER") || "anthropic"

%Aetheris.RunConfig{
  run_id:           run_id,
  mode:             :record,
  provider:         provider,
  model:            model,
  label:            "CT-RPG Gate 3 Verify",
  sandbox_path:     agent_root,
  overlay_base_dir: nil,
  max_steps:        4,
  context_strategy: :full,
  tools:            ["run_command"],
  system_prompt:    """
You are the gate-3 (verify) agent of the ct-rpg migration use case.

Invocation contract — this file's own words, and the whole prompt. The
gate's rules live in ct-rpg/docs/specs/runbook-gates.md; this prompt
carries only the contract below.

- The caller passes the migration repo root as a parameter in the user
  prompt. Never assume a path and never hard-code one; if the parameter is
  missing, report that and stop.
- Run the verify step the spec names — `docker compose run --rm
  --entrypoint python rpg-migrator verify_raven_to_postgres.py` — exactly
  once, with the working directory set to the supplied migration repo
  root. Do not split it, retry it, or run any neighbouring command around
  it.
- When the command returns, emit ONE plain-text reply as the run's final
  event — a tool call must not be the last event, or the run records no
  outcome. The reply states the gate outcome from the run's own output,
  never invented: quote the verifier's `[SUCCESS]` line on success or its
  FAIL line on failure, plus the exit code, in the shape
  "<quoted line> — exit code <code>: gate 3 (verify) <passed/failed>".
  If neither line appears in the output, say so and quote the last line
  that did appear instead of fabricating it.
- A non-zero exit is a failed gate; say so plainly in that reply.
- Do not run preflight, migrate, or api, do not start services, and do
  not run any other gate's step. Gate 3 only.
""",
  user_prompt:      "T4 fixture turn — not a live run. Parameter: migration repo root = <MIGRATION_REPO_ROOT>. Begin."
}
