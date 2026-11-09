# r2pg-migration — Design Doc

> Audience: a human reading the repo for the first time, or an agent executing it tomorrow.
> Everything below is stated as the repo actually behaves. File paths and command strings are exact.
> This document describes; it does not change anything.

---

## 1. Purpose

This repository migrates a school/fee-management dataset from **RavenDB** (source) to **PostgreSQL** (target), then proves the result three ways: a field-by-field parity audit, a small REST API serving the migrated data, and an xUnit test suite. The migration logic lives entirely in **fixed Python scripts** — one per business domain, with table names, field maps, and transforms written into the code. **The repo does not generate migrations**: there is no schema introspection, no generic mapper, no DSL. Nothing here adapts to an arbitrary RavenDB database; it moves the collections it was written for, in the order it was written. The *agents* referenced in this repo (`agent_runbook.md`, driven via Google Antigravity) live outside the code and only **invoke** these scripts and check their outputs — they own no migration logic, choose no modules, and write no SQL.

---

## 2. Architecture

### What runs inside Docker

Four services are declared in `docker-compose.yml`:

| Service | Image / build | Role |
|---|---|---|
| `rpg-postgres` | `postgres:16-alpine`, port `${PG_PORT}:5432` (default 15432) | Target database. Starts **empty**; all tables are created by the migrator. |
| `rpg-api` | built from `student-fee-poc/dotnet/student-fee-poc/Dockerfile`, port `${API_PORT}:8080`→5000 | ASP.NET Core 10 REST API over the migrated data. Never touches RavenDB. |
| `rpg-migrator` | built from `./scripts/Dockerfile` (Python 3.12, `WORKDIR /app/scripts`, `ENTRYPOINT ["python", "migrate_all.py"]`, `CMD ["--all"]`) | One-shot ETL runner and parity verifier. Mounts `.env` (ro), `scripts/certs/` (ro), `validation/` (rw). |
| `rpg-tests` | `mcr.microsoft.com/dotnet/sdk:10.0-preview` | Runs `dotnet test` (xUnit) against `rpg-postgres`. |

### What runs on the host

- `scripts/verify-prerequisites.sh` — the preflight check (git, docker, compose v2, `.env`, certificate, no secrets tracked by Git). Plain bash, runs from the repo root.
- The **agent hops**: the agent itself (Antigravity `agy` CLI/IDE) runs on the host and issues the gate commands below; the work happens in containers. The API curl checks also run on the host (or from any shell that can reach `localhost:5000`).

### The gate commands, named exactly

The agents invoke **four `docker compose` gate commands**, in this order:

1. `docker compose up -d --build rpg-api`
2. `docker compose run --rm rpg-migrator --all`
3. `docker compose run --rm --entrypoint python rpg-migrator verify_raven_to_postgres.py`
4. `docker compose run --rm rpg-tests`

Around them sit two host-side assertion sets: gate 0 preflight (`bash scripts/verify-prerequisites.sh`) and gate 4's three curls against `http://localhost:5000` (see §6). `scripts/wait-for-api.sh` exists as an optional bounded readiness probe; no gate references it.

### Where the per-collection scripts live, and how `--all` finds them

Per-collection ETL scripts live in `scripts/migrations/*.py` (30 files, e.g. `scripts/migrations/students_ravendb_to_postgres_migrate.py`). `--all` does **not** discover them by globbing: `migrate_all.py` holds a fixed, ordered registry — `MODULE_SCRIPTS` at `scripts/migrate_all.py:15-46` — mapping module name → script filename. `--all` (or no `--module`) walks that list top to bottom, spawning each script with `subprocess.run([sys.executable, <path>])` from `scripts/migrations/`. A module name that is not in the registry is silently ignored (see §7). Execution order is always registry order, even for a `--module` subset.

---

## 3. Decisions (what was chosen, and why)

**One script per RavenDB collection, not a generic mapper.**
Each domain gets a standalone file (`scripts/migrations/<domain>_ravendb_to_postgres_migrate.py`). The students script is the widest, covering three collections (`Orgs`, `Institutes`, `Students` → three tables); the narrowest handle one collection each. This mirrors the parity auditor's 42 collection↔table pairs and keeps each domain's quirks (identity fallback chains, enum mappings) local and readable. Cost: 30 near-identical copies of the same fetch/upsert skeleton.

**Hardcoded field maps and table names inside each script.**
Column lists, PG enum types, and Raven field names are written literally in the SQL strings (e.g. `ensure_target_schema()` / `upsert_student()` in the students script). There is no external mapping file. `--module` names are resolved through a ~100-entry alias table in `migrate_all.py` (`"student"→"students"`, `"admission"→"applications"`, …). Collection names are *not* hardcoded — they come from `.env` (`ORG_COLLECTION`, `STUDENT_COLLECTION`, …) so the same scripts can target differently named RavenDB databases.

**Docker Compose for the migrator and Postgres.**
No host installation of Python, psycopg2, .NET, or PostgreSQL is assumed; `playbook.md` states this explicitly. Compose pins the in-container DB coordinates (`PG_HOST=rpg-postgres`, `PG_PORT=5432`) regardless of the host port mapping, mounts the certificate and `validation/` output dir read-only where secrets are involved, and gates the API/migrator/tests on the Postgres healthcheck. RavenDB stays outside Compose — it is a live external service (cloud or `host.docker.internal:8080`).

**Post-migration SQL applied after the table loads.**
`01_student_fee_view.sql` (cross-module `student_fee_summary_view` + GIN/B-tree indexes) and `02_trigger.sql` (`modified_on` triggers + `fee_transaction_audit`) are applied by `migrate_all.py:apply_post_migration_sql()` only **after** ≥1 module has loaded, via a direct psycopg2 connection — not by the API, not by Docker init scripts. This keeps PostgreSQL clean until data exists, matching the README's "zero hardcoded schema initialization" decision. Consequence: post-SQL failures are warnings, not errors (see §7).

**Parity check as a separate Python audit, not inside the load scripts.**
`scripts/verify_raven_to_postgres.py` re-reads both sides independently and compares. This separation means the loader can't mark its own homework: the verifier re-derives identities from the Raven documents (`extract_standard_id` / `extract_student_id`), re-applies the enum transforms, and auto-expands any Raven field that has a same-named PG column. It also lets the verifier run standalone (`--module`, `--core-only`) without re-running any load.

**API verification as three fixed curls, not a generated client.**
Gate 4 is literally three `curl` calls with a hard-coded POST body (see §6). No Swagger-generated client, no test harness. The rationale is gate simplicity: an agent can run `curl -s -f` and check the exit code. The deeper assertions (row persisted, audit trigger fired) were pushed to the xUnit suite (gate 5) instead of the curls.

**Other decisions found in the tree that shaped the scripts:**
- **Identity by first-UUID-in-string.** Every script derives primary keys with a regex (`UUID_RE`) that extracts the *first* UUID in a value and lowercases it, walking a fallback chain (`SourceX` → `Id` → metadata `@id`). For students the order is reversed (metadata UUID first). No surrogate keys are generated by the migration.
- **Single transaction per run.** The students ETL creates schema under autocommit, then loads **all** orgs + institutes + students inside one `with conn:` transaction — any row failure rolls back the whole data load while the DDL stays.
- **Upsert, not insert.** Every load is `INSERT … ON CONFLICT (id) DO UPDATE SET <every column>`, making re-runs idempotent (and overwriting `created_on` from source).
- **Canonical data model naming.** Lowercase snake_case, UUID PKs, `{table}_id` FKs, `idx_/uq_/…_gin` index names — specified in `docs/sql_to_postgres_canonical_migration_guide.md` and followed by all 42 tables.
- **The API mimics the legacy product's payload shapes** (status → numeric codes Active=1/Disabled=99, camelCase keys, synthetic defaults like `domicile.country: "India"`) rather than inventing a clean REST contract, because its purpose is parity with `https://svc.campustrack.net/api/*`.
- **Secrets discipline.** `.env` and `scripts/certs/*.pfx` are git-ignored; the preflight actively fails if Git tracks them; the runbook forbids echoing secret values.
- **Everything-through-Docker rule** for agents (`agent_runbook.md`: "Do not run local Python, psql, or .NET on the host").

---

## 4. Scenarios the scripts handle

Only cases present in the code are listed. Format: *case — owner (file:function/line region)*.

- **Empty RavenDB collection** — every ETL: `raven_query_collection()` (e.g. `students_ravendb_to_postgres_migrate.py:1039-1076`) stops on the first empty page; zero documents simply load zero rows. Same in `verify_raven_to_postgres.py:fetch_raven_collection()` (695–722).
- **Missing field on a document** — every `upsert_*`: `doc.get(...)` yields `None` → SQL `NULL` column; JSONB wrappers (`as_json`, students script 1032–1036) keep SQL NULL semantics; the verifier's `normalize_val()` (104–136) treats empty string/list/dict as equivalent to None on both sides.
- **Type coercion** — per-script transform helpers: `parse_ts()` (ISO normalization, tz-naive → UTC, fractional seconds truncated to 6 digits), `parse_int()`, `extract_uuid_from_any()` (first UUID in any string, lowercased), enum maps `parse_student_gender/status`, `parse_organization_status`, `parse_edu_level`, etc. The verifier mirrors these and adds `normalize_datetime()` (61–101) plus numeric rounding to 4 decimals.
- **Unparseable status value** — silently coerced to `"Active"` (`parse_student_status` etc., `.get(int(value), "Active")` fallback). Open item — see §7.
- **Duplicate id / re-run** — `ON CONFLICT (id) DO UPDATE SET <all columns>` in every `upsert_*` (e.g. students 1846–1997): re-runs update in place; the orchestrator's pre-load `SELECT 1` distinguishes new vs updated for the summary stats.
- **Document with no derivable UUID** — skipped silently: `upsert_organization/institute/student` return `None` when the fallback chain finds no UUID; the doc is neither loaded nor counted as failed (only the fetched-vs-processed printout reveals the gap).
- **Enrollment pointing at an unloaded institute** — `student.inst_id` set to NULL silently (`derive_source_inst_id_from_student` + the existence check in `upsert_student`, 1829–1839).
- **`short_name` longer than 6 chars (institute)** — truncated to 6, blank → NULL (`upsert_institute`, 1627–1631).
- **Non-200 / malformed RavenDB response** — `RuntimeError` raised; the ETL's single `try` in `main()` prints `Migration failed: …` to stderr and exits 1 (schema DDL stays, data load rolls back). The verifier instead records per-pair status `ERROR` and continues.
- **Missing target table during verification** — `MISSING_TABLE` status with message (`verify_domain`, 754–766).
- **Missing module script file** — `[!] Warning: Script <file> not found. Skipping.` and counted as a failure (`migrate_all.py:248-254`).
- **Unknown module name on the CLI** — silently ignored: not in the registry, never counted, run ends `0 succeeded, 0 failed`, exit 0 (`migrate_all.py:135-239`).
- **Post-migration SQL failure** — swallowed: `apply_post_migration_sql()` catches everything and prints `[!] Warning during post-migration SQL execution: …`; exit code stays 0 (`migrate_all.py:98-119`).
- **Missing config** — ETL scripts hard-fail via `parser.error("Missing … config")` (students 153–180); the **verifier does not** — it silently defaults (§7).
- **POST `/api/feeTx` with invalid status string** — Postgres cast to `fee_tx_status_enum` fails → caught → `400 {"error": …}` (`Program.cs:100-103`).
- **POST `/api/feeTx` with non-existent studentId/feeId** — succeeds silently: no FK on `fee_transaction.student_id`, feeId only embedded in JSONB (`fees_ravendb_to_postgres_migrate.py:534-561` DDL).
- **DB down at health check** — `/health` returns **503** `{"status":"Unhealthy","database":"Disconnected"}` (`Program.cs:44-58`); the preflight/verifier PG failure paths return exit 1 with `[!] Critical Error`.
- **Verifier `--module` filter with no match** — zero pairs selected; audit table prints totals-only and overall PASS (vacuous). `--core-only` selects **all 42** pairs (every spec is `is_core: True`) — see §7.

---

## 5. What an agent must not assume

1. **Do not invent collection names.** Collections come from `.env` (`*_COLLECTION` variables) and the fixed registry in `migrate_all.py`. The 42 valid collection→table pairs are listed in §6 of `docs/migration_schema_reference.md` and enforced by `scripts/verify_raven_to_postgres.py:get_all_domain_specs()`.
2. **Do not write new migration scripts or SQL.** The 30 ETLs and the two post-SQL files are the complete, fixed set. Adding a domain is a code change, not an agent action.
3. **Do not reshape the fee-tx POST body.** Gate 4's body is fixed verbatim (studentId `cc93c106-82ea-4610-9873-3db87f1307c6`, amount `500.00`, status `"Active"` as a **string**, feeId `a7e2851c-2321-4adc-993a-387deefee3a8`, refNo `"AGENT-DEMO-01"`). Changing it is a product decision, not an agent liberty — the ids are dataset-coupled and dangling references are accepted silently.
4. **Do not start or stop services on your own initiative.** `docker compose up -d --build rpg-api` (gate 1) is the only service-starting command, and it comes at its position in the sequence. Teardown (`docker compose down` / `down -v`) is the operator's call.
5. **Do not choose modules.** The runbook's only documented migration command is `--all`; `--module` is a human-side tip (README:181, QUICKSTART:101, playbook:117) and would break gate 2's "42 tables" criterion.
6. **Do not run host runtimes.** Per `agent_runbook.md` rules: everything through Docker; no local Python, psql, or .NET.
7. **Do not echo secrets or commit them** — `.env`, `*.pfx`, `scripts/certs/*` (`agent_runbook.md` safety list; preflight enforces).
8. **Do not invent success strings.** Gate 2's real success signal is exit code 0 plus `[=] MIGRATION SUMMARY: N succeeded, 0 failed`; the runbook's quoted criterion string is never printed (§7).
9. **Do not reorder gates.** Gate 3 verifies data written by gate 2; gate 4 curls assume gate 1's API; each gate's criteria presuppose the previous ones.

---

## 6. How to run the gates by hand (golden baseline)

Working directory for **every** command: the **repository root** (`r2pg-migration/`), with `.env` configured and the `.pfx` certificate in `scripts/certs/`.

```bash
# Gate 0 — Preflight (host, bash)
bash scripts/verify-prerequisites.sh
# pass: exit 0, "[PREFLIGHT PASS] All checks passed (N warnings)."

# Gate 1 — Services (starts rpg-postgres + rpg-api; stays up)
docker compose up -d --build rpg-api
# verify: docker compose exec rpg-postgres psql -U postgres -d rpg -c "SELECT 1;"
#         curl -s -f http://localhost:5000/health   -> {"status":"Healthy","database":"Connected",...}

# Gate 2 — Migrate (one-shot container; all 30 modules + post-SQL)
docker compose run --rm rpg-migrator --all
# pass: exit 0, "[=] MIGRATION SUMMARY: 30 succeeded, 0 failed";
#       docker compose exec rpg-postgres psql -U postgres -d rpg -c "\dt"  lists 42 tables

# Gate 3 — Parity audit (one-shot container; re-entrypoint to run the verifier)
docker compose run --rm --entrypoint python rpg-migrator verify_raven_to_postgres.py
# pass: exit 0, "[SUCCESS] 100% COMPLETE PARITY CONFIRMED ACROSS ALL 42 TABLES AND N RECORDS!";
#       report JSON in validation/exhaustive-parity-report-<timestamp>.json

# Gate 4 — API (host curls; services from gate 1 must be up, data from gate 2)
curl -s -f "http://localhost:5000/api/stu/student?limit=2"
curl -s -f "http://localhost:5000/api/feeTx?limit=2"
curl -s -f -X POST "http://localhost:5000/api/feeTx" \
  -H "Content-Type: application/json" \
  -d "{\"studentId\": \"cc93c106-82ea-4610-9873-3db87f1307c6\", \"amount\": 500.00, \"status\": \"Active\", \"feeId\": \"a7e2851c-2321-4adc-993a-387deefee3a8\", \"refNo\": \"AGENT-DEMO-01\"}"
# pass: reads HTTP 200 ({"data":[...]} envelope); write HTTP 201 (Created)

# Gate 5 — Tests (one-shot container; also validates the audit trigger from gate 4's write)
docker compose run --rm rpg-tests
# pass: exit 0, "Passed! - Failed: 0, Passed: X, Skipped: 0"
```

The four `docker compose` commands (gates 1, 2, 3, 5) are the agent-invoked set; gates 0 and 4 are host-side checks around them. Teardown when done: `docker compose down` (keep data) or `docker compose down -v` (wipe volume).

### Collection → table pairs (the migration's fixed scope)

All 42 pairs, as declared in `scripts/verify_raven_to_postgres.py:get_all_domain_specs()` and `docs/migration_schema_reference.md`:

| # | RavenDB collection | PostgreSQL table | | # | RavenDB collection | PostgreSQL table |
|---|---|---|---|---|---|---|
| 1 | `Orgs` | `organization` | | 22 | `CommitAssets` | `commit_asset` |
| 2 | `Institutes` | `institute` | | 23 | `CommitAcs` | `commit_ac` |
| 3 | `Students` | `student` | | 24 | `ContentTags` | `content_tags` |
| 4 | `Courses` | `course` | | 25 | `Emails` | `email` |
| 5 | `Staffs` | `staffs` | | 26 | `Gradings` | `gradings` |
| 6 | `Personas` | `persona` | | 27 | `ImageTags` | `image_tags` |
| 7 | `Fees` | `fee` | | 28 | `InstituteCalendars` | `institute_calendars` |
| 8 | `FeeTxes` | `fee_transaction` | | 29 | `InventoryItemViews` | `inventory_item_views` |
| 9 | `Exams` | `exam` | | 30 | `InventoryJournalViews` | `inventory_journal_views` |
| 10 | `Users` | `users` | | 31 | `LedgerAccountViews` | `ledger_account_views` |
| 11 | `Applications` | `applications` | | 32 | `MaterialViews` | `material_views` |
| 12 | `ApplicationFormTemplates` | `application_form_templates` | | 33 | `MemberViews` | `member_views` |
| 13 | `Artefacts` | `artefacts` | | 34 | `Questions` | `questions` |
| 14 | `ArtefactTags` | `artefact_tags` | | 35 | `QATags` | `qa_tags` |
| 15 | `Assessments` | `assessments` | | 36 | `RandomQuestionSubmissions` | `random_question_submissions` |
| 16 | `AssessmentTags` | `assessment_tags` | | 37 | `Receipts` | `receipts` |
| 17 | `AssetViews` | `asset_views` | | 38 | `SeatMatrices` | `seat_matrices` |
| 18 | `AttendanceEvents` | `attendance_event` | | 39 | `SMs` | `sms` |
| 19 | `CalendarRules` | `calendar_rules` | | 40 | `SmsMessages` | `sms_message` |
| 20 | `CirculationViews` | `circulation_views` | | 41 | `Topics` | `topics` |
| 21 | `Commits` | `commits` | | 42 | `VoucherViews` | `voucher_views` |

(The `students` ETL module covers pairs 1–3 together; the `fees` module covers 7–8; `commits` covers 21–23; `assessments` 15–16; `questions` 34–36; `sms` 39–40; the remaining modules are one-to-one.)

---

## 7. Open items (left unresolved by the scripts)

Quoted from the tree; each is a divergence a maintainer must decide on, not fix silently.

1. **Windows preflight variant does not exist.** `agent_runbook.md:64` and `agent_runbook_guide.md:83` instruct `.\scripts\verify-prerequisites.ps1` — no such file is in the repo (bash `verify-prerequisites.sh` only).
2. **Silent PG defaults in the verifier.** `verify_raven_to_postgres.py:621-625`:
   `self.pg_host = ... or os.getenv("PG_HOST", "localhost")`, `... PG_PORT, "5432"`, `... PG_DB, "rpg"`, `... PG_USER, "postgres"`, `... PG_PASSWORD, ""` — with missing config it audits `localhost:5432/rpg` instead of failing, unlike the ETL which `parser.error`s.
3. **Unordered offset paging in the verifier.** `verify_raven_to_postgres.py:702`: `rql = f"from '{collection}'"` — no `order by id()`. The ETL pages with `order by id()` and comments (`students_...py:1051-1052`): *"Stable ordering makes offset paging deterministic; freeze source writes for the migration window to guarantee a consistent snapshot."* The verifier's own paging therefore has no such guarantee against a live source.
4. **`--core-only` is a no-op.** The verifier's docstring claims "9 core domains with 177 deep field/column transformations" and "33 auxiliary", but all 42 specs in `get_all_domain_specs()` carry `"is_core": True` (first spec, line 1699: `"is_core": True` on `Organizations`; spot-checks confirm all 42) — so `--core-only` selects everything.
5. **Runbook gate-2 criterion string is never printed.** `agent_runbook.md:102` expects *"All migrations and post-migration scripts completed successfully"*; `migrate_all.py` prints only `[=] MIGRATION SUMMARY: N succeeded, M failed` (line 263) and per-child `[+] Success: …` lines.
6. **Post-SQL failures are swallowed.** `migrate_all.py:118-119`: `except Exception as ex: print(f"[!] Warning during post-migration SQL execution: {ex}")` — the run still exits 0 with view/triggers possibly missing.
7. **Unknown module name is a silent success.** `migrate_all.py:135-239` — a name absent from `MODULE_SCRIPTS` is skipped without counting: `0 succeeded, 0 failed`, exit 0. Unknown flags are also forwarded verbatim to every child (e.g. a typo'd `--al` runs everything anyway).
8. **Unparseable status defaults to `Active`.** `students_...py:352-373` (`parse_student_status`): `return mapping.get(int(value), "Active")` — same fallback in the org/institute variants; the `Unknown` enum value is reachable only via explicit `-1`.
9. **`todaysAbsenteesOnly` is a no-op.** Bound in `Program.cs:64` but never referenced in `StudentQueries.GetStudentsPayloadAsync`'s SQL; `activeStudentsOnly` *is* used.
10. **`tx_no` collisions possible.** Generated as `TXN-{DateTime.UtcNow:yyyyMMddHHmmssfff}` (`FeeTransactionWriteQueries.cs:32`); the DDL declares `tx_no VARCHAR(100)` with no UNIQUE constraint (`fees_ravendb_to_postgres_migrate.py:536`), and `fee_transaction.student_id` has no FK — bogus ids persist silently.
11. **Verifier's PKCS#12 fallback leaves key material on disk.** `verify_raven_to_postgres.py:669-679`: key+certs are extracted to `tempfile.NamedTemporaryFile(delete=False, suffix=".pem")` and never deleted; on parse failure it only prints `[!] Warning: Unable to parse PKCS#12 certificate` and proceeds without client auth.
12. **Unused `deleted_students` counter.** Initialized at `students_...py:2047` (`deleted_students = 0`), never incremented — a delete/reconciliation step appears planned but unimplemented.

---

*End of document. Nothing in §6 or §4 authorizes new behaviour; the scripts are the contract.*
