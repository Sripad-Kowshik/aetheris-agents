# ct-rpg/agents/rpg-main.exs
#
# The parent migration-gate agent as a RunConfig.
# The system_prompt below is the WIRE section only — this file's own words:
# the hop order, the stop-on-first-failure rule, the services readiness
# check, the task_prompt recipe, and the four child role-text blocks. The
# extracted spec (ct-rpg/docs/specs/runbook-gates.md) does NOT travel in
# the prompt: each child carries only the gate section it needs (extracted
# at eval time below, from the child's own file), and the spec stays in
# docs/specs. No gate rule, KB statement, human-view text, or open item is
# copied into this prompt outside the role blocks.
#
# History:
# T1 — the parent as a RunConfig; its system_prompt then carried the spec
#      body verbatim plus a wire description.
# T6 — the wire became real: four hops one at a time; the child role texts
#      extracted at eval time from the children's files.
# T7 follow-ups — the role texts grew to contract + marked section;
#      CT_RPG_SANDBOX_PATH; run_command on the parent; per-hop tools and
#      max_steps: 6; CT_RPG_API_BASE and CT_RPG_FEE_TX_BODY for hop 4; the
#      services readiness check between hop 1 and hop 2.
# T-follow-up (this change) — the spec body is deleted from the prompt: it
#      starts at the WIRE heading. The gate rules live in the children and
#      in the spec; the parent carries only the wire.

agent_root = Path.expand(Path.join(Path.dirname(__ENV__.file), ".."))

run_id = "ct-rpg-main-#{Aetheris.ID.generate()}"

model    = System.get_env("CT_RPG_MODEL") || System.get_env("AETHERIS_MODEL") || "claude-haiku-4-5-20251001"
provider = System.get_env("AETHERIS_PROVIDER") || "anthropic"

# T6, extended by the T7 follow-up: the four child role texts, read at eval
# time from each child's own file (the at1cmd skill-hint pattern, as in
# ct-bot's T7 wire). Each role text is the child's own system_prompt — its
# invocation contract (the paragraphs before the marked block: run the named
# command once; emit a plain-text reply as the run's final event) FOLLOWED
# by its marked gate section — up to and including the end-marker line.
# Fail fast at eval time if a wrap is missing or its heredoc unterminated.
# The parent does not restate the gate rules or the contracts — the blocks
# embedded in the wire below ARE the children's own system prompts.
gate_role = fn root, file ->
  path = Path.join([root, "agents", file])
  text = if File.exists?(path), do: File.read!(path), else: raise("missing ct-rpg child wrap: #{path}")

  case String.split(text, "system_prompt:    \"\"\"", parts: 2) do
    [_before, after_prompt] ->
      case String.split(after_prompt, "\n\"\"\"", parts: 2) do
        [role, _after] -> String.trim(role)
        _ -> raise("unterminated system_prompt heredoc in #{path}")
      end

    _ ->
      raise("system_prompt heredoc not found in #{path}")
  end
end

preflight_role = gate_role.(agent_root, "rpg-preflight.exs")
migrate_role   = gate_role.(agent_root, "rpg-migrate.exs")
verify_role    = gate_role.(agent_root, "rpg-verify.exs")
api_role       = gate_role.(agent_root, "rpg-api.exs")

# T7 follow-up: the sandbox is caller-supplied when the variable is set and
# non-empty; the file-derived root remains the fallback. The children are
# still read from the file-derived root above — only the run's sandbox_path
# moves.
sandbox_path =
  case System.get_env("CT_RPG_SANDBOX_PATH") do
    nil -> agent_root
    "" -> agent_root
    path -> path
  end

# T7 follow-up: hop 4's API base — caller-supplied at eval time, never
# hard-coded (API_PORT is configurable and the deployed host is not
# localhost). Unset is legal: the file still evaluates, and the wire
# reports the missing value and runs no hop 4. Hops 1-3 never receive it.
api_base =
  case System.get_env("CT_RPG_API_BASE") do
    nil -> "<MISSING — CT_RPG_API_BASE is not set; hop 4 cannot run>"
    "" -> "<MISSING — CT_RPG_API_BASE is not set; hop 4 cannot run>"
    base -> base
  end

# T7 follow-up: hop 4's demo fee-tx body — caller-supplied at eval time,
# never hard-coded and never rebuilt from the GET response (the API
# expects status as a string; reshaping the read response into the write
# body is what produced the 400). Unset is legal: the file still
# evaluates, and the wire reports the missing value and runs no hop 4.
# Hops 1-3 never receive it.
fee_tx_body =
  case System.get_env("CT_RPG_FEE_TX_BODY") do
    nil -> "<MISSING — CT_RPG_FEE_TX_BODY is not set; hop 4 cannot run>"
    "" -> "<MISSING — CT_RPG_FEE_TX_BODY is not set; hop 4 cannot run>"
    body -> body
  end

%Aetheris.RunConfig{
  run_id:           run_id,
  mode:             :record,
  provider:         provider,
  model:            model,
  label:            "CT-RPG Migration Gate Orchestrator",
  sandbox_path:     sandbox_path,
  overlay_base_dir: nil,
  max_steps:        12,
  context_strategy: :full,
  tools:            ["spawn_agent", "wait_for_all", "run_command"],
  system_prompt:    """
================================================================================
WIRE — the gate chain (this file's own words; NOT part of the spec)
================================================================================

The document above is the gate contract: the rules, not yours to rewrite. On
the turn below you run the gate chain through child agents.

Four hops, ONE at a time, in this exact order:

  hop 1 — gate 0 preflight
  readiness check — services, not a hop (the parent runs it itself)
  hop 2 — gate 2 migrate
  hop 3 — gate 3 verify (parity)
  hop 4 — gate 4 api

Spawn a hop, wait for it, read its result, then spawn the next. Never spawn
in parallel; never spawn the next hop until the previous one has finished.

Harness mechanics (not choices):
- spawn_agent arguments are task_prompt, tools, max_steps, timeout_ms —
  there is no payload field. task_prompt becomes the child's system_prompt;
  put the child's role body AND its parameter in task_prompt.
- Each hop is spawned with tools: ["run_command"].
- Each hop is spawned with max_steps: 6.
- spawn_agent does not load the standalone wraps in ct-rpg/agents/ — the
  role bodies travel inside this prompt and are copied into each
  task_prompt from the marked blocks below (the ct-bot T7 finding).
- wait_for_all returns one map per run: run_id, status, final_message,
  steps. final_message is the channel — the hop's last text. Wait after
  each spawn with run_ids = [that hop's run_id] and timeout_ms: 120000,
  passed explicitly.
- A hop whose wait reports a TERMINAL status (for example "done") is
  finished: read final_message and continue the chain — a finished hop is
  never reported as timed out.
- A hop whose wait reports a NON-TERMINAL status is a FAILED CHAIN: report
  which hop failed and that the rest did not run, and stop. Do not retry.
  Do not spawn the next hop.

A failed hop stops the chain — the spec's own stop-on-first-failure rule,
applied to the spawn order. After each wait, read final_message: if the
hop reports its gate FAILED — a non-zero exit code, a [FAIL] / error
line, or an explicit failure report — report which hop failed and that
the remaining hops did not run, and stop. Do not retry. Do not spawn the
rest.

Readiness check — between hop 1 and hop 2 only, before hop 2 is spawned
(not a hop, not a gate; the parent runs it itself with run_command):

- The command, exactly once: `curl #{api_base}/health` — <API base> is
  the same value the hop-4 parameter carries.
- The check passes only when the exit code is 0 AND the response
  contains "Healthy".
- On any other exit code or response, report that services are not
  ready and stop the chain — spawn no further hop. Do not start
  services, do not retry, and do not call wait-for-api.sh.
- If the API base reads as MISSING, readiness cannot be confirmed:
  report that and stop before hop 2.

Each hop's task_prompt is exactly two things — that child's role text and
the parameter. You do not restate the gate rules or the invocation
contract; you only hand the child its role and the parameter:

- The role text: the correspondingly named block below, copied VERBATIM
  and whole. Each block is that child's own system_prompt, extracted at
  eval time from the child's file — its invocation contract (run the
  named command once; emit a plain-text reply as the run's final event)
  followed by its marked gate section. Edit nothing, drop nothing, add
  nothing of yours.
- The parameter, exactly as the child already expects it. Never invent,
  substitute, or hard-code a path or a port:
  - Hops 1-3: one line — "Migration repo root: <the value from the user
    prompt>". If the user prompt carries no value, report that and run
    no hop.
  - Hop 4 only: three lines —
      Migration repo root: <the value from the user prompt>
      API base: #{api_base}
      Fee-tx body: #{fee_tx_body}
    The API base and the fee-tx body are the values CT_RPG_API_BASE and
    CT_RPG_FEE_TX_BODY carried in the parent's environment at eval time —
    they are not in the user prompt and are never invented, reshaped, or
    rebuilt from the GET response. No other hop receives the API base or
    the fee-tx body. If either the API base line or the fee-tx body line
    above reads as MISSING, report that hop 4 cannot run and do not run
    it; hops 1-3 still run.

  hop 1 (preflight) → the PREFLIGHT ROLE TEXT block below
  hop 2 (migrate)   → the MIGRATE ROLE TEXT block below
  hop 3 (verify)    → the VERIFY ROLE TEXT block below
  hop 4 (api)       → the API ROLE TEXT block below

The chain is exactly these four hops — gates 1 (services) and 5 (tests)
have no child in this milestone's ticket list and are not hops.

=== PREFLIGHT ROLE TEXT (the child's own system_prompt — invocation contract + marked gate section — extracted at eval time from ct-rpg/agents/rpg-preflight.exs) ===
#{preflight_role}
=== END PREFLIGHT ROLE TEXT ===

=== MIGRATE ROLE TEXT (the child's own system_prompt — invocation contract + marked gate section — extracted at eval time from ct-rpg/agents/rpg-migrate.exs) ===
#{migrate_role}
=== END MIGRATE ROLE TEXT ===

=== VERIFY ROLE TEXT (the child's own system_prompt — invocation contract + marked gate section — extracted at eval time from ct-rpg/agents/rpg-verify.exs) ===
#{verify_role}
=== END VERIFY ROLE TEXT ===

=== API ROLE TEXT (the child's own system_prompt — invocation contract + marked gate section — extracted at eval time from ct-rpg/agents/rpg-api.exs) ===
#{api_role}
=== END API ROLE TEXT ===
""",
  user_prompt:      "T6 fixture turn — not a live run. Parameter: migration repo root = <MIGRATION_REPO_ROOT>. Begin."
}
