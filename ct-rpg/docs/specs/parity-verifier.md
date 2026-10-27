# migration · parity-verifier — extracted spec (v0.1)

> **Status:** extraction from legacy code · **Confidence ceiling reached:** medium (code-only; no SME sign-off, no golden captured against a live legacy environment)
> **Legacy provenance:** `scripts/verify_raven_to_postgres.py` (whole file, 1,940 lines); invoked by the agent runbook as gate 3 (`docker compose run --rm --entrypoint python rpg-migrator verify_raven_to_postgres.py`, relies on container `WORKDIR /app/scripts`); counterpart of `specs/migration/etl-module-students.md` whose outputs it audits
> **Layers below:** (1) KB spine · (2) human view · (3) golden refs · (4) open items
>
> Source-priority note: code-first. The 42 domain specs embedded in `get_all_domain_specs()`
> were machine-counted (42 pairs, all `is_core: True`, 621 explicit field tuples) rather
> than trusted from the file-header prose. No SME available ⇒ nothing exceeds `medium`.

---

## 1. KB spine

```kb
% --- entity / scope ---
statement(parity_verifier, is_a, read_only_parity_auditor, [certainty(medium), source([code]), note("fetches both sides and compares — never writes to RavenDB or PostgreSQL (except rollback on per-domain errors)"), mechanism("python CLI verify_raven_to_postgres.py"), ref("verify_raven_to_postgres.py:724-891")]),
statement(parity_verifier, has_attribute, domain_registry, [type(ordered_list), has_value_set(42_collection_table_pairs), certainty(medium), source([code]), note("42 RavenDB collections ↔ PostgreSQL tables; every pair carries: domain, collection, table, key_fn, explicit field list (621 tuples total), is_core flag"), ref("get_all_domain_specs:898-1741")]),

% --- configuration contract ---
statement(parity_verifier, depends_on, env_resolution_order, [certainty(medium), source([code]), mechanism(".env tried at <script>/../ → <script>/ → cwd; pre-set env vars always win (same rule as ETL/orchestrator)"), ref("VerificationEngine.__init__:604-625, main:1744-1752")]),
statement(parity_verifier, accepts, cli_overrides, [certainty(medium), source([code]), mechanism("--raven-url/--raven-db/--raven-cert-*/--raven-insecure/--pg-host/--pg-port/--pg-db/--pg-user/--pg-password/--module/--core-only/--summary-json-path/--no-summary-json"), ref("main:1754-1794")]),
statement(s(parity_verifier, depends_on, pg_connection_defaults), needs, product_decision,
          [certainty(unresolved), source([code]),
           note("when env/CLI are missing, PG config silently defaults to localhost:5432/rpg/postgres with an EMPTY password — unlike the ETL module, which hard-fails on missing config; the verifier can happily audit the WRONG database and still print a results table")]),

% --- extraction (its own view of RavenDB) ---
statement(parity_verifier, reads, collections_via_raven_query_api, [certainty(medium), source([code]), mechanism("POST /databases/{db}/queries, RQL `from '<Collection>'` (single-quoted, NO order-by), offset paging Start += len, PageSize = 1000 (hard-coded), timeout 60s"), ref("fetch_raven_collection:695-722")]),
statement(s(parity_verifier, reads, collections_unordered), needs, product_decision,
          [certainty(unresolved), source([code]), contradicts(code),
           note("the ETL pages with `order by id()` for determinism; the verifier pages WITHOUT any ordering — offset paging over an unordered RQL on a live/mutating source can skip or duplicate documents, so the audit itself may miss records and nothing detects it (the parity gate is only as trustworthy as this paging)")]),

% --- identity derivation ---
statement(parity_verifier, identifies, raven_documents_by_first_uuid_or_metaid, [certainty(medium), source([code]), mechanism("extract_standard_id: metadata @id UUID → Id UUID → metadata @id string → Id string (lowercased); students use extract_student_id: metadata UUID → Id → SourceStudentId → StudentId UUIDs — matches the ETL's derivation, including the student-first asymmetry"), ref("extract_standard_id:546-559, extract_student_id:561-571")]),
statement(parity_verifier, identifies, pg_rows_by_lowercase_id, [certainty(medium), source([code]), mechanism("SELECT * FROM <table>; map keyed by str(id).lower()"), ref("verify_domain:755-821")]),

% --- comparison semantics ---
statement(parity_verifier, audits, declared_fields_plus_auto_expansion, [certainty(medium), source([code]), mechanism("starts from the domain's explicit field list, then auto-expands: every Raven key (except @metadata, Id) is camel→snake-cased and, IF a same-named PG column exists and isn't already covered and isn't modified_on, appended with an optional per-table transform (e.g. applications enums, users uuid-columns, exam id-columns)"), ref("verify_domain:773-817")]),
statement(parity_verifier, validates, values_via_normalization, [certainty(medium), source([code]), mechanism("normalize_val: empty string/list/dict → None (absent == empty); datetime-like strings (heuristic: len≥19, T-or-space, leading digits) → UTC-seconds ISO with Z; UUID-looking substrings extracted; numbers rounded to 4 decimals; dicts/lists JSON-dumped sorted-keys after recursive None-stripping"), ref("normalize_val:104-136, normalize_datetime:61-101")]),
statement(parity_verifier, retains, skip_rules, [certainty(medium), source([code]), has_value_set(["modified_on always skipped (PG trigger rewrites it)", "users.password/salt/otp/otp_validity/password_reset_on/password_changed_on never audited", "virtual_id no-transform compared only when present in source"]), note("secret columns are deliberately outside the parity contract"), ref("verify_domain:801-811, 839-856")]),
statement(s(parity_verifier, has_attribute, silent_unmapped_raven_fields), needs, sme_input,
          [certainty(low), source([code]),
           note("Raven keys with NO same-named PG column are silently unaudited — there is no 'field in source, absent in target' report; auto-expansion only checks columns PG already has")]),

% --- verdicts ---
statement(parity_verifier, transitions_to, per_domain_status, [certainty(medium), source([code]), has_value_set([PASS, FAIL, MISSING_TABLE, ERROR]), mechanism("PASS iff raven_count == pg_count AND missing_in_pg empty AND field_mismatches == 0; missing table → MISSING_TABLE; any exception → ERROR with message and the audit continues to the next domain"), ref("verify_domain:762-771, 878-889")]),
statement(s(parity_verifier, transitions_to, extra_in_pg_derived_not_checked), needs, sme_input,
          [certainty(low), source([code]),
           note("extra_in_pg is recorded but never directly asserted; PASS holds only because 'counts equal AND missing==0' arithmetically forces extra==0 — if the count-equality clause were relaxed, target-only rows would pass silently. Confirm the invariant is intended as the guard")]),

% --- reporting ---
statement(parity_verifier, creates, summary_table_stdout, [certainty(medium), source([code]), mechanism("fixed-width table Domain|Collection|PG Table|RavenDB|PG|Matched|Status; failing rows append error/missing-IDs(first 3)/sample mismatches(first 3); totals row 'TOTAL AUDITED (N TABLES)'"), ref("main:1857-1888")]),
statement(parity_verifier, creates, parity_report_artifact, [certainty(medium), source([code]), mechanism("validation/exhaustive-parity-report-<yyyymmdd_hhmmss>.json (or --summary-json-path / VERIFICATION_SUMMARY_JSON; disabled by --no-summary-json); payload: timestamp, totals, overall_status, per-pair results with sample_mismatches"), ref("main:1890-1930")]),
statement(parity_verifier, transitions_to, exit_code, [certainty(medium), source([code]), note("exit 0 iff every selected pair PASSed; else '[FAILURE] DATA PARITY ISSUES DETECTED' + exit 1; PG connect failure → '[!] Critical Error' + exit 1"), ref("main:1817-1821, 1932-1937")]),

% --- selection ---
statement(parity_verifier, accepts, module_filter, [certainty(medium), source([code]), mechanism("--module matches table, collection, domain (case-insensitive) OR table with underscores stripped; --core-only filters is_core specs; NOTE --all flag exists but is never read by the filter logic (default True is decorative)"), ref("main:1823-1838")]),
statement(s(parity_verifier, has_attribute, core_only_no_op), needs, product_decision,
          [certainty(unresolved), source([code]), contradicts(code),
           note("header prose claims '9 core domains with 177 deep field audits / 33 auxiliary', but ALL 42 specs are marked is_core:True and the registry holds 621 explicit field tuples — '--core-only' therefore audits all 42 pairs (a no-op) and the 9/33/177 narrative is stale")]),

% --- security-relevant mechanism note ---
statement(s(parity_verifier, depends_on, pkcs12_fallback_temp_key), needs, product_decision,
          [certainty(unresolved), source([code]),
           note("cert handling: Pkcs12Adapter preferred; on ImportError it falls back to manually extracting key+certs from the .pfx via cryptography into a temp .pem (delete=False, never removed) and mounting it as session.cert — private key material left on disk; if parsing fails it prints a warning and proceeds WITHOUT client auth (all domains then error → FAIL exit 1, safe verdict but lingering key file)")]),

% --- provenance / validation (reified) ---
statement(s(parity_verifier, is_a, gate_3_of_runbook), sourced_from, code, [ref("agent_runbook.md:28")]),
statement(s(parity_verifier, creates, parity_report_artifact), validated_by, golden(parity_verifier), [note("pending capture; validated_against_legacy=false")])
```

---

## 2. Human view (SME reads this)

**Q: What does the parity verifier do?**
It is a read-only auditor: for each of the 42 collection↔table pairs it re-fetches the RavenDB collection, reads the whole PostgreSQL table, matches rows by derived ID, then compares every auditable field value, and finally prints a summary table, writes a JSON report to `validation/`, and exits 0 only if every pair passed.

- **Q: How does it decide "pass" for one pair?**
  Same record counts on both sides, zero Raven IDs missing in PG, and zero field mismatches on matched rows. Statuses: `PASS`, `FAIL`, `MISSING_TABLE` (target table absent), or `ERROR` (any exception — recorded, and the audit moves on to the next pair).

  - **Q: What about rows that exist only in PostgreSQL?**
    *[LOW]* They're tallied as `extra_in_pg` but never directly asserted — the pass condition ("counts equal AND nothing missing") only catches them arithmetically. If that count-equality guard ever changed, target-only rows would slip through. → **SME question.**

- **Q: Which fields does it compare?**
  Each domain declares its core mapping (621 field tuples across the 42 pairs), then the engine **auto-expands**: any other Raven key that maps to an existing same-named PG column (camelCase→snake_case) is added too — that's how "all fields across all tables" is claimed. Some columns are deliberately skipped: `modified_on` (a PG trigger rewrites it), and for `users` the secret columns (password, salt, OTP fields) are never audited.

  - **Q: What about Raven fields with no PG column?**
    *[LOW]* Silently unaudited — there's no "in source, absent in target" report. → **SME question.**

- **Q: How are values compared?**
  After per-field transforms (enum strings, UUID extraction, business `student_id` re-derivation), both sides go through a normalizer: empty string/list/dict ≈ absent (None), timestamps collapse to UTC-seconds ISO with `Z`, UUIDs are extracted from longer strings, numbers round to 4 decimals, and JSONB structures compare as sorted-key JSON. Two `None`s count as a match.

- **Q: How does it page RavenDB?**
  Offset paging (`Start`, `PageSize` 1000) on `from '<Collection>'` — **without any ordering**, unlike the ETL's `order by id()`.

  - **Q: Does that matter?**
    *[UNRESOLVED]* Yes: on a live source, unordered offset paging can skip or duplicate documents between pages, so the audit can miss records with no signal. The parity gate is only as trustworthy as this paging. → **product decision.**

- **Q: What configuration does it need?**
  Same env story as the ETL (`RAVEN_*`, `PG_*`, `.env` resolution, pre-set env wins), plus CLI overrides, `--module` filtering, and `--summary-json-path`.

  - **Q: What if the PG config is missing entirely?**
    *[UNRESOLVED]* It **silently defaults** to `localhost:5432/rpg` user `postgres` with an empty password (the ETL hard-fails instead) — it can audit the wrong database and still produce a plausible-looking table. → **product decision.**

- **Q: What does a failing audit look like?**
  Non-passing rows print their error, up to 3 missing IDs, and up to 3 sample field mismatches (`Raven(field) vs PG(field)` with truncated values). Exit code 1, `[FAILURE] DATA PARITY ISSUES DETECTED.` The detailed JSON report always lands unless `--no-summary-json`.

- **Q: Anything security-relevant?**
  Two things: user secret columns are (sensibly) outside the audit; but the PKCS#12 fallback writes the extracted **private key to a temp `.pem` that is never deleted**. → **product decision** (security review).

---

## 3. Golden fixtures

| id | covers | source | status |
|---|---|---|---|
| `parity_verifier` | `--module students` happy path: 1-org/1-institute/1-student dataset verified; per-pair PASS row, totals line, JSON artifact `overall_status: PASS`, exit 0 | authored-from-code (stdout strings, status logic, and report shape lifted verbatim from the script; dataset mirrors `etl_module_students` fixture) | **pending** capture against a live legacy run for validation |

See `specs/golden/migration/parity_verifier.json`.

---

## 4. Open items

1. `[legacy-divergence]` **`--core-only` is a no-op** — all 42 specs carry `is_core: True`; the "9 core domains with 177 attributes / 33 auxiliary" prose (file header + docstring) is stale (actual: 42 pairs, 621 explicit field tuples). — product decision/doc fix.
2. `[legacy-divergence]` **unordered offset paging** (`from 'X'` without `order by id()`, unlike the ETL) — audit can skip/duplicate records on a live source undetected. — product decision.
3. `[legacy-divergence]` **silent PG connection defaults** (localhost:5432/rpg, empty password) instead of hard failure — can audit the wrong database. — product decision.
4. `[legacy-divergence]` **PKCS#12 fallback leaves the extracted private key in a temp `.pem`** (delete=False, never cleaned); on cert-parse failure it proceeds unauthenticated (safe FAIL verdict, lingering key file). — product decision / security review.
5. `[low]` **`extra_in_pg` guarded only arithmetically** (count equality + missing==0); confirm the invariant is the intended protection against target-only rows. — SME question.
6. `[low]` **duplicated transform logic** — the verifier re-implements every enum/status mapping (`parse_*` helpers) instead of sharing code with the ETL module; drift between the two is undetected. — SME/refactor note.
7. `[low]` **users secret columns permanently outside the audit** (password/salt/OTP fields skipped in auto-expansion) — confirm the exclusion list is the intended contract.
8. `[low]` **unmapped Raven fields silently unaudited** — no "present in source, absent in target column" report; confirm intended.
9. `[todo]` **capture golden against a live legacy run** (reachable RavenDB + PostgreSQL with the `etl_module_students` dataset loaded) to set `validated_against_legacy: true`.
