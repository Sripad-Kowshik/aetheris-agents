# ct-rpg/agents/rpg-main.exs
#
# T1 — the parent migration-gate agent as a RunConfig.
# The system_prompt below is the body of ct-rpg/docs/specs/runbook-gates.md,
# copied verbatim (flush-left, so a diff against the source file shows exactly
# the wrap), including the file's own title line. There are NO retargets: the
# spec's legacy-repo references (agent_runbook.md, verify-prerequisites.sh,
# references/campustrack.md, specs/golden/) are the spec's own citations and
# stay verbatim. Every rule is kept; nothing is restated, summarised, or
# softened.
#
# T6 — the wire. The WIRE section after the copy is this file's own words:
# four hops in order — gate 0 preflight, then gate 2 migrate, then gate 3
# verify (parity), then gate 4 api — ONE at a time: spawn a hop, wait for it,
# read its final_message, then spawn the next. A hop whose wait reports a
# non-terminal status is a failed chain: report which hop failed and stop; do
# not retry and do not spawn the rest. A hop that finishes and reports its
# gate FAILED does the same. Each hop's task_prompt carries exactly two
# things — that child's role text (the child's own system_prompt — its
# invocation contract followed by its marked gate section — extracted at
# eval time below, fail-fast if a wrap is missing) and the migration repo
# root parameter, passed through exactly as the user prompt carried it. The
# parent does not restate the gate rules; it only hands the child its role
# and the parameter. This decision discharges the "spawn not decided" note
# carried by T3, T4, and T5.
#
# T7 follow-up — the live chain run (ct-rpg-main-NEufxg) returned
# final_message nil on every hop: the spawned children received only the
# marked gate section, so the invocation contract — run the named command
# once, emit a plain-text reply as the run's final event — never reached
# them; they explored with tool calls, hit max_steps, and ended on a tool
# call. The role text extracted below is therefore the child's WHOLE
# system_prompt (contract + marked section), read from the child's file at
# eval time the same way the marked section was — nothing hard-coded here.

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
# migration · runbook-gates — extracted spec (v0.1)

> **Status:** extraction from legacy runbook artifacts · **Confidence ceiling reached:** medium (no SME sign-off; no golden captured against a live legacy environment)
> **Legacy provenance:** `agent_runbook.md` (YAML frontmatter + steps 0–6), `agent_runbook_guide.md` (agent-runner launch contract), backed by the gate scripts they invoke: `scripts/verify-prerequisites.sh`, `scripts/migrate_all.py`, `scripts/verify_raven_to_postgres.py`, `scripts/wait-for-api.sh`, `docker-compose.yml`
> **Layers below:** (1) KB spine · (2) human view · (3) golden refs · (4) open items
>
> Note: the stack adapter (`references/campustrack.md`) targets the CampusTrack .NET/RavenDB
> codebase; for this migration-repo operation the source-priority collapses to **code** —
> the runbook YAML *is* the operation contract, and the scripts it gates on are the
> realisation. No Raven indexes, job contracts, or assertion-bearing tests apply here.

---

## 1. KB spine

```kb
% --- entities ---
statement(runbook_gates, is_a, gated_execution_contract, [certainty(medium), source([code]), mechanism("YAML frontmatter with step/gate list at top of agent_runbook.md"), ref("agent_runbook.md:1-38")]).
statement(runbook_gates, has_attribute, version, [type(string), has_value_set(["2.1.0"]), certainty(medium), source([code]), ref("agent_runbook.md:3")]).
statement(runbook_gates, has_attribute, execution_mode, [type(enum), has_value_set(["docker-canonical"]), certainty(medium), source([code]), ref("agent_runbook.md:4")]).
statement(runbook_gates, has_attribute, stop_on_error, [type(bool), has_value_set([true]), certainty(medium), source([code]), ref("agent_runbook.md:6")]).

% --- agent execution rules (apply to every gate) ---
statement(runbook_gates, requires, non_interactive_execution, [certainty(medium), source([code]), ref("agent_runbook.md:48")]).
statement(runbook_gates, requires, stop_and_report_on_first_failure, [certainty(medium), source([code]), ref("agent_runbook.md:50")]).
statement(runbook_gates, requires, secrets_never_committed_or_echoed, [certainty(medium), source([code]), ref("agent_runbook.md:50-52")]).
statement(runbook_gates, requires, all_execution_inside_docker_containers, [certainty(medium), source([code]), note("no local Python, psql, or .NET on host"), ref("agent_runbook.md:52")]).
statement(runbook_gates, requires, repo_root_as_working_directory, [certainty(medium), source([code]), ref("agent_runbook.md:42")]).

% --- gate 0: preflight ---
statement(gate_0_preflight, validates, toolchain_present, [certainty(medium), source([code]), mechanism("bash scripts/verify-prerequisites.sh; checks git, docker, curl, docker daemon, compose v2"), on_invalid(error("[PREFLIGHT FAIL] ... exit 1")), ref("verify-prerequisites.sh:26-65")]).
statement(gate_0_preflight, validates, env_configured, [certainty(medium), source([code]), mechanism(".env exists and 8 required vars (PG_PORT, PG_DB, PG_USER, PG_PASSWORD, RAVEN_URL, RAVEN_DB, RAVEN_CERT_FILE, API_PORT) are set and non-placeholder"), on_invalid(error("fail per missing var")), ref("verify-prerequisites.sh:70-98")]).
statement(gate_0_preflight, validates, raven_certificate_present, [certainty(medium), source([code]), mechanism("cert file found at scripts/<RAVEN_CERT_FILE> or <RAVEN_CERT_FILE>"), on_invalid(error("[FAIL] certificate not found")), ref("verify-prerequisites.sh:100-120")]).
statement(gate_0_preflight, validates, no_secrets_tracked_by_git, [certainty(medium), source([code]), mechanism("git ls-files .env *.pfx scripts/certs/*"), on_invalid(error("[FAIL] Secret files are tracked by Git")), ref("verify-prerequisites.sh:132-141")]).
statement(gate_0_preflight, creates, preflight_pass_marker, [certainty(medium), source([code]), mechanism("stdout line '[PREFLIGHT PASS] All checks passed (N warnings).' + exit 0"), ref("verify-prerequisites.sh:146-156")]).

% --- gate 1: services ---
statement(gate_1_services, requires, postgres_ready, [certainty(medium), source([code]), mechanism("docker compose up -d --build rpg-api (pulls rpg-postgres via depends_on service_healthy); psql SELECT 1 returns 1, exit 0"), ref("agent_runbook.md:71-90")]).
statement(gate_1_services, requires, api_health_ok, [certainty(medium), source([code]), mechanism("curl http://localhost:5000/health returns HTTP 200 with {status:Healthy, database:Connected}"), ref("agent_runbook.md:86-90")]).

% --- gate 2: migration ---
statement(gate_2_migration, creates, postgres_tables_and_data, [certainty(medium), source([code]), mechanism("docker compose run --rm rpg-migrator --all → python migrate_all.py: 30 module ETLs in fixed order, then 01_student_fee_view.sql + 02_trigger.sql"), ref("agent_runbook.md:94-108, migrate_all.py:15-46")]).
statement(gate_2_migration, requires, migration_exit_code_zero, [certainty(medium), source([code]), mechanism("migrate_all.py exits 1 if any module failed; else 0"), ref("migrate_all.py:186-189")]).
statement(gate_2_migration, requires, all_tables_present, [certainty(medium), source([code]), mechanism("psql \\dt lists 42 migrated tables"), ref("agent_runbook.md:104-108")]).

% --- gate 3: parity ---
statement(gate_3_parity, validates, raven_postgres_parity, [certainty(medium), source([code]), mechanism("docker compose run --rm --entrypoint python rpg-migrator verify_raven_to_postgres.py; audits 42 collections, deep-audits 9 core domains"), ref("agent_runbook.md:110-122, verify_raven_to_postgres.py:1-11")]).
statement(gate_3_parity, requires, parity_report_pass, [certainty(medium), source([code]), mechanism("exit 0; stdout '[SUCCESS] 100% COMPLETE PARITY CONFIRMED ACROSS ALL 42 TABLES AND N RECORDS!'; JSON overall_status=PASS with 0 missing, 0 extra, 0 mismatches"), ref("verify_raven_to_postgres.py:1930-1937, 1909")]).
statement(gate_3_parity, creates, parity_report_artifact, [certainty(medium), source([code]), mechanism("writes validation/exhaustive-parity-report-<utc-timestamp>.json"), ref("verify_raven_to_postgres.py:1890-1930")]).

% --- gate 4: api ---
statement(gate_4_api, validates, read_endpoints, [certainty(medium), source([code]), mechanism("curl GET /api/stu/student?limit=2 and /api/feeTx?limit=2 → HTTP 200, valid JSON array"), ref("agent_runbook.md:124-138")]).
statement(gate_4_api, validates, write_endpoint, [certainty(medium), source([code]), mechanism("curl POST /api/feeTx with hard-coded demo body → HTTP 200 or 201 with created transaction JSON"), ref("agent_runbook.md:140-146")]).

% --- gate 5: tests ---
statement(gate_5_tests, validates, xunit_suite_passes, [certainty(medium), source([code]), mechanism("docker compose run --rm rpg-tests → dotnet test; exit 0, output 'Passed! - Failed: 0, Passed: X, Skipped: 0'"), ref("agent_runbook.md:148-158")]).

% --- teardown + summary contract ---
statement(gate_6_teardown, is_a, optional_step, [certainty(medium), source([code]), mechanism("docker compose down (keep data) or down -v (wipe volume)"), ref("agent_runbook.md:160-172")]).
statement(runbook_gates, creates, onboarding_summary_report, [certainty(medium), source([code]), mechanism("markdown block 'Onboarding Status: SUCCESS' with PASS per step 0-5 when all gates succeed"), ref("agent_runbook.md:176-188")]).

% --- dependencies ---
statement(runbook_gates, depends_on, env_and_certificate_configured, [certainty(medium), source([code]), note(".env from .env.example; .pfx placed in scripts/certs/"), ref("agent_runbook_guide.md:40-55")]).
statement(runbook_gates, depends_on, docker_running, [certainty(medium), source([code]), ref("agent_runbook_guide.md:9-28")]).

% --- divergences (route to product decision) ---
statement(s(runbook_gates, reports, ps1_preflight_variant), needs, product_decision,
          [certainty(unresolved), source([code]), contradicts(code),
           note("agent_runbook.md:64 and agent_runbook_guide.md:83 instruct '.\\scripts\\verify-prerequisites.ps1' as the PowerShell preflight, but no .ps1 file exists anywhere in the repo — the Windows path of gate 0 cannot execute as documented")]).
statement(s(gate_2_migration, reports, success_message), needs, product_decision,
          [certainty(unresolved), source([code]), contradicts(code),
           note("runbook gate-2 criterion expects 'All migrations and post-migration scripts completed successfully', but migrate_all.py only prints '[=] MIGRATION SUMMARY: X succeeded, Y failed' — the criterion string is never printed, so a literal string-match gate can never pass")]).
statement(s(gate_4_api, requires, hard_coded_demo_ids), needs, product_decision,
          [certainty(unresolved), source([code]),
           note("POST /api/feeTx body pins studentId cc93c106-82ea-4610-9873-3db87f1307c6 and feeId a7e2851c-2321-4adc-99a3-... from one specific dataset; against any other RavenDB source the write gate can fail despite a correct migration")]).
statement(s(gate_4_api, requires, hard_coded_port_5000), needs, product_decision,
          [certainty(unresolved), source([code]), contradicts(code),
           note("runbook curl commands hard-code localhost:5000 while API_PORT is configurable in .env (and wait-for-api.sh honours it); a non-default API_PORT silently breaks gate 4")]).

% --- low-confidence / doc contradictions ---
statement(s(gate_1_services, has_value_set, postgres_host_port_5433), needs, sme_input,
          [certainty(low), source([code]), contradicts(code),
           note("README.md:374-379 troubleshooting says PostgreSQL is bound to host port 5433, but compose/runbook/README-config all use PG_PORT=15432 — stale doc paragraph")]).
statement(s(runbook_gates, has_attribute, agent_runner), needs, sme_input,
          [certainty(low), source([code]),
           note("agent_runbook_guide.md assumes Google Antigravity ('agy' CLI/IDE) as the executing agent; the runbook itself is runner-agnostic YAML — which runner is canonical is unconfirmed")]).
statement(s(runbook_gates, depends_on, wait_for_api_script), needs, sme_input,
          [certainty(low), source([code]),
           note("scripts/wait-for-api.sh exists as a bounded readiness helper honouring API_PORT, but no gate step references it — its intended place in the sequence is an SME question")]).
statement(s(gate_3_parity, requires, entrypoint_override), needs, sme_input,
          [certainty(low), source([code]),
           note("gate-3 command relies on container WORKDIR /app/scripts (scripts/Dockerfile) for the bare filename verify_raven_to_postgres.py to resolve — fragile but currently correct")]).
```

---

## 2. Human view (SME reads this)

**Q: What do the runbook gates do?**
They define a strictly ordered, stop-on-first-failure sequence of six verification gates an agent must execute from the repo root to take the system from clean checkout to verified migration: preflight → start services → migrate data → audit parity → exercise the REST API → run the test suite. On full success the agent reports a structured "Onboarding Status: SUCCESS" summary with a PASS line per gate.

- **Q: What must be true before gate 0?**
  Docker Desktop running, `.env` created from `.env.example` with all credentials filled (no `<placeholder>` text left), and the RavenDB `.pfx` client certificate dropped into `scripts/certs/`.

  - **Q: What exactly does the preflight gate check?**
    Seven groups: `git`/`docker`/`curl` in PATH, Docker daemon reachable, Compose v2 available, `.env` present with 8 required variables non-placeholder, certificate file resolvable, `docker-compose.yml` present, and no secret files tracked by Git. Any failure prints `[FAIL] …` and exits 1.

    - **Q: What if the operator is on Windows PowerShell?**
      *[UNRESOLVED]* Both runbook docs say to run `.\scripts\verify-prerequisites.ps1`, but that file does not exist in the repository. The Windows preflight path is documented but unimplementable as written. → **product decision.**

- **Q: How does gate 1 know PostgreSQL and the API are ready?**
  `docker compose up -d --build rpg-api` starts PostgreSQL first (compose healthcheck) then the API. The agent then verifies `SELECT 1` returns 1 via psql-in-container and `curl /health` returns HTTP 200 with `{"status":"Healthy","database":"Connected"}`.

- **Q: What counts as a successful migration in gate 2?**
  The migrator container runs all 30 module ETL scripts in a fixed order, then applies the view + trigger SQL, then exits 0. The agent also lists tables with `\dt` and expects all 42.

  - **Q: What if a module fails?**
    The orchestrator prints a per-module `[!]` error, tallies failures, still applies post-SQL if at least one module succeeded, and exits 1 — the runbook's stop-on-error rule then halts the whole sequence.

- **Q: What does the parity gate (3) verify?**
  All 42 RavenDB collections vs their PostgreSQL tables — full count/ID parity everywhere plus deep field-by-field audits on the 9 core domains. Pass = exit 0, JSON `overall_status: "PASS"` with 0 missing / 0 extra / 0 mismatches, and a detailed report JSON written under `validation/`.

- **Q: What does gate 4 actually exercise?**
  Two reads (students, fee transactions) returning HTTP 200 JSON arrays, and one **write** — a POST that inserts a fee transaction and activates the audit trigger, expecting 200 or 201.

  - **Q: What if the dataset doesn't contain the hard-coded demo student/fee IDs?**
    *[UNRESOLVED]* The POST body pins two UUIDs from one specific source dataset. Against any other RavenDB source, a *correct* migration can still fail the write gate. → **product decision.**

  - **Q: What if `API_PORT` in `.env` isn't 5000?**
    *[UNRESOLVED]* The runbook's curl commands hard-code `localhost:5000` and ignore `API_PORT` (which the companion `wait-for-api.sh` *does* honour). → **product decision.**

- **Q: What does gate 5 run?**
  The xUnit suite in the .NET SDK container against the same PostgreSQL instance; pass = exit 0 and a `Passed! - Failed: 0` summary line.

- **Q: What happens at the end?**
  Optional teardown (`docker compose down`, or `down -v` to wipe data), then — only if every gate passed — the agent emits the fixed summary block: `### Onboarding Status: SUCCESS` with PASS for steps 0–5.

- **Q: Are there rules the agent must follow throughout?**
  Yes: never prompt interactively; stop immediately and report on the first failure; never commit or echo `.env` / `*.pfx` / `scripts/certs/*` secrets; and run everything through Docker containers, never host-installed Python/psql/.NET.

---

## 3. Golden fixtures

| id | covers | source | status |
|---|---|---|---|
| `runbook_gates_full_pass` | all gates 0–5 passing on a configured environment: preflight PASS marker, health JSON, migration summary + exit 0, parity PASS report artifact, API 200s, test suite exit 0, final SUCCESS summary | authored-from-code (criteria and strings lifted verbatim from `agent_runbook.md` and the gate scripts) | **pending** capture against a live legacy run for validation |

See `specs/golden/migration/runbook_gates_full_pass.json`.

---

## 4. Open items

1. `[legacy-divergence]` **`verify-prerequisites.ps1` referenced but missing** — gate 0's PowerShell variant cannot run as documented. — product decision.
2. `[legacy-divergence]` **gate-2 success-string mismatch** — runbook criterion quotes a message `migrate_all.py` never prints ("All migrations and post-migration scripts completed successfully"); literal string-matching against the criterion can never pass. — product decision.
3. `[legacy-divergence]` **hard-coded demo UUIDs in gate-4 POST** — write gate is dataset-coupled; fails on any source other than the one the demo IDs came from. — product decision.
4. `[legacy-divergence]` **hard-coded `localhost:5000` in gate-4 curls** — contradicts configurable `API_PORT` honoured elsewhere (`wait-for-api.sh`). — product decision.
5. `[low]` **PostgreSQL host port (5433 vs 15432)** — stale README troubleshooting paragraph contradicts compose/runbook default. — SME/doc cleanup.
6. `[low]` **canonical agent runner** — guide assumes Google Antigravity (`agy`); runbook is runner-agnostic YAML. Confirm intended runner. — SME question.
7. `[low]` **`wait-for-api.sh` placement** — readiness helper exists but is referenced by no gate step. — SME question.
8. `[low]` **gate-3 entrypoint fragility** — bare-script filename depends on container `WORKDIR /app/scripts`. — note; revisit if Dockerfile changes.
9. `[todo]` **capture golden against a live configured environment** (Docker + reachable RavenDB + cert) to set `validated_against_legacy: true` — no frozen dataset or running instance was available for this extraction.

================================================================================
WIRE — the gate chain (this file's own words; NOT part of the spec)
================================================================================

The document above is the gate contract: the rules, not yours to rewrite. On
the turn below you run the gate chain through child agents.

Four hops, ONE at a time, in this exact order:

  hop 1 — gate 0 preflight
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
