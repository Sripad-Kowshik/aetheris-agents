# migration · api-verification — extracted spec (v0.1)

> **Status:** extraction from legacy code · **Confidence ceiling reached:** medium (code-only; no SME sign-off, no golden captured against a live legacy environment)
> **Legacy provenance:** gate contract in `agent_runbook.md` Step 4 (lines 124–146) + readiness probe `scripts/wait-for-api.sh`; realising behaviour read from the API the gates call: `student-fee-poc/dotnet/student-fee-poc/Program.cs`, `Db/Student/StudentQueries.cs`, `Db/Fee/FeeQueries.cs`, `Db/Fee/FeeTransactionQueries.cs`, `Db/Fee/FeeTransactionWriteQueries.cs`, `Models/FeeTransactionApiResponse.cs`; DDL constraints from `scripts/migrations/fees_ravendb_to_postgres_migrate.py`; side-effect check lives in `student-fee-poc-tests/DbWriteTests.cs` (runbook gate 5, not the curls)
> **Layers below:** (1) KB spine · (2) human view · (3) golden refs · (4) open items
>
> Source-priority note: the curl gates are the *contract*; the .NET minimal-API code is
> the *behaviour*. Per the adapter, code was read for what it does (response shapes,
> status codes, defaults, constraint absence) — not for what names suggest. The xUnit
> suite is used as inventory only (it owns the audit-trigger assertion).

---

## 1. KB spine

```kb
% --- gate contract ---
statement(api_verification, is_a, curl_gate_sequence, [certainty(medium), source([code]), mechanism("agent_runbook.md Step 4: three curl checks against http://localhost:5000 after services are up"), ref("agent_runbook.md:124-146")]),
statement(api_verification, validates, student_read_endpoint, [certainty(medium), source([code]), mechanism("curl GET /api/stu/student?limit=2 → criterion 'HTTP 200; valid JSON array returned'"), ref("agent_runbook.md:128-133")]),
statement(api_verification, validates, fee_tx_read_endpoint, [certainty(medium), source([code]), mechanism("curl GET /api/feeTx?limit=2 → criterion 'HTTP 200 with JSON fee transaction records'"), ref("agent_runbook.md:135-139")]),
statement(api_verification, validates, fee_tx_write_endpoint, [certainty(medium), source([code]), mechanism("curl POST /api/feeTx with hard-coded demo body → criterion 'HTTP 200 or 201 with created transaction JSON'"), ref("agent_runbook.md:140-146")]),
statement(api_verification, depends_on, services_ready, [certainty(medium), source([code]), mechanism("gate 1 health probe: curl /health → 200 {status:Healthy, database:Connected}; bounded readiness helper wait-for-api.sh honours API_PORT from .env (30 attempts × 2s) but is referenced by no gate step"), ref("agent_runbook.md:86-90, wait-for-api.sh")]),

% --- realising API: health ---
statement(api_health_endpoint, transitions_to, healthy_or_unhealthy, [certainty(medium), source([code]), mechanism("SELECT 1 ok → 200 {status:'Healthy', database:'Connected', timestamp:UtcNow}; any DB error → 503 {status:'Unhealthy', database:'Disconnected', error}"), ref("Program.cs:44-58")]),

% --- realising API: student read ---
statement(student_read_endpoint, is_a, campustrack_parity_read, [certainty(medium), source([code]), mechanism("GET /api/stu/student?activeStudentsOnly=false&todaysAbsenteesOnly=false&limit=50; builds each row in SQL via jsonb_build_object then recursively camelCases keys in C# (special-cases photoURL, instId, studentId, courseId, virtualId, dob, pan, doa)"), ref("Program.cs:61-76, StudentQueries.cs:9-156")]),
statement(student_read_endpoint, creates, data_envelope_response, [certainty(medium), source([code]), mechanism("HTTP 200 with {\"data\": [ <student>… ]} — an OBJECT wrapping the array, each student ~30 keys"), ref("StudentQueries.cs:74-95")]),
statement(student_read_endpoint, projects, first_enrollment_only, [certainty(medium), source([code]), mechanism("LEFT JOIN LATERAL … LIMIT 1 over s.enrollments JSONB — course/term/section/rollNo/admission fields always come from enrollment[0]; multi-enrollment students surface only their first"), ref("StudentQueries.cs:62-68")]),
statement(student_read_endpoint, transforms, status_to_legacy_codes, [certainty(medium), source([code]), mechanism("Active→1, Disabled→99, else -1 (plus statusAsString text)"), ref("StudentQueries.cs:40-41")]),
statement(student_read_endpoint, has_value_set, synthetic_payload_defaults, [certainty(medium), source([code]), has_value_set(["attendance: 'Present' when source blob lacks Status", "attendanceList: 8×'Present' when absent", "domicile: {caste:null, state:null, country:'India', motherTongue:null}", "iep: {terms:[]}", "doa: '0001-01-01T00:00:00'", "rollNo: 0 when no RollNo/RollNoAsInt"]), ref("StudentQueries.cs:48-59")]),
statement(s(student_read_endpoint, accepts, todays_absentees_only_param), needs, product_decision,
          [certainty(unresolved), source([code]),
           note("the todaysAbsenteesOnly query parameter is bound but never referenced in the SQL — a silent no-op filter that always returns the same rows; activeStudentsOnly IS honoured")]),

% --- realising API: fee-tx read ---
statement(fee_tx_read_endpoint, is_a, campustrack_parity_read, [certainty(medium), source([code]), mechanism("GET /api/feeTx?id=&limit=10; loads the WHOLE fee table as a lookup map, then joins fee_transaction→student→first enrollment, newest first (tx_date DESC NULLS LAST, tx_no DESC)"), ref("FeeTransactionQueries.cs:9-77")]),
statement(fee_tx_read_endpoint, creates, data_envelope_response, [certainty(medium), source([code]), mechanism("HTTP 200 {\"data\":[<tx>…]}, tx DTO with 20 camelCase fields (JsonPropertyName-pinned)"), ref("FeeTransactionApiResponse.cs:5-31")]),
statement(fee_tx_read_endpoint, transforms, status_to_legacy_codes, [certainty(medium), source([code]), mechanism("Active→1, Disabled→99, else 0"), ref("FeeTransactionQueries.cs:58-62")]),
statement(fee_tx_read_endpoint, enriches, installments_from_fee_lookup, [certainty(medium), source([code]), mechanism("per installment: feeName/feeDisplayText/description fall back to the fee table by FeeId; installmentId from InstallmentId or Id; dueDate fraction stripped; amount default 0"), ref("FeeTransactionQueries.cs:110-177")]),
statement(fee_tx_read_endpoint, has_value_set, synthetic_payload_defaults, [certainty(medium), source([code]), has_value_set(["dueDate: '2015-08-20T00:00:00' when source lacks DueDate", "feeAdjustment.name: 'Adj Fee' / description: 'Extra Amount' when blob empty", "finesPaid/discounts: empty arrays when blobs empty"]), ref("FeeTransactionQueries.cs:155-204")]),

% --- realising API: fee-tx write ---
statement(fee_tx_write_endpoint, creates, fee_transaction_row, [certainty(medium), source([code]), mechanism("POST /api/feeTx body {studentId?, amount, status?, feeId?, refNo?, paidBy='Cash'}; INSERT with id=Guid.NewGuid(), txNo='TXN-<yyyyMMddHHmmssfff>' (UTC, ms), txDate=UtcNow, status default 'Active' cast to fee_tx_status_enum; installments_paid = ONE synthetic installment {FeeId, Amount, DueDate=UtcNow-no-fraction}; fines/discounts/adjustment forced empty"), ref("FeeTransactionWriteQueries.cs:27-106")]),
statement(fee_tx_write_endpoint, transitions_to, created_201, [certainty(medium), source([code]), mechanism("Results.Created → HTTP 201 with Location /api/feeTx?id=<newId> and body {id, txNo, txDate, studentId, amount, status, message:'Fee transaction inserted successfully.'} — satisfies the gate's '200 or 201'"), ref("Program.cs:97-98, FeeTransactionWriteQueries.cs:97-105")]),
statement(fee_tx_write_endpoint, on_invalid, any_exception_400, [certainty(medium), source([code]), mechanism("single catch → 400 {error:<message>} (e.g. invalid status enum string); success response never distinguishes partial effects"), ref("Program.cs:100-103")]),
statement(s(fee_tx_write_endpoint, accepts, nonexistent_student_or_fee_id), needs, product_decision,
          [certainty(unresolved), source([code]),
           note("fee_transaction.student_id has NO foreign key (fees ETL DDL) and feeId is only embedded in the installments JSONB — the POST silently persists dangling references for any well-formed UUID; the write gate therefore cannot detect a wrong dataset, it just succeeds")]),
statement(s(fee_tx_write_endpoint, generates, collision_prone_tx_no), needs, product_decision,
          [certainty(unresolved), source([code]),
           note("tx_no 'TXN-<utc-ms>' has NO unique constraint and no uniqueness check — two inserts within the same millisecond produce duplicate tx_no silently")]),
statement(s(fee_tx_write_endpoint, creates, synthetic_installments_paid), needs, product_decision,
          [certainty(unresolved), source([code]),
           note("the inserted installments_paid is a single synthetic row {FeeId, Amount, DueDate=now} regardless of the fee's real installment plan — audit trail diverges from the product's per-installment semantics")]),

% --- side effect ownership ---
statement(api_verification, delegates, audit_trigger_check, [certainty(medium), source([code]), note("the curls do NOT verify the fee_transaction_audit side effect; that assertion lives in xUnit DbWriteTests (runbook gate 5), triggered by trg_fee_transaction_audit from 02_trigger.sql"), ref("agent_runbook.md:150-158, DbWriteTests.cs")]),

% --- divergences already reified at the gate level (cross-refs) ---
statement(s(api_verification, requires, hard_coded_demo_ids), needs, product_decision,
          [certainty(unresolved), source([code]),
           note("POST body pins studentId cc93c106-… and feeId a7e2851c-… from one specific dataset (see specs/migration/runbook-gates.md open item 3); combined with no-FK semantics the gate passes even when the ids dangle — masking the dataset coupling")]),
statement(s(api_verification, requires, hard_coded_port_5000), needs, product_decision,
          [certainty(unresolved), source([code]),
           note("runbook curls hard-code localhost:5000; API_PORT is configurable in .env and honoured by wait-for-api.sh but not by the gate commands (see specs/migration/runbook-gates.md open item 4)")]),
statement(s(api_verification, validates, json_array_wording), needs, product_decision,
          [certainty(unresolved), source([code]), contradicts(code),
           note("gate criterion says 'valid JSON array returned' but BOTH read endpoints return a {\"data\":[…]} OBJECT envelope, never a bare JSON array — the criterion as literally worded can never be satisfied; it evidently means 'JSON containing an array'")]),

% --- provenance / validation (reified) ---
statement(s(api_verification, is_a, gate_4_of_runbook), sourced_from, code, [ref("agent_runbook.md:28")]),
statement(s(api_verification, validates, fee_tx_write_endpoint), validated_by, golden(api_verification), [note("pending capture; validated_against_legacy=false")])
```

---

## 2. Human view (SME reads this)

**Q: What does API verification do?**
It is runbook gate 4: three curl checks proving the migrated data is servable and writable through the parity REST API — read students, read fee transactions, insert a fee transaction — plus the `/health` probe from gate 1 that establishes readiness. It exercises the ASP.NET Core minimal API in front of the migrated PostgreSQL tables.

- **Q: What do the read endpoints actually return?**
  Both wrap their array in an object: `{"data": [ … ]}` — never a bare JSON array.

  - **Q: The gate criterion says "valid JSON array returned". Does it?**
    *[UNRESOLVED]* Not literally — the payload is an object with a `data` key. The criterion evidently means "JSON containing an array", but as worded it can never be satisfied. → **product decision** (fix the criterion wording or the envelope).

  - **Q: A student has several enrollments — which one does the API show?**
    Only the **first** (a `LATERAL … LIMIT 1` over the enrollments JSONB). Course/term/section/roll number all come from enrollment[0]. Status maps to legacy codes (Active→1, Disabled→99) alongside a text form, and several fields have synthetic defaults (attendance "Present", a domicile template with `country: "India"`, DOA `0001-01-01…`).

    - **Q: What does `todaysAbsenteesOnly=true` do?**
      *[UNRESOLVED]* **Nothing** — the parameter is bound but never used in the query; the response is identical either way. (`activeStudentsOnly` *is* honoured.) → **product decision.**

- **Q: What does reading fee transactions add?**
  Rows joined with the student (and the student's first enrollment), newest first, with installment entries enriched from a full `fee`-table lookup (name / display text / installment description by `FeeId`). Missing pieces get hard-coded defaults — notably a `dueDate` of **`2015-08-20T00:00:00`** and fee-adjustment labels "Adj Fee" / "Extra Amount".

  - **Q: Are those defaults intentional?**
    *[LOW]* They exist to mimic legacy CampusTrack payload shapes (the whole endpoint family is a parity exercise), but the magic 2015 date and template labels are hard-coded. Confirm with an **SME** that they mirror the product payloads.

- **Q: What does the write gate actually create?**
  A `fee_transaction` row with a fresh GUID, `tx_no = TXN-<UTC timestamp to milliseconds>`, status defaulting to `Active`, and **one synthetic installment** `{FeeId, Amount, DueDate=now}` — regardless of the fee's real installment plan. Response is **HTTP 201** (Created, with a `Location` header) and a body carrying the new id/txNo and the fixed message "Fee transaction inserted successfully." Any exception becomes **400** `{error}`.

  - **Q: What if the posted studentId doesn't exist?**
    *[UNRESOLVED]* **It still succeeds** — `fee_transaction.student_id` has no foreign key, and `feeId` is only embedded in the installments JSONB. Dangling references are persisted silently. This also means the write gate **cannot detect a wrong dataset** — it passes even with bogus ids (which is exactly why the gate's hard-coded demo UUIDs are doubly risky; see the runbook-gates spec). → **product decision.**

  - **Q: Can two transactions get the same `tx_no`?**
    *[UNRESOLVED]* Yes — `TXN-<millisecond>` with no unique constraint; same-millisecond inserts collide silently. → **product decision.**

- **Q: Who checks the audit trigger?**
  Not the curls. The `fee_transaction_audit` row written by `trg_fee_transaction_audit` is asserted by the xUnit write tests in runbook gate 5. The API gate proves reachability + CRUD, the test gate proves the side effect.

- **Q: Where do the curls point?**
  `http://localhost:5000` hard-coded. *[UNRESOLVED]* `API_PORT` is configurable in `.env` and the companion `wait-for-api.sh` honours it — the gate commands don't. → **product decision.**

---

## 3. Golden fixtures

| id | covers | source | status |
|---|---|---|---|
| `api_verification` | gate 4 happy path: health 200; student read 200 `{"data":[…]}`; fee-tx read 200 `{"data":[…]}` (newest first); POST 201 Created with txNo/Location/message contract and a readable follow-up record | authored-from-code (response shapes, defaults, status codes, and messages lifted verbatim from the .NET sources; gate commands from the runbook) | **pending** capture against a live legacy run for validation |

See `specs/golden/migration/api_verification.json`.

---

## 4. Open items

1. `[legacy-divergence]` **gate criterion wording** — "valid JSON array returned" vs. actual `{"data":[…]}` object envelope on both read endpoints; the criterion is unsatisfiable as literally worded. — product decision.
2. `[legacy-divergence]` **POST accepts non-existent studentId/feeId silently** — no FK on `fee_transaction.student_id`, feeId only embedded in JSONB; dangling references persist and the gate cannot detect a wrong dataset (compounds the hard-coded demo UUIDs). — product decision.
3. `[legacy-divergence]` **`tx_no` collision** — `TXN-<utc-ms>` with no unique constraint; same-millisecond inserts duplicate silently. — product decision.
4. `[legacy-divergence]` **`todaysAbsenteesOnly` is a silent no-op** — bound but unused in SQL (unlike `activeStudentsOnly`). — product decision.
5. `[legacy-divergence]` **synthetic write payload** — POST always writes a single fabricated installment (`{FeeId, Amount, DueDate=now}`) instead of the fee's real plan. — product decision.
6. `[low]` **hard-coded read defaults** — dueDate `2015-08-20T00:00:00`, feeAdjustment "Adj Fee"/"Extra Amount", attendance "Present" + 8×"Present" list, domicile template `country:"India"`, iep `{terms:[]}` — confirm they mirror legacy CampusTrack payloads. — SME question.
7. `[low]` **first-enrollment-only projection** — multi-enrollment students surface only enrollment[0]; confirm parity intent. — SME question.
8. `[low]` **hard-coded `localhost:5000`** in gate commands vs configurable `API_PORT` honoured by `wait-for-api.sh` (cross-ref: runbook-gates open item 4). — product decision.
9. `[todo]` **capture golden against a live legacy run** (API + migrated dataset) to set `validated_against_legacy: true`.
