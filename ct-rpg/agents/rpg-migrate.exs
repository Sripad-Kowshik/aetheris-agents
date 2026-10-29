# ct-rpg/agents/rpg-migrate.exs
#
# T3 — the gate-2 (migrate) child agent as a RunConfig.
# T-follow-up: the marked gate section is DELETED from the prompt — the KB
# statements and the human-view Q&A were residual spec and did not change
# what this agent runs or how it reports. The prompt is the invocation
# contract only; the gate's rules live in ct-rpg/docs/specs/
# runbook-gates.md (§migrate), not here. Nothing is restated.
#
# Scope: gate 2 ONLY. This agent runs the migrate step the spec names,
# once, and reports the exit code and the last stdout line. It does not
# run preflight, verify, or api, does not start services, and does not
# run any other gate's step.
#
# Spawn is NOT decided here: how (or whether) the parent carries this
# wrap's role text is recorded as open in
# ct-rpg/docs/milestones/m-ct-rpg-t3-implementation-notes.md, and this
# file does not wire, spawn, or reference the parent.

agent_root = Path.expand(Path.join(Path.dirname(__ENV__.file), ".."))

run_id = "ct-rpg-migrate-#{Aetheris.ID.generate()}"

model    = System.get_env("CT_RPG_MODEL") || System.get_env("AETHERIS_MODEL") || "claude-haiku-4-5-20251001"
provider = System.get_env("AETHERIS_PROVIDER") || "anthropic"

%Aetheris.RunConfig{
  run_id:           run_id,
  mode:             :record,
  provider:         provider,
  model:            model,
  label:            "CT-RPG Gate 2 Migrate",
  sandbox_path:     agent_root,
  overlay_base_dir: nil,
  max_steps:        4,
  context_strategy: :full,
  tools:            ["run_command"],
  system_prompt:    """
You are the gate-2 (migrate) agent of the ct-rpg migration use case.

Invocation contract — this file's own words, and the whole prompt. The
gate's rules live in ct-rpg/docs/specs/runbook-gates.md; this prompt
carries only the contract below.

- The caller passes the migration repo root as a parameter in the user
  prompt. Never assume a path and never hard-code one; if the parameter is
  missing, report that and stop.
- Run the migrate step the spec names — `set -o pipefail; docker compose
  run --rm rpg-migrator --all | tail -n 80` — exactly once, with the
  working directory set to the supplied migration repo root. Do not
  split it, retry it, or run any neighbouring command around it. The
  pipe keeps only the tail: the tool result is long, the harness
  truncates it before the end, and the summary line lives at the end.
  The pipefail keeps the exit code the migrator's — without it the exit
  code would be tail's, and a failed migrator would look like exit 0.
- Pass timeout_ms: 300000 on that run_command. Do not pass a shorter
  value.
- When the command returns, emit ONE plain-text reply as the run's final
  event — a tool call must not be the last event, or the run records no
  outcome. The reply states the gate outcome from the run's own output,
  never invented: quote the orchestrator's `[=] MIGRATION SUMMARY` line
  when it is visible in the tailed output; if it is still absent, quote
  the last visible line and report the exit code, in the shape
  "<quoted line> — exit code <code>: gate 2 (migrate) <passed/failed>".
  Do not invent the line.
- A non-zero exit is a failed gate; say so plainly in that reply.
- Do not run preflight, verify, or api, do not start services, and do not
  run any other gate's step. Gate 2 only.
""",
  user_prompt:      "T3 fixture turn — not a live run. Parameter: migration repo root = <MIGRATION_REPO_ROOT>. Begin."
}
