# migration · etl-orchestrator — extracted spec (v0.1)

> **Status:** extraction from legacy code · **Confidence ceiling reached:** medium (code-only; no SME sign-off, no golden captured against a live legacy environment)
> **Legacy provenance:** `scripts/migrate_all.py` (whole file); realization context: `docker-compose.yml` (`rpg-migrator` service, entrypoint), `scripts/Dockerfile` (`WORKDIR /app/scripts`, `ENTRYPOINT python migrate_all.py`, `CMD --all`); child contract sampled via `scripts/migrations/students_ravendb_to_postgres_migrate.py`
> **Layers below:** (1) KB spine · (2) human view · (3) golden refs · (4) open items
>
> Source-priority note: per the adapter this is a code-first extraction. There are no
> Raven indexes, dispatched jobs, or assertion-bearing tests for this operation; the
> orchestrator treats its 30 child scripts as opaque exit codes (their internals —
> RavenDB paging, transforms, `validation/` summary JSON — are a separate extraction).

---

## 1. KB spine

```kb
% --- entity ---
statement(etl_orchestrator, is_a, batch_migration_runner, [certainty(medium), source([code]), mechanism("python CLI `migrate_all.py`; containerized as rpg-migrator ENTRYPOINT with CMD --all"), ref("migrate_all.py:1-6, scripts/Dockerfile")]).
statement(etl_orchestrator, has_attribute, module_registry, [type(ordered_list), has_value_set([users, personas, courses, staffs, students, fees, exams, applications, assets, attendance_events, commits, emails, sms, artefacts, assessments, topics, voucher_views, seat_matrices, receipts, questions, member_views, material_views, ledger_account_views, inventory, institute_calendars, image_tags, gradings, content_tags, circulation_views, calendar_rules]), certainty(medium), source([code]), note("30 modules, fixed order; `students` module also migrates organization + institute"), ref("migrate_all.py:15-46")]).

% --- selection ---
statement(etl_orchestrator, requires, module_selection, [certainty(medium), source([code]), note("--all, or --module/-m comma list; absence of both defaults to ALL"), ref("migrate_all.py:129-137")]).
statement(etl_orchestrator, validates, module_names_normalized, [certainty(medium), source([code]), mechanism("lowercase + ~100-entry alias table (e.g. student→students, admission→applications, calendar→institute_calendars, qatag→questions, commit→commits)"), ref("migrate_all.py:139-239")]).
statement(etl_orchestrator, retains, registry_order_for_selection, [certainty(medium), source([code]), note("even a --module subset executes in the fixed registry order, not in the order requested"), ref("migrate_all.py:246-247")]).

% --- env handling ---
statement(etl_orchestrator, depends_on, root_env_file, [certainty(medium), source([code]), mechanism("loads <scripts_dir>/../.env into os.environ; pre-set environment variables always win (only sets keys not already in env); quote-stripping on values"), ref("migrate_all.py:48-59, 122-126")]).
statement(etl_orchestrator, depends_on, pg_connection_env, [certainty(medium), source([code]), mechanism("PG_HOST/PG_PORT/PG_DB/PG_USER/PG_PASSWORD; in-container compose sets PG_HOST=rpg-postgres, PG_PORT=5432 (overriding .env's host port value)"), ref("migrate_all.py:90-94, docker-compose.yml:42-45")]).

% --- execution ---
statement(etl_orchestrator, creates, child_process_per_module, [certainty(medium), source([code]), mechanism("subprocess.run([sys.executable, <script>]) — sequential, blocking, one module at a time; each child banner-printed '[*] Starting Migration: …' / '[+] Success: …'"), ref("migrate_all.py:61-71, 256-260")]).
statement(etl_orchestrator, carries_forward, unrecognized_args_to_children, [certainty(medium), source([code]), mechanism("parse_known_args: every flag the orchestrator does not know is forwarded verbatim as extra args to EACH child script (children parse_known_args and silently ignore what they don't know)"), ref("migrate_all.py:133, 65, 256")]), 
statement(etl_orchestrator, on_invalid, child_exit_nonzero, [certainty(medium), source([code]), mechanism("prints '[!] Error: <script> failed with exit code N', counts a failure, and CONTINUES to the next module (no stop-on-first-failure inside the orchestrator)"), ref("migrate_all.py:67-69, 246-260")]).

% --- post-migration SQL ---
statement(etl_orchestrator, requires, at_least_one_successful_module_for_post_sql, [certainty(medium), source([code]), note("post-SQL runs only if success_count > 0 and --skip-post-sql was not given"), ref("migrate_all.py:266-267")]).
statement(etl_orchestrator, creates, views_indexes_and_triggers, [certainty(medium), source([code]), mechanism("psycopg2 connect (autocommit) executes 01_student_fee_view.sql then 02_trigger.sql; sql dir resolved by first-existing of <root>/student-fee-poc/sql → <root>/sql → <scripts>/sql; missing dir or missing file is only warned"), ref("migrate_all.py:73-119")]).

% --- reporting / exit ---
statement(etl_orchestrator, creates, migration_summary_line, [certainty(medium), source([code]), mechanism("stdout '[=] MIGRATION SUMMARY: <n> succeeded, <m> failed'"), ref("migrate_all.py:262-264")]).
statement(etl_orchestrator, transitions_to, exit_code, [certainty(medium), source([code]), note("exit 1 iff failure_count > 0 (missing script file counts as a failure); post-SQL errors never affect the exit code"), ref("migrate_all.py:269-270")]).

% --- divergences (route to product decision) ---
statement(s(etl_orchestrator, reports, success_after_post_sql_failure), needs, product_decision,
          [certainty(unresolved), source([code]),
           note("apply_post_migration_sql wraps its whole body in try/except and only prints '[!] Warning during post-migration SQL execution' — a bad connection or failing SQL never fails the run, so the orchestrator can exit 0 with the cross-module view and triggers never created (the runbook's gate-2 criterion 'views/triggers applied' is then silently untrue)")]).
statement(s(etl_orchestrator, on, unrecognized_module_name), needs, product_decision,
          [certainty(unresolved), source([code]),
           note("'--module bogus' (or a typo'd alias) normalizes to a name absent from the registry; the loop skips it without counting anything → summary '0 succeeded, 0 failed', post-SQL skipped (success_count==0), exit 0 — a request that migrated NOTHING reports success")]).
statement(s(etl_orchestrator, on, partial_module_failure), needs, product_decision,
          [certainty(unresolved), source([code]),
           note("with success_count>0 and failure_count>0 the post-SQL (student_fee_summary_view) is still applied over partially loaded data BEFORE exiting 1 — the view can then silently serve incomplete joins if anything reads it before the failed module is re-run")]).
statement(s(etl_orchestrator, forwards, unrecognized_args_to_children), needs, product_decision,
          [certainty(unresolved), source([code]),
           note("a typo'd orchestrator flag (e.g. '--al') is treated as unknown: orchestrator defaults to ALL modules AND forwards '--al' verbatim to every child, where it is silently ignored — the run completes with no signal that the intended flag never took effect")]).

% --- low-confidence / SME questions ---
statement(s(etl_orchestrator, on_invalid, child_failure_continue_not_stop), needs, sme_input,
          [certainty(low), source([code]),
           note("the orchestrator runs all remaining modules after one fails, whereas the agent runbook's global rule is stop-on-first-error — confirm which layer owns the stop policy")]).
statement(s(etl_orchestrator, depends_on, env_precedence), needs, sme_input,
          [certainty(low), source([code]),
           note(".env values only apply when the variable is not already in the environment; child scripts independently re-load .env with the same precedence — confirm this two-level resolution is intended")]).
statement(s(etl_orchestrator, depends_on, sql_dir_fallback), needs, sme_input,
          [certainty(low), source([code]),
           note("third candidate '<scripts>/sql' exists on neither host layout nor container image — dead fallback path; confirm the first two are the only real layouts")]).
statement(s(etl_orchestrator, has_attribute, child_summary_artifacts), needs, sme_input,
          [certainty(low), source([code]),
           note("children write validation/migration-summary-<ts>.json, but the orchestrator neither reads, aggregates, nor surfaces them — confirm they are operator-facing only")]).
```

---

## 2. Human view (SME reads this)

**Q: What does the ETL orchestrator do?**
It is the master runner for the RavenDB→PostgreSQL migration: given a module selection, it executes the matching per-domain ETL child scripts **sequentially in a fixed 30-module order**, then — if at least one module succeeded — applies the cross-module view, indexes, and trigger SQL directly to PostgreSQL, and finally reports a succeeded/failed tally with exit 1 if anything failed.

- **Q: How do I ask it what to migrate?**
  `--all` migrates everything (also the default when no `--module` is given). `--module a,b` migrates a subset; names are lowercased and passed through a large alias table (`student`→`students`, `admission`→`applications`, `calendar`→`institute_calendars`, …). Whatever you select, execution order is the registry's, not yours.

  - **Q: What if I misspell a module name?**
    *[UNRESOLVED]* An unrecognized name matches nothing, is counted nowhere, and the run ends with `0 succeeded, 0 failed` and **exit 0** — nothing migrated, nothing post-processed, no error. → **product decision.**

- **Q: Where does configuration come from?**
  The `.env` at the repo root (loaded only for variables not already set in the environment — pre-set env always wins). Each child also re-resolves the same `.env` itself. In Docker, compose pins `PG_HOST=rpg-postgres` / `PG_PORT=5432` for the post-SQL connection regardless of the host-port forwarding value in `.env`.

- **Q: What does each child run look like?**
  A blocking subprocess (`python <script>`), one at a time, with banner lines before/after. Any arguments the orchestrator itself doesn't recognize are **forwarded verbatim to every child** (that's how `--raven-url …` etc. reach the ETL scripts).

  - **Q: What if a module fails?**
    *[LOW]* The orchestrator prints `[!] Error: <script> failed with exit code N`, counts it, and **keeps going** through the remaining modules — no stop-on-first-failure inside this layer. Exit code is 1 at the end if anything failed. Whether this layer or the agent's stop-on-error rule owns the halt policy is an **SME question**.

  - **Q: What if I typo an orchestrator flag, like `--al`?**
    *[UNRESOLVED]* Unknown flags are forwarded to children and silently ignored there; meanwhile the orchestrator sees neither `--all` nor `--module` and **defaults to migrating everything** — the run succeeds with no hint your flag was never understood. → **product decision.**

- **Q: When do the view/indexes/triggers get applied?**
  After all selected modules finish, only if **at least one** module succeeded and `--skip-post-sql` was not passed. The SQL directory is found by trying `<repo>/student-fee-poc/sql`, then `<repo>/sql`, then `<scripts>/sql`; the two files (`01_student_fee_view.sql`, `02_trigger.sql`) are executed over a single autocommit connection.

  - **Q: What if that SQL fails — bad connection, syntax error, missing file?**
    *[UNRESOLVED]* Everything is caught and printed as a `[!] Warning …`; the run still **exits 0**. A migration can report success with the `student_fee_summary_view` and audit triggers never created. → **product decision.**

  - **Q: What if *some* modules failed but others succeeded?**
    *[UNRESOLVED]* The post-SQL still runs — over partially loaded data — and only afterwards does the process exit 1. The cross-module view can exist and serve incomplete joins before the failed module is re-run. → **product decision.**

- **Q: What does a successful run print?**
  One `[*] Starting Migration` banner per module, a `[+] Success` line per child, then `[=] MIGRATION SUMMARY: N succeeded, M failed`. Per-module JSON summaries land in `validation/`, but the orchestrator itself never reads them.

---

## 3. Golden fixtures

| id | covers | source | status |
|---|---|---|---|
| `etl_orchestrator` | targeted `--module fees` run: alias/selection, banner lines, child exit propagation, summary line, post-SQL applied, exit 0 | authored-from-code (stdout strings and control flow lifted verbatim from `migrate_all.py`; child inputs from `students_…py` arg/env contract) | **pending** capture against a live legacy run (needs reachable RavenDB + PostgreSQL) for validation |

See `specs/golden/migration/etl_orchestrator.json`.

---

## 4. Open items

1. `[legacy-divergence]` **post-SQL failures swallowed** — try/except prints a warning; run exits 0 with view/triggers possibly missing. — product decision.
2. `[legacy-divergence]` **unknown module name = silent no-op with exit 0** (`--module bogus` → "0 succeeded, 0 failed"). — product decision.
3. `[legacy-divergence]` **post-SQL applied over partially loaded data** when some modules failed (success>0, failure>0) before exiting 1. — product decision.
4. `[legacy-divergence]` **typo'd flags forwarded to every child and silently ignored** (`--al` → full migration anyway). — product decision.
5. `[low]` **no stop-on-first-failure inside the orchestrator** vs the agent runbook's global stop-on-error rule — which layer owns the halt policy. — SME question.
6. `[low]` **env precedence** — pre-set environment always wins over `.env`, resolved twice (orchestrator + each child). — SME question.
7. `[low]` **dead sql-dir fallback** `<scripts>/sql` exists in neither host nor container layout. — SME question.
8. `[todo]` **child ETL contract** (per-module RavenDB paging, transforms, `validation/migration-summary-*.json` writes) is opaque to this orchestrator and is its own extraction — the orchestrator is only fully specified once at least one child (e.g. `students`) is extracted.
9. `[todo]` **capture golden against a live legacy run** (reachable RavenDB + PostgreSQL) to set `validated_against_legacy: true`.
