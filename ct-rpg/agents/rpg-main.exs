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
# After the copy comes the WIRE section — this file's own words, clearly
# marked as not part of the spec. It is the only place behaviour is added:
# spawn one child at a time, in order — gate 0 preflight, then gate 2
# migrate, then gate 3 verify (parity), then gate 4 api — wait for each,
# read final_message, and stop on the first failed gate, reporting which
# gate failed and that the rest did not run. The channel is the child's
# final_message; spawn_agent + wait_for_all is the whole mechanism.

agent_root = Path.expand(Path.join(Path.dirname(__ENV__.file), ".."))

run_id = "ct-rpg-main-#{Aetheris.ID.generate()}"

model    = System.get_env("CT_RPG_MODEL") || System.get_env("AETHERIS_MODEL") || "claude-haiku-4-5-20251001"
provider = System.get_env("AETHERIS_PROVIDER") || "anthropic"

%Aetheris.RunConfig{
  run_id:           run_id,
  mode:             :record,
  provider:         provider,
  model:            model,
  label:            "CT-RPG Migration Gate Orchestrator",
  sandbox_path:     agent_root,
  overlay_base_dir: nil,
  max_steps:        12,
  context_strategy: :full,
  tools:            ["spawn_agent", "wait_for_all"],
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

Four children, ONE at a time, in this order — gate 0 preflight, then gate 2
migrate, then gate 3 verify (parity), then gate 4 api. Spawn a child, wait
for it, read its result, then spawn the next. Never spawn children in
parallel, never spawn the next before the previous one has been read.

Harness mechanics (not choices):
- spawn_agent arguments are task_prompt, tools, max_steps, timeout_ms — there
  is no payload field. task_prompt becomes the child's system_prompt; put the
  child's role text AND its parameters in task_prompt.
- wait_for_all returns one map per run: run_id, status, final_message, steps.
  final_message is the channel — the child's last text. Wait after each spawn
  with run_ids = [that child's run_id] and timeout_ms: 120000, passed
  explicitly. A child whose status is terminal is FINISHED: read
  final_message and continue the chain — a finished child must never be
  reported as timed out. Report a timeout only when wait_for_all reports the
  run timed out AND the run's status is not terminal.

Stop-on-first-failure (the spec's own execution rule, applied to the chain):
after each wait, read final_message. If the child reports its gate FAILED —
a non-zero exit code, a [FAIL] / error line, or an explicit failure report —
STOP. Report which gate failed and that the remaining children did not run.
Do not spawn the rest. Do not retry.

Child role texts, copied into each task_prompt from the document above:
- Gate 0 (preflight): the `% --- gate 0: preflight ---` KB block from §1 plus
  the three preflight Q&A entries from §2, verbatim, plus this invocation
  contract: the migration repo root arrives as a parameter in the user
  prompt — pass it through in the task_prompt, never hard-code a path; the
  child runs `bash scripts/verify-prerequisites.sh` once from that root and
  reports its exit code and last stdout line. (The standalone wrap is
  ct-rpg/agents/rpg-preflight.exs; spawn_agent does not load standalone
  wraps — the role text travels in task_prompt.)
- Gate 2 (migrate): the `% --- gate 2: migration ---` KB block from §1. Its
  standalone wrap lands at T3 (ct-rpg/milestone.md).
- Gate 3 (verify): the `% --- gate 3: parity ---` KB block from §1. Its wrap
  lands at T4.
- Gate 4 (api): the `% --- gate 4: api ---` KB block from §1. Its wrap lands
  at T5.

Until the T3–T5 wraps land, reaching one of those gates means the chain
stops there: report which gate is next, that its child does not exist yet,
and stop. Gates 1 (services) and 5 (tests) have no child in this milestone's
ticket list; the same rule applies if the chain reaches them.
""",
  user_prompt:      "T1 fixture turn — not a live run. Parameter: migration repo root = <MIGRATION_REPO_ROOT>. Begin."
}
