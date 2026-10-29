# ct-rpg/agents/rpg-preflight.exs
#
# T1 — the gate-0 (preflight) child agent as a RunConfig.
# T-follow-up: the marked gate section is DELETED from the prompt — the KB
# statements and the human-view Q&A were residual spec and did not change
# what this agent runs or how it reports. The prompt is the invocation
# contract only; the gate's rules live in ct-rpg/docs/specs/
# runbook-gates.md (§preflight), not here. Nothing is restated.
#
# Scope: gate 0 ONLY. This agent runs the preflight script once and reports
# the exit code and the last stdout line. It does not start services, does
# not migrate, does not verify parity, and does not call the API — gates 1–5
# belong to other children.

agent_root = Path.expand(Path.join(Path.dirname(__ENV__.file), ".."))

run_id = "ct-rpg-preflight-#{Aetheris.ID.generate()}"

model    = System.get_env("CT_RPG_MODEL") || System.get_env("AETHERIS_MODEL") || "claude-haiku-4-5-20251001"
provider = System.get_env("AETHERIS_PROVIDER") || "anthropic"

%Aetheris.RunConfig{
  run_id:           run_id,
  mode:             :record,
  provider:         provider,
  model:            model,
  label:            "CT-RPG Gate 0 Preflight",
  sandbox_path:     agent_root,
  overlay_base_dir: nil,
  max_steps:        4,
  context_strategy: :full,
  tools:            ["run_command"],
  system_prompt:    """
You are the gate-0 (preflight) agent of the ct-rpg migration use case.

Invocation contract — this file's own words, and the whole prompt. The
gate's rules live in ct-rpg/docs/specs/runbook-gates.md; this prompt
carries only the contract below.

- The caller passes the migration repo root as a parameter in the user
  prompt. Never assume a path and never hard-code one; if the parameter is
  missing, report that and stop.
- Run `bash scripts/verify-prerequisites.sh` exactly once, with the working
  directory set to the supplied migration repo root.
- When the command returns, emit ONE plain-text reply as the run's final
  event — a tool call must not be the last event, or the run records no
  outcome. The reply states the gate outcome from the run's own output,
  never invented: quote the script's `[PREFLIGHT PASS]` line on success or
  its `[FAIL]` line on failure, plus the exit code, in the shape
  "<quoted line> — exit code <code>: gate 0 (preflight) <passed/failed>".
  If the expected marker is absent from the output, say so and quote the
  last line that did appear instead of fabricating it.
- A non-zero exit code is a failed gate; say so plainly in that reply.
- Do not run any other command and no other gate's step. Gate 0 only.
""",
  user_prompt:      "T1 fixture turn — not a live run. Parameter: migration repo root = <MIGRATION_REPO_ROOT>. Begin."
}
