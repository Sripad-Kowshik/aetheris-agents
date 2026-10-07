# Backlog — 2026-06

> **The open-row index.** One section per open row: its heading and a field list, nothing
> else. Terminal rows live in [`backlog-2026-06-closed.md`](backlog-2026-06-closed.md). The id
> is the address: `scripts/backlog_status.py`, `drift_check.py`'s `backlog_resolution` and the
> harness sprint's KNOWN_RED resolver all read the union of the two files.
>
> **Row fields are the only status surface.** GitHub Issues carry none (arbiter ruling R1,
> 2026-09-14).
>
> **Evidence path: `docs/evidence/<ID>.md`**, derived from the id; no index lists the files.
> Each holds the row's body verbatim, with corrections and later evidence appended below it.
>
> **Fields, in order:** `state` · `type` · `area` · `priority · size` · `blocked-by / trigger`
> (optional) · `evidence` · `done-when` · `disposition` (terminal rows only).
> `python3 scripts/backlog_status.py --check` enforces the shape.
>
> **`state`** ∈ `open`, `committed`, `ready`, `blocked`, `triggered`, `verifying`, `done`.
> **`disposition`** ∈ `fixed`, `verified`, `accepted-risk`, `evidence-only`, `superseded`,
> `rejected`.
>
> **Closing an index row** (ruling 2026-09-14, reverses BL-252 D7 going forward): set
> `state: done`, add `disposition`, move the field list to `backlog-2026-06-closed.md`; the
> evidence file stays. BL-252 itself predates this rule and is left as committed.
>
> **Every open row states its `done-when`.** A non-terminal row whose `done-when` reads
> `not stated` fails `--check`.
>
> **`done-when` length.** The backlog index states the closure test in at most 240 UTF-8
> bytes. Supporting cases, rationale, history, and procedural detail belong in the row's
> evidence file. `backlog_status.py --check` enforces it on non-terminal rows (2026-09-21).

---

## Bugs

> **`BUG-` is a distinct id space from `BL-`, and the split is by kind, not by
> priority.** A `BUG-` row is a **defect with a root cause** — something that
> behaved wrongly, was diagnosed, and whose row records the diagnosis. A `BL-` row
> is **enhancement or hardening** — work that makes something better or safer,
> including defects filed as opportunities rather than as diagnosed faults. Both
> spaces are parsed by `scripts/backlog_status.py` via the same union, and
> `drift_check.py`'s `backlog_resolution` resolves `BL-` references only; the id
> remains the address, and
> nothing about the prefix changes where a row may live or when it closes.
> `[Declared 2026-09-07 with BUG-001, the first row in this space. The convention
> had been proposed and used in filenames — the ticket was `bug-001`, its reviews
> are `docs/reviews/bug-001-review*.md` — with no row anchoring it, which is the
> shape BL-162 names: a rule alive only in the artifacts that assume it.]`
> [Corrected 2026-09-14, BL-252: this sentence said both spaces were read by both readers.
> When written, both parsed `BL-` headings only; `backlog_status.py` reads `BUG-` since `995b4d0`.]

### BUG-001 — the Drive upload step ignored the requested month and uploaded every archived month into it
- state: verifying
- type: defect
- area: aetheris-agents
- priority: high · size: S
- evidence: docs/evidence/BUG-001.md
- done-when: The next live upload for a month that has **prior months present in `payslip/output/`** both: 1. completes inside the step timeout, and 2. leaves the destination period folder containing **only that month's files**.

---

## Harness (aetheris/)

### BL-024 — Fork lineage queries (`fork_event_id` / "list forks of run X")
- state: open
- type: not stated
- area: Harness
- priority: low · size: M
- evidence: docs/evidence/BL-024.md
- done-when: a lineage query exists that composes with `caused_by`, handles both provenance shapes, and has an e2e covering the null-`fork_step` case.

---

### BL-026 — Verify: divergence report names no first diverging event
- state: triggered
- type: not stated
- area: Harness
- priority: low — **PARKED ON TRIGGER** · size: S
- blocked-by / trigger: the first `verify` run against a multi-agent / orb trajectory
- evidence: docs/evidence/BL-026.md
- done-when: a failing verify names the first diverging event/step explicitly, and the trigger condition above has actually occurred.

---

### BL-032 — WAL connection-lifecycle follow-ups
- state: open
- type: not stated
- area: Harness
- priority: low · size: M
- evidence: docs/evidence/BL-032.md
- done-when: a decision is recorded — either WAL is made deterministic via connection lifecycle (with the three items addressed), or opportunistic WAL is ratified as the permanent design and documented as such.

---

### BL-033 — Remove `:fork` from the `RunConfig` mode union
- state: open
- type: not stated
- area: Harness
- priority: low · size: S
- evidence: docs/evidence/BL-033.md
- done-when: `:fork` is removed from the union, or a reason to keep it is recorded on this entry.

---

### BL-282 — `run_command` confinement: `pivot_root` in the worker's mount namespace plus a shared confinement crate
- state: open
- type: hardening
- area: harness — worker sandbox / exec server
- priority: high · size: M–L
- evidence: docs/evidence/BL-282.md
- done-when: `run_command` cannot reach a path outside the sandbox root by `working_dir`, argument or PATH lookup; the exec server resolves through the shared crate; a test asserts `cat /etc/hosts` and an absolute out-of-root `working_dir` are refused.

---

### BL-283 — the harness runbook does not point at the Rig-side playground setup
- state: open
- type: documentation
- area: harness — runbook.md
- priority: low · size: XS
- evidence: docs/evidence/BL-283.md
- done-when: the harness runbook (`docs/aetheris/runbook.md`) points at the Rig-side playground setup in `docs/rig/runbook.md`.

---


---

## Rig (aetheris-agents/rig/)

### BL-006 — Document `stop_reason` when first observed
- state: triggered
- type: not stated
- area: Rig
- priority: tracked (event-triggered, not scheduled) · size: S
- blocked-by / trigger: when drift_check emits `INFO payload_fields: llm_responded.stop_reason in DB events but not listed in specs.md §6`
- evidence: docs/evidence/BL-006.md
- done-when: the INFO fires once and the field is promoted.

---

### BL-023 — Retry parity for hosted-provider adapters: 429 handling
- state: triggered
- type: not stated
- area: Rig
- priority: answered-and-parked (event-triggered, not scheduled) · size: S
- blocked-by / trigger: an observed 429 from OpenRouter in a real run's trajectory
- evidence: docs/evidence/BL-023.md
- done-when: the question is answered and recorded here.

---

### BL-035 — Extract `formatCost` / `formatTokens` to `src/lib/format.ts`
- state: open
- type: not stated
- area: Rig
- priority: low · size: XS
- evidence: docs/evidence/BL-035.md
- done-when: one `src/lib/format.ts` exports both helpers; all four sites import them; no local copies remain; `bunx tsc -b && bun run lint` green.

---

### BL-054 — The twelfth `requires_worker` failure is a load-sensitive flake with no stable identity
- state: committed
- type: not stated
- area: Harness
- priority: low · size: XS–S
- evidence: docs/evidence/BL-054.md
- done-when: the fixed-ms windows in `run_helpers_timeout_test.exs` poll for the state transition, or the tests are tagged so a loaded full-suite run cannot flake them; and BL-050's race is settled.

---

### BL-052 — drift_check check 9: ghost-struct arm is scoped to `commands/*.rs`
- state: open
- type: not stated
- area: Rig
- priority: low · size: XS
- evidence: docs/evidence/BL-052.md
- done-when: the source scan covers `src-tauri/src/**/*.rs`, or the row is closed with a recorded reason for keeping the narrow scope; `tests/test_drift_check.py` covers a non-`commands/` struct either way.

---

### BL-037 — Nullable `label` in RunSummary/RunDetail: backend distinguishes real from fallback
- state: blocked
- type: not stated
- area: Rig
- priority: low · size: XS–S
- blocked-by / trigger: BL-024
- evidence: docs/evidence/BL-037.md
- done-when: `label` is nullable end-to-end; no consumer compares `label` to `run_id`; the run_id fallback is applied once, at display; `cargo test` + `tsc -b` + `bun run lint` green.

---

### BL-058 — specs §5 (TypeScript Interfaces) is unchecked, and already stale
- state: open
- type: not stated
- area: Rig
- priority: low-medium · size: S
- evidence: docs/evidence/BL-058.md
- done-when: a `drift_check` check compares specs §5 interfaces against `src/hooks/types.ts` with a documented scope rule, §5's `RunSummary` matches source, and `--strict` is green.

---

### BL-062 — Fork provider/model overrides
- state: triggered
- type: not stated
- area: harness CLI + Rig fork dialog
- priority: medium · size: S–M
- blocked-by / trigger: the next ticket whose Touches names `cli/commands/fork.ex` or the Rig fork dialog
- evidence: docs/evidence/BL-062.md
- done-when: the CLI accepts the flags and they reach the fork run; the §4 sentence is corrected and its ref repointed under §8 ratification; operator access (picker vs CLI-only) is decided and recorded.

---

### BL-071 — Resource-level AWS cost + the resource-rate spot-check
- state: triggered
- type: not stated
- area: aetheris-agents
- priority: low (deferred) · size: M
- blocked-by / trigger: the first provider actually billed per resource, or AWS usage growing enough that enabling CE resource-level granularity is worthwhile
- evidence: docs/evidence/BL-071.md
- done-when: a resource-level cost path emits per-resource cost lines for at least one provider, and the rate spot-check compares them against the inventory estimates.

---

### BL-076 — `compose_report_data` sums *every* provider's prior snapshot into one `prior_total`
- state: committed
- type: not stated
- area: cloudcost
- priority: medium · size: S
- evidence: docs/evidence/BL-076.md
- done-when: `load_prior_snapshots`/`month_on_month` scope priors to the run's own providers; one test keeps `no_prior_month` alive beside another provider's history, a second shows an N>1 run unchanged.

---

### BL-061 — Gemini thought signatures are not recorded, so a forked Gemini run loses them
- state: triggered
- type: not stated
- area: harness
- priority: low-medium · size: S
- blocked-by / trigger: the first fork of a Gemini tool run
- evidence: docs/evidence/BL-061.md
- done-when: a Gemini fork of a tool step is run and recorded, and §4 is updated either way: the limitation is confirmed harmless, or the signature is recorded and round-trips with a test that fails if it is lost.

---

### BL-059 — Parallel tool calls are silently discarded: the adapter keeps the first `tool_use` block
- state: committed
- type: not stated
- area: harness
- priority: medium · size: M
- evidence: docs/evidence/BL-059.md
- done-when: multiple `tool_use` blocks in one response are all executed and recorded, or the request disables parallel tool use; the choice is in the determinism contract; a test fails if extra blocks are dropped.

---

### BL-040 — Event-type list exists in three places; drift between them is silent
- state: open
- type: not stated
- area: Rig
- priority: low-medium · size: S
- evidence: docs/evidence/BL-040.md
- done-when: `Trajectory.File` derives its map from `Event.known_types/0`, and a test asserts the `@type` union and `@event_types` agree — the union is not derivable, so the test is the only possible guard.

### BL-078 — Converge the AWS client plumbing into a shared `scripts/_aws.py`
- state: triggered
- type: not stated
- area: cloudcost
- priority: low · size: S
- blocked-by / trigger: do it the next time `fetch_aws.py` is legitimately edited
- evidence: docs/evidence/BL-078.md
- done-when: the four AWS client helpers live in `scripts/_aws.py` and both CLIs import them; `fetch_aws.py`'s AWS tests and t4's suite stay green with no fixture change.

### BL-079 — cloudcost holds no S3 storage rate for `ap-south-1`, where this account's buckets live
- state: triggered
- type: not stated
- area: cloudcost
- priority: low · size: XS
- blocked-by / trigger: the next ticket that edits `detect_optimization_signals.py`
- evidence: docs/evidence/BL-079.md
- done-when: an `ap-south-1` Standard rate is added **from a verified source with its `as_of`**, or the table is dropped in favour of whatever BL-072's engine-backed integration returns.

### BL-080 — `detect_optimization_signals` reports `partial` for intentional honesty, not only for a read gap
- state: triggered
- type: not stated
- area: cloudcost
- priority: low · size: S
- blocked-by / trigger: BL-081 is taken
- evidence: docs/evidence/BL-080.md
- done-when: a third envelope bucket holds intentional omissions; `status` is `partial` only for `denied[]` or `warnings[]`; render distinguishes it; a test asserts an unrated-region-only run reports `ok`.

### BL-081 — `s3_no_lifecycle_policy` fires on an observably empty bucket
- state: open
- type: not stated
- area: cloudcost
- priority: low · size: XS
- evidence: docs/evidence/BL-081.md
- done-when: `s3_no_lifecycle_policy` is suppressed when and only when the object count was observed to be 0; a test asserts an unknown-count bucket with no policy still raises it.

### BL-082 — no end-to-end orchestrated run of the `CLOUDCOST_OPTIMIZATION=1` path
- state: open
- type: not stated
- area: cloudcost
- priority: low · size: S
- evidence: docs/evidence/BL-082.md
- done-when: either a `cloudcost` sprint leg runs the orchestrator with `CLOUDCOST_OPTIMIZATION=1` and asserts the rendered report contains the optimization section, or an operator runs it once and the trajectory is recorded in the implementation notes.

### BL-084 — Tools manifests for the four use cases that have none
- state: open
- type: not stated
- area: aetheris-agents
- priority: low-medium · size: S
- evidence: docs/evidence/BL-084.md
- done-when: the six cloudcost scripts show without the amber badge and with structured arg forms; descriptions match `capability-matrix.md`; the other three use cases are filed or done.

### BL-085 — Cloudcost credentials + per-launch provider selection in Rig
- state: open
- type: not stated
- area: aetheris-agents
- priority: medium · size: M
- evidence: docs/evidence/BL-085.md
- done-when: a Rig-launched AWS run authenticates with the read-only key and reports; `CLOUDCOST_AWS_*` appears in no trajectory or `config_json`; the operator picks aws or do per launch; the runbook records the posture.

### BL-086 — Trajectory: label steps by their `run_command` stage
- state: open
- type: not stated
- area: aetheris-agents
- priority: medium · size: S
- evidence: docs/evidence/BL-086.md
- done-when: a cloudcost run and a docbuilder run label their steps by `run_command` stage, including `detect_optimization_signals` when enabled; non-script steps render unchanged.

### BL-087 — `payslip/tools.json` omits a runnable CLI
- state: open
- type: not stated
- area: aetheris-agents
- priority: low · size: XS
- evidence: docs/evidence/BL-087.md
- done-when: the entry is declared with arg forms derived from `python3 scripts/merge_employee_payslips.py --help`; the `xfail` marker in `tests/test_tools_manifests.py` is removed in the same commit.

### BL-088 — `ManifestScript.runnable`: mark a manifest entry describe-only
- state: triggered
- type: not stated
- area: aetheris-agents
- priority: low · size: S
- blocked-by / trigger: BL-089 is taken
- evidence: docs/evidence/BL-088.md
- done-when: `runnable` (default true) exists on `ManifestScript`, mirrors into `types.ts`, gates the Run button, and is enforced server-side in `tools_run_script`; the manifest spec documents it.

### BL-089 — tools.json for the three use cases that still have none
- state: open
- type: not stated
- area: aetheris-agents
- priority: low-medium · size: S
- evidence: docs/evidence/BL-089.md
- done-when: `tools.json` exists for docbuilder, provenance and boxy-pipeline; `NO_MANIFEST_YET` in `tests/test_tools_manifests.py` is empty; the suite passes.

### BL-091 — exportConfig() drops every manifest-derived env key
- state: open
- type: not stated
- area: aetheris-agents
- priority: low-medium · size: S
- evidence: docs/evidence/BL-091.md
- done-when: `exportConfig()` exports every non-masked manifest-derived env key; the masked-key policy is recorded; a test asserts a dynamic key appears in Export.

### BL-093 — runbook drift: PAYSLIP_MONTH described as non-persistent
- state: open
- type: not stated
- area: aetheris-agents
- priority: low · size: XS
- evidence: docs/evidence/BL-093.md
- done-when: the intended `PAYSLIP_MONTH` mechanism (per-launch or persistent) is ruled and recorded; `rig/docs/runbook.md` and `agentConfigDefs.ts` both match it.

## Milestones (L — issue docs first, per repo convention)

### BL-094 — A direct, non-LLM launch door for config-style orchestrators
- state: open
- type: not stated
- area: aetheris-agents
- priority: medium · size: M/L
- evidence: docs/evidence/BL-094.md
- done-when: Rig launches a named config-style orchestrator with no LLM planning turn; the driver-vs-config discriminator is tested, including a loud failure on the wrong path; specs, architecture and cloudcost's runbook agree.

---

## Drift apparatus (optional hardening)

### BL-046 — Tool-result payload key is a convention, not a contract: `"output"` vs `"result"`
- state: open
- type: not stated
- area: Harness
- priority: low · size: S
- evidence: docs/evidence/BL-046.md
- done-when: the `:tool_result` payload contract is stated in one place, existing readers point at it, and a writer inventing a third key is caught by a test or by construction.

---

### BL-044 — `mix aetheris` discards every command's exit code
- state: open
- type: not stated
- area: Harness
- priority: low · size: S
- evidence: docs/evidence/BL-044.md
- done-when: `mix aetheris` propagates the exit code (or documents why it cannot), and `sprint.sh` is audited for commands that would newly abort it.

---

### BL-057 — A stub run that declares tools silently gets no worker, so its tool calls never execute
- state: committed
- type: not stated
- area: Harness
- priority: medium · size: S–M
- evidence: docs/evidence/BL-057.md
- done-when: the question is answered and recorded; behaviour matches it (worker started, or config rejected); `OverlayAutonomousTest` passes unskipped or is rewritten to the answer; the six files' blast radius is walked.

---

### BL-051 — One unidentified `mix test` failure, and the capture discipline that lost its name
- state: open
- type: not stated
- area: Harness
- priority: low (capture fix) / unknown (the flake itself) · size: XS
- evidence: docs/evidence/BL-051.md
- done-when: gate runs capture full test output (summary and failure blocks) to a file; if the flake recurs with a name it gets its own row with a mechanism.

---

### BL-045 — `RunConfig mode: :verify` is a misnomer: no verification semantics
- state: open
- type: not stated
- area: Harness
- priority: low · size: S
- evidence: docs/evidence/BL-045.md
- done-when: the mode is renamed to what it does (e.g. `:replay_context`) with its two call-site parsers updated, or kept with a docstring stating it performs no verification — decided, not left ambiguous.

---

### BL-185 — `backlog_status.py --check` reports ARCHIVED-ONLY as a NOTE, and the corpus population is now zero
- state: committed
- type: not stated
- area: Drift apparatus
- priority: low · size: S
- evidence: docs/evidence/BL-185.md
- done-when: `resolve` promotes `ARCHIVED-ONLY` from `notes` to `problems` so `--check` exits 1; the promotion carries red-by-mutation evidence; `--census` at that commit prints a population of 0.

---


## boxy-pipeline

### BL-011 — Extract shared parsing helpers into `scripts/parsing_utils.py`
- state: open
- type: not stated
- area: boxy-pipeline
- priority: before next catalog/resolver change · size: S
- evidence: docs/evidence/BL-011.md
- done-when: the four helpers are defined only in `scripts/parsing_utils.py`; resolver and extractor import them; `pytest tests/` passes unchanged.

---

### BL-012 — Catalog enrichment merge strategy
- state: triggered
- type: not stated
- area: boxy-pipeline
- priority: before anyone enriches `catalog.jsonl` · size: S–M
- blocked-by / trigger: m-boxy-pipeline-1a t3 merged (resolver reads JSONL)
- evidence: docs/evidence/BL-012.md
- done-when: the enrichment option (A, B or C) is recorded in `boxy-pipeline/docs/m-boxy-pipeline-1a.md`; a test shows populated `mapped_20_20_codes` and `notes` survive re-extraction.

---

### BL-013 — Parameterise column x-boundaries in `so_extractor.py`
- state: open
- type: not stated
- area: boxy-pipeline
- priority: before processing a second SO PDF · size: S–M
- evidence: docs/evidence/BL-013.md
- done-when: `so_extractor.py` derives column bounds from the header row, with no hardcoded x constants; SO86708 still yields 34 items and $8,099.54.

---

### BL-014 — Parse Bill To and Ship To addresses separately in `_parse_header`
- state: open
- type: not stated
- area: boxy-pipeline
- priority: low (before multi-customer use) · size: S
- evidence: docs/evidence/BL-014.md
- done-when: `_parse_header` sets `bill_to` and `ship_to` separately; tests assert SO86708's `bill_to` contains "Brokaw" and `ship_to` contains "Laurel".

---

## Unsectioned

### BL-098 — The inventory envelope has no extras key, so adapter run-metadata dies at stdout
- state: committed
- type: not stated
- area: aetheris-agents
- priority: medium · size: M
- evidence: docs/evidence/BL-098.md
- done-when: the §Normalized inventory envelope carries an extras key, ratified doc-first per m3 §D-C; all three adapters emit it; compose carries it; the report separates "could not be assessed" from "empty".

---

### BL-102 — The complete-but-unmarked sweep runs at milestone closes only, so batch closes leave rows silently open
- state: committed
- type: not stated
- area: aetheris-agents
- priority: low-medium · size: XS–S
- evidence: docs/evidence/BL-102.md
- done-when: the export procedure states what the complete-but-unmarked sweep reads at a batch close; BL-084 and BL-085 are adjudicated done-or-open; the `CLAUDE.md` rule no longer reads as milestone-only.

---

### BL-108 — the eduloka sink gate parses a merged stream: same shape, different root cause
- state: open
- type: not stated
- area: harness
- priority: low · size: XS
- evidence: docs/evidence/BL-108.md
- done-when: the gate's parse survives anything on stderr, or the capture stops merging it; the ambient-variable question is recorded; a constructed stderr-contaminated run yields the right verdict or fails loudly.

---

### BL-109 — two `milestone-reference.md` files, canonical by different measures
- state: open
- type: not stated
- area: harness
- priority: low · size: XS
- evidence: docs/evidence/BL-109.md
- done-when: one file is canonical or both are retired; every cross-reference points at whatever survives; and if an index is kept, it either covers current work or says plainly what era it stops at.

---

### BL-111 — session memory is a durable instruction surface outside git, and no census, review or gate can reach it
- state: open
- type: not stated
- area: process
- priority: medium · size: S to characterise
- evidence: docs/evidence/BL-111.md
- done-when: a ruling says whether session memory is a private scratchpad or an untracked normative document; if the latter, what a census owes it is written where a session will read it.

---

### BL-112 — the BEAM's latin1 fallback silently corrupts non-ASCII in `--json` payloads
- state: committed
- type: not stated
- area: harness
- priority: medium · size: S
- evidence: docs/evidence/BL-112.md
- done-when: a `--json` payload with non-ASCII is byte-identical with and without a UTF-8 locale, or the harness refuses with a reason; runs with and without `LANG` are recorded; Rig's fork consumer is verified.

---

### BL-113 — a missed *knob* or *optional* credential constant disappears from the sprint's adapter env bridge silently
- state: open
- type: not stated
- area: aetheris-agents
- priority: low · size: XS
- evidence: docs/evidence/BL-113.md
- done-when: an adapter credential constant cannot be added, renamed or mis-categorised without the sprint selecting it correctly or a test failing; the mutation posture is recorded for the three silent cases.

---

### BL-115 — a stopped instance with no attached storage and a non-zero own estimate yields no candidate
- state: committed
- type: defect
- area: cloudcost
- priority: **high** · size: S–M
- evidence: docs/evidence/BL-115.md
- done-when: a stopped compute resource with no attached storage and a non-zero own estimate yields a candidate, or the blind spot and its DO consequence are recorded; a test covers the DO shape.

---

### BL-116 — the aged-snapshot rule's docstring requires a gate its code does not apply
- state: open
- type: defect
- area: cloudcost
- priority: medium · size: S
- evidence: docs/evidence/BL-116.md
- done-when: `rule_aged_snapshot` gates on `attached_to is None`, or the docstring is corrected and the 0.7 confidence re-ruled; tests match.

---

### BL-117 — an out-of-vocabulary `type` is counted everywhere and evaluated by nothing
- state: open
- type: defect
- area: cloudcost
- priority: medium · size: S
- evidence: docs/evidence/BL-117.md
- done-when: `usable_resources` skips an out-of-vocabulary `type` with a reason, and `sprint.sh`'s rule-legibility arms change in the same landing so none is unreachable.

---

### BL-118 — five I/O sites decode adapter JSON under the platform default encoding
- state: open
- type: defect
- area: cloudcost
- priority: medium · size: S
- evidence: docs/evidence/BL-118.md
- done-when: the five I/O sites pass `encoding="utf-8"`; a non-ASCII-name fixture runs detect → compose → render with an assertion on the rendered bytes.

---

### BL-119 — a cost snapshot with a declared total and no line items is silently dropped from discovery
- state: open
- type: defect
- area: cloudcost
- priority: medium · size: S (the warning) / M (the document-type change)
- evidence: docs/evidence/BL-119.md
- done-when: `discover_bundles` warns and records a `skipped` entry for any document `classify` cannot type, with a test; step 2 (`document_type`) is then refiled or rejected.

---

### BL-120 — the idle-load-balancer rule rests on a `tag:` convention nothing enforces
- state: open
- type: defect
- area: cloudcost
- priority: medium · size: XS to check
- evidence: docs/evidence/BL-120.md
- done-when: the DO and Linode load-balancer normalizers are read and the answer — can an in-use LB present `attached_to is None`? — is recorded; a defect row or a test follows.

---

### BL-122 — `source_granularity` is carried into the report and validated nowhere
- state: open
- type: defect
- area: cloudcost
- priority: medium · size: XS–S
- evidence: docs/evidence/BL-122.md
- done-when: valid `source_granularity` values are enumerated; `service_totals` warns on coarser than `service` and accepts finer; a test covers both.

---

### BL-123 — `age_phrase` truncates, so the evidence sentence contradicts its own threshold
- state: open
- type: defect
- area: cloudcost
- priority: low · size: XS
- evidence: docs/evidence/BL-123.md
- done-when: `age_phrase` never prints an age that, as printed, would not exceed its threshold; the display convention is recorded; evidence-text tests match.

---

### BL-124 — C3: reject a naive timestamp rather than assuming UTC
- state: open
- type: contract consequence
- area: cloudcost
- priority: medium · size: S
- evidence: docs/evidence/BL-124.md
- done-when: `parse_timestamp` rejects a naive timestamp into `timestamp_warnings`; adapter fixtures were swept for naive stamps first; the timestamp field set is named once in `_normalized.py` (BL-125).

---

### BL-126 — C4: carry the currency's minor-unit exponent and round to it
- state: open
- type: contract consequence
- area: cloudcost
- priority: medium · size: M
- evidence: docs/evidence/BL-126.md
- done-when: the cost snapshot carries the minor-unit exponent; `money()` takes it at every call site; the reconcile tolerance is per currency; zero-decimal and sub-cent tests pass.

---

### BL-128 — C6: the keep marker becomes a first-class field, not a tag spelling
- state: open
- type: contract consequence
- area: cloudcost
- priority: medium · size: M
- evidence: docs/evidence/BL-128.md
- done-when: a boolean keep field exists in §Normalized and every adapter emits it; `has_keep_tag` reads the field, not a tag spelling; fixtures and the keep acceptance test match.

---

### BL-129 — C10: service identity needs a stable identifier beside the display name
- state: open
- type: contract consequence
- area: cloudcost
- priority: medium · size: M–L
- evidence: docs/evidence/BL-129.md
- done-when: each cost line carries a stable service id; the MoM delta keys on it; prior snapshots without an id still load, with a test.

---

### BL-130 — C11: promote `swept_regions` to a first-class optional envelope field
- state: open
- type: contract consequence
- area: cloudcost
- priority: medium · size: S–M
- evidence: docs/evidence/BL-130.md
- done-when: `swept_regions` is a first-class optional cost-envelope field; the `provider_extra` read is gone; DO and Linode reports stay byte-identical.

---

### BL-133 — the loop's evidence is not retained, so no past run's greenness is checkable after the fact
- state: open
- type: method
- area: process / harness
- priority: medium · size: S to rule, S–M to implement
- evidence: docs/evidence/BL-133.md
- done-when: a ruling states whether a round's findings and dispositions must outlive the session; if so, a mechanism retains them in the repo for every ticket, not `hc-*` only.

---

### BL-137 — a freshness census over `cloudcost/milestone.md` §Open items: items whose trigger has already fired, or whose framing predates adapters that have since shipped
- state: open
- type: method
- area: cloudcost
- priority: medium · size: S–M
- evidence: docs/evidence/BL-137.md
- done-when: each of the eleven §Open items in `cloudcost/milestone.md` is read against HEAD and marked still accurate, trigger fired, framing stale (corrected in place, old wording quoted) or discharged elsewhere (cited).

---

### BL-138 — C8's D21 clause enumerates the declared parameter block wrongly
- state: open
- type: accuracy
- area: cloudcost
- priority: low · size: XS
- evidence: docs/evidence/BL-138.md
- done-when: C8's D21 clause names the five emitted keys, or names the four and says the fifth explicitly; and the *"and nothing else"* claim is either true as written or replaced.

---

### BL-139 — record the conditions under which a triad exchange may be looped without a human turn
- state: committed
- type: method
- area: process / methodology
- priority: low · size: S to rule
- evidence: docs/evidence/BL-139.md
- done-when: the two conditions are written into whichever of the triad documents the ruling names, or the row is closed with a recorded decision that no criterion is to be stated.

---

### BL-140 — whether a correction owes a same-commit sweep for recurrences as a standing obligation
- state: committed
- type: method
- area: process / methodology
- priority: medium · size: S to rule
- evidence: docs/evidence/BL-140.md
- done-when: the same-commit recurrence sweep is stated in one named document with its scope, or declined with a reason; the `CLAUDE.md` correction-chasing entry is reconciled with the answer.

---

### BL-141 — a Done-check that cannot fail, and whether a positional claim must carry path:line
- state: ready
- type: method
- area: process / methodology
- priority: medium · size: S–M to rule (two questions, one document)
- evidence: docs/evidence/BL-141.md
- done-when: (a) §6 either carries a bar with a stated recognition test or records the decision not to add one; and (b) is either settled by reference to **m5-D1** with the reference written down, or ruled on separately.

---

### BL-142 — whether §6 should require `Touches` to be derived from a search for the premise
- state: committed
- type: method
- area: process / methodology
- priority: medium · size: S to rule
- evidence: docs/evidence/BL-142.md
- done-when: §6's `Touches` field either states the derivation requirement with the search it implies, or records the decision that enumeration stays the author's and why.

---

### BL-143 — the `project_knowledge` export boundary has no owner and no schedule
- state: ready
- type: decision
- area: process / project knowledge
- priority: medium · size: S to decide
- evidence: docs/evidence/BL-143.md
- done-when: the refresh has a named owner and a trigger that fires without a human remembering, or the permanent occupancy is accepted in writing where `drift_check`'s output sends a reader.

---

### BL-144 — a round whose output is a derivation may leave it only in a scratch directory
- state: committed
- type: decision
- area: process / round records
- priority: medium · size: S to decide
- evidence: docs/evidence/BL-144.md
- done-when: the obligation is stated in one named document with its scope — which artifacts, whose responsibility, and where they land — or declined with the reason recorded.

---

### BL-147 — the absence of a reachability stamp encodes three different dispositions
- state: open
- type: defect
- area: cloudcost
- priority: medium · size: S
- evidence: docs/evidence/BL-147.md
- done-when: either every contract carries a legible disposition, or the three-way silence is stated once in §Contracts' preamble so a reader can decode it without the notes file.

---

### BL-148 — C7 and C13 state adapter obligations with no exemplar and no verdict in the contract
- state: committed
- type: defect
- area: cloudcost
- priority: medium — before provider four · size: S–M
- evidence: docs/evidence/BL-148.md
- done-when: C7 and C13 either carry an exemplar or state that they do not and why; and C7's tag-grammar obligation has a stated enforcement position, even if that position is "none, by decision".

---

### BL-149 — two live documents use "live" in incompatible senses
- state: committed
- type: decision
- area: process / round vocabulary
- priority: medium · size: S to decide
- evidence: docs/evidence/BL-149.md
- done-when: a discriminator for "live" is stated in one named document and the citing rounds match it, or the collision is recorded as accepted with its reason.

---

### BL-153 — the cloudcost sprint's credential gate exits before the stale-artifact guard, so a credential-less leg leaves the previous run's artifacts in place
- state: committed
- type: defect
- area: harness
- priority: medium · size: S
- evidence: docs/evidence/BL-153.md
- done-when: on every credential branch of `sprint.sh`'s cloudcost arm, a failed credential gate leaves the run directory unable to read as the current run; a credential-less run proves it.

---

### BL-154 — Rig's Cancel kills the direct child only, and transitions nothing
- state: committed
- type: defect
- area: aetheris-agents
- priority: medium · size: M
- evidence: docs/evidence/BL-154.md
- done-when: a Rig cancel leaves a terminal event and a `runs.status` distinct from `running` and `failed`, and the UI shows the steps' real end state; or `failed`-by-sweep is ruled intended, the sweep's framing corrected, the UI half still owed.

---

### BL-155 — the capability matrix has three consumers, no gate, and is the one wiring place an LLM writes
- state: committed
- type: defect
- area: aetheris-agents
- priority: medium-high · size: M
- evidence: docs/evidence/BL-155.md
- done-when: a stale or wrong capability matrix is caught by a mechanism whose blind spots are named, or the matrix is ruled not gate-worthy and its three consumers are documented as reading an unchecked artefact.

---

### BL-156 — the approval card's step text is written by the planner per run, and nothing checks it
- state: committed
- type: defect
- area: aetheris-agents
- priority: medium · size: M
- evidence: docs/evidence/BL-156.md
- done-when: the approval card's step text is derived from something checkable (manifest description, matrix row or per-agent template), or the card labels it model-generated and unverified.

---

### BL-157 — the bare module name `conftest` is a standing trap, and it is held open by an absence
- state: open
- type: defect
- area: test apparatus
- priority: medium · size: S
- evidence: docs/evidence/BL-157.md
- done-when: the absence is either enforced or removed as a dependency, and which of those is **not decided here**.

---

### BL-158 — the pre-existing `integration` population has never been audited against the criterion the gate now uses
- state: open
- type: gate
- area: test apparatus
- priority: medium · size: M
- evidence: docs/evidence/BL-158.md
- done-when: the 159 have been read against the criterion and the result recorded — each either confirmed, or reported as not meeting it — and the reverse sweep for unmarked tests that should carry it has been run once over the whole tree.

---

### BL-159 — what the dormant set owes when boxy-pipeline resumes
- state: triggered
- type: gate
- area: test apparatus
- priority: low until boxy-pipeline resumes, then blocking · size: M
- blocked-by / trigger: boxy-pipeline resumes
- evidence: docs/evidence/BL-159.md
- done-when: boxy-pipeline resumes and, before the `pytestmark` lines go, the dormant set has run to completion once, its duration and every failure by name are recorded, and gate membership or a split is decided.

---

### BL-160 — the U2 export gate has never returned information in either direction
- state: committed
- type: gate
- area: process / project knowledge
- priority: medium · size: M
- evidence: docs/evidence/BL-160.md
- done-when: a decision on (3) is recorded, and (1) and (2) are answered against it: the pattern set is ruled sufficient with its under-reach accepted, or a corpus and its custody are defined and the value sweep restored.

---

### BL-162 — an inbound pointer is not a scope change, and nothing tells the row
- state: committed
- type: decision
- area: process / backlog discipline
- priority: medium · size: S to decide
- evidence: docs/evidence/BL-162.md
- done-when: one of the three remedies is written into a named document with its scope, or the gap is accepted with a reason; either way it states what a citing document owes its target and where a row's reader learns of it.

---

### BL-164 — a test that hard-codes a value the code derives goes red when the derivation moves, not when the code breaks
- state: committed
- type: defect (instance fixed) + decision (the class)
- area: testing discipline
- priority: medium · size: S to decide the class; the instance is already done
- evidence: docs/evidence/BL-164.md
- done-when: the class has a stated check (rule, lint or recorded sweep) or is accepted in writing with its reason; either way the sweep has been run and its result recorded, including a result of nothing.

---

### BL-166 — `drift_check --strict` is green because of an untracked personal profile export
- state: ready
- type: defect
- area: process / gates
- priority: medium _(proposed)_ · size: S _(proposed)_
- evidence: docs/evidence/BL-166.md
- done-when: `drift_check --strict` is green in a fresh clone with no untracked environment, or the dependency is declared in a tracked file and its absence is a legible skip; a published done-check says what `payload_fields` sampled.

---

### BL-167 — run-level completion needs a harness post-run hook; it is not satisfiable agents-side
- state: committed
- type: gap
- area: harness
- priority: medium _(proposed)_ · size: M _(proposed)_
- evidence: docs/evidence/BL-167.md
- done-when: a reader can tell a complete run from an interrupted one for all six producers by a mechanism no prompt line can skip; or per-step attestation is ruled sufficient and BL-153's "runs LAST UNCONDITIONALLY" clause is corrected.

---

### BL-168 — `aetheris_run_id` is declared in five DDL sites across two languages, written by nothing and read by nothing
- state: open
- type: defect
- area: aetheris-agents
- priority: low _(proposed)_ · size: S _(proposed)_
- evidence: docs/evidence/BL-168.md
- done-when: either the five sites are written and something reads them, **or** all five are dropped and `docs/provenance/specs.md`'s four lines go with them.

---

### BL-170 — the concurrency detector is probabilistic, and a single green is not evidence the lock is present
- state: committed
- type: bug
- area: aetheris-agents
- priority: medium · size: S
- evidence: docs/evidence/BL-170.md
- done-when: the mutation control is deterministic, evidenced the way the current figure was: N runs with the lock disabled all red, N runs with it restored all green, with N and the commands recorded.

---

### BL-175 — nothing can report a workflow cache path that names nothing, and the instrument that can is uncommitted
- state: ready
- type: bug
- area: harness
- priority: medium · size: S
- evidence: docs/evidence/BL-175.md
- done-when: the check is committed at a named path in one of the two repos, is invoked by something that runs on its own (not by hand), and has been demonstrated red — by mutation, on the tree it guards, with the restore verified.

---


### BL-180 — the single-backtick wrapper convention mangles wherever the wrapped text carries an inner backtick
- state: open
- type: bug
- area: documentation system
- priority: medium · size: M
- evidence: docs/evidence/BL-180.md
- done-when: a form is chosen and stated; a committed, named script converts the population, with a before-and-after render on a real sample; a check, lint or `drift_check` arm is shown red on a reintroduced instance and restored.

---

### BL-183 — `orb_blackboard_test.exs:73` reads a blackboard key one step after the other agent writes it, with nothing synchronising the two
- state: committed
- type: bug
- area: harness
- priority: not stated · size: not stated
- evidence: docs/evidence/BL-183.md
- done-when: the interleaving is forced (A's write held past B's read) and the outcome recorded; a real race is synchronised by a mechanism, never a sleep, retry or relaxed assertion; the sibling assertions from BL-181's census are ruled on.


### BL-187 — the planner's `params` map has no declared per-use-case spec, and nothing validates it before the operator approves
- state: committed
- type: defect
- area: aetheris-agents
- priority: medium · size: M
- evidence: docs/evidence/BL-187.md
- done-when: an operator cannot approve a plan with a param key no agent in it reads, or a value outside the key's declared set: the plan is rejected before the card renders, or the card marks the param unvalidated.


### BL-188 — nothing carries a month from a cloudcost request to the pipeline, so a month-named request cannot be honoured
- state: open
- type: missing capability
- area: aetheris-agents
- priority: medium · size: S–M
- evidence: docs/evidence/BL-188.md
- done-when: for each of the four providers, a cloudcost request naming a month yields a report for that month, or a plan or report stating which period it covers and why it differs.


### BL-189 — a degraded run has no representation: the stage CLIs' three-valued status is collapsed to a boolean on both operator surfaces, in opposite directions
- state: committed
- type: defect
- area: aetheris-agents and harness
- priority: medium · size: M
- evidence: docs/evidence/BL-189.md
- done-when: on a nonzero step exit the Orchestrator card shows the stage-CLI `errors[]`, else truncated stdout, never a blank, including `partial` with `errors: null`; a `partial` run is distinct from success and failure.

---

### BL-190 — the whole-suite gate is red: a cloudcost seat test compares a frozen fixture against a reference date that is the wall clock
- state: ready
- type: defect
- area: aetheris-agents
- priority: medium · size: S
- evidence: docs/evidence/BL-190.md
- done-when: the seat test pins `--reference-date` relative to the fixture and asserts what that date implies, or asserts the post-t3 truth (a legible seat yields a candidate) with the date still pinned; the choice is the ticket's.

---

### BL-198 — MVML record-mode assertion: at prompt assembly, the assembled prompt equals the log-derived prompt
- state: committed
- type: gate
- area: harness
- priority: medium · size: S
- evidence: docs/evidence/BL-198.md
- done-when: in record mode, at `prompt_built`, the loop derives the prompt from prior events plus recorded config, compares it with the assembled one, and surfaces a divergence as an event or a run failure; the choice is recorded here.

---

### BL-199 — length-stop tool-call guard: a tool call inside a response the token limit cut off is executed as if it were whole, on both provider paths
- state: ready
- type: defect — reachable by reading, not demonstrated live
- area: harness
- priority: medium · size: S
- evidence: docs/evidence/BL-199.md
- done-when: on a length stop with a tool call present, nothing executes; each call gets a recorded `tool_result` with a structured error (`truncated_response`, or an error key named on this row); the loop continues to the next turn.

---

### BL-202 — measure the two-surface fetch-instruction condition: the generated index's fetch header has never been in front of a probe
- state: open
- type: measurement
- area: aetheris
- priority: low — cheap, and gated on nothing · size: S
- evidence: docs/evidence/BL-202.md
- done-when: one probe run under the two-surface condition is filed as a measurement record under harness `docs/aetheris/research/` in the series' shape, with a §Reading that names the outcome against the two branches in evidence.

### BL-203 — the on-demand pin column carries no obligation, and does not say so
- state: open
- type: documentation
- area: aetheris-agents
- priority: low — nothing fails; the cost is a reader chasing a lag that is not drift · size: XS
- evidence: docs/evidence/BL-203.md
- done-when: the manifest states in its opening paragraphs what the pin means per surface: for `export` and `both`, a store claim that check 8 compares; for `on-demand`, a last-moved note nothing compares.

---

### BL-206 — the event-type map in `trajectory/file.ex` is unenforced and is already one short: `:observation` is declared but unmapped
- state: open
- type: hardening
- area: harness
- priority: low while latent; the trigger that makes it live is ordinary work · size: S
- evidence: docs/evidence/BL-206.md
- done-when: `@event_types`, the `@type event_type` union and `@event_type_map` hold the same set, and a `drift_check.py` arm or a harness test covers that three-way identity.

---

### BL-209 — `build_synthesis_request/1` hardcodes `model: "stub-v1"`, so skill LLM synthesis 404s against a real provider
- state: blocked
- type: bug
- area: harness
- priority: medium · size: TBD — see the Done-when; the row's decision is whether this is fixed at all
- blocked-by / trigger: BL-224
- evidence: docs/evidence/BL-209.md
- done-when: the model comes from the run's config and `mix test --include integration` passes that test; or m14 T5's supersession is recorded as retiring this code path, with the retirement pointed at.

---
### BL-210 — the Anthropic adapter discards the text block on tool-calling responses
- state: ready
- type: defect
- area: harness
- priority: medium · size: S
- evidence: docs/evidence/BL-210.md
- done-when: The adapter preserves the text block alongside `tool_use`, the `llm_responded` payload carries it, and a test asserts a tool-calling response round-trips both.

---
### BL-211 — Segmenter's public surface: an events-taking entry point, and fence-stripping's home
- state: open
- type: defect
- area: harness
- priority: medium · size: S
- evidence: docs/evidence/BL-211.md
- done-when: `Segmenter` takes events without re-reading the file and `Candidate` uses that path; fence-stripping has one implementation in `lib/`; a test parses a fenced and a bare response through it.

---
### BL-212 — `EXTRACTOR_DENY_LIST` is applied by nothing, and T3's notes claim otherwise
- state: open
- type: defect
- area: harness
- priority: medium · size: M
- evidence: docs/evidence/BL-212.md
- done-when: the deny-list reaches a run through a `RunConfig` field (rule 15's three sites), a worker init-payload field and `main.rs`; a test shows a declaring run cannot write a denied path; T3's notes are corrected.

---

### BL-213 — the curator's provenance record has no durable home
- state: open
- type: defect
- area: harness
- priority: high · size: M
- evidence: docs/evidence/BL-213.md
- done-when: A curation writes its report durably; the record is readable back by `source_run_id` and by skill id; §2's constraint says documents; and a test asserts a rejected candidate — which produces no `skills` row — still appears in the log.

---
### BL-214 — the pre-reflection envelope is recoverable and unused
- state: open
- type: enhancement
- area: harness
- priority: medium · size: M
- evidence: docs/evidence/BL-214.md
- done-when: the curator takes an extractor run id, diffs the reflected envelope against the stored one and records the differences in BL-213's record; `store_prompts` false yields a stated not-available outcome; a test covers both.

---
### BL-215 — the reflector can exceed its response budget, leaving an unparseable envelope
- state: open
- type: defect
- area: harness
- priority: medium · size: S
- evidence: docs/evidence/BL-215.md
- done-when: a truncated or unparseable envelope is detected by the run itself, and a long trajectory has a stated strategy: chunking, per-candidate emission, or a documented cap on candidates per run.

---

### BL-217 — the nested row structs in `commands/*.rs` are fence-undocumented, so `command_fields` cannot see them
- state: open
- type: defect
- area: Rig
- priority: medium · size: M
- evidence: docs/evidence/BL-217.md
- done-when: every `pub struct` in `commands/*.rs` is in `command_fields`' population or excluded by a rule the check implements; the sweep covers all 44; a test shows a field added to a previously-unfenced struct draws a finding.

---

### BL-218 — `usage.rs` drops undecodable DB rows silently
- state: committed
- type: defect
- area: Rig
- priority: medium · size: S
- evidence: docs/evidence/BL-218.md
- done-when: An undecodable row is surfaced — an error, or a returned count of what was dropped — rather than discarded, and a test covers the drop path.

---

### BL-219 — the reflector's `findings` describe its own input, not the harness
- state: open
- type: defect
- area: harness
- priority: low · size: S
- evidence: docs/evidence/BL-219.md
- done-when: the `findings` instruction separates an observation about the harness from a description of the envelope, or the key is closed with a recorded reason; a live run yields findings about the harness or none.

---

### BL-222 — a skill row can be INSERTED already approved, bypassing the gate
- state: open
- type: defect
- area: harness
- priority: medium · size: S
- evidence: docs/evidence/BL-222.md
- done-when: No write path other than `approve_skill/3` can produce a row with `status: "approved"`, and a test asserts that `insert_skill/1` cannot.

---

### BL-224 — retire m04's `Skill.Extractor` and `extract_skill/3`
- state: open
- type: chore
- area: harness
- priority: medium · size: S
- evidence: docs/evidence/BL-224.md
- done-when: `grep -rn 'extract_skill\|Skill.Extractor' lib/` returns 0; the suite is green with every m04 extraction assertion converted or explicitly retired with its reason; no doc names either.

---

### BL-225 — FrequencyPrior's corpus should read the run's recorded `use_case`
- state: triggered
- type: enhancement
- area: harness
- priority: medium · size: S
- blocked-by / trigger: `RunConfig.use_case` landing, which is part of m14 T12
- evidence: docs/evidence/BL-225.md
- done-when: The corpus comes from runs' recorded `use_case` where present; the union remains the fallback for runs predating the field; a test asserts a run never extracted from still counts toward the prior.

---

### BL-226 — an edited approved body has no re-approval path
- state: open
- type: defect
- area: harness
- priority: medium · size: M
- evidence: docs/evidence/BL-226.md
- done-when: An operator who edits an approved body has a supported path back to served, the path leaves a record of both approvals, and a test asserts the original approval is not overwritten.

---

### BL-227 — `docs/rig/specs.md` §2 is two columns behind on `skills`
- state: open
- type: chore
- area: Rig
- priority: low · size: XS
- evidence: docs/evidence/BL-227.md
- done-when: §2's `skills` block lists both columns and `db_schema` emits no `skills` INFO.

---

### BL-228 — a resumed run loses its served catalog mid-run
- state: open
- type: defect
- area: harness
- priority: high · size: M
- evidence: docs/evidence/BL-228.md
- done-when: A resumed run either re-serves the same catalog — same entries, same body hashes — or records in the trajectory, not only in a log, that it could not.

---

### BL-230 — `broadcast_message_test.exs:258` is a timing race between two agents
- state: committed
- type: defect
- area: harness
- priority: low · size: S
- evidence: docs/evidence/BL-230.md
- done-when: The mechanism is identified and the test no longer races, or the row records why it cannot be made deterministic.

---

### BL-231 — `uc3-skill-extraction.md` describes the retired injector
- state: open
- type: chore
- area: harness
- priority: low · size: XS
- evidence: docs/evidence/BL-231.md
- done-when: The doc is swept to index injection, or marked as describing m04 as history.

---

### BL-233 — a recorded run does not say which agent file produced it
- state: committed
- type: defect
- area: harness
- priority: medium · size: M
- evidence: docs/evidence/BL-233.md
- done-when: A run records what produced it — the agent file's path and the commit or content hash it was read at — and a test asserts a recorded run can name its producer without inference.

---

### BL-234 — baselines locked before BL-221 were computed over unmarked runs
- state: open
- type: defect
- area: harness
- priority: medium · size: S
- evidence: docs/evidence/BL-234.md
- done-when: A baseline records the selection rule it was locked under, and a baseline predating BL-221 is either re-locked or refused by the gate rather than used silently.

---

### BL-238 — `Runner.build_run_config/3` hand-builds a `RunConfig`, bypassing rule 15
- state: ready
- type: defect
- area: harness
- priority: medium · size: S
- evidence: docs/evidence/BL-238.md
- done-when: `Runner` constructs through `from_map/2`; the two divergences are resolved with the choice stated; a test asserts a newly added `RunConfig` field reaches a Runner-built config with no Runner change.

---

### BL-240 — `specs.md` §6 does not list `skill_injected`'s marker fields
- state: open
- type: chore
- area: aetheris-agents
- priority: low · size: XS
- evidence: docs/evidence/BL-240.md
- done-when: §6's `skill_injected` row lists `served_under?` and `status?` and says that `served_under` marks a gate measurement.

---

### BL-241 — a forked arm drops its template's pre-tools output
- state: open
- type: defect
- area: harness
- priority: medium · size: M
- evidence: docs/evidence/BL-241.md
- done-when: a forked run's first turn carries the context an unforked run of the same template would; a test asserts a task with pre-tools produces the same first-turn context forked and unforked.

---

### BL-243 — after a use_case's first approval, no ordinary run can seed a baseline
- state: open
- type: defect
- area: harness
- priority: high · size: M
- evidence: docs/evidence/BL-243.md
- done-when: A baseline can be locked for a use_case that has approved entries — state the mechanism and what a baseline then means — and a test asserts a scope with one approved entry can still seed a baseline for a new candidate.

---

### BL-244 — a forked arm takes its tool list from the template and only its prefix from the recorded run
- state: open
- type: defect
- area: harness
- priority: medium · size: M
- evidence: docs/evidence/BL-244.md
- done-when: A fork either refuses a template whose tool list cannot execute the prefix, or the mismatch is recorded on the run; a test covers a prefix calling a tool the template omits.

---

### BL-245 — a corpus run's recorded segmentation cannot be found, so the prior re-segments it
- state: open
- type: defect
- area: harness
- priority: medium · size: M
- evidence: docs/evidence/BL-245.md
- done-when: an extraction is findable from its run and from the skills rows it produced; the prior reuses a recorded segmentation and says so; a test asserts prior and candidate agree on segment boundaries.

---

### BL-246 — a run declaring `tools: []` is still offered spawn_agent, wait_for_event and wait_for_all
- state: ready
- type: defect
- area: harness
- priority: medium · size: S
- evidence: docs/evidence/BL-246.md
- done-when: A run is offered exactly its declared `tools`, plus what a stated contract adds, or the extractor stops claiming it has none and its run fails rather than reports done when it produces no envelope.

---

### BL-247 — the gate's result does not record which control-2 check rejected a candidate
- state: open
- type: defect
- area: harness
- priority: medium · size: S
- evidence: docs/evidence/BL-247.md
- done-when: The control-2 result names which check fired, both when only one does and when both do; a test asserts a candidate matching only the modal path reports that reason and not membership.

### BL-248 — the ETXTBSY / `spawn_agent` worker-sharing question is answered in code and recorded nowhere
- state: committed
- type: documentation
- area: both repos
- priority: medium · size: S
- evidence: docs/evidence/BL-248.md
- done-when: The answer is recorded where the question is asked: both cross-repo tables, with the citations; uc-ingestion phase 1 no longer names it as a gate; and the nested-mix case is stated separately so the answer is not read wider than it goes.

---

### BL-249 — the harness ExUnit `:integration` population has no audit
- state: open
- type: gate
- area: harness
- priority: low–medium · size: M
- evidence: docs/evidence/BL-249.md
- done-when: A criterion exists for what the harness `:integration` tag means; the 24 are audited against it; each either loses the tag or keeps it with the reason recorded where a reader of the gate output can reach it.

---

### BL-250 — a run that fails before serving is recorded `:unavailable` and counted as a no-skill run
- state: committed
- type: defect
- area: harness
- priority: medium · size: S
- evidence: docs/evidence/BL-250.md
- done-when: A run that failed before serving reads `:unknown`, not `:unavailable`; `lock/2` therefore refuses it; and a test covers a run that fails at step 0 with its serve incomplete.

### BL-251 — `mix test` results vary between runs at the same seed: `Skill.BodyTest` captures a concurrent test's warning
- state: ready
- type: defect (test infrastructure)
- area: harness
- priority: medium — a gate whose result varies at a fixed seed is not evidence the suite passed · size: TBD
- evidence: docs/evidence/BL-251.md
- done-when: the assertion distinguishes this test's own log output from concurrent output, or the test is made non-async — with the choice and its cost recorded.

### BL-254 — three retained-manifest-header sentences point "after the table" / "below" at blocks BL-253 moved out
- state: open
- type: defect
- area: process / project knowledge
- priority: low · size: XS
- evidence: docs/evidence/BL-254.md
- done-when: the three retained-header pointers resolve to where the blocks now live (the index entry or `docs/export-boundaries/`), not to a file position; a check or sweep confirms no header sentence points at a moved block.

### BL-263 — a boot-resumed run is not yet registered when the scheduler's first tick runs, so `:overlap_live` cannot see it
- state: open
- type: defect — found while implementing BL-256, not demonstrated live
- area: harness — scheduler / admission (INV-2)
- priority: medium · size: S
- evidence: docs/evidence/BL-263.md
- done-when: a boot-resumed run is registered before the scheduler's first tick can admit a start for its schedule, or the tick waits for resume; a test asserts the first tick refuses `:overlap_live` and names the window closed.

### BL-264 — the suite's live scheduler fires other modules' residue schedule rows, starting untracked runs mid-suite
- state: open
- type: defect — demonstrated live (seed 70665, two `Aetheris.AdmissionDedupTest` failures)
- area: harness — test environment
- priority: medium · size: S
- evidence: docs/evidence/BL-264.md
- done-when: a `mix test` run starts no run the suite did not ask for; the `priv/runs/` directories such starts leave are ruled in or out of BL-261b's retention; a test asserts a `with_file_store/1` round trip starts no scheduled run.

### BL-265 — a default or inherited `max_duration` bound for unattended scheduled runs
- state: open
- type: gap — deferred by the arbiter at BL-262, not demonstrated live
- area: harness — scheduler / watchdog
- priority: low-medium · size: S
- evidence: docs/evidence/BL-265.md
- done-when: a ruling states whether a scheduled run with no `max_duration` gets a bound, from what, and how long-lived and boot-resumed unbounded runs are treated; if a bound lands, a test asserts both cases behave as ruled.

### BL-268 — terminal transitions are not final: events and status writes follow the first terminal write
- state: open
- type: defect
- area: harness — Agent.Server / execution loop
- priority: high · size: M
- evidence: docs/evidence/BL-268.md
- done-when: _(proposed)_ no event is appended to a run after its first terminal status write, or each remaining case is documented as intended; each item in the evidence has a regression test or a recorded disposition.

### BL-269 — multiple VMs write one store: every CLI command boots its own Store, Scheduler and sweep on the same file
- state: open
- type: defect
- area: harness — Store / Scheduler / Sweep
- priority: medium · size: S–M
- evidence: docs/evidence/BL-269.md
- done-when: _(proposed)_ each multi-VM hazard in the evidence is either prevented (single-writer enforcement or cross-VM coordination) or documented as an unsupported deployment with a guard; tests or recorded dispositions for each.

### BL-270 — a busy read crashes the singleton Store: `collect_rows/3` has no `:busy` arm
- state: open
- type: defect
- area: harness — Store
- priority: high · size: XS
- evidence: docs/evidence/BL-270.md
- done-when: _(proposed)_ a busy read returns an error to the caller instead of crashing Store, with a test.

### BL-271 — a terminal worker `:DOWN` never notifies waiters or the agent tree
- state: open
- type: defect
- area: harness — Agent.Server
- priority: medium-high · size: S
- evidence: docs/evidence/BL-271.md
- done-when: _(proposed)_ a run driven terminal by a worker `:DOWN` notifies the same surfaces as `{:run_failed, _}`; a test asserts a parent waiting on `agent_done` is woken when its child's worker dies.

### BL-272 — Rig infers run completion from `run_complete` on the poll path
- state: open
- type: defect
- area: rig — harness views (`useRunEvents`, RunList EventsContent)
- priority: medium · size: S
- evidence: docs/evidence/BL-272.md
- done-when: _(proposed)_ both sites take completion from the run row's status (`TERMINAL_STATUSES`, `useHarness.ts:141`), or from a stream control frame where one is present, and neither reads `run_complete` as a status.

### BL-273 — stale `server.ex:` line citations across Rig source, one of them a false claim
- state: open
- type: defect
- area: rig — source comments citing harness `lib/aetheris/agent/server.ex`
- priority: low · size: S
- evidence: docs/evidence/BL-273.md
- done-when: _(proposed)_ every `server.ex:` citation in `rig/src` and `rig/src-tauri/src` names its anchor and resolves at the harness commit it cites; `useTrajectory.ts`'s write-result sentence states what `run_outcome/2` does.

---

### BL-274 — five of BL-266 T3's click-through checks were never exercised
- state: open
- type: verification
- area: rig — BL-266 T3 run-event-stream consumer
- priority: medium · size: S
- evidence: docs/evidence/BL-274.md
- done-when: _(proposed)_ each of the five T3 click-through checks is exercised once against a live harness and recorded, or has an automated substitute that exercises the real run path; the T3 notes' §Click-through carries the outcome.

---

### BL-275 — `mix aetheris` does not load `config/runtime.exs`, so the documented token override has no effect
- state: open
- type: defect
- area: harness — `mix aetheris` task / runtime config
- priority: medium · size: S
- evidence: docs/evidence/BL-275.md
- done-when: _(proposed)_ starting the server the way the runbook documents honours `AETHERIS_PLAYGROUND_TOKENS`, or the docs state the supported way to start it so the override is reached; carried by a test or by a recorded disposition.

---

### BL-277 — `compile.aetheris_worker` copies the worker and exec-server binaries unconditionally, so any mix invocation fails while either is running
- state: open
- type: defect
- area: harness — compile task
- priority: high · size: S
- evidence: docs/evidence/BL-277.md
- done-when: _(proposed)_ a mix invocation succeeds while previously built binaries are running — **both** the worker and the exec server, verified separately — by a staleness check or an equivalent; carried by a test or a recorded disposition.
