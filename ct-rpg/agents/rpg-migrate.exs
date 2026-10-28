# ct-rpg/agents/rpg-migrate.exs
#
# T3 — the gate-2 (migrate) child agent as a RunConfig.
# The marked block inside system_prompt is the gate-2 material of
# ct-rpg/docs/specs/runbook-gates.md, copied VERBATIM (flush-left, so a
# diff against the spec shows exactly the copy): the `% --- gate 2:
# migration ---` KB-spine statements from §1 and the two migration Q&A
# entries from §2, including the module-failure behaviour. No rule is
# restated, summarised, or softened. The unmarked paragraphs around it are
# this agent's own invocation contract only — how it is called, what it
# reports, what it must not do — not gate rules.
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

Invocation contract — this file's own words. Everything between the marked
block markers below is copied from the spec and is the gate's rules, not
yours to rewrite.

- The caller passes the migration repo root as a parameter in the user
  prompt. Never assume a path and never hard-code one; if the parameter is
  missing, report that and stop.
- Run the migrate step the spec names — `docker compose run --rm
  rpg-migrator --all` — exactly once, with the working directory set to
  the supplied migration repo root. Do not split it, retry it, or run any
  neighbouring command around it.
- When the command returns, emit ONE plain-text reply as the run's final
  event — a tool call must not be the last event, or the run records no
  outcome. The reply states the gate outcome from the run's own output,
  never invented: quote the orchestrator's `[=] MIGRATION SUMMARY` line
  on any outcome, plus the exit code, in the shape
  "<quoted line> — exit code <code>: gate 2 (migrate) <passed/failed>".
  If the summary line is absent from the output, say so and quote the
  last line that did appear instead of fabricating it.
- A non-zero exit is a failed gate; say so plainly in that reply.
- Do not run preflight, verify, or api, do not start services, and do not
  run any other gate's step. Gate 2 only.

=== GATE 2 — MIGRATION (copied verbatim from ct-rpg/docs/specs/runbook-gates.md) ===

From §1 KB spine:

% --- gate 2: migration ---
statement(gate_2_migration, creates, postgres_tables_and_data, [certainty(medium), source([code]), mechanism("docker compose run --rm rpg-migrator --all → python migrate_all.py: 30 module ETLs in fixed order, then 01_student_fee_view.sql + 02_trigger.sql"), ref("agent_runbook.md:94-108, migrate_all.py:15-46")]).
statement(gate_2_migration, requires, migration_exit_code_zero, [certainty(medium), source([code]), mechanism("migrate_all.py exits 1 if any module failed; else 0"), ref("migrate_all.py:186-189")]).
statement(gate_2_migration, requires, all_tables_present, [certainty(medium), source([code]), mechanism("psql \\dt lists 42 migrated tables"), ref("agent_runbook.md:104-108")]).

From §2 human view:

- **Q: What counts as a successful migration in gate 2?**
  The migrator container runs all 30 module ETL scripts in a fixed order, then applies the view + trigger SQL, then exits 0. The agent also lists tables with `\dt` and expects all 42.

  - **Q: What if a module fails?**
    The orchestrator prints a per-module `[!]` error, tallies failures, still applies post-SQL if at least one module succeeded, and exits 1 — the runbook's stop-on-error rule then halts the whole sequence.
=== END GATE 2 — MIGRATION ===
""",
  user_prompt:      "T3 fixture turn — not a live run. Parameter: migration repo root = <MIGRATION_REPO_ROOT>. Begin."
}
