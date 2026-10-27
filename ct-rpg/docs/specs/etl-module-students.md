# migration · etl-module-students — extracted spec (v0.1)

> **Status:** extraction from legacy code · **Confidence ceiling reached:** medium (code-only; no SME sign-off, no golden captured against a live legacy environment)
> **Legacy provenance:** `scripts/migrations/students_ravendb_to_postgres_migrate.py` (whole file, 2,148 lines); invoked by `scripts/migrate_all.py` as the `students` module (also carries the org + institute domains, cf. `specs/migration/etl-orchestrator.md`); schema contract re-checked by `scripts/verify_raven_to_postgres.py` (domain 27: `Orgs`/`Institutes`/`Students` → `organization`/`institute`/`student`)
> **Layers below:** (1) KB spine · (2) human view · (3) golden refs · (4) open items
>
> Source-priority note: code-first. The RavenDB collections are read live over HTTP
> (no client SDK); the only independent second source is the parity verifier, which
> re-derives the same collection→table mapping (used to cross-check identity rules).
> No SME available ⇒ nothing exceeds `medium`.

---

## 1. KB spine

```kb
% --- entities / scope ---
statement(etl_module_students, is_a, single_domain_etl, [certainty(medium), source([code]), mechanism("standalone python CLI; also run as the `students` module child process of migrate_all.py"), ref("students_...py:1-33, migrate_all.py:20")]),
statement(etl_module_students, migrates, three_collections, [certainty(medium), source([code]), has_value_set([Orgs, Institutes, Students]), note("collection names overridable via ORG_COLLECTION / INSTITUTE_COLLECTION / STUDENT_COLLECTION env or CLI"), ref("parse_args:124-128")]),
statement(etl_module_students, creates, target_tables, [certainty(medium), source([code]), has_value_set([organization, institute, student]), mechanism("CREATE TYPE (5 enums) + CREATE TABLE IF NOT EXISTS over an autocommit connection; column lists fixed in-code (zero external DDL)"), ref("ensure_target_schema:1107-1268")]),

% --- configuration contract ---
statement(etl_module_students, requires, raven_and_pg_config, [certainty(medium), source([code]), note("RAVEN_URL, RAVEN_DB, PG_HOST, PG_PORT, PG_DB, PG_USER, PG_PASSWORD, and the 3 collection names are mandatory — hard parse error if absent"), on_invalid(error("parser.error('Missing … config')")), ref("parse_args:153-174")]),
statement(etl_module_students, requires, page_size_and_timeout_positive, [certainty(medium), source([code]), on_invalid(error("Invalid page size / timeout")), ref("parse_args:176-180")]),
statement(etl_module_students, requires, https_url_when_cert_used, [certainty(medium), source([code]), note("RAVEN_CERT_FILE with a non-https RAVEN_URL is rejected — mutual TLS only makes sense over https"), on_invalid(error("RAVEN_CERT_FILE requires an https:// RavenDB URL")), ref("parse_args:195-199")]),
statement(etl_module_students, depends_on, env_resolution_order, [certainty(medium), source([code]), mechanism("searches .env at <script>/../../ → <script>/../ → <script>/; pre-set env vars always win (same rule as the orchestrator)"), ref("parse_args:92-100, load_env_file:65-81")]),

% --- extraction ---
statement(etl_module_students, reads, collections_via_raven_query_api, [certainty(medium), source([code]), mechanism("POST {raven_url}/databases/{db}/queries with RQL `from \"<Collection>\" order by id()`; offset paging Start += len(Results), PageSize = PAGE_SIZE (default 500); stops on first empty page"), ref("raven_query_collection:1039-1076")]),
statement(etl_module_students, validates, raven_response_shape, [certainty(medium), source([code]), on_invalid(error("RuntimeError('Unexpected RavenDB response …') / non-document result")), ref("raven_query_collection:1060-1068")]),
statement(etl_module_students, depends_on, pkcs12_client_cert, [certainty(medium), source([code]), mechanism("requests.Session + Pkcs12Adapter mounted on https:// (requires requests-pkcs12, hard ImportError message otherwise); --raven-insecure disables TLS verification"), ref("configure_raven_session:1079-1104")]),

% --- identity derivation (the hidden rules) ---
statement(organization_row, identified_by, first_uuid_of_source_orgid_orgid_id_metaid, [certainty(medium), source([code]), mechanism("extract_uuid_from_any takes the FIRST UUID regex match in the string, lowercased; missing → doc silently skipped"), ref("upsert_organization:1505-1513, extract_uuid_from_any:979-985")]),
statement(institute_row, identified_by, first_uuid_of_source_instid_instid_id_metaid, [certainty(medium), source([code]), ref("upsert_institute:1614-1622")]),
statement(student_row, identified_by, first_uuid_of_metaid_id_sourcestudentid_studentid, [certainty(medium), source([code]), note("PRECEDENCE DIFFERS from org/inst: Raven document UUID (metadata @id) is preferred for student, source-first for org/institute"), ref("derive_student_pk:1754-1768")]),
statement(student_row, has_attribute, student_id_business_code, [certainty(medium), source([code]), note("business code (e.g. 23P001): SourceStudentId → StudentId → first enrollment's StudentId; the Raven document UUID is NEVER substituted"), ref("derive_student_id:1771-1791")]),
statement(student_row, has_attribute, inst_id_resolved_against_loaded_institutes, [certainty(medium), source([code]), note("first enrollment InstId UUID, set only if that institute row already exists in the institute table at that moment — otherwise silently NULL, no warning"), ref("derive_source_inst_id_from_student:1794-1806, upsert_student:1829-1839")]),

% --- transforms ---
statement(etl_module_students, transforms, status_enums, [certainty(medium), source([code]), mechanism("PG enums (5): organization/institute_status_enum {Unknown,ActivationPending,Active,Locked,Disabled}, student_status_enum {Unknown,Active,Disabled}, student_gender_enum {Female,Male,NoInfo}, edu_level_enum"), ref("ensure_target_schema:1111-1156")]),
statement(s(etl_module_students, transforms, unparseable_status), needs, product_decision,
          [certainty(unresolved), source([code]),
           note("parse_student_status / parse_organization_status / parse_institute_status fall back to 'Active' for ANY unrecognized value — a garbage or out-of-range source status silently becomes Active (the API re-encoder treats -1 as 'Unknown', so the two layers disagree)")]),
statement(etl_module_students, transforms, institute_short_name, [certainty(medium), source([code]), note("truncated to 6 chars; blank after strip → NULL"), ref("upsert_institute:1627-1631")]),
statement(etl_module_students, transforms, timestamps_to_utc, [certainty(medium), source([code]), mechanism("parse_ts: ISO-normalization, fractional seconds truncated to 6 digits, tz-naive assumed +00:00"), ref("parse_ts:988-1016")]),
statement(etl_module_students, transforms, nested_documents_to_jsonb, [certainty(medium), source([code]), has_value_set([address, attendance, father, mother, guardian, domicile, fees_receivable, iep, documents, contacts, addresses, attributes, occupations, enrollments]), mechanism("as_json preserves SQL NULL for absent values"), ref("upsert_student:1964-1988")]),

% --- boundary re-homing (adapter-flagged divergence class) ---
statement(s(student_table, embeds, fees_context_data), needs, product_decision,
          [certainty(unresolved), source([code]),
           note("Raven Student document embeds FeesReceivable; it is persisted verbatim as student.fees_receivable JSONB even though the target model owns fee data in the fees context (adapter: boundary re-homing) — blob stays for parity, target owner is `fees`")]),
statement(s(student_table, embeds, academics_context_data), needs, product_decision,
          [certainty(unresolved), source([code]),
           note("same re-homing class for Attendance → student.attendance JSONB; target owner is the academics/attendance context")]),

% --- persistence ---
statement(etl_module_students, persists, schema_autocommit_then_single_transaction, [certainty(medium), source([code]), mechanism("schema DDL committed immediately (autocommit); ALL upserts (orgs → insts → students) run inside ONE `with conn:` transaction — any row failure rolls back the entire data load"), ref("main:2033-2066")]),
statement(etl_module_students, persists, full_row_upsert_per_document, [certainty(medium), source([code]), mechanism("SELECT existence (for new/updated stats) then INSERT … ON CONFLICT (id) DO UPDATE SET <every column> — full overwrite including created_on/created_by from source; keyed by derived UUID"), ref("upsert_organization:1518-1605, upsert_institute:1633-1751, upsert_student:1846-1997")]),
statement(etl_module_students, validates, target_schema_before_load, [certainty(medium), source([code]), mechanism("assert_required_schema checks every required column exists AND datatype/udt matches against information_schema; raises RuntimeError on any gap"), on_invalid(error("Table public.<t> is missing required columns / has datatype mismatches")), ref("assert_required_schema:1271-1496")]),

% --- failure & reporting ---
statement(etl_module_students, on_invalid, any_exception_exit_1, [certainty(medium), source([code]), mechanism("single try/except around main: 'Migration failed: <exc>' to stderr, return 1; connection/session closed in finally"), ref("main:2138-2144")]),
statement(etl_module_students, creates, summary_json_artifact, [certainty(medium), source([code]), mechanism("validation/migration-summary-<yyyymmdd_hhmmss>.json (or --summary-json-path / MIGRATION_SUMMARY_JSON); disabled by --no-summary-json; contains source/target/run_stats/post_load_counts and optionally api_payload_validation"), ref("main:2086-2134, write_summary_json:223-228")]),
statement(etl_module_students, creates, api_payload_validation_block, [certainty(medium), source([code]), mechanism("re-queries PostgreSQL after load through 7 API-shaped payload builders (studentManage, coursewiseBreakup, sectionwiseBreakup, studentParentDetails, newAdmissions, studentDetails, dashboardSummary) over an ENROLLMENT_LATERAL jsonb join; disabled by --no-api-payload-validation"), ref("build_api_payload_validation:907-953")]),

% --- provenance / validation (reified) ---
statement(s(etl_module_students, is_a, verified_by_parity_audit), sourced_from, code, [ref("verify_raven_to_postgres.py domain 27")]),
statement(s(etl_module_students, creates, summary_json_artifact), validated_by, golden(etl_module_students), [note("pending capture; validated_against_legacy=false")])
```

---

## 2. Human view (SME reads this)

**Q: What does the students ETL module do?**
It reads the `Orgs`, `Institutes`, and `Students` collections straight from RavenDB over its HTTP query API, creates the three target tables (plus five enum types) if they don't exist, verifies the schema column-by-column, then upserts every document into PostgreSQL — organizations first, then institutes, then students — inside **one single transaction**, and finally writes a run summary JSON (with an optional API-shaped payload re-creation) into `validation/`.

- **Q: How does it page through RavenDB?**
  RQL `from "<Collection>" order by id()` with offset paging (`Start` advancing by the page size, default 500) until an empty page. Ordering by id makes paging deterministic.

  - **Q: What if the source changes while the migration runs?**
    *[UNRESOLVED]* Offset paging is only consistent if source writes are frozen for the migration window — the code's own comment says so. A live, mutating collection can silently skip or duplicate documents between pages; nothing detects it. → **product decision.**

- **Q: How does it decide the primary key of each row?**
  It extracts the **first UUID found** in a fallback chain (lowercased): for orgs `SourceOrgId → OrgId → Id → metadata @id`; for institutes the same pattern; for **students the order is different** — the Raven document UUID (`@metadata.@id`) wins, falling back to `Id → SourceStudentId → StudentId`. *[LOW]* Whether the student-first order is intentional is an **SME question**.

  - **Q: What if a document has no UUID anywhere in that chain?**
    *[UNRESOLVED]* It is **silently skipped** — not upserted, not counted as processed, not counted as failed. The "fetched vs processed" gap is visible only by comparing the two printed counts; exit code stays 0. → **product decision.**

- **Q: How is the business `student_id` (e.g. `23P001`) derived?**
  `SourceStudentId → StudentId →` the first enrollment carrying a `StudentId`. The Raven document UUID is explicitly **never** used as the business ID.

- **Q: How is `student.inst_id` set?**
  From the first enrollment's `InstId` — but only if that institute row **already exists** in the `institute` table at that moment (institutes are loaded first, which usually guarantees it).

  - **Q: What if the enrollment points at an institute that wasn't loaded?**
    *[UNRESOLVED]* `inst_id` is set to **NULL silently** — no warning, no error, no failure count. → **product decision.**

- **Q: What happens to a student's status if the source value is garbage?**
  *[UNRESOLVED]* It **defaults to `Active`** — for students, orgs, and institutes alike. There is a distinct `Unknown` enum value, but the fallback chain never reaches it on unparseable input. (The API re-encoder, in contrast, maps `-1` → `Unknown`.) → **product decision.**

- **Q: What lands in the `student` row?**
  44 columns: identity, name parts, gender/dob, emails/phones (both single and CSV variants), parents as both names and JSONB blobs, Aadhaar, UDID, PAN, plus **embedded JSONB documents** for `attendance`, `fees_receivable`, `enrollments`, `documents`, contacts, etc.

  - **Q: `fees_receivable` and `attendance` live inside the student row — shouldn't they belong to other modules?**
    *[UNRESOLVED]* Yes — this is the adapter's **boundary re-homing** class: the legacy Raven document embeds fee-receivable and attendance data; the target model assigns them to the `fees` and `academics` contexts respectively. They persist verbatim as JSONB blobs on `student` for parity. → **product decision** (target owner vs parity copy).

- **Q: Is the load restartable / idempotent?**
  Upserts are keyed by the derived UUID, so a re-run updates in place rather than duplicating. But the conflict clause overwrites **every** column, including `created_on`/`created_by` from the source document — *[LOW]* whether that's intended (source-of-truth wins) or should preserve first-seen audit values is an **SME question**.

- **Q: What does a failure look like?**
  Config problems fail fast with argparse errors. Any runtime failure (Raven unreachable, schema mismatch, one bad row) aborts: the schema DDL stays committed, the **entire data load rolls back**, `Migration failed: …` goes to stderr, and the process exits 1.

- **Q: What does a successful run leave behind?**
  Populated tables; post-load row counts; and `validation/migration-summary-<timestamp>.json` containing source/target config, run stats (processed vs new per domain), post-load counts, and — unless disabled — an `api_payload_validation` block that re-queries the migrated data through 7 API-shaped SQL builders (manage list, breakups, parents, admissions, details, dashboard) using a JSONB LATERAL join on enrollments.

  - **Q: What are those API payloads filtered by?**
    *[LOW]* Hard-coded demo baseline: `courseName "I"`, `section "A"`, `term "Annual"`. On a dataset without those values the block comes back with empty `Data` but the run still succeeds. → **SME question** (baseline should be configurable?).

---

## 3. Golden fixtures

| id | covers | source | status |
|---|---|---|---|
| `etl_module_students` | happy path: 1 org + 1 institute + 1 student (single enrollment, resolved `inst_id`) fetched, transformed, upserted; exit 0; summary JSON + stdout contract | authored-from-code (mappings, precedence chains, stdout lines, and summary shape lifted verbatim from the script) | **pending** capture against a live legacy run (RavenDB + PostgreSQL) for validation |

See `specs/golden/migration/etl_module_students.json`.

---

## 4. Open items

1. `[legacy-divergence]` **unparseable status defaults to `Active`** (student/org/institute) while the API re-encoder maps `-1` → `Unknown` — the layers disagree. — product decision.
2. `[legacy-divergence]` **offset paging over a live mutating source** can silently skip/duplicate documents; the code comment itself requires frozen source writes. — product decision.
3. `[legacy-divergence]` **documents with no derivable UUID are silently skipped** — never counted, exit stays 0. — product decision.
4. `[legacy-divergence]` **`student.inst_id` silently NULL** when the enrollment's institute was not loaded. — product decision.
5. `[legacy-divergence]` **boundary re-homing**: `fees_receivable` (→ fees context) and `attendance` (→ academics context) persist as JSONB blobs on `student`. — product decision (adapter-flagged class).
6. `[low]` **PK precedence asymmetry** — student is metadata-UUID-first, org/institute are source-field-first. Confirm intent with SME.
7. `[low]` **full-row overwrite includes `created_on`/`created_by`** on re-runs — confirm source-wins vs preserve-first-seen audit intent.
8. `[low]` **hard-coded API-payload baseline filters** (`courseName "I"`, `section "A"`, `term "Annual"`) — empty on other datasets, still exit 0. Confirm whether baseline should be configurable.
9. `[low]` **unused `deleted_students` counter** (initialized, never incremented) hints at a planned delete/reconciliation step that was never implemented. Confirm with SME whether deletes are in scope.
10. `[low]` **progress-banner numbering inconsistent** — `[1/5]`/`[2/5]` then `[3/6]`…`[6/6]`; harmless but breaks naive string-matching gates. Cosmetic.
11. `[todo]` **capture golden against a live legacy run** (reachable RavenDB + PostgreSQL) to set `validated_against_legacy: true`.
