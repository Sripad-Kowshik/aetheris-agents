# Backlog — 2026-06 (closed)

> **Terminal rows only**, split out of [`backlog-2026-06.md`](backlog-2026-06.md) at
> ds t1b. A row is here iff its title section carries `**Status:** DONE`; `UNRULED` is
> not terminal and stayed. Every section an id owns travelled with it.
>
> The **id is the address and the path is never load-bearing**. This file is not in the
> project-knowledge export set. `## ` container headings are reproduced from the open
> file so a row keeps its context; they are the only lines here that are not verbatim
> from the original.

---

### BL-135 — `run_helpers_timeout_test.exs:84` is timing-flaky: a 200 ms feeder against a 300 ms bound (#TBD)
**Status:** DONE
**Size:** S · **Priority:** medium · **Section:** harness (`../aetheris/test/aetheris/cli/commands/run_helpers_timeout_test.exs`)

Filed 2026-08-09 from **hc-d r3's** ticket-boundary gate run — off-territory, the way the gate rule
intends, and filed the day it was found rather than carried.

**The observation.** `mix test` returned **exit 2**, `972 tests, 1 failure`:

```
1) test a status change alone counts as activity, with no events at all
   (Aetheris.CLI.Commands.RunHelpersTimeoutTest)
   test/aetheris/cli/commands/run_helpers_timeout_test.exs:84
   right: {:error, "run await-status-activity-8610 stalled: no status or event
           activity for 300ms (last status: running, last event seq: -1)"}
   stacktrace: test/…/run_helpers_timeout_test.exs:98
```

**Not caused by the ticket that found it.** hc-d r3's diff (`48f59e7`) touches
`scripts/sprint.sh` and nothing else — no `lib/`, no `test/`, no `config/`. The three preceding gate
runs in the same cycle all reported `972 tests, 0 failures`.

**The mechanism is structural, and visible in the test's own source.** A feeder task writes four
status changes with `Process.sleep(200)` between them, while the assertion runs
`await_bounded(run_id, await_inactivity_timeout_ms: 300)`. **A 100 ms margin.** Any scheduling delay
that pushes one 200 ms sleep past 300 ms fires the inactivity bound and the test fails. The gate run
that caught it was executing concurrently with sprint runs and filesystem watchers.

**Not reproduced, and that is stated rather than glossed.** **9 attempts, 0 reproductions**: 8
consecutive runs of `…:84` on an idle machine (8 PASS), plus 1 run under deliberate CPU load (6 spin
loops) which also passed. So the failure is real and observed, and the conditions that produce it
are **not** established — only the 100 ms margin that makes it possible.

**Do not "fix" it by widening the bound alone.** `await_inactivity_timeout_ms` is the behaviour under
test; inflating it to buy margin weakens the assertion it exists to make. The likely correct shape is
to make the feeder's activity observable rather than timed — drive it off a signal the assertion can
wait on — or to give this test an explicitly generous bound *with the reason recorded*, so a later
reader does not read the number as the contract.

**Done when:** the test is either deterministic under load, or its timing margin is stated as
deliberate with a recorded rationale, and 20 consecutive runs under CPU load pass. Until then the
gate runs **expected-flaky, named with this row's ref** per the tracked-carry clause — named in
packets, not re-triaged, and **not relaxed**.

`Source: hc-d r3 ticket-boundary gate run, 2026-08-09 (harness 48f59e7, agents 4222804). One
observation; the non-reproduction is recorded above as part of the evidence, not omitted from it.`

> **`[FOLDED into BL-075, 2026-08-09 (hc-e's opening edit, E3). Same defect — this row should not
> have been filed. Kept, not deleted, because the fold and its reason are the record.]`**
>
> **They are the same defect, established from the rows and the source, not from resemblance.**
> BL-075's m4 close-b annotation already names the identity in full — same module
> (`Aetheris.CLI.Commands.RunHelpersTimeoutTest`), same file and line
> (`test/aetheris/cli/commands/run_helpers_timeout_test.exs:84`), same stacktrace line (`:98`),
> same assertion (`await_bounded(run_id, await_inactivity_timeout_ms: 300)`), and the same error
> shape (`stalled: no status or event activity for 300ms … last event seq: -1`). The only
> difference between the two observations is the generated run id — `await-status-activity-7139`
> at close-b, `-8610` here — which is `System.unique_integer` and distinguishes nothing.
>
> **Not two tests in one module, and not two failures of one test.** One test, one assertion, two
> observations seven days apart. `grep -c 'run_helpers_timeout_test'` over `../aetheris/scripts/`
> is not the question; the question is the module's test count, and the row above named a single
> `test …:84`.
>
> **So this row is a duplicate, and the error is mine.** The gate rule says a red gate gets a
> tracked ticket *the day it is found* — it does not say file without looking. I filed BL-135 at
> hc-d r3 without searching the backlog for an existing row on the same test, and BL-075 not only
> existed but already carried the identical stack trace. **The count error is over a population of
> size two:** filing a second row for one defect, exactly as filing one row for two would have
> been.
>
> **What BL-135 contributes, folded onto BL-075 above as a third observation:** the 2026-08-09
> failure with its own date and evidence, and — new — **nine non-reproductions** (8 idle runs of
> `:84`, one under six CPU spin loops, plus a full green suite), which is the first time the
> reproduction conditions have been probed rather than only the failures counted. **The warning
> against the tempting fix stands and is not duplicated:** widening
> `await_inactivity_timeout_ms` weakens the assertion, because the bound *is* the behaviour under
> test — which is BL-075's own *"fixed-ms window rather than a poll"* mechanism class, and
> BL-054's §Suggested order entry already names the cure.
>
> **Status:** folded. Track the defect on **BL-075**. This row stays as the record of the
> duplication and of the non-reproduction evidence.

---

## Housekeeping (do first, near-zero effort)

### BL-001 — Capture clean drift baseline (#42)
**Status:** DONE
**Size:** S · **Priority:** now

Every drift_check output recorded so far predates at least one parser fix
(paren-depth, payload `?` marker, `_evaluate_payload_fields` extraction).
There is no recorded genuinely-clean run.

- Run `python3 scripts/drift_check.py` with `AETHERIS_DB_PATH` set.
- Expected (as observed 2026-07-15): 8 PASS, 0 FAIL, 0 WARN. The 8th PASS
  is the `project_knowledge` check. INFOs fall in two benign categories:
  `env_vars` (agent-side vars in specs §1 not read by Rig) and
  `payload_fields` (event payload fields observed in the DB but not yet
  promoted to specs §6). The phantom `runs.finished_at` and
  `llm_responded.stop_reason` INFOs must be gone.
- Append the summary line to `docs/rig/current-state-2026-06.md` as
  "Drift baseline 2026-07-XX: …".

**Done when:** baseline recorded; any unexpected finding triaged.

**Status:** Done 2026-07-15 — baseline in `current-state-2026-06.md`,
commit `d24e482`. Expectation lines above corrected to observed reality
per review finding 1 (`docs/reviews/bl-001-review.md`).

---

### BL-015 — Promote nine observed payload_fields to specs §6 (#66)
**Status:** DONE
**Size:** S · **Priority:** now (before BL-002)

> Numbered BL-015, not BL-010 as the review draft suggested — BL-010
> through BL-014 are existing boxy-pipeline tickets. GitHub issue #66.

The 2026-07-15 baseline (`d24e482`) reports nine payload fields observed
in DB events but absent from specs §6: `prompt_built.key`,
`prompt_built.tool_schema`, `llm_responded.content`,
`llm_responded.tool_input`, `llm_responded.tool_name`,
`llm_responded.type`, `tool_result.is_error`, `tool_result.result`,
`error.detail`. Per the BL-006 logic, observed fields get promoted — but
the §8 errata's `llm_called`/`llm_responded` divergence means each field
needs a canonical-name confirm before promotion, not a mechanical copy.

Split from BL-001 review finding 3. Ordered before BL-002 so BL-002's
single export catches the promoted fields, the corrected backlog, and the
new baseline in one manifest refresh. `stop_reason` stays with BL-006 —
still zero rows, its trigger hasn't fired; BL-015 does not subsume it.

**Done when:** each field has a disposition (promoted to §6 / errata note
/ anomaly triaged); drift_check shows zero `payload_fields` INFOs, 0 FAIL,
0 WARN.

**Status:** Done 2026-07-15. 6 canonical fields promoted to specs §6
(`prompt_built.tool_schema`; `llm_responded.tool_name`/`tool_input`;
`tool_result.result`/`is_error`; `error.detail`) — each confirmed against
current harness emission (`loop.ex:170/244/245/352/355`,
`agent/server.ex:529`). 3 fields errata-noted in specs §6, **not**
promoted: `prompt_built.key` (test-fixture `{"key":"value"}`) and
`llm_responded.content`/`type` (pre-2026-05-15 legacy emission, superseded
by `raw_response`/`response_type`) — all confined to 2026-05-12 rows.
Residual after this ticket: 3 `payload_fields` INFOs (legacy DB rows;
clear on dev-DB reset, DB read-only here) and 2 `project_knowledge` WARN
(manifest staleness from the BL-001 + BL-015 doc commits — BL-002 owns the
refresh and the clean re-verify, per BL-001 review finding 2).

**Tracked follow-up (event-triggered, not scheduled — BL-006 pattern):** a
dev-DB reset clears the three BL-015 documented-legacy payload INFOs
(`prompt_built.key`, `llm_responded.content`/`type`). **Gated on BL-003
completion** — the pre-2026-05-15 legacy rows share the May window with
BL-003's orphaned-`running` fixtures, so a reset before BL-003 consumes
them would destroy fixtures. (Note surfaced during BL-015: the DB now holds
76 `running` rows, not five — BL-003's "five orphaned rows" count is itself
stale and wants re-checking when BL-003 is scoped.)

---

### BL-002 — Refresh Claude project knowledge files (all three scopes) (#43)
**Status:** DONE
**Size:** S · **Priority:** now

The Claude.ai project still carries the 2026-05-31 snapshot (superseded
handoff, pre-fix specs/architecture/runbook). This staleness is what
triggered the entire reality-check exercise. The refresh must cover all
three scopes, not just Rig:

**Rig** (replaces current stale set):
- `docs/rig/specs.md`, `docs/rig/architecture.md`, `docs/rig/runbook.md`,
  `docs/rig/milestones/p3/protocol.md`, `docs/rig/current-state-2026-06.md`
- `rig/CLAUDE.md` if conversations will touch Rig implementation
  (it is the authoritative Claude Code context for that subtree)

**aetheris-agents repo** (mostly new additions):
- Repo-root `CLAUDE.md` (refresh — now carries the doc-sync DoD)
- `docs/agent-creation-guide.md` (CLAUDE.md names it the authoritative
  agent-building reference; currently absent from project knowledge)
- `docs/capability-matrix.md` (what agents exist; orchestrator plans
  from it; needed for any "which agent does X" conversation)
- `docs/backlog-2026-06.md` (this file)

**aetheris (harness)** (currently zero representation):
- `aetheris/CLAUDE.md` if it exists (verify) — the harness-side Claude
  Code contract. Harness *source* facts (schema, event types, trajectory
  format) are deliberately NOT exported raw; they live verified in
  `current-state-2026-06.md` §7/§8/3.1 and the corrected specs.md.

**Drops:** the superseded handoff (banner already redirects) and
`docs/rig/README.md` (redundant with architecture + current-state).

**Manifest:** add `docs/project-knowledge-manifest.md` — one table:
file → commit hash at export. Refresh the manifest with every export.
This makes project-knowledge staleness mechanically detectable: the
next reality-check (or a future drift_check check) compares manifest
hashes against `git log -1 --format=%h -- <file>`.

- Convention going forward: refresh at the same boundaries the
  reality-check prompt runs at (milestone end / before handoff), and
  the manifest is part of the export, not optional.

**Done when:** project knowledge matches HEAD for all three scopes and
the manifest exists in-repo.

**Status:** Done 2026-07-15. Repos rule added to root `CLAUDE.md`; BL-001
/ BL-002 / BL-015 marked complete here and on the roadmap Active line;
`../aetheris/CLAUDE.md` confirmed present (27 KB) and in the export set.
Manifest regenerated as the final commit (hashes at HEAD after the doc
edits): `rig--specs.md`, `rig--current-state-2026-06.md`,
`backlog-2026-06.md`, `aetheris-agents--CLAUDE.md`. drift_check re-verify
at HEAD: 8 PASS / 0 FAIL / 0 WARN / 7 INFO. The Claude.ai upload itself is
the human step; export file list + hashes delivered in the packet.

## Harness (aetheris/)

### BL-003 — Startup sweep for orphaned `running` runs (watchdog, cure side) (#44)
**Status:** DONE
**Size:** M · **Priority:** high

Rig's "stalled?" marker (commit `0eddf20`) is the *detector*; the DB still
lies forever. As of the 2026-07-15 baseline (verified `d24e482`),
`priv/aetheris.db` holds **76** `status='running'` rows — not the five May
rows the earlier draft assumed (corrected per BL-002 review finding 2).
Census (reference fixture — re-run at execution time, see done-when):

| Last event | Count | True state | Sweep action |
|---|---|---|---|
| (no events) | 11 | orphaned | `run_orphaned`, `finished_at`=`started_at` |
| `llm_called` | 30 | orphaned | `run_orphaned`, `finished_at`=last-event ts |
| `tool_called` | 22 | orphaned | `run_orphaned`, `finished_at`=last-event ts |
| `prompt_built` | 3 | orphaned | `run_orphaned`, `finished_at`=last-event ts |
| `run_complete` | 6 | finished (status lagged) | reconcile → `done`, `finished_at`=event ts |
| `error` | 4 | errored (status lagged) | reconcile → terminal, `finished_at`=event ts |
| `agent_waiting` | 0 | none paused currently | synthetic fixture required |

- **Pre-flight — this is the project's first ticket that WRITES to the DB
  (76 status mutations, a new event type, `finished_at` stamps).** Before
  the first sweep run, copy `priv/aetheris.db` aside (plain file copy; the
  harness must not be running during the sweep). The census is the
  acceptance fixture; the backup is the undo button if the sweep mishandles
  real rows on first contact. Record the backup path in the implementation
  notes; delete it after the done-check passes.
- On harness application start (and/or a `mix aetheris sweep` task), find
  runs where `status='running'` and the owning process is provably gone
  (no live GenServer for the run_id; last event older than a **named config
  threshold** — see below).
- **Orphaned (66, no terminal event):** mark `failed`; emit a new
  **`run_orphaned`** event type — per harness rule 14 this is a three-place
  change in one commit: `event.ex` union **and** `Trajectory.File`
  `@event_type_map` **and** specs §6, then drift_check. `finished_at` =
  last-event timestamp; for the 11 no-event rows, `started_at`. **Never
  sweep time** — that fabricates the dormancy gap into the run duration.
- **Reconcilable (10, last event `run_complete`/`error`):** adopt the
  terminal outcome the events already record — set `runs.status` to
  `done`/error and `finished_at` to the terminal event's timestamp; emit
  **no** new event (the trajectory already tells the truth); log one
  reconciliation line. Do **not** overwrite a real outcome with `failed`.
- Must not touch legitimately paused runs: a run whose latest event is
  `agent_waiting` with an unexpired `wait_condition` in `run_checkpoints`
  is paused, not dead. **Zero such runs exist in the current DB** — the
  exclusion path has no live fixture, so build a **synthetic
  `wait_for_event` run** during the ticket to exercise it; do not assume
  it is present.
- The liveness **threshold is a named config key**, not a buried constant:
  name it, pick a default with one sentence of rationale, and document it
  in `runbook.md` (runbook update rule — operational knob, same commit).
- Specs §6's `run_orphaned` row **notes the status mapping** (event
  `run_orphaned`, status `failed`) so the event/status asymmetry reads as
  designed, not accidental.
- Write `finished_at` when sweeping (note: Rig's `TrajectoryMeta` treats
  missing `finished_at` as `""`).

**Do not:** change Rig's stalled? detector (ships as-is; this is the cure
side); clean up the BL-015 legacy event rows (separately gated on this
ticket's completion).

**Done when:** re-run the census pre-sweep (fresh numbers, not the
`d24e482` reference) → sweep → post-sweep counts match that fresh census:
orphaned rows marked `failed` with `run_orphaned`, reconcilable rows
adopted to their recorded terminal outcome, **0** rows remain `running`;
both censuses in the implementation notes; a kill-9'd run is swept on next
harness start; a synthetic `wait_for_event` run survives; drift_check
passes (`--strict` if BL-009 landed).

**Status:** Done 2026-07-15. `Aetheris.Sweep` ships the cure: startup hook
(after checkpoint resume, gated by `config :aetheris, :sweep_on_start`,
default on) plus `mix aetheris sweep`. New `run_orphaned` event type added
via the rule-14 three-place change (`event.ex` union + `Trajectory.File`
`@event_type_map` + specs §6, one commit); drift `event_types` parity holds
at 22 types. Fresh pre-sweep census matched the `d24e482` reference exactly
(66 orphaned / 10 reconcilable / 0 paused); post-sweep **0** rows remain
`running`. Liveness threshold is the named config key
`:sweep_liveness_threshold_ms` (default 300 000 ms, mirroring Rig's "stalled?"
display detector; documented in `runbook.md`). Paused-run exclusion exercised
with a synthetic unexpired `wait_for_event` fixture (survives, not merely
created). Methodology §6 repo-qualified-Touches rule batched into this commit
per the approved promotion. Implementation notes + both censuses in
`../aetheris/docs/aetheris/milestones/bl-003-startup-sweep-implementation-notes.md`.

---

### BL-004 — Per-run token totals in RunSummary (#45)
**Status:** DONE
**Size:** S · **Priority:** low

Gap A residual ("Rig-side addressed" note in current-state doc): cost
landed in the run list; token totals did not.

- Same pattern as `total_cost_usd` in `harness.rs` `harness_list_runs`:
  correlated subquery `SUM(json_extract(payload_json,'$.input_tokens'))` /
  `'$.output_tokens'` over `type='llm_responded'` (tokens live ONLY in
  `llm_responded` — see specs §6 / report errata).
- `RunSummary` + `types.ts` + optional column or tooltip in `RunList.tsx`
  (the table is at 8 columns; consider folding tokens into the Cost
  cell's tooltip instead of a 9th column).
- Update specs §3; run drift_check.

**Done when:** token totals visible per run; NULL stays NULL for stub runs.

**Status:** Done 2026-07-20 — `total_input_tokens` / `total_output_tokens` added to
`RunSummary` as correlated subqueries mirroring `total_cost_usd`, surfaced in the
Cost cell's `title` tooltip (table stays at 8 columns), commit `c39bf7e`. No
`COALESCE`: NULL stays NULL, verified against stub fork runs. Cross-checked against
`usage.rs`'s differently-shaped aggregation — 57591 input tokens both ways on
`docbuilder-orch-iDGIIQ`. Columns appended after `total_cost_usd` so `row.get`
indices 0–10 are unshifted.

**Correction:** "Update specs §3" above is a **stale structural pointer**. §3 is
*Trajectory File Schema*; the Tauri command structs live in **§4**, which is also the
section `drift_check.py` parses. §4 is what was edited. A backlog row quoting doc
structure decays exactly like a `file:line` citation does — same class, different
surface (review finding 3, `docs/reviews/bl-029-review.md`).

---

### BL-016 — Fix standing `payslip_orchestrator` test failure (#67)
**Status:** DONE
**Size:** S · **Priority:** medium

`test/aetheris/agents_test.exs:22` ("payslip_orchestrator.exs evaluates to a
valid RunConfig") is **red on `main`** and has been since before BL-003.
Surfaced during BL-003's suite run and triaged per the standing pristine-HEAD
rule: with BL-003's work stashed, `mix test test/aetheris/agents_test.exs`
still fails identically (`git stash push --include-untracked` → run → pop), so
it is not a BL-003 regression. Evidence in `docs/reviews/bl-003-review.md`
finding 2 and `bl-003-startup-sweep-implementation-notes.md`.

- The test asserts `agents/payslip_orchestrator.exs` resolves to tools
  `["run_command", "spawn_agent", "wait_for_all"]` (test lines 43–45), but the
  agent file currently yields only `["run_command"]` — `assert "spawn_agent" in
  result.tools` fails (`left: "spawn_agent", right: ["run_command"]`).
- Decide the source of truth: either the agent file lost `spawn_agent` /
  `wait_for_all` (restore them) or the test is ahead of the file (correct the
  assertion). Do not silently delete the assertion.

**Why it matters:** a standing red test normalises "1 failure is expected" and
lets the *next* real failure hide behind it (alarm fatigue). Close it so the
suite is 0-failure and a new red is unambiguous.

**Done when:** `mix test` is green with no excluded/expected failures; whichever
side was wrong (agent file or test) is corrected with a one-line rationale.

**Status:** Done 2026-07-15. Evidence resolved the fork: `git log -p` on
`payslip/agents/payslip_orchestrator.exs` shows commit **5abd4b9**
("refactor(payslip): move employee loop into generate script, remove LLM
iteration") deliberately dropped `spawn_agent`/`wait_for_all` — the LLM was
mangling employee IDs when iterating, so the same commit rewrote
`generate_employee_payslips.py` to loop over all employees internally. This is
the deliberate-sequential branch, aligned with the ROADMAP "Sequential over
parallel for independent agents" principle — so the **test was stale**, not the
agent file. Fixed in the harness (`test/aetheris/agents_test.exs:22`):
`tools == ["run_command"]`, `context_strategy == :full`; the stale spawn-based
assertions and `max_spawn_depth == 2` corrected, not deleted. The ROADMAP
uc-payslip description (the current-state mirror that still claimed "Parallel
sub-agents via spawn_agent + wait_for_all") was corrected in the same change.
`payslip/milestone.md` left as-is: it is a point-in-time milestone record of the
as-built parallel design, not a current-state claim.

---

### BL-025 — Verify: effect classes / record-and-serve for effectful tools (#TBD)
**Status:** DONE
**Size:** M · **Priority:** medium — **DONE 2026-07-23**

**Landed.** `Aetheris.Execution.EffectClass` declares `:pure` / `:contained` /
`:uncontained` as the single source of truth; `Verifier` record-and-serves `:uncontained`
tools by default and reports them **served, not verified** (excluded from the verified
tally); `aetheris verify <traj> --allow-effects` opts back in. Proven by a hermetic
localhost listener: **0 inbound connections** under default verify, **1** under
`--allow-effects`. A completeness test asserts the classifier is total over
`Registry.names/0` and every in-process tool module, mutation-checked.

**Scope grew, by human decision in-cycle (rev 2, 2026-07-22).** `aetheris verify` never
reached `Verifier` at all — `Commands.Verify` started a fresh **live** run
(`mode: :verify`) and returned `verified: true` unconditionally. The CLI was rewired to
`Aetheris.verify_run/2` and now returns the real verdict with a failure-reflecting exit
code; the vacuous `verified == true` test was replaced with a mutation-checked pass/fail
pair.

**Contract edits (§8, human-approved in-cycle):** determinism-contract **§3** (verify row;
plus a new paragraph separating `verify` the command from `RunConfig mode: :verify`) and
**§5** (full rewrite: taxonomy, record-and-serve, served-not-verified, mechanized
tripwire). Draft: `docs/reviews/bl-025-contract-draft.md`.

**MCP scope note:** the MCP *family* is classified `:uncontained`, not `http_call` alone.
Because MCP tool names are discovered at runtime, classification falls back to the recorded
`"source"`/`"server_id"` — with `server_id == "aetheris_exec"` held `:contained`, since the
internal exec server routes `run_command` and all eleven `git_*` as MCP calls.

**BL-027 folded in (human call, 2026-07-23).** `verify_step/2` now reads the recorded result
through the same `"output"`-else-`"result"` fallback as the served path. Without it, BL-025
would have shipped the crash as the behaviour of the command it had just made real: any
trajectory with a failed contained tool call took verify down. See BL-027 for the red-first
evidence; the payload-key *convention* residue is BL-046.

**Deliberately not closed here:** capability-level egress safety. `run_command` stays
`:contained` (rev 3) and its allowlisted interpreters can still egress — named as a §5
limitation, tracked by **BL-042**. Follow-ups filed: BL-042, BL-043 (`http_call` is
SIGSYS-killed in every mode), BL-044 (`mix aetheris` discards exit codes), BL-045
(`mode: :verify` misnomer), BL-046 (payload-key convention).

---

**Original row:**

`verify` **re-executes** every recorded tool call against a live worker
(`verifier.ex:136`, `Client.execute/2`). For a pure tool that is the point; for an
effectful one it is a hazard. The motivating case: verifying a run that called
`http_call` performs the network egress **again** — real requests to a third party,
from what an operator reasonably reads as a read-only check. A verify over a run
with a destructive tool call would re-perform the destruction.

Determinism contract §5 names this; `verifier.ex:130-136` is the mechanism.

Shape to consider: classify tools as pure / effectful, and for effectful ones
*record-and-serve* the recorded output rather than re-executing — verifying the
transcript's consistency without re-entering the world.

**Done when:** verify cannot re-perform an external effect without an explicit
opt-in; `http_call` is covered by a test that asserts no egress during verify.

---

### BL-027 — Verify: `KeyError` crash on paired in-process tools (#TBD)
**Status:** DONE
**Size:** S · **Priority:** medium — **DONE 2026-07-23 (folded into BL-025)**

**Closed.** `Verifier.verify_step/2` now reads the recorded result through the same
`recorded_result/1` fallback (`"output"`, else `"result"`) that the record-and-serve path
uses — one reader, both paths. Red-first evidence, on a trajectory whose recorded
`read_file` **failed**:

```
** (KeyError) key "output" not found in:
   %{"is_error" => true, "result" => "Error: :enoent", "tool_name" => "read_file"}
   verifier.ex:201  Aetheris.Execution.Verifier.verify_step/2
→ after the fix: 6 tests, 0 failures; the step reports :output_mismatch with
  recorded_output "Error: :enoent" — a genuine divergence, legibly, instead of a crash.
```

**Why it was unparked rather than left on its trigger.** The stated trigger — a
multi-agent/orb trajectory — was **too narrow**, and the row's in-process framing was the
reason. `Loop.record_tool_error/7` writes *every* recorded tool failure under `"result"`
with `"is_error"` and no `"output"` key, including for **contained, worker-dispatched**
tools. So a single failed `read_file` or `run_command` — a routine shape, needing no orb —
crashed verify. BL-025 made `aetheris verify` actually route through `Verifier`, which would
have shipped that crash as the operator-visible behaviour of the command it had just made
real. Human call, 2026-07-23: fold the fix in rather than release that state.

BL-025's record-and-serve independently removed the *in-process* face (those tools are
`:uncontained` and no longer dispatched), so the residual this fix closes is precisely the
contained-tool face the original row did not describe.

**Not closed here — tracked as BL-046:** the payload-key *convention* itself, shared with
BL-028. This row fixed the reader; it did not unify the writers.

---

**Original row:**

**Same trigger and ratification as BL-026: activates on the first `verify` run
against a multi-agent / orb trajectory.** Human-ratified 2026-07-19. Recorded, not
scheduled.

`verify_step/2` reads the recorded tool output with
`result_event.payload |> Map.fetch!("output")` (`verifier.ex:133`) — a hard fetch,
not a lookup with a default. But **in-process** tool writers emit the payload under
`"result"`, not `"output"` (`loop.ex:421-497`). So verifying a trajectory whose
tools ran in-process raises `KeyError` and takes the verify down.

The tools that hit this are exactly the orb/coordination ones —
`wait_for_event`, `read_blackboard`, `write_blackboard` — which is why the trigger
is a multi-agent/orb trajectory: that is the first trajectory shape that can
contain them, and the crash is unreachable until one exists.

**Trigger correction (BL-025, 2026-07-23) — the stated trigger is too narrow, and the
in-process framing is now stale in both directions.** Two changes:

1. **The crash never needed an orb trajectory.** `Loop.record_tool_error/7` writes *every*
   recorded tool failure — including worker-dispatched, contained tools — under `"result"`
   with `"is_error" => true` and **no `"output"` key at all**. So a trajectory containing a
   single failed `read_file` or `run_command` reaches the same `Map.fetch!` and crashes
   verify. Demonstrated at BL-025 against a recorded `http_call` failure before that tool
   was reclassified:
   `** (KeyError) key "output" not found in: %{"is_error" => true, "result" => "Error: :timeout", …}`
   at `verifier.ex:133`. The parked-on-trigger status understates reachability accordingly.

2. **BL-025 sidesteps the in-process case without fixing this row.** The in-process tools are
   now classified `:uncontained` and record-and-served, so verify no longer dispatches them
   and the `"result"`-key crash is unreachable *for them*. The residual — and the real scope
   of this row now — is a **`:contained`** tool whose recorded result is an error. Do not
   read BL-025 as having closed this; the hard fetch on the re-execution path is untouched.

Fix shape unchanged: read the recorded result with a fallback (`"output"`, else `"result"`),
as `Verifier.serve_step/1` already does on the served path — the two paths should share one
reader.

Note the shared root cause with BL-028: two independent consumers of recorded tool
results each assume `"output"` while a family of writers uses `"result"`. Worth
fixing as one payload-key convention rather than two point patches.

**Done when:** verify tolerates both payload keys (or the writers converge on one),
with a test over an orb trajectory — and the trigger has occurred.

**Evidence base (added 2026-07-21, BL-028 round 2 — annotation only; trigger,
ratification and parked status all stand unchanged).** Root-cause map and fix-space
analysis in BL-028's implementation notes
(`../aetheris/docs/aetheris/milestones/bl-028-implementation-notes.md`). Note in
particular: `record_tool_error/6` writes `"result"` (`loop.ex:354`) for **every**
recorded tool error regardless of which tool raised it — so the `KeyError` is
reachable on any trajectory containing a tool error, not only orb trajectories. The
trigger's wording stands as ratified; its reachability is wider than the row's
"multi-agent / orb" framing implies.

---

### BL-028 — Fork reconstruction drops `"result"`-keyed tool output (#TBD)
**Status:** DONE
**Size:** S · **Priority:** medium

`event_to_messages(:tool_result)` reads `Map.get(payload, "output", "")`
(`fork.ex:101-105`). Many in-process tool writers store the payload under
`"result"` instead (`loop.ex:354,424,435,450,459,469,482,492,508`). Because the read
**defaults to an empty string**, those tool results reconstruct as tool messages
with **empty content** — silently. The fork starts from a transcript in which the
tools appear to have returned nothing, and nothing in the output says so.

Silent-empty is the dangerous part: a fork that should have failed loudly instead
proceeds from a subtly wrong context.

`fork.ex`-local fix, but a behaviour change beyond t2's four goals, which is why t2
surfaced rather than fixed it. Shares its root cause with BL-027 — see that entry.

**Done when:** fork reconstruction carries `"result"`-keyed tool output, with a
test asserting non-empty reconstructed content for an in-process tool.

**Status:** Done 2026-07-21 — read-side fix in `event_to_messages(:tool_result)`
plus `normalize_content/1` (nil → `""`, non-binary → JSON-encoded; contract §2's
string invariant), commit `9b2b102`. Three test arms, each verified red-first.
Citations above describe the pre-fix file and are left as written; post-fix
locations in the contract's repaired citations and
`../aetheris/docs/aetheris/milestones/bl-028-implementation-notes.md`. BL-027
annotated same round (`16de968`), not reopened. Review:
`docs/reviews/bl-028-review.md`.

---

### BL-030 — Early-return `fork_run` (spawn without blocking to completion) (#TBD)
**Status:** DONE
**Size:** M · **Priority:** medium

`mix aetheris fork` blocks until the forked run finishes: the CLI reveals the new
run id only via `RunHelpers.await_run/1` at the end (`fork.ex:37`,
`run_helpers.ex`). Every consumer inherits the block — Rig's "Fork from here"
button sits disabled for the full run, which for a real fork is minutes.

Wanted: a spawn-and-return-early shape like `orchestrate_start`, which needs the
**harness CLI to emit the run id at fork-start** rather than at completion. Once it
does, Rig can navigate to the child immediately and let it stream.

Harness-touching enhancement, ratified-tracked at BL-007 t3 and explicitly not t3
or t4 scope — the t4 affordance ships against the blocking contract on purpose.
Pairs naturally with BL-031: an early-return fork makes the unbounded `await_run`
loop far less load-bearing.

**Done when:** the fork CLI can emit the run id at start; Rig's affordance returns
without waiting for completion.

**Status:** Done 2026-07-26. Harness: `cli/commands/fork.ex` emits the run id
between `start_fork/3` and `await_fork/1`, per resolved mode
(`{"status":"forked","run_id":…}` under `--json`); `output_mode/1` moved from
`Aetheris.CLI` to `Formatter.resolve_mode/1` so the command can resolve the same
mode the closing `print/2` uses. The CLI still blocks to completion — deliberately:
the fork run is a Task in the CLI process's own supervision tree, so an early
return would kill it. Rig: `fork.rs` spawns piped and owns the child, returns at
the first `run_id` line, and hands the running subprocess to a detached thread that
drains both pipes and reaps; `handleForked` sets `status: 'running'` so
`TrajectoryView`'s existing BL-005 events-fallback polling streams the child.
`--detach`/`--follow` untouched (daemon path). Notes:
`docs/rig/milestones/bl-030-early-return-fork-implementation-notes.md` +
`../aetheris/docs/aetheris/milestones/bl-030-implementation-notes.md`. Scout:
`docs/reviews/bl-030-fork-early-return-scout.md`. Review: `docs/reviews/bl-030-review.md`
(r1, approve; F1 non-blocking, fixed at harness `f79365a`).

**Closed 2026-07-26 after three rounds and a confirmed GUI pass.**

- **r0** — the early-return fork itself (harness `ae0c510`, agents `b5e8eee`).
- **r1** — completion transition, folding BL-063 (agents `4bf0fd6`). A fork
  watched to completion stayed in BL-005 reconstructed mode: the trajectory file
  that now existed was never re-read, so provenance / `started_at` / duration
  appeared only after a manual tab-out/in. Scouted first, and the scout changed
  the mechanism: the `run_complete` **event** precedes the file write
  (`loop.ex:267` → `server.ex:680` → `server.ex:456`), so a reload triggered by
  the event races it, while one gated on the row's **terminal status** cannot.
  Status-gated, no retry. Packet `docs/reviews/bl-030-r1-review-packet.md`.
- **r2** — source-seeded selection (agents `c2af6cf`). r1's per-consumer fix left
  the Events header reading the synthesized summary directly: `new Date('')` →
  "Invalid Date", with `label` and `model` blank from the same cause. The
  **Adjacent-case** class — the blast radius was one consumer wider than the view
  the fix was written against. Closed at the source: `handleForked` now seeds the
  selection from the real `runs` row (`runSummaryFromDetail/1`), so the invented
  summary is gone and there is no consumer list to keep in step. Incidentally
  retires a documented compromise — a labelled fork now hands its label to a
  grandchild without a Refresh. Packet `docs/reviews/bl-030-r2-review-packet.md`.
- **GUI pass confirmed end-to-end** on the real app: Trajectory (r1) — provenance
  banner, the amber "live — reconstructed" banner clearing in place at completion,
  incremental steps; Events (r2) — real label, run_id, model and `Started:` date
  on first landing, no re-select.

Carried out of this ticket as their own rows: **BL-062**, **BL-064**, **BL-065**.

> **Dangling ref, deliberate.** Determinism contract §4 says "the CLI and Rig entry
> points pass a label only (BL-030)". That sentence is still **true** after this
> ticket — BL-030 did not add overrides — but its `(BL-030)` ref now points at a
> closed ticket that never carried them. The override work split out as **BL-062**,
> whose §8 edit repoints it. Flagged rather than left to rot: §4 already carries one
> decayed parenthetical (D2's `cli/commands/fork.ex:47-55`, per the scout), so this
> section has form.

---

### BL-031 — `await_run` has no timeout or cap (#TBD)
**Status:** DONE
**Size:** S · **Priority:** medium

`await_run` (`cli/commands/run_helpers.ex`) is a poll-forever loop —
`Process.sleep(200)` + `Store.get_run`, with **no bound**. If a terminal status
never lands, the CLI spins forever, and so does any Rig `invoke` wrapping it.

This was the **amplifier**, not the cause, of BL-007 t4's field hang: a store
`:busy` crash stopped statuses landing, and the unbounded loop turned that into an
indefinite hang. t4 fixed the store side (`059c92e`), so statuses land and the loop
terminates today — which is exactly why this stayed out of that emergency fix
(scope held to three store changes).

It remains a latent resilience defect: **any** future cause of a stuck
non-terminal status reproduces the hang, with no timeout to convert it into a
legible error. Surfaced at t4 r3 F7.

**Done when:** `await_run` bounds its wait and returns a timeout error naming the
run and its last-seen status.

**Status:** Done 2026-07-21 — inactivity bound on `{status, max_event_seq}` with
paused-run exemption via `Aetheris.RunPause` (shared with Sweep by construction),
config key `:await_inactivity_timeout_ms` default 300 000; harness `4392194`+`a935038`,
notes/agents `6defe0e`+`d0690a6`; r2 also fixed a boot-crash regression in `Store`
event deserialization (compile-time type map) and filed BL-040. Review:
`docs/reviews/bl-031-review.md`.

---

### BL-034 — `prompts/bl-002-refresh-project-knowledge.md` has a self-staling step order (#TBD)
**Status:** DONE
**Size:** S · **Priority:** medium

The BL-002 prompt is **internally contradictory**, and has been since it was written.
Step 2 writes `docs/project-knowledge-manifest.md` with each file's current hash. Its
closing constraint then says to *append* a drift-baseline line to
`docs/rig/current-state-2026-06.md` — a file the manifest tracks. That append moves
`current-state`'s hash past the value just recorded, so the manifest is stale for that
row the instant the step completes. The same constraint also says to "run drift_check.py
once at the end to confirm exit 0 and **zero WARN**" — which the preceding instruction
has guaranteed cannot happen.

~~Evidence it fired in production, not just on paper: at the 2026-07-17 export
(`628f15f`) the manifest recorded `current-state` at `d24e482`, two commits behind
`628f15f`. The row was born stale.~~ — **WITHDRAWN as false, 2026-07-22. This claim was
never verified and does not hold; see the Evidence correction in the Status block below.
The hazard is real but latent — it never fired.**

The general rule the fix must encode: **any file the manifest tracks is edited *before*
the manifest is written, never after.** BL-007 Phase B hit this and sequenced around it
by hand — the manifest regen was made the last commit of the export, after the rider,
this row, and the notes had all landed.

Not fixed inline at BL-007 t5 Phase B because the Phase B scope was the export itself,
and editing the prompt mid-export is the same class of ordering mistake the row
describes.

**Done when:** the prompt's step order puts every manifest-tracked edit (including the
drift-baseline append) before the manifest write, and the "zero WARN" assertion is
reachable — or the baseline append is dropped from the prompt if it is not worth the
ordering constraint.

**Status:** Done 2026-07-22. Resolved by **dropping the baseline append** (decision:
drop, human call 2026-07-22). The append was the sole reason BL-002 wrote a
manifest-tracked file other than the manifest, so removing it makes the manifest the
only tracked write and trivially the last. **Three defects closed in
`prompts/bl-002-refresh-project-knowledge.md`:** (1) the ordering hazard this row
describes; (2) the `exit 0 and zero WARN` done-check the committed append made
unreachable; (3) an adjacent self-contradiction the row did not name — the constraint
declared current-state read-only (`read-only outside …manifest… and /tmp`) then ordered
a write to it four lines later. Defects (2) and (3) are demonstrable from the prompt
text alone.

**Evidence correction (supersedes this row's "it fired in production" claim).** The line
above — "at the 2026-07-17 export (`628f15f`) the manifest recorded current-state at
`d24e482`, two commits behind … born stale" — is **WITHDRAWN as false** (struck in place
above). A check-8 sweep of all 38 committed manifests is clean (38/38); no manifest was
ever born-stale. The two hashes are real (`d24e482` = the BL-001 baseline commit;
`628f15f` = a real export commit — the export HEAD named in manifest commit `d11464f`'s
Exported line, not a manifest commit itself) but the "two commits behind" relationship
between them was never checked — a **Cited-means-read** instance. At `d11464f` the
manifest pinned `current-state` at `d24e482` and the file genuinely last changed at
`d24e482`; the row was correct. The comparison made was per-file pin vs export HEAD, and
a per-file pin always lags HEAD — that is what it records. The hazard is real but
**latent, never fired**; the drop stands on the prompt's textual self-contradiction plus
latent-staleness, not on a production instance. The same false claim also appears in the
b1–b3 export manifest narrative (`docs/project-knowledge-manifest.md`, "reproducing the
2026-07-17 instance at `628f15f`") — it must **not** be repeated in the next manifest
regen; flagged here so the correction chases forward rather than silently recurring. The
manifest is deliberately not edited by this ticket (an out-of-scope tracked write).

The general rule is now encoded as a standing invariant in the prompt itself (the
manifest is the last tracked write; no manifest-tracked edit after Step 2), so a future
re-addition reads as the regression it is. The per-export drift-baseline capture is
intentionally **not** relocated — BL-001 (#42) captured the one-time clean baseline and
is Done; nothing consumes a per-export refresh. The overdue 2026-07-22 baseline is closed
by the same removal (no baseline is owed in current-state). The prompt file is not
manifest-tracked, so the fix stales nothing; this row's own edit stales
`backlog-2026-06.md` until the next export (expected, strict-exempt).

## Rig (aetheris-agents/rig/)

### BL-005 — TrajectoryView fallback for live runs (#46)
**Status:** DONE
**Size:** S–M · **Priority:** medium

`trajectory.json` is written atomically at run end (`server.ex:673,944`
via `file.ex:37-38`) — the file does not exist while a run is live, so
TrajectoryView errors for `status='running'`.

- On `trajectory_load` failure for a running run, build the same view from
  `harness_get_events`: `EventRow.payload` is a JSON *string* (SQLite) vs
  the file's inlined object — parse per row; payloads are complete/
  untruncated in both stores, so fidelity is identical.
- Reuse the existing step-grouping; show a "live — reconstructed from
  events" banner; optionally reuse the p2 polling hook for live append.
- `meta` is unavailable pre-completion except via `runs.config_json` —
  render what's derivable, leave the rest blank.
- Update the runbook troubleshooting entry ("use the Events tab for live
  runs") to reflect the new behavior.

**Done when:** opening Trajectory on a running run shows events instead of
an error; completed runs unchanged.

**Status:** Done 2026-07-15. `TrajectoryView` falls back to
`harness_get_events` + `harness_get_run` on `trajectory_load` failure and
rebuilds the step-grouped view via `src/lib/reconstructTrajectory.ts`; the
`run` prop replaces `runId` so the banner can vary by status. **Scope
widened** past "for a running run" per the ticket's own recommendation:
BL-003 swept 66 orphaned runs to `failed` with no trajectory file either, so
the fallback triggers on any `trajectory_load` failure, with the banner
reading `live — reconstructed from events` (running) vs `trajectory file
unavailable — reconstructed from events` (terminal — covers absent *and*
corrupt/`.tmp` files, with the read error logged to console). p2 polling reused
for live append (decision: **in** — free via the existing `useRunEvents` hook).
Fidelity verified byte-identical against a real 58-event `trajectory.json`,
guarded durably by `rig/scripts/verify-reconstruct-trajectory.ts`. Export JSON
hidden in reconstructed mode. No new Tauri command (specs §4 unchanged).

---

### BL-017 — Resolve `react-hooks/set-state-in-effect` lint failures (#68)
**Status:** DONE
**Size:** S–M · **Priority:** after BL-016 (standing-red gate)

`bun run lint` (`eslint .`) is red on `main`: **31** `react-hooks/set-state-in-effect`
errors across ~15 files. Origin is a bump of `eslint-plugin-react-hooks` that
promoted the rule to error — undated, because the gate had not been run
whole-project until BL-005 ran it off-territory (per the gate-boundary rule now
in `CLAUDE.md`). The flagged pattern is the idiomatic `if (!id) { setData(null) }`
reset at the top of the data hooks (`useHarness`, `useTrajectory`, `useRunDiff`,
the `use*` corpus/provenance hooks) plus a few views (`OrchestratorView:140`,
`PlaygroundView:295/325/333/341`). No BL-005 file is among them.

**Decide first, before touching any site:** does this codebase *adopt* the rule
(refactor all ~15 sites so effects don't call `setState` synchronously — the
lint-clean-per-file path) or *reject* it (disable the rule in `eslint.config.js`
with a comment stating why the guard pattern is acceptable here)? Pin the
decision in this ticket; do **not** let it be settled implicitly by silencing
errors file-by-file.

**Done when:** ~~`bun run lint` exits 0~~, and the adopt-vs-reject decision is
recorded (in the rule-config comment if rejected, or in the notes if adopted).

**Divergence noted (per the standing rule):** the "31 = one rule" premise was a
miscount — the true split is **28 `react-hooks/set-state-in-effect` + 3
`react-refresh/only-export-components`** (BL-016's gate line read only the
eslint tail). So BL-017's done-when is corrected to: *the 28
`set-state-in-effect` errors cleared, the reject decision recorded, and the
residual 3 tracked as BL-018 (#69)*. `bun run lint → exit 0` is delivered
jointly with BL-018 at one shared export boundary, not by BL-017 alone.

**Status:** Done 2026-07-16 (decision: **reject**, 2026-07-15 human call on
claude-ui recommendation). `react-hooks/set-state-in-effect` disabled rule-level
in `rig/eslint.config.js` (not 28 per-site comments) with the decision recorded
in the config comment: functionally-correct data-hook resets, rule targets
render hygiene not bugs, ~22 sites with no frontend test runner → refactor risk
without a net; revisit when a test runner exists. Lint went 31 → 3. The residual
3 are a different rule class (react-refresh) — surfaced as a finding, not swept
— and are BL-018's scope. See `docs/reviews/bl-017-review.md`.

---

### BL-018 — Resolve `react-refresh/only-export-components` lint failures (#69)
**Status:** DONE
**Size:** S · **Priority:** immediately after BL-017 (joint lint-green endpoint)

The residual behind BL-017's rule disable: **3** `react-refresh/only-export-components`
errors, pre-existing since 2026-05-31 (`ed63058`), hidden behind the 28
`set-state-in-effect` errors until BL-017's verify step surfaced them (origin:
BL-017 packet). Fast-refresh requires that a file exporting a component export
nothing else:

- `rig/src/components/ui/badge.tsx:37` — exports `badgeVariants` (cva helper)
- `rig/src/components/ui/button.tsx:67` — exports `buttonVariants` (cva helper)
- `rig/src/context/AppContext.tsx:103` — exports the `useApp` hook

Unlike BL-017's rule, this one has a standard zero-risk fix (extract the
non-component exports to their own modules), verifiable by `tsc -b` + `bun run
build` without a frontend test runner — so it is fixed, not disabled.

**Touches:** the 3 source files + new sibling modules (`badge-variants.ts`,
`button-variants.ts`, `app-context.ts`, `useApp.ts`) + `useApp` import sites
(Sidebar, RightPanel, TopBar); backlog status; the shared manifest regen.

**Done when:** `bun run lint` exits 0 (the joint endpoint BL-017 and BL-018
deliver together), `tsc -b` + `bun run build` green, decision-comment convention
followed (each new module cites BL-018 / #69).

**Status:** Done 2026-07-16. `badgeVariants`/`buttonVariants` extracted to
`*-variants.ts`; `AppContext` object + types to `app-context.ts` and the `useApp`
hook to `useApp.ts`, leaving `AppContext.tsx` exporting only `<AppProvider>`; the
3 `useApp` importers repointed. Verified `bun run lint → exit 0` (31 → 0),
`tsc -b` 0, `bun run build` 0 (1908 modules); no behavior change. This is the
shared export boundary that also clears BL-016's carried staleness WARN — its
named endpoint moved one ticket later than promised (BL-016 → BL-018), dated
here so the carry stays honest.

---

### BL-019 — Harness runbook: sweep section + mirror convention (#70)
**Status:** DONE
**Size:** S · **Priority:** now (before BL-007 planning)

BL-003's operational docs single-homed on the Rig side (`docs/rig/runbook.md`,
agents repo — per that ticket's Touches). The harness's own
`docs/aetheris/runbook.md` has no sweep entry, so a harness-side operator finds
nothing on `mix aetheris sweep`, the config knobs, or the startup hook. The gap
was invisible by construction: harness-side docs (methodology excepted) sit
outside every detection mechanism built this cycle — no manifest row, no drift
check, no export. Surfaced by human spot-check 2026-07-16.

Three parts: (1) sweep section in the harness `runbook.md`, describing
**observed** behavior — one real harness start performed during the ticket
confirms the startup hook's log line; (2) a header codifying the mirror
convention (the BL-016 mirror-vs-record distinction, applied); (3) decision —
manifest-track the harness runbook: **yes** (claude-ui recommendation; BL-007 has
operational surface and will touch this file — untracked mirrors are how this
cycle started).

**Done when:** sweep section present and matching observed behavior; convention
header in place; manifest row added; `drift_check --strict` exit 0 at the
closeout export.

**Approved deviations (on record, per the standing rule):**
- **Touches widened to `docs/rig/runbook.md`.** The Rig entry already carried the
  knob defaults/rationale and behavioral detail, so writing the harness section
  without trimming Rig would leave the same facts in two docs — and `drift_check`
  compares each doc against its *own* repo's git history, never cross-doc
  agreement, so divergence would be silent. That is the one rot class the tooling
  cannot see. BL-017/018's scope split separated *different fix classes*; this is
  one docs-only restructure of a single feature across its two mirrors, where
  splitting would manufacture the inconsistency rather than prevent one.
- **Convention wording supersedes the ticket's draft.** The drafted rule
  ("`runbook-m*.md` files are point-in-time milestone records") was written from
  inference; `ls` proves that glob also matches `runbook-model-comparison.md`, a
  *living* topic guide, which the rule would have frozen by name-accident. The
  taxonomy is three-way and **enumerated**: status is a property of the file, not
  its name — a category rule defined by filename pattern is exactly what failed.
- **Rider taken:** one-line status headers added to the three living topic guides
  so category is visible from inside each file, not only from `runbook.md`.

**Status:** Done 2026-07-17. Harness `runbook.md` gains: the three-category
convention header (canonical-for-current-state / milestone records / living topic
guides, plus a self-maintaining "add it to the correct list" line); `mix aetheris
sweep` in the CLI commands block; and a `## Orphan sweep` section placed after
*Checkpoint and resume* to mirror real boot order (resume → sweep). The section
documents the five-way verdict table, the `finished_at`-never-sweep-time rule,
both config knobs, idempotency, BL-003's worked census, and the highest-value
operational gotcha — a *just-killed* run reports `skipped_recent`, not a cure, and
only sweeps once staleness exceeds the threshold. Observed-behavior check ran
against the real DB; log line matched BL-003's documented behavior exactly, so the
"finding, not write-around" clause did not fire. Rig entry trimmed to badge +
cure command + cross-ref. `aetheris--runbook.md` joins the manifest — the harness
runbook enters project knowledge for the first time.

---

### BL-020 — Update HTTP-stack dependencies carrying security advisories (#71)
**Status:** DONE
**Size:** S–M · **Priority:** medium

Surfaced by the clean-clone smoke test 2026-07-17. `mix deps.get` on a fresh clone
prints "Found packages with security advisories"; `mix hex.audit` itemises them —
all in the HTTP stack (the Bandit / Req dependency chain):

| Package | Advisories |
|---|---|
| `req 0.5.17` | EEF-CVE-2026-49755 (**HIGH**), EEF-CVE-2026-49756 (LOW) |
| `plug 1.19.1` | EEF-CVE-2026-54892 (**HIGH**), EEF-CVE-2026-8468 (**HIGH**), EEF-CVE-2026-56814 (MEDIUM), EEF-CVE-2026-56813 (LOW) |
| `mint 1.8.0` | **8 advisories** — 49754 (HIGH), 48862 (HIGH), 56810 (HIGH), 58229 (HIGH), 49753 (MED), 59246 (MED), 59249 (MED), 48861 (LOW) |
| `hpax 1.0.3` | EEF-CVE-2026-58226 (**HIGH**) |

> **Table corrected 2026-07-17 by BL-020's pre-audit capture (a finding).** As
> first written, the `mint` row listed only 56810, putting the total at 8. The
> true count is **15**: `mint 1.8.0` alone carries **8** advisories. This was not
> upstream drift — the clean-clone smoke test was the same day — it was a
> reporting error: the table was composed from two *truncated* views of
> `mix hex.audit` (`head -20` and `tail -8`), capturing the first seven entries
> and the last one. Same failure mode as the BL-016 gate-line miscount:
> characterising a tool's output from a fragment. Note that BL-017's hardening
> ("gate lines quote the tool's actual summary line") would **not** have caught
> it — `hex.audit`'s summary line, `Found packages with security advisories`,
> carries no count. The generalised lesson: never compose a factual table from a
> truncated view; capture the whole output or count it programmatically.

No CI gate fails on these — deps resolve, `compile --warnings-as-errors` is clean,
suite green 857/0 from a clean clone. That is *why* they went unnoticed:
`hex.audit` is not in the gate set, so the advisories are invisible to every check
that runs at a ticket boundary. Reachable surface, not dormant: `req` backs the
LLM adapters, `plug`/`bandit` back the playground HTTP API.

- `mix deps.update` across the HTTP chain; re-run the full gate line.
- Sensitive area on update: the adapters' retry/timeout handling (see the
  `receive_timeout` note in CLAUDE.md — socket timeouts must stay terminal, not
  `:retry`).
- Open question for the ticket: should `mix hex.audit` join the CI contract, so
  this class surfaces at a boundary rather than by clean-clone spot-check?

**Done when:** `mix hex.audit` clean, or each residual advisory explicitly
accepted with a recorded rationale; full gate line green.

**Status:** Done 2026-07-17. `mix hex.audit` → **`No retired or security advisory
packages found`** (exit 0). All 15 advisories cleared; **no residuals**, so the
accept-with-rationale path was not needed and no human decision is pending.

Version delta (`mix deps.update req plug mint hpax`; `mix.lock` only — **`mix.exs`
unchanged**, since `~> 0.5` already permitted 0.6.x and `~> 1.0` permitted 1.20.x;
no constraint conflicts, no forced overrides):

| Package | Before | After | |
|---|---|---|---|
| `req` | 0.5.17 | **0.6.3** | target (0.x minor — see below) |
| `plug` | 1.19.1 | **1.20.3** | target |
| `mint` | 1.8.0 | **1.9.3** | target |
| `hpax` | 1.0.3 | **1.0.4** | target |
| `finch` | 0.21.0 | 0.23.0 | resolver-dragged (via req) |
| `telemetry` | 1.4.1 | 1.4.2 | resolver-dragged |

Six packages, nothing else — no opportunistic updates, so the diff stays
auditable *as* a security patch.

**`req 0.5.17 → 0.6.3` crossed a 0.x minor boundary** (breaking-change territory
for a 0.x library) and `req` backs every LLM adapter — the sensitive area. Verified
rather than assumed: `test/aetheris/execution/llm_adapter/gemini_test.exs:351`
("Req.TransportError timeout is terminal and not retried") stubs
`Req.Test.transport_error(conn, :timeout)` and asserts both that the error
surfaces (`{:error, "receive timeout"}`) **and** that it prevented the retry
(`call_count == 1`). It passes under 0.6.3, so `Req.TransportError`'s shape and
semantics survived the bump. No adapter code changed.

**Finding — asymmetric coverage (surfaced, not filled).** The identical terminality
branch exists in **two** adapters — `gemini.ex:79` and `anthropic.ex:91` — but only
Gemini has a test. Anthropic, the *primary production adapter* and the one CLAUDE.md's
`receive_timeout` note is explicitly written about, has none; its correctness here is
verified only by symmetry with Gemini (identical clause shape, and compilation proves
the struct still exists). Low risk, genuinely unverified. ~~Related: `ollama.ex` and
`openrouter.ex` set `receive_timeout` but never match `TransportError` at all, so a
socket timeout there falls to `{:error, _} -> {:error, :retry}` — the exact behavior
CLAUDE.md forbids.~~ Worth a ticket.

> **Correction 2026-07-17 (BL-021 verify step) — the struck sentence was false.**
> The anthropic coverage gap above is real and stands. The ollama/openrouter claim
> was not: **neither adapter has a `:retry` fallthrough, because neither retries
> anything.** `:retry` is an adapter-*internal* protocol consumed only by each
> adapter's own `with_retry/2`; `ollama.ex` and `openrouter.ex` have no
> `with_retry/2` and never emit `:retry`. Their catch-alls, quoted verbatim:
>
> ```elixir
> # ollama.ex:63 (call_native) and :83 (call_xml)
> {:error, reason} ->
>   {:error, "Ollama request failed: #{inspect(reason)}"}
>
> # openrouter.ex:49
> {:error, reason} ->
>   {:error, "OpenRouter request failed: #{inspect(reason)}"}
> ```
>
> Terminal binaries. A socket timeout in those adapters was **already terminal**;
> CLAUDE.md's rule governs adapters that retry, and is vacuously satisfied there.
> There was no live bug.
>
> **How the error was made:** `anthropic.ex`'s catch-all *is*
> `{:error, _reason} -> {:error, :retry}`. That file was read; ollama/openrouter
> were only *grepped* for `TransportError` (0 hits), and their catch-all shape was
> **inferred from the sibling** and asserted with `file:line` citations that made
> it look verified. Grep proved absence of X; it was treated as proving presence of
> Y. The citations are why it passed two reviews and propagated into BL-021 (#72)
> and BL-022's item 3. Promoted to CLAUDE.md as **Cited-means-read** (author side)
> and **Demonstration-not-citation** (reviewer side), extending **Complete-output**
> — which would *not* have caught this, since no output was truncated; the lines
> were simply never read.

**Gate recommendation on the pinned open question** — *should `mix hex.audit` join
the gate set?* **Adopted 2026-07-17** (human call on claude-ui recommendation).
`mix hex.audit` now sits in the harness CI contract after `deps.get`, with the
accept path written into CLAUDE.md rather than left implicit: advisories cannot be
suppressed (no ignore mechanism), so when no patched version exists the accepted
advisory gets a backlog rationale and the gate runs **expected-red, named with its
ticket ref** per the tracked-carry clause. Upstream-triggered red — a new advisory
arriving through nobody's commit — is the gate working, not a defect, and gets a
ticket the day it is found. Adopted knowingly with that tradeoff on record.

---

### BL-021 — Adapter socket-timeout terminality: test all four adapters (#72)
**Status:** DONE
**Size:** S · **Priority:** next (runnable standalone, harness-side)

> **Re-scoped 2026-07-17 by its own verify step, before any code was changed.** As
> filed, this ticket had two parts: (a) a coverage gap, (b) a "live violation" in
> ollama/openrouter. **(b)'s premise was false and (b) is withdrawn** — see the
> correction note in §BL-020 for the verbatim catch-alls and the how-it-happened.
> In short: `:retry` is an adapter-*internal* protocol consumed only by each
> adapter's own `with_retry/2`; ollama and openrouter have **no `with_retry/2` and
> never emit `:retry`**, so their socket timeouts were already terminal. There was
> no bug. The claim came from inferring their catch-all's shape from
> `anthropic.ex` and asserting it with citations to lines never read.

Origin: BL-020's packet. Verifying that `req 0.5 → 0.6` had not changed
`Req.TransportError` semantics surfaced that terminality is *tested* unevenly
across the four LLM adapters. CLAUDE.md's `receive_timeout` note requires
`%Req.TransportError{reason: :timeout}` be matched as **terminal**, never
`:retry` — a rule that binds adapters which retry, and is vacuously satisfied by
adapters which do not.

Actual state, verified by reading every catch-all:

| Adapter | `with_retry/2` | Timeout path | Was |
|---|---|---|---|
| `anthropic` | yes | `TransportError` clause (`:91`) precedes the `:retry` catch-all (`:94`) → terminal | correct, **untested** |
| `gemini` | yes | same shape (`:79` before `:82`) | correct, tested |
| `ollama` | **none** | catch-all → terminal binary | correct by construction, untested |
| `openrouter` | **none** | catch-all → terminal binary | correct by construction, untested |

**(a) Test the Anthropic terminality branch.** The load-bearing part.
`anthropic.ex:91` sits *before* the `{:error, _reason} -> {:error, :retry}`
catch-all, so without it a timeout reaches `with_retry/2` and is retried 6× with
exponential backoff — the exact CLAUDE.md scenario. Untested until now. Template:
`gemini_test.exs:351`, non-vacuous (error surfaces **and** `call_count == 1`).

**(b′) Regression guards for ollama + openrouter — tests only, no code change.**
Not vacuous: they lock in current-correct behaviour and fail the day someone adds
`with_retry/2` without excluding `TransportError`. The exact message is incidental
and deliberately unpinned; the load-bearing pair is *terminal (never `:retry`)*
and *exactly one call*.

**Done when:** all four adapters have a test asserting both that a socket timeout
surfaces as terminal and that no retry occurred; full gate line green (now
including `mix hex.audit`).

**Status:** Done 2026-07-17. Four tests, gemini's as the template for all.
`openrouter_test.exs` created (none existed; also gained an API-key-absent test).
**No adapter code changed** — none needed changing. The anthropic test was
**mutation-checked** rather than assumed load-bearing: removing the
`TransportError` clause makes it fail inside `with_retry/2` at
`Process.sleep/1` (anthropic.ex:113), blowing the 60 s ExUnit timeout — CLAUDE.md's
documented scenario reproduced. Findings promoted to CLAUDE.md as
**Cited-means-read** and **Demonstration-not-citation**. The 429-parity observation
became BL-023.

---

### BL-022 — Refresh harness architecture.md + manifest-track it (#73)
**Status:** DONE
**Size:** S–M · **Priority:** before BL-007 milestone docs (input to fork planning)

`docs/aetheris/architecture.md` was last refreshed around m13 and predates the
entire hygiene cycle (confirmed: last touched **2026-05-22**, `56fd1f8`).
Surfaced by human spot-check 2026-07-17 (claude-ui review of the project-knowledge
copy) — the same way the runbook gap was found, and for the same reason: **the
file is in project knowledge but has no manifest row**, so no mechanism watches
it. Second instance of the harness-doc blind-spot class (first: BL-019).

Verified-stale items (all found against the project-knowledge copy — **re-verify
each against source**):

1. **Event-type list (§Trajectory.Log)** enumerates 12 types; the `event_type()`
   union has 22 (drift-verified at parity all cycle, incl. `run_orphaned` from
   BL-003). Regenerate the list *from the union*, not by patching the delta.
2. **"Adding a new event type" says two places; rule 14 is three** (`event.ex` +
   `file.ex` + specs §6, one commit, drift-enforced). Following the doc as written
   produces a drift FAIL. Cite rule 14.
3. **§Known Limitations `receive_timeout` claim — verify, then add per-adapter
   nuance + a coverage pointer.** *(Rewritten 2026-07-17: as first drafted this
   item said the "Fixed" claim was over-broad because ollama/openrouter "carry the
   forbidden `:retry` fallthrough". That premise was false — see §BL-020's
   correction note and §BL-021. It is corrected here rather than carried, since a
   ticket built on a false premise produces a wrong edit.)* Expected outcome is now
   that the claim is **accurate but under-specified**, not over-broad. Verify
   against source, then say what "fixed" means per adapter: `anthropic`/`gemini`
   retry transient errors via `with_retry/2` and exclude
   `%Req.TransportError{reason: :timeout}` explicitly, so the clause is
   load-bearing; `ollama`/`openrouter` have no retry mechanism at all, so their
   timeouts are terminal by construction and the rule is vacuously satisfied. All
   four now carry a terminality test (BL-021, #72) — point at them. Do **not**
   restate this as "all four fixed the same way"; the two mechanisms differ, and
   flattening them is how the original error started.
4. **Adapter list (repo structure) omits `openrouter.ex`.** While correcting it,
   spot-check the whole repo-structure tree against `ls` — one omission found by
   eyeball suggests others; verify, don't assume the rest is current.
5. **No sweep anywhere**: add `Aetheris.Sweep` to the component narrative and the
   application-start/boot-order description (reseed → resume → sweep → optional
   API). Cross-ref runbook §Orphan sweep rather than duplicating the verdict
   table — BL-019's dedup rule applies.
6. ~~**Execution Modes table lists "Fork" as a shipped mode.** What exists is
   `Eval.AB.run_forked/5` (m11); `Aetheris.fork_run` is BL-007, unbuilt. Footnote
   the row to say exactly that.~~ **FALSE — struck 2026-07-17 by this ticket's own
   verify step. The table is correct; no change made.** `Aetheris.fork_run/3`
   **exists** (`lib/aetheris.ex:73`), backed by `Fork.from_step/3`
   (`lib/aetheris/execution/fork.ex`, since 2026-05-17), a CLI command
   (`cli/commands/fork.ex`), tests in both `execution/fork_test.exs` and
   `cli/commands/fork_test.exs`, and `:fork` is first-class in the mode union
   (`run_config.ex:115`). Acting on this item would have added a **false footnote
   to accurate content** — the failure mode inverted: not a stale doc, a stale
   reviewer.
   **How it happened (reviewer-side `Cited-means-read` violation):** the claim was
   written from the backlog's BL-007 scope sketch and the roadmap — *planning*
   documents — and asserted as code state; `lib/aetheris.ex` was never opened.
   Planning docs describe intent, and intent reads like fact. Caught only by this
   ticket's own instruction to treat its items as leads and re-verify against
   source. See `docs/reviews/bl-022-review.md`.
7. **Trajectory-file layout shows `meta.json` as a separate file**; BL-005 treated
   `meta` as inline in `trajectory.json`. Verify on disk against a real run
   directory; correct whichever is wrong (specs §3 is the tiebreaker).
8. **Add the current-state-mirror header** per BL-019's convention (this file is
   canonical current-state; milestone docs are the frozen records), and **add the
   `aetheris--architecture.md` manifest row** — confirmed absent today; the only
   `architecture` row is `rig--architecture.md`.

While in the file, sweep for *other* post-m13 staleness beyond the eight — the list
above is what a review of the exported copy caught, not a guarantee of
completeness. Anything found is corrected and named in the packet.

**Done when:** all eight items resolved with source-verified corrections; header +
manifest row in place; `drift_check --strict` exit 0 at the closeout export; the
refreshed doc uploaded to project knowledge (the copy claude-ui reads during BL-007
planning is the point of the ticket).

**Sequencing:** run **after BL-021 (#72)** — item 3 writes cleanest as a statement
of fixed reality rather than an annotation of a known bug, and BL-021 is the
smaller, sharper ticket. Fresh session each: BL-021 touches adapter code with
tests, BL-022 is a doc-verification sweep — different modes, don't chain them to
save a `/clear`. The two boundaries may share one export if run back-to-back, or
close separately. *(BL-021 landed 2026-07-17; item 3 rewritten in light of it.)*

**Approved deviation (on record):** **Touches widened to `../aetheris/CLAUDE.md`**
to correct **rule 14** in the same boundary. Item 2 required architecture.md to say
"three places"; rule 14 said "two". Fixing only the doc would manufacture a
cross-mirror contradiction that no tooling detects — the BL-019 logic exactly. Rule
14's text now matches what `drift_check.py` has always enforced, with the
enforcement behaviour cited as the evidence. This is a correction to enforced
reality, not a new rule.

**Status:** Done 2026-07-17. Eight items verified against source before any write —
**six true, two false-premised**, both false ones authored by the reviewer from
exported/planning docs and both caught by this ticket's own instruction to treat its
items as leads rather than facts. Landed: three-category convention header;
event-type list regenerated **from the union** (12 → all 22, table-formatted); the
three-place rule with rule 14 corrected alongside; `openrouter.ex` added to the
adapter tree — plus the spot-check the item asked for, which found the tree stale
well beyond it (7 of 9 tools and 6 execution modules were missing, incl. `fork.ex`);
`Aetheris.Sweep` added to the component narrative and the boot-order section
(reseed → resume → sweep → API, with *why* the order is load-bearing), cross-ref'd
to the runbook rather than duplicating its verdict table; the `receive_timeout`
claim given per-adapter nuance and a coverage pointer, with an explicit note that
flattening the two mechanisms is how BL-021's false report began; and the trajectory
layout corrected — `meta` is inline, no `meta.json` has ever been written (verified
on disk and against specs §3). Item 6 **not acted on** — the table was already
correct. `aetheris--architecture.md` joins the manifest. Findings: BL-007's scope
sketch annotated (its harness half already shipped); rule 14 corrected; the
reviewer-side `Cited-means-read` instance appended to CLAUDE.md. See
`docs/reviews/bl-022-review.md`.

---

### BL-029 — Rig reads the run label from the wrong place, for every run (#TBD)
**Status:** DONE
**Size:** S · **Priority:** medium

Both Rig harness queries read the run label out of `config_json`:

- `harness_list_runs` — `COALESCE(json_extract(r.config_json, '$.label'), r.run_id)`
  (`rig/src-tauri/src/commands/harness.rs:82-84`)
- `harness_get_run` — same shape (`harness.rs:196`)

But the harness **strips `label` from `config_json` before persisting it**:
`encode_config/1` does `Map.delete(:label)`
(`../aetheris/lib/aetheris/agent/server.ex:758`). The label lives in the dedicated
`runs.label` column (`../aetheris/lib/aetheris/store.ex:807`, backfilled by
`ensure_runs_label_column/1` at `:989`).

So the `json_extract` always returns NULL and the `COALESCE` always takes the
fallback: **Rig displays `run_id` as the label for every run.** The feature reads as
"labels aren't set" rather than as a bug, which is why it survived this long.

Not fork-specific — it affects every run in the list. Surfaced at BL-007 t3 while
chasing why forked runs showed no label; the t4 fork invoke omits `label`
accordingly, and can pass it once this lands.

One-line-per-site fix: read `r.label` / `label` from the column, keeping the
`COALESCE(..., run_id)` fallback for genuinely unlabelled runs.

**Done when:** both queries read `runs.label`; a labelled run shows its label in the
Rig run list and detail view.

**Status:** Done 2026-07-20 — both queries read `runs.label` with the
`COALESCE(..., run_id)` fallback retained, commit `c39bf7e`. Measured at the fix:
878 runs, 596 labelled, **0** with a label in `config_json` — so the old read
returned the fallback for every row, including the 596 properly named ones.
Batched with BL-004 per the sequencing table. The BL-007 t4 fork rider landed in
the same commit: a fork inherits its parent's label verbatim, guarded on both ways
`label` is not real (the COALESCE fallback, and the `label: ''` placeholder in
`handleForked`). Reviewed round 1 in `docs/reviews/bl-029-review.md`; merge gated
on the manual GUI pass (review finding 2). Backend real-vs-fallback distinction
deferred to BL-037 (review finding 5).
**F9 addendum:** the run detail header now shows the run_id when it differs from the
label, commit `5ad4bf2`. Making labels real had removed the operator's only view of
the run_id — the handle `mix aetheris inspect` / `fork` / `tree show` all take — so
restoring it is part of what BL-029 ships, not a separate fix (review finding 9).

---

### BL-036 — drift_check: field-level checking for specs §4 command structs (#TBD)
**Status:** DONE
**Size:** M · **Priority:** low

`check_tauri_commands` (`scripts/drift_check.py:194-238`) compares command **names**
only, three ways (`lib.rs` `generate_handler!` / `#[tauri::command]` fns / specs §4).
The *struct fields* documented under each command in §4 are entirely unguarded.

Found by: specs §4 documented `RunDetail` with an `events: Vec<EventRow>` field that
the real struct (`harness.rs`) has never had. Nothing caught it; it was noticed only
because BL-029 happened to edit that exact block. Corrected in the BL-029 + BL-004
commit. The same blind spot let `RunSummary.label`'s `// from config_json.label`
provenance comment stay wrong for as long as the bug itself lasted.

§6 payload fields already have a live-DB sampling checker (`check_payload_fields`) —
this is the §4 analogue. Likely approach: parse the ```rust fenced blocks in §4 for
`pub <field>: <type>` and compare against the corresponding struct in
`commands/*.rs`. The `?`-suffix optionality convention from §6 may be worth reusing.

**Done when:** a field present in a §4 struct block but absent from the Rust struct
(or vice versa) is reported; the checker is in the sprint's `--strict` run;
`tests/test_drift_check.py` covers both directions.

---

### BL-036 — DONE 2026-07-25

Landed as a **new check 9**, `command_fields` (`11675cc`), batched with BL-041(b) — both
are `drift_check` blind spots on one file surface. `check_tauri_commands` stays names-only
and three-way: the ratified shape was a separate check, not field logic folded into check 2.

**What it does.** Parses the ` ```rust ` fenced blocks under specs §4 for
`pub struct NAME { pub field: Type }` and compares against the same-named struct in
`rig/src-tauri/src/commands/*.rs`. The join key is the **struct name** — it appears verbatim
on both sides, and one fenced block may declare two structs (`TrajectoryEvent` +
`TrajectoryFile`). One shared field parser serves both sides (the doc blocks and the Rust
source are the same syntax); it drops `///` doc comments, trailing `// …` notes and `#[…]`
attributes, and is line-based rather than comma-split because a type may contain a comma
(`HashMap<String, String>`).

**Signals.** WARN on documented-but-absent (the phantom-field case this row was filed for),
struct-field-undocumented, type mismatch, and ghost struct. FAIL is reserved for the
structural "zero structs parsed from §4", matching every other check's shape. The §6
`?`-suffix optionality convention is reused: a documented `field?: T` is satisfied by
`Option<T>`, and `?` relaxes the **type**, not existence — a `field?` absent from the struct
still warns. §4 documents `Option<T>` directly today and uses no `?`; the convention is
forward-compatible and carries its own tests.

**Result at HEAD: clean** — 9 documented §4 structs, 52 fields, all matching
(`RunSummary`, `EventRow`, `RunDetail`, `HarnessStatus`, `TrajectoryEvent`, `TrajectoryFile`,
`PollResult`, `CapabilityMatrix`, `UsageStats`, against `commands/harness.rs`,
`trajectory.rs`, `orchestrate.rs`, `capability_matrix.rs`, `usage.rs`). The phantom
`RunDetail.events` was already corrected in the BL-029 commit, and nothing else had drifted,
so **no specs §4 edit was needed** — the row closes with nothing to reconcile rather than
with a silent fix. The green is mutation-checked, not asserted: neutering the absent-field
branch turns its tests red.

Sprint coverage is automatic — `sprint.sh`'s `drift_check` case invokes `--strict` with no
hardcoded check count, and the header/`Summary` lines were already computed from
`len(selected)`/`FINDINGS`.

`Source: 11675cc, 2026-07-25. Notes:
docs/rig/milestones/bl-041b-bl-036-drift-check-guards-implementation-notes.md.`

**r1 (review F1/F2/F3), `0d5127b`.** The closing PASS in check 8 is now gated on
structural failures too (see the BL-041 DONE section); `_field_types_match` carries a
docstring line naming its textual-matching limitation (F2 — no row, conditional on §4 first
documenting a qualified or aliased type); the ghost-struct scope became **BL-052** (F3).
Check 9's result at HEAD is unchanged: 9 structs, 52 fields.
Review: `docs/reviews/bl-041b-bl-036-review.md`.

---

### BL-053 — DONE 2026-07-25 — verify makes no filesystem-hash claim (#TBD)
**Status:** DONE
**Size:** S · **Section:** Harness (aetheris/) · Closes the **fs_hash strand of BL-048**

Landed at harness `915d582`, with the §3 contract edit ratified at `b4857eb` (r1). Diagnosis:
`docs/reviews/bl-048-fs-hash-diagnosis.md` (harness, committed in the same change). Contract
edit: `docs/reviews/bl-053-contract-draft.md` — **RATIFIED, option B** (§8, human, 2026-07-25).

**§3 changed in both cells, not one.** r0 struck "— and recorded vs. actual filesystem `fs_hash`"
from the `verify` row's Guarantees cell; review chose **option B** over a bare strike, so r1 added
an explicit non-guarantee to the same row's Does-NOT cell: *"any filesystem-state claim — the
comparison ranges over tool output only, so an unrelated file changing between record and verify
is not detected."* The reasoning: the row previously *told* operators verify compared filesystem
state, so a pure strike would make that change invisible to anyone who trusted the old claim, and
the loss below is exactly a non-guarantee worth stating where operators read guarantees. §5 is
untouched in both rounds.

**What was wrong.** `verify`'s comparison had a second arm —
`recorded_fs_hash != actual_fs_hash -> :hash_mismatch` — that could not fire for any tool.
`read_file`/`list_dir` stopped hashing at **`d4728af`** (2026-06-06), which removed a recursive
whole-sandbox-tree SHA-256 that reliably blew the 30 s GenServer timeout on a 31 GB / 52k-file
sandbox, and deleted `fs_hash.rs`. The exec-server family records and re-executes `nil`. Served
steps never reach a comparison. `write_file`'s hash is a digest of the *recorded input content*,
which re-execution reproduces by construction. So the arm compared `nil` to `nil`, fell through
to `:verified` — while §3's mode table told operators a filesystem hash had been compared. Two
Elixir tests still asserted the pre-`d4728af` `"sha256:"` shape and were three of BL-048's 15
failures.

**Ratified direction: delete and correct, do not restore.** `d4728af` is a correct fix for a real
defect and is not reverted. Verify's comparison is output value-equality over the deterministic
portion, full stop.

**What landed.** Verify-side deletes: the `:hash_mismatch` arm, `compare_status/4` → `/2`, the
`recorded_fs_hash`/`actual_fs_hash` extraction and step-map fields, the hardcoded exec-server
`fs_hash: nil`, `:hash_mismatch` from the `verify_report.ex` status union, and the per-step
rendering of both hashes. §3's clause struck; five mirrors corrected (`runbook.md`, `specs.md`
×2, `architecture.md` ×2). **Record side untouched** — the trajectory `fs_hash` payload field
stays (`null` for read tools, real for `write_file`); removing it is a schema migration touching
fork and the `payload_fields` drift check.

**Tests made honest, and one made non-vacuous.** `client_test.exs` now asserts
`Map.fetch!(result, :fs_hash) == nil` — `fetch!`, so the key must be *present and null* rather
than absent. `fs_hash_stability_test.exs` is **re-pointed at `write_file`**: it asserted
`hash1 == hash2` over two nils, so the stability property it existed to guard had not been
exercised since `d4728af` — the failing `"sha256:"` line was the only thing keeping it honest.
It now writes identical content twice, asserts a 64-char hex digest *before* comparing, and adds
a sensitivity case (different content → different hash) so the guarantee cannot be met by a
constant. Two verify tests asserting `Map.get(step, :actual_fs_hash) == nil` were changed to
`refute Map.has_key?` — `Map.get` on a deleted key also returns `nil`, so they would have kept
passing while asserting nothing.

**The real loss, stated plainly.** Whole-sandbox drift detection — an unrelated file changing
between record and verify — was removed at `d4728af` and is **not** restored here. Nothing
detects it today. If it is ever wanted it is a new, performance-aware feature (bounded to the
files a step touched, not the whole tree), not a revert.

**Evidence:** `requires_worker` 15 → 12 failures, the three fs_hash failures green and
non-vacuous; default `mix test` 934/0; `grep` confirms no remaining `:hash_mismatch` producer or
consumer outside explanatory comments; mutation-checked — reintroducing the arm turns the new
output-only verify test red (`verified: 0`, expected 1).

`Source: BL-048 fs_hash strand; diagnosis 2026-07-25. Review:
docs/reviews/bl-053-review.md (pending).`

---

### BL-038 — Run list: search/filter, and the LIMIT window hides old runs (#TBD)
**Status:** DONE
**Size:** S · **Priority:** medium

Two faces of one gap, surfaced together during BL-029's merge-gate check (2026-07-20).

**No search.** At 250+ visible runs (878+ in store), locating a run by id or label
means scrolling. A text filter over label + run_id on the loaded rows is the minimum;
it makes labels (real as of BL-029) actually navigational.

**The window is silent.** `harness_list_runs` is `ORDER BY started_at DESC LIMIT ?`
(`rig/src-tauri/src/commands/harness.rs`), so runs older than the window are
unreachable from the UI with no indication they exist — an operator concludes "not
there" for a row that is. Concrete instance: `demo-01` (verified present, unlabelled,
forkable — 53 events, steps 0–9) invisible at the default limit. A client-side filter
alone does **not** fix this face: it filters the window, not the store. Minimum honest
fix is to show "N of M runs" so the cutoff is visible; the full fix is server-side
search (`WHERE label LIKE ? OR run_id LIKE ?`) or pagination.

The two faces share a failure shape with BL-029 itself: the UI stated something false
without appearing to state anything at all. There, every run's label silently read as
its run_id; here, the store silently reads as 250 runs deep. Both degrade to a
confident wrong answer rather than a visible gap, which is why both survived — an
operator has no prompt to doubt what they see.

**Relation:** BL-024's lineage view will need find-run-by-id anyway; whichever lands
first should carry the shared piece.

**Does not block BL-029.** An earlier draft of this row claimed it did, via the
`demo-01` / `run_zS6XSQ` candidates being windowed out. That claim was stale when
written and is struck: both candidates were deliberately retired, and the gate's
closure path moved to a stub fixture agent. The real obstacle to fork-based checks is
**BL-039** — real-provider fork continuation fails at the first LLM call — which no
amount of window-raising fixes, since a real-provider fork of any run fails
identically. Search/window and fork continuation are independent gaps.

**Done when:** an operator can locate any run in the store by id or label from the UI,
or the UI states plainly that it is showing a truncated window.

**Decided scope (2026-07-25, ahead of implementation): server-side, one filtering
path.** The row above offers "a text filter over label + run_id on the loaded rows"
as the minimum and server-side search *or* pagination as the full fix. Adjudicated:
**server-side search, no client-side filter layer, no pagination UI.** Two filtering
paths — client over the window, server over the store — can disagree, which is the
same silent-wrong-answer class the ticket exists to kill; a second path is a second
thing that can lie. The round-trip against local SQLite is sub-millisecond, so a
debounce is sufficient and the instant-filter layer buys nothing. Pagination is
dropped rather than built alongside search: search subsumes the navigational need and
building both is gold-plating an S.

Wire shape: `harness_list_runs` returns `RunListResult { runs, total_count }` rather
than `Vec<RunSummary>`; `total_count` is `COUNT(*)` under the same `WHERE` from the
same call. A separate `harness_runs_count` command was rejected — two calls can
straddle a concurrent write and desync the badge from the list.

**Status:** Done 2026-07-25 — `c0977c2` (agents). Both faces closed. Search filters
`WHERE runs.label LIKE ?term OR runs.run_id LIKE ?term` (`%term%`, metacharacters
escaped) on the **raw** columns, so an unlabelled run is reachable by run_id — `LIKE`
never matches the NULL label, and `demo-01` (NULL label, 879th of 896 by `started_at
DESC`) is the verified instance: absent from the unsearched 250-run window, returned
by search, proven against the real store by an opt-in live test arm. Window
disclosure renders "Showing N of M runs", with a second form while the client-side
*status* filter is active so the badge cannot misdescribe the rows on screen. Both
reads run inside one deferred read transaction — one command is not sufficient for
the stated invariant on its own, since two statements can still straddle a harness
insert. Notes: `docs/rig/milestones/bl-038-run-list-search-implementation-notes.md`.
**Merge gate closed** — manual GUI pass executed 2026-07-25 against the real 896-run
store: A/B/C/rider green, `Showing 500 of 896 runs` confirmed (BL-029 precedent; Rig
has no frontend test runner, BL-017). The expected badge is the **default** 500 window,
not the 250 the live test first used (review F1, fixed in `e4baddf`; arms and numbers
in the implementation notes). Review: `docs/reviews/bl-038-review.md` — no blocking
code findings; both in-cycle additions (LIKE-metacharacter escaping, single read
transaction) endorsed. Spawned **BL-058** (specs §5 TypeScript interfaces are
unchecked and already stale). Nothing pulled in from BL-037, BL-035, or BL-024.

---

### BL-039 — Fork continuation fails against real providers: reconstructed transcript carries a `"tool"` role (#TBD)
**Status:** DONE
**Size:** M (docs-first — the fix is a design choice with contract implications)
· **Priority:** medium-high

Forking a run and continuing it against a real provider fails at the **first LLM
call**. Two layers, and the second is why this is M rather than a one-line fix.

**Layer 1 — the immediate rejector.** `../aetheris/lib/aetheris/execution/fork.ex:104`
emits a message with `"role" => "tool"`:

```elixir
defp event_to_messages(%{type: :tool_result, payload: payload}) do
  tool_name = Map.get(payload, "tool_name", "")
  output = Map.get(payload, "output", "")
  [%{"role" => "tool", "tool_name" => tool_name, "content" => output}]
end
```

Anthropic accepts `user` and `assistant` only → HTTP 400 on the first call. This is
the only `"role" => "tool"` site in the tree.

**Layer 2 — why relabeling is insufficient.** Rewriting that message to the API's real
shape (a `user`-role turn carrying a `tool_result` block) would *still* be rejected: a
`tool_result` must pair with a preceding assistant `tool_use` block, and those are
never reconstructed. `event_to_messages(:llm_responded)` spans `fork.ex:87-98` and
drops every non-text response at `:95-96`:

```elixir
      _ ->
        []
```

So the contract's §4 known limitation — assistant tool-call turns are not
reconstructed — is not cosmetic. It is operationally fatal against any validating
provider.

**Minimal reproducer:** fork from any step whose `llm_responded` was a tool call. Step
0 of any tool-using agent hits it.

**Evidence.** `fork-aa6a6a65804f6645` — **human-executed via the Rig UI**, `fork_step:
0`, parent `payslip-orch-a7Vi3A`, `provider: anthropic`, 2026-07-20. `message_count: 2`
at seq 0 (user_prompt + the tool-role message; the parent's step 0 was a `run_command`
with no text response, so `event_to_messages(:llm_responded)` contributed nothing),
HTTP 400 at seq 2. This was the **first real-provider fork continuation ever
attempted**; all fourteen prior `fork-*` rows were stub-provider, and the stub
validates nothing. Full trail in `docs/reviews/bl-029-review.md`.

**Reproduced — three attempts, two distinct parents, all identical.** All human-executed
via the Rig UI, all `fork_step: 0`, `provider: anthropic`, `message_count: 2` at seq 0,
`HTTP 400: Unexpected role "tool"` at seq 2:

| fork run | parent | date |
|---|---|---|
| `fork-aa6a6a65804f6645` | `payslip-orch-a7Vi3A` | 2026-07-20 |
| `fork-333da479c4902361` | `payslip-orch-a7Vi3A` | 2026-07-20 |
| `fork-955dd155d2a8d4c4` | `payslip-orch-TVgr-Q` | 2026-07-21 |

100% failure rate on real-provider fork continuation; zero successes ever recorded. The
minimal reproducer is demonstrated, not inferred.

**And the stub "successes" are vacuous — the failure is universal, not real-provider-
only.** `encode_config` strips `stub_responses` (`../aetheris/lib/aetheris.ex:372`), so
a stub fork begins with an **empty queue**, receives `[stub exhausted]` on its first
call, and terminates at step 0. Confirmed on `fork-94c31612127f2009`: `llm_called`
(`stub-model`) → `llm_responded` (`[stub exhausted]`) → `run_complete`
(`agent_finished`). The fourteen green `fork-*` rows from 2026-07-19 are green for this
reason. **No fork on any provider has ever had a meaningful continuation** — real ones
are rejected at the first call, stub ones exhaust at it. Any future fix must be
verified against a fork that actually continues, since a `done` stub fork proves
nothing.

**Operator-facing symptom (noted, not separately filed):** the Rig UI surfaces this as
`Fork failed: [sandbox] entered user+mount namespaces … Error: run <id> failed` — the
sandbox preamble is carried into the error string and the actual cause (the HTTP 400)
does not appear at all. An operator cannot diagnose from the UI message; the reason is
only reachable by querying the events table. Whoever takes BL-039 or BL-030 should
decide which owns surfacing the underlying error.

**Fix space — sketched, not decided.** Either reconstruct assistant `tool_use` blocks
from recorded `llm_responded` payloads (if the payload retains enough to rebuild the
block), or fold tool results into user-role text and abandon structured tool
continuation. The choice changes what a fork *is* — whether it resumes a tool
conversation or replays a flattened one — so it is a contract decision, docs-first.

**Third consideration: the stub queue is stripped on fork** (`aetheris.ex:372`), which
is why no stub fork can exercise a continuation. Whatever the fix, it needs a test path
where a fork *actually continues* — either by carrying `stub_responses` across the fork
(cheap, test-only) or by an integration test against a recorded real transcript.
Without that, the fix's own verification would be as vacuous as the fourteen green rows
this row documents.

**Sequencing.** Ahead of BL-030: an early-return fork UX matters little while real
forks cannot run at all. **Builds atop BL-028's landed state** — BL-028's
`"output"`/`"result"` key fix is in this exact clause (`fork.ex:101-105`,
`Map.get(payload, "output", "")` at `:103`). Land BL-028 (b2) first; BL-039 must not
race it.

**§4 wording ratified 2026-07-26** — `../aetheris/docs/reviews/bl-039-contract-draft.md`,
with three edits (positional pairing named as an adapter dependency rather than a world
property; the id claim scoped to the harness; cross-provider fork carrying its
reachability caveat). Implementation is unblocked. The adjudication spawned **BL-059** —
the adapter silently discards parallel `tool_use` blocks, which is the *only* reason
one-call-per-step holds; BL-039 must not fix it, and its §4 clause records the coupling.
This row's own citations were corrected at HEAD by the scout memo
(`../aetheris/docs/reviews/bl-039-fork-continuation-scout.md`) — line numbers moved
post-BL-028, the "only `role => tool` site" claim is false, and the `aetheris.ex:372`
stub-strip attribution is wrong (the fork path never *sets* `stub_responses`; the cited
function is the scheduled-run template encoder). Conclusions unaffected.

**Done when:** a fork of a tool-using run continues successfully against a real
provider, or the contract states plainly that fork continuation is stub-only and the
UI refuses real-provider forks rather than failing at the first call.

**Status:** Done 2026-07-26 — harness `ebc3878` (docs-first §4 + §2 and runbook echo
sweep), `e44d35c` (implementation), `3f561d9` (notes); agents `7d6013a` (rig runbook +
fork fixture mirrors). Design A as ratified. A recorded tool step rebuilds as the
canonical pair — an assistant `tool_use` block and a `user` `tool_result` block sharing
a step-derived synthetic id — built through
`Aetheris.Execution.CanonicalMessage`, extracted from `loop.ex` so the live loop and
fork reconstruction have one definition. The record path is untouched: no `tool_use_id`
is added to any event. Part C ships in the same change —
`RunHelpers.terminal_error_reason/1` puts the fork's terminal `error` reason into the
CLI message, which previously read only "run \<id\> failed". No provider/model fork
overrides were built (BL-030).

**Done-when is met, demonstrated not asserted.** The `:requires_real_provider` arm was
run manually against Anthropic: **PASS**, and mutated back to the pre-fix shape the same
arm returns `HTTP 400: messages: Unexpected role "tool"…` — byte-identical to the reason
recorded in `fork-aa6a6a65804f6645`. That retires the hedge the §4 wording deliberately
carried (`bl-039-contract-draft.md` obligation 2). All three done-check arms are
mutation-checked; the stub-continuation arm asserts the reconstructed context as well as
the continuation, because the stub validates nothing and continuation alone would be a
fifteenth vacuous green. Notes:
`../aetheris/docs/aetheris/milestones/bl-039-implementation-notes.md`.

**Two corrections to the scout memo, recorded because they outlive this ticket.** The
memo's §4 "one constraint the design must respect" attributes key-dropping to
`Agent.Server.normalize_context_entry/1` and quotes both clauses fetching `"content"`;
at HEAD the atom-key clause fetches `:content`, and the function is **not on the wire
path** — it feeds `Agent.Server`'s `context:` state, while the adapter's messages come
from `Loop.run/5`, which uses `config.fork_context` unnormalized. The design instruction
(everything inside `content`) is unaffected; its stated reason was wrong. Also: the memo
is at `docs/reviews/bl-039-fork-continuation-scout.md` in **this** repo, not
`../aetheris/` as this row and the ticket text both say.

**Spawned BL-060** (`mix hex.audit` red on an upstream `bandit` advisory), found by an
off-territory gate run, and **BL-061** (review F1 — Gemini thought signatures are not
recorded, so a forked Gemini run does not round-trip them).

**Review:** `docs/reviews/bl-039-review.md` — approved, no blocking findings; two
non-blocking items dispositioned in r1 (`ebc3878`..`0e14500` plus the r1 commit).

---

### BL-067 — `capability_matrix_assemble.exs` computes its whole derived block in the LLM, so the Summary counts, the unique-tools line and the Overlap Report are unverified every regen (#TBD)
**Status:** DONE
**Size:** S · **Priority:** next · **Section:** aetheris-agents (`agents/capability_matrix_assemble.exs`)

Steps 2 and 3 of the assembler's prompt ask the model to *detect overlaps*, *count agents and
scripts per section*, and *list all unique tools* — three computations over content it has just
read, handed to an LLM. **Everything the assembler derives rather than pastes is in scope
here**; the counts are only the loudest instance.

**The counts.** Two consecutive runs at m1-cloudcost t5, same restored section files, both
wrong and wrong differently:

```
run cap-matrix-assemble-QWY6QQ : docbuilder 27 · Total 27 / 70
run cap-matrix-assemble-9bx1Pw : docbuilder 25 · Total 27 / 68
actual (counted from the emitted table rows) : docbuilder 24 · Total 26 / 67
```

**The unique-tools line** (t5 review, finding 2 — the same defect one line lower). It is
LLM-derived too, and it silently changed across this regen:

```
eeb37a1 : run_command, write_blackboard, send_message, read_blackboard, wait_for_event,
          spawn_agent, wait_for_all, read_file,            MCP servers (corpus_search, lattice)
6abc3e8 : run_command, read_file, write_file, spawn_agent, wait_for_all, write_blackboard,
          send_message, read_blackboard, wait_for_event,   MCP servers (corpus_search, lattice)
```

`write_file` appeared. It was not new — `context_builder.exs` has carried
`read_file, write_file, run_command` since m3, and that row is *in the same document*
(`docs/capability-matrix.md:164`). So the line was **wrong at `eeb37a1` and is right now by
luck, not by mechanism** — which is the proof that it is non-deterministic rather than
authoritative. A derived line that silently heals trains the same "probably fine" reflex as one
that silently rots. The **Overlap Report** (Step 2) is derived by the same means and has never
been checked at all; its agent-name column also churned this regen.

This is a direct violation of the repo's core principle (`CLAUDE.md` → "Scripts do; agents
decide… Never ask the LLM to construct file content or compute values programmatically"), and
it is a **Silent-wrong-answer**: every one of these outputs is well-formed and plausible inside
a generated artifact nobody recounts.

Not fixed at t5: the fix needs a deterministic generator, which means giving the assembler
`run_command` + a script, beyond that ticket's scope. t5 hand-corrected the three Summary
numbers to the verified values and said so in its packet; the tools line and overlap block were
left as the regen produced them.

**Fix:** `scripts/assemble_matrix.py` does the **whole assemble** — reads `docs/.sections/*.md`
in an explicit `SECTIONS` order, concatenates them verbatim, computes the entire derived block
(Summary table, unique-tools line, Overlap Report) from the sections' own table rows, and writes
`docs/capability-matrix.md`. `agents/capability_matrix_assemble.exs` is retired; sprint.sh's
`capability_matrix` case calls the script where it called the agent.

> Widened from "the generator emits the derived block to a file, the assembler pastes it
> verbatim" (this row's original Fix) because that leaves an LLM transcribing a counted block —
> the same fallible actor the fix exists to remove, and the m2a blob round-trip says it will
> improvise. Concatenation is not a task worth an LLM either.

**Done when:** the Summary counts, the unique-tools line and the Overlap Report are all
script-produced with no LLM in the assemble step; a regen is byte-stable for unchanged sections;
and a test **per derived value** asserts claimed == counted against the emitted tables (per-section
and total agent/script counts, claimed tools == union of the tool cells, claimed tool-set and
script-name overlaps == recomputed overlaps).

**Status:** Done 2026-07-30 — `scripts/assemble_matrix.py` + `tests/test_assemble_matrix.py`
(24 tests, each derived-value check mutation-verified), `agents/capability_matrix_assemble.exs`
deleted, `aetheris/scripts/sprint.sh` `capability_matrix` case calls the script. Commits
`de685fe` (agents) + `27bcd94` (harness). The regen corrected three Overlap Report defects the LLM had left standing (the
5-tool group listed 4 of 7 agents, the `write_blackboard, send_message, run_command` group was
missing entirely, and `docbuilder_orchestrator` was absent from the `run_command` group) — none
of which had ever been checked. Notes: `docs/milestones/bl-067-implementation-notes.md`.

> The matrix committed with this ticket was assembled over sections **restored from
> `HEAD:docs/capability-matrix.md`**, because a full section-agent regen still destroys curated
> prose (BL-068). That restore is a stopgap ritual; BL-068 retires it.

---

### BL-068 — A full capability-matrix regen destroys hand-curated section content, because `docs/.sections/` is gitignored (#TBD)
**Status:** DONE
**Size:** S · **Priority:** next · **Section:** aetheris-agents (`agents/capability_matrix_{uc}.exs`, `docs/.sections/`)

The section files are the only home for the matrix's curated prose, and they are gitignored.
Re-running all eight section agents therefore rewrites every section — reordering rows,
rewording purposes, and dropping the hand-added m3/m5/m6 provenance annotations in the
docbuilder Scripts table. m1-cloudcost t5 measured it: a 121-line diff for a one-section
addition, against 1–6 line diffs for the three prior matrix commits, i.e. previous sessions had
been regenerating only the changed section. That practice is correct, undocumented, and
unenforced — the artifact's durability rests on each session remembering it.

The current workaround is a manual ritual: reconstruct the sections from
`HEAD:docs/capability-matrix.md`, then re-run the assembler alone. BL-067 used it (its packet
says so), and it is the reason a full sprint regen is discarded rather than committed.

**Related:** `agents/capability_matrix_eduloka.exs` exists but is wired into neither sprint.sh's
`capability_matrix` case nor `SECTIONS` in `scripts/assemble_matrix.py`, and there is no
`docs/.sections/eduloka.md`; eduloka has never appeared in the matrix. Decide whether it joins
the matrix or the agent is deleted — either way it stops being an unwired ninth file.

**Fix direction:** give the curation a home the section agents cannot clobber — a committed
overrides file (`docs/capability-matrix-overrides.md` or JSON, keyed by use case + script name)
that `assemble_matrix.py` merges over the generated purpose cells, or a preserve step that
re-applies curated cells after a regen. The overrides route is preferred: it is deterministic,
diffable, and the assembler is already the single place every section passes through.

Raised at m1-cloudcost t5 (implementation notes, "`docs/.sections/` is gitignored, so a full
regen is destructive"); filed as a row at BL-067 per *a deferred finding gets a backlog row in
the same round it's deferred* — t5 left it as prose, which files nothing.

**Done when:** a full eight-agent regen preserves curated purpose text (or the curation lives
somewhere a regen cannot reach), so the restore-from-HEAD ritual is no longer needed; the
runbook's "Full regen loses curation" limitation is removed rather than documented; and the
eduloka question is resolved either way.

**Status:** Done 2026-07-30 — commits `e60bcfd` (agents) + `fd9ac48` (harness). `docs/capability-matrix-overrides.json` is the
durable home: committed, keyed by use case → `agents`/`scripts` → row key → field, merged by
`scripts/assemble_matrix.py` **before** anything is counted, so claimed == counted still holds
and an overridden Tools cell flows into the unique-tools line and the overlap tables like any
other. Seeded with the twelve known-fragile cells (eleven docbuilder m3/m4/m5/m6/rig-p9 purpose
annotations + provenance `search_agent.exs`'s prose Tools cell — the BL-067 §1e leak).

*Demonstrated, not asserted:* a full nine-agent regen ran and the section agents reworded **all
twelve** curated cells (every milestone marker gone), yet the emitted matrix is byte-identical to
`HEAD` in each of them — the overrides were load-bearing on every one, and the matrix committed
here is the regen's own output, with no restore-from-HEAD anywhere. An override matching no row
**fails the run** (exit 1), so a renamed script can no longer drop its curation quietly. The
runbook's "Full regen loses curation" limitation is deleted and replaced by a **Curated cells**
section.

**Eduloka: wired, not deleted** — `eduloka/` has a real surface (`eduloka_orchestrator.exs` +
14 scripts), so it joined `SECTIONS`, sprint.sh and the matrix (`eduloka 1 / 14`; totals 26/67 →
27/81). Wiring it exposed why it had never appeared: `max_steps: 15` against ~18 needed tool
calls, so its first live run ended `max_steps_reached` before writing its section. Raised to 30,
matching the scaling the other agents already use (provenance 16 scripts → 30, docbuilder 24 →
50). It had never been run since the day it was written.

---

### BL-066 — Bump `bandit` to `~> 1.12` (hex.audit HIGH, EEF-CVE-2026-65623) (#TBD)
**Status:** DONE
**Size:** XS · **Priority:** now (security gate red) · **Section:** harness (`../aetheris/mix.exs` + `mix.lock`)

Quadratic CPU blow-up reassembling fragmented WebSocket frames. Fix is a **version
bump, not an accepted advisory**: `aetheris/mix.lock` pins 1.11.1;
`aetheris/mix.exs:30` declares `{:bandit, "~> 1.0"}`; `mix hex.info bandit`
recommends `~> 1.12`.

**Touches:** harness repo (`aetheris/mix.exs` + `mix.lock`), tracked here per the
**BL-020** supply-chain precedent — same class, same ledger, so the advisory
history stays in one series instead of forking across two.

Surfaced off-territory by the m1-cloudcost t1 boundary gate, 2026-07-27. Until the
bump lands, `mix hex.audit` runs **expected-red, named with this ref**
(tracked-carry, not silent-carry).

```
Advisories:
  bandit 1.11.1 - EEF-CVE-2026-65623 (HIGH)
    aka: CVE-2026-65623, GHSA-vg8x-66vg-5pxh
    Quadratic CPU blow-up reassembling fragmented WebSocket messages in Bandit
    https://osv.dev/vulnerability/EEF-CVE-2026-65623

Found packages with security advisories
```

**Done when:** `mix hex.audit` is clean (exit 0), or any residual advisory carries
an explicit rationale on this row per the BL-020 accept path; the harness CI
contract passes with the bumped dependency.

**Status:** Done 2026-07-30 — commit `892b0f7`. `mix.exs:30` now declares
`{:bandit, "~> 1.12"}`; `mix deps.update bandit` resolved **bandit 1.12.4**, and moved two
co-resolved deps: `thousand_island` 1.4.3 → 1.5.0, `plug_crypto` 2.1.1 → 2.2.0 (`websock`
0.5.3, `plug` 1.20.3, `hpax` 1.0.4 unchanged). `mix hex.audit` → **`No retired or security
advisory packages found`**, exit 0 — verified after the bump, not assumed from the `~> 1.12`
constraint. Full CI contract green on the bumped tree: `compile --warnings-as-errors`,
`format --check-formatted`, `credo --strict` (2047 mods/funs, no issues), `dialyzer` (0
errors), `test` (969 tests, 0 failures, 133 excluded), plus `./scripts/sprint.sh
playground_api` — the Bandit-served path — green end to end.

> **Duplicate of BL-060**, which filed the same advisory one day earlier from BL-039's gate
> run; this row's "same class, same ledger" note missed it. Both closed by this commit. The
> harness has exactly one Bandit call site (`lib/aetheris/api/server.ex:25`,
> `Bandit.start_link(plug:, scheme:, port:, ip:)`) and no `WebSock` usage at all, so the
> advisory's fragmented-frame path was never reachable here — a bound on the exposure, not a
> reason the gate could have been left red.

---

### BL-069 — DO ≥1-orphan assertion is armed: its planted reserved IP is deleted (#TBD)
**Status:** DONE
**Size:** S · **Priority:** now (live failure mode) · **Section:** aetheris-agents (cloudcost)

> **Done-when superseded 2026-08-06 (m4 t2, step 0).** The row offers two ways to close and the
> cycle has ruled out both as written. **Decision 12** (`cloudcost/m4-consolidation.md`
> §Ratified decisions → Technical) retires planted cloud resources on every provider, and reframes
> re-pointing as a **rule-legibility assertion** rather than a recorded orphan fixture. So this row
> closes by **retirement** — a third branch its own Done-when does not contemplate. The Done-when
> is marked `[corrected 2026-08-06]` below with the superseded text kept beneath it. Everything
> else in this row is record — what was planted, when it was deleted, the one run the Linode leg
> went green — and is left intact.

The DO cloudcost pipeline's `≥1 orphan` end-to-end assertion is a **known-positive
pipeline self-test**, not a business alert — it proves detection *fires* against the real
bill, using a planted orphan as the fixture. Reserved IP **168.144.13.150** (NYC1),
that fixture, was confirmed deleted 2026-07-30 (m1 loose end closed). So the next
DO-inclusive run finds **0** DO orphans and the assertion either fails, or — worse —
greens **vacuously** off a prior run's gitignored output (Silent-wrong-answer, harness
`CLAUDE.md`). Independent of the AWS work; m2 is per-provider (decision H), so AWS carries
its own planted Elastic IP and does not depend on this.

**`[corrected 2026-08-06]` Done when:** the practice is retired rather than re-fixtured. The
cloudcost sprint case no longer asserts a planted orphan; in its place it asserts the property
that tripwire stood in for — that the adapter's inventory **reached the rule catalog in a shape
the catalog could read**: every emitted `type` drawn from `_normalized.CANONICAL_TYPES`, imported
rather than restated, and an empty illegible-skip set. A zero-resource inventory reaches a stated
not-applicable arm and never a pass. Mutation posture is owed on **every** arm, not only the
failing one. And every live instruction anywhere in either repo directing an operator to create a
billable cloud resource is removed; records of what was planted stay intact.

> *Superseded 2026-08-01 text, kept:* "**Done when:** before the next DO run, either a fresh DO
> orphan is planted, or the assertion is re-pointed to a recorded fixture rather than the live
> account — and a DO run confirms the assertion passes for the right reason (mutation posture: it
> must fail when no orphan is present)."

**The Linode leg went green once, 2026-08-05 — and reverted.** m3 t3 planted a zero-backend
`common` NodeBalancer (`aetheris-m3-bl069-plant`, `2405879`, us-southeast) and the assertion
passed for the right reason: run `cloudcost-orch-linode-h5lltQ`, 1 candidate, rule
`idle_load_balancer`, confidence 0.85, **$10.00/month**, priced from `/nodebalancers/types` and
independently corroborated by July's `NodeBalancer` invoice line at $20.00 for the two
pre-existing balancers. The plant is deleted after the run (`cloudcost/runbook.md:307-310`), so
the Linode leg **reverts to red** and this row stays armed. Recorded so the row does not read as
never-green: the mutation posture the Done-when asks for is already demonstrated on one provider —
t3's first live read found zero zero-backend balancers and the sprint was not run, then the same
read found one and the assertion passed. What remains is a *durable* fixture, on any leg.
**DO and AWS are untouched by this** — the DO reserved IP is still deleted and the AWS Elastic IP
is still `m2-milestone.md` §Prereqs 3, pending.

**DONE 2026-08-06 (m4 t2) — by retirement. The DONE section itself is written 2026-08-08 at the
m4 close, and that gap is this row's second finding.** The work closed at t2; the row was never
marked, so §Ticket set and §What t2 established both read *closed by retirement* while the row
read open. **§Close criteria clause 1 caught it** — *"a row closed in the repo and open here, or
the reverse"* — which is the one thing that clause exists to do, on the one row where it had
something to find. Assessed per clause of the amended Done-when, verified at harness `288c8ef`:

| Clause | Satisfied by |
|---|---|
| *the practice is retired rather than re-fixtured* | the `≥1 orphan` assertion is gone from `../aetheris/scripts/sprint.sh`; `grep` for `orphan candidates` / `expected ≥1` returns nothing |
| *in its place it asserts … every emitted `type` drawn from `_normalized.CANONICAL_TYPES`, imported rather than restated* | `sprint.sh:3025` — `from _normalized import CANONICAL_TYPES`; membership tested at `:3048`, not restated in shell |
| *an empty illegible-skip set* | `:3048` computes `outside`, and `:3055` names both the offenders and the canonical set on failure |
| *a zero-resource inventory reaches a stated not-applicable arm and never a pass* | three arms at `:3071–3075` — `ok` / `warn` (not-applicable, explicitly *"an unknown, not a clean empty account"*, citing BL-098) / `fail` |
| *mutation posture is owed on **every** arm, not only the failing one* | all three arms mutation-checked at t2, the two failing ones against real artifacts rather than invented fixtures (§What t2 established) |
| *every live instruction anywhere in either repo directing an operator to create a billable cloud resource is removed; records of what was planted stay intact* | t2's substance census over both repos; re-verified at this close — no live plant instruction in `cloudcost/runbook.md` or `sprint.sh`. The records above are **kept deliberately**: they are history, not instruction |

**Two sentences above are superseded by this closure and are left standing as record**, per
decision 7: *"the Linode leg **reverts to red** and this row stays armed"* and *"What remains is a
*durable* fixture, on any leg."* Both were true when written and were made false by decision 12 —
there is no durable fixture because there is no fixture; the assertion the row was armed on no
longer exists. **No cloud resource was ever planted for this cycle**, and none is owed.

`Source: m2-cloudcost ratification, 2026-08-01; m1 loose end (reserved IP) closed 2026-07-30;
m3-cloudcost t3 live run 2026-08-05 (Linode leg green once, reverted on plant deletion). Retired
at m4 t2, 2026-08-06 (harness f8bbac8). DONE section written at m4 close-c, 2026-08-08, after
§Close criteria clause 1 found the row unmarked.`

---

### BL-069 — DONE 2026-08-06 (m4 t2) — closed by **retirement**, neither branch its Done-when offered

The row offered two closures: plant a fresh orphan, or re-point the assertion at a recorded
fixture. Decision 12 ruled out the first and reframed the second, so the row closes a third way —
**the assertion and the practice behind it are retired outright**. The Done-when was corrected at
t2's opening, before any implementation, with the superseded text kept beneath it.

**What was removed.** `../aetheris/scripts/sprint.sh` no longer asserts `orphan candidates ≥ 1`;
the assertion and its KNOWN-RED comment block are gone, replaced in place by a comment recording
why and warning the next reader off reinstating a count-based orphan check. An assertion whose
only satisfying state is *money being wasted on a live account* is not a check on the pipeline.

**What replaced it — rule legibility, three arms.** Outside the `CLOUDCOST_PERIOD` guard (it reads
the provider output directory, not the report, so it stays meaningful on exactly the runs where
the report is missing — the D2 credential grep's precedent). It reads the run's own two artifacts,
both found by pattern rather than by period, and imports the canonical vocabulary from
`cloudcost/scripts/_normalized.py` (`CANONICAL_TYPES`) rather than restating it in shell:

| Arm | Condition | Output |
|---|---|---|
| legible | resources evaluated, every emitted `type` canonical, nothing skipped, catalog count agrees with the inventory | `[OK]` |
| illegible | a `type` outside the closed set, a non-empty skip set, or a count disagreement | `[FAIL]` |
| not applicable | zero resources | `[WARN]`, stated as an unknown — never a pass |
| vacuity guard | either artifact missing, or not exactly one | `[FAIL]` |

No new sprint output state; `fail()`'s effect on exit status untouched; nothing under
`cloudcost/scripts/` edited (all eight blob hashes unchanged).

**Why the third arm reports an unknown rather than a clean not-applicable.** Whether the adapter's
*coverage* was complete is recorded in no artifact the sprint can read — the inventory envelope is
five keys and carries no `not_inventoried` (**BL-098**), and the adapter's summary, which does
carry it, dies at its own stdout (verified: 0 occurrences across 13 archived
`sprint/*/cloudcost/run.json` captures). The orchestrator-exit assertion cannot discharge it
either, because `mix aetheris` discards every command's exit code (**BL-044**, verified at harness
`871a720`). **BL-098 is what would discharge it**, and it is out of scope for this cycle. So a zero
is reported as *nothing was evaluated, and why is not established here*.

**Mutation posture, all arms** — each state constructed, the arm observed, then restored. The two
`[FAIL]` fixtures are real artifacts rather than invented ones: `cloudcost/output/do_inventory_2026-07.json`,
a surviving pre-m2 inventory carrying `droplet` / `reserved_ip`, drove the out-of-vocabulary arm;
an entry with `type` removed drove the skip arm; a real zero-resource AWS inventory drove the
not-applicable arm; the live DO run drove the pass.

**Live outcome, before and after**, same leg, same day:

```
[FAIL]  orphan candidates: 0 (expected ≥1 — BL-069 armed: …)                    (18:25, pre-edit)
[OK]    rule legibility: 18 resources evaluated, 0 skipped; types
        [compute_instance, load_balancer, volume] all drawn from the canonical set  (18:29, post-edit)
```

**The retirement sweep.** Censused by substance across both repos, not by the token "plant". Live
instructions were treated under the cycle's document rules: `cloudcost/runbook.md` corrected in
place (decision 8); `CLAUDE.md`'s gate-rule exemplar corrected in place, since it read as an
endorsement of planting; `cloudcost/milestone.md`, `m2-milestone.md` (including the
`Status: PENDING` prerequisite, which was an instruction awaiting execution rather than a record)
and `m3-milestone.md`, plus three handoffs, each given one dated superseded note with its original
text intact (decision 7). Records were left alone. The full census — terms run, every hit, its
classification and its treatment — is in `cloudcost/docs/m4-t2-implementation-notes.md`.

**Not verified against a live account:** the m3 Linode plant `aetheris-m3-bl069-plant`
(`2405879`) is recorded as deleted in two places — this row above, and
`docs/project-knowledge-manifest.md` — and this session holds no Linode credential, so that
remains a record rather than an observation.

`Source: m4-consolidation decision 12; m4 t2, 2026-08-06. Live runs sprint/20260806_182514
(pre-edit, run cloudcost-orch-digitalocean-XApoxQ) and sprint/20260806_182911 (post-edit, run
cloudcost-orch-digitalocean-OK48Sw).`

---

### BL-070 — Retire the dormant cross-provider merge code in `compose_report_data.py` (#TBD)
**Status:** DONE
**Size:** S · **Priority:** low · **Section:** aetheris-agents (cloudcost)

m2 adopted per-provider reporting (decision H, no cross-provider roll-up), which makes the
N-merge, the `providers_without_prior_snapshot` caveat, the multi-currency "No combined
total" path, and the cross-currency 4-site aggregation all **unreachable**. m2 left them
**dormant** rather than deleting them, so `compose_report_data.py` stayed literally
unchanged and the "contract is mechanical" negative proof stayed pristine. Dead code that
is never exercised rots — delete it in a dedicated cleanup, not inside a ticket whose
result depends on `compose` not moving.

**Also converge the two slug functions — the risk class is silent-wrong-answer, not tidiness
(t2 review N1).** t2 added `_normalized.provider_slug()`, used by `detect_orphans` to write
`{provider}_orphan_candidates_{period}.json`; `compose_report_data.py` keeps an identical
private `slug()` for its history filenames. They were deliberately *not* converged at t2 —
that edit would have touched `compose` and spoilt the negative proof. Today both transforms
agree on every live provider token (`aws`, `digitalocean`), so there is no divergence to fix,
only one to prevent: a future provider whose name the two functions transform differently
would have `compose` silently find no orphans file and under-report — a well-formed report
with a section missing, not an error. Converge on the shared helper here, where `compose` is
already being edited.

**Done when:** the unreachable cross-provider merge / caveat / currency paths are removed
`[deferred 2026-08-07 — see the amendment note]`;
`compose` uses `_normalized.provider_slug()` and its private `slug()` is gone
`[DONE 2026-08-07, m4 t5b]`; the retained
single-provider compose has a test asserting its behaviour is unchanged; and the four m1 open
items those paths carried are marked resolved-by-deletion.

**Done-when amended 2026-08-07 (m4 t5b), before any deletion was made** — the same move t2 made
on BL-069 and t4b made on BL-074 clause 2: a row implemented against a premise the work has
already undermined is implemented against nothing.

*What changed.* **The cross-provider deletions are deferred, not cancelled**, pending **BL-131**.
The **slug convergence is discharged here**, independently of them, on §Contracts C9's explicit
assignment (*"BL-070 owns the convergence, to be taken when that file is next legitimately
edited"*) and on its own argument, which is divergence-prevention rather than reachability.

*What the deferral covers.* **Every target whose premise is decision-H-unreachability** — the
N-merge, the `providers_without_prior_snapshot` caveat, all four cross-currency aggregation sites,
and the multi-currency "No combined total" path — **not only the two that turned out to be
contract-covered.** m4 t5b's gate found C4 and C11 describing cross-provider behaviour as current,
but the premise is shared by targets no contract mentions, and a premise under question does not
become sound where nobody happened to write it down.

*Why the premise is under question — three states, not two.* This row calls the paths
**unreachable**; `cloudcost/milestone.md` §Open items calls them **"latent while m1 is DO-only
single-currency; live at the first fan-out"**; and m4 t5b's gate established a third reading: the
`--input-dir` route that reaches them is **declared in `cloudcost/tools.json` with a worked
example**, so it is an advertised interface that the orchestrator simply never invokes. Dead,
source-only, and live are three different things and this row assumed the first. BL-131 decides
which it is.

*One consequence recorded here rather than left to be rediscovered.* The multi-currency path is
reachable **only** through the N-merge, so retaining one while deleting the other would retain code
no input can reach — which is what this row exists to remove. The two cannot be taken separately in
either direction.

`Source: m2-cloudcost decision H, ratified 2026-08-01; slug convergence added from the t2
review's N1 (docs/reviews/m2-cloudcost-t2-review.md), 2026-08-02.`

---

### BL-070 — DONE 2026-08-10 (m5 t2) — the cross-provider deletions are **not taken**, by ruling

**m5-D2** (`cloudcost/m5-n1-compose.md` §Ratified decisions — *"the N>1 compose surface is
retained and bounded. It is a library-and-CLI capability the pipeline does not invoke, and it is
declared as such"*) disposes this row's deferred deletions **not taken**. The N-merge, the
`providers_without_prior_snapshot` caveat, all four cross-currency aggregation sites and the
multi-currency *"No combined total"* path all stay.

**The row's premise did not hold, and that is why.** This row called those paths **unreachable**;
m5 t1's **E1** established **three** routes that reach N>1 — the repeatable flags, `--input-dir`,
and the directory route — and that the route-bearing code is byte-unchanged since the commit
BL-131 read. So the paths are **reachable and uninvoked**, not dead: no orchestrator invocation
takes any of the three. Deleting reachable, advertised, tested code because nothing in one caller
happens to call it is the deletion m4 t5b withdrew and this ruling declines.

**Its four Done-when clauses, each disposed rather than left to be read against a ruling that
moved them:**

1. **The deletions** — **not taken**, per the above.
2. **The slug convergence** — already **DONE 2026-08-07 (m4 t5b)**, independently of this ruling
   and on C9's assignment. Unaffected.
3. **A test asserting the retained single-provider compose is unchanged** — **moot as written.**
   It existed to prove a deletion changed nothing; with no deletion there is nothing for it to
   bracket. The offline spine's 386 tests already constrain compose at N=1 and are unchanged by
   this ticket.
4. **The four m1 open items marked resolved-by-deletion** — **corrected in place, as this row's
   Done-when was once before at m4 t5b.** Nothing is deleted, so nothing is resolved by deletion,
   and the clause is unsatisfiable as written. Those items **stay open** in `cloudcost/milestone.md`
   §Open items with a determinate status they did not have before: the paths they name are
   reachable, uninvoked and now declared. **The one that changes character is the human-eyeball
   item** — *"Two of t4's rendered paths have never been looked at by a human"*, the new-provider
   caveat and the multi-currency *"No combined total"* rendering — which that section calls
   *"unreachable while DO is the only provider"*. Under this ruling they are **not** unreachable;
   they are uninvoked, and the eyeball is still owed by the first ticket that makes either
   reachable from the pipeline. §Open items is not in this ticket's `Touches` and is not edited
   here; the correction is recorded in this row, which owns the clause.

`Source: m5-D2, ratified 2026-08-10 at the m5 gate stop; applied at m5 t2, 2026-08-10. Route
count and byte-unchanged finding from m5 t1's E1 (cloudcost/docs/m5-t1-implementation-notes.md).`

---

### BL-073 — Surface a run's report artifact in Rig ("View report"), minimal (#TBD)
**Status:** DONE
**Size:** S · **Priority:** medium · **Section:** aetheris-agents (`rig/`)

**Rescoped 2026-08-03** from the m2-filed generic row ("deferred; the delivery-side decision is
the weight of the ticket") to an actionable minimal build. The original's open question — how does
Rig learn the path — is **answered below against a real run**, which is what makes it buildable.
Generic over any report-producing use case (docbuilder too), **not** cloudcost-specific: no
cloudcost strings in Rig.

**The gap.** The report is a self-contained HTML at
`output/{provider}/cloudcost_report_{period}.html`; Rig shows the run but not the report, so "test
from Rig" ends at the file system. Pairs with per-provider **solo runs** (decision H): one run,
one report, so the run→artifact relation is 1:1 with nothing to disambiguate.

**Decision 1 — discovery: SCRAPE. Verified against run `cloudcost-orch-aws-oFbapA`,** not
inferred — the path is present in the completed run's trajectory twice, so no harness change and
no new event type is needed:

| Where | Event | Content |
|---|---|---|
| step 4, seq 28 | `tool_result` | the render step's stdout JSON, `file` = `output/aws/cloudcost_report_2026-08.html` |
| step 5, seq 32 | `llm_responded` | the same path restated in the LLM's closing prose |

**Read the `tool_result`, never the `llm_responded`.** The orchestrator prompt forbids the LLM
editing a path, but a UI affordance must not depend on a model honouring an instruction when the
tool's own structured output is right there. Parse `payload.output` → `stdout` → `file`.

**Selecting WHICH `file` — do not key on the render step, and do not key on `.html`.** A pipeline
emits a file from most of its stages, so "the render step's tool_result" is exact for cloudcost and
wrong as a general rule. Measured on the two real pipelines:

| Run | file-emitting `tool_result`s | Final artifact |
|---|---|---|
| `cloudcost-orch-aws-oFbapA` | 4 (costs+inventory, orphans, report_data, report) | `…/cloudcost_report_2026-08.html` |
| `docbuilder-orch-iDGIIQ` | 1, carrying **4 paths** | `…offer_letter….docx` **and** `.pdf` |

So the discriminator is the **document extension set** (`.html`, `.pdf`, `.docx`, …) — never
`.html` alone, which would find *nothing* in the docbuilder run and leave the control permanently
absent on the case this row exists to prove generic. Take the **last** qualifying artifact across
tool_results (later steps are more final; the intermediates are all `.json`). Note docbuilder emits
several documents in one result — two formats of two documents — so "last wins" is not
self-evidently right there: either offer the qualifying set, or take the last and say so, but do
not silently pick one of four and label it "the report".

*Two more things this row would otherwise discover mid-ticket:*
- **The path is relative** (`output/aws/…`). Resolve it against the run's `sandbox_path`, which is
  already in `runs.config_json` (`/home/it/…/aetheris-agents/cloudcost` for the verified run).
  Both halves are already stored — that is what makes "no harness change" true rather than hopeful.
- **Guard on `overlay_base_dir`.** It is `nil` for cloudcost by requirement, so the file really is
  at that path. A use case running under an overlay would resolve the same relative path into the
  overlay instead — show no control rather than a broken link, which the done-when already demands.

The alternative — a run that *formally records* an artifact path — is cleaner and
cross-provider-stable but touches the harness/orchestrator and likely the event union (the
three-change rule + `drift_check`), so it is **deferred**. Settle that convention before provider
three *if* you want it recorded rather than scraped; for this row, scrape.

**Decision 2 — surface + security: open-external or sandboxed.** A "View report" control in the
run detail. The HTML is our template and `render_report` escapes provider-supplied strings
(`test_provider_supplied_strings_are_escaped_not_injected`), but it still embeds provider data — so
**never `innerHTML` it into Rig's React tree**. Open in the OS browser (Tauri shell), or a
sandboxed `<iframe>` with a restrictive CSP, or a separate webview window. Open-external is the
smallest honest version.

**Scope guard — discover + open, nothing more.** Explicitly OUT: inline render with section
navigation, orphan/optimization panels, live refresh. That is the rich version, a separate small
milestone, and it is the scope-creep magnet of this batch; do not let it grow this row.

**Do-not-generate.** `innerHTML` of use-case HTML into the app DOM; any cloudcost-specific path or
logic in Rig (derive from the trajectory, keep it generic); a new event type unless the
recorded-path option is deliberately chosen (it is not, for minimal); trusting the LLM's prose path
over the tool's JSON.

**Doc-sync DoD carried from the original row:** any new Tauri command or `RunSummary`/`RunDetail`
field lands with its `specs.md` §4/§5 entry in the same commit (check 9 `command_fields` guards §4
structs). Follow the runbook's "Adding a new module" pattern (`harness.rs` query + `types.ts` +
detail view, the BL-004/BL-029 precedent).

**Done when:** from a completed cloudcost run's detail, "View report" opens the produced HTML
(external or sandboxed); the same control works for a docbuilder run with no cloudcost-specific
code; a run that produced no artifact shows no control or a disabled one, never a broken link;
`tsc -b` + `bun run build` + `drift_check --strict` green.

`Source: m2-cloudcost §Referenced Rig ticket, ratified 2026-08-01 (decision H); rescoped from the
m2-filed generic row at the m2 Rig thread, 2026-08-03, with discovery verified against run
cloudcost-orch-aws-oFbapA.`

### BL-073 — DONE 2026-08-04

Landed `2bfa984` → `11e53ef`, merged `d4f44e4`. Discovery scrapes document-extension paths from
`tool_result` (four guarded hops: `output` → JSON → `stdout` → JSON → recursive value-scan);
resolution + **existence gate** are server-side, which subsumes the overlay case *and* drops
docbuilder's `rename_output` `original` paths (renamed away by the step that reported them —
value-scanning yields six candidates for a three-document run, the gate keeps three). Offer-the-set:
one artifact → button, N → list. 8 unit tests + a live arm, with an explicit anti-vacuity control.

**Reopened once (r2).** The first cut opened via the frontend shell plugin, whose `open` is
URL-scoped and rejects filesystem paths — so it could never have worked. Fixed by opening
server-side (`harness_open_artifact`), which re-vets the path against a freshly computed artifact
set before `open::that_detached`; the shell scope is untouched, since widening it would have let
the frontend open any local file and discarded the existence-gated invariant. **The residual
concealed the defect** — "the open is owed" read as an unverified step when the primitive behind
it was unusable; promoted as a review learning.

**Live acceptance:** cloudcost's HTML opens; `docbuilder-orch-wFwf_g` (3 artifacts) renders the
offer-the-set list. Doc-sync in the same commits: `specs.md` §4 carries both commands.

`Source: BL-073, closed 2026-08-04.`

---

### BL-074 — Seam sweep: enumerate every provider-vocabulary / provider-assumption seam in shared machinery (#TBD)
**Status:** DONE
**Size:** S–M · **Priority:** medium · **Section:** cloudcost (`cloudcost/scripts/`)

m1 closed calling `STOPPED_STATES` *"the one seam where a provider's own vocabulary reaches
shared machinery."* m2 t1 found it is at least **three**:

1. **`state`** — `detect_orphans.py:71` `STOPPED_STATES = {"off"}` (DO vocabulary). Known at
   m1, resolved at **t2 (a)**.
2. **`type`** — every rule keys on the inventory `type` field, but m1's §Normalized schemas
   never enumerated its *values*, so DO's `droplet` / `reserved_ip` were provider vocabulary
   inside shared machinery. Surfaced at **t1**, resolved at **t2 (a′)**.
3. **The flat-billed-regardless-of-state cost assumption** — `rule_stopped_droplet_with_attached_storage`
   takes its saving from the instance's own `monthly_cost_estimate` (`detect_orphans.py:243`
   states the m1 forward: *"saving estimate is the instance's own monthly_cost_estimate;
   attached storage is named but not summed (m1)"*). True for DO, which bills a droplet on or
   off; false for AWS, which bills no compute for a stopped instance. Adapter half resolved at
   **t1** (a stopped instance reports `monthly_cost_estimate: 0.0`, keeping the provider's cost
   model in its adapter per D5); saving half at **t2 (c)**.

**Why a row rather than three fixes.** All three are being fixed. What is not fixed is the
thing that produced them: the "one seam" claim came from **observation, not enumeration** —
exactly the **Adjacent-case** rule (*"enumerate every site of that exact class before filing or
fixing the first one"*). Fixing the three found by accident leaves the same blind spot for the
fourth. So this ticket is the enumeration itself.

**Scope.** Sweep `detect_orphans.py`, `_normalized.py`, `compose_report_data.py` and
`render_report.py` for *any other* value, threshold, spelling or billing assumption a provider
could legitimately differ on, and decide for each whether it is schema-level (enumerate it in
§Normalized schemas) or adapter-owned (push it into the adapter). Named next candidates:

- the rule-catalog **age thresholds** (`UNATTACHED_VOLUME_MIN_AGE_DAYS`,
  `STOPPED_DROPLET_MIN_AGE_DAYS`, `DEFAULT_SNAPSHOT_AGE_DAYS`) — a provider whose billing
  granularity differs may want different ones, and today they are global constants;
- the **`keep=true` tag spelling** (`KEEP_TAG`) — DO tags are flat strings, AWS tags are
  key/value pairs flattened to `k=v` by the adapter, so the spelling is already an adapter
  convention masquerading as a shared constant;
- `EPHEMERAL_NAME_PATTERN`, and `TAGGED_ACCOUNT_COVERAGE_THRESHOLD`.

Also **correct m1's "the one seam" text where it appears** (`cloudcost/milestone.md` §Open
items) so the next reader does not re-derive the wrong count.

**Done when:** every provider-differing value in shared machinery is enumerated with a
schema-level-or-adapter-owned ruling; the ones ruled schema-level are in
`[amended 2026-08-07]` **§Contracts** ~~§Normalized schemas~~;
m1's "one seam" text is corrected; the sweep's *method* (how completeness was established) is
recorded, so this is an enumeration and not another observation;
`[added 2026-08-07]` **and the rows the rulings created are filed** — see the second amendment
note below.

**Done-when clause 2 amended 2026-08-06/07 (m4 t4b, reviewer's ruling), before the row was
assessed against it** — the same move t2 made on BL-069, and for the same reason: a row assessed
against a clause the work has already superseded is assessed against nothing.

*What changed.* The schema-level rulings live in **`cloudcost/milestone.md` §Contracts (C1–C15)**,
a new sibling section immediately after §Normalized schemas, not inside it. As written the clause
was **unsatisfiable**, so the row could not have closed cleanly against it.

*Why.* The two sections make different kinds of statement. **§Normalized schemas states shapes**;
**§Contracts states value semantics and adapter obligations.** Interleaving 48 of the second into
the first would make the shapes harder to read for every future reader — an argument that holds
regardless of anything else.

Secondarily, and stated as a floor with its method named: **at least 12 citations across 9 files**
call §Normalized schemas *frozen*, by a search of both repos for the literal word `frozen` within 40
characters of the section name. `cloudcost/m2-milestone.md` (×3), `cloudcost/m3-milestone.md`,
`cloudcost/runbook.md`, `cloudcost/docs/t1-implementation-notes.md` (×2),
`cloudcost/docs/t3-implementation-notes.md`, `cloudcost/docs/m3-linode-scout.md`,
`docs/reviews/m2-cloudcost-closeout.md` and two handoffs. So rewriting the section would have
falsified a standing claim in nine other documents in the same commit, and `cloudcost/runbook.md` —
live operational guidance — is the one that would have cost most.

*Two things about that figure, both corrected at t4b r2.* The search returns **13**, not 12: the
thirteenth is **this paragraph**, which the search matches because it contains the claim. Counting
the assertion as evidence for itself is the error, and it is excluded here explicitly rather than
silently. (It is **not** a harness hit — the search spans both repos and every genuine citation is
agents-side, so *"in this repo"* was doing no work and has been dropped.) And the figure is a
**floor**, not a census: the pattern requires the literal word *frozen*, so a document that says the
section is fixed as of m1 and must not be edited, without using that word, is invisible to it. The
argument needs a floor and never needed a count.

**Done-when clause 5 added 2026-08-07 (m4 t4b r2, reviewer's ruling — branch (a)).** t4b assessed
all four original clauses **satisfied** and still did not close this row. That reason lived only in
the ticket's packet and in `cloudcost/m4-consolidation.md`, so a reader of *this file* saw a row
whose stated Done-when was fully met, no DONE section, and no explanation in the row — the shape a
done-check exists to prevent, arriving from the other side.

*Why (a) rather than a hold note.* The assessment was **already applying a fifth clause**; it was
simply unwritten. An unwritten clause is worse than an amended one, because it cannot be reviewed
and it cannot be checked at the close. Writing it makes the row **honestly unmet** rather than
mysteriously open.

*What the fifth clause requires.* The rulings produced eleven items that stay broken whichever arm
they land in — a scoring modifier that has never fired, a billing case neither stopped rule covers,
a validation the sprint's own gate presumes absent — plus three exclusions to be recorded with their
reasons. **m4 t4c files them; this row closes there.** A Done-when satisfied by documents whose
consequences have nowhere to live is the complete-but-unmarked shape BL-102 exists for.

**§7 promotion candidate at m2 close** — Adjacent-case / enumerate-the-class, in its
"a uniqueness claim produced by observation" form.

**Coupling added 2026-08-06 (m4 t2): the sprint case is now a consumer of the vocabulary
surface this row sweeps.** The cloudcost sprint case's rule-legibility assertion imports
`CANONICAL_TYPES` from `cloudcost/scripts/_normalized.py` — deliberately, so the vocabulary is
never restated in shell. If this sweep relocates or renames it, `../aetheris/scripts/sprint.sh`
breaks, and it breaks *loudly* (the probe fails and the arm reads `[FAIL]`), which is the intended
posture. Two observations for the sweep, both found while wiring it:

- **`CANONICAL_TYPES` has no public accessor.** Adapters import the seven `TYPE_*` constants
  individually and never the set; nothing outside tests referenced the set before t2. If the sweep
  wants a stable surface, this is the moment to decide whether one exists.
- **`usable_resources()` checks that `type` is *present*, never that it is *canonical*.** An
  out-of-vocabulary `type` passes through as usable and simply matches no rule — silently. That
  gap is precisely why the sprint assertion had to check membership itself, and it is a candidate
  for this sweep's ruling: schema-level validation in `_normalized`, or left to the callers.

**DONE 2026-08-07 (m4 t4a / t4b / t4c).** All five Done-when clauses satisfied; assessed per
clause below.

| # | Clause | Satisfied by |
|---|---|---|
| 1 | *every provider-differing value … enumerated with a schema-level-or-adapter-owned ruling* | `cloudcost/docs/m4-t4a-implementation-notes.md` — **54 items** from a structural AST extraction over **518 nodes**, with a recorded completeness argument. Ruled at t4b: **48 schema-level, 4 adapter-owned, 2 neither**. **Qualification, stated not glossed**: the clause offers two arms and **two items fit neither** (D5, operator configuration; R4, an environment dependency), recorded with their reason under C15 rather than forced. |
| 2 | *the ones ruled schema-level are in §Contracts* `[amended]` | `cloudcost/milestone.md` **§Contracts (C1–C15)**. Every one of the 54 is cited by item id in **exactly one** contract — an exact bijection, derived not asserted. Clause amended 2026-08-07 before assessment (note above). |
| 3 | *m1's "one seam" text is corrected* | `cloudcost/milestone.md` §Open items, corrected in place. m2 had corrected *"the one seam"* → *"at least three"*; **that was itself an observation**, produced by the failure mode the sentence describes. The entry now states the censused count, asserts **no seam count** (t4a establishes a censused count, not a seam count), and carries its correction history by strikethrough. |
| 4 | *the sweep's method is recorded, so this is an enumeration and not another observation* | `cloudcost/docs/m4-t4a-implementation-notes.md` §2 — the extraction inlined verbatim and re-runnable, per-class node counts a reader can diff, the classification criterion, the exclusion record with reasons, and §2.7 *"what would not have counted"*, which names *"I searched for the known candidates and found them"* as the failure mode. §2.6 bounds the claim: an AST-class census is complete **relative to its class list**, and the method cannot answer from inside itself whether a further population remains. |
| 5 | *and the rows the rulings created are filed* `[added]` | **17 rows: BL-114–BL-130.** Ten defect rows (X4, F2, F3, N8, X5, P8, D16, P2, P11, D12) and seven contract-consequence rows (N3, D20, N5, N7, D6, P6, P7). Three exclusions confirmed already recorded in §Contracts with their reasons and deliberately not filed — D15 (C7), D17 (C3), P4 (C10). One candidate row **not** filed: D5's precondition was run at t4c and failed, and the residual is a note under C15. |

**What this row established, beyond its own fix.** m1 called `STOPPED_STATES` *"the one seam"*; m2
found three; the census found **54**, of which the seven candidates BL-074 and its later couplings
named account for eight items. **The substantive finding is that this was never a handful of seams
to close but a large, mostly undocumented contract** — which is why the deliverable was a contract
section rather than a migration, and why 48 of 54 ruled schema-level: these four scripts *are* the
shared machinery, so almost nothing in them should move to an adapter.

**The §7 promotion candidate this row carried** — *Adjacent-case / enumerate-the-class, in its "a
uniqueness claim produced by observation" form* — is now evidenced three times over in one lineage:
*"the one seam"*, then *"at least three"*, then a t4b correction that asserted a seam predicate over
all 54 which the census denies. Each was a count replaced without re-checking the claim it hung on.
Carried to the m4 close.

`Source: m4 t4a (census, agents 904a568), m4 t4b (§Contracts, agents 611feba), m4 t4c (rows,
this commit). Closed 2026-08-07.`

`Source: m2-cloudcost t1 review r0/r1 (docs/reviews/m2-cloudcost-t1-review.md), ratified
2026-08-01. Line citations verified at aetheris-agents 3bc970b. Coupling appended m4 t2,
2026-08-06.`

---

### BL-077 — `sprint.sh` assertion failures do not affect the sprint's exit code (#TBD)
**Status:** DONE
**Size:** S–M · **Priority:** medium · **Section:** harness (`../aetheris/scripts/sprint.sh`)

Filed 2026-08-02 from the m2-cloudcost **t3** review (claude-ui N1). Pre-existing and
**sprint-wide** — all 31 cases, not t3's to fix, which is why it is a row rather than a patch.

**The gap.** `fail()` is a printer:

```bash
fail()    { echo -e "\033[0;31m[FAIL]\033[0m  $*"; }
```
(`sprint.sh:37`, verbatim.)

It sets no exit status and no failure flag, and `run_agent`/`run_orb` wrap their invocation in
an `if` so a non-zero child exit is swallowed too. Only the explicit `exit 1` preflights
(missing tool, missing credential) can make the script exit non-zero. So a sprint whose
**assertions** all fail still exits **0**.

Observed concretely at t3: both cloudcost legs printed
`[FAIL] orphan candidates: 0 …` and the sprint exited 0 either way. The red was real and
correctly reported — but nothing downstream of `$?` could have known.

**Why it matters.** It makes the sprint's exit code a check that passes identically whether or
not the thing under test worked — the **Silent-wrong-answer** shape, one level up, in the
apparatus rather than in a script. Any CI job, cron wrapper, or `&&` chain keying on `$?` reads
a fully-red sprint as success. The gate rule (*every existing gate runs at ticket boundaries; a
red gate gets a tracked ticket the day it's found*) leans on someone **reading** the output,
which holds for a human at a terminal and fails for anything automated.

**Not a trivial flip.** Making `fail` set a flag turns every currently-tolerated red into a
sprint failure at once — including tracked known-reds like **BL-069**, which are *supposed* to
stay visible without blocking. So the row has a design question, not just an edit:

- a `FAILURES=$((FAILURES+1))` counter plus a final `exit $(( FAILURES > 0 ))`, and
- a companion `expected_fail()` (or a `KNOWN_RED` allowlist keyed by ticket ref) so a tracked
  carry prints its `[FAIL]` line and its ticket without flipping the exit code.

Without the second half this fix cannot land while BL-069 is armed.

**Done when:** the sprint exits non-zero when an untracked assertion fails, tracked known-reds
are declared with their ticket ref and do not flip the exit, the summary block prints the
pass/fail tally (it is static text today), and the change is mutation-checked — deliberately
break one assertion in one case, confirm a non-zero exit; restore, confirm zero. Audit all 31
cases for reds that would newly become blocking before flipping the default.

> **`[corrected 2026-08-09 (hc-d, G5). The population is 29, not 31 — derived, not inherited.]`**
> One pattern, stated: `^if \[\[ "\$TARGET" ==`, the line that opens a case block.
> **30 blocks, 29 distinct case names** (`uc4` opens twice, at `:202` and `:303`); `all` is the
> selector, not a case. Both non-case-head `$TARGET` lines are accounted for rather than dropped —
> `:192` is the credential preflight's `!=` guard and `:1467` is an inner exit inside the
> `playground_api` case. The independent population agrees: `$TARGET ==` takes 30 distinct values,
> one of which is `all`.
>
> **Identical at `fa158a4`, the commit this row cites, and at `1b09b23`** — so the row was wrong
> when filed, not overtaken. **Whether 31 has a provenance is NOT established and is therefore not
> offered:** `grep -c 'section "'` returns exactly 31 at both commits (29 indented + 2 unindented),
> which makes it the only quantity in the file equal to 31 and a live candidate — but a plausible
> explanation for a wrong number is not a truth-maker, and nothing in either repo settles what the
> row's author counted.
>
> The audit clause is answered by **R7's fail-safe posture** rather than by sweeping 29 cases: no
> arm becomes blocking without individual verification, so nothing newly blocks by default and the
> undeclared count is printed on every run.

**Status:** Done 2026-08-09 — hc-d. `fail()` now counts; `blocking_fail`/`blocking_ok` are the
per-arm promotion; `expected_fail <BL-row>` is the tracked carry and rejects an entry naming no
row; `known_red_healed` makes a healed entry a failure. The summary prints all four counters
including zeros, and the script exits 1 iff a blocking failure occurred. **Mutation-checked both
ways on a real red**, not a simulated one: a phantom event type added to `docs/rig/specs.md` §6
made the promoted `drift_check` arm fail — `sprint.sh drift_check` exited **1**; restored, it
exited **0**. R17's arms (b) and (c) were constructed and observed. **One arm promoted** — the
`drift_check` case, the only one individually verifiable here without credentials or network;
every other arm stays undeclared by design, which is R7, not an omission.

`Source: m2-cloudcost t3 review, claude-ui N1, 2026-08-02 (aetheris fa158a4; observed on both
cloudcost legs). Reported by claude-code in the t3 packet before the review raised it.`

---

### BL-060 — `mix hex.audit` is red: bandit 1.11.1 carries EEF-CVE-2026-65623 (#TBD)
**Status:** DONE
**Size:** S · **Priority:** medium · **Section:** harness (`../aetheris/mix.exs`, `mix.lock`)

Found 2026-07-26 by BL-039's ticket-boundary gate run — off-territory, exactly the way
the gate rule intends. Filed the day it was found, not carried.

```
bandit 1.11.1 - EEF-CVE-2026-65623 (HIGH)
  aka: CVE-2026-65623, GHSA-vg8x-66vg-5pxh
  Quadratic CPU blow-up reassembling fragmented WebSocket messages in Bandit
  https://osv.dev/vulnerability/EEF-CVE-2026-65623
```

**Upstream-triggered, not commit-triggered** — the advisory was published under a lock
file nobody touched, which is the case `CLAUDE.md`'s `hex.audit` section names as the
gate working rather than failing. BL-020 cleared all 15 advisories on 2026-07-17 with no
residuals, so this is a fresh one, not a regression.

`mix.exs` requires `{:bandit, "~> 1.0"}` and the lock pins **1.11.1**; hex advertises
`Config: {:bandit, "~> 1.12"}` with 1.12.3 released 2026-07-25. So a patched line exists
and the constraint already admits it — this looks like a lock bump plus a `mix.exs`
floor, not a migration. **Confirm the advisory is actually fixed in the 1.12 line before
bumping** (this row read the version list, not the changelog) and check the
`thousand_island`/`websock`/`plug` co-resolution.

Reachability is worth a sentence in the fix, not a reason to defer: bandit backs the
playground API, which is **disabled by default** and started on demand
(`api/server.ex`), and the WebSocket path is not something the harness exposes today.
That bounds the exposure; it does not clear the advisory, and `hex.audit` has no
suppression mechanism.

Until it lands, the gate runs **expected-red, named with this row's ref** per the
tracked-carry clause — named in packets, not re-triaged.

**Done when:** `mix hex.audit` is clean, or the residual advisory has a recorded
rationale here and the gate's expected-red state is stated with this ref.

**Status:** Done 2026-07-30 — commit `892b0f7`, the same bump that closes **BL-066**, which
filed this identical advisory a day later (2026-07-27, off m1-cloudcost t1's gate run) without
noticing this row. BL-060 is the original; keep the fix detail on BL-066's row.

Both of this row's pre-conditions were checked rather than assumed: the advisory **is** fixed in
the 1.12 line — `mix hex.audit` is clean at the resolved **bandit 1.12.4** — and the
co-resolution moved `thousand_island` 1.4.3 → 1.5.0 and `plug_crypto` 2.1.1 → 2.2.0, leaving
`websock`/`plug`/`hpax` where they were. The reachability sentence this row asked for: the
playground API stays disabled by default and on-demand, and `grep` over `lib/` finds one Bandit
call site and no `WebSock` usage, so the fragmented-frame path was never exposed.

**The gate is green as of this commit** — the expected-red carry above no longer applies, and
any packet naming `hex.audit` red against BL-060 or BL-066 is out of date.

---

### BL-083 — Run list: classify the four unclassified use cases; provider in the cloudcost label (#TBD)
**Status:** DONE
**Size:** S · **Priority:** medium · **Section:** aetheris-agents (`rig/`, `cloudcost/agents/`)

Filed 2026-08-03. **Scoped wider than the cloudcost symptom that surfaced it** — the open question
("why does payslip group but cloudcost not?") resolved on first read, and the answer showed the
class.

**Mechanism.** `RunList.tsx:133` `classifyRun(run.label)` matches the **label**, not the run_id,
against the hardcoded `USE_CASE_PREFIXES` list (`:118`). There is no `cloudcost` entry, so it falls
through to `Unclassified` (`:138`). Nothing about run_id prefixes is involved.

**The class, counted from the live store (`mix aetheris list --limit 200`), not inferred:**

| Label | Runs | Today |
|---|---|---|
| `Docbuilder Orchestrator` / `Context Builder` / `Context Orchestrator` | **54** | Unclassified |
| `Cloudcost Orchestrator` | 9 | Unclassified |
| `Capability Matrix -- Provenance` (legacy label; `cap-matrix:` siblings match) | 5 | Unclassified |
| `cap-matrix: *`, `Payslip *`, `Email *` | 49 | correct |

So cloudcost is **not** the main occupant of Unclassified — docbuilder is, by 6×. Fixing only
cloudcost leaves 59 runs misfiled and the next reader re-derives all of this. Also **two dead
entries**: `api-tenant` and `api-gateway` match nothing, because the api agents are labelled
`at1cmd` / `at1qry` / `cot1` / `cot1_stub`; and `eduloka` has an orchestrator but no prefix.

**Scope.** Add `cloudcost`, `docbuilder`, `eduloka`; fix or drop the two dead api entries (decide
against the real labels, not against the use-case directory names); handle the legacy
`Capability Matrix -- Provenance` label. Separately, `cloudcost_orchestrator.exs` sets a
provider-distinct `label` — `Cloudcost · AWS` / `Cloudcost · DigitalOcean`. Note the two halves
compose: `classifyRun` lowercases and does `startsWith`, so `"cloudcost · aws"` still matches a
`cloudcost` prefix — changing the label cannot break the grouping, but only in that direction.

**Done when:** no use case with a live orchestrator lands in Unclassified; the cloudcost rows name
their provider without the search filter; every remaining `USE_CASE_PREFIXES` entry matches at
least one real label (a prefix matching nothing is the dead-entry defect, re-armed).

### BL-083 — DONE 2026-08-04

Landed as a **label patch, not run_id re-keying** — reversing handoff §Corrections 3, which had
recorded the opposite as answered. The run_ids it rests on were verified at HEAD and the api ones
break it: `uc-api-t2-AeGOtw-at1cmd` / `uc-api-t2-tuquiQ-cot1`, where the first segment is `uc` (not
the use case, and zero run_ids start with `api`), the tenant/gateway discriminator is a **suffix**,
and the shared prefix embeds a milestone number that `t3` would invalidate. Full adjudication in
`docs/rig/milestones/bl-083-run-classifier-implementation-notes.md`.

Three of the row's own claims did not survive re-derivation and are corrected there: the docbuilder
"bare `Context Builder`" variants **do not exist** (all three labels start with `Docbuilder`, so one
prefix covers all 57); the legacy capability-matrix label has **14** runs, not 5, plus a missed
`Capability matrix generator`; and **eduloka has never produced a run** — it is covered because a
real agent *declares* the label, which is why "real label" was defined as declared ∪ observed.

**Result over 957 runs — Unclassified 693 → 565, 128 rescued:**
API/Gateway 0→15, API/Tenant 0→29, Cloudcost 0→12, Docbuilder 0→57, Capability Matrix 85→100;
Drive/Email/Payslip/Provenance unchanged.

`cloudcost_orchestrator.exs` now emits `Cloudcost · AWS` / `Cloudcost · DigitalOcean`, which still
groups as Cloudcost (`startsWith` on the lowercased label).

**Standing guard added** — `scripts/check_run_classifier.py` + `tests/test_run_classifier.py`
(15 tests, hermetic). It parses `USE_CASE_PREFIXES` out of `RunList.tsx` rather than duplicating it,
and fails on either rot direction: a prefix matching no known label, or a declared agent label
falling through. Mutation-checked both ways.

**Residual, conceded:** label-keying is safe for suffix appends (proven by the `· AWS` change) but
a change to a label's *leading* word unfiles its runs. That is what the guard watches.

**Not verified visually:** the run list renders via Tauri `invoke`, so grouping was confirmed by
computation over the same store, not by looking at Rig. The group headings are the one thing that
does not cover.

`Source: m2-cloudcost close-out, 2026-08-03; closed 2026-08-04.`

### BL-090 — capability-matrix stale: cloudcost omits detect_optimization_signals (#TBD)
**Status:** DONE
**Size:** XS · **Priority:** low · **Section:** aetheris-agents (`docs/`, matrix generator)

Filed 2026-08-03 by BL-084. `docs/capability-matrix.md` §Cloudcost lists six scripts and its summary
reads `| cloudcost | 1 | 6 |`, but seven `.py` are on disk — `detect_optimization_signals.py` is
absent. Cross-checked against BL-084's serde script counts: every other use case's matrix count
matches disk (drive/payslip differ from their manifests only by import-only/undeclared scripts, as
expected); cloudcost is uniquely short, i.e. the script was added after the last matrix regen.

The matrix is GENERATED — fix by re-running the capability_matrix sprint case, not by hand-editing.
One reconciliation at regen: the generator will source detect_optimization_signals' cell from its
docstring, which differs from BL-084's code-derived manifest description (written from the signal
constants, deliberately more precise than the docstring). Either improve the script docstring to
match, or accept the manifest wording as canonical and let the cells differ. "descriptions match
capability-matrix.md" is not re-opened by this — BL-084 satisfied it 5-of-6 with the 6th documented.

**Second staleness in the same section, added 2026-08-04 by BL-083.** `docs/capability-matrix.md`
§Cloudcost still shows the agent Label as `Cloudcost Orchestrator`; BL-083 changed it to
`Cloudcost · #{provider_name}`, so the live values are `Cloudcost · AWS` / `Cloudcost ·
DigitalOcean`. Filed rather than hand-fixed for the reason this row already gives — the matrix is
generated — and noted here so the regen reconciles both cells in one pass instead of discovering
the second one afterwards.

`Source: BL-084, 2026-08-03; label drift appended by BL-083, 2026-08-04.`

### BL-090 — DONE 2026-08-05

Regenerated in `4d98ec2` (m3-cloudcost t3), merged `8dca843`. **Both** stale cells this row
accumulated reconcile in the one pass it asked for:

| cell | before | after | filed by |
|---|---|---|---|
| Agent Label | `Cloudcost Orchestrator` | `Cloudcost · {provider}` | BL-083, 2026-08-04 |
| Scripts | 6 listed, `detect_optimization_signals.py` absent | 8 listed | BL-084, 2026-08-03 |

Summary row `| cloudcost | 1 | 6 |` → `| 1 | 8 |`; totals `27 | 82` → `27 | 84`.

**Eight, not the seven §t3 predicted.** The "seven" figure is the scout's §A9 count, written
against `dc8c077` — six on the matrix plus `detect_optimization_signals.py` — and it predates
t1 adding `fetch_linode.py`. So the doc was the stale side of its own staleness ticket: t3
reported the count the regen produced and flagged the prediction rather than reconciling
down to it (`m3-milestone.md` rev 7 corrected §t3). This is the m3 learning about documents
that quote repo state, fired on the row whose subject *is* a document quoting repo state.

Regenerated by the §A9 ritual — the cloudcost section agent alone
(`cap-matrix-cloudcost-BEWzHw`), then `assemble_matrix.py` over all nine sections. Never a
full nine-agent regen (BL-068: `docs/.sections/` is gitignored, so a full re-run destroys the
eight sections it does not regenerate), never a hand-edit — the artifact is generated, which
is the reason this row exists rather than a one-line fix. The regen also rewrote the six
carried script descriptions from current docstrings; that is regen output, not a curation.

`Source: BL-084 (filed 2026-08-03), label drift appended by BL-083 (2026-08-04), closed by
m3-cloudcost t3 done-when 5, 2026-08-05.`

### BL-092 — tools.rs manifest-deserialization test coverage (#TBD)
**Status:** DONE
**Size:** S · **Priority:** low · **Section:** aetheris-agents (`rig/`)

Filed 2026-08-03 by BL-084. `tools.rs` has zero `#[cfg(test)]`. BL-084 proved cloudcost/tools.json
deserializes into `ToolsManifest` via a temporary test module, then discarded it (tools.rs is
byte-identical to HEAD). Make it permanent: a `#[cfg(test)]` module round-tripping every committed
manifest into `ToolsManifest` and asserting Ok plus the env_deps dedup walk. This is the only
standing offline guard against the pytest suite's transcription gap — a manifest that passes pytest
but fails serde is dropped to None with every script going amber and nothing saying why. Seed is in
`cloudcost/docs/bl-084-implementation-notes.md` §"What is proven offline."

`Source: BL-084, 2026-08-03.`

### BL-092 — DONE 2026-08-05

Landed `f28b817` (m3-cloudcost t2), merged `f552094`. A `#[cfg(test)] mod tests` at the end of
`rig/src-tauri/src/commands/tools.rs` — 157 insertions, 0 deletions, one hunk; the file is
byte-identical outside `cfg(test)`.

**Coverage is by walk, not by list.** `committed_manifests()` reads the agents root and takes
every `<use_case>/tools.json`, mirroring `tools_list_inventory`'s own exclusions, so a manifest
added later is guarded without editing the test. Four tests over that set:

- `every_committed_manifest_round_trips_into_tools_manifest` — the property the row exists for.
  `tools_list_inventory` does `serde_json::from_str(&raw).ok()`, so a schema violation is not an
  error but a `None`: the use case silently falls back to all-undeclared, every script amber and
  nothing saying why. Also re-serializes and re-parses, catching a field that deserializes only
  because serde defaulted it away.
- `a_manifest_missing_an_env_dep_field_is_rejected` — **the negative control.** Without it the
  round-trip has only ever been seen passing, so it is not yet a check. Drops `"masked"` from
  cloudcost's first `EnvDep` (a bool, so removal is a schema violation rather than a coercion),
  asserts the mutation applied, and asserts the mutant fails to deserialize.
- `discovery_finds_every_committed_manifest` — anti-vacuity for all of the above: a walk that
  silently returned nothing would pass a round-trip over zero manifests. Asserts the *set*
  (`api, cloudcost, drive, eduloka, email, payslip`), not a count, so adding a use case fails
  where the expectation lives instead of silently widening coverage.
- `env_deps_dedup_walk_keeps_the_first_occurrence_only` — the first-occurrence-wins dedup,
  anchored on `CLOUDCOST_AWS_ACCESS_KEY_ID`, which genuinely repeats across `fetch_aws` and
  `detect_optimization_signals`; the anchor's repetition is itself asserted, so the dedup is
  doing work rather than passing over an already-unique list. Also asserts
  `CLOUDCOST_LINODE_TOKEN` is masked in the Rig config surface.

This is the standing offline guard `tests/test_tools_manifests.py` structurally cannot be: the
pytest suite transcribes these structs, only this test runs serde. Seed was
`cloudcost/docs/bl-084-implementation-notes.md` §"What is proven offline", as the row directed.

`Source: BL-084 (filed 2026-08-03), closed by m3-cloudcost t2 done-when 5, 2026-08-05.`

### BL-095 — plan-card renders secret config values in clear (#TBD)
**Status:** DONE
**Size:** S · **Priority:** medium · **Section:** aetheris-agents (`rig/`)

Filed 2026-08-04 by BL-085. `StepCard` builds `` `${k}: ${configValues[k]}` `` for every
`STEP_CONFIG_HINTS` key that is set and renders the result as visible text
(`rig/src/components/modules/orchestrator/OrchestratorView.tsx:83-86`, rendered `:105-111`;
`configValues` is the persisted agent config, `:130`). The `payslip/agents/payslip_pipeline.exs`
hint list includes `SMTP_PASSWORD` and `GOOGLE_SERVICE_ACCOUNT` (`:20-30`), so an approved payslip
plan card displays those secrets in clear today.

Fix by consulting the same `masked` flag the config tab already uses (`AgentConfigTab.tsx:41-61`),
or by showing set/unset status only — the `ToolDetail.tsx:83-101` "Required config" dots are the
existing pattern for exactly this and render no values.

Found while adjudicating BL-085's STEP_CONFIG_HINTS question; it is the reason no cloudcost entry
was added there (a cloudcost entry would have printed `CLOUDCOST_AWS_SECRET_ACCESS_KEY` and
`CLOUDCOST_DO_TOKEN` in clear). Pre-existing — BL-085 surfaced it, payslip owns the live exposure.

`Source: BL-085, 2026-08-04.`

### BL-095 — DONE 2026-08-04

Landed `63ea4b5`, merged `5fe1903`. **Deny by default, not mask-if-flagged**: `StepCard` renders a
hint value only on an explicit `masked === false`, so masked keys, the two hint keys carrying no
metadata at all (`DOCBUILDER_CONTEXT_FILE`, `DOCBUILDER_REQUEST`), and any future undeclared key
show `set` rather than their value.

**Enumeration falsified both candidate rules.** Of the 15 hint keys exactly one is `masked: true`
(`SMTP_PASSWORD`) — and `GOOGLE_SERVICE_ACCOUNT`, the other key this row names as leaked, was
explicitly `masked: false`. Mask-if-flagged would have left it in clear; so would a
"show if `masked === false`" rule. Resolved by fixing the metadata rather than special-casing the
rule: it is now `masked: true`, being a credential-*file* locator. A plan-card-only secrecy list
was rejected — duplicated secrecy metadata is a drift class this repo already pays for.

11 of 15 keys still render their values, so `PAYSLIP_MONTH: 2026-04` survives as plan-review
signal. Predicate proven against the real `AGENT_CONFIG_DEFS` with **two** anti-vacuity arms,
because the obvious cheat is hiding everything. Live: the card reads `set` for both secrets and
Settings dots the service-account path.

`Source: BL-085 (filed), closed 2026-08-04.`

### BL-096 — `fetch_aws.py` exceeds the 60 s `run_command` default on every AWS run (#TBD)
**Status:** DONE
**Size:** XS · **Priority:** medium · **Section:** aetheris-agents (`cloudcost/`)

Filed 2026-08-04 by BL-085, found while diagnosing a Rig-launched run reported as "timed out".
`cloudcost/agents/cloudcost_orchestrator.exs` mentions `timeout` **nowhere**, so STEP 1's
`run_command` uses the exec server's 60 000 ms default
(`../aetheris/native/aetheris_exec_server/src/main.rs:472`, documented `:127`).
`fetch_aws.py` takes **63–67 s** against the real bill, so the first call always times out.

**Chronic, not a regression — 5 of 5 AWS runs in the DB:**

| run | fetch_aws calls | timeouts | tool durations (ms) |
|---|---|---|---|
| `cloudcost-orch-aws--ez4vQ` (Rig, 2026-08-04) | 2 | 1 | 60000, 66991, 49, 47, 134 |
| `cloudcost-orch-aws-oFbapA` (m2 milestone run, `m2-milestone.md:4`) | 2 | 1 | 60000, 66136, 43, 42, 129 |
| `cloudcost-orch-aws-SdBOkw` | 2 | 1 | 60000, 66454, 44, 42, 172 |
| `cloudcost-orch-aws-XWjM8A` | 2 | 1 | 60000, 63818, 42, 45, 121 |
| `cloudcost-orch-aws-cwB8KA` | 2 | 1 | 60000, 63352, 38, 45, 119 |

Every run recovers: the LLM retries the identical command with `timeout_ms: 300000` and succeeds.
That recovery is why this went unnoticed through all of m2 — including the milestone's own cited
evidence run.

**This is a determinism-contract item, not a cosmetic one.** The contract's §1 opens *"The harness
is deterministic; the model is not"* (`../aetheris/docs/aetheris/determinism-contract.md:31`,
manifest-tracked as `aetheris--determinism-contract.md`). Whether a four-stage deterministic
pipeline **completes** is a harness-side property, and today it is not one: STEP 1 always fails, and
the run only finishes because the model elects to retry with a larger `timeout_ms`. Nothing
instructs that retry — not the agent file, not the exec server, not the tool description. It has
held 5/5, but only under `claude-haiku-4-5-20251001`; a model swap, a temperature change, or a
differently-worded plan converts a working pipeline into a failed run with no code change anywhere.
The LLM is on the success path for a question it should never have been asked.

It also inverts *scripts do, agents decide* in its purest form: the run duration of `fetch_aws.py`
is a fixed, measurable property of the script, rediscovered by an LLM at runtime, once per run,
forever. And it burns a guaranteed-wasted 60 s — ~45 % of a 2 m 18 s run — to rediscover it.

**Fix — instruct the timeout so the model is off the success path.** Declare an explicit
`timeout_ms` on the `fetch_aws` step in `cloudcost/agents/cloudcost_orchestrator.exs`
(300 000 matches what the model already converges on), or raise the exec-server default for that
call. Either way completion becomes deterministic and the retry stops being a lucky behaviour. The
other three stages run in 38–172 ms and need nothing. Check whether the DO path carries the same
latent gap at a different threshold — `fetch_do.py` currently completes inside the default, so the
gap there is unproven, not absent (**Absent is unknown, not zero**).

**Done when:** an AWS run shows one `fetch_aws` `tool_called` and zero timeouts in its trajectory;
the timeout value is declared in the agent file rather than chosen at runtime; and the
determinism-contract cross-reference is recorded when the fix lands.

### BL-096 — DONE 2026-08-04

Fixed in `32933d8`: `fetch_timeout_ms = 300_000` declared on STEP 1 of
`cloudcost/agents/cloudcost_orchestrator.exs`. Exec-server default untouched.

Live acceptance — run `cloudcost-orch-aws-3KU2NQ`, status `done`, report produced:

| check | before (`--ez4vQ`) | after (`3KU2NQ`) |
|---|---|---|
| `fetch_aws` `tool_called` | 2 | **1** |
| timeout events | 1 | **0** |
| `timeout_ms` on the **first** call | absent (defaulted to 60 000) | **300000** |
| tool durations (ms) | 60000, 66991, 49, 47, 134 | **63882, 45, 47, 115** |
| wall clock | 2 m 18 s | **1 m 18 s** |

The first call now carries the declared value and completes in 63.9 s — inside the measured
63–67 s band, and no longer a retry. The third row is the load-bearing one: without it a run that
merely finished fast would read as a passing fix.

Non-leak re-checked under the settled BL-085 criterion: all 20 stored agent-config values with
length ≥ 8 grepped against this run's trajectory and `config_json` — zero secret hits.
The only value matches are non-secrets (`AETHERIS_MODEL`, `AETHERIS_PROVIDER`,
`CLOUDCOST_AWS_REGION`), `RunConfig.env` is `{}`, and both D2 guard warnings fired, so the run was
in the poisoned-but-guarded posture the criterion expects.

**Still open, deliberately:** a prompt declaration *instructs* the timeout, it does not
structurally remove the model from the success path. `pre_tools`
(`../aetheris/lib/aetheris/run_config.ex:44-47`) is the only mechanism that would; not taken, for
the three reasons in `cloudcost/docs/bl-096-implementation-notes.md`. File a follow-up if
prompt-adherence ever proves insufficient.

`Source: BL-085, 2026-08-04 (diagnosing cloudcost-orch-aws--ez4vQ); closed same day by
cloudcost-orch-aws-3KU2NQ.`


## Drift apparatus (optional hardening)

### BL-009 — Promote sprint drift_check to `--strict` (#50)
**Status:** DONE
**Size:** S · **Priority:** after BL-001

Zero standing WARNs was achieved (f2/provenance command tables added).
Flip the sprint.sh case to `drift_check.py --strict` so new WARNs fail the
sprint instead of accumulating into the next alarm-fatigue cycle.

**`project_knowledge` staleness exemption (decision 2026-07-15).** Under
`--strict`, manifest-*staleness* WARNs are reported but do **not** fail —
every doc commit re-stales the manifest until the next export, so mid-cycle
staleness is expected truth between export boundaries, not regression. The
invariant becomes **"zero *unexplained* WARNs"**, not "zero WARNs".
Structural manifest problems (missing manifest, unknown repo, git failure)
are **not** exempt and still fail. Land the promoted standing rule in
CLAUDE.md alongside: *ticket text quoting repo state cites the commit it was
verified against; divergence is a deviation to note, never silently follow*
(source: BL-001, BL-015, BL-002).

**Done when:** sprint runs `--strict` and passes; CLAUDE.md doc-sync
section documents strict mode, the exemption + rationale, and the standing
rule.

**Depends on:** BL-001 (#42)

**Status:** Done 2026-07-15. `drift_check.py` `--strict` exempts
`project_knowledge` staleness via a `strict_exempt` flag on `record`
(only the staleness WARN at the manifest-comparison site; structural pk
WARNs still promote to FAIL). `sprint.sh` drift case flipped to `--strict`.
CLAUDE.md doc-sync section updated. Exemption isolation verified: staleness
WARN → exit 0; a milestone_status WARN → `--strict` exit 1.

---

### BL-041 — Manifest-staleness done-checks are vacuous pre-commit; `drift_check` reads committed state only (#TBD)
**Status:** DONE
**Size:** S · **Priority:** medium

Surfaced by BL-034's own verification (fe8298c, 2026-07-22), and caught by the executing
session as a Silent-wrong-answer in its own gate order — recorded here because a deferred
finding gets a row, not packet prose.

`check_project_knowledge` (check 8) computes each row's "actual" hash via
`_git_head_hash` → `git log -1 --format=%h -- <path>` (`scripts/drift_check.py:623-628`),
which reads **committed** history. A working-tree (uncommitted) edit to a manifest-tracked
doc creates no commit, so it is **invisible to check 8**: a `drift_check --strict` run
*before* the edit is committed reports the manifest clean whether or not the edit was
made. At BL-034 the pre-commit `--strict` run showed 0 WARN; the predicted
`backlog-2026-06.md` staleness WARN only materialized after fe8298c.

**Class: Silent-wrong-answer, in the verification order rather than the checker.** A
pre-commit gate on a manifest-staleness question passes identically in the broken and
fixed worlds — it looks like confirmation but exercises nothing about the edit. Ask what
the gate would show if the staleness were real: identical → it verifies nothing.

**Two dispositions (decide before implementing):**

- **(a) Convention, doc-only (cheap, do now).** Encode in the CLAUDE.md doc-sync section
  (and the export/handoff conventions): *any done-check that turns on manifest staleness
  runs post-commit; a pre-commit drift_check on a tracked-file edit is a vacuous PASS.*
  One rule, no tooling change.
- **(b) Tooling guard (optional hardening).** `drift_check` emits a WARN (or INFO) when a
  manifest-tracked path has uncommitted working-tree modifications (`git status
  --porcelain -- <path>`), so the gap is visible in the tool instead of relying on gate
  discipline. This closes the manifest-blind direction from the *other* side — the header
  already warns the check cannot see an upload without a regen; this is the same blindness
  to an uncommitted edit. Reuses the `?`/INFO-vs-WARN split the checker already has.

**§7 learning candidate.** The Silent-wrong-answer entry gains a verification-ordering
instance. Below the ≥2-ticket threshold on its own — promote when a second instance lands,
or by explicit human ratification, per §7. Recorded here as the first instance so the
recurrence is countable.

---

### Worked instance — BL-025, 2026-07-23 (second instance; disposition (b) now warranted)

BL-025 edited **three** manifest-tracked docs (`docs/backlog-2026-06.md`,
`../aetheris/docs/aetheris/runbook.md`,
`../aetheris/docs/aetheris/determinism-contract.md`). The same gate, run either side of the
commit boundary:

```
pre-commit   (working tree):   7 PASS  0 FAIL  1 WARN   backlog stale
post-commit  (8021a59/00ddd34): 7 PASS  0 FAIL  3 WARN   + runbook, + determinism-contract
```

All three are the exempt staleness class and both runs exit 0, so nothing was *wrong* — but
the pre-commit number was **understated by two**, and it was the number that went into the
review packet's done-check section as the cross-repo gate result.

**Why this instance is decisive for the disposition choice.** The executing session had
already read this row, and *flagged the vacuity in the packet from this row's own text* —
naming BL-041, stating that the pre-commit reading was vacuous in both directions and that
the hash would move after commit. It then reported "1 WARN" anyway. So disposition **(a)**,
the doc-only "run it post-commit" convention, was tested under the most favourable possible
conditions — the rule was known, cited, and consciously applied by the person holding it —
and still did not produce the right number. Discipline did not surface the gap; only the
commit did.

That moves **(b)** from "optional hardening" to warranted. A rule that fails while its own
author is quoting it is not a rule problem to be solved with better wording; the checker has
to say it. Recommended: implement (b), and keep (a) as the human-facing companion rather
than the primary defence.

**Class, in its own right.** "1 WARN" was well-formed, authoritative, and wrong by two —
Silent-wrong-answer in the summary-headline carrier, not merely in the verification order.
It would have looked identical had the run concealed ten stale docs instead of two.

**§7 status: second instance, now countable at 2** (BL-034 fe8298c, BL-025 8021a59/00ddd34),
same class and same verification-ordering form. That clears the ≥2 bar on its face; promotion
wording is still a milestone-boundary act with human ratification, per §7 — recorded here, not
self-promoted.

**Done when:** the post-commit ordering rule is recorded (disposition a), and the tooling
guard (disposition b) is either implemented in the `--strict` run with a
`tests/test_drift_check.py` case both directions, or explicitly declined on this row with
a reason.

`Source: BL-034 review packet flagged observation, fe8298c, 2026-07-22; worked instance
BL-025, 8021a59 + 00ddd34, 2026-07-23.`

---

### BL-041 — DONE 2026-07-25 (both dispositions)

**(a) Convention — `1013a95`.** The post-commit ordering rule is in `CLAUDE.md`'s doc-sync
section: a `drift_check --strict` before committing a manifest-tracked edit is vacuous;
run it after the commit and *name* the exempt `project_knowledge` staleness WARNs rather
than chasing them. Kept as the human-facing companion, not the primary defence.

**(b) Tooling guard — `11675cc`.** `_git_is_dirty` runs `git status --porcelain -- <path>`
per manifest row **in that row's owning repo** — the harness rows live in the sibling
`../aetheris` checkout, and porcelain against `REPO_ROOT` would report every one of them
clean, which is the same blindness one layer down. A dirty tracked path gets a per-path
**strict-exempt WARN** naming that check 8 compares committed history, so its staleness
reading for that path is vacuous, and to re-run after committing. Structural arms (missing
manifest, unknown repo, git failure — now including a `git status` failure) stay
**non-exempt** and still FAIL under `--strict`.

The closing PASS is suppressed while any tracked path is dirty. "N manifest entries all
match git HEAD" is a well-formed, authoritative answer to a question the run cannot yet
answer — the Silent-wrong-answer carrier this row was filed against, and it would have
survived the guard otherwise.

**The two signals are complementary across the commit boundary**, which is what closes the
gap discipline could not. For a path whose manifest entry is *fresh at the export*: pre-commit
only the uncommitted WARN can fire and the staleness WARN cannot, because the committed hash
still matches; post-commit the uncommitted signal clears and the real staleness WARN takes its
place. They are not mutually exclusive in general — a path already stale from an earlier
commit in the same cycle fires **both** while it is dirty (observed on this ticket's own r1
edit to this file, stale from `de46ac0` and uncommitted at once). That compound state is
correct and is the point: the uncommitted WARN says the staleness reading is not final, not
that there is no staleness. Both are strict-exempt, both exit 0.

**Self-exercised by its own landing.** This row's DONE edit is to `docs/backlog-2026-06.md`,
itself manifest-tracked, so the ticket ran the boundary it describes: while the edit was
uncommitted the new guard fired for that path and the staleness WARN could not; after the
commit the guard cleared and the exempt staleness WARN took its place. Both `--strict` runs
exit 0, and both are recorded verbatim in the review packet and in the implementation notes.

**§7 status.** The Silent-wrong-answer verification-ordering instance stands at 2 (BL-034
`fe8298c`, BL-025 `8021a59`/`00ddd34`) and was promoted as disposition (a) at `1013a95`.
No new promotion is claimed here; (b) is the mechanical enforcement of the rule already
promoted.

**r1 — review F1 folded, `0d5127b`.** The closing PASS was suppressed for `stale` and
`uncommitted` rows but **not** for rows that failed *structurally* (unknown repo, `git log`
failure, and the new `git status` failure), so a skipped row could sit beside
"`N` manifest entries all match git HEAD" — a count including rows never checked. Pre-existing
and `--strict`-safe (structural WARNs promote to FAIL), but it is this ticket's own
Silent-wrong-answer class one arm over, in the function already being edited, so it was folded
rather than filed. `check_project_knowledge` now tracks `structural` alongside the other two and
gates the PASS on all three; with the gate in place `len(rows)` is accurate wherever the PASS
prints, so the count needed no narrowing. Two tests, one per arm — `git log` failure, and the
unknown-repo arm which `continue`s before either guard. Mutation-checked: without the fold both
go red, and the run prints the contradictory pair the finding describes.
Review: `docs/reviews/bl-041b-bl-036-review.md`.

`Source: 1013a95 (a), 11675cc (b), 2026-07-25. Notes:
docs/rig/milestones/bl-041a-promotion-implementation-notes.md,
docs/rig/milestones/bl-041b-bl-036-drift-check-guards-implementation-notes.md.`

---

### BL-042 — Capability-shaped containment for the verify worker (`CLONE_NEWNET`) (#TBD)
**Status:** DONE
**Size:** M · **Priority:** medium · **Section:** Harness (aetheris/)

BL-025 classifies `run_command` `:contained` and record-and-serves only the purpose-network
tools (`http_call`, MCP). But the verify sandbox confines filesystem only — no network
namespace (`CLONE_NEWNET` absent, `sandbox.rs:144`), seccomp permits `connect`
(`sandbox.rs:265-278`) — and the exec allowlist (`aetheris_exec_server/src/runner.rs:7-24`)
permits `python3`/`node`/`npm`/`mix`/`cargo`/`git`, every one socket-capable
(`npm install` / `mix deps.get` egress by design). So verify re-executing a `run_command`
that ran a networked script **egresses**, regardless of BL-025's record-and-serve. The
containment is command-shaped, not capability-shaped (found at BL-025, HEAD `d567d75`).

Fix: add `CLONE_NEWNET` to the verify worker's namespace set so re-execution cannot egress
regardless of allowlist — capability-shaped containment. This makes BL-025's record-and-serve
**defence-in-depth** for the purpose-network tools rather than the sole (and partial) defence.

**Builds on BL-025, does not race it.** Under a network namespace, `http_call`/MCP would
*fail* (no network) rather than egress — so record-and-serve (BL-025) must be landed first,
or those tools break under verify. Sequence BL-042 after BL-025.

**Adjacent — decide, don't assume:** a networked `run_command` re-executed under a netns will
*diverge* (the script fails/times out) rather than reproduce. That is verify honestly
reporting a non-reproducible (network-dependent) step, but the divergence message must read
as "network unavailable under verify," not a spurious content mismatch — specify the surfaced
error. Do not silently skip it.

**Interacts with BL-043.** BL-043 (missing `setsockopt`) currently truncates worker egress at
`connect(2)` by accident. Fixing BL-043 restores full egress and makes this row's exposure
larger, not smaller; fixing this row makes BL-043's repair safe. Neither is a substitute for
the other — do not let BL-043's accidental truncation be read as containment.

---

### Pre-implementation handoff (verified at `8021a59`, 2026-07-23)

Recorded here, not in BL-025's implementation notes, because the next session reads *this
row* and not the previous ticket's notes. Each item below was checked against source; treat
them as verified ground, not leads.

**H1 — the premise holds: the exec server inherits the netns.** This was the way the row's
fix could have been quietly false — `run_command`/`git_*` are dispatched to a *separate
process*, so the netns closes their egress only if that process is inside it. Startup order
in `native/aetheris_worker/src/main.rs` settles it: `enter_namespaces()` at `:53` → exec
server spawned at `:80` (comment: "before seccomp filter — execve is blocked after") →
`apply_seccomp_filter()` at `:92`. The exec server is spawned **after** `unshare`, so it
inherits the namespaces. Adding `CLONE_NEWNET` at `sandbox.rs:144` therefore does cover
`run_command` and the eleven `git_*` tools. (Note the exec server is *not* under the seccomp
filter — a separate process, filtered independently — which is why BL-043's `setsockopt`
kill affects `http_call` but not `run_command`.)

**H2 — `lo` comes up DOWN in a fresh netns. Decide, don't default.** A new network namespace
has only a loopback interface and it starts down, so 127.0.0.1 is unreachable until something
brings it up. Nothing in the worker needs it: the worker↔BEAM channel is pipes (`Port`), and
MCP stdio is pipes. **Recommendation: leave `lo` down** — it is the stricter choice and
matches the row's goal; bringing it up would re-admit localhost-only egress for no benefit
verify needs. Flagged for ratification, and whichever way it goes it must be a stated
decision in the implementation notes, not an unexamined default.

**H3 — `enter_namespaces()` fails open, and verify must not inherit that.** `unshare`
failure is logged and execution continues (`sandbox.rs:146-153`: "Fails open: if `unshare` is
rejected by the kernel (e.g. in restricted container environments), the error is logged and
the worker continues without isolation"). So in a restricted container there is **no netns**,
and verify would report a clean result while having had none of the containment it claims —
a well-formed verdict over a gap, which is the Silent-wrong-answer class BL-025 exists to
remove. **Verify cannot stay silent about this.**

  - **RATIFIED 2026-07-23 (human): fail closed.** Verify refuses to re-execute and errors
    (`cannot establish network containment`) rather than proceeding under a banner. This is
    settled — implement it, do not re-litigate.

    Two reasons, recorded so a future reader sees the argument and not just the verdict.
    (i) Verify's entire value *is* the guarantee, so a verify that cannot guarantee has
    nothing to report; a banner is the mitigation you choose when refusing is not an option,
    and here it is — `--allow-effects` already names the deliberate-uncontained path (H4),
    so a *silently* uncontained default has no constituency.
    (ii) **Fail-closed is the reversible direction.** The niche it does not serve is the
    operator who wants default behaviour (serve uncontained, re-execute contained) but cannot
    get a netns; only degrade-and-report serves that. Checked at `8021a59`: nothing in this
    repo runs verify inside a restricted container — CI excludes `:requires_worker`
    (`ci.yml:64`) so the worker never starts there, Rig invokes verify nowhere, `sprint.sh`
    runs on the host. The niche is empty today. If it later appears, degrade-and-report is
    *additive* (a new flag or downgraded verdict, strict default intact); shipping it first
    and tightening later would be a behaviour change on the default path needing its own
    contract edit and migration. Cheap-to-reverse wins.
  - **`record` mode keeps its fail-open.** Normal runs in restricted containers must keep
    working; do not tighten `enter_namespaces` globally.

**H4 — the netns MUST be gated on `not allow_effects`. Required, not optional.** An
unconditional netns breaks `--allow-effects`: the flag exists precisely to re-issue real
network effects, and inside a netns it cannot. It would also flip BL-025's opt-in test
(`test/aetheris/execution/verify_effects_test.exs` — `--allow-effects` → **≥1** connection to
a listener living outside the netns) to 0, i.e. the regression guard for the opt-in path
would silently invert into asserting the opposite of what it was written for.

  - default verify → **netns on**: contained tools re-execute but cannot egress (this row's goal)
  - `--allow-effects` → **netns off**: re-execute everything with real egress (the explicit opt-in)

  It is a clean per-verify decision because BL-025's `Verifier.execute_planned_steps/3` starts
  exactly one worker per verify, and `allow_effects` is already resolved at that point.

**H5 — scope: this is not a one-line flag add.** Three pieces, in order:

  1. **Conditional `CLONE_NEWNET`** — the flag must be *requestable*, so it rides the init
     payload: `Worker.Client.worker_init_payload/5` (`lib/aetheris/worker/client.ex:58-70`)
     builds the map (`sandbox_path`, `memory_limit_bytes`, `cpu_quota_percent`, optional
     `overlay`); add a `network_namespace` field plus a matching `Client.start_link` opt
     (`init/1`, `:157-171`), and have `enter_namespaces` take it.
  2. **Establishment-status plumbing** — and note the ordering problem: the worker writes
     `{"status": "ready"}` at `main.rs:51`, **before** `enter_namespaces()` at `:53`. The
     existing handshake therefore *cannot* carry the netns result without reordering it (move
     the ready write after namespace setup, or add a second message). Whichever is chosen,
     `enter_namespaces` must report whether `CLONE_NEWNET` was actually established rather
     than only logging.
  3. **Verify's non-silent handling** of that status, per H3.

**H6 — reuse the existing hermetic harness.** `test/aetheris/execution/verify_effects_test.exs`
(BL-025) already provides a localhost listener that counts inbound connections, and the
`recorded-trajectory` fixture shape. BL-042's egress test is the same harness pointed at a
`run_command` that shells out to `python3` (allowlisted) opening a socket — expect **0** under
default verify. Its `--allow-effects` arm must keep recording **≥1** (H4).

**Decision status.** H3 (fail closed) — **ratified, human, 2026-07-23**. H2 (`lo` down) —
**agreed in review 2026-07-23**; still must be *stated* as a decision in the implementation
notes rather than left as an unexamined default. H4 (netns gated on `not allow_effects`) is a
requirement, not a choice. Nothing here is open; the implementer starts from settled ground.

**Done when:** the verify worker runs under `CLONE_NEWNET` **when re-executing without
`--allow-effects`**; a `run_command` recorded doing network egress cannot egress during
verify (hermetic listener: 0 hits) and its divergence is reported legibly; the
`--allow-effects` path still egresses and BL-025's opt-in arm still asserts ≥1 (H4); netns
establishment is reported by the worker and acted on by verify, never silently assumed (H3),
with `record` mode's fail-open untouched; `http_call`/MCP remain served (BL-025) and do not
fail under the netns; §5's egress-safety statement upgrades from partial to
capability-complete, human-approved in-cycle (§8) — **and that §5 edit is two statements, not
one**: (a) the upgrade itself, and (b) the guarantee is *conditional on the netns being
establishable*, with the fail-closed refusal (H3) named as contract-visible behaviour, since
an operator whose kernel denies `unshare` gets an error instead of a verdict. Drafting (a)
without (b) would restate the exact overclaim BL-025's §5 rewrite was written to remove —
a capability-complete guarantee asserted unconditionally over an environment that cannot
provide it. Draft both in one review-file artifact for a single approval, as BL-025 did with
§3+§5.

`Source: BL-025 execution, run_command allowlist finding, HEAD d567d75, 2026-07-22.
Pre-implementation handoff verified at 8021a59, 2026-07-23.`

---

### BL-042 — DONE 2026-07-23

**Landed:** conditional `CLONE_NEWNET` (`sandbox.rs:161-224`, gated on the init payload's
`network_namespace`), establishment status reported through a reordered handshake (namespaces
entered *before* `ready`, which now carries `network_namespace` — `main.rs:56-74`),
fail-closed enforcement in `Worker.Client.init/1` via `containment_verdict/2`, the netns
requested as `not allow_effects` by `Verifier` (`verifier.ex:89-96`), a legible CLI refusal,
and `network_isolated` on `VerifyReport` so a networked divergence is interpretable.

**Grew in-cycle by one tool, and the growth was load-bearing.** H6's red-first arm could not
be written as specified: `Verifier` sent every tool to the worker's own dispatch table, but
`run_command` is an exec-server MCP tool, so it re-executed as `unknown_tool:run_command` and
opened **0 connections before the netns existed**. The row's "0 hits" done-when was already
true, for a reason that had nothing to do with containment — a check that could not fail.
Routing `run_command` (scoped decision, human, 2026-07-23) made the red arm real; the
`git_*` family was left alone and filed as **BL-047** with the taxonomy question it deserves.

**Evidence** (`test/aetheris/execution/verify_effects_test.exs`, `--include requires_worker`;
the tag is excluded by default, so a plain `mix test` exercises neither arm):

| arm | connections | step status |
|---|---|---|
| pre-fix, unrouted | 0 | `:error` — `unknown_tool:run_command`, never ran |
| pre-netns, routed | **1** | re-executed and egressed — the red arm |
| default verify (netns) | **0** | `:output_mismatch` + isolation note |
| `--allow-effects` | **≥1** | re-executed and egressed — opt-in preserved (H4); status not asserted, see BL-049 |

**Decisions recorded** (implementation notes: `../aetheris/docs/aetheris/milestones/bl-042-implementation-notes.md`):
H2 `lo` left down — no code brings it up. On a `/proc` mapping-write failure the worker keeps
its log-and-continue and reports `network_namespace: false`, so record's fail-open survives
that path too while verify still refuses. Non-Linux hosts report `net: false`, so a default
verify there refuses — fail-closed working as ratified, named in §5 rather than discovered.

**Off-territory gate finding:** `mix test --include requires_worker` is red with 15 failures,
identical on a clean tree — filed as **BL-048**, not carried silently.

**§5 contract edit:** drafted in `docs/reviews/bl-042-contract-draft.md` as three statements
— (a) partial → capability-complete, (b) conditional on establishability with the fail-closed
refusal named as contract-visible, and (c) the correction of BL-025's false "`:contained` …
re-executed and compared" claim. Lands only on human approval per §8.

---

### BL-043 — `http_call` is killed by seccomp (SIGSYS) in every mode: `setsockopt` missing from the allowlist (#TBD)
**Status:** DONE
**Size:** S · **Priority:** medium · **Section:** Harness (aetheris/)

`http_call` does not work at all — not in verify, not in a normal **record** run. The worker's
seccomp allowlist (`native/aetheris_worker/src/sandbox.rs`) carries a section explicitly
headed *"Network (http_call + MCP stdio)"* listing `socket`, `connect`, `sendto`, `recvfrom`,
`sendmsg`, `recvmsg`, `bind`, `listen`, `accept4`, `poll`, `epoll_*` — but **omits
`setsockopt`** (x86_64 syscall 54), which `ureq` calls to set timeouts immediately after
`connect(2)`. The filter's default action is `KillProcess`, so the worker dies of SIGSYS.

**Demonstrated at BL-025** (hermetic localhost listener + kernel audit, 2026-07-23):

```
audit: type=1326 … comm="aetheris_worker" … sig=31 arch=c000003e syscall=54 code=0x80000000
worker exit status 159   (128 + 31 = SIGSYS)
Worker.Client.execute → {:error, "worker_crashed"}
INBOUND TCP CONNECTIONS TO LISTENER: 1
```

So the TCP connection **does** land; only the HTTP request is never written.

**Do not read this as containment.** It is an unintended truncation of a real egress path,
and the "Network" heading shows egress was the intent. Two consequences:

- **`http_call` is unusable.** Any agent using it gets a crashed worker, not a response. That
  the defect went unnoticed suggests the tool has no live users — worth confirming before
  choosing a fix direction.
- **It is load-bearing by accident.** Adding `setsockopt` restores full egress instantly,
  which widens BL-042's exposure. Sequence: BL-025 (landed) → BL-042 (netns) → this row, or
  accept the widened window knowingly.

**Second defect, same path:** `Verifier` starts the worker with `Client.start_link`, so a
worker that dies takes the **caller** with it (`{:worker_crashed, 159}` propagates as an exit
signal). A library function should not kill its caller because a sandboxed tool crashed; the
BL-025 test traps exits to assert around it. Decide whether the verify worker should be
started unlinked or supervised.

**Operator-visible consequence, observed at BL-025:** the two defects compose, so
`aetheris verify <traj> --allow-effects` on any trajectory containing `http_call` **crashes
the CLI** rather than reporting a verdict:

```
** (stop) {:worker_crashed, 159}
** (EXIT from #PID<0.95.0>) {:worker_crashed, 159}
```

BL-025's opt-in flag is proven to route correctly (the step is served without it, re-executed
with it — 0 vs 1 inbound connections at a hermetic listener), but the opt-in is not
practically usable for `http_call` until this row lands. Not a BL-025 regression: the same
crash occurs on the pre-BL-025 code path and in record runs.

**Done when:** `setsockopt` (and any other syscall a real `ureq` request needs — enumerate by
running one, do not guess the list) is either added to the allowlist with an `http_call`
round-trip test against a hermetic local listener, or `http_call` is explicitly retired; the
worker-crash-kills-caller behaviour is resolved or consciously accepted with a reason.

`Source: BL-025 execution, demonstrated 2026-07-23 (kernel audit + hermetic listener).`

---

### BL-043 — DONE 2026-07-25 — `http_call` repaired (5 syscalls), caller-kill fixed

Landed at harness `515a4ab`, with the §5 contract edit ratified at `1e00a52` (r1). Direction:
**repair, not retire**. Contract edit: `docs/reviews/bl-043-contract-draft.md` (harness) —
**RATIFIED (generalized)**, §8, 2026-07-25.

**§5 names no syscalls, by review disposition.** The r0 draft listed three of the five and
misattributed one (`getsockopt` is a resolver call, not a `ureq` call) — the contract had drifted
from the code inside a single ticket. The ratified clause points at `sandbox.rs`'s commented
"Network" list instead, which is the only copy that cannot fall out of step with the code.

**No-live-users checkpoint, run first as the row required.** The scan found only declarations,
tests and contract examples — no working dependent, as expected of a tool that has SIGSYS-crashed
since forever. Two agent files list it (`agents/news_research.exs`, `agents/pr_learner.exs`), and
the m07→m08 handoff records `pr_learner.exs` as *"run after `http_call` stable"* — it was deferred
pending exactly this fix. Two milestone docs list `tools: ["http_call"]` as a worker-start
*workaround*, already resolved elsewhere. Repair therefore unblocks `pr_learner.exs` rather than
disturbing anything.

**Five syscalls, not one — and they took three rounds to find.** The row named `setsockopt`; the
enumeration turned up four more. Method: patch the filter's default action to non-killing, drive
the real worker binary over its stdio protocol against a hermetic localhost listener under
`strace -ff`, diff the request-path syscalls against the allowlist, then restore `KillProcess` and
re-probe. Each round's probe found the *next* wall:

| Round | Probe | Syscall(s) found |
|---|---|---|
| 1 | `http://127.0.0.1:PORT/` (IP literal) | `setsockopt` (TCP_NODELAY, then SO_RCVTIMEO/SO_SNDTIMEO), `getsockname` |
| 2 | `http://localhost:PORT/` (resolver via `/etc/hosts`) | `getsockopt` |
| 3 | `http://…invalid/` (real nameserver query) | `sendmmsg`, `recvmmsg` — glibc sends A+AAAA in one call |

Round 2 is why "enumerate, don't guess" earned its place: `localhost` resolves from `/etc/hosts`
and never issues a DNS query, so a hostname probe that *looks* like it covers resolution does not.
Only a name that must reach a nameserver surfaced the last two.

**Verified against three paths under the live `KillProcess` filter**, all worker-exit-0: plaintext
localhost round-trip returns `{"status":200,"body":"live"}`; a real DNS lookup returns a clean
`Dns Failed … Name or service not known`; and HTTPS to a self-signed local listener returns a
clean certificate-validation error — i.e. the TLS handshake path is covered too. The suite's
`https://httpbin.org/get` test now reaches the real host and fails on *its* `503`, which is the
clearest possible evidence the request completes end-to-end.

**A near-miss worth recording.** The first "successful" round-trip was a false green: adding
`setsockopt` to the allowlist without adding it to `syscall_number/1` made filter *construction*
fail, and `apply_seccomp_filter` **fails open** — so the worker ran with **no filter at all** and
`http_call` worked because the sandbox was gone. A typo in that list silently disables the entire
sandbox while every tool test stays green. Three Rust tests now guard it: every allowlist name
resolves, the filter builds, and the five socket calls are present by name.

**Caller-kill (part 2): unlinking was necessary but not sufficient.** `Verifier` now starts the
worker via a new `Client.start/1` (unlinked) plus a monitor, `demonitor(:flush)` on every exit
path — unlinked+monitor rather than supervised because the worker has a one-call lifecycle and a
re-executed step must not be restarted. But `GenServer.call` *independently* exits the caller with
the server's reason when the server dies mid-call, so the unlink alone left the crash path intact;
`execute/2` and `call_mcp_tool/4` now convert any such exit into `{:error, "worker_crashed"}`,
matching what the port handler already replies to dispatched requests. Both halves are
mutation-checked, and a verify-level test kills the worker *from inside a re-executed step* (via
`/proc` to reach the grandparent pid) — without it, reverting to `start_link` reddened nothing.

**Result: `requires_worker` 12 → 11 failures; SIGSYS 8 → 4.** Not the ~4 total the ticket
predicted, because the 8 SIGSYS were **two different gaps**, not one — see BL-055. The four this
row fixed are gone; the four that remain are MCP-stdio spawn hitting a *deliberate* exclusion, and
they must not be "fixed" by widening the filter.

`Source: BL-043, 2026-07-25. Captures: full_requires_worker{,2}.txt, strace rounds 1–3.`

---

### BL-050 + BL-055 + BL-056 — DONE 2026-07-25 (one reorder, three rows)

Landed together at harness `9871059` — they were the same surgery — with the §5 contract edit
ratified at `dd12dbb` (r1). Contract edit: `docs/reviews/bl-050-055-056-contract-draft.md`
(harness), **RATIFIED (hedged)**, §8, 2026-07-25. Review: `docs/reviews/bl-050-055-056-review.md`.

**§5 was hedged at review, and the operator message deliberately was not.** The r0 wording asserted
that container runtimes refusing `unshare` do not refuse `seccomp` — the exact claim the scout memo
had listed as *unverified*. §5 now says the filter is *rarely* refused and admits no survey was
done; the one-line error in `verify.ex` still says "harness defect, not an environment limitation",
because its job is to stop an operator reaching for `--allow-effects`. That split is recorded in §5
itself and in the draft so a later reader does not reconcile one to the other.
Scout memo that settled the directions: `docs/reviews/bl-055-bl-056-containment-decisions.md`.

**The one change.** `ready` was written straight after the namespaces while cgroup, overlay,
exec-server spawn and the seccomp filter all happened *after* it. `ready` is now the
**fully-established barrier**:

```
namespaces → cgroup → overlay → exec server → stdio MCP servers → seccomp → ready(attests all)
```

and the handshake carries `overlay`, `exec_server`, `seccomp` (+ error) and a per-server
`mcp_servers` attestation alongside `network_namespace`. Order is forced: the filter must be last
because the exec server and the stdio servers both need `execve`, which it excludes.

**BL-050** — the overlay is mounted before the handshake, so `RunOverlayTest`'s `File.dir?(upper)`
immediately after start no longer races. Green, no sleep, no polling.

**BL-055 (option 1)** — `config.mcp_servers` travels in the init payload (stdio entries only;
`:http` still connects at request time through the exec server, which the filter permits). The
worker spawns them pre-filter and attests each. `loop.ex` no longer spawns — it only lists tools.
The request-time `mcp_spawn` is **removed** on both sides rather than left as a call that always
killed the worker; `spawn_mcp_server/2` became `connect_http_mcp_server/2`, which refuses a stdio
config. Verify passes no `mcp_servers`, so a verify worker spawns none.

**BL-056** — the worker still fails open and now *attests*; policy moved to the BEAM, which is the
only side that knows the mode. Verify **refuses** with a message that shares no wording with the
netns refusal and does **not** offer `--allow-effects` (the flag would not install a filter and
would drop the network guard too). Record **continues**, but no longer silently: `Logger.error` at
worker start plus `meta.containment` in the trajectory, so a later reader can tell a sandboxed run
from an unsandboxed one. That silence was the defect, not the fail-open.

**Risks checked rather than assumed.** Time-to-ready after the reorder: **2–3 ms** bare, **17–20 ms**
with a stdio MCP server declared, against the **5 000 ms** init timeout — three orders of magnitude
of headroom, no adjustment needed. `requires_worker` run **twice**: 6 failures both times with
**identical membership**, so the reorder introduced and shifted no flake; the BL-054 slot did not
appear in either run.

`Source: BL-050/055/056, harness 9871059, 2026-07-25.`

---
### BL-056 — `apply_seccomp_filter` fails open: any filter-build failure runs the worker fully unsandboxed (#TBD)
**Status:** DONE
**Size:** S–M · **Priority:** medium · **Section:** Harness (aetheris/)

Filed from BL-043's flagged observation at review r1, per the standing rule that a deferred
finding gets a row rather than packet prose.

**The defect.** `Sandbox.apply_seccomp_filter/0` returns `Err` on any build failure, and the caller
logs a single stderr line and **continues** (`main.rs`):

```
[sandbox] seccomp filter failed: unknown syscall: setsockopt
```

The worker then runs with **no filter at all**. Nothing else reports it: the handshake still says
`ready`, tools still work — better than before, in fact — and every test stays green. The failure
mode of a disabled sandbox is *more* capability, so nothing downstream notices.

**BL-043 tripped this live, which is why it is filed rather than theorised.** Adding `"setsockopt"`
to the allowlist without adding it to `syscall_number/1` made construction fail; the resulting
`http_call` round-trip **passed**, and it passed *because the sandbox was gone*. A green test was
the evidence of the protection's absence.

**Why the BL-043 guards do not close it.** The three Rust tests added there (every allowlist name
resolves; the filter builds; the five socket calls are present) close the **typo vector at test
time**. The runtime fail-open remains for every other build-failure path: a seccompiler shape
rejection (it rejects identical match/mismatch actions — also hit during BL-043), an architecture
`TargetArch::try_from` failure, or a kernel that refuses `SECCOMP_SET_MODE_FILTER`.

**The parallel that frames the decision.** Verify already **fail-closes** on its *other* containment
primitive: a worker that cannot establish the network namespace never finishes starting, and
`aetheris verify` reports `cannot establish network containment for verify; re-run with
--allow-effects …` rather than a verdict (§5, "When containment cannot be established"). The
seccomp filter — the primitive that confines everything the namespace does not — fail-opens
instead. Those two should not disagree.

Fail-open is **correct** for `enter_namespaces` in *record* mode, and that must not change: a
normal run in a restricted container has to keep working, and §5 says so explicitly. The question
is narrower — should **verify** proceed with an unfiltered worker?

**Done when:** the question is decided and recorded — verify refuses to run unfiltered (the netns
parallel), or accepts it with a reason written down — and the chosen behaviour is implemented with
a test that exercises the *failure* path, not just the happy one. If refuse is chosen, the refusal
must be distinguishable in the report from the netns refusal, since an operator needs to know
which primitive was unavailable. The refuse-vs-accept call is **§8/human**; this row carries it.

`Source: BL-043 done-check flagged observation, review r1 disposition, 2026-07-25.`

---

### BL-055 — MCP stdio servers cannot be spawned after the seccomp filter: `execve` is excluded by design (#TBD)
**Status:** DONE
**Size:** M · **Priority:** medium · **Section:** Harness (aetheris/)

Surfaced by BL-043's done-check, which expected to clear all 8 of BL-048's SIGSYS failures and
cleared 4. The other 4 are a different defect wearing the same symptom.

`Client.spawn_mcp_server/2` sends `mcp_spawn` to the worker **at request time**, i.e. *after*
`apply_seccomp_filter`. Spawning a subprocess there needs `prilimit64` then `execve`, and neither
is in the allowlist. Traced, not inferred — the worker dies at `prlimit64` immediately after two
`pipe2` calls:

```
read(0, "…{\"id\": \"1\", \"command\": \"mcp_…"…) = 109
pipe2([3, 4], O_CLOEXEC)                = 0
pipe2([5, 6], O_CLOEXEC)                = 0
prlimit64(0, RLIMIT_NOFILE, …)          = 302
+++ killed by SIGSYS (core dumped) +++
```

**This exclusion is deliberate, and BL-043 deliberately did not touch it.** `main.rs:95` says so
in as many words — *"Spawn internal exec server before seccomp filter — execve is blocked after
filter is applied"* — and the harness spawns its own exec server pre-filter for exactly this
reason. Adding `execve` to the allowlist would let a sandboxed worker execute arbitrary binaries
after the filter is installed, which is a containment decision far larger than a test fix, and
BL-043's ticket explicitly forbade weakening containment to make tests pass.

So the four affected tests (`spawn_mcp_server/2`, `list_mcp_tools/2`, `call_mcp_tool/4` in
`client_test.exs`, and `McpGithubTest`, which spawns `github-mcp-server` over stdio) assert a
capability the sandbox removes. One of three things is true and someone has to choose:

1. **Stdio MCP servers must be spawned pre-filter**, like the internal exec server — i.e. from the
   init payload, with the server list known at worker start. This preserves containment and makes
   the capability real, at the cost of no longer being able to add servers mid-run.
2. **Stdio MCP spawn is unsupported** and the tests are stale — HTTP-transport MCP and the
   pre-spawned exec server remain the supported paths.
3. **The filter is relaxed** for this case. Named for completeness; it is the option that trades
   the sandbox for a convenience and should not be chosen quietly.

**Done when:** one of the three is chosen and recorded; the four tests either pass under the
chosen design or are removed/retagged with the reason; and if (1), the mid-run spawn API is
removed rather than left as a call that always crashes the worker.

`Source: BL-043 done-check, 2026-07-25 (strace of the mcp_spawn path).`

---

### BL-049 — A `run_command` step can essentially never verify: `duration_ms` is inside the compared payload (#TBD)
**Status:** DONE
**Size:** S · **Priority:** medium-high · **Section:** Harness (aetheris/)

`Verifier.compare_status/4` compares recorded vs re-executed tool output by **value equality**
over the whole payload string. The exec server's `run_command` payload is
`{"duration_ms":N,"exit_code":N,"stderr":"…","stdout":"…"}` — it carries a wall-clock
measurement. So two runs of an identical, perfectly reproducible command differ whenever the
timing differs, which is almost always.

Measured, six consecutive runs of the same `python3` one-liner, recorded and then re-executed
under `--allow-effects` (no namespace, network reachable, identical stdout and exit code):

```
status: :output_mismatch  recorded: {"duration_ms":19,…}  actual: {"duration_ms":21,…}
status: :verified         recorded: {"duration_ms":22,…}  actual: {"duration_ms":22,…}
status: :output_mismatch  recorded: {"duration_ms":23,…}  actual: {"duration_ms":19,…}
status: :output_mismatch  recorded: {"duration_ms":19,…}  actual: {"duration_ms":20,…}
status: :output_mismatch  recorded: {"duration_ms":19,…}  actual: {"duration_ms":21,…}
status: :output_mismatch  recorded: {"duration_ms":21,…}  actual: {"duration_ms":20,…}
```

Five of six report a divergence that is purely timing; the sixth "verifies" by coincidence.

**Exposed by BL-042, not caused by it.** Before BL-042 routed `run_command`, the step returned
`unknown_tool:run_command` and never reached the comparison at all, so the defect was
unreachable. It is now live for any operator running `aetheris verify` on a trajectory
containing `run_command` steps: they get `Failed: N` on commands that reproduced exactly.

**Not a patch — a §5 semantics decision.** Three directions, and they differ in what "verified"
comes to mean:
- **Exclude volatile fields from comparison** (`duration_ms` today; enumerate rather than
  guess). Verify then compares what the tool *did*, not how long it took.
- **Compare structurally** rather than by string equality, with a per-tool field policy. More
  general, more machinery, and the policy is exactly the thing that needs deciding.
- **Stop returning timing inside the compared payload** — move `duration_ms` out of the tool
  output and into the step envelope, where it is recorded but not compared. Cleanest, and it
  touches the exec server's response shape plus every recorded trajectory's expectations.

Whichever is chosen, §5 must say what a `:verified` `run_command` step asserts, since today it
asserts something no honest command can satisfy.

**Adjacent, check before fixing:** `read_file`/`list_dir`/`write_file` go through the worker's
own dispatch and their `duration_ms` sits *outside* the compared `output` (`parse_execute_response/1`
splits `output`/`fs_hash`/`duration_ms`) — which is why this never surfaced for them, and why
the third direction above is the one that matches the existing worker-native shape.

**Done when:** the comparison semantics for timing-bearing payloads is decided and recorded in
§5 with a human-approved edit (§8); a recorded `run_command` that reproduces exactly reports
`:verified` deterministically; and a regression test asserts that across repeated runs, not
once.

`Source: BL-042 review, 2026-07-23 — reviewer challenged the packet's `:verified` claim for the
--allow-effects arm; measurement showed the arm is nondeterministic and the claim was wrong.`

---

### BL-049 — DONE 2026-07-24

**Direction chosen:** the third of the row's three, *"stop returning timing inside the compared
payload"* — the one the row itself flagged as matching the existing worker-native shape. The
verifier grew **one** change and it is reuse, not policy: it calls the same strip on the
recorded side. It holds no field list of its own, which is what separates this from the
rejected "exclude volatile fields in the compare".

**Landed:** `Aetheris.Execution.VolatileMetadata` as the single definition of "volatile"
(`fields/0`, `split/1`, `strip/1`); `Loop.exec_server_payload/2` splitting `duration_ms` into
the step envelope for every `aetheris_exec`-routed tool; `Verifier` stripping both the
re-executed output and — via `normalize_recorded/2` — the recorded one before comparing; the
two LLM-facing `registry.ex` descriptions corrected; a tripwire test binding the worker-native
envelope (`parse_execute_response/1`) to the same definition.

**Why the read side is not optional.** Trajectory events are immutable (critical rule #1), so
every trajectory recorded before this commit carries `duration_ms` inside the recorded blob
forever. A parse-layer-only fix would have satisfied the invariant for new records while
turning the old corpus's 1-in-6 flap into a deterministic `:output_mismatch` — a confident
wrong verdict, which is worse than a flaky one. Normalizing both sides through one definition
is what lets §5 say "resolved" without hedging to "resolved for records at or after `13ff59c`".

**Evidence** — the same hermetic `python3 -c 'print("bl049")'` trajectory, six verifies:

| | verdicts | note |
|---|---|---|
| before fix | 5 × `:output_mismatch`, 1 × `:verified` | `stdout`/`stderr`/`exit_code` byte-identical in all six; only `duration_ms` moved (recorded 10, actual 13/12/9/11/10/11) |
| after fix, pre-fix recording | 6 × `:verified` | exercises the read-side normalization; fixture asserted to still contain `duration_ms` |
| after fix, post-fix recording | 6 × `:verified` | exercises the parse-layer fix; fixture asserted to *not* contain it |

Each run additionally asserts `verified: 1`, `served: 0` and a non-empty actual output — a
served step cannot fail, so it must not be allowed to pass as a fix
(`test/aetheris/execution/verify_verdict_test.exs`, `--include requires_worker`). The
deterministic half of the proof needs no worker at all
(`test/aetheris/execution/volatile_metadata_test.exs`): two responses differing only in
`duration_ms` compare byte-identical.

**BL-042's `--allow-effects` arm tightened.** It asserted only `!= :served` because the verdict
was a coin flip; it now asserts `== :verified`, confirmed across six seeds. Two BL-042
assertions comparing `recorded_output` to the raw exec-server blob were updated: they were
asserting the pre-fix shape. They now assert the *compared* form **and** that the on-disk
recording still carries `duration_ms` — immutability of the record and exclusion of the field
from the compare are separate claims, and both are now asserted.

**Deviation from the ticket's sketch, adjudicated.** The ticket said to extract the strip *out
of* `parse_execute_response/1`. Nothing there is extractable: that function splits sibling keys
of a decoded map, while the exec-server case removes keys from a JSON object embedded in the
`output` string. The invariant ("one definition of volatile") binds; the sketch does not. It is
met by `VolatileMetadata.fields/0` plus a tripwire test on the worker-native envelope.

**Consequence stated rather than buried:** the agent no longer sees `duration_ms` in an
exec-server tool result. `payload["output"]` *is* the transcript content (`fork.ex:107`), so
the recorded and model-visible values cannot diverge without breaking fork replay. This is the
worker-native behaviour, where the field was always envelope-only.

**Decisions recorded** (implementation notes:
`../aetheris/docs/aetheris/milestones/bl-049-implementation-notes.md`): `normalize_recorded/2`
is restricted to `@exec_server_tools` rather than applied to every recorded output, because a
worker-native `read_file` result that merely *happens* to be JSON with a `duration_ms` key is
file content, not execution metadata. `Verifier`'s `@exec_server_tools` stays `run_command`
alone — verify only compares what it re-executes, and `git_*` is BL-047's decision.

**§5/§3 contract edits: LANDED, harness `a926631` (§8, human-approved 2026-07-24).** Three,
after review grew (a)'s two to three: (a) §5 gains "What the comparison ranges over" — the
compare is value equality over the deterministic portion, volatile metadata excluded, resolved
across both record eras (landed **restructured** per r2, out of Residual-limitations into the §5
body with a one-line resolved pointer left behind); (b) "The opt-in" — `--allow-effects` also
waives the netns; (c) §3 verify row qualified to "the deterministic portion … excluded on both
sides" (added at r1 F3, an overstatement the r0 draft had claimed needed no change). Draft +
before/after: `docs/reviews/bl-049-contract-draft.md`. Reviews: r0/r1/r2 in `docs/reviews/`.

---

### BL-050 — `RunOverlayTest` races the worker handshake: overlay dirs are created *after* `ready` (#TBD)
**Status:** DONE
**Size:** S · **Priority:** medium-low · **Section:** Harness (aetheris/)

`run_overlay_test.exs:38` asserts `File.dir?(upper)` immediately after `Client.start_link`
returns. `start_link` returns as soon as the worker's `ready` handshake arrives
(`client.ex`, `init/1`), but the worker writes `ready` at `main.rs:71-74` and only *then*
runs `sandbox::mount_overlay` (`main.rs:79-94`), which is what creates `upper`/`work`/`merged`
(`sandbox.rs:242-244`). The test therefore synchronises on a handshake that does not cover
the side effect it asserts.

The test's own comment — "always created by the Rust worker before attempting the mount" — is
true and is not the issue: both the creation and the mount happen after `ready`.

**Latent since BL-042**, which moved namespace entry (and with it the `ready` write) ahead of
the rest of init so the handshake could carry `network_namespace`. The reorder was correct and
is not in question; this test was left synchronising on the old ordering.

**Load-dependent, which is why it reads as flaky.** It passes in isolation (3/3), passes
under `--trace` (`max_cases: 1`), and fails 5 times in 8 seeds when run after a module that
starts several workers in quick succession:

```
seed 1: 4 tests, 0 failures      seed 5: 4 tests, 0 failures
seed 2: 4 tests, 1 failure       seed 6: 4 tests, 1 failure
seed 3: 4 tests, 1 failure       seed 7: 4 tests, 1 failure
seed 4: 4 tests, 0 failures      seed 8: 4 tests, 1 failure
```

**Not caused by BL-049, demonstrated rather than asserted.** With BL-049's `lib/` changes
applied and its two new test files removed from the run, `mix test --include requires_worker`
produces a **byte-identical failing set** to the clean tree (907 tests, 14 failures, same
names). With the new test files present the set gains only this one entry (921 tests, 15
failures) — they add worker churn ahead of it, they do not change what it exercises.

**Done when:** the test waits for the condition it asserts rather than for `ready` — poll for
the directory with a deadline, or have the worker report overlay establishment in the
handshake the way BL-042 made it report `network_namespace`. The second is the better shape
and is the same argument BL-042 made: a worker that announces itself ready before its setup
exists leaves the BEAM no way to tell setup from its absence. Prefer it if the handshake is
being touched anyway; the poll is acceptable otherwise. Do **not** add a `Process.sleep`.

`Source: BL-049 done-check, off-territory, 2026-07-24. Mechanism read from main.rs/sandbox.rs
at 9d994fd; non-causation demonstrated by a three-way run (clean / lib-only / full).`

---


## Suggested order

### BL-099 — The sprint's D2 credential grep is AWS-only, so two providers' D2 posture is asserted rather than checked (#TBD)
**Status:** DONE
**Size:** S · **Priority:** medium · **Section:** aetheris-agents (`../aetheris/scripts/sprint.sh`)

Filed 2026-08-05, from m3-cloudcost t3 review r0 F1. The cloudcost sprint case greps the run
output for the live credential — the D2 trajectory half — inside
`if [[ "$CC_PROVIDER" == "aws" ]]` (`../aetheris/scripts/sprint.sh:2670`). So on the **Linode**
and **DigitalOcean** legs no assertion covers m3 §Done-when 7 (`CLOUDCOST_LINODE_TOKEN` appears in
neither stdout, stderr nor the trajectory), and the DO equivalent has never had one at all.

**A provider whose credential is never grepped has a D2 posture that is asserted rather than
checked.** A green Linode or DO sprint says nothing about credential leakage; it says the run
finished. That is the gap, and it is invisible because the leg is green either way.

**The fix is the same shape as the strip t2 already landed.** t2 extended `CC_HERMETIC` to Linode
by taking the strip list from `fetch_linode.SHADOWING_ENV` rather than hand-typing it, so the
prefix and the adapter cannot drift. The D2 grep wants the same treatment: select the credential
variable from `$CC_PROVIDER` and grep for *that*, keeping the existing gate on the searched file
demonstrably having content and a `run_id` — a grep over an empty file is the classic vacuous
pass, which is why the AWS arm already carries that guard.

**Add the control the AWS arm lacks.** t3 ran the Linode arm by hand with an explicit anti-vacuity
check — the same `grep -qF` against a file constructed to contain the token **does** find it — so
a clean result is the grep working rather than the grep being incapable of matching. Without it,
a credential whose shell-quoting or encoding differs from what `grep -qF` sees would report clean
forever. Land that control with the generalisation, not after it.

**Why it was not fixed in m3 t3.** `sprint.sh` is in §t2's Touches, not §t3's; t3 found it while
satisfying done-when 7 and could not edit the file. This is the second Linode-shaped defect in
that file found by a ticket that could not fix it — t1 found the wall-clock report filename and
t2 fixed it.

**Done when:** the credential grep runs on every provider leg against that provider's own
credential variable; the file-has-content-and-a-run_id gate is preserved; an anti-vacuity control
proves the grep can match; and the mutation posture is recorded (a run output seeded with the
credential must fail the assertion).

`Source: m3-cloudcost t3 §3.3, t3 review r0 F1 (2026-08-05).`

**DONE 2026-08-06 (m4 t3).** Every Done-when clause discharged.

- **The grep runs on every provider leg against that provider's own credential variable.** It sits
  outside any provider gate now. The names are **selected from the adapter that reads them** —
  `TOKEN_ENV` / `ACCESS_KEY_ENV` / `SECRET_KEY_ENV` / `SESSION_TOKEN_ENV`, the same treatment t2
  gave `CANONICAL_TYPES` — so a hand-typed copy cannot drift, and the grep, the survival arm and
  the poison control need no per-provider edit. (The bridge's provider→module map and the
  credential preflight `case` do still take an entry per provider; both fail loudly if missed.)
  Region constants are deliberately not selected: they are not secrets and their values
  legitimately appear in the report, so grepping for them would fire falsely.
- **The file-has-content-and-a-run_id gate is preserved**, per file.
- **An anti-vacuity control proves the grep can match.** The same matcher runs first against a
  file constructed to contain the credential and must find it, else `fail`. The file is
  `mktemp`-derived, mode `600`, and removed unconditionally by trap.
- **The mutation posture is recorded**: a run output seeded with the live credential produced
  `[FAIL] CLOUDCOST_DO_TOKEN appears in run.json — D2 violated`; a bait file built without the
  credential produced `[FAIL] D2 anti-vacuity FAILED …`. The seeded capture was located by content
  and deleted, and every other capture swept clean.
- **Decision 15 honoured:** the searched-file set is the array `CC_D2_FILES`, not an inline path,
  so covering `run.err` if the harness round splits the streams is one entry rather than a rewrite.

**Observed on the leg this row was filed about:** the DigitalOcean leg now prints
`[OK] no CLOUDCOST_DO_TOKEN in run.json (searched a file with content and a run_id)`. Before this
ticket that leg had no D2 assertion at all and was green either way — which is exactly the
asserted-rather-than-checked posture the row names.

`Source: m4 t3, 2026-08-06 — landed with BL-104 in one pass; the two interact.`

---

### BL-100 — the sprint's `--json` reads fail unpredictably; the status line prints a fallback token when they do (#TBD)
**Status:** DONE
**Size:** S–M · **Priority:** low-medium · **Section:** aetheris-agents (`../aetheris/scripts/sprint.sh`)

> **Rescoped and corrected 2026-08-06 (t1a).** Three changes, each recorded rather than silently
> applied. **(1) The causal claim below is false.** `2>&1` is not why the reads fail: the
> harness's **Logger output shares stdout with the payload**
> (`mix aetheris --json list --limit 1 2>/dev/null` emits both; `… 2>&1 >/dev/null` emits
> nothing), so the merge is irrelevant to parseability. Whether `[sandbox]` lines go to stdout or
> stderr is **not established** — that command spawns no worker. **(2) Stream splitting is not
> sufficient**: it cannot restore parseability in any environment where the harness emits Logger
> output on stdout, which is every capture in this repo from 2026-07 onward. Whether it sufficed
> earlier depends on `[sandbox]` routing, which is unestablished — *not* a claim that it could
> never have worked. **(3) The subject is not "broken reads" but reads whose success depends on
> ambient run-store state.** Identical expressions succeed or fail by environment — by store
> state, by harness version, and by whether a worker ran; see `claude-notes.md` for which line
> does which. News captures
> parse in 4 of 4, payslip fails in 8 of 8, cloudcost fails in 10 of 10 — same helper, same
> redirect. Non-determinism is the defect, and it is why fixing this makes the reads
> *deterministic* rather than "makes every read work". Size raised XS → S–M to match. The
> original text below is left intact **except where marked `[corrected 2026-08-06]`** — this is an
> open row, so the paragraphs someone would act on are corrected rather than merely annotated.

Filed 2026-08-05, from m3-cloudcost t3 review r0 F1. The cloudcost case's inline run redirects
`2>&1` into `run.json` (`../aetheris/scripts/sprint.sh:2571-2572`), so the harness's boot warnings
and the two `[sandbox]` lines are prepended to the `--json` document. `jq -r '.status // "unknown"'`
cannot parse the result and falls through its `||` to the literal `no-json`, which is what the
`[OK]` line prints:

```
[OK]    uc-cloudcost orchestrator → no-json (695 bytes)
```

The JSON payload is intact on the last line
(`{"label":"Cloudcost · Linode","status":"done","run_id":"cloudcost-orch-linode-h5lltQ"}`), and the
**assertion** is the surrounding `if` on exit status rather than the `jq`, so nothing is
mis-asserted and no check is vacuous. This is a display defect only.

**Its cost is a signal nobody will read when it finally matters.** A status field that reads
`no-json` on every run trains every reader to skip it, so the one run where the status is genuinely
interesting — `partial`, `error`, a status the exit code does not distinguish — reports it into a
line already classified as noise. That is the same reflex the standing gate rule names for a
known-red note that never changes.

**`[corrected 2026-08-06]` That justification is not achievable by this row alone.** The payload's
`status` can only ever read `done`: `handle_run_status/5`
(`../aetheris/lib/aetheris/cli/commands/run_helpers.ex`) returns `{:ok, %{… status: :done}}` for
`"done"` and `{:error, …}` for `"failed"`/`"cancelled"`, and the formatter's error branch
(`../aetheris/lib/aetheris/cli/output/formatter.ex`, `def print({:error, reason}, _mode)`) ignores
the output mode and emits no JSON at all. So `partial`/`error` never reach the line. Fixing this
row stops the display asserting something false and makes the read deterministic; recovering the
*signal* requires the sibling harness row on the `--json` failure contract.

**Provider-independent and pre-existing.** The redirect is not in any provider branch, so DO, AWS
and Linode are all affected, and have been since the case was written (m1 t5). m3 t3 surfaced it
rather than introducing it.

**`[corrected 2026-08-06]` Scope — the class, not the one line.** This row was filed against the
cloudcost case's status line. The same expression appears at four sites in `sprint.sh` — the `ok`-line reads inside
`run_agent()` (`:53`) and `run_orb()` (`:70`), the chaos case's gate extraction (`:297`), and the
cloudcost case's inline orchestrator line (`:2573`) — and the same root cause reaches eight further reads (`.run_id` ×6, `.orb_id`,
`extract_step_count`). **The chaos site is a gate, not a display line**: its operand feeds
`[[ "$status" == "done" ]]`, so when the read fails the assertion cannot match. Two sites already
carry ad-hoc `grep` workarounds (docbuilder, cloudcost) while their siblings do not. Enumerate the
class before fixing the first instance.

**`[corrected 2026-08-06]` The fix: payload extraction, and splitting is not an alternative.** The
original two-candidate framing below is superseded. Splitting the streams cannot restore
parseability while Logger output is on stdout, so it is not a viable branch — see the correction
block above. What works is a **backward scan for the last line that parses as a JSON object**,
which holds whatever is on either stream, whatever the store contains, and whether noise lands
before *or after* the payload. `tail -1` is **not** sufficient: three captured files carry worker
output after the payload (`sprint/2026052{1_202137,2_090058,2_095912}/payslip/run.json`). When no
line parses, print an explicit unknown — never a fabricated status; four captures have no payload
at all. A working implementation is in `../aetheris/docs/aetheris/claude-notes.md` §Claude Code —
sprint output parsing, verified against all four capture shapes.

*Original two-candidate text, superseded, kept as the record:* **Two candidate fixes, and the
choice is the whole ticket.** Either split the streams (`2>` to a sibling `run.err`, leaving
`run.json` parseable) — which changes what the D2 credential grep searches, so BL-099's
generalisation must then cover both files; or keep the merge and extract the payload (`tail -1`,
or the last line that parses), which is a one-line change that leaves every existing consumer's
file untouched. Do **not** do the first without re-reading BL-099: a credential-leak grep that
stops covering stderr is a strictly worse trade than a wrong status word.

**`[corrected 2026-08-06]` Done when:** the sprint's `--json` reads are **deterministic** — they
parse the payload regardless of ambient run-store state — at every site of the class, not only the
cloudcost status line; the chaos gate's operand is a real status rather than the fallback token;
a file with no payload prints an explicit unknown rather than a fabricated status; the streams stay
merged so the D2 credential grep continues to search everything the run wrote to both; and the
mutation posture is recorded against states that can actually occur (noise after the payload; no
payload at all) rather than against a non-success status, which the harness never writes into the
payload — see the sibling harness rows.

*Original done-when, superseded, kept as the record:* the sprint's orchestrator line prints the
run's real status, and whichever fix is chosen, the D2 credential grep demonstrably still searches
everything the run wrote to both streams.

**DONE 2026-08-06 (t1b).** Every Done-when clause discharged, each against evidence rather than
assertion:

- **One mechanism, every site.** `json_read <file> <jq-filter> [absent]` in
  `../aetheris/scripts/sprint.sh` scans the file's lines in reverse and takes the first that
  parses as a JSON object. **29 reads converted** across four previously-distinct mechanisms:
  **13** × `jq` over the file (incl. `run_agent`, `run_orb`, the chaos gate, the cloudcost inline
  line), **5** × `tail -1 | jq`, **7** × `grep -o '"run_id":"[^"]*"' | tail -1 | cut`, **4** × `jq`
  over a `--json` pipe (via the `json_read_cmd` wrapper, which captures the pipe to a temp file so
  the same scan applies). The workarounds that *worked* were folded in too — two mechanisms for one
  job is how the class regenerates. **13 sites excluded with reasons** (trajectory `--export`
  files, curl HTTP bodies, use-case script stdout, the eduloka sink gate → BL-108, the D2
  credential grep, `head -1` over `ls`).
  *(Count corrected at t1b review round 1 from a stated 19: three Group A sites — payslip, drive,
  email `.run_id` — were converted and verified but omitted from the census table, and the "19"
  itself rested on a bogus pairing step. 29 censused = 29 helper call sites, derived independently
  and matching; see the implementation notes.)*
- **Deterministic, on clean and noisy alike.** Per converted site, verified against the four
  capture shapes in `../aetheris/sprint/`: clean single line, noise *before* the payload, worker
  output *after* it, and no payload at all. **23 checks, 23 pass.** Expected values are pinned
  literals obtained independently of `json_read`, so the check cannot satisfy itself.
- **The chaos gate's operand is a real status.** Before: `[WARN] Chaos 1: status=no-json
  (investigate)`. After: `[OK] Chaos 1: agent exhausted max_steps → :done (expected)`. Both
  quoted from live runs — and the "before" is **the first chaos output ever captured in this
  repo**, so BL-107's "it has always warned" is now observation for at least one environment
  rather than inference. See BL-107.
- **A file with no payload prints an explicit unknown.** The token is `no-payload`, naming *the
  read* rather than the run. It cannot collide with a run status now (`handle_run_status/5` admits
  only `done`) nor with the statuses BL-106 would add. Sites feeding a `[[ -n … ]]` guard yield
  **empty** instead — a token there would push a garbage id into `mix aetheris inspect`.
- **The streams stay merged.** No change to any redirect, and none to the D2 credential grep,
  `CC_HERMETIC`, the poison-control arms or the orphan-count assertion. Live cloudcost leg
  confirms both D2 arms still run.
- **Mutation postures against states that occur in the record** — construct, observe, restore:
  non-JSON output *after* the payload (gate holds `OK`; the old `tail -1 | jq` yields `no-json` on
  the same file); no parseable payload at all (gate → `WARN status=no-payload`); and an
  anti-vacuity posture flipping the payload's `status` to `failed` (gate → `WARN status=failed`),
  which proves the repaired gate can still report red.

**The multiple-payload question, which this row's fix rested on, is settled — see BL-105's
sibling note and `../aetheris/docs/aetheris/claude-notes.md`.** One invocation *can* emit two
parsing JSON objects, for exactly one command (`fork`, per its own source comment at
`../aetheris/lib/aetheris/cli/commands/fork.ex:71`); it writes the early document first and the
result last, so recency still selects correctly, and `sprint.sh` never invokes `fork`. Of 319
captured files, zero carry more than one.

**Live evidence:** `./scripts/sprint.sh cloudcost` → `uc-cloudcost orchestrator → done (707 bytes)`
— the line that read `no-json` on every cloudcost run ever recorded. `./scripts/sprint.sh payslip`
→ `uc-payslip orchestrator → done (687 bytes)` (payslip parsed in 0 of 8 prior captures).

`Source: m3-cloudcost t3 §4, t3 review r0 F1 (2026-08-05).`
`Source (2026-08-06 corrections + rescope): t1a — census and evidence in
cloudcost/docs/t1a-implementation-notes.md; causal claim refuted by the stdout/stderr split
recorded there. Citations verified at aetheris@aaf0f9a / aetheris-agents@90c7c67.`
`Source (2026-08-06 close): t1b — census, per-site checks and postures in
cloudcost/docs/t1b-implementation-notes.md.`

---

### BL-101 — The report states tag coverage as a percentage and nothing else; surface the tags themselves (#TBD)
**Status:** DONE
**Size:** S–M · **Priority:** medium · **Section:** aetheris-agents (`cloudcost/scripts/compose_report_data.py`, `cloudcost/templates/report.html.j2`)

Filed 2026-08-05 from the m3-cloudcost close. The report's Tag coverage section renders one
ratio (`40.00 % (0.4) tagged — 6 of 15 usable resources carry at least one tag; 9 carry none`)
plus per-provider counts and top untagged spenders. It never names a single tag. An operator
who wants to tag critical infrastructure so it is protected, and throwaway infrastructure so it
is visible, cannot tell from the report which tags exist, what carries them, or what they cost.

**A third of this is already built and dropped on the floor.** `detect_orphans.py` emits a
`reported` block — the untagged-in-tagged-account governance rule, reported-only by §t2 design,
each entry carrying its own `evidence[]` — and `compose_report_data.orphan_section` carries
`candidates` only, so `report_data` has no key for it and the template cannot render it. The
rule fires in the pipeline and is invisible in its output. m1 closed with exactly this as an
open question ("decide whether the report carries the `reported` list — a scope question, not a
done-when gap"); this row is the answer.

**Scope — descriptive only.** No detection logic changes, no §Normalized extension: `tags` is
already first-class on every inventory resource, and `reported` already exists in the orphan
artifact. Three additions:
- carry `reported` through compose into `report_data`, and render it as its own section;
- a **tags-in-use** table: each distinct tag, the resources carrying it, and their summed
  `monthly_cost_estimate`, ordered by cost. Apply the existing `top_k` convention and report
  the cap applied — a long tail of one-off tags is the expected shape and a silent truncation
  reads as "these are all the tags";
- show each resource's `tags` on the rows the report already renders (top untagged spenders,
  orphan candidates — candidates already carry `tags` in their identity fields, so this is a
  template change alone).

**Keep the orphan section and the tag section apart, deliberately.** m1 ruled that `keep=true`
resources stay invisible because "those are resources the operator asked to keep, and
suppressing them is the intent." That ruling is about the orphan *queue* and is preserved: an
excluded resource is still not a candidate. Showing it in the **tag** section — as a resource
carrying a keep tag, with its cost — is a different statement and does not reverse the ruling.
Do not merge the two sections into one "governance" block; that reversal, if ever wanted, is
its own decision.

**Not in scope, and gated.** Grouping by tag *key* is not a cross-provider concept: AWS tags are
key/value flattened to `k=v` by its adapter, DO and Linode tags are flat strings where `k=v` is
a human convention nothing enforces. A key-grouped view would be honest on AWS and inferred
elsewhere — the provider-vocabulary seam class **BL-074** exists for, and which already names
`KEEP_TAG`'s spelling as an adapter convention masquerading as a shared constant. Tags *driving*
detection (a `lifecycle=temp` tag raising confidence or creating candidates) is a change to the
shared engine and a milestone of its own, gated on BL-074 landing first. This row is the
descriptive layer that makes either worth building.

**Sequence with BL-070.** Both edit `compose_report_data.py`, which has been byte-unchanged
since m1 and whose stillness was the negative proof for two milestones. Doing them together is
one review of that file instead of two — the BL-078 trigger shape (do it the next time someone
is legitimately in the file).

**Note on content.** Tags can carry owner emails, project codenames and ticket ids. The report
is a local self-contained HTML file, so this is not a new exposure, but a tag table makes the
strings prominent where the percentage did not. Worth a line in the runbook when this lands
rather than a guard in the code.

**Done when:** the report names the tags in use with their resource counts and summed
estimates, applying and reporting a `top_k`; the `reported` governance list reaches
`report_data` and renders with its evidence; each rendered resource row shows its tags; a
`keep=true` resource appears in the tag section and still appears nowhere in the orphan section;
and the tag figures reconcile with the existing coverage ratio, asserted in a test.

`Source: m3-cloudcost close, 2026-08-05 (human request, from reading the live Linode report);
resolves m1-cloudcost §Open items' `reported`-list question.`


**DONE 2026-08-07 (m4 t5b).** Every Done-when clause satisfied; assessed per clause.

| Clause | Satisfied by |
|---|---|
| *the report names the tags in use with their resource counts and summed estimates, applying and reporting a `top_k`* | `coverage_section` emits `tags_in_use` / `tags_in_use_total` / `tags_not_shown`; the template renders a **Tags in use** table and states its cap in **both** states. `test_the_tag_table_reports_its_own_cap_in_both_states`, `test_the_tags_in_use_table_renders_with_its_tags` |
| *the `reported` governance list reaches `report_data` and renders with its evidence* | `orphan_section` carries `reported` through with `evidence[]` intact; the template renders it as its own sub-section. `test_the_governance_reported_block_reaches_report_data_with_its_evidence` |
| *each rendered resource row shows its tags* | spender rows carry `tags` (key always present, `[]` when none) and render chips or an explicit em dash. `test_untagged_spender_rows_carry_their_tags_and_the_key_is_always_present`, `test_untagged_spender_rows_render_their_tags_or_an_explicit_dash` |
| *a `keep=true` resource appears in the tag section and still appears nowhere in the orphan section* | `test_a_reported_resource_never_appears_in_the_orphan_section`; the m1 ruling is preserved, not reversed, and `test_a_reported_entry_is_never_banded_as_a_candidate` pins that a reported entry carries no `confidence` and no `monthly_saving_estimate` |
| *the tag figures reconcile with the existing coverage ratio, asserted in a test* | `test_tags_in_use_reconciles_with_the_coverage_ratio`, with `test_the_reconciliation_check_fails_against_a_deliberately_broken_fixture` as its anti-vacuity control |

**One finding worth carrying.** The governance rule **has never fired on any committed fixture** —
`inventory_rules_positive` is at 16.67 % coverage and `inventory_soc_2026-07` at 25 %, both below
the 50 % threshold, so `account_uses_tags` is False on every fixture in the repo. Asserting the
fired state required constructing an inventory over the threshold. The unfired state is what the
live DO report renders, and it now says **"Not evaluated … the rule did not run. This is not a
finding of 'no untagged resources'."** — which is the rider's shape, arrived at because this row
could not be implemented honestly without it.

`Source: m3-cloudcost close, 2026-08-05; implemented m4 t5b, 2026-08-07.`

---

### BL-104 — sprint.sh's hermetic prefix is a denylist; invert it to an allowlist (#TBD)
**Status:** DONE
**Size:** S · **Priority:** medium · **Section:** harness (`scripts/sprint.sh`)

Filed from the m3-cloudcost close. The `CC_HERMETIC=(env -u …)` array in the cloudcost case
(`../aetheris/scripts/sprint.sh`, verified at `aetheris@082b37c:2383-2386`)
neutralises **named** variables: `env -u AWS_ACCESS_KEY_ID -u AWS_SECRET_ACCESS_KEY
-u AWS_PROFILE`, plus `AWS_SHARED_CREDENTIALS_FILE=/dev/null`, plus (m3 t2) `-u LINODE_CLI_TOKEN
-u LINODE_TOKEN`. Every one of those is a name someone thought of. **A denylist cannot cover the
name nobody thought of**, and the list grows by one entry per provider forever.

**The live instance.** During m3 t1's preflight a 64-character credential-shaped variable named
`LINODE_BILLING` was found in the session environment — read by no Linode library, present in no
denylist, and surviving three separate cleanup passes (`~/.profile`, the systemd user-manager's
imported block, and a `gnome-terminal-server` process that snapshotted it at launch). Had it been
an active credential for the account under test, the hermetic proof would have reported green
while the run inherited it. The three-carrier finding is recorded in `aetheris/CLAUDE.md`
(Adjacent-case, *the class is not only code*).

**Fix direction — default-deny.** `env -i` with an explicit passthrough list rather than `-u` per
hazard. Establishing that list empirically is the whole risk of the ticket: `PATH`, `HOME`, the
`CLOUDCOST_*` keys the selected provider actually needs, and whatever the mix/BEAM invocation
genuinely requires (`MIX_ENV`, `ERL_*`, locale, possibly `ANTHROPIC_API_KEY`). Build it by
starting from nothing and adding only what the run demonstrably fails without, recording why each
entry is on it — a passthrough list assembled by guessing is the denylist problem wearing the
other hat.

**What the inversion buys beyond coverage.** The poison-control block — the `CC_POISON` /
`CC_PROBE` arms (i)–(iii), and their Linode siblings `CC_LINODE_POISON` / `CC_LINODE_PROBE`
(verified at `082b37c:2480-2560`) — then proves a *structural* property rather than an
enumerated one, and its per-provider arms collapse: with `env -i` there is nothing
provider-specific to unset, so the AWS arm's `[[ "$CC_PROVIDER" == "aws" ]]` gate **inside the
poison-control block** (verified at `082b37c:2512`) — the same test also guards the region
assertions (`:2651`) and the D2 credential grep (`:2671`), and this row means only the first —
disappears rather than being duplicated per provider. Adding provider four stops touching this
file at all.

**Sequence with BL-099 and BL-100 — all three edit the same block, and two of them interact.**
BL-099 generalises the D2 credential grep past AWS; this row changes what reaches the child at
all, so arm (iii) — *the credential the adapter reads survives the strip* — must hold for every
provider under the new passthrough list, or the run cannot authenticate. BL-100's stream-splitting
option changes what the grep searches. One pass over the cloudcost sprint case beats three, and
the interaction is only visible when they are read together.

**The standing-rule form of this is deliberately held.** *Environment isolation wants an
allowlist, not a denylist* is true and generalises past `sprint.sh` to any hermetic prefix or
container invocation, but it is one instance and its full argument is already here, where someone
acting on it will be standing. Filing it as a `CLAUDE.md` rule now puts one argument in two files.
Trigger for promoting it: a second denylist-shaped isolation found anywhere else — at which point
it promotes on the normal ≥2 bar with two citations.

**Done when:** `CC_HERMETIC` passes an explicit allowlist rather than unsetting names; the
poison-control block proves a non-allowlisted variable does not reach the child **without naming
it**; the AWS, DO and Linode legs all pass unchanged in behaviour; each passthrough entry is
recorded with the reason it is there; and the mutation posture is shown — a variable added to the
ambient environment and not to the list must not appear in the child.

`Source: m3-cloudcost t1 preflight, 2026-08-05 — LINODE_BILLING found in the session environment
under a name no denylist carried.`

`Citations verified at aetheris@082b37c. Anchors name the construct; the line numbers are
parentheticals against that commit, so a later insert makes them checkable rather than
silently wrong — the fix the m3 promotion prescribes, applied to a row that had already
drifted three times before it was filed.`

**DONE 2026-08-06 (m4 t3).** Every Done-when clause discharged.

- **`CC_HERMETIC` passes an explicit allowlist rather than unsetting names.** It is no longer an
  `env` array at all: `env -i NAME=value` would have put the credential in **argv**, readable from
  `/proc`, which breaks D2 in the ticket that hardens D2. It is now a `cc_hermetic` function that
  unsets every exported name not on the list inside a subshell and `exec`s — no value is re-typed,
  copied, or placed in an argv.
- **The poison control proves a non-allowlisted variable does not reach the child without naming
  it.** Arm (i) asserts the child's *entire* key set is a subset of the list — it names no hazard,
  so it covers `LINODE_BILLING`, `AWS_REGION` and DO's shadow names (none of which the denylist
  carried) by construction. The permitted shell-injected extras (`LC_CTYPE`/`PWD`/`SHLVL`/`_`) are
  derived from `env -i`, **not** from the mechanism under test — deriving them from `cc_hermetic`
  would let a leaking prefix excuse its own leak.
- **Each passthrough entry is recorded with the reason it is there**, and every reason is an
  observed failure: `PATH` (exit 127), `HOME` (`could not find the user home`), `LANG` (silent
  latin1 corruption of the payload — `c2 b7` becomes a bare `b7`), `ANTHROPIC_API_KEY` (run
  `failed` at step 0), `CLOUDCOST_OPTIMIZATION` (another component's fail-fast guard silently
  stops firing), plus the adapter-selected credential and knob names. Full transcripts in
  `cloudcost/docs/m4-t3-implementation-notes.md` §2.
- **The mutation posture is shown** — probe allowlisted → arm (ii) fails as a declared tautology;
  credential not allowlisted → survival arm fails. Both constructed, observed, reverted.
- **The per-provider arms collapsed as this row predicted.** Six arms across two blocks became
  three; adding provider four touches none of it.
- **Legs:** digitalocean run in full (16 `[OK]`, 0 `[FAIL]`). AWS and Linode **not runnable — the
  credentials are not present in this environment, and none was minted or probed to make them so.**
  Their adapter env surface, guard raises and knob behaviour were verified without a run; this row
  is closed on that basis and the limit is stated rather than papered over.

**Two things this row did not anticipate, both found by doing it:**

1. **`env -i` removes `AWS_SHARED_CREDENTIALS_FILE`, and absent is not `/dev/null`.** Absent
   restores boto3's default `~/.aws/credentials` lookup, and `HOME` is on the allowlist, so the
   file is reachable. A naive inversion would have re-opened the exact arm the denylist closed.
   It is kept as an explicit assignment.
2. **Default-deny strips the Linode endpoint-redirect names, which the denylist deliberately let
   through** so the adapter could *warn* about them. The hazard is now neutralised instead of
   reported. The signal is restored as a parent-side `warn` before the strip, using the adapter's
   own `ENDPOINT_REDIRECT_ENV`/`SHADOWING_ENV` constants — names only, no values read.

`Source: m4 t3, 2026-08-06 — landed with BL-099 in one pass, per this row's own sequencing note.`

---

### BL-105 — `--json` mode's payload shares stdout with the harness's Logger output (#TBD)
**Status:** DONE
**Size:** S · **Priority:** medium · **Section:** harness (`../aetheris/lib/aetheris/cli/`)

Filed 2026-08-06 from t1a. `mix aetheris --json <cmd>` writes its payload to stdout via
`IO.puts(Jason.encode!(data))` (`../aetheris/lib/aetheris/cli/output/formatter.ex:47`), and the
application's Logger writes to the **same stream** — the console backend is unconfigured for a
device (`../aetheris/config/runtime.exs:3` sets only `level: :info`). Demonstrated rather than
inferred:

```
$ mix aetheris --json list --limit 1 2>/dev/null        # stdout only
07:51:25.434 [warning] [Aetheris.Application] failed to resume run bl031-paused-demo-2658: …
07:51:25.436 [info]    [Aetheris.Scheduler] started run run_5S_eBQ for schedule 'news-sprint-…'
07:51:25.460 [info]    [Aetheris.Application] orphan sweep: %{errors: 0, …}
{"entries":[{"id":"run_5S_eBQ","label":"","status":"running","type":"run","started_at":"…"}]}

$ mix aetheris --json list --limit 1 2>&1 >/dev/null    # stderr only
(nothing)
```

**Claim scope, deliberately narrow:** the *Logger* output shares stdout. Whether `[sandbox]` lines
go to stdout or stderr is **not established** — the command above spawns no worker, and this row
does not need it.

**The consequence is non-determinism, not universal breakage.** Identical expressions succeed or
fail by environment. **The mechanism is not single, and only part of it is established:** the
resume-failure lines *are* store-state dependent, but the orphan-sweep line is not — it logs with
every counter at zero and is gated on `config :aetheris, :sweep_on_start`
(`../aetheris/config/config.exs`), and it did not exist before 2026-07-15 (`0188a90`, BL-003), so
its absence from the May captures is a version boundary. Do not attribute a file's failure to one
cause without checking which lines it carries. Across the captures in `../aetheris/sprint/`: news parses in 4 of 4, payslip fails in
8 of 8, cloudcost fails in 10 of 10 — same helper, same redirect. A clean single-line capture
exists from 2026-05-21, written *after* the resume-failure Logger line already existed in the code
(`application.ex`, added 2026-05-20), which is what establishes the dependence on store state
rather than on code age. So fixing this makes the sprint's reads **deterministic**; it does not
"make every read work", because some already do — that is the defect.

**A shipped product surface parses this output.** Rig's fork command builds `--json` argv and scans
stdout line by line for a parsing JSON object
(`rig/src-tauri/src/commands/fork.rs`, `fork_argv/3` at `:117`, `run_id_from_line/1` at `:140`,
`read_first_run_id/1` at `:155`). Its own comment already records the correct diagnosis — *"`mix`
compile and log noise shares stdout and does not parse as JSON"* — written 2026-07-26, ten days
before BL-100 was filed with the wrong one. Any fix must keep that consumer working.

**Reach, stated precisely — this does NOT on its own fix every sprint read.** Fixing the Logger
contaminant addresses the reads that fail *because of it*, which is the 2026-07-onward captures.
It does **not** cover a second contaminant: three captures carry
`aetheris_worker fatal: Broken pipe (os error 32)` lines *after* the payload, emitted by
`eprintln!` in the worker's entry point (`../aetheris/native/aetheris_worker/src/main.rs`, the
fatal-exit arm) — i.e. on **stderr**, which the sprint's `2>&1` merge carries into the file
regardless of what this row changes. So a `tail -1`-style read stays wrong after this lands, and
the sprint still needs its own backward-scan fix. That is why BL-100 and this row are separate,
and why neither obviates the other. See BL-100.

**With both streams now established, the solution space is fully determined — and the two fixes
are complementary, not alternative.** Logger is on stdout; worker output is on stderr:

| | `run.json` contains | parseable? |
|---|---|---|
| Split streams only | stdout, still carrying Logger output | no |
| This row only (Logger off stdout), streams merged | worker stderr via `2>&1` | **not reliably** — unparseable whenever the worker emits, not unconditionally |
| **Both** | the payload alone | **yes, no scan needed** |

Row 2 is what refutes "at a stroke"; row 1 is why the arbiter's payload-extraction choice was
right. **The combination has a cost this repo already knows: splitting is exactly what BL-099's D2
credential grep must then cover across two files** — BL-099's row records that a credential-leak
grep which stops covering stderr is a strictly worse trade than a wrong status word. So anything
that pairs this row with a split must land BL-099's generalisation with it, not after. The
backward scan remains correct under all three worlds, so t1b's design is unaffected either way.

**Constructibility note on the mutation posture below.** It asks for a run whose store emits boot
output and one whose store does not. `config :aetheris, :sweep_on_start` defaults to **true**
(`../aetheris/config/config.exs`), so the orphan-sweep line is emitted regardless of store
contents — the second run cannot be produced by arranging the store alone and requires toggling
that config (or the equivalent of `config/test.exs`, which sets it false). Whoever picks this up
should plan for that rather than discover it mid-ticket.

**Done when:** the `--json` payload is separable from log output by a consumer that does not have
to know what the noise looks like — either the payload moves to a stream the Logger does not share,
or the contract states that consumers must scan for the last parsing JSON object and every in-repo
consumer does so; Rig's fork path is verified unbroken either way; and the mutation posture is
recorded against a run whose store emits boot output and one whose store does not.

**DONE 2026-08-09 (hc-c).** Closed with BL-106 as one contract. The arm taken is the first of
the Done-when's two — *the payload moves to a stream the Logger does not share* — implemented by
moving **Logger**, not the payload: stdout is the payload stream, stderr the diagnostic stream.
Moving the payload instead would have broken Rig, which reads stdout.

Applied on the boot path (`Aetheris.Application.route_logging_to_stderr/0`), not in
`config/runtime.exs`, because config does not reach the entry points that matter: `mix aetheris`
never runs `app.start`, so the *running* handler keeps writing to stdout however the file is set,
and an escript never evaluates `runtime.exs`. Found by capture — the handler's config and its
actual destination disagreed under `mix aetheris`, which is why the fix is not a config line.
`:logger.update_handler_config/3` cannot do it either (`:illegal_config_change` on a live
`logger_std_h`); the handler is removed and re-installed, and only when it is still the stock
stdout one, so a file handler or an operator's own destination is never overwritten.

**Mutation posture, both store conditions the row names.** Noisy store (default env,
`sweep_on_start: true`, two resumable checkpoints): stdout = **1** line, parses; stderr = 3 lines.
Quiet store (`MIX_ENV=test` — `sweep_on_start: false`, `:memory:` db, the toggle this row's
constructibility note anticipated): stdout = **1** line, parses; stderr = **0** lines. The broken
state was observed on this same tree before the fix: the row's own demonstration command emitted
**4** non-blank stdout lines, 3 of which did not parse.

**The third arm hc-a proposed — suppress boot logging on the boot path — was considered and not
taken.** It removes only the boot lines; any log line emitted during a run still lands on the
payload stream, so it does not deliver *"separable by a consumer that does not have to know what
the noise looks like"*, and it costs observability to boot.

**Reach, unchanged and restated honestly:** `mix` compile noise is a different emitter and still
goes to stdout on a run that recompiles. The Done-when is about Logger, and Logger is what moved.

**The change is wider than this row, so its consumers were swept (hc-c r1, F1).** Moving Logger
affects **every** invocation and every mode, not only `--json`, so "no `--json` reader broke" is
not the question. **Population:** every file in both repos with an executable extension
(`.sh .py .rs .ts .tsx .exs .ex`, excluding `node_modules`, `target`, `_build`, `deps`, `priv`,
`.git`) containing a harness invocation — **39 files**, of which **5** actually spawn the harness
and read a stream. **0 of the 5 read log text from stdout**; the enumeration and each site's
reading behaviour are in `docs/milestones/hc-c-implementation-notes.md` §7. **The sweep is clean,
not exhaustive** — it cannot reach an operator's own pipeline or anything outside these two repos,
and that residue is recorded in `docs/milestones/hc-consolidation.md` §Not established item 6
rather than left to read as completeness.

`Source: t1a, 2026-08-06 — established by the stdout/stderr split above; BL-100's `2>&1` diagnosis
corrected in the same round. Citations verified at aetheris@aaf0f9a / aetheris-agents@90c7c67.`

---

### BL-106 — `--json` emits no JSON document on a non-success run (#TBD)
**Status:** DONE
**Size:** S · **Priority:** medium · **Section:** harness (`../aetheris/lib/aetheris/cli/`)

Filed 2026-08-06 from t1a. **Sibling of BL-105 — one contract, two mechanisms.** BL-105 is why the
sprint's reads are unreliable; this row is why a programmatic consumer gets nothing on exactly the
runs it most needs to read.

The formatter's error branch ignores the output mode entirely
(`../aetheris/lib/aetheris/cli/output/formatter.ex:56`):

```elixir
  def print({:error, reason}, _mode) do
    IO.puts(:stderr, "Error: #{reason}")
    1
  end
```

`_mode` is unused, so `--json` and `--human` behave identically on the error path. And every
non-success terminal state routes there: `handle_run_status/5`
(`../aetheris/lib/aetheris/cli/commands/run_helpers.ex:112`) returns `{:ok, %{… status: :done}}`
for `"done"` but `{:error, …}` for `"failed"` and `"cancelled"`; `await_run/2`'s declared success
shape is `status: :done` and nothing else; `await_orb/1`
(`../aetheris/lib/aetheris/cli/commands/run.ex:121`) turns `%{status: :failed}` into `{:error, …}`
at `:126`. Confirmed in the record: all ten captured cloudcost payloads read `status: "done"`, and
a failed payslip run emitted `Error: run payslip-orch-cAdfJQ failed` with no JSON line at all
(`../aetheris/sprint/20260521_191506/payslip/run.json`).

**Product-facing, but not an outage — the known consumer compensates.** Rig does not look for JSON
on the failure path; it collects stderr on a separate thread and renders that prose
(`rig/src-tauri/src/commands/fork.rs`, `stderr_collector` at `:88`/`:108`, `start_failure_error/1`).
That works, and it means a UI error string is derived from human-readable wording rather than from
a machine contract — brittle to rewording, not broken today.

**This is the row BL-100's justification was actually describing.** BL-100 argued the fix would
restore a signal for *"`partial`, `error`, a status the exit code does not distinguish"*. Those
statuses never reach the payload, so BL-100 cannot deliver them; this row is where that becomes
achievable.

**Done when:** `--json` emits a JSON document on every terminal outcome, success or not, carrying
the run id and a real status; the human path is unchanged; Rig's fork error path is migrated or
verified still correct; and the mutation posture is recorded — a genuinely failing run must produce
parseable output naming the failure.

**DONE 2026-08-09 (hc-c).** Closed with BL-105 as one contract. `Formatter.print({:error, …}, :json)`
now emits a document on stdout beside the unchanged prose on stderr, and the terminal run outcomes
carry a structured detail so the document can name the run: `handle_run_status/5`'s `failed` and
`cancelled` branches and `Run.await_orb/1`'s failed branch return
`%{run_id | orb_id, status, error}` instead of a bare string. A failure that is *not* a run outcome
stays a string and renders `{"status":"error","error":"…"}` with **no `run_id`** — there is no run
to name, and that absence is load-bearing (see the Rig note below). The human path, the stderr
prose and the exit code are unchanged.

**Mutation posture: a genuinely failing run, observed.** `mix aetheris --json run
agents/ollama_smoke.exs` against an Ollama that cannot load the model emitted
`{"error":"run ollama-9EuU5w failed","status":"failed","run_id":"ollama-9EuU5w"}` on stdout. The
broken state was observed on the same tree minutes earlier: the same failing run emitted **no JSON
at all**. Three unit tests were added and mutation-checked — with the `:json` error clause removed,
the two payload-asserting tests fail and the human-path test correctly stays green.

**Rig's fork error path is verified still correct, not migrated** — the option this row's Done-when
allows. `read_first_run_id` returns the *first* stdout line with a string `run_id`, and the
fork-start line is written before `await_fork/1` is called (`fork.ex`, `run_with_step/4`), so an
error document carrying the same `run_id` can only follow it. A fork that never starts yields a
bare-string error, hence no `run_id` key, hence `None` and the stderr path — exercised live
(`--step` with no matching `step_complete` → `{"error":"failed to build fork config:
:step_not_found","status":"error"}` on stdout, prose on stderr). Rig's own 7 tests pass unchanged,
including `read_first_run_id_none_on_eof_without_a_run_id`, which already pinned `{"status":"error"}`
as a no-`run_id` line. The starts-then-fails case is covered by the harness's own
`fork_test.exs` test of that name.

**Not taken here: BL-112.** Its row says the UTF-8 choice "belongs with BL-105/BL-106". It is a
different defect (latin1 fallback corrupting payload bytes) and outside hc-c's scope, which is
these two rows' Done-whens and no `--json` schema beyond them. Left filed.

**The exit code is still 0 on a failed `mix aetheris` run** — `Mix.Tasks.Aetheris.run/1` discards
`Aetheris.CLI.run/1`'s code. That is **BL-044**, R3's question for hc-d, and is deliberately not
touched here. It is also why a real status word in the payload is worth having.

`Source: t1a, 2026-08-06. Citations verified at aetheris@aaf0f9a / aetheris-agents@90c7c67.`

---

### BL-107 — the chaos-case gate has never evaluated its subject (#TBD)
**Status:** DONE
**Size:** XS–S · **Priority:** medium · **Section:** harness (`../aetheris/scripts/sprint.sh`)

Filed 2026-08-06 from t1a, per the gate rule — *a red gate gets a tracked ticket the day it's
found*. This is that ticket. **Repair is scheduled, not started:** it is expected to fall out of
BL-100's sprint work (t1b), which has not run. **If that sequence changes, this gate is carried
red with this row named**, per the tracked-carry clause — never relaxed, re-pointed or downgraded
to get a clean run.

`../aetheris/scripts/sprint.sh:296-299`:

```bash
  run_aetheris --json run /tmp/aetheris_chaos_maxsteps.exs > "$OUT_DIR/chaos/maxsteps.json" 2>&1 || true
  status=$(jq -r '.status // "unknown"' "$OUT_DIR/chaos/maxsteps.json" 2>/dev/null || echo "no-json")
  [[ "$status" == "done" ]] && ok "Chaos 1: agent exhausted max_steps → :done (expected)" \
                             || warn "Chaos 1: status=$status (investigate)"
```

Unlike the other three `.status` sites — `run_agent()` (`:53`), `run_orb()` (`:70`) and the
cloudcost case's inline `ok` line (`:2573`) — which interpolate into an `ok` line, **this one is a
gate** — the extracted value is the operand of an equality test. When the
read fails, `status` is the literal `no-json`, the test cannot match, and the case emits
`warn "Chaos 1: status=no-json (investigate)"`.

**Both claims below are qualified, because neither is a bare observation.** The operand is the
fallback token **in every environment emitting harness boot output** — not unconditionally, since
BL-105 establishes that some environments produce a clean, parseable file. And the frequency claim
is **inference, not observation**: no chaos output has ever been captured in this repo
(`find ../aetheris/sprint -path '*chaos*'` returns nothing), so "it has always warned" is derived
from the extraction's behaviour rather than seen. The premise — that every chaos run to date ran in
a noisy-store environment — is unexamined.

**Chaos runs only under specific sprint targets** — the chaos case's opening
`if [[ "$TARGET" == "chaos" || "$TARGET" == "all" ]]` guard (`:277`) — not on every sprint
invocation.

Nothing other than the warn line consumes the result: `grep -n '\$status'` over the file returns
exactly four reads — the `ok` lines inside `run_agent()` (`:54`) and `run_orb()` (`:71`), both
where `status` is `local`, and the chaos gate's own test and warn (`:298`, `:299`) — and
`maxsteps.json` is read only by the chaos gate's own extraction (`:297`). The chaos `status` is a
global but is never read after its warn line. `warn` sets no exit status (BL-077), so no exit path changes.

**Done when:** the gate's operand is a real status rather than a fallback token; the assertion's
outcome is recorded before and after, so the change from `warn` to whatever it becomes is visible
and adjudicated rather than silent; and if it then reports a genuine failure, that gets its own row
rather than being absorbed. **No claim is made here about what it will report after repair** — it
has never evaluated, so that is unknown.

**DONE 2026-08-06 (t1b). The gate now evaluates, and it passes.** Repair landed with BL-100's
single extraction mechanism, as this row anticipated, so the carried-red branch was not exercised.

| | Assertion outcome, quoted from the run |
|---|---|
| **Before** (`sprint/20260806_172144`, pre-edit tree at agents `c5b63ae` / harness `f6fbd82`) | `[WARN]  Chaos 1: status=no-json (investigate)` |
| **After** (`sprint/20260806_172825`, post-edit) | `[OK]    Chaos 1: agent exhausted max_steps → :done (expected)` |

The gate line itself is byte-unchanged apart from the extraction: the comparison
`[[ "$status" == "done" ]]`, the `ok` text and the `warn` text are all as they were. **Nothing was
relaxed, re-pointed or downgraded** — the operand changed from a fallback token to the payload's
real `status`, and that is the whole edit.

**Two claims this row qualified are now resolved by observation rather than inference.** The row
noted that "it has always warned" was derived from the extraction's behaviour, because
`find ../aetheris/sprint -path '*chaos*'` returned nothing. The before-run above **is** the first
chaos capture in this repo, and it warned — so the claim is now observed for at least this
environment. Its file (`sprint/20260806_172144/chaos/maxsteps.json`, 9 lines) carries two
`failed to resume run` warnings, an orphan-sweep line and two `[sandbox]` lines ahead of an intact
payload: the noisy-store shape the row's premise assumed, confirmed rather than presumed. Whether a
chaos run in a *clean*-store environment would have parsed remains open — that premise is still
unexamined, and is left in `cloudcost/m4-consolidation.md` §Not established.

**No new row is owed by this gate.** It reported no genuine failure. (A separate, unrelated red
*was* found off-territory during t1b's live runs and is filed as **BL-110**.)

`Source: t1a, 2026-08-06. Citations verified at aetheris@aaf0f9a.`
`Source (2026-08-06 close): t1b — before/after runs and the mutation postures in
cloudcost/docs/t1b-implementation-notes.md.`

---

### BL-121 — the untagged-spenders cap truncates across all providers and reports nothing (#TBD)
**Status:** DONE
**Kind:** defect · **Census item:** P2 · **Contract:** C11
**Size:** XS · **Priority:** low–medium · **Section:** cloudcost (`cloudcost/scripts/compose_report_data.py`)

Filed 2026-08-07 from m4 t4c. **Established from the code.**

`coverage_section` sorts untagged resources by estimate **across all providers combined** and then
truncates to `top_untagged` (`compose_report_data.py:388–408`). At N>1 a provider whose resources
are individually cheap can be **absent from the table entirely** while another fills every row —
and nothing in the payload records that anything was dropped.

**The same file argues against exactly this, one section away.** `region_coverage_section`'s
rationale (`:521–534`) invokes decision D's no-silent-caps clause: *"a sweep narrowed by an override
or by a failed region enumeration is visible rather than quietly shrinking the inventory behind an
unchanged-looking report."* The spenders cap is that shape, unguarded.

**Owes:** the dropped count in the payload — how many untagged resources exist beyond `top_k`, and
ideally the per-provider breakdown, so an absent provider is visible as absent rather than as
having nothing to report.
**Costs:** XS. Additive to the payload; the template may render it or not.
**Collides with:** BL-101, which redesigns the tag section (adds a tags-in-use table and carries the
`reported` block through). Same section, same file — take together or sequence.

**Annotated 2026-08-07 (m4 t5b).** **The cap-truncation gap is fixed** — `untagged_not_shown` and
`tags_not_shown` now travel in the payload and render in both states, and the fix does **not**
depend on BL-131. **The row's stated consequence does.** *"A provider can be absent from the table
entirely"* requires the N>1 compose path, whose support BL-131 decides; at N=1 the same cap drops
rows without dropping a provider. **Not re-characterised here** — doing so now would pre-empt
BL-131's ruling.

`Source: m4 t4a census item P2; ruled schema-level at m4 t4b under C11. Read at agents 611feba.`


**DONE 2026-08-07 (m4 t5b).** `untagged_not_shown` travels in the payload and the template states
the truncation in both states — *"N further untagged resource(s) are not shown"* and *"Every
untagged resource is shown; the cap of N dropped none."* Zero is emitted explicitly rather than
omitted, so *nothing dropped* and *nobody counted* are different renderings (absent-is-unknown).
The same treatment was given to the new tag table, which BL-101's own text required.
`test_the_cap_reports_what_it_dropped_in_both_states`,
`test_the_spenders_cap_states_what_it_dropped_in_both_states`.

**The row's stated consequence is not closed by this** — see the annotation above: *"a provider can
be absent from the table entirely"* needs the N>1 path, which BL-131 decides. The cap-truncation
gap itself was real at any N and is fixed.

**Framing resolved 2026-08-10 (m5 t2) — and with it the row closes.** **m5-D2**
(`cloudcost/m5-n1-compose.md` §Ratified decisions) rules the N>1 compose surface **retained as a
library-and-CLI capability the pipeline does not invoke**. So this row's stated consequence —
*"a provider can be absent from the table entirely while another fills every row"* — is
**true of the surface and unreachable from the pipeline**: every orchestrator run composes one
bundle, and at one bundle the cap drops rows without dropping a provider. It is not withdrawn and
not re-characterised as a defect; it is **correctly stated and source-only**, which is the third
reading this row could not choose between while BL-131 was open.

Nothing further is owed. The **fix** landed at m4 t5b and never depended on the ruling; the
**framing** was the whole of what waited, and it is settled here. C11 carries the same declaration
in `cloudcost/milestone.md` §Contracts, where a reader meets it.

`Source: m5-D2, ratified 2026-08-10; framing applied at m5 t2, 2026-08-10.`

---

### BL-127 — C6: a non-`str` tag element is a counted skip, not a silent drop (#TBD)
**Status:** DONE
**Kind:** contract consequence · **Census item:** N7 · **Contract:** C6
**Size:** S · **Priority:** low–medium · **Section:** cloudcost (`cloudcost/scripts/_normalized.py`)

Filed 2026-08-07 from m4 t4c. **Nothing is broken today** — all three adapters emit `list[str]` by
construction.

**C6 requires:** a non-`str` tag element is a **counted skip**, surfaced the way `usable_resources`
surfaces a malformed resource.

**The code today:** `tags_of` filters non-`str` elements out silently (`_normalized.py:112`,
`[t for t in tags if isinstance(t, str)]`) — no warning, no `skipped` entry. An adapter emitting the
wrong element type would have every tag vanish, taking `tag_coverage` to `0.0` and switching off the
untagged-in-tagged-account governance rule. **A clean-looking zero**, which is the failure shape this
contract set exists to name.

**Costs:** S. `tags_of` currently returns a list and has no skip sink, so it needs one — which means
touching both callers (`has_keep_tag`, `tag_coverage`) and `coverage_section` in compose.
**Collides with:** BL-121 and BL-101 both edit the tag-coverage path.

`Source: §Contracts C6 at m4 t4b, marked [code consequence]; census item N7. Code claim **read**
(not inherited) at agents 1779368: `_normalized.py:112`, `return [t for t in tags if isinstance(t,
str)] if isinstance(tags, list) else []`.`


**DONE 2026-08-07 (m4 t5b).** `tags_of` takes an optional skip sink; a non-`str` element is
recorded with its `resource_id`, index and type rather than silently filtered.
`test_a_non_string_tag_element_is_counted_not_silently_dropped` asserts both states — a clean
inventory records no tag skip, a broken one records exactly two with their reasons.

**The sink is opt-in per caller, and that is the row's real content.** The sprint's rule-legibility
arm reads `orphans["skipped"]`, fires `illegible` on **any** entry, and separately asserts
`evaluated + len(skipped) == len(resources)`. A tag-element skip is neither a whole resource nor an
unreadable one, so routing it there would have failed the sprint **from another repo**.
`detect_orphans` therefore passes no sink and is byte-identical to its pre-BL-127 behaviour;
`compose_report_data` passes its own report-data sink, which nothing in the sprint reads.
`test_the_tag_skip_sink_never_reaches_the_orphan_artifacts_skipped_list` pins the constraint so it
cannot regress silently.

---

### BL-131 — decide whether the N>1 compose path is a supported surface (#TBD)
**Status:** DONE
**Kind:** decision · **Census items:** n/a (surfaced by the m4 t5b gate) · **Contract:** C4, C11
**Size:** S to decide, M–L to implement either way · **Priority:** medium
**Section:** cloudcost (`cloudcost/scripts/compose_report_data.py`, `cloudcost/milestone.md`)

Filed 2026-08-07 from m4 t5b's G2 gate-stop. **This row exists because three documents describe
the same code three different ways and no decision record settles it.**

**The three states, and each is asserted somewhere.**

| State | Asserted by | Reading |
|---|---|---|
| **dead** | **BL-070** — *"decision H … makes the N-merge … unreachable"* | delete it |
| **live at the first fan-out** | `cloudcost/milestone.md` §Open items — *"latent while m1 is DO-only single-currency; **live at the first fan-out**"* | fix it before provider four |
| **advertised but uninvoked** | established at m4 t5b (below) | decide whether to support it |

**The reachability derivation** (m4 t5b G7, at agents `6832159`): the N>1 path is reachable only
through `--input-dir` → `discover_bundles`. The orchestrator
(`cloudcost/agents/cloudcost_orchestrator.exs:258, 263`) passes **exactly one**
`--cost`/`--inventory`/`--orphans` triple, and `--input-dir` appears in neither the orchestrator,
`../aetheris/scripts/sprint.sh`, nor `cloudcost/runbook.md`. **But it is declared in
`cloudcost/tools.json` (`args[3]`) with a worked example** — *"`--input-dir output/aws
--output-dir output/aws --history-dir history/aws`"* — so it is a documented tool interface, not a
stray flag. Note the example points at **one** provider's directory: even the advertised use is
N=1. **So N>1 is an emergent capability of a supported interface that nothing advertises, tests or
invokes** — and those are two separable questions this row must not conflate.

**Resolving this requires amending §Contracts either way.** C4's currency paragraph ratifies the
one-currency-scalar policy as *"correct, and m1's stated position"* and states its blast radius as
*"blanks the report's headline number for **every provider**"*; C11's P2 paragraph describes the
spenders cap as applied *"after a global sort **across all providers**"*. **Both describe
cross-provider behaviour that only exists because the N-merge exists.** Whichever way this goes,
those two paragraphs change — kept and justified, or rewritten as superseded by decision H.

**The knock-ons resolve with it, not before it:**

- **BL-121**'s stated consequence (*"a provider can be absent from the table entirely"*) is
  reachable only on this surface. The cap-truncation gap itself is real at any N and was fixed at
  m4 t5b; only the framing waits.
- **BL-119**'s subject is `discover_bundles`, which is this surface.
- **BL-070**'s remaining deletion targets are all premised on this being dead.

**Owes:** a ruling — supported, or removed — and the §Contracts amendment that follows it.
**Costs:** the decision is cheap; either implementation is M–L, because "supported" means tests and
a sprint leg for N>1 and "removed" means deleting a declared tool interface and its manifest entry.
**Collides with:** BL-070, BL-119, BL-121's framing, C4, C11.

**It blocks nothing in m4 and it blocks provider four.** Sequence: **after the harness
consolidation round, before provider four** — the first fan-out is exactly when the wrong answer
starts costing.

**Scoped 2026-08-09 into `cloudcost/m5-n1-compose.md`** — a two-ticket round
with a gate stop: t1 establishes read-only and stops, the reviewer rules, t2
applies the ruling and amends §Contracts. Both tickets' §6 anatomy is authored
there before either opens, per hc-consolidation R12. **This row is not amended
by that scoping** — it states the same question it stated when filed, and the
round is where the answer will be.

`Source: m4 t5b G2 gate-stop and G7, 2026-08-07. Reachability derived at agents 6832159; the
orchestrator, sprint, runbook and tools.json all read at that commit.`

---

### BL-131 — DONE 2026-08-10 (m5 t2) — closed on the ruling: **retained and bounded**

The row asked for *"a ruling — supported, or removed — and the §Contracts amendment that follows
it."* Both have landed. **m5-D2** (`cloudcost/m5-n1-compose.md` §Ratified decisions), ratified
2026-08-10 at the m5 gate stop, rules the surface **neither supported nor removed but retained and
declared**: *"It is a library-and-CLI capability the pipeline does not invoke, and it is declared
as such."*

**The three states this row could not choose between are all answered, and none was the answer.**
Not **dead** — m5 t1's **E1** found three routes reaching N>1, not the one this row derived, and
the route-bearing code byte-unchanged since `6832159`, so the derivation was incomplete rather
than overtaken. Not **live at the first fan-out** — decision H makes provider four a fourth solo
run, so nothing about a fourth provider brings the path into the pipeline, and the urgency this
row borrowed from the first fan-out was borrowed from an event H forecloses. **Advertised but
uninvoked** is what holds, and it is a state that needed declaring rather than resolving.

**Its own framing, corrected where t1 falsified it.** This row's reachability derivation states
*"the N>1 path is reachable only through `--input-dir` → `discover_bundles`"*. **E1** established
that `bundles_from_args` reaches N>1 with no `--input-dir` at all, the three flags being
`action="append"`. The row's **conclusion** — that no orchestrator invocation reaches N>1 — is
unaffected and was confirmed at HEAD by this ticket's step-1 gate; only its route count was wrong.
Recorded here rather than silently inherited, because a later reader citing this row would
otherwise carry the one-route claim forward.

**What landed, and where a reader meets it** — m5-D2's four declaration requirements, all
discharged at m5 t2: §Contracts **C4** and **C11** in `cloudcost/milestone.md` each carry a
*Source-only by ruling* paragraph and each one's m4 t5b pointer block is discharged in place;
`cloudcost/scripts/compose_report_data.py`'s module docstring states the pipeline invokes it at one
bundle, with no executable line changed; `cloudcost/runbook.md`'s now-unreachable sentence is
corrected to reachable-and-uninvoked; and the rows that resolve with this one carry their
dispositions — **BL-070** not taken, **BL-121** framing resolved, **BL-132** keeping its census
with two instances answered, **BL-119** open and now unambiguously in scope.

`Source: BL-131 filed 2026-08-07 from m4 t5b's G2 gate-stop; scoped 2026-08-09 into
cloudcost/m5-n1-compose.md; established read-only at m5 t1 (E1–E8); ruled as m5-D2 2026-08-10 at
the gate stop per R12; applied at m5 t2, 2026-08-10.`

---

### BL-132 — establish, per contract, whether the behaviour it states is reachable from the live pipeline (#TBD)
**Status:** DONE
**Kind:** method · **Census items:** n/a (surfaced by the m4 t5b gate) · **Contract:** all of C1–C15
**Size:** S · **Priority:** medium · **Section:** cloudcost (`cloudcost/milestone.md` §Contracts)

Filed 2026-08-07 from m4 t5b's G2 gate-stop. **The method finding, which is the row:**

> **The m4 t4a census swept *code*. §Contracts at t4b stated that code as *contract*. Neither step
> established *reachability*.**

So §Contracts can state — accurately, as a description of the source — behaviour that no live
invocation can produce. **C4 and C11 are the two known instances**: both describe cross-provider
behaviour, and the cross-provider path is reachable only through a CLI flag the orchestrator never
passes (BL-131). Neither contract is *false*; each describes the source correctly. The gap is that
a reader — including the reviewer who wrote the ruling that m4 t5b's gate stopped — can cite a
contract as authority without knowing whether it describes a path anything takes.

**Two is not a census.** That is this row's whole point, and it is the same lesson BL-074 was filed
for: *"the one seam"* was an observation. Two contract instances found by accident, through a
collision map, are an observation too.

**The method, which is cheap and bounded — and the row states it so the work is not mis-scoped:**

- **The entry point is `cloudcost/agents/cloudcost_orchestrator.exs`.** Everything the pipeline
  runs, it runs from there. Anything reachable only through a CLI flag the orchestrator never
  passes is **source-only**.
- For each contract C1–C15, ask one question: *is the behaviour this states produced by any
  invocation the orchestrator makes?* Answer **reachable**, **source-only**, or **untested** —
  and where source-only, say whether the contract should be kept, qualified, or superseded.

**This is a reachability check, not decision-record archaeology.** It does not ask what any
milestone decided or when; it asks what the current entry point can produce. Scoped as archaeology
it becomes a multi-day read of five milestone documents, which is not what it is for and not what
it costs.

**Owes:** the per-contract table, and a qualifying sentence in each contract found source-only.
**Costs:** S. Fifteen contracts, one question each, one entry point.
**Collides with:** BL-131, which decides the two known instances. **Take BL-131 first** — otherwise
this row re-derives its answer and then has to change it.

**Annotated 2026-08-09.** BL-131 is scoped in `cloudcost/m5-n1-compose.md`. This
row's *"Take BL-131 first"* clause is unchanged; the round to take first now has
a document.

**Annotated 2026-08-10 (m5 t2). This row stays open, and its census is not run here.** BL-131 has
been taken first, as this row required: **m5-D2** rules the N>1 surface retained and declared, and
m5 t2 amended **C4** and **C11** accordingly. **The two known instances are answered, so the census
need not re-derive them** — each now carries a *Source-only by ruling* paragraph naming m5-D2, and
each one's m4 t5b pointer block is discharged in place. Start from **C1**; C4 and C11 are done and
their answer is **source-only**, with the qualifying sentence this row asks for already written.

**What is unchanged is the row's whole point.** Two contract instances found by accident are still
not a census, and the remaining thirteen are still unexamined. m5 t2 deliberately did **no**
reachability work over C1–C15 — its ticket forbids it (*"no reachability work over C1–C15 (BL-132's
row)"*) — precisely so that this row's method runs once, over the full set, rather than being
half-done as a side effect of another ticket.

**Annotated 2026-08-10 (m5 t2), marked as such 2026-08-11.** The paragraph below landed at
`305b3a1`, in the same commit as the annotation block above it, and until now carried no opening
marker — so it read as text filed 2026-08-07. Its wording is unchanged.

**One thing m5 t1 supplies that this row's method should use.** BL-132 names the entry point as
`cloudcost/agents/cloudcost_orchestrator.exs` and asks one question per contract. m5 t1's **E1**
showed that *"reachable only through a CLI flag the orchestrator never passes"* undercounted the
routes to the same surface by two. The method survives — the question is still *is this produced by
any invocation the orchestrator makes?* — but the answer for a source-only contract should
**enumerate the routes it is reachable by**, not just assert the orchestrator misses one.

**Taken 2026-08-11. Anatomy and method refinements, authored by the reviewer before the row
is worked, per R12.**

**Shape — light, and one part of it is new.** Taken directly as a backlog row: one
implementation-notes file, no round document, no review file — the shape **BL-084**,
**BL-085** and **BL-096** were taken in. **Those three carried no anatomy at all**, so the
`Touches` and `Done-check` below are an addition to that shape rather than a relocation of
§6's fields into it. They are added because both earned their place in m5: a scoping a
ticket may not exceed, and a completion condition a ticket cannot declare for itself.

**Touches.**

- `cloudcost/milestone.md` — **§Contracts only**: a reachability sentence in each contract
  found source-only, and nothing else. **C4 and C11 are neither re-derived nor re-edited** —
  m5 t2 answered both, and each already carries its qualifying paragraph.
- `docs/backlog-2026-06.md` — **this row only**.
- `cloudcost/docs/bl-132-implementation-notes.md` *(new)*.

Nothing else. Any other path that changes is a deviation and is named in the notes.

**Do not generate.** No change to any executable line. **No amendment to any contract's
guarantee** — only to what it claims about reachability. No new contract, no renumbering, no
edit to a contract's `Closed arm` rulings. **No decision-record archaeology**: this row
forbids it in its own text, and the population is the source at HEAD, not five milestone
documents.

**Done-check.**

```bash
# 1. The offline spine, unchanged — this row changes no executable line. Re-resolve both
#    anchors at HEAD before running: cloudcost/runbook.md §Offline tests for the command,
#    CLAUDE.md §Commands for the root. A differing count is a finding, not a pass.
python3 -m pytest cloudcost/tests/ -v

# 2. The census covers its population. Print §Contracts' identifier enumeration beside the
#    table's rows and show they match. A table with a row missing is not a census, and a
#    count without its enumeration is not an answer.

# 3. Every contract found source-only carries its sentence in the file, read back from the
#    file rather than from the packet.
grep -n 'BL-132' cloudcost/milestone.md

# 4. Nothing outside Touches changed.
git status --short
```

**Method — three refinements on what this row already states.**

1. **Execution before reading.** The two STEP 3 arg forms are the entry point and they can
   be *run* — over recorded fixtures, with those exact forms, capturing the payload and the
   rendered report. A contract is then checked against **what came out**, not against source
   read for what it implies. Where a contract's subject sits upstream of compose, say so and
   check it differently; do not stretch one instrument across the whole set. m5 t1 settled in
   one run what three documents had disagreed about.
2. **Three contracts state reachability about themselves — those are claims to check, not
   answers to inherit.** C3 names a wall-clock fallback unreachable on all three adapters;
   C8 says a modifier never fired against any real inventory; C12 says its own guarantee does
   not hold. BL-131's entire cost was a reachability claim taken on a document's word.
3. **C13 has no reachability question.** It states field ownership and a prohibition, not
   behaviour an invocation produces. Record it **not applicable**, with that reason, rather
   than forcing a verdict onto it.

**Population, refined.** Fifteen contracts; **C4 and C11** answered at m5 t2; **C13** not
applicable. **Twelve to answer** — verify that split against §Contracts at HEAD before
relying on it.

**Findings threshold, in force for this row.** A finding earns its own action only if it has
already cost something pointable — a session that derived it, a ruling that rested on it, a
check that passed for the wrong reason. **A gap argued from structure alone is recorded in
the notes and swept once at the end, not acted on.** A gap argued from structure is a
prediction; a gap with a session that paid for it is a finding.

`Anatomy authored 2026-08-11 by the reviewer, before the row is worked, per R12. Shape ruled
light by the human on the BL-084 / BL-085 / BL-096 precedent — row taken directly, one
implementation-notes file, no round document, no review file. Those three carried no anatomy at
all, so Touches and Done-check are new fields here rather than §6 fields relocated into the
light shape. This block attributes to this date and not to the row's Source line below.`

`Source: m4 t5b G2 gate-stop, 2026-08-07 — the finding that C4 ratified an m1 position decision H
had already superseded, and that no step between the census and the contract checked reachability.`

---

### BL-132 — DONE 2026-08-11 — the census ran over all fifteen; **both `Owes:` items discharged**

**The row's own `Owes:` is the checklist, and both are discharged.** *"The per-contract table"* —
in `cloudcost/docs/bl-132-implementation-notes.md` §2, fifteen rows, each with its verdict and what
the verdict rests on. *"A qualifying sentence in each contract found source-only"* — **nine**
landed in `cloudcost/milestone.md` §Contracts, one closing each of **C1, C2, C3, C6, C8, C9, C10,
C12** and **C14**, each tagged `Reachability (BL-132, 2026-08-11)` so the set is greppable from the
file rather than from a packet.

**The distribution.** Fifteen contracts. **Two** answered before this row ran and not re-derived —
**C4** and **C11**, source-only by **m5-D2**. **One** not applicable: **C13** states field
ownership and a keying prohibition, not behaviour an invocation produces, so it was recorded with
that reason rather than given a verdict forced onto it. **Twelve** answered here, and none of the
twelve was source-only *whole*: every one holds a guarantee the pipeline exercises beside a clause
describing something no invocation reaches. **Three** — **C5**, **C7**, **C15** — are reachable
entire and took no sentence.

**The population was derived, not inherited.** `grep -c '^### C[0-9]' cloudcost/milestone.md` → 15,
contiguous C1–C15, no gap and no duplicate, measured at `8845d85`. The anatomy's *twelve to answer*
is confirmed; it was checked rather than relied on, which the anatomy required.

**Method — the entry point was run, not read.** Both STEP 3 arg forms in
`cloudcost/agents/cloudcost_orchestrator.exs` were executed over recorded artifacts, with STEP 2
before and STEP 4 after, and contracts were checked against the payload and the rendered report.
**The result that could not have come from reading**: **C2**'s X1 clause says the ~fifteen raw
provider state strings *"reach the rendered report verbatim"* via evidence text — at HEAD both
interpolation sites are gated on `STOPPED_STATES`, so only the canonical value can, and the
composed payload carries no `state` field at all. Measured over three chains of the orchestrator's
own STEP 3 forms across recorded DO and Linode artifacts — DO at both arg forms and Linode at the
first: **zero** `"state"` across **all three composed payloads and all three rendered reports**,
against a control of **18** in the DO inventory those chains consumed.

> **`[corrected 2026-08-11 (the row-correction round). The measurement is stated over six artifacts
> and one named inventory, not two artifacts and an unnamed one — taken from the corrected sibling,
> not re-derived.]`**
>
> **It read:** *"Zero in either payload and either rendered report, against **18** in the inventory
> those runs consumed."*
>
> **Both clauses failed, and in opposite directions — which is why this is a replacement and not a
> narrowing.** *"Either"* is two; the exercise sweep at `8f36e45` re-measured all **six** artifacts
> of the three chains and every one is zero, so the row **understated** the population its result
> rests on. *"The inventory those runs consumed"* is the clause that is **over-broad**: those chains
> consumed **two** inventories with different counts — **18** DO and **15** Linode
> (`cloudcost/milestone.md` §C6's basis figures) — so one control attributed to *the* inventory
> conflates them, which is the same defect `8f36e45` corrected in C3 one file over. The replacement
> is the text `cloudcost/milestone.md:391–394` carries at HEAD, quoted rather than re-derived.
>
> **The verdict is unchanged**, and so is every other claim in this paragraph — the `STOPPED_STATES`
> gating, the absent `state` field, and the finding that this result could not have come from
> reading. Corrected here because `8f36e45` touched `cloudcost/milestone.md` **only**, leaving this
> row as the sibling that still carried the superseded wording — the gap **BL-140**'s `Source:`
> block names, below in this file. The second such site,
> `cloudcost/docs/bl-132-implementation-notes.md` §2's C2 basis cell, is corrected in the same
> commit as this and was **not** named in that note. The round's record is
> `cloudcost/docs/bl-132-row-correction-implementation-notes.md`.

**The three self-reporting contracts were treated as subject, not input**, per the anatomy's
method refinement 2 — **C3**'s unreachable wall-clock fallback, **C8**'s never-fired activity
modifier, **C12**'s own report that its guarantee does not hold. **All three hold under check**,
each established by a different instrument. Had one been false the ticket was to stop and relay;
none was.

**One finding, and it is filed rather than carried here: `BL-138`.** C8's D21 clause enumerates the
declared parameter block wrongly — it emits five keys, one of which the clause excludes. It was
**declined on scope**: this row's subject is reachability and D21's defect is accuracy, and D21's
operative claim — the block is write-only — is confirmed and unaffected. Filed as its own row
rather than left as prose, because prose owns nothing.

`Source: BL-132 filed 2026-08-07 from m4 t5b's G2 gate-stop; annotated 2026-08-09 and 2026-08-10
(m5 t2); anatomy authored into this row 2026-08-11 by the reviewer per R12; census run and closed
2026-08-11. Record: cloudcost/docs/bl-132-implementation-notes.md.`

---

### BL-152 — the repo-root `pytest` invocation cannot collect (#TBD)
**Status:** DONE
**Kind:** gate · **Census items:** n/a · **Contract:** `CLAUDE.md` (agents) §Definition of done — *every existing gate runs at ticket boundaries, even off-territory*
**Size:** S · **Priority:** medium — **CLOSED 2026-08-16**
**Section:** test apparatus (agents)

Filed 2026-08-13 at m6 t2b, **the day it was found**, by a ticket whose own done-check is the
repo-root whole-suite command. Off-territory: t2b touches neither module below.

**What is red.** `cd ~/sandbox/elixirws/aetheris-agents && python3 -m pytest -q` aborts during
collection:

```
ERROR boxy-pipeline/tests/test_pipeline.py               ModuleNotFoundError: No module named 'main'
ERROR provenance/mcp/corpus-search/tests/test_server.py  ModuleNotFoundError: No module named 'tests.test_server'
!!!!!!!!!!!!!!!!!!! Interrupted: 2 errors during collection !!!!!!!!!!!!!!!!!!!!
```

Collection is *interrupted*, so **no test runs at all** — the command is not "mostly green with
two errors", it is a command that executes nothing.

**Not introduced by t2b.** Reproduced with t2b's changes stashed, at agents `0303597`.

**Not broken product code.** Both modules import and their tests run when pytest is invoked
against their own scope. This is a rootdir / `sys.path` collection defect — the repo has no
`pytest.ini`, `setup.cfg` or `pyproject.toml`, so rootdir and `sys.path` are inferred per
invocation, and each use case's `conftest.py` inserts its own `scripts/` only.

**The two named modules are the visible edge of it, not the extent.** Scopes that collect
cleanly alone fail when *combined*, which means the defect is not "two broken files":

```
python3 -m pytest cloudcost/tests/ -q --collect-only    → 440 tests collected
python3 -m pytest tests/          -q --collect-only    → 136 tests collected
python3 -m pytest cloudcost/tests/ tests/ -q --collect-only
                                                        → 136 collected, 8 errors, Interrupted
```

So no single invocation covers even two scopes at once. Any fix must be verified by collecting
the whole tree, not by making the two named modules import.

**And collection is only the first obstacle.** With the two uncollectable modules `--ignore`d, the
tree run reaches `boxy-pipeline` and blocks inside a live subprocess —
`boxy-pipeline/scripts/plan_extractor.py` against two sample PDFs — still running at 8m42s with no
output, and killed rather than waited out. So even a collection fix would leave the root command
running live extraction work on every invocation. Whatever replaces it has to decide what the
whole-suite gate *excludes*, not only what it can import; the `@pytest.mark.integration`
convention already used elsewhere in the repo is the obvious lever and is not applied here.

**Why it matters more than it looks.** Ticket done-checks are written as *the whole suite, not
`<use_case>/tests/`* precisely when a change touches a root-level test — t2b's W3 is that case.
A done-check whose literal command collects nothing cannot distinguish a green repo from a broken
one, which is the **Silent-wrong-answer** class in the apparatus rather than the product. Sessions
have been running scoped invocations and reporting whole-suite-shaped numbers (m6 t1's *"386
passed"* is not reproducible from the root command), so the divergence has been invisible in both
directions.

**When it went red is unknown**, and nothing was watching in either direction — the same
invisibility the standing gate rule exists to prevent.

**Done when:** `python3 -m pytest -q` from the repo root collects every test module and its result
is a real pass/fail over the whole suite — or the root-level invocation is declared not to be the
gate, in one named document, with the gate that replaces it stated and the done-check wording in
`CLAUDE.md` corrected to match. **Not** when the two modules are individually skipped.

**Costs:** S. Likely one `pytest.ini`/`conftest.py` at the root fixing rootdir and `sys.path`;
the risk is that pinning rootdir changes how every use case's existing `conftest.py` resolves, so
it needs the whole suite run before and after rather than the two modules alone.

`Source: m6 t2b, 2026-08-13. Found by running the ticket's own stage-1 done-check command
verbatim, then reproduced with the ticket's changes stashed to establish it was inherited. Filed
rather than left in the packet, per the standing rule that prose in a packet or notes files
nothing.`

**Annotated 2026-08-16 (BL-152's own ticket): the gate exists and is green; the row is NOT
closed.** Established at agents `6ffcd76` / harness `d19f4b6`; record at
`docs/milestones/bl-152-implementation-notes.md`.

**The gate is now** `python3 -m pytest -q -m "not integration and not dormant"`, run from the
`aetheris-agents/` repo root, stated as that command — not as an outcome — in `CLAUDE.md`
§Definition of done, which also extends the standing gate enumeration to include it.
`1384 passed, 3 skipped, 320 deselected, 7 xfailed in 178.56s`, exit 0.

**Two exclusions, two markers, never merged, and the gate prints both counts** on its own summary
line: `deselected by reason: integration=112, dormant=208 (total 320)`. `integration` asserts
*test mechanics* — the test depends on state outside this repo's tracked tree. `dormant` asserts
*business state* — boxy-pipeline's work is paused pending its client, dated, with the condition
for return recorded in `pytest.ini` (*it runs again when boxy-pipeline work resumes*). Dormant
tests **still collect and still import**; 208 of them, deselected at run time and never at import,
because a use case whose tests stop collecting is the very rot this row exists to remove. Each set
has its own command, so an exclusion is a deferral rather than a deletion:
`python3 -m pytest -q -m "integration and not dormant"` and `python3 -m pytest -q -m dormant`.
Neither marker is in `addopts`. Dormancy was applied to the test apparatus and nothing else — no
sprint case, tools manifest, runbook or capability list was touched, and no boxy code, fixture or
output was moved.

**What fixed collection.** A root `pytest.ini` — pinning rootdir, and
`addopts = --import-mode=importlib` — plus one `sys.path.insert` in
`boxy-pipeline/tests/conftest.py` and the deletion of the empty `email/tests/__init__.py`. Not
`--ignore`, not `skip`, not `xfail`, and no product code. The row's *"two named modules are the
visible edge, not the extent"* is confirmed: three distinct module-name collisions under pytest's
default `prepend` import mode, only one of which either named module shows —
`tests/conftest.py` vs `cloudcost/tests/conftest.py` both claiming `conftest` (the row's 8
errors); `email/tests/` vs `provenance/mcp/corpus-search/tests/` both claiming the package
`tests`; and `boxy-pipeline/main.py` reachable only when the working directory *is*
`boxy-pipeline/`, because `python3 -m` puts the cwd on `sys.path` and nothing else did.

**The true whole-suite figure is 1714 collected, zero collection errors**, equal to the sum of all
twelve per-scope collections, and the gate accounts for every one of them (1384 + 3 + 7 + 320).
Only one scope's count moved — `boxy-pipeline/tests` 196+error → 208, the twelve tests in
`test_pipeline.py` that could not previously be imported from the root — so the *Costs*
paragraph's stated risk did not materialise. It reconciles with **no** figure previously recorded
here, and should not: every *"full suite"* number in the notes — m6 t1's **386 passed** included —
is printed beside `python3 -m pytest cloudcost/tests/`, a scope figure that was never a
root-command figure. That scope runs 464 passed today. Neither number is adjusted.

**Ten tests gained `@pytest.mark.integration`** — three in
`boxy-pipeline/tests/test_plan_extractor.py` reading gitignored client PDFs (four siblings with
the identical guard were already marked; these three were the inconsistency), seven in
`provenance/tests/` spawning `mix run --eval` in the sibling `../aetheris`. **None was red**:
the pre-marker tree run was 1545 passed / 0 failed and the post-marker run 1535, and 1545 − 1535
is exactly the ten. **Where this ticket exercised judgement the row did not settle**: the line
between those seven and the many tests that `subprocess.run` this repo's *own* tracked scripts is
drawn at *leaves this repository*, and is the packet's question for the arbiter.

**Reds found, reported, not fixed.**
`boxy-pipeline/tests/test_catalog_resolver_refactor.py::test_real_jsonl_resolve_matches_excel_result`
**FAILED** and is left red inside the dormant set — deselected for dormancy, never for failing. A
second failure in the same set is **unidentified**: the verbose run was cap-killed before reaching
it, and it is not named by inference. Separately, the ticket introduced and then removed a red of
its own: a root `conftest.py` shadowed the bare module name `conftest` that ten cloudcost lines
import at runtime, breaking two tests; the hooks moved to `tests/conftest.py`. That fragility
remains latent and is offered as a candidate row rather than fixed here.

**Every run that can reach live subprocess work ran under an explicit wall-clock cap, and a
cap-kill is recorded as a result.** `-m "integration and not dormant"` completes in 25.27s. The
dormant set is documented and **deliberately not run**: two capped runs made before the split were
killed at 52m21s (cap 2700s, 37/169) and 10m17s (cap 2400s, 21/57), the first stalled at
`test_plan_path_produces_same_output_as_drawings_path` — which spawns `plan_extractor.py` against
the two sample PDFs, exactly as the row describes. **The row's "blocks inside a live subprocess"
is confirmed, not refuted**; projected from the observed rate that set needs roughly four hours,
and it is now behind a marker nothing runs by default.

**Two of the row's other pointers were wrong at HEAD**, corrected in the notes rather than here:
the scope counts have moved (`cloudcost/tests/` 440 → 465, `tests/` 136 → 164, the 8-error
combination result exact); and *"their tests run when pytest is invoked against their own scope"*
is false for `boxy-pipeline/tests` from the repo root, which is the mechanism rather than a
detail.

**The harness needs no change; its HEAD is unchanged at `d19f4b6`.** `sprint.sh`'s
`python3 -m pytest ../aetheris-agents/api/{tenant,gateway}/tests/ -q` legs now find this
`pytest.ini` by upward search and are unaffected — 108 passed, 11 skipped, the same 119 collected
as before. Every scoped invocation in every runbook, README and milestone doc in both repos
collects identically before and after, verified scope by scope in both the root-relative and
cwd-relative forms, so none of them was edited.

`[CLOSED 2026-08-16 by the arbiter, on the BL-152 packet and its amendment —
agents 2868a3e and ace771c, both public. Closed on the row's FIRST branch: the
root invocation collects the whole tree and yields a real result. With one
qualification the row's own text demanded — the gate EXCLUDES tests, by two
separately named markers, each carrying its own command, with both counts printed
on every run that deselects anything. The row anticipated this in its "collection
is only the first obstacle" paragraph. The exclusion policy is part of what closed
it, not an escape from it.

WHAT THE CLOSURE CLAIMS. The root command collects every test module with zero
collection errors and its result is a real pass/fail over the set it runs.
CLAUDE.md names the COMMAND rather than an outcome, so that sentence stays true on
a day the suite is red. The per-scope census reconciles with the whole-tree total
in both root-relative and cwd-relative forms, so no scope silently lost tests to
the rootdir pin — which was this row's own stated Costs risk, and it did not
materialise.

WHAT IT DOES NOT CLAIM, recorded so no later reader mistakes a green gate for a
trustworthy suite. The gate deselects tests on marks that are registered but not
audited against the criterion the gate now uses (BL-158). The dormant set does not
terminate usefully, holds one named red left deliberately red, and holds at least
one further failure nobody has identified (BL-159). The bare name `conftest`
remains a trap held open by an absence that nothing checks (BL-157). The gate
reports truthfully about the population it runs; it certifies nothing about the
population it does not.

RULING 1 FIRED, IN A DIRECTION THE TICKET DID NOT PREDICT. The failures the fix
exposed were not in the gate's population but in the dormant one. The ticket also
introduced a red of its own — a root conftest.py breaking ten runtime
`from conftest import …` sites — and recorded it against itself after two runs had
reported a green gate that was not green. The positive control caught it. That is
the first occasion in this project on which a control paid for itself inside the
ticket that built it.

TWO OF THIS ROW'S OWN CLAIMS RESOLVED. "Both modules import and their tests run
when pytest is invoked against their own scope" was FALSE for boxy-pipeline, which
collects only with cwd set to its own directory. And m6 t1's "386 passed" was
never a root-command figure and was never presented as one — the mismatch was
between the number and the phrase "full suite" standing beside it, not between two
measurements. "When it went red is unknown" remains unknown, and is now moot.

THE ARBITER'S `integration` CRITERION WAS WRONG AS FIRST WRITTEN and was corrected
by the implementing session. Phrased as "would it pass in a fresh clone", it
exempted every test that guards itself with a skip — which was all ten it had just
been written to justify. The shipped criterion counts a silent skip. Recorded
because the defect was in the ruling, not in the work.]`

`[2026-08-16, appended after the closure. The earlier annotation in this row
stating that the row is NOT closed was TRUE WHEN WRITTEN — it recorded the
implementing session's correct refusal to close its own row — and is SUPERSEDED
by the closure above. It is left standing because dated annotations in this file
record what was believed at a date and are not rewritten. The row's status is the
`CLOSED` marker on its Size/Priority line.]`

---

### BL-163 — `bl-002`'s post-upload checks state check 1 and check 3 without the namespace boundary (#TBD)
**Status:** DONE
**Kind:** defect · **Census items:** n/a · **Contract:** `docs/backlog-2026-06.md` BL-143, the `[Ruled 2026-08-16 …]` annotation
**Size:** S · **Priority:** medium — **CLOSED 2026-08-18**
**Section:** process / project knowledge (`prompts/bl-002-refresh-project-knowledge.md`)

Filed 2026-08-16 at BL-143's close, in the round that deferred it. Established at agents `84c24c7`.
**This row is the deferral's executor.**

**What is stale.** `prompts/bl-002-refresh-project-knowledge.md` §Post-upload verification (`:139`)
states the two checks in the form BL-143's ruling supersedes. Check 1 (`:150–152`): *"The store's
document set equals the manifest's export-name column exactly — set comparison in both directions,
not a count. A name in one and not the other is the finding."* Check 3 (`:156–162`) covers a
document predating the upload window and offers *"either it is a deliberate non-manifest document
(agent-written docs land under `claude/`), in which case the manifest should say such documents may
coexist and are out of scope, or the upload was incremental."* Neither is scoped to a namespace, so
check 1 reads a `claude/` document as a finding while check 3 reads it as out of scope — and check
3's escape clause is written as a *condition on the manifest* that was unmet when the text was
authored and is met now.

**What the rewrite must say**, carried here so it is not re-derived: **check 1 governs every store
path not under `claude/`**; **check 3 governs `claude/`**; and **neither treats the other's
population as a finding** — a `claude/`-namespaced document is out of the export set by construction,
neither a check-1 finding nor a check-3 exception. The reasoning is BL-143's and is not restated
here; the standing form is `CLAUDE.md` §Definition of done.

**NOT KNOWN, and this row's first step.** Whether anything else in that prompt assumes the unscoped
reading — the remove half of the procedure, the ordering of the three checks, or any prose
describing what the store contains. That sweep **was not run** at the close, and nothing here should
be read as a claim that the two checks are the only affected text. Running it is this row's first
step, before any edit.

**Why this is its own row and not a widening of BL-143's Done-when.** BL-143 asks one question —
ownership and trigger — and widening it to carry this rewrite would be **BL-162's defect committed
in the act of recording it**: an obligation attached to a row from outside, silently changing what
that row must satisfy. BL-143's Done-when can be discharged in full without this rewrite ever
happening, which is precisely why the deferral needed an executor rather than a mention.

**Why it was not done in the ruling's own commit**, in the ruling's own words: *"the ruling and the
procedure it governs are separate landings, and a procedure edited in the same commit as the ruling
that authorises it cannot be reviewed against it."*

**Done when:** §Post-upload verification states the namespace boundary for check 1 and check 3, and
the sweep above has been run with its result recorded — including the result that there is nothing
else, if that is what it finds.

**Costs:** S. The two checks are a paragraph each. The sweep is the unpriced half and is small.

**Collides with:** nothing. It does not reopen BL-143's ruling and does not touch that row's open
Done-when. **BL-161**'s second branch — whether the export mechanism owes a sprint case — concerns a
different file and does not wait on this.

`Source: the BL-143 close of 2026-08-16, packet §4, which established that the deferral recorded
inside BL-143 had a record and no executor. The deferred text is quoted from BL-143's `[Ruled
2026-08-16 …]` annotation at `84c24c7`. The prompt file was read at `84c24c7` to establish the
quotations above and was **not** edited, then or by this filing.`

`[CLOSED 2026-08-18 at the ds cycle's export boundary, stage A. **The correction landed at agents
`7e8602d`**, which touches `prompts/bl-002-refresh-project-knowledge.md` and nothing else: checks 1
and 3 replaced unit by unit, quote-then-replace, with check 2, the section intro and the row's
`Source:` line byte-unchanged.

**The occasion is this boundary; the reason is that the checks are wrong independent of ds.** They
were written without a namespace boundary, and read without one they contradict each other on the
documents that actually exist — true on 2026-08-16 when this row was filed, and true at any later
date with no boundary in sight. Nothing here is a change made to get a boundary green: these are
post-*upload* checks. No gate in either repo runs them, `drift_check` does not read this file, and
the correction could not have moved any result in the session that made it, in either direction.

**Done-when, clause by clause.** *"§Post-upload verification states the namespace boundary for check
1 and check 3"* — **check 1** now runs over *"every store path **not** under `claude/`"* and states
that such a document *"carries no row and is out of the export set **by construction**: it is not a
check-1 finding, and check 3 is where it is accounted for"*. **Check 3** now splits on the namespace
— under `claude/` an enumeration with no condition on the manifest owed and no check-3 exception
claimed, outside `claude/` an incremental upload and the finding — and the unmet subjunctive
*"in which case the manifest should say such documents may coexist and are out of scope"*, whose
condition BL-143's ruling discharged, is gone. A closing sentence points at BL-143 for the reasoning
and `CLAUDE.md` §Definition of done for the standing form, and states that neither check treats the
other's population as a finding. The rewrite says what this row said it must say and adds nothing to
it.

*"and the sweep above has been run with its result recorded — including the result that there is
nothing else, if that is what it finds"* — **run, and it is not nothing.** Population: every line of
the prompt file matching `store|remove|upload|project knowledge|knowledge file|claude/|namespace|document set|coexist|non-manifest`
(case-insensitive), 28 lines, read one by one. Four sites cleared and one finding:

- **`:148`, the ordering of the three checks** — *"Three checks, and the third is the one that
  catches an incremental upload"*. **Survives the scoping and is unchanged.** Under the ruling check
  3's `claude/` arm is an enumeration, but its other arm — a document outside `claude/` older than
  the window — still means the remove was partial, so the sentence remains true of the rewritten
  check.
- **`:141–146`, the prose describing the store** — describes `drift_check`'s blindness and who runs
  the verification. Names no population and assumes no namespace. **Unchanged.**
- **`:73`, *"an uncommitted edit does not reach the store"*** — a statement about the assembler's
  source, not about the store's contents. **Unchanged.**
- **the section's `Source:` line** (`:164–165` before the correction, `:173–174` at `7e8602d`) —
  *"the store-side check that found the manifest describing 25
  documents while the store held 26"*. A point-in-time record of the m3 boundary of 2026-08-05, and
  the 26th document's namespace is not recorded anywhere this session can reach. Point-in-time
  records are not amended (BL-143's ruling, on the two deviation blocks). **Unchanged, deliberately.**
- **`:107–110`, the remove half of the procedure — THE FINDING, and it is not this row's class.**
  Step 5 tells the operator to *"REMOVE the old knowledge files (stale handoff, old
  specs/architecture/runbook/protocol/README, old CLAUDE.md), then upload everything in
  /tmp/claude-project-export/"*. That does **not** assume the unscoped reading — it names no
  namespace at all, and errs the other way: it is a hand-written enumeration of document *kinds*
  standing in for *all of the manifest set*, so an operator following it literally performs a
  partial remove, which is the very thing check 3 exists to catch. Different class from this row's
  (a short enumeration, not an unscoped rule), a different unit of the file, and outside the scope
  this row states. Filed as **BL-165**, which is its executor; not closed here and not folded into
  this row.

**What this close does not touch.** BL-143's Done-when — who owns the boundary and on what trigger —
is untouched and still open, exactly as this row's *Collides with* said. BL-161's second branch is
untouched.]`

---

### BL-161 — the export-mechanism round deferred a sprint arm and filed no row (#TBD)
**Status:** DONE
**Kind:** process · **Census items:** n/a · **Contract:** `CLAUDE.md` (agents) §Learning — BL-007 — *a deferred finding gets a backlog row in the same round it's deferred*
**Size:** S · **Priority:** medium
**Section:** process / backlog discipline; the arm itself is harness (`../aetheris/scripts/sprint.sh`)

Filed 2026-08-16 at the export boundary's amendment pass. Established at agents `a2df7b5`.

**What happened.** The export-mechanism round (agents `5dae22b`, 2026-08-16) shipped
`scripts/repin_manifest.py` and `scripts/assemble_export_bundle.py` with tests and a runbook
pointer, and recorded in its notes that one companion could not land
(`docs/milestones/export-mechanism-implementation-notes.md`):

> **One companion is owed and cannot land here: a sprint case.** Both comparators have one
> (`sprint.sh` `capability_matrix` and `drift_check`, `aetheris/scripts/sprint.sh:1533` and
> `:1594`). `sprint.sh` lives in the harness, which this ticket's REPOS clause puts out of bounds,
> so the export mechanism ships with tests and no sprint arm. Reported rather than quietly
> dropped; it is a gap for whoever takes BL-143, not a defect this ticket may fix.

The reasoning is sound and the deferral is correct. **The record is not.** That round's commits
touched `CLAUDE.md` and never `docs/backlog-2026-06.md`, and **BL-143's row does not mention a
sprint arm** — so the sentence *"it is a gap for whoever takes BL-143"* addresses a reader who has
no way to receive it. Whoever takes BL-143 opens BL-143.

**The rule it breaches** is `CLAUDE.md` §Learning — BL-007: *a deferred finding gets a backlog row
in the same round it's deferred — prose in a packet or notes files nothing.* The same entry's
closing clause is why naming BL-143 was not enough: a finding recorded somewhere that does not
carry an executor *"has a record, not an executor"*.

**The breach was recoverable only by accident, and that is the part worth keeping.** The notes file
is committed and attributed, so the deferral survives in a readable form — that is the *only*
reason this row can be written at all. But nothing was going to read it. It surfaced because the
2026-08-16 export boundary's content sweep **wandered past its own scope**: that sweep was
chartered to find closures and rulings missing from tracked files, a sprint arm is neither, and it
was found by a session reading the round's notes for something else and noticing. A discipline that
depends on the next session being curious about a file it had no reason to open is not a discipline.

**Whose omission this is.** The arbiter's, stated so the record is not silently flattering: the
export-mechanism packet was approved and its §8 ruled against, without noticing that a deferred
companion had no row.

**What is actually owed, kept small.** A `sprint.sh` case exercising the two export scripts, beside
the `capability_matrix` and `drift_check` cases it would sit with. It is a harness write, so it
needs a cross-repo ticket; nothing about it is difficult, and it has been unowned since 2026-08-16.

**Done when:** either the sprint arm exists and is named in a boundary record, or a ruling is
recorded that the export mechanism's tests are sufficient and no sprint case is owed — with the
reason, in `CLAUDE.md` §Definition of done beside the mechanism's pointer, where a reader of that
pointer will meet it.

**Costs:** S. The arm is a few lines against two scripts that already exit non-zero on failure.

**Collides with:** **BL-143**, which the notes file named as the inheriting row and which does not
know it. Closing this row's first branch is naturally part of BL-143's work; closing its second
branch is not, and does not wait for it.

`[Annotated 2026-08-16 at BL-143's close. The **Collides with** above states, in passing, a shape
that is now filed as a finding in its own right: a document named BL-143 as the inheriting row and
BL-143 *"does not know it."* That is one of **BL-162**'s two instances — the other is the
check-1/check-3 contradiction, routed to the same row by two further documents and equally invisible
from it — and BL-162 owns the question of what a citing document owes its target. **This row is
unchanged by that filing:** the sprint arm is still owed here, both branches of its Done-when stand
as written, and BL-162 closes neither.]`

`Source: the export boundary of 2026-08-16, packet §F4, and the amendment pass that filed it. The
quoted paragraph is transcribed from `docs/milestones/export-mechanism-implementation-notes.md`
at agents `a2df7b5`. The attribution of the omission is the arbiter's own, given at the amendment.`

`[Disposed 2026-08-21 at ds t3, on Done-when branch 1. Branch 2 — a ruling that the tests suffice —
is NOT taken and is not reachable from here.

**WHAT LANDED.** A `sprint.sh` case, `export_mechanism`, at harness `d648aa8`, sitting immediately
after `drift_check`'s `fi` — beside the two comparators this row names. Six assertions, every one
through a command line: `repin_manifest.py --dry-run` exits 0 and leaves the tracked manifest
byte-identical, asserted by sha256 across the run; `repin_manifest.py` against an unreadable
`--manifest` exits 1; `assemble_export_bundle.py DEST` exits 0, writes a non-empty bundle and puts
the manifest's own row in it, with no `_UNSWEPT-DO-NOT-UPLOAD.txt` marker; a non-empty destination
without `--replace` exits 1; the temp destination is removed. It is in `all`, it is hermetic, and it
writes no tracked file. It is **not promoted** — every assertion uses `fail` — because R7 makes
promotion per-arm and requires the promoting ticket's own verification on the record.

**WHY IT WAS WORTH BUILDING, re-derived at HEAD rather than assumed.** Both scripts end in
`sys.exit(main())` and the 37 tests across `tests/test_export_bundle.py` and
`tests/test_repin_manifest.py` contain zero occurrences of `main(`; their only subprocess helper
runs `git`. Demonstrated rather than argued: mutating `sys.exit(main())` to `main()` in
`repin_manifest.py` leaves those 37 tests reporting `37 passed` and makes the new arm report *"the
CLI is not propagating main()'s exit code"*.

**THE HALF OF BRANCH 1 THIS TICKET COULD NOT PERFORM AS WORDED, stated rather than glossed.**
Branch 1 reads *"the sprint arm exists and is named in a boundary record"*. In this repository a
**boundary record** is a dated entry in `docs/project-knowledge-manifest.md`'s export-boundary log,
and ds t3 runs no export boundary, so no such entry can honestly be written here. The naming was
landed instead in `CLAUDE.md` §Definition of done, in the paragraph that already carries the
mechanism's pointer and its `Tests:` line — which is where branch 2 places *its* outcome, on the
stated ground that a reader of that pointer will meet it, and it is the surface the next boundary
record's author reads. **This is a substitution of surface and it is the arbiter's to accept or
reverse.** The row is marked DONE rather than held open because what remained was a naming with no
executor and no trigger, which is the precise failure this row was filed about.

**THE `Collides with` CLAUSE ABOVE IS SUPERSEDED.** It says *"Closing this row's first branch is
naturally part of BL-143's work"*. BL-143's scope note of 2026-08-16 refuses that routing in terms:
the sprint arm *"[does not] appear anywhere in this row's own text"*, and BL-143's Done-when —
ownership and trigger — is *"unchanged and open"*. Branch 1 belonged to no row but this one, and it
belongs to ds t3. BL-143 is untouched by this disposition and stays open on its own question. The
routing itself is **BL-162**'s subject, and this is one of its two instances working out in
practice.]`

`[Amended 2026-08-21 at ds t3 stage 3, after the arbiter ruled on stage 2's packet.

**The substitution is ruled, and by whom.** Branch 1's second clause — *"named in a boundary
record"* — was **discharged by substitution of surface**, and the arbiter ruled that substitution
accepted. The reason, in one sentence: a boundary record here is a dated entry in
`docs/project-knowledge-manifest.md`'s export-boundary log, ds t3 runs no export boundary, and so
the naming landed in `CLAUDE.md` §Definition of done beside the mechanism's pointer — the surface
branch 2 was told to use, for the same reason it was told to use it, that a reader of that pointer
will meet it.

**And the naming now has an executor, which is what stage 2 left owing.**
`prompts/bl-002-refresh-project-knowledge.md` — the operator procedure, and the document that
actually causes a boundary record to be written — gains a **Step 0** that runs
`./scripts/sprint.sh export_mechanism` before anything is written, and its Step 2 now requires the
boundary record's narrative to name that arm and the verdict it returned. So the next boundary
record carries the naming **by construction** rather than because someone remembered. A naming no
procedure causes is a promise, and a deferral with no executor is this row's own subject; that is
why the amendment exists and why the row did not close honestly without it.

**This row stays DONE.** Nothing above is reopened. The arm existed at the disposition and exists
now; what changed is that the second half of branch 1 is now performed by a procedure instead of
asserted by a document.]`

[Corrected 2026-09-15, BL-253: both sentences above that define a boundary record as an entry in
`docs/project-knowledge-manifest.md` describe the file as it was. Records now live in
`docs/export-boundaries/<date>.md`, each indexed by one line in the manifest's `## Export boundary log`.]

---


### BL-171 — `mix hex.audit` is red: bandit 1.12.4 carries two advisories, and 1.12.5 is out (#TBD)
**Status:** DONE
**Kind:** bug · **Census items:** n/a · **Contract:** harness `CLAUDE.md` §CI contract, `### mix hex.audit — supply-chain gate`
**Size:** S · **Priority:** high
**Section:** harness (`../aetheris/mix.exs`, `../aetheris/mix.lock`)

Found 2026-08-21 by **ds t3**'s ticket-boundary gate run — off-territory, exactly the way the gate
rule intends, on a ticket whose subject is a sprint arm and not the dependency tree. Filed the day
it was found, not carried.

```
$ cd ~/sandbox/elixirws/aetheris && mix hex.audit          # exit 1
Advisories:
  bandit 1.12.4 - EEF-CVE-2026-75484 (MEDIUM)
    aka: CVE-2026-75484, GHSA-x3gh-xhj4-3vq8
    HTTP/2 header field values containing CR, LF or NUL are passed to the application unvalidated in Bandit
    https://osv.dev/vulnerability/EEF-CVE-2026-75484

  bandit 1.12.4 - EEF-CVE-2026-74836 (HIGH)
    aka: CVE-2026-74836, GHSA-xj8g-532w-jv94
    HTTP/2 connection-window starvation pins Plug processes indefinitely in Bandit
    https://osv.dev/vulnerability/EEF-CVE-2026-74836

Found packages with security advisories
```

**This is NOT BL-060 recurring, and the distinction is the whole reason a new row was needed.**
BL-060 is DONE and its subject was **bandit 1.11.1 / EEF-CVE-2026-65623**, a different package
version and a different advisory. These two are new. No open row named `bandit` or `hex.audit`
before this one.

**Upstream-triggered, not commit-triggered.** ds t3's two commits touch `../aetheris/scripts/sprint.sh`
and eight agents-side documents; neither goes near `mix.exs` or `mix.lock`. The advisories were
published under a lock nobody moved. Harness `CLAUDE.md`'s own supply-chain section says this is the
gate working rather than a defect — *"An advisory published upstream turns it red through nobody's
commit. That is the gate reporting that the world changed under us."*

**A patched release appears to exist and was NOT taken here.** `mix hex.info bandit` reports
**1.12.5 (2026-08-20)** against a locked **1.12.4 (2026-07-27)**, and `mix.exs:30` declares
`{:bandit, "~> 1.12"}`, so the constraint already admits it. Whether 1.12.5 actually carries the
fixes for both CVEs is **not established here** — it was inferred from the release date, and this
row does not assert it. ds t3 did not bump: a dependency change belongs to a ticket that can run the
full harness gate set against it and read the changelog, not to a sprint-arm ticket that happened to
find the red.

**This row is why BL-169 matters, arriving as an instance rather than an argument.** BL-169 records
that `mix hex.audit` is a declared merge gate no workflow runs. This red was found only because a
human-directed ticket-boundary run typed the command. Nothing in CI would have reported it, and
nothing will report the next one.

**Done when:** either `bandit` is on a version `mix hex.audit` reports clean — with the changelog
read and the fix for **both** advisory ids confirmed rather than inferred from a version number —
or, if no patched version covers one of them, that advisory is accepted in writing with its
rationale here and the gate runs **expected-red, named with this row's ref** per the tracked-carry
clause. Not relaxed, not re-pointed, and not downgraded to a warning.

**Costs:** S if 1.12.5 is the fix — a lock bump and the harness gate set. Larger only if it is not.

**Collides with:** **BL-169**, which owns the question of what runs `hex.audit` and what its red does
to a pull request. Neither closes the other: BL-169 owes a decision about the gate, this row owes a
clean audit.

`Source: ds t3's ticket-boundary gate run, 2026-08-21, at harness `d648aa8` / agents `f003e4a`. The
audit output is transcribed complete rather than excerpted. The `1.12.5` figure is from
`mix hex.info bandit` run the same day and is a claim about Hex, not about this repository.`

`[Disposed 2026-08-22 at BL-171. Done-when branch 1 — *"`bandit` is on a version `mix hex.audit`
reports clean, with the changelog read and the fix for **both** advisory ids confirmed rather than
inferred from a version number"*. Branch 2 — an advisory accepted in writing with the gate carried
expected-red — is NOT taken and is not reachable from here.

**THE READ, WHICH IS WHAT THIS ROW ACTUALLY OWED.** The row was explicit that 1.12.5 carrying the
fixes was *"not established here — it was inferred from the release date"*. Both advisories were
resolved at their OSV records (`curl -sS https://api.osv.dev/v1/vulns/<id>`), not at a version
number:

| advisory | severity | affected range, as OSV states it | first fixed |
|---|---|---|---|
| `EEF-CVE-2026-74836` | HIGH, `CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N` = 8.7 | SEMVER, `{"introduced": "0.3.4"}` → `{"fixed": "1.12.5"}` | `1.12.5` |
| `EEF-CVE-2026-75484` | MEDIUM, `CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N` = 6.9 | SEMVER, `{"introduced": "1.4.0"}` → `{"fixed": "1.12.5"}` | `1.12.5` |

`74836` is allocation of resources without limits: when a response body exceeds the HTTP/2
connection-level send window, Bandit queues the remainder with no timeout bound, so an
unauthenticated client holding the connection window shut with periodic PINGs pins the stream
process indefinitely. The stream-level path is bounded at 15 s; the connection-level path was not.
`75484` is CRLF neutralisation: `Bandit.HTTP2.Stream.read_headers/1` validated pseudo-header
placement, casing, connection-specific headers, `te` and `content-length`, but never field
**values**, so HTTP/2 header values containing CR, LF or NUL reached the application unvalidated —
a check the HTTP/1 path already performed.

**The installed version is in both ranges and 1.12.5 is outside both**, checked against each
record's own `versions` array rather than by reasoning about semver: `1.12.4` is present in both,
`1.12.5` in neither.

**The changelog confirms it independently, and names the advisories by id** — which is the
difference between a read and a date inference. `bandit` 1.12.5 (20 Aug 2026,
https://bandit.hexdocs.pm/changelog.html):

> **Changes** — "Bound and cancel HTTP/2 sends blocked on the connection window
> (GHSA-xj8g-532w-jv94) (#671)"
>
> **Fixes** — "Validate HTTP/2 header field values for CR/LF/NUL (GHSA-x3gh-xhj4-3vq8) (#670)"

So this is **Case 1 — 1.12.5 fixes both**. Had it fixed one, the bump would not have been taken:
a partial fix that turns the gate green removes the signal and leaves the defect.

**ONE THING COULD NOT BE READ, and it is recorded rather than glossed.** The two GHSA identifiers
do not resolve as records anywhere reachable from here. `GHSA-xj8g-532w-jv94` and
`GHSA-x3gh-xhj4-3vq8` both return **404** from `gh api /advisories/<id>` and from
`https://api.osv.dev/v1/vulns/<id>`, and `https://github.com/advisories/<id>` returns 404 to a
fetch. The same command with the same flags resolves `GHSA-vv2x-vrpj-qqpq` and
`GHSA-2c7c-3mj9-8fqh` normally, so the searches are not simply blind. These are Erlang Ecosystem
Foundation advisories: the GHSA ids exist as **aliases** in the EEF-sourced OSV records and as
citations in `bandit`'s changelog, and both of those were read. What could not be done is
corroborating the EEF record against an independent GitHub record. The two sources actually read
agree, and they are not fully independent of each other.

**WHAT LANDED.** Harness `7ea1a3a`, `mix.lock` alone — one line, `bandit 1.12.4` → `1.12.5`, with
its new hashes. No transitive dependency moved; `mix deps.get` afterwards reports every other
package `Unchanged`.

**`mix.exs` is deliberately unchanged, recorded as a decision rather than left as a silent
non-choice.** `{:bandit, "~> 1.12"}` at `mix.exs:30` already admits 1.12.5, so the fix belongs in
the lock alone. Pinning `~> 1.12.5` would narrow the constraint permanently in order to fix
something already fixed, and would then be the obstacle at the next advisory.

**THE GATE.** `mix hex.audit` now exits **0**: `No retired or security advisory packages found`.
The full harness seven were run once at the boundary after the commit, each in the foreground
under an explicit `timeout`, all exit 0: `deps.get` 1s, `hex.audit` 1s,
`compile --warnings-as-errors` 3s, `format --check-formatted` 0s, `credo --strict` 4s
(`2056 mods/funs, found no issues`), `dialyzer` 17s, `test` 94s.

**The two load-bearing gates were baselined before the bump and compared after**, because `bandit`
is the HTTP server and a dependency bump makes them evidence rather than routine. `mix test`:
`972 tests, 0 failures, 133 excluded` both sides, wall 90.8 s → 91.7 s, and the single compiler
warning (`module attribute @github_mcp_skip_reason was set but never used`) is byte-identical
before and after — it is a pre-existing test-file warning and is not `bandit`'s. `mix dialyzer`:
`Total errors: 0` both sides, and the application list under analysis is the same 29 apps. Its
wall time moved 5 s → 17 s for a stated reason and not an unexplained one — the baseline reported
`PLT is up to date!` while the post-bump run rebuilt the PLT over `1175 modules`, `bandit`'s beams
having changed. Analysis time itself moved 4.24 s → 4.42 s.

**WHAT THIS ROW DID NOT CLOSE.** **BL-169** stands. This red was found by a human typing the
command at a ticket boundary, which is that row's argument arriving as an event; the instance is
recorded on BL-169 and the row is not closed by it. Filing that instance turned up a second and
larger fact — `ci.yml` fires on `pull_request` only and no pull request has been opened since
2026-05-17 — which is **BL-172**, filed at this ticket.]`

`Source: BL-171, 2026-08-22. Harness `7ea1a3a`, agents at the commit carrying this disposition. The
advisory table and the version-membership check are from the OSV JSON captured at this ticket; the
changelog block is quoted from `bandit.hexdocs.pm`. No figure above is carried from the row's own
2026-08-21 capture — `mix hex.audit` was re-run at HEAD before any edit and reproduced it exactly.`

---

### BL-169 — `mix hex.audit` is a declared merge gate that no workflow runs (#TBD)
**Status:** DONE
**Kind:** bug · **Census items:** n/a · **Contract:** harness `CLAUDE.md` §CI contract
**Size:** S · **Priority:** medium
**Section:** harness (`../aetheris/.github/workflows/ci.yml`, `../aetheris/CLAUDE.md` §CI contract)

Filed 2026-08-21 at ds t3, from the gate-declaration census filed on **BL-150** the same day. Out
of ds scope — this row is the executor, and ds t3 does not fix it.

**The declaration.** Harness `CLAUDE.md` §CI contract lists seven commands under *"Every change must
pass all of these before merge"*, and `mix hex.audit` is one of them. It is the only member of that
set with a section of its own — `### `mix hex.audit` — supply-chain gate` — added 2026-07-17 on a
human call, whose stated evidence is **BL-020**, where fifteen advisories across the HTTP stack were
invisible to every other gate and surfaced only by a clean-clone spot-check. That section also
states two properties that only make sense for a gate something runs: that an upstream-published
advisory turning it red *"is the gate working, not a defect"*, and that advisories cannot be
suppressed because the tool has no ignore mechanism.

**Nothing runs it.** `../aetheris/.github/workflows/ci.yml` is the only workflow file in the
repository (`git ls-files | grep -iE '\.github|\.gitlab|circleci'` returns it and
`.github/copilot-instructions.md`). Its main job runs `deps.get`, `compile --warnings-as-errors`,
`format --check-formatted`, `credo --strict`, `dialyzer` and a tag-excluded `mix test`; a second job
runs the sandbox set behind a capability probe. `mix hex.audit` appears in neither. There is no mix
alias wrapping it (`mix.exs` declares no `aliases`), no tracked git hook, and no Makefile or
justfile. The whole-repo search for the string in the harness returns four hits: the contract entry,
its own section heading, a line inside that section, and one implementation-notes file.

**Why it matters more than the other three disagreements** on the BL-150 census. The others are
declarations that under-state what CI does. This one is the reverse: a gate whose entire purpose is
to catch a red **nobody's commit caused**, so no ticket-boundary run will encounter it by accident.
An upstream advisory published today is invisible until someone types the command from memory. That
is exactly the invisibility the standing gate rule exists to prevent, arriving through absence
rather than through neglect.

**First live instance, 2026-08-22 (BL-171).** `mix hex.audit` went red on two upstream `bandit`
advisories — `EEF-CVE-2026-74836` and `EEF-CVE-2026-75484`, both published `2026-08-20T21:11Z`
(`curl -sS https://api.osv.dev/v1/vulns/<id>`, field `published`) — under a lock nobody moved. It
was found only because **ds t3's** ticket-boundary run typed the command, and it was cleared at
BL-171 by a lock bump to `bandit 1.12.5`. That is this row's argument arriving as an event rather
than as a prediction.

**And the reason no workflow reported it is worse than this row states.** This row establishes that
`ci.yml` does not contain `mix hex.audit`. It does not establish that `ci.yml` *runs* — and it does
not: the most recent workflow run on `vishal-h/aetheris` is `2026-05-17T14:10:29Z` on branch
`t2-write-file`, three months before these advisories existed
(`gh run list --limit 1 --json createdAt,headBranch,conclusion`). So the counterfactual *"CI would
not have caught it"* holds for two independent reasons, and wiring `hex.audit` into `ci.yml` would
have closed neither. **That second reason is out of this row's scope and is filed as BL-172**; this
row still owes only the decision about what runs the gate and what its red does to a pull request.
BL-171 does not close it.

**Done when:** either `mix hex.audit` runs in CI — and, given that its red is upstream-triggered and
unsuppressable, the decision of what a red does to a pull request is taken and recorded with it — or
the §CI contract stops declaring it a merge gate and says what does run it and on what trigger. Not
both silently.

**Costs:** S to wire. The decision about upstream-triggered reds is the part with judgement in it,
and the §CI contract's own section already argues one side of it.

**Collides with:** nothing. **BL-150** carries the census this came from and settles nothing; this
row is the only executor for this half of it.

`Source: ds t3, 2026-08-21, derived at harness `d648aa8`. Every claim above was re-run rather than
carried: the contract's seven, the workflow's steps, the absence of aliases and hooks, and the
four-hit search.`

---

**DONE 2026-08-22 at BL-172, on Done-when's FIRST disjunct.** The disjunction is *either*
`mix hex.audit` runs in CI with the decision about its red taken and recorded *or* §CI contract
stops declaring it a merge gate. The second disjunct is not taken: the contract is unchanged and
still declares the seven. The first is taken in both its halves, and the row's own text says the
halves are separable — *"S to wire. The decision about upstream-triggered reds is the part with
judgement in it."*

**THE WIRING.** Harness `203dec8` adds a step to `ci.yml`'s `check` job, between `mix deps.get`
and `mix compile --warnings-as-errors`, named `mix hex.audit (advisory — visible, non-blocking)`.

**THE JUDGEMENT, ruled 2026-08-22 and recorded here because the wiring does not carry it.** An
advisory red is **VISIBLE and NON-BLOCKING**. Both properties bind at once, and inside one step
they pull against each other: a step that fails makes the red visible and blocks, and a step that
swallows its exit code makes it non-blocking and invisible in the run's conclusion. The step
resolves it by splitting the two channels — the advisory text goes to `$GITHUB_STEP_SUMMARY`,
which is where a reader meets the run, and the exit code is always 0, so the job's conclusion is
never `failure` because of it. That form is not invented here: the `sandbox` job in the same file
already solves the same shape for its named skip, and its comment states the reason — a job that
reddens on something nobody's commit caused gets disabled, which is how the `requires_worker` set
rotted the first time.

**THE FAILURE MODE THIS ACCEPTS, stated rather than left for a later reader to find.** A
non-blocking gate is one nobody is forced to look at. What makes it visible is the summary
section on the run's own page; what would make it ignorable is habituation — nothing fails, no
notification is sent, and a summary section can be scrolled past. The step's comment carries this
same paragraph, so the ruling is legible at the place it governs. If advisories do start being
ignored, the answer is an owner and a trigger, not a red X.

**WHAT IS PROVEN AND WHAT IS NOT.** The step's two arms were run before the commit landed,
against the step body **extracted from the committed YAML** rather than retyped, with a stub `mix`
on `PATH` and `GITHUB_STEP_SUMMARY` pointed at a file: with the stub exiting 0 the summary reads
`### Supply-chain audit: clean`; with the stub exiting 1 the summary carries the advisory text
under `### Supply-chain audit: ADVISORIES FOUND — and this job did NOT fail` and **the step still
exits 0**. That is a local exercise of the step's own shell, not a run on GitHub.

**A red advisory's behaviour on a real runner is therefore UNVERIFIED by this row**, and it gets a
stated closing condition rather than silence or a ticket: it closes the first time `mix hex.audit`
goes red after this lands, because the standing gate rule already requires that red to get a
tracked ticket the day it is found — and that ticket is written by someone looking at the run.
No row owns it and none should; manufacturing a red to test it would mean faking an advisory in
the lock.

**WHAT THIS ROW DID NOT CLOSE.** **BL-172** stands. `mix hex.audit` is in a workflow that, at
this commit, still has no run on the record triggered by the path work takes — the `push:` trigger
lands in the same harness commit and is unverified until something is pushed. This row owed the
decision about what runs the gate and what its red does; it did not owe the proof that the
workflow fires, which is BL-172's and stays BL-172's.

`Source: BL-172, 2026-08-22, at harness `203dec8` / agents at the commit carrying this
disposition. The step is quoted from `ci.yml` at that commit; the two-arm exercise is this
ticket's own and its transcript is in the review packet, which is not committed.`

`[Added 2026-08-22 at BL-172's close, and it NARROWS the two paragraphs above rather than
correcting them — both were true when written and stay unedited. The step has since executed on a
GitHub runner: run `32563924592`, `check` job step 9, exit 0, log ending
`No retired or security advisory packages found`. Two things follow. The runner reports
`shell: /usr/bin/bash -e {0}` for that step — the same interpreter and flag the local two-arm
exercise used — so the shell semantics the `set +e` / `status=$?` / `set -e` construction depends
on are corroborated on the runner and are no longer an assumption. And what remains unverified is
therefore **narrower than "a red advisory's behaviour"**: it is the `else` branch's own content,
the text under `### Supply-chain audit: ADVISORIES FOUND`, which has executed nowhere but the local
stub. **The closing condition itself is unchanged** — the first real red after this lands, read by
whoever files the tracked ticket that red owes. BL-172's own disposition carries the same narrowing
under its item (b).]`

---

### BL-172 — `ci.yml` fires on `pull_request` only, and no pull request has been opened since 2026-05-17 (#TBD)
**Status:** DONE
**Kind:** bug · **Census items:** n/a · **Contract:** harness `CLAUDE.md` §CI contract
**Size:** M · **Priority:** high
**Section:** harness (`../aetheris/.github/workflows/ci.yml`, `../aetheris/CLAUDE.md` §CI contract)

Filed 2026-08-22 at **BL-171**, from a claim that ticket wrote into BL-169 and then could not
support. The draft sentence read *"every CI run on this repository was green"*; checking it before
it stood showed there had been no CI run at all. The row exists because the check was run, not
because the defect was suspected.

**BL-169 establishes that `ci.yml` does not contain `mix hex.audit`. This row is the larger fact
underneath it: `ci.yml` does not run.** The two are independent, and neither closes the other —
wiring `hex.audit` into a workflow nothing triggers changes nothing.

**The mechanism, read from the file rather than inferred.** `../aetheris/.github/workflows/ci.yml`
declares its triggers in full as:

```yaml
on:
  workflow_dispatch:
  pull_request:
```

There is no `push:`. So the workflow fires on a pull request, or when a human dispatches it by
hand, and on nothing else.

**And the pull-request path has been unused for three months.** Every figure here carries the
command that produced it, run at harness `7ea1a3a`:

| what | figure | command |
|---|---|---|
| most recent workflow run | `2026-05-17T14:10:29Z`, branch `t2-write-file`, `success` | `gh run list --limit 1 --json createdAt,headBranch,conclusion` |
| most recent pull request | `#70`, `2026-05-17T14:10:24Z` | `gh pr list --state all --limit 5 --json number,title,createdAt` |
| commits on `main` since that date | `371` (`24` of them merges) | `git log --since=2026-05-17 main --oneline \| wc -l` |
| last commit touching the workflow | `6e2fad8`, `2026-07-25` | `git log -1 --format='%h %ad %s' --date=short -- .github/workflows/ci.yml` |

The last run and the last PR are five seconds apart, which is the same event: PR #70 opened, CI
ran, and neither has happened since. The 24 merge commits are local merges, which `pull_request`
does not observe. `6e2fad8` is the sharpest of the four — the workflow was **edited** on
2026-07-25, two months after the last run that could have exercised the edit.

**What this costs, stated rather than left to inference.** Harness `CLAUDE.md` §CI contract opens
*"Every change must pass all of these before merge"* and lists seven commands. Six of the seven
are in `ci.yml`; the seventh is BL-169. For 371 commits the enforcement of all six has been the
ticket-boundary rule and nothing else — which is to say, a human typing them. That rule works, and
this cycle is evidence that it works: BL-171's red was found by exactly that route. But the §CI
contract describes a merge gate, and what exists is a discipline. **A discipline and a gate fail
differently**, and the contract does not say which one a reader is being promised.

**Not a regression, and not silently carried.** Nothing broke; the repository changed how it
lands work — direct to `main` rather than through pull requests — and the workflow's trigger was
never moved to match. That is the same shape as the standing gate rule's own examples, where a
gate rots because nothing runs it off-territory.

**Done when:** either the workflow fires on the path work actually takes — a `push:` trigger on
`main`, or a stated requirement that changes land through pull requests — with one run on the
record proving it fires, **or** the §CI contract stops calling these seven a merge gate and says
what enforces them and on what trigger. Not both silently, and not a `workflow_dispatch` run
performed once to make this row look closed: the Done-when is about the trigger, not about a run.

**Costs:** M. Adding `push:` is a two-line edit; deciding whether this repository wants
pull-request-gated merges is not, and the answer changes what BL-169 should do as well.

**Collides with:** **BL-169**, which owes the decision about `mix hex.audit` specifically. This row
owes the decision about whether the workflow runs at all. BL-169's fix is inert until this one
lands; this one does not close BL-169.

`Source: BL-171, 2026-08-22, at harness `7ea1a3a` / agents `001a2fe`. Every claim above was run
rather than carried — the trigger block is quoted from the file, and the four figures each carry
their command in the table. The `pull_request` trigger has a trailing space in the source file,
preserved in neither the quote above nor this note because it is not load-bearing.`

**2026-08-22 — the trigger lands at harness `203dec8`, and this row STAYS OPEN.** Read the
Done-when as written: disjunct 1 is *"the workflow fires on the path work actually takes — a
`push:` trigger on `main` … — **with one run on the record proving it fires**"*. The trigger half
is done. The run half cannot be: the commit is held for review and nothing is pushed, so no
push-triggered run exists and none can until it is. The row's closing sentence — *"the Done-when
is about the trigger, not about a run"* — refuses a `workflow_dispatch` run staged to look like
closure; it does not remove the proof this disjunct asks for, and reading it that way would close
the row on the strength of a file nobody has run.

**What landed.** `push: branches: [main]`, scoped to `main` rather than to every branch. `main`
is the path work actually takes; a pull-request branch would otherwise run the whole workflow
twice for one commit, once on `push` and once on `pull_request`; and a work-in-progress branch is
not what a merge gate is for. The concurrency group landed with it, in the same commit, because
shipping the trigger without it is a defect — `group: pr-${{ github.event.pull_request.number }}`
yields `pr-` on every event that is not a pull request, so each push run would have joined one
group and cancelled its predecessor whatever ref it was for. `cancel-in-progress` became
conditional at the same time and this is the one judgement in the edit beyond what was asked:
cancelling a superseded run is right for a pull request and wrong for a push to `main`, where two
pushes seconds apart would otherwise leave the first commit with no completed run — the exact
property this trigger exists to produce.

**What the first push-triggered run has to show, so the reader is not left to infer it.** That run
is this row's evidence, and it happens when the arbiter pushes. Look for: an entry in
`gh run list` whose event column reads `push` and whose branch is `main`; two jobs, `check` and
`sandbox`; `check` concluding `success` with a step named
`mix hex.audit (advisory — visible, non-blocking)` between `mix deps.get` and
`mix compile --warnings-as-errors`; that step's summary section on the run page reading
`### Supply-chain audit: clean`, since the lock is green at `bandit 1.12.5`; and `sandbox`
concluding `success` with its named skip, which is that job's design and not a defect.

**What that run still will not show.** A *red* advisory's behaviour. The step is implemented
non-blocking and was exercised in both arms locally, and no run on a green lock can demonstrate
it — see the closing condition recorded on **BL-169**, which this commit closed.

`Source of the 2026-08-22 block: BL-172 itself, at harness `203dec8` / agents at the commit
carrying it. The Done-when is quoted from this row's own text above; the trigger, the group
expression and the step name are quoted from `ci.yml` at `203dec8`. The filing Source above covers
the filing only — it predates this block and does not vouch for it.`

**DONE 2026-08-22, on Done-when's FIRST disjunct, both halves.** The disjunction is quoted whole
above. The second disjunct is not taken: harness `CLAUDE.md` §CI contract is unchanged and still
opens *"Every change must pass all of these before merge"* over the same seven commands. The first
is taken, and it has two halves that closed a few hours apart.

**Half one — the trigger.** Harness `203dec8` adds

```yaml
  push:
    branches: [main]
```

scoped to `main` rather than to every branch, for the reasons recorded in the file's own comment
and in the `2026-08-22` block above.

**Half two — one run on the record proving it fires.** Run **`32563924592`**,
<https://github.com/vishal-h/aetheris/actions/runs/32563924592>, created `2026-08-22T09:03:37Z`:
**event `push`, branch `main`, sha `203dec8`, conclusion `success`**, both jobs green — `check`
`09:03:41Z → 09:09:53Z`, `sandbox` 1m26s with its named skip. This is the first push-triggered run
in the repository's history; the row was filed on the fact that the last run of any kind was
`2026-05-17T14:10:29Z`.

**It fired on the commit that added it, so no second push was needed.** GitHub reads the workflow
file from the pushed head, so `203dec8` — the commit introducing `push:` — is itself the commit
that triggered under it. The sha in the run record and the sha of the trigger commit are the same
object, `203dec8ffdf4e550b1a0517a133f951e16d56a69`. A reader expecting the first run to come from
the *next* commit will not find one, and that is not a gap.

**The gate the row was really about is now enforced by a machine.** Six of the §CI contract's seven
commands ran in that job, in order, all green; the seventh is `mix hex.audit`, which ran as step 9
under the advisory ruling recorded on **BL-169**. For the 371 commits this row counted, enforcement
was a human typing them.

**TWO THINGS THIS DISPOSITION CARRIES, neither of them a Done-when item.**

**(a) The conditional `cancel-in-progress` is EVALUATED, NOT DEMONSTRATED.** The concurrency block
landed in the same commit because shipping the trigger without it was a defect —
`group: pr-${{ github.event.pull_request.number }}` yields `pr-` on every non-pull-request event,
so every push run would have joined one group. The replacement groups a push run per ref and sets
`cancel-in-progress: ${{ github.event_name == 'pull_request' }}`. **One push happened, so no
competing run ever existed and nothing has watched a second push queue behind a first.** The
expression was evaluated against GitHub's documented semantics — its expressions reference lists
`null` among the falsy values, and its workflow-syntax reference prescribes exactly this `||`
fallback for a property defined only on some events — and the group value is not readable after the
fact either: `gh api repos/vishal-h/aetheris/actions/runs/32563924592 --jq 'keys'` returns 35 keys
and none is a concurrency or group field. **This does not hold the row open.** It is written here
so that a later reader who sees two pushes both complete knows nobody has yet watched that happen,
and does not mistake the absence of a report for a report of absence.

**(b) The runner's shell is corroborated; the red arm's CONTENT is not.** The run's log records
`shell: /usr/bin/bash -e {0}` for the `hex.audit` step — the same interpreter and the same `-e`
flag the local two-arm exercise used. That is what the step's `set +e` / `status=$?` / `set -e`
construction depends on, and it is no longer an assumption about the runner. **State precisely what
remains: not the shell, and not the exit-code arithmetic — only the `else` branch's own content,
which has never executed anywhere.** The lock is green at `bandit 1.12.5`, so on the runner and in
the local exercise the `status -eq 0` arm ran, and the text under
`### Supply-chain audit: ADVISORIES FOUND` has been read by no reader of a real run. That remainder
belongs to **BL-169**'s stated closing condition — the first real red after this lands — and this
narrowing refines that condition's subject without reopening it or contradicting it.

`Source: BL-172's own close, 2026-08-22, at harness `203dec8` / agents at the commit carrying this
disposition. The run's fields are from `gh run view 32563924592 --json event,headBranch,headSha,conclusion,url`;
the step name, its ordinal and the shell line are from that run's `check` job log. The Done-when is
quoted from this row's own text above.`

---

### BL-173 — `ci.yml` caches two paths that do not exist, and the cache step reports nothing (#TBD)
**Status:** DONE
**Kind:** bug · **Census items:** n/a · **Contract:** n/a
**Size:** S · **Priority:** low
**Section:** harness (`../aetheris/.github/workflows/ci.yml`)

Filed 2026-08-22 at **BL-172**, which read the file line by line to add a trigger and found these
beside the lines it was changing. **Reported, not fixed** — BL-172's ruling was that the trigger,
the concurrency group and `hex.audit` land and nothing else does. This row exists because BL-172
and **BL-169** both close their own questions and neither can hold this one: a finding recorded
inside a row that is being disposed has a record and no executor. **Both of those rows are now
DONE and live in `docs/backlog-2026-06-closed.md`** — BL-169 at the commit that filed this row,
BL-172 at the one that closed it on run `32563924592`. The id is the address, so the references
above resolve there and nothing here reopens either. This row is the executor that outlived them,
which is the reason it was filed separately.

**The two paths, at harness `203dec8`.**

| path | cache step | state | command |
|---|---|---|---|
| `native/aetheris_nif/target` | `Cache Cargo` | the directory was deleted on 2026-05-20 | `git -C ../aetheris log -1 --format='%h %ad %s' --date=short -- native/aetheris_nif` → `e977af0 2026-05-20 Remove Rust NIF and replace with pure Elixir equivalents` |
| `priv/plts` | `Cache Dialyzer PLTs` | never existed in the tree | `git -C ../aetheris ls-files priv/plts` → nothing; `ls ../aetheris/priv/` lists no `plts` |

`e977af0` is **three days after** the last workflow run that could have exercised the file
(`2026-05-17T14:10:29Z`, `gh run list`), which is the whole reason nothing noticed.

**Neither is load-bearing, and that is the finding rather than a mitigation.** Both cache steps
list other paths that do exist — `~/.cargo/registry` and `~/.cargo/git`, and
`~/.mix/dialyxir_*.plt`, which is where dialyxir actually writes, `mix.exs` declaring
`dialyzer: [plt_add_apps: [:mix]]` and no `plt_file`. `actions/cache@v4` skips a missing path
silently, so the steps save and restore from the surviving paths and report nothing. Read from
the run of 2026-08-22 (`gh run view --job=96984722921 --log`): `Post Cache Cargo` ends
`Cache saved with key: Linux-cargo-e6bffd8c…` and `Post Cache Dialyzer PLTs` ends
`Cache saved with key: plt-Linux-v1.17.2-otp-27-OTP-27.0.1-…`, with no warning in either about a
path it could not find.

**So the cost is not a broken cache. It is a declaration that has been wrong for three months
with no instrument that could say so** — the same shape as the gate declarations collected on
**BL-150**, one layer down: the file states what it caches, the statement is false, and the tool
is designed to be quiet about exactly this.

**Done when:** both paths are decided — removed, or replaced with the path that was meant — and
the decision is recorded. Removing `native/aetheris_nif/target` is the obvious call and
`priv/plts` needs a reading of whether a repo-local PLT directory was ever intended; if it was,
the fix is `mix.exs`, not the workflow.

**Costs:** S. Two lines, and one question about `priv/plts` that the workflow cannot answer alone.

**Collides with:** **BL-174**, which owns `native/aetheris_nif` in the documentation. The cache
path here is a member of that census and is disposed by this row rather than that one, because
its failure mode is a silent cache miss and theirs is an operator following an instruction into a
directory that is not there. The rows cross-reference; neither waits for the other.

`Source: BL-172, 2026-08-22, derived at harness `203dec8` / agents at the commit carrying this
row. Every figure above carries its command. The absence of a warning is read from the run's own
log rather than inferred from `actions/cache`'s documentation.`

**DONE 2026-08-22** at harness `7ccfc6a`, in one commit with **BL-174**'s instruction-surface
sweep — the two rows share a census member (`native/aetheris_nif/target` is a cache path here and
a census hit there) and both are harness documentation-and-config edits.

**Done-when, quoted from this row above:** *"both paths are decided — removed, or replaced with
the path that was meant — and the decision is recorded. Removing `native/aetheris_nif/target` is
the obvious call and `priv/plts` needs a reading of whether a repo-local PLT directory was ever
intended; if it was, the fix is `mix.exs`, not the workflow."* Both clauses are discharged below;
the decisions are recorded **in `ci.yml` itself**, beside the steps they govern, rather than only
here.

**`priv/plts` — removed, and the reading the Done-when asked for is: never intended.** Not stale;
never true. It has been in the file since its first commit (`0982a74`, 2026-05-15) and no commit
on any branch has ever contained `plt_local_path` or `plt_file` —
`git -C ../aetheris log --all -S'plt_local_path' -- .` and the same for `plt_file` both return
nothing, against the positive control `git -C ../aetheris log --all -S'plt_add_apps' -- .` which
returns `56a79ea 2026-05-11`. So it is the cache half of the standard dialyxir recipe whose
`mix.exs` half was never written, and the Done-when's conditional — *"if it was, the fix is
`mix.exs`"* — does not fire. Removing the path IS removing the intent, because no intent was ever
recorded.

**`native/aetheris_nif/target` — removed, and it went stale in two steps, not one.** This row's
body reads the deletion (`e977af0`, 2026-05-20) as the staling event. It is the second one.
`190eb39` (2026-05-17T14:43:52Z) made `native/` a cargo workspace, and a workspace member's build
output goes to the shared `native/target`, so the path stopped naming cargo's output three days
before the crate was deleted. That is **33 minutes after** the last workflow run before this month
(`2026-05-17T14:10:29Z`, run `25993150988`, and `190eb39` is not an ancestor of that run's
`80a846b`) — so no run ever executed against the workspace with this path in the file. The row's
*"three days after the last CI run"* is correct about the deletion and understates how quickly the
declaration went wrong.

**`native/target` is deliberately NOT added in its place**, and the omission is recorded in
`ci.yml` so it does not read as the same oversight repeated. Removing a path that names nothing
and adding one that caches real build output are different changes with different justifications;
the second is a performance change owing its own measurement, and this row is about declarations
that are false.

**The silence this row filed is confirmed, and more precisely than the body states.** Both paths
appear in the logs of both 2026-08-22 runs exactly twice each — as the action echoing its own
`with:` inputs (`path: priv/plts`, `native/aetheris_nif/target`), never as a warning. No line in
either log names a path the action could not find. The body's quoted `Cache saved with key:` lines
are from run `32553802996` (job `96984722921`, the `workflow_dispatch`), which was the cold-cache
run; the push run `32563924592` reports `Cache hit occurred on the primary key …, not saving
cache.` for both steps. Neither warns.

**A check was built for this edit and mutation-tested.** It parses `ci.yml` and reports any
`actions/cache` path that is neither a `~`-rooted runner path nor present in the tree. Against
`203dec8` it reports both paths; against `7ccfc6a` it reports none; re-adding both to the working
copy makes it fail naming both, and the restore was from a sha-verified working-copy backup with
the mutation confirmed absent afterwards. It is a scratchpad instrument, not committed — wiring a
standing gate for phantom workflow paths is not this row's, and is not filed as one.

**What this row does NOT close.** The `check` job's own gate set still disagrees with every other
surface that declares one; that is **BL-150**'s, and no row owns the reconciliation. And the first
push-triggered run after this commit is the evidence that the workflow still parses and both cache
steps still restore and save — the arbiter pushes, per the ticket's ruling.

`Source: this ticket, 2026-08-22, at harness `7ccfc6a` / agents at the commit carrying this
disposition. Every figure above carries the command that produced it. The two-step staling and the
33-minute gap are new findings of this close, derived from `git log -1 --format='%h %aI %s'
190eb39`, `git merge-base --is-ancestor`, and `gh run list`; they refine this row's body rather
than contradict it.`

---

### BL-174 — the `aetheris_nif` removal was never swept out of the documentation, and one of the surfaces is read by an agent (#TBD)
**Status:** DONE
**Kind:** bug · **Census items:** five surfaces, enumerated below · **Contract:** n/a
**Size:** S · **Priority:** medium
**Section:** harness (`../aetheris/README.md`, `../aetheris/.github/copilot-instructions.md`, `../aetheris/docs/aetheris/test-plan.md`, `../aetheris/docs/aetheris/notes-m09.md`, `../aetheris/docs/aetheris/milestones/m10-autonomous-agent-tooling.md`)

Filed 2026-08-22 at **BL-172**, from the same reading that produced **BL-173**. **BL-172 is now
DONE and lives in `docs/backlog-2026-06-closed.md`**, closed on run `32563924592`; the id is the
address, so that reference resolves there, and this row stays open on its own terms. **Reported,
not fixed.** `e977af0` (2026-05-20) deleted `native/aetheris_nif/` and removed the `rustler`
dependency; `mix.exs` names neither and `lib/aetheris/nif.ex` is gone
(`git -C ../aetheris ls-files lib/aetheris/nif.ex` returns nothing). The documentation was not
swept with it.

**The census**, at harness `203dec8`, from
`git -C ../aetheris grep -c 'aetheris_nif' -- .` — which returns hits in eleven files, of which
`docs/aetheris/milestones/remove-nif.md`, `remove-nif-implementation-notes.md`,
`m01-core-harness.md` and `m03-replay-diff.md` are records of what a past ticket did and are
**correctly** left alone, `.github/workflows/ci.yml` is **BL-173**'s, and one is not a document at
all — `aetheris`, the committed escript binary, carries the string in compiled data and is out of
scope here for that reason rather than by judgement. The remainder are standing surfaces that
instruct a reader:

| surface | what it says | who reads it |
|---|---|---|
| `README.md:143`, §*Running checks* | `cd native/aetheris_nif` then three `cargo` commands | anyone following the README's own check list |
| `README.md:115`, §*Project structure* | lists `native/aetheris_nif/` and `nif.ex  Rustler NIF wrapper` | the same reader, one section earlier |
| `.github/copilot-instructions.md:43-45` | *"For any change touching `native/aetheris_nif/`"* + the same `cargo` chain | **a coding agent**, not a person |
| `.github/copilot-instructions.md:15` | describes the project as having a Rust NIF crate | the same agent, as orientation |
| `docs/aetheris/test-plan.md:37,94,98` | a Rust unit-test section, a `cargo test` line, and an *"All checks"* chain ending in the deleted directory | a ticket author deciding what to run |
| `docs/aetheris/notes-m09.md:91` | the same `cargo` chain | m09's reader |
| `docs/aetheris/milestones/m10-autonomous-agent-tooling.md:868` | `cd ../aetheris_nif && cargo …` inside an instruction block | m10's reader |

**Why this is worth a row when the failure is loud.** `cd` into a directory that does not exist
fails immediately, so a human hits it and works around it. The `copilot-instructions.md` surface
is the exception and is the reason for the **medium** rather than low: it is read by a coding
agent as standing instruction, and an agent that cannot find the directory has no author to ask —
it improvises, or it reports a check it did not run. **BL-150**'s standing subject is documents
that say what the tree does not; this is that class with an agent as the reader.

**And it is a worked instance of the vocabulary-sweep rule** in harness `CLAUDE.md` — *"a
vocabulary change owes a sweep of everything that speaks it, in the same commit"*. `remove-nif.md`
lists *"Remove the `native/aetheris_nif/` subtree from the Project structure section"* as a
deliverable, so the sweep was scoped to the README's structure list and not to the class; the
structure list still names it anyway.

**Done when:** each surface above is either corrected or marked as historical, with the choice
recorded per surface, and a re-run of the census command returns only the records deliberately
left. `README.md` §Project structure also names `nif.ex`, which is a second deletion the same
commit made and the same sweep missed — it is in scope.

**Costs:** S. The judgement is per-surface: which of these are records and which are
instructions, and `m10-autonomous-agent-tooling.md` is the ambiguous one.

**Collides with:** **BL-173**, which holds the `ci.yml` cache path from the same census. **BL-150**
carries the gate-declaration append that found three of these surfaces, and settles nothing.

`Source: BL-172, 2026-08-22, derived at harness `203dec8`. The census command and its output are
above; the control that it is not blind is the same command for `aetheris_exec_server`, which
returns hits in `.gitignore`, `CLAUDE.md` and `docs/aetheris/advanced-git-tools.md` among others.
Line numbers are from that commit and are cited with their sections, which survive an insert.`

---

**PARTIAL 2026-08-22 at harness `7ccfc6a` — the three INSTRUCTION surfaces are corrected; this row
stays OPEN because two surfaces are referred to the arbiter and its Done-when requires a choice
recorded for *each*.**

**The triage test, stated before it was applied.** Does the document address a reader in the
present about what to do now, or does it describe what a past ticket asked for at its own time?
Present-tense standing guidance whose audience is *whoever is working now* → INSTRUCTION, fixed.
A dated unit of past work — a milestone ticket, its notes, its implementation record — whose
audience is that unit's reader → RECORD, not edited. A compiled binary → ARTIFACT. A dated record
carrying a present-tense instruction block → BOTH, referred.

| surface | class | disposition |
|---|---|---|
| `.github/copilot-instructions.md` §Repository context, §Full check suite, §Rust standards | INSTRUCTION | **fixed** |
| `README.md` §Project structure, §Running checks | INSTRUCTION | **fixed** |
| `docs/aetheris/test-plan.md` §1 table, §2, §Commands | INSTRUCTION | **fixed** |
| `.github/workflows/ci.yml` | INSTRUCTION (to a machine) | **fixed under BL-173**, closed |
| `docs/aetheris/milestones/m01-core-harness.md` | RECORD | not edited |
| `docs/aetheris/milestones/m03-replay-diff.md` | RECORD | not edited |
| `docs/aetheris/milestones/remove-nif.md` | RECORD | not edited |
| `docs/aetheris/milestones/remove-nif-implementation-notes.md` | RECORD | not edited |
| `aetheris` (committed escript) | ARTIFACT | not editable; see below |
| `docs/aetheris/notes-m09.md:91` | **BOTH** | **referred — not decided** |
| `docs/aetheris/milestones/m10-autonomous-agent-tooling.md:868` | **BOTH** | **referred — not decided** |

**Why the two are referred rather than ruled.** Both are dated records carrying a live-shaped
instruction block. `m10` sits in the same directory as `m01` and `m03`, which this row rules
correctly-left-alone, and this row's own Costs line already calls it *"the ambiguous one"*; ruling
it INSTRUCTION would require a reason that does not also reach `m01` and `m03`, and none was found.
`notes-m09.md` is the same shape one level down — a milestone's notes file, opening *"Architecture
call:"* and *"Worth knowing ahead of T5"*, with one `cargo` chain inside it. The choice is
available and cheap either way; what is not available is making it silently, so it is named here
with an executor rather than left in a packet.

**The escript, stated so it is not re-triaged.** `aetheris` is a committed escript — a zip archive
whose entry table contains `aetheris_nif.so`, embedded when it was built at `f43c905`
(2026-05-16), four days before the crate was deleted. It is not a document, carries no instruction,
and no text edit reaches it. Separately: it is a build output committed to the tree and three
months stale, which is a different defect from this row's and is **not** filed here.

**The census is short — extended, not corrected.** Following this row's own vocabulary-sweep
argument, the class is *the `e977af0` deletion*, and `aetheris_nif` is only one token that speaks
it. `e977af0` also deleted `lib/aetheris/nif.ex` and removed the `rustler` dependency, so
`git -C ../aetheris grep -niE 'rustler|rust nif|nif crate|nif\.ex|NifResult'` reaches surfaces the
row's command cannot. Run at `7ccfc6a`, the ones **still standing and not covered above** are:

- `docs/aetheris/specs.md` §10 *Rust NIF Interface* — a standing specification, present tense,
  giving the full `defmodule Aetheris.NIF` signature block for a module deleted at `e977af0`, plus
  two `**Constraint:**` lines about NIF scheduling. This is INSTRUCTION-class by the test above and
  is the largest single surface the token census missed.
- `.gitignore:22` — `# Rust build output (compiled by Rustler at mix compile time)`, and `:25`
  `# Compiled NIF binaries (generated, not source)` over `/priv/native/`. The patterns still do
  useful work; the comments describe a mechanism that no longer exists.
- `docs/aetheris/milestones/milestone-reference.md:7` — RECORD (m03's row, what m03 built).
- `mix.lock:23` still carries a `rustler` entry at `0.37.3` — a resolved dependency for a package
  absent from `mix.exs` since `e977af0`, and `deps/rustler` exists in the working tree. **Not
  documentation**, so out of this row's class entirely, and named here only so the finding has a
  home; `mix deps.unlock --unused` is the shape of it.

**Not swept, deliberately, and named so the omission is visible:** the gate-set enumerations on
every page this ticket touched are left unreconciled. `README.md` §Running checks still declares
four `mix` commands, `test-plan.md` two disagreeing sets on one page, `.github/copilot-instructions.md`
five. That is **BL-150**'s standing subject and its 2026-08-22 append says in terms that reconciling
them *"is not filed as a row here either"*. This ticket removed the `cargo` tails that were false
and touched nothing else in those lists.

**Done-when, restated against what is left.** *"each surface above is either corrected or marked as
historical, with the choice recorded per surface"* — nine of eleven done, two referred.
*"a re-run of the census command returns only the records deliberately left"* — at `7ccfc6a` the
command returns the four records, the escript, the two referred surfaces, and one sentence in each
of the four fixed files recording what was removed and why. Those sentences are a category the
Done-when did not anticipate; they are deliberate, and removing them to satisfy the clause
literally would delete the record the clause exists to produce.

`Source: this ticket, 2026-08-22, at harness `7ccfc6a` / agents at the commit carrying this append.
The triage test is stated above and was applied to all eleven hits. The extended census is
reproducible by the command quoted in it; its positive control is the same command and flags for
`aetheris_worker`, which returns hits across the tree rather than nothing. **No count is given
here deliberately** — the first draft of this sentence said *45 files*, and this ticket's own
commit made it 46 by adding one `aetheris_worker` mention to `README.md`. A control figure over a
set the commit is editing is falsified by that commit; the command is the durable form.`

**DONE 2026-08-23 at harness `a49d05a`** (stage 2), the stage that discharged the arbiter's ruling
on the two referred surfaces, repaired the surface stage 1 found and did not fix, and gave the
findings stage 1 had only named an executor each. Stage 1 is harness `7ccfc6a` / agents `b3b6069`,
both on origin, with run **`32611562210`** green on `7ccfc6a`.

**The ruling, and why it is the right one.** `docs/aetheris/notes-m09.md` and
`docs/aetheris/milestones/m10-autonomous-agent-tooling.md` are **RECORD**. Stage 1 could not find a
discriminator between them and the three surfaces it fixed, and the finding is that there is none
of the kind it was looking for: every dated ticket document carries imperative prose, so
"contains an instruction block" promotes `m01`, `m03`, `remove-nif` and
`remove-nif-implementation-notes` too, and this row becomes a rewrite of the milestone archive
that its own RECORD ruling refuses. The discriminator is **ARRIVAL**. A reader reaches
`CLAUDE.md`, `README.md` and `.github/copilot-instructions.md` without having chosen a subject; a
reader reaches a dated milestone document only by choosing it. Repairing arrival points is bounded
by the number of entry points; repairing records is bounded by the number of past tickets, which
only grows.

**C1a — the class-level sentence was WIDENED, because its own words did not reach the surface the
ruling was about.** As committed at `7ccfc6a` it read *"If you are reading a **milestone document**
that instructs you to build or check a NIF, that document is a record of past work and not an
instruction to you."* `notes-m09.md` sits at `docs/aetheris/notes-m09.md`, **not** under
`milestones/`. Semantically it is a document about milestone 09; by location it is not a milestone
document, and a reader resolving the phrase by location would have excluded exactly the file the
ruling names. Ambiguity in the instrument is the thing worth removing, so the sentence now binds
*"any document"*, enumerates where records live — the milestone tickets, their implementation
notes, and the loose per-milestone notes files directly under `docs/aetheris/` — and names
`notes-m09.md` explicitly.

**C1b — the sentence is now in every arrival surface, and the set was established rather than
assumed.** `.github/copilot-instructions.md` is Copilot's, not what a Claude session reads.

| file | how it was established | before |
|---|---|---|
| `CLAUDE.md` | self-declares mandatory: *"Read this file in full before touching any code"* | absent — added |
| `.github/copilot-instructions.md` | GitHub's own convention; opens *"Before writing any code, read `CLAUDE.md` in full"* | present since `7ccfc6a` |
| `README.md` | the repo front door; the surface stage 1 already classed INSTRUCTION on this same arrival criterion | absent — added |

**Excluded, with the reason**: `AGENTS.md` does not exist (`git -C ../aetheris ls-files AGENTS.md`
is empty) though `README.md` §Project structure still names it — a stale structure entry, not this
row's; `docs/aetheris/elixir-agent-instructions.md` is titled `# AGENTS.md` and addresses AI agents
but governs a **`scheduler` service**, and `git grep` finds nothing pointing at it;
`docs/aetheris/playbook.md` is linked from README's document list rather than made mandatory, and
carries no NIF content at all. Each placement is in its own file's voice, not a pasted duplicate.

**C2 — `specs.md` §10 is repaired, not deferred.** It was the largest instruction-class instance of
this row's own subject, and closing the row while it waited for another row would have reproduced
the defect this row names: a complete-looking claim produced by a narrow instrument. §10 is
repointed from *Rust NIF Interface* to *Hashing and Diff Primitives*, read from the code:
`hash_content/1` is a private helper inlined in three modules (`git -C ../aetheris grep -n 'defp
hash_content' -- lib/` → `Eval.Runner`, `Execution.Loop`, `Skill.Extractor`), `byte_identical?/2`
was dropped with no replacement, and `diff_text/2` is a pure-Elixir Myers diff inside
`Trajectory.Diff` whose public `enrich_hunks/1` is unchanged. Two dependents are **named, not
edited** — §5's *"skips word-diff NIF enrichment"* and §14's *"NIFs must not block the scheduler"*.
`docs/aetheris/determinism-contract.md` does **not** depend on §10: zero hits for
NIF/rustler/hash_content/byte_identical, against positive controls of 2 for `hash` and 9 for
`determinis` on the same command and flags.

**C3 — the two `.gitignore` comments are corrected and NO pattern is touched**, verified by diffing
the comment-stripped file against `HEAD`: identical. `/priv/native/` can no longer be produced by
anything, so the comment says so and the pattern stays, because a stale
`priv/native/aetheris_nif.so` survives in working copies predating the deletion.

**C7 — how the Done-when's census clause is satisfied, stated so a later reader does not take it
literally.** The clause reads *"a re-run of the census command returns only the records
deliberately left"*. It is satisfied by **every hit having a recorded class**, not by the token
being absent. The census at `a49d05a` returns the four milestone records, the escript, the two
surfaces ruled RECORD here, and one or two sentences in each of `ci.yml`, `README.md`,
`CLAUDE.md`, `.github/copilot-instructions.md`, `.gitignore`, `docs/aetheris/specs.md` and
`docs/aetheris/test-plan.md` that exist **because** of this row — they record what was removed and
why, and they are the class-level statement the ruling asked for. **Deleting them would satisfy the
clause literally and destroy the record it exists to produce.** Note that `CLAUDE.md` and
`.gitignore` did not carry the token before and now do; that is deliberate, and is the same
category as the four sentences stage 1 added.

**What this row did NOT do**, each with its executor:

| finding | executor |
|---|---|
| a standing gate for phantom workflow cache paths | **BL-175** |
| `aetheris`, a stale committed build output | **BL-176** |
| `mix.lock`'s unused `rustler` entry | **BL-177** |
| no `cargo` gate against the two surviving crates | **BL-178** |
| every CI job forced off a deprecated Node runtime | **BL-179** |
| the gate-set declarations disagreeing across nine surfaces | **BL-150**, and no row owns reconciling them |
| the CI `sandbox` job passing without running the set | **BL-048**, which is UNRULED and already owns it |

`Source: BL-174 stage 2, 2026-08-23, at harness `a49d05a` / agents at the commit carrying this
close. Every figure carries its command. The arrival set, the §10 dependents and the
`determinism-contract.md` negative were derived at this stage, not inherited.`

---

### BL-182 — recorded commands name `grep`, and the shell decides what `grep` is (#TBD)
**Status:** DONE
**Kind:** bug · **Census items:** n/a · **Contract:** n/a
**Section:** both repos — every tracked document carrying a re-runnable command
**Size:** M · **Priority:** medium

Filed 2026-08-23 at **BL-181**'s filing round, under the standing rule that a deferred finding
gets a row in the round it is deferred. **This row measures. It repairs nothing**, and it does not
close on the disagreements it finds being repaired — that is a later row this one sizes.

**The subject.** A recorded command is written into a tracked document as something a reader may
re-run: a Source line, a Done-when clause, a census command, a positive control, a step in an
operator procedure. Such a command names `grep`, and a shell resolves a bare name from ambient
state. The verification its author ran therefore does not predict what its reader gets, and
nothing in the command says so.

**The instance is established and is not restated here: BL-180 clause 3.** Two commands written
with a PCRE escape returned different results under the shell's `grep` and under
`/usr/bin/grep` — silently, with empty stderr and no warning. Read that row for the evidence.

**What this environment actually resolves, established at this filing rather than carried from a
prior packet.** `type -a grep` reports a **shell function** shadowing `/usr/bin/grep`; the function
dispatches to the Claude Code binary invoked as **ugrep** (`ugrep 7.8.4`), while `/usr/bin/grep` is
**GNU grep 3.7**. `find` is shadowed the same way onto **bfs**. `sed`, `awk` and `git` are not
shadowed. The full set of binary-shadowing functions is `grep`, `find` and `pkill`, from
`declare -F` cross-checked against `type -a`. The functions are **injected into the Bash tool's own
shell** — they appear in no dotfile and are not exported, so `bash -lc 'type -t grep'` reports
`file`. Two readers of the same recorded command therefore get different programs depending on
where they paste it, and neither is told.

**Note that `grep --version` does not answer this question.** It reports whatever ran. Here it
happens to print `ugrep`, which discloses the substitution by accident of that tool naming itself;
a wrapper that forwarded `--version` would not. `type -a` is the question's actual instrument.

**Scope of the measurement.** Every tracked `*.md` in both repositories — a superset of the named
scope (both backlog files, the ruling registry, the manifest, both `CLAUDE.md`, the operator
procedures under `prompts/`, and the harness documents the BL-174 arc touched), derived by one
rule rather than assembled by hand, from `git ls-files '*.md'` in each repo.

**The partition, reported as classes.** Occurrences of a shell-resolved tool name fall into
**git-subcommand** (`git grep` — git's own engine, unaffected by a shell function),
**absolute-path** (`/usr/bin/grep` — names the binary), **command-builtin** (`command grep` —
bypasses the function), and **bare-name** (the affected class). Only bare-name is affected.
**The absolute-path class is empty in the corpus** — no tracked document names the binary — and
that negative is a searched one: the extractor's control proves the class would have been
reported had a member existed.

**What was run.** Every bare-name `grep`/`find` command that is self-contained — a real operand,
balanced quoting, not a prose fragment, no destructive construct — was run **both ways** from its
own document's repository root: once with the shim functions in force, once with the bare name
resolving through `PATH` to the GNU binary. Comparison is over stdout as a set, exit code and
stderr. The classes found: **agrees on all three**; **same result set, different exit code**;
**different result set**; and **one side did not return within the cap**.

**The disagreements that are properties of the corpus rather than of the extractor:**

- **A census command whose filter silently stops working.** `docs/milestones/ds-milestone.md:290`
  pipes a recursive search into `grep -v '^docs/backlog-2026-06\.md:'`. ugrep emits paths
  unprefixed; GNU grep emits them `./`-prefixed, so the anchored filter matches under one and not
  the other. The command returns **31 lines under the shim and 33 under the binary**, reproducibly,
  **both exiting 0 with empty stderr**. A reader re-running the census gets a different population
  and no signal that they have.
- **An exit code that flips.** `cloudcost/docs/m5-obligation-landing-implementation-notes.md:124`
  runs a recursive search across both repositories. Both tools return the same ten lines; the shim
  exits **0** and the binary exits **2**, because GNU grep descends into `../aetheris/priv/runs/`
  and hits `Permission denied` where ugrep does not. Anything keying on exit status reads success
  under the author's shell and failure under a reader's.
- **Traversal order.** `find -printf` at `cloudcost/docs/m5-t1-implementation-notes.md:635`
  returns the same entries in a different order under bfs and under GNU find. A recorded command
  whose result is taken from the head of the output is order-dependent and does not survive the
  substitution.

  > **[Corrected 2026-08-23 at this row's close.** This bullet is **wrong** and is withdrawn as a
  > corpus finding. The tool difference is real — bfs and GNU find do walk in different orders — but
  > the **site is not a recorded command.** `m5-t1-implementation-notes.md:635` reads *"A `find
  > -printf '%T@ %s %p'` snapshot of both trees was taken before and after the run"*: it is prose
  > describing a procedure, and the two tree operands it names were **dropped by this row's own
  > extractor**, which then ran the operand-less remainder over the whole repository. That is the
  > same over-capture already labelled for the two `m5-t3-implementation-notes.md` entries, and it
  > should have carried the same label. Nothing in the corpus has been shown to depend on traversal
  > order. **No recorded command is repaired on this ground**, and the withdrawal is recorded rather
  > than deleted per **R32**. Found by re-reading the site during this round's check of the previous
  > round's claims. **]**
- **A latency class that is not a content class.** Path-less recursive searches return promptly
  under the shim and can take minutes under the binary, which walks `_build`, `deps`, `.git` and
  `node_modules` that the shim's ignore handling skips. The one member settled under a generous
  cap — `grep -rn "caused_by"` at `docs/rig/milestones/bl-007/bl-007-t0-caused-by.md:6` — **agreed
  on content**, both returning the same result set. The rest are **unsettled at the cap this round
  used**, and that is the recorded result rather than a check still owed.

  > **[Corrected 2026-08-23, hours after this row was committed at `7d9cf69`.** The sentence above
  > says *"the one member settled under a generous cap"*. That was false when written: **five**
  > members of this class settled, not one, and **every one of them agreed on result set and exit
  > code** — four at a 90-second cap (`grep -rhoE "BL-[0-9]{3}" . ../aetheris/ ...` at
  > `cloudcost/docs/m5-obligation-landing-implementation-notes.md:244`, and three searches under
  > `provenance/` at `docs/reviews/provenance-scout-2026-08-03.md:422`, `:475` and `:683`), plus
  > `caused_by` at a 900-second one. **Six** remain unsettled, not the rest. The correction
  > **strengthens** the claim the paragraph is making rather than weakening it: wherever this class
  > has been settled at all, it has been a latency difference and not a content one. **How the
  > error was made, because it is this row's own subject in miniature:** the tally was read from a
  > results file **while the job writing it was still running**, so a partial capture was taken for
  > a complete one — the same defect the repo's packet rules name, and indistinguishable from a
  > complete result by content alone. The full file was re-read after the job exited. Corrected in
  > place per **R32**; the original sentence is not rewritten. **]**


> **[Settled 2026-08-23 at this row's close, and the bullet above is partly wrong.** All six
> members left unsettled were re-run both ways at a **900-second cap per side**, backgrounded with
> incremental output. **All six settled; none hit the cap.** Four agree on result set and exit
> code:
>
> ```
> cloudcost/docs/t1b-implementation-notes.md:47         grep -rln 'aetheris --json'                    15 = 15 lines, rc 0 = 0
> docs/backlog-2026-06.md:7028                          grep -rn 'aetheris_run_id'                      24 = 24 lines, rc 0 = 0
> docs/reviews/bl-039-review.md:100                     grep -rni "thinking|budget_tokens"               1 =  1 line,  rc 0 = 0
> docs/rig/milestones/bl-007/bl-007-t0-caused-by.md:6   grep -rn "caused_by"                            61 = 61 lines, rc 0 = 0
> ```
>
> **Two disagree, on content**, so *"a latency class that is not a content class"* is **false as a
> claim about the whole class** and is corrected here rather than rewritten:
>
> ```
> cloudcost/docs/m6-t2c-implementation-notes.md:351     grep -rn "evaluation_coverage\|uncatalogued"   shim 113, binary 125, both rc 0
> docs/reviews/provenance-scout-2026-08-03.md:494       grep -rn "tool_result\|payload_json"           shim 288, binary 352, both rc 0
> ```
>
> **The mechanism is a third one, distinct from either repaired above.** In both cases the shim's
> result is a strict subset — nothing is found only by the shim — and every extra line the binary
> returns comes from a directory the shim's ignore handling skips and git does not track:
> `cloudcost/.pytest_cache/`, `rig/dist/`, `rig/node_modules/`. So the divergence is not a broken
> filter and not an unreadable directory; it is **which files the walk is willing to enter**. Both
> sides exit 0 with empty stderr, so a reader is told nothing here either.
>
> **Neither is repaired**, and the reason is scope rather than judgement: this closing round was
> scoped to the two repairs above and forbidden from filing further rows. They are recorded here
> so that a later reader knows they exist and knows that nothing is tracking them. The discipline
> below is what stops more of them being written. **]**

**Done when** — all three:

1. Every affected recorded command has been run both ways and the result recorded, including the
   members left unsettled by this round's cap.
2. The disagreements are listed with the document each lives in.
3. A discipline is stated for commands written from here on.

**It does NOT close on the disagreements being repaired.** Repair is a separate row, which this
one exists to size.

**The candidate disciplines, recorded without choosing among them:**

- Verify each recorded command against the binary before committing it.
- Prefer `git grep` in recorded commands, whose engine is unambiguous.
- Remove the shadowing, so a bare name means one program.

A fourth may be better than any of these. **The choice depends on a decision the arbiter owns
about the environment** — whether the shadowing stays — and under **R35** this row reserves that
choice rather than referring it as a decision for now: it is a choice the Done-when requires be
made with evidence the row has not yet produced, and deciding it in prose is the close the
Done-when refuses arriving by another route.

**THE DISCIPLINE, CHOSEN AT THIS CLOSE. This supersedes the three candidates above, which stay
as the record of what was weighed.** The evidence the Done-when required has now been produced,
so the choice is made here rather than reserved:

> **A recorded command must name the program it runs.**
>
> 1. **`git grep` where the search is over tracked files**, which is most of them. Git's search
>    engine is not reached through a shell name, so the command means one thing for everybody.
>    Both repairs in this round took this form, and both went from divergent to byte-identical.
> 2. **Otherwise the binary by path** — `/usr/bin/grep` — or a form **verified** to behave
>    identically under both tools, with that verification recorded beside it.
>
> **Neither assumption about the environment is available.** The shadowing is injected by the
> tooling and not by a dotfile, so a reader cannot be assumed to have it, and cannot be assumed
> to lack it either. That is precisely why the discipline binds the *command* rather than waiting
> on a decision about the *environment*: it is correct under either answer, so it no longer
> depends on one. The question the candidates deferred to the arbiter — whether the shadowing
> stays — is not answered here and does not need to be.

**And the third candidate is not adopted.** Removing the shadowing would fix this repository's
authors and nothing else: a document leaving this machine is read wherever it is read, and a
command that names its program survives that. Recorded so the option is not re-proposed as though
it had been overlooked.

**Costs:** M. The measurement is most of it and is largely done; the discipline is the part that
needs the environment settled first.

**Collides with:** **BL-180** (established the instance; its clause 3 is the evidence this row
does not restate). Nothing else — the repair row this one sizes does not exist yet.

`[Both lines above are pre-close statements and are kept unrewritten. The close below supersedes
the second: no repair row follows, and the reason is given there.]`

`Source: this row's own filing, 2026-08-23, at agents da34af1 / harness a4f93e1. The resolution facts are from type -a, declare -F and a bash -lc control run at this filing. The corpus scope is git ls-files in each repo. The disagreements were produced by running each command both ways from its document's repo root and comparing stdout as a set, exit code and stderr; the two named as reproducible were re-run to confirm.`

---

## The close — 2026-08-23

**Done-when clause 1 — the corpus was measured, both ways.** Scope was every tracked `*.md` in
both repositories, from `git ls-files '*.md'` in each — a superset of the named scope, derived by
one rule. 334 distinct (repository, command) pairs were run twice: once with the shim functions in
force, once with the bare name resolving through `PATH` to the GNU binary, each from its own
document's repository root, compared on stdout as a set, exit code and stderr. The extractor
carried an **R34 control** — commands planted inside a fence, inside a blockquote, after a list
marker, split across two lines, and inside a table cell, plus two negative controls — and the
control **caught a real defect in the extractor on its first run**, which was fixed before the
measurement was believed.

**Clause 1's residue is closed.** The six members unsettled at the previous round's cap were
re-run at a 900-second cap per side; **all six settled and none hit the cap**. Nothing in this row
is left unsettled.

**Clause 2 — the partition, as classes.** Occurrences of a shell-resolved tool name fall into
**git-subcommand** (git's own engine — unaffected), **absolute-path** (names the binary —
unaffected), **command-builtin** (bypasses the function — unaffected), and **bare-name**, the
affected class. The **absolute-path class is empty** in the corpus and that negative is a searched
one, not a remembered one — the planted control proves the class would have been reported had a
member existed.

**Clause 2 — the disagreements, with their documents. Four are properties of the corpus, and
three distinct mechanisms produce them.**

| document | mechanism | shim | binary | repaired here |
|---|---|---|---|---|
| `docs/milestones/ds-milestone.md:290` | an output filter anchored at `^docs/`, defeated by GNU grep's `./` prefix | 31 lines, rc 0 | 33 lines, rc 0 | **yes** |
| `cloudcost/docs/m5-obligation-landing-implementation-notes.md:124` | GNU grep descends into an unreadable run directory | 10 lines, rc 0 | 10 lines, **rc 2** | **yes** |
| `cloudcost/docs/m6-t2c-implementation-notes.md:351` | the walk enters ignored, untracked build directories | 113 lines, rc 0 | 125 lines, rc 0 | no |
| `docs/reviews/provenance-scout-2026-08-03.md:494` | the same | 288 lines, rc 0 | 352 lines, rc 0 | no |

**Every one of the four exits 0 on at least one side with empty stderr on both, except the second,
whose whole defect is that the status differs while the output does not.** That is the row's thesis
in one line: nothing in the command, and nothing in the output, tells a reader which program ran.

The remaining disagreements found by the sweep were **artefacts of this row's own extractor** —
prose fragments over-captured as commands — and are labelled as such rather than counted. One of
them, the traversal-order bullet, was published as a corpus finding in error and is withdrawn
above.

**Clause 2 — the repairs, in this commit and not in a row.** Both repaired commands were rewritten
to the `git grep` form, run both ways three times, and returned **byte-identical stdout with
identical md5 and identical exit code on every repeat**. The originals still diverge, which is the
control that the repair is what changed the outcome. Each repair is recorded at its own site as a
dated **R32** note that gives the corrected command and states why the original was wrong when
written; **neither original is rewritten**, and in both cases the figures the original produced
were correct — it was reproducibility that failed, not arithmetic.

**Clause 3 — the discipline is stated above and is chosen, not proposed.**

**No repair row follows, and that is the point rather than an omission.** Two commands in two
documents were two edits, made here. A row to carry them would have been a row that outlived its
own work. The two unrepaired commands are recorded in the settled-latency block above with their
measurement, deliberately in the row's own text rather than in a new row, so that they are
discoverable by anyone reading this one and are not mistaken for tracked work.

**What this row does not claim.** It measured `grep` and `find`, the two shadowed names that
appear in documents. It did not measure `pkill`, the third shadowed name, which appears in none.
It did not survey which shells readers actually use. And of the four corpus disagreements it
established, it repaired two, by the scope stated above.

---

### BL-181 — `coordinator_test.exs:127` failed on CI at harness `a4f93e1` and does not reproduce locally; `main` is red (#TBD)
**Status:** DONE
**Kind:** bug · **Census items:** n/a · **Contract:** harness `CLAUDE.md` §CI contract
**Size:** M · **Priority:** high
**Section:** harness (`../aetheris/test/aetheris/orb/coordinator_test.exs`, `../aetheris/lib/aetheris/orb/coordinator.ex`, and whatever the C4 census reaches)

Filed 2026-08-23 the day it was found, per the standing rule that a red gate gets a tracked
row the day it is found and is never carried silently. Found by the push-triggered run of the
BL-174 arc's final harness commit — off-territory, the way the gate rule intends.

**The run.** `32618789914`, `push`, head harness `a4f93e1`, conclusion **failure**. `sandbox`
green; `check` red. `gh run view 32618789914 --json databaseId,headSha,conclusion,jobs`.

**The failure, from the run's own log rather than a summary:**

```
  1) test step fix — :agent_message_received event carries receiver step from server state (Aetheris.Orb.CoordinatorTest)
     test/aetheris/orb/coordinator_test.exs:127
     Assertion with > failed, both sides are exactly equal
     code: assert received_event.step > 0
     left: 0
     stacktrace:
       test/aetheris/orb/coordinator_test.exs:168: (test)

Finished in 95.1 seconds (6.9s async, 88.1s sync)
972 tests, 1 failure, 133 excluded
##[error]Process completed with exit code 2.
```

The suite total is the same 972/133 as every green run of this arc; one assertion moved.

**NOT caused by the commit that triggered the run, and this is derived rather than assumed.**
`git -C ../aetheris diff --name-only 7ccfc6a..a4f93e1` returns five files —
`.github/copilot-instructions.md`, `.gitignore`, `CLAUDE.md`, `README.md`,
`docs/aetheris/specs.md`. Filtering that list with
`grep -E '^(lib|test|config|native)/|^mix\.(exs|lock)$'` returns **nothing**, exit 1. Neither
the test nor the module under test has moved in three months:
`git -C ../aetheris log -1 --format='%h %ad' --date=short -- test/aetheris/orb/coordinator_test.exs`
gives `4f6a925 2026-05-16`, and the same for `lib/aetheris/orb/coordinator.ex` gives
`4942312 2026-05-19`. The whole BL-174 arc is documentation and workflow configuration.

**NOT REPRODUCED, and the attempts are not evidence.** 16 attempts, 0 reproductions: 10
consecutive runs of `mix test test/aetheris/orb/coordinator_test.exs:127` on an idle machine,
then 6 more under six CPU spin loops — the method BL-135 used. Three full-suite runs during the
same arc reported `972 tests, 0 failures`.

**Those sixteen passes establish nothing about the mechanism and the row says so plainly.** They
are a negative with no positive control: nothing was done to make the failure *possible* in
those runs, so their passing is equally consistent with "the race is rare", "the race cannot
occur on this machine", and "the race is not what happened at all". Counting attempts reads as
diligence and is not; the only thing that separates those three is C3's forced reproduction. Do
not cite the attempt count as evidence of anything but the absence of an accidental repro.

**The reading, offered as a hypothesis and labelled as one.** The assertion requires receiver B
to have advanced past step 0 by the time A's message lands, and `left: 0` says the
`:agent_message_received` event carried step 0 — so the message arrived while B was still in its
first step. On a slower or more contended machine A reaches its `send_message` before B has
advanced. **This is a reading of one line of output. It is not established.**

**Done when — all four, and none of them alone:**

1. **The failure has been produced DELIBERATELY.** Delay or hold receiver B so the message
   provably arrives during step 0, and show the assertion fail on demand. Repetition is not a
   substitute: the mechanism is either forced or unknown. **If forcing it does NOT reproduce the
   failure, the reading above is wrong, and the row records that** — that outcome is worth as
   much as a confirmation and must not be quietly dropped in favour of a second guess.
2. **The census in the next clause has been run**, and the row does not close having repaired one
   assertion while it is unrun.
3. The assertion (or the coordination it tests) is made deterministic, with the fix argued from
   the forced reproduction rather than from the green that follows it.
4. The workflow is green on a commit that carries the fix, with the run id recorded.

> **[Amended 2026-08-23.** Clause 4 as written is the unforced pass this row rejects everywhere
> else in its own text. The row states that sixteen passes establish nothing about the mechanism,
> and that a green re-run answers nothing because it is one more unforced pass — and then takes a
> single green workflow run as its closing evidence. That is the same evidence it has already
> refused, arriving under a different name. **The test of the fix is clause 1's forced
> reproduction, re-run against the repaired code and no longer producing the failure.** A run
> that cannot be made to fail before the repair proves nothing about the repair; one that could,
> and then cannot, is the only thing here that does. **A green workflow run is corroboration
> recorded after that check, with its run id, and is not the check.** Clause 4 is left as written
> rather than rewritten, so a later reader sees both the contradiction and its correction — the
> row's own argument was sound and its closing condition did not follow it, which is worth more
> to that reader than a clause that was always right. **]**

**Is this one test or a class? — the census, and it is a Done-when clause, not a suggestion.**
Two timing-dependent assertions in this suite have now failed under load in three months, this
one and **BL-135**'s. Two is either coincidence or a pattern and the row establishes which. The
census: every assertion in the harness suite whose result depends on elapsed time, or on another
process having advanced, **with nothing synchronising it** — sleeps against bounds, `assert
x > 0` over a counter another process increments, `Process.sleep` followed by an assertion on
state, receive-with-timeout used as a barrier. **Report the classes found, not a count.**

**The census instrument owes a control, per R34.** Plant an assertion in a shape the census is
most likely to miss — a timing dependency expressed without any of the census's search terms, for
instance a bound computed into a variable and asserted several lines later — and show the census
finds it. An instrument that under-reports here produces a clean-looking "one test, not a class"
verdict, which is the answer that closes the row prematurely.

**What this row FORBIDS, stated so a later session does not have to infer it:**

- **No retry wrapper, no `@tag :flaky`, no exclusion, no relaxed bound.** The bound is the
  behaviour under test. A change made to get past a test is what the ds milestone rejected on the
  record, and the standing gate rule forbids a quiet downgrade in terms.
- **No re-running the workflow until it goes green.** **ONE** re-run is permitted and only as an
  experiment whose purpose is written down first: does it reproduce on a CI machine, which is not
  the machine that failed to reproduce it? **Both run ids go in this row whichever way it lands**,
  and a green re-run answers nothing — it is one more unforced pass, which this row has already
  said is not evidence.
- **The red is CARRIED and NAMED**, per the tracked-carry clause: named in packets with this
  row's ref, not re-triaged, and not relaxed.

**Why priority high, argued from the cost rather than asserted.** While `main` is red for a
known reason, the next unknown red is indistinguishable from it — every future run's failure has
to be diffed against this one before it can be read at all. That is the same alarm-fatigue
mechanism the `--strict` drift rule and BL-048's rot both exist to prevent, and it is why the
size is M and the priority is not low.

**What is untouched by this row.** **BL-174**'s close cites run `32611562210`, green on
`7ccfc6a`, as its evidence; that citation remains true and this row does not disturb it. What
changed is that the newest harness run is red, so `main`'s badge no longer agrees with BL-174's
cited evidence, and a reader who checks the badge rather than the row will draw the wrong
conclusion. **BL-135** is the prior instance of this class in this suite —
`run_helpers_timeout_test.exs:84`, a 200 ms feeder against a 300 ms bound, likewise real and
likewise not reproduced (9 attempts). **It is DONE and lives in `docs/backlog-2026-06-closed.md`**,
so it is a precedent and a method to copy, **not** a currently-carried red; this row is the only
open red in the harness suite.

> **[Worked 2026-08-23 at harness `77ab709`. The row's reading was RIGHT about where the message
> lands and WRONG about what that means, and the difference is the whole ticket.**
>
> **The row stays OPEN, and the status field stays the bare vocabulary word `OPEN` because the
> field takes one of three and nothing else.** What is outstanding is narrow and is stated here
> rather than in the field: clauses 1, 2 and 3 are discharged, and clause 4's *check* as amended is
> discharged; only the **corroborating run id** remains, and it is the arbiter's to record because
> it comes from a push this session was forbidden to make.
>
> **The reading is confirmed on its facts.** The message does arrive while B is in its first step,
> and that is what `left: 0` reported. Forced rather than repeated: `:sys.suspend/1` on B's stub LLM
> adapter holds B inside its first loop iteration, and the assertion then fails **on demand, five
> runs of five**, in 0.06 s. The hold is a real hold, not a starvation — at delivery B is `:running`
> and has already appended its own `prompt_built` and `llm_called`, **both at step 0**. So the
> message did not arrive *before B started*; it arrived while B was **working inside step 0**, which
> is the fact that decides the repair.
>
> **But step 0 is a LEGAL receiver step, so the CODE is right and the EXPECTATION was wrong.**
> Established from the code rather than from the test: `Loop.run/5` enters at
> `do_run(opts, 0, ...)`, so a loop's first iteration **is** step 0 and every event it appends
> carries step 0. `Agent.Server.handle_call({:deliver_message, ...})` records
> `max(state_step, current_step(log_pid))`, and `Log.append/2` is a synchronous `GenServer.call`,
> so that read returns B's true step — not a default standing in for a value the coordinator failed
> to read. Both readings the ticket posed were therefore testable and the second is false: there is
> no defect to repair in `coordinator.ex` or `server.ex`, and **synchronising the test would have
> hidden real, correct behaviour behind a barrier.**
>
> **What `> 0` was actually asserting** is that B finished one whole iteration before A finished
> two — a scheduling outcome, not a contract. On an idle machine B wins by a comfortable margin;
> under CI contention it does not. The sibling assertion at `:124` is **not** the same shape and is
> left alone: it reads the *sender*'s step, and A issues `send_message` as its second stub response,
> so that step is 1 by construction.
>
> **The repair is stricter than what it replaces, and that is measured rather than claimed.** The
> assertion now pins the step to B's own preceding event instead of admitting any positive number.
> Under an injected off-by-one in `deliver_message` (`... + 1`), the OLD assertion reports
> `10 tests, 0 failures` and the NEW one reports `10 tests, 1 failure`. So it is not a relaxed
> bound in any sense this row forbids; it catches a defect the original missed.
>
> **Clause 4, as amended.** The amendment's check — the forced reproduction re-run against the
> repaired code — is discharged: **fails before, five of five; passes after, five of five**, same
> harness, same hold, same conditions. The forcing harness is **scratch and was not committed**: the
> repaired assertion is scheduling-independent, so a permanent held-receiver test would add a
> `:sys.suspend` dependency on an internal registry key for no coverage the mutation control does
> not already establish. It is reproduced verbatim in
> `docs/milestones/bl-181-implementation-notes.md` so a later session can re-run it.
>
> **The corroborating workflow run is NOT recorded here, and this row does not claim one.** It
> requires a push, which this ticket forbade. What it should show when the arbiter pushes: the
> `check` job green, `972 tests, 0 failures, 133 excluded` — the same totals as the red run
> `32618789914`, which reported `972 tests, 1 failure, 133 excluded`. Locally at `77ab709` the CI
> command `MIX_ENV=test mix test --exclude requires_worker --exclude integration` gives exactly
> that, exit 0. **The permitted single re-run of `32618789914` was NOT used** and remains available.
>
> **The census ran, and its answer is "one assertion, but a real class".** Reported in full at
> `docs/milestones/bl-181-implementation-notes.md` §Census. The instrument's R34 control passed;
> it also **under-reported twice before it passed**, both times caught and both recorded there.
> One member of the class it found is beyond this ticket's repair scope and is filed as **BL-183**.
> **]**

**Costs:** M. Forcing the race is the work; the repair may be small once the mechanism is known,
and the census is the part whose size is genuinely unknown until it runs.

**Collides with:** **BL-135** (closed — precedent and method, not a live dependency). **BL-048**,
whose `requires_worker` set is excluded from this gate and is unaffected either way.

`Source: this row's own filing, 2026-08-23, at harness a4f93e1 / agents at the commit carrying it. Every figure carries the command that produced it. The failure text is transcribed from gh run view 32618789914 --log, the causation from the commit range, and the non-reproduction from runs performed at this close and reported with their method rather than only their result.`

> **[CLOSED 2026-08-23. Clause 4 discharged in full, and the row closes on all four.** The
> corroborating workflow run is **`32636070709`** — `push`, head harness **`77ab709`**, conclusion
> **success**, both jobs green (`sandbox`, `check`). Its test step reports
> **`972 tests, 0 failures, 133 excluded`**, from the run's own log rather than a summary
> (`gh run view 32636070709 --log`).
>
> **That is what this row predicted it would show, published before the push and matched exactly** —
> the same `972` / `133` totals as the red run `32618789914`, which reported
> `972 tests, 1 failure, 133 excluded`. One assertion moved and nothing else did.
>
> **The corroboration is recorded in the amendment's order, not the original clause's.** The check
> was clause 1's forced reproduction, discharged before the push: fails before, five of five;
> passes after, five of five, same harness and same hold. This run is corroboration recorded
> **after** that check, which is exactly what the 2026-08-23 amendment says it is and all it is. A
> reader should not read this run as the thing that established the repair.
>
> **Both run ids are in this row whichever way it landed**, as the row required: `32618789914` red
> at `a4f93e1`, `32636070709` green at `77ab709`. **The permitted single re-run of `32618789914`
> was never used.**
>
> **`main` is no longer red.** The condition that made this row priority-high — every future
> failure having to be diffed against this one before it could be read — is gone.
>
> Pushed at the arbiter's ratification: harness `77ab709`, then agents `1130871`. **]**

---

### BL-176 — `aetheris`, a build output, is committed to the tree and is three months stale (#TBD)
**Status:** DONE
**Kind:** question · **Census items:** n/a · **Contract:** n/a
**Size:** S–M · **Priority:** low
**Section:** harness (`../aetheris/aetheris`)

Filed 2026-08-23 at **BL-174** stage 2. Surfaced by that row's census, which returned the file as
one of eleven `aetheris_nif` hits and classed it **ARTIFACT** — neither an instruction to fix nor
a record to preserve, and out of that row's scope for that reason rather than by judgement.

**What it is.** `file aetheris` reports an escript; it is a ZIP archive whose entry table contains
`aetheris_nif.so`, the compiled shared object of a crate deleted at `e977af0` (2026-05-20). It was
committed at `f43c905` (2026-05-16) and has not been rebuilt since —
`git -C ../aetheris log -1 --format='%h %ad' --date=short -- aetheris`.

**The question is not whether to rebuild it.** Rebuilding produces a fresh binary that is stale
again the next time `lib/` changes, and nothing notices in between; that is the same defect with a
newer timestamp. The question is **whether a build output belongs in the tree at all**. `mix
escript.build` produces it on demand and `CLAUDE.md` §How to run already documents that command.
Against removal: someone may be invoking `./aetheris` from a checkout without a build step, and
this repo has not surveyed who.

**Done when:** the file is either removed from the tree and gitignored, with the invocation path
for anyone relying on it named, or deliberately kept with a stated rebuild trigger and something
that enforces it. Recording "we looked and chose to keep it" **without** a trigger does not
discharge this row — that is the state it is already in.

**Costs:** S if removed, M if kept, because keeping it means building the trigger.

**Collides with:** nothing. **BL-174** classed it and does not dispose of it.

`Source: BL-174 stage 2, 2026-08-23, at harness `a49d05a`. The ZIP entry was read with
`grep -aoE '.{60}aetheris_nif.{60}' aetheris` at stage 1.`

> **[CLOSED 2026-08-23 at harness `82a12cd`. The ruling was REMOVE, and the branch the Done-when
> offered as the alternative was not taken.** `aetheris` is out of the tree and ignored at
> `.gitignore:19`, whose comment states why a build output committed for three months is ignored now
> and names this row.
>
> **The check that could have stopped it ran first, and it found five live sites.** Both trees were
> searched for references to the file **as a path** rather than as a build product, before the
> removal. Repointed in the same commit: `scripts/sprint.sh`'s four closing `info` lines, now
> `mix aetheris …` — the script's own `ESCRIPT` variable was already `"mix aetheris"` and nothing in
> it consumed the binary, so its `mix escript.build` prerequisite was dropped as false as well as
> unused; `agents/skill_extraction.exs:3`'s worked example in a `raise` message; and
> `docs/aetheris/runbook.md` §Exit code, which names the escript as the way to get a real exit code
> (BL-044) and now says to build it first. `runbook.md` §Option C already had the build step above
> the invocation and is unchanged. **None of the four standing-instruction files** —
> `.github/copilot-instructions.md`, `CLAUDE.md`, `README.md`, `docs/aetheris/test-plan.md` — named
> it as a path; `CLAUDE.md:519-521` names it under `mix escript.build`, which is the form this row
> relied on. Nothing under `.github/` mentions it. Nothing execs it: Rig's `fork.rs` builds
> `Command::new("mix")` with `"aetheris"` as the first *argument*, a Mix task.
>
> **Every remaining hit is a frozen record, and that is a ruling this row makes rather than an
> assumption.** `runbook-m11.md`, `runbook-m12.md`, `handoff-m07-m08.md`, the two m08 milestone
> docs, five review files, and backlog and consolidation rows. This repo states the class in its own
> words twice — `.github/copilot-instructions.md:24-31` ("that document is a record and not an
> instruction to you", covering "every dated record in the repository, wherever it sits") and
> `docs/aetheris/runbook.md:6-25`, which enumerates the three runbook categories rather than
> pattern-matching them and puts `runbook-m11.md` and `runbook-m12.md` in the never-retro-updated
> list. So the Done-when's "document you may not edit" case was reached and is answered: there is no
> live document with a claim on this file that was left standing, and no record was edited.
>
> **The staleness is demonstrated, not argued from the date.** The removed binary carried the
> `aetheris_nif.so` of a crate deleted at `e977af0`, and it bundled `rustler` — the same May residue
> **BL-177** removes from `mix.lock` in this batch, which is how the two rows turn out to be one
> fact seen twice. Run bare it did not start at all: the exqlite NIF fails to load and the run exits
> 1 before any command dispatches. Run under the workaround the frozen m11/m12 runbooks document,
> `ERL_LIBS=_build/dev/lib`, **it worked** — and worked *wrongly*, which is the more useful result.
> That variable supplies current *deps*; the escript's own archive supplies `aetheris`. Its
> `--help` listed neither `schedule` nor `server`, added at `f018b5f` (2026-05-20) and `be43092`
> (2026-05-21), and `./aetheris server --help` answered `Error: unknown command: server`, exit 1,
> where the current CLI dispatches it. The binary ran May's CLI and said nothing about it. **That is
> the row's own hypothesis — "runs May's code silently" — turned into an observation.**
>
> **The invocation path for anyone relying on it, which the Done-when requires by name.** They now
> get `./aetheris: No such file or directory`, exit **127**. The command that produces the file is
> `mix escript.build`, documented at `CLAUDE.md:519-521` §How to run and at
> `docs/aetheris/runbook.md` §Option C.
>
> **No gate observes this file's disappearance, and none is added.** That is stated rather than
> left for a later reader to discover: nothing in `ci.yml`, `sprint.sh`, `drift_check.py` or the
> harness seven reads `aetheris` as a file, before this commit or after it, so the removal is
> invisible to
> every check and its only consequence is the exit 127 above. Checked, not assumed:
> `grep -n -P "(^|[^.])\./aetheris|escript|['\"]aetheris['\"]" scripts/drift_check.py` returns five
> hits and every one is the harness *directory* — `HARNESS_ROOT = REPO_ROOT.parent / "aetheris"` and
> its four derivatives — with a positive control of 5 `HARNESS_ROOT` occurrences from the same
> grep shape; and the harness seven were run to green on a tree from which the file was already
> gone. A gate asserting the absence of a build output would be a rebuild trigger by another
> name, which is the branch this ruling declined.
> **]**

> **[Residue tested and closed 2026-08-23 at harness `c171a78`. BL-176 stays DONE; this row is not
> reopened.** Its implementation notes §8 reported, as an observation rather than a row, that this
> removal made `docs/aetheris/runbook.md` §Option C the only route to an escript while the
> `ERL_LIBS=_build/dev/lib` requirement that makes one start was recorded **only** in
> `runbook-m11.md`, `runbook-m12.md` and `milestones/handoff-m07-m08.md` — all point-in-time
> records. The notes could not settle whether a *freshly built* escript still needs it, because that
> ticket was forbidden to rebuild. **The rebuild was authorised afterwards and the question is now
> answered: it does.**
>
> ```
> $ mix escript.build                            Generated escript aetheris with MIX_ENV=dev   EXIT=0
> $ ./aetheris list --limit 1                    EXIT=1   Exqlite.Sqlite3NIF.open/2 is undefined
> $ ./aetheris server --help                     EXIT=1   same failure, before any dispatch
> $ ERL_LIBS="_build/dev/lib" ./aetheris list --limit 1    EXIT=0   run listed
> ```
>
> **The requirement is a property of running an escript at all, not of a stale one**, which is the
> finding — and the two binaries are provably different rather than assumed so: the removed one
> raised at `store.ex:194` and answered `Error: unknown command: server`; this one raises at
> `store.ex:568` and, under `ERL_LIBS`, **dispatches** `server`, starting a server and being
> cap-killed at 120s (exit 124, recorded as the complete result it is and not retried longer).
>
> So the canonical instruction was missing the half that makes its own procedure work, and
> `c171a78` adds it to §Option C with its reason. The frozen records were not edited and their
> content is not repeated beyond the one requirement. **The observation in the notes is discharged
> here rather than left standing as an open question for a later reader to re-investigate.**
>
> **And the removal's structural claim is confirmed by the same test:** the built escript is
> 18,643,194 bytes in the working tree and `git status --porcelain` is empty —
> `git check-ignore -v aetheris` reports `.gitignore:19:/aetheris`, the rule this row added. A
> rebuild can no longer be committed by accident. **]**


---

### BL-177 — `mix.lock` still resolves `rustler`, a dependency removed three months ago (#TBD)
**Status:** DONE
**Kind:** bug · **Census items:** n/a · **Contract:** n/a
**Size:** S · **Priority:** low
**Section:** harness (`../aetheris/mix.lock`)

Filed 2026-08-23 at **BL-174** stage 2, found by that row's **extended** census — the one keyed on
the `e977af0` deletion rather than on the `aetheris_nif` token, which does not reach this file.

`mix.lock:23` carries a resolved entry for `rustler` at `0.37.3`. `mix.exs` has named no such
dependency since `e977af0` removed `{:rustler, "~> 0.36"}` (2026-05-20), and `deps/rustler` exists
in at least one working tree. **Outside BL-174's class** — a lockfile is not documentation — so it
is filed rather than swept.

**Why it is not fixed in BL-174's commit, stated so the next reader does not treat the omission as
an oversight.** `mix deps.unlock --unused` rewrites `mix.lock`, and `mix.lock` is hashed into two
`ci.yml` cache keys: `plt-…-${{ hashFiles('**/mix.lock') }}` and the deps/build key. Changing it
invalidates both, and the next run is cold. That is a small, one-time, self-healing cost — but it
is a **cache-behaviour change**, and BL-174 is a documentation row whose whole argument is that it
changes declarations and not behaviour. Mixing the two would make the row's own claim false.

**And the cost is now measured rather than assumed.** Run `32611562210` demonstrated the same
mechanism from the other direction: BL-173 removed a *path* from two cache steps, which changes
`actions/cache`'s **version** rather than its key, and both caches missed on byte-identical keys
and rebuilt. One cold run either way. See **BL-175**.

**Done when:** `mix.lock` carries no entry absent from `mix.exs`'s dependency tree — check with
`mix deps.unlock --check-unused` if that flag holds in this Elixir version, otherwise by
`mix deps.unlock --unused` producing an empty diff — and the run that follows the change is
observed cold and then green, with the run id recorded. A green run alone does not discharge it;
the point is that the invalidation was expected and watched.

**Costs:** S. One command and one cold CI run.

**Collides with:** **BL-175** (shares the cache-invalidation mechanism), **BL-174** (found it, does
not own it).

`Source: BL-174 stage 2, 2026-08-23. The lock entry is `git -C ../aetheris grep -n rustler mix.lock`;
the cache-key dependency is `ci.yml`'s two `hashFiles('**/mix.lock')` expressions.`

> **[Worked 2026-08-23 at harness `9b76009`. The edit is done and the row stays OPEN on one clause,
> which is the run.** The status field keeps the bare vocabulary word `OPEN` because it takes one of
> three and nothing else; what is outstanding is narrow and is stated here rather than in the field.
>
> **The lock clause is discharged.** This Elixir is 1.17.2 and it does carry `--check-unused`, so the
> set was established before the removal rather than inferred after it: `mix deps.unlock
> --check-unused` named exactly `:rustler` and exited 1; `mix deps.unlock --unused` reported
> `Unlocked deps: * rustler`; the diff is one deleted line, `mix.lock:23`; and `--check-unused`
> then exits 0. `mix.exs`'s dependency list names nothing removed. `deps/rustler` is present in
> this working tree and is **not tracked** — `/deps/` is gitignored and `git ls-files deps/` returns
> nothing — so it is named and left alone, as this row said it would be.
>
> **The harness seven ran green on the resulting tree**, each capped: `mix test` reports `972 tests,
> 0 failures, 133 excluded` in 90.5s, and `mix dialyzer` `Total errors: 0`. **BL-135** did not fire.
>
> **What remains is clause 2 — the run observed cold and then green, with its run id recorded — and
> it is the arbiter's to record, because it comes from a push this batch was forbidden to make.**
> The prediction is published here *before* that push so it can be falsified rather than described.
> `hashFiles('**/mix.lock')` matches exactly one tracked file, whose sha256 moves
> `50d81d01…d974` → `f8422995…8407`, and that hash is in two of the four cache keys. **BL-179**
> lands in the same batch and bumps `actions/cache` v4 → v6, which can move the derived entry
> *version* independently of the key (**BL-175**). Per step:
>
> | step | key input | prediction |
> |---|---|---|
> | `check` / Cache deps and build | `hashFiles('**/mix.lock')` | **cold, certain** |
> | `check` / Cache Dialyzer PLTs | `hashFiles('**/mix.lock')` | **cold, certain** |
> | `sandbox` / Cache deps and build | `hashFiles('**/mix.lock')` | **cold, certain** |
> | `check` / Cache Cargo | `hashFiles('**/Cargo.lock')`, unchanged here | **not predicted either way** |
>
> Cache Cargo is the step that separates the two mechanisms, and it is deliberately left unpredicted
> rather than guessed: its key does not move, so it goes cold only if the major bump moves the entry
> version. **The three certain-cold steps carry `restore-keys`, and HOW they miss reads the same
> question a second time** — a partial restore from the `${{ runner.os }}-mix-…-` prefix means the
> entry version did **not** move across the bump; a complete miss means it did. The two readings
> must agree with each other and with Cache Cargo. A disagreement is a finding about **BL-175**'s
> mechanism and goes in that row, not this one. **]**

> **[CLOSED 2026-08-23 on run `32639839807`** — `push`, head harness `c171a78`, conclusion
> **success**, both jobs green (`check` 19 steps, `sandbox` 13, no failed step). **Clause 2's run
> id is recorded and the row closes.**
>
> **The invalidation was expected, published before the push, and observed** — which is this row's
> stated point, in its own words: *"A green run alone does not discharge it; the point is that the
> invalidation was expected and watched."* The primary key moved on exactly the three steps
> predicted and on no others. From the run's own log:
>
> | step | primary key | outcome |
> |---|---|---|
> | `check` / Cache deps and build | `…-77751441ec3b…` | **miss**; restored from `…-99d441acfd94…` |
> | `check` / Cache Dialyzer PLTs | `plt-…-77751441ec3b…` | **miss**; restored from `plt-…-99d441acfd94…` |
> | `sandbox` / Cache deps and build | `…-77751441ec3b…` | **miss**; restored from `…-99d441acfd94…`, saved under the new key |
> | `check` / Cache Cargo | `Linux-cargo-e6bffd8c…` | **exact hit** — *"Cache hit occurred on the primary key … not saving cache."* |
>
> `99d441acfd94…` is `hashFiles('**/mix.lock')` before this row's edit and `77751441ec3b…` after
> it; `sandbox`'s post step saved the new one, and `check`'s post step reported
> *"Failed to save: Unable to reserve cache with key …, another job may be creating this cache"* —
> the two jobs racing to write the same new entry, benign and green.
>
> **THE OBSERVED SHAPE IS NARROWER THAN THE WORD "COLD", AND THIS ROW SAYS SO RATHER THAN LETTING
> THE WORD STAND.** `grep -c 'Cache not found for input keys'` over the whole log returns **0**:
> no step experienced a complete miss. All four restored an entry. The three moved-key steps took a
> **partial restore** from their `restore-keys` prefix — resolved, in this run, to
> `Linux-mix-v1.17.2-otp-27-` and `plt-Linux-v1.17.2-otp-27-OTP-27.0.1-`. So what happened is
> *primary-key invalidation with prefix fallback*, not a cold run; this row's filing said *"the next
> run is cold"* before anyone had considered that these steps carry `restore-keys`. **The close
> rests on the invalidation clause, which is satisfied exactly, and not on the word.**
>
> **What the run settles about the mechanism, which was the other reason to watch it.** The
> second reading published with the prediction was: a partial restore means the derived entry
> *version* did **not** move across the `actions/cache` v4→v6 bump, a complete miss means it did,
> and the reading must agree with Cache Cargo. **Both readings agree, and they agree twice
> over** — Cache Cargo, whose key is byte-identical across the change, took an **exact primary-key
> hit**; and the three moved-key steps found prefix entries *written by v4 runs*, which a version
> change would have made invisible to a v6 reader. **The major bump did not move the entry
> version.** That is information **BL-175** wants and it is deliberately not written there: this
> round was authorised to touch that row only on a *disagreement*, and there is none. **]**

---

### BL-179 — every CI job warns that its actions target a deprecated Node, and the runner is already forcing them onto a newer one (#TBD)
**Status:** DONE
**Kind:** bug · **Census items:** n/a · **Contract:** n/a
**Size:** S · **Priority:** medium
**Section:** harness (`../aetheris/.github/workflows/ci.yml`)

Filed 2026-08-23 at **BL-174** stage 2, from run `32611562210` — the push-triggered run that
discharged **BL-173**'s outstanding evidence. Not caused by that commit and not by this one:
the same annotation appears in run `32563924592`, at the same count.

**What the runs say.** Both jobs annotate:

> Node 20 is being deprecated. This workflow is running with Node 24 by default. If you need to
> temporarily use Node 20, you can set the `ACTIONS_ALLOW_USE_UNSECURE_NODE_VERSION=true`
> environment variable.

It is emitted once per step using `actions/cache@v4` or `actions/checkout@v4`, which declare a
Node 20 runtime.

**Why this is a row and not a style note.** The forcing has **already been applied** — the runner
is not warning about a future change, it is reporting that it overrode the actions' declared
runtime today. Every step using these actions is running on a runtime its author did not test
against, and the escape hatch named in the message is a variable whose own name says it is
unsafe. A deprecation with a runner-side override already in effect is a dated failure: the
override is what will be withdrawn, and when it is, the actions stop rather than warn.

**Done when:** every action in `ci.yml` declares a Node runtime the runner does not override, or
each one that cannot is named with the upstream issue and a date to re-check. A run whose log
contains no such annotation is the check; `gh run view <id> --log | grep -c 'Node 20 is being
deprecated'` returning 0 discharges it, and the positive control is the same command against
`32611562210`, which does not return 0.

**Costs:** S if a major-version bump of both actions clears it; unknown if a pinned action has no
Node-24 release.

**Collides with:** **BL-173** (closed; this was found in its evidence run and is not its subject).

`Source: BL-174 stage 2, 2026-08-23, from `gh run view 32611562210 --log` and the same for
`32563924592`. Checked for an existing owner before filing: no row in either backlog file mentions
`actions/cache@`, `actions/checkout@`, Node 24 or `ACTIONS_ALLOW_USE_UNSECURE` except BL-173's own
closed row, which names `actions/cache@v4` for its missing-path silence and not for its runtime.`

> **[Worked 2026-08-23 at harness `0783e3f`. The bump is done and the row stays OPEN on one clause,
> which is the run.** The status field keeps the bare vocabulary word `OPEN`; what is outstanding is
> stated here rather than in the field.
>
> **The enumeration clause is discharged, and it was run over EVERY action in the file rather than
> the two the annotation names.** `runs.using` was read from each action's own `action.yml` at the
> pinned ref through the GitHub contents API — the action's own declaration, not its documentation:
>
> | action | pinned | `runs.using` at that pin | annotates? | disposition |
> |---|---|---|---|---|
> | `actions/checkout` | `@v4` | `node20` | yes | bumped to **`@v7`** (`node24`) |
> | `actions/cache` | `@v4` | `node20` | yes | bumped to **`@v6`** (`node24`) |
> | `erlef/setup-beam` | `@v1` | **`node24`** | no | unchanged — `v1` already declares it |
> | `dtolnay/rust-toolchain` | `@stable` | **`composite`** | no | unchanged — declares no Node runtime at all; every step is `shell: bash` and it nests no `uses:` |
>
> **No action in this file lacks a Node-24 release, so the row's alternative clause — name it with
> an upstream issue and a date to re-check — is not engaged.** `actions/checkout` declares `node24`
> from `v5` up; `actions/cache` from `v5` up.
>
> **The table is corroborated from live data, in the other direction, by the annotation's own
> distribution in the row's own run.** All 12 hits in `32611562210` fall on `checkout` and
> `Cache *` steps and their `Post` halves — 8 in `check` (checkout plus three caches, main and post
> each), 4 in `sandbox` (checkout plus one cache) — and **none** on `setup-beam` or
> `rust-toolchain`, which is what a `node24` action and a composite action look like in that log.
>
> **Changelogs read before bumping, not after.** `checkout` v5 and `cache` v5 are the `node24`
> majors and raise the minimum **self-hosted** runner to `2.327.1`; both jobs are `ubuntu-latest`.
> `checkout` v6 persists credentials to a separate file and this workflow performs no git write.
> `checkout` v7 blocks fork checkout for `pull_request_target` and `workflow_run`, and this
> workflow triggers on `workflow_dispatch`, `pull_request` and `push: [main]` — neither. `cache` v6
> and `checkout` v7 are ESM migrations. No `cache` release note between `v4.3.0` and `v6.1.0`
> mentions cache-version derivation, compression or zstd; the positive control on that negative is
> the same pipeline searching for `node`, which returns 2.
>
> `yaml.safe_load` parses the edited file: two jobs, `check` (13 steps) and `sandbox` (9), ten
> `uses:` steps enumerated.
>
> **What remains is the run, and it is the arbiter's, because it comes from a push this batch was
> forbidden to make.** The check is
> `gh run view -R vishal-h/aetheris <id> --log | grep -c 'Node 20 is being deprecated'` returning
> **0**. **Its positive control was run BEFORE the change, against the run this row names**, so the
> control cannot be an artifact of the fix: the same command against `32611562210` returns **12**,
> not 0. The expectation for the arbiter's run is therefore 12 → 0. See **BL-177**, same batch, for
> what the cache steps are predicted to do in that same run. **]**

> **[CLOSED 2026-08-23 on run `32639839807`** — `push`, head harness `c171a78`, conclusion
> **success**, both jobs green. **The check returned 0 and the row closes.**
>
> ```
> $ gh run view -R vishal-h/aetheris 32639839807 --log | grep -c 'Node 20 is being deprecated'
> 0
> ```
>
> **Positive control, restated at the close and unchanged from the one run before the fix**, so it
> cannot be an artifact of the fix:
>
> ```
> $ gh run view -R vishal-h/aetheris 32611562210 --log | grep -c 'Node 20 is being deprecated'
> 12
> ```
>
> **12 → 0**, which is exactly the expectation this row published before the push. `gh` bound with
> `-R vishal-h/aetheris` on both invocations, per **R33** — `gh run view` otherwise resolves the
> repository from the working directory.
>
> The Done-when's first branch is the one taken: *every* action in `ci.yml` now declares a Node
> runtime the runner does not override. The alternative branch — name any action that cannot, with
> an upstream issue and a date to re-check — was **not engaged**, because no action in the file
> lacked a Node-24 release. Nothing is carried forward from this row. **]**

---

### BL-048 — The `requires_worker` test set is red: 15 failures, invisible to CI and to every default `mix test` (#TBD)
**Status:** DONE
**Size:** M · **Priority:** medium · **Section:** Harness (aetheris/)

`mix test --include requires_worker` reports **15 failures** on `main` at `8021a59`, with no
BL-042 changes applied (verified by stashing them and re-running: the failing set is
byte-identical, 900 tests / 15 failures). CI never sees them — `ci.yml:64` runs
`--exclude requires_worker --exclude integration` — and neither does a local `mix test`,
because `test_helper.exs:4` excludes the same tags by default. Found off-territory by
BL-042's own done-check, which is the only reason it is on the record at all.

Three distinct causes, not one:

- **Test written against a stale allowlist** — `run_command_test.exs` uses `pwd`, which is not
  in `PERMITTED_COMMANDS` (`aetheris_exec_server/src/runner.rs:7-24`); the exec server
  correctly answers `command not permitted: pwd`. 3 failures.
- **`fs_hash` is nil where the test expects `sha256:…`** — `client_test.exs:53`,
  `fs_hash_stability_test.exs` (×2). ~~This one is **not** obviously a stale test and may be a
  live defect in worker fs-hashing; it needs diagnosis, not a test edit.~~ **CORRECTED — it is
  nil by design, not a live defect. Diagnosed and closed as BL-053** (`d4728af` removed the
  whole-sandbox hash for a real 30s-timeout reason; the tests were never updated). 3 failures,
  now green.
- **Network/credential-dependent integration tests pulled in by the include** — `httpbin.org`,
  the GitHub MCP server, the HTTP MCP transport. `--include requires_worker` overrides the
  `:integration` exclusion for tests carrying both tags, so these run whether or not the
  environment can support them. 6+ failures. **CORRECTED — the characterization is mostly
  wrong.** Eight of the nine carry `** (stop) {:worker_crashed, 159}` — 159 = 128+31 = SIGSYS —
  which is **BL-043**'s `setsockopt` seccomp gap killing the worker, not a missing credential or
  an unreachable host. Landing BL-043 should clear ~8 of these on its own. The ninth
  (`RunOverlayTest`) is **BL-050**'s handshake race. So the strand is two tracked defects wearing
  an environment-dependency costume; the `:integration` tagging question is real but secondary.
  Do not re-triage per packet — this correction is the triage.

**This is the gate-rot pattern the CLAUDE.md gate rule exists to catch**, running in the
direction that is hardest to see: a set that no gate executes cannot go red visibly, so it
went red silently and stayed. When it broke is unknown, because nothing was watching.

**Done when:** each failure is triaged to stale-test / live-defect / environment-dependent;
stale tests are corrected, live defects get their own rows, environment-dependent tests are
tagged so an include cannot drag them into a run that cannot satisfy them; and the set is
wired into something that runs it — a sprint case or a CI job with the worker available —
so it cannot rot invisibly again. Until then it is a **known-red gate named with this ticket
ref** in packets, not re-triaged each time.

`Source: BL-042 done-check, off-territory, 2026-07-23. Baseline captured on a clean tree.`

**Status 2026-07-25, after BL-050/055/056 (`9871059`):** `requires_worker` is **6 failures**
(951 tests / 65 excluded), down from 11 — and **stable across two consecutive runs with identical
membership**. The four MCP failures and `RunOverlayTest` are gone. Residual, each named:

| Cause | Count | Ticket |
|---|---|---|
| stale `pwd` allowlist | 3 | BL-048 (this row) — the last strand actually owned here |
| `McpHttpTest` — `port_close` in an `on_exit` cleanup | 1 | environment |
| `McpGithubTest` — the server now spawns fine; the agent did not choose to call an MCP tool | 1 | LLM-behaviour integration test, not containment |
| `OverlayAutonomousTest` | 1 | **not BL-050** — see below |

**`OverlayAutonomousTest` is a different defect wearing BL-050's clothes.** It fails with a
byte-identical message before and after the reorder. Root cause: `supervisor.ex:62` starts **no
worker at all** for `provider: "stub"` with empty `mcp_servers`, so that run never mounts an
overlay and the probe cannot land in `upper/`. Diagnosed rather than assumed fixed, and left with
BL-048 rather than silently claimed by BL-050. It needs its own decision — the test asserts overlay
behaviour for a configuration that by design has no worker.

**Zero real SIGSYS remain.** The only `worker_crashed, 159` lines in the capture are
`verify_worker_lifecycle_test.exs` stopping workers with that reason deliberately.

**Status 2026-07-25, after BL-043:** `requires_worker` reports **11 failures** (940 tests / 65
excluded) at harness `515a4ab`, and **SIGSYS is down 8 → 4**. BL-043 corrects this row's
third bullet twice over: the nine residuals were never "network/credential-dependent integration
tests", and they were never *one* cause either. They are now:

| Cause | Count | Ticket |
|---|---|---|
| stale `pwd` allowlist | 3 | BL-048 (this row) |
| MCP-stdio spawn vs. the deliberate `execve` exclusion (SIGSYS) | 4 | **BL-055** |
| overlay (`RunOverlayTest`, `OverlayAutonomousTest`) | 2 | BL-050 / BL-054 slot |
| external service — `httpbin.org` returning 503, and `McpHttpTest`'s `port_close` cleanup | 2 | genuinely environment-dependent |

The `httpbin` one is worth reading closely: it now fails on a real **503 from the live host**,
where before it died of SIGSYS. That is the repair working — the request reaches the internet.

**Status 2026-07-25, after BL-053:** `mix test --include requires_worker` at harness
`915d582` reports **12 failures** (was 15; 934 tests / 65 excluded). The fs_hash strand
is closed. Remaining: pwd ×3, SIGSYS/BL-043 ×8, and **one load-sensitive flake** — the twelfth
slot is not stable. In the BL-053 run it was `RunHelpersTimeoutTest` "a status change alone
counts as activity" (a 300 ms inactivity window, 10/10 green in isolation); in the diagnosis run
it was `RunOverlayTest` (BL-050). Both are races that surface only under the full suite's load.
Filed as **BL-054** so the twelfth slot has a name rather than being met as a first sighting each
time (the BL-051 lesson).

---

### BL-048 — DONE (pending first CI dispatch) 2026-07-25

Landed at harness `6e2fad8`. **The set is green and wired.** `mix test --include
requires_worker` on a capable machine: **951 tests, 0 failures, 67 excluded, 1 skipped**,
identical across two consecutive runs.

**One thing pends, and it is the human's move.** The wiring is a CI job gated on the worker's
containment attestation, and the attestation only reports on `ubuntu-latest` once a job runs
there (a PR or `workflow_dispatch`). If it reports capable, BL-048 closes as a CI job. If it
reports *not* capable — GitHub's 24.04 image may restrict unprivileged user namespaces via
AppArmor, which this repo has deliberately not surveyed — the harness sprint is the standing
home and **BL-048 still closes**, just wired there: `scripts/sprint.sh` already prints the same
probe. Either way the set has a gate; which gate is what the first dispatch decides.

**The six, each triaged (the row's own done-when):**

| Test | Disposition | Why |
|---|---|---|
| `RunCommandTest` ×3 | **fixed** | Three *different* non-permitted commands — `sleep`, `pwd`, `false` — not just `pwd`. Each asserted against a command the exec server is right to refuse, so none exercised what its name claimed. Rewritten on `python3` |
| `McpHttpTest` | **fixed** | Test-hygiene, not environment: `on_exit` called `Port.close` on an already-closed port and raised, so the test's only failure mode was its own teardown. It is hermetic (local python mock) and stays in the set |
| `McpGithubTest` | **retagged, kept** | `:requires_real_provider`. Needs a real model to *choose* to call the tool, plus a token and the binary. The stdio GitHub MCP path is live and surfaced, so the test is kept — it just cannot live in a sandbox-only set |
| httpbin `http_call` | **retagged (extracted)** | `:requires_internet`, in a module of its own. See the correction below |
| `OverlayAutonomousTest` | **skipped, filed as BL-057** | Cannot pass as written; no test-side config fixes it. See BL-057 |

**A correction worth recording, because it nearly shipped.** The first attempt retagged the
httpbin test in place with `@tag requires_worker: false`. That does **not** hold against a
module-level `@moduletag :requires_worker` under an `--include` — the test still ran, and the
set reported **green** because httpbin happened to return 200 on that run. The second run got a
503 and exposed it. The fix is a module of its own; the lesson is that "the set is green" needed
two runs to be worth saying, which is why the done-check asked for two.

**Residual accounting, corrected one last time.** This row's characterisations were wrong twice
before: "network/credential-dependent integration tests" (they were mostly SIGSYS → BL-043),
then "mostly BL-043" (half were the MCP-stdio/`execve` exclusion → BL-055). Final state: **zero
residual in the deterministic set.** What was environment-dependent is retagged out and still
runs under its own include — verified, not assumed: both retagged tests were executed under
`--include requires_internet` / `--include requires_real_provider` and fail for their
environmental reasons (a live 503; the model not calling the tool). Retagged, not dropped.

**Part B — the set cannot rot invisibly again.** `scripts/containment_probe.exs` asks the worker
what it established (BL-050/055/056 made that a runtime fact) and reports
netns/seccomp/exec-server/overlay. The CI `sandbox` job runs the probe, then runs the set if
capable or **skips with the missing primitive named** — deliberately not red, because a job that
reddens on a runner's limits gets disabled, which is how this set rotted in the first place.

`Source: BL-048, closed at harness 6e2fad8, 2026-07-25.`

`2026-08-23, at the BL-174 close — the first dispatch has happened and the CI branch is CLOSED: three runs on ubuntu-latest (32553802996, 32563924592, 32611562210) all report the probe verdict NOT CAPABLE with missing seccomp, exec_server, network_namespace and "worker refused to start: :containment_unavailable", so the deterministic set is absent from every one of their step lists and the sandbox job has passed without executing it every time. The remaining branch, the harness sprint as the standing home, is AVAILABLE BUT CONDITIONAL and the condition is stated here because the row does not carry it: BL-048 closes on that branch only when the containment probe is run WHERE THE SPRINT RUNS and the set is shown actually executing and able to go red. Wiring it to a sprint that fails the same probe reproduces the vacuous green one level down, which is the defect this row exists to remove. If the probe fails there too, the finding is that the set has no automatic home at all, which is a larger row and not a close. Ruling recorded only: not executed, the probe not run, and this row's status unchanged.`

`2026-08-23, later the same day — the CONDITION IS MET and the row CLOSES on the sprint branch, at
harness bb06cfb. The condition was that the containment probe be run WHERE THE SPRINT RUNS, and
that the set then be shown actually executing and able to go red.`

**Where the sprint runs, concretely, because the ruling asked for the method and not just the
verdict.** The sprint is `../aetheris/scripts/sprint.sh`, run by hand on this workstation from the
harness root — it is not a hosted runner and has no counterpart in CI. It already invokes the probe
at its Prerequisites section, line 344, as `mix run scripts/containment_probe.exs` in the **dev**
env, which is the invocation that was reproduced verbatim rather than approximated; CI's `sandbox`
job runs the same script under `MIX_ENV=test`, and the worker binary is built per-env, so the two
are not interchangeable. The machine: Ubuntu 22.04.5 LTS, kernel 6.8.0-136-generic, with
`kernel.unprivileged_userns_clone=1` and `kernel.apparmor_restrict_unprivileged_userns=0` — which
is the concrete difference from the `ubuntu-latest` 24.04 image the CI branch died on, and it is a
property of one laptop rather than of anything reproducible.

**The probe's own output there, exit 0:**

```
  ── containment probe ─────────────────────────────────────────────
    network namespace : true
    seccomp filter    : true
    exec server       : true
    overlay           : false   (not required)
  ──────────────────────────────────────────────────────────────────
    verdict: CAPABLE — the sandbox set can run here
```

**Against the CI branch, re-verified here rather than taken from the ruling above.** All three runs
report `verdict: NOT CAPABLE` with `missing: seccomp, exec_server, network_namespace`, and
`grep -c 'Run the deterministic sandbox set'` returns **0** in all three logs — the step is absent
from the step list, so the job passed without the set ever executing. That is the vacuous green the
condition exists to avoid reproducing.

**The arm, and both things it was required to show.** `./scripts/sprint.sh sandbox_set`, also in
`all`.

1. **It EXECUTES, named rather than counted.** The arm runs `mix test --only requires_worker
   --trace` and writes every test that actually ran to `sprint/<ts>/sandbox_set/executed.txt` — 64
   of them, by name, distinguished from the excluded ones by carrying a timing rather than the
   literal `(excluded)`. It gates on an **anchor**: `BL-043: http_call completes a real round-trip
   under the live seccomp filter`, the one test in the set that can only pass where containment was
   genuinely established. If the anchor stops running the arm fails, because the set having run is
   not the same claim as the set having run *sandboxed*.
2. **It can go RED.** An assertion in the set was mutated —
   `test/aetheris/execution/tool/run_command_test.exs`, the `working_dir` test's
   `assert Map.fetch!(decoded, "exit_code") == 0` changed to `== 99`. The arm failed and named the
   failing test: `[FAIL] mix test --only requires_worker exited non-zero — 972 tests, 1 failure,
   907 excluded, 1 skipped`, with `1) test run_command with working_dir executes in the specified
   directory` in its trace. The file was restored from a **sha-verified working-copy backup**
   (sha256 `bc8f04b82df5…` before and after), never `git checkout --`, and the arm went green again.

**`--only requires_worker`, not `--include`.** `--include` runs the whole suite and reports one
total, so the set's own result is invisible inside it. `--only` runs exactly the set and **exits
non-zero when the filter matches nothing**, so an arm that stops selecting the set goes red rather
than green-on-empty — which is the same defect as the CI branch, one level down.

**The arm is NOT promoted.** Every assertion uses `fail`, so it is counted and non-blocking under
R7; the sprint exited 0 on the red run, with `reds NOT YET DECLARED ... 1`. Promotion is a later
ticket's act with its own red-by-mutation evidence, exactly as `export_mechanism` was left.

**What this close does NOT claim.** The set now has an automatic home **on a capable host**, which
is the branch the ruling left available. It has no home that runs without a human starting it, and
none on any hosted runner — the CI branch is closed NOT CAPABLE and nothing here reopens it. D4's
larger finding is therefore not reached, but it is not refuted either: the sprint is a standing home
in the sense the ruling meant, and it is one person's laptop.


---

### BL-178 — no `cargo` gate runs against either surviving Rust crate, and their state is unknown (#TBD)
**Status:** DONE
**Kind:** question · **Census items:** n/a · **Contract:** harness `CLAUDE.md` §CI contract
**Size:** M · **Priority:** medium
**Section:** harness (`../aetheris/native/aetheris_worker`, `../aetheris/native/aetheris_exec_server`)

Filed 2026-08-23 at **BL-174** stage 2. Stage 1 removed four `cargo` commands from `README.md`
§Running checks because they ran under `native/aetheris_nif`, deleted at `e977af0`. That left the
README declaring **no Rust checks at all** — which is true, and is the finding.

`native/aetheris_worker` and `native/aetheris_exec_server` exist and are the workspace members of
`native/Cargo.toml`. Nothing runs `cargo fmt --check`, `cargo clippy -- -D warnings` or
`cargo test` against either: not `ci.yml` (which installs `dtolnay/rust-toolchain@stable` and then
never invokes cargo directly), not `sprint.sh`, and no other gate.

**This row does NOT decide to add a gate.** It decides what the gate would find, first, because a
gate that has never run has an unknown initial state and a red first run inside a documentation
ticket converts that ticket into Rust repair of unknown size. That is the sequencing this
backlog already carries as a rule — enumerate what a hardening will trip before sequencing it
(**BL-077**, **BL-069**).

**Done when:** all three commands have been RUN against each crate and the results recorded here —
command, crate, exit code, and the head of any failure — **before** any decision about wiring. If
all six are green, adding the gate is a separate, small, and now-safe change with its own row. If
any is red, this row's disposition is the triage, not the gate.

**One thing to settle while running them, for this row and not for BL-174's commit.** The crates
are workspace members, so `cargo fmt --check --all`, `cargo clippy --workspace -- -D warnings` and
`cargo test --workspace` from `native/` may cover both in one invocation and would be the better
form. `.github/copilot-instructions.md` currently prescribes the per-crate shape
(`cd native/<crate> && …`), landed at `a49d05a`; if the workspace form is adopted, that instruction
is corrected by this row.

**Costs:** M, and the size is genuinely unknown until the six runs happen — which is the point.

**Collides with:** **BL-150** (the gate-set declarations disagree and no row owns reconciling them;
this row must not be read as taking that on).

**CLOSED 2026-08-23 at harness `bb06cfb`. All six ran, all six exited 0, and the gate is wired in
the same ticket.** The six, each command against each surviving crate:

| command | crate | exit | output |
|---|---|---|---|
| `cargo fmt --check` | `aetheris_worker` | 0 | no output |
| `cargo fmt --check` | `aetheris_exec_server` | 0 | no output |
| `cargo clippy --locked -- -D warnings` | `aetheris_worker` | 0 | `Checking` through the dependency graph, then the crate; `Finished` |
| `cargo clippy --locked -- -D warnings` | `aetheris_exec_server` | 0 | `Checking aetheris_exec_server`; `Finished` |
| `cargo test --locked` | `aetheris_worker` | 0 | `test result: ok. 34 passed; 0 failed` |
| `cargo test --locked` | `aetheris_exec_server` | 0 | `test result: ok. 17 passed; 0 failed` |

**Two of the first-pass runs were warm-cache replays, and the results above are NOT those runs.**
`cargo clippy --locked` on `aetheris_exec_server` finished in 0.04s emitting `Finished` and no
`Checking` line at all — a green from a step that checked nothing, which is this backlog's
**Silent-wrong-answer** class arriving inside the measurement meant to settle the row. Caught by
reading the elapsed time and the absence of a `Checking` line rather than the exit code, which was
0 either way. Every result in the table is from a re-run against a fresh `CARGO_TARGET_DIR` in the
scratchpad, so no verdict rests on a replay and none of it touched `native/target`.

`native/Cargo.lock` is byte-identical before and after — sha256 `b0e038b3615b…`, checked after each
group. **`cargo fmt` cannot take `--locked` and does not need it**: it rejects the flag outright
(`error: unexpected argument '--locked' found`) because it resolves no dependencies. The flag is on
the two commands that do.

**The workspace question, settled: the workspace form is equivalent and is what was wired.** The
row asked for the same RESULT and not merely the same exit code, and exit codes agreeing was the
weakest of the three checks:

- `cargo clippy --workspace --locked -- -D warnings` from `native/` emits a `Checking` line for
  **each** member, so both crates are demonstrably reached.
- `cargo test --workspace --locked` runs the **same two test binaries** the per-crate runs built —
  identical binary hashes, `aetheris_worker-e00e58200b0a51e3` and
  `aetheris_exec_server-381c87e387d05e41` — with the same per-crate counts.
- `cargo fmt --check --all` reports nothing on a clean tree, so its coverage is invisible in its own
  output and agreement proves nothing. A formatting defect was planted in one file of **each** crate;
  the workspace form exited 1 and named **both** (`Diff in …/aetheris_worker/src/protocol.rs:48`,
  `Diff in …/aetheris_exec_server/src/runner.rs:218`). Restored from a **sha-verified working-copy
  backup**, never `git checkout --`, and green again.

**The row's "separate row" clause is overruled, on the prompt's instruction and its reasoning.** The
row deferred wiring because a gate with an unknown initial state can turn a small ticket into Rust
repair of unbounded size. The measurement discharges exactly that reason, and the wiring is a few
lines — so it lands here rather than as a second row. **This is not a precedent for skipping the
measurement**; it is what the measurement was for.

**What landed at `bb06cfb`:** three steps in `ci.yml`'s `check` job with
`working-directory: native`, placed after the existing `mix` steps. No cache path, key or step was
touched — `native/target` is still not cached, which is the same deliberate omission recorded beside
the Cargo cache step. `.github/copilot-instructions.md` prescribed the per-crate `cd native/<crate>`
shape and is corrected to the workspace form, per this row's own clause.

**One clause stays open for the arbiter's push**, the way BL-179 and BL-177 did: the gate's first
CI run is its own evidence and has not happened, because this ticket does not push.

`Source: BL-174 stage 2, 2026-08-23, at harness `a49d05a`. The absence of any cargo GATE is
`git -C ../aetheris grep -ln 'cargo fmt\|cargo clippy\|cargo test' -- scripts/ .github/ mix.exs lib/`,
which returns `.github/copilot-instructions.md` alone — a file that prescribes the commands and
runs nothing. `git -C ../aetheris grep -n cargo -- .github/workflows/ci.yml scripts/sprint.sh`
returns hits in `ci.yml` only, all of them `~/.cargo` cache paths, a cache key and one comment;
`sprint.sh` returns none. Positive control on the same pair, `mix`: 28 and 60.`

---

## The close — 2026-08-25

**One row, and it arrives with an edit rather than as a pure move.** BL-047's implementation closed on 2026-07-24 and its doc half closed the same day at harness
`af56a57`; the row was never moved, and its heading and summary-table row went on saying the doc half was pending
for a month. Both are superseded in place with dated notes below, the row is given its **first live `**Status:**`
field** — it never had one at depth 0 — and the preserved pre-implementation ticket under its `<summary>`
travels **byte-identical**, `**Status:** UNRULED` included. That block is not edited to say DONE: it is the
record of what the row declared BEFORE the work, and a post-implementation verdict written into it would
destroy the one thing it exists to hold.

**Placement follows the archive's own convention, not the header's general sentence.** `fda1466` states it:
arrivals land under the dated `## The close — …` container at EOF — where BL-181, BL-176, BL-177, BL-179,
BL-048 and BL-178 all went — rather than under the topic container reproduced from the open file (BL-047
sat under `## Drift apparatus (optional hardening)` there). A new round gets a new dated container.

### BL-047 — DONE 2026-07-24 · §5/§3 edits landed the same day, harness `af56a57` (#TBD)
**Status:** DONE
**Size:** M · **Priority:** medium · **Section:** Harness (aetheris/)

`[Superseded 2026-08-25, and corrected in place with this note per the harness supersession rule (`CLAUDE.md` §Continuous learning → Workflow patterns, *An artifact's kind decides how a correction is made; its push state decides only whether the correction may be silent*). This row is a PUBLISHED RECORD, not a ratified decision: the licence to correct it silently lapsed when it acquired readers, so the text is corrected and the correction is dated. The heading previously read:*

> `### BL-047 — DONE (impl) 2026-07-24 · §5/§3 edits pending §8 ratification`

*and the summary-table row in `backlog-2026-06.md` carried the same clause. Both were TRUE WHEN WRITTEN and became false the same day: `af56a57` (harness, 2026-07-24, `BL-047: land determinism-contract §5/§3 edits (approved, §8)`) landed the five held edits, and the row's own body recorded that it had — see the **§5/§3 edits (five): LANDED** paragraph below, which is RIGHT and is NOT rewritten to match anything. Superseded, therefore, and NOT R32, which governs a record that was wrong when written. The `(#TBD)` suffix is added at the same time and is not cosmetic: it makes this the row's TITLE section, which after the archive's title-first convention it now is — the only depth-0 section BL-047 owns. It is also true, in the sense `CLAUDE.md` fixes for it: BL-047 never had a GitHub issue and none is owed.]`


**Classification ratified (human, 2026-07-24): Option 3** — `git_*` is served-not-verified,
always, **not** lifted by `--allow-effects`. It is `:contained` for *safety* (local-only; no
`push`/`fetch`/`pull`/`clone`/`remote`, confirmed from source) but not verify-reproducible:
verify mounts no overlay, so the recorded repo is absent and `git_commit` embeds a
nondeterministic SHA. Re-executing would manufacture a spurious `:output_mismatch` — BL-049 at
family scale. The read/mutate line does **not** split the family; none reproduce.

`[Premise superseded 2026-08-26 (BL-186). The paragraph above says "verify mounts no overlay,
so the recorded repo is absent" — TRUE WHEN WRITTEN and false as of harness `a748861`, where
BL-184 gave verify an overlay whose lower layer is the recorded `sandbox_path`. **The
ratification is not disturbed and this row is not reopened**: Option 3 stands, `git_*` remains
served-not-verified and not lifted by `--allow-effects`, because what verify would now see is
the repo as it is NOW rather than as it was recorded, and `git_commit` still embeds a fresh
SHA. The reason moved; the conclusion did not. `determinism-contract.md` §5 carries the
restated premise. This row's text is not rewritten — corrected in place with this note, per
the harness supersession rule, on the same footing as the BL-184 heading note in this
container.]`

**Landed (harness `f41eb12` code+tests, `68d2614` notes):** `EffectClass` gains `@git_tools`
(single source of the **ten** names — read `git_status`/`git_diff`/`git_diff_staged`/`git_log`/
`git_show`, mutate `git_add`/`git_commit`/`git_checkout`/`git_cherry_pick`/
`git_cherry_pick_control`), referenced by both `@contained_tools` and the new
`@non_reproducible_tools`, plus `non_reproducible?/1`. `Verifier.plan_step/2` serves
non-reproducible tools **ahead of** the `--allow-effects` gate, so the git serve is
unconditional. Union / `@classes` / `known_tools/0` / completeness test / `@exec_server_tools`
(`[run_command]`) all untouched — git is served, never re-executed (3a; 3b rejected).

**The family is TEN, not eleven.** All three authorities agree on ten; the landed §5 said
"eleven" (×2), inherited from BL-042 — corrected in the held §5 edits, flagged not followed.

**Tripwire (BL-049 F1 forward):** every `git_*` the *registry* exposes must be in
`@non_reproducible_tools`, expected set derived from `Registry.names()` (a real source), not a
literal — mutation-checked (drop `git_commit` → guard fails naming it; completeness stays
green). A future `git_worktree` forgotten in the set fails loudly instead of shipping
re-executable.

**Done-check:** before-fix `git_commit` → `:error unknown_tool:git_commit`; after → `:served`
under default AND `--allow-effects`; git-only starts no worker; non-vacuity — git served while
a co-recorded `http_call` re-executes and egresses under `--allow-effects`. `mix test` 930/0,
format/credo/dialyzer/hex.audit green. `requires_worker` red set unchanged (BL-048 + BL-050).

**§5/§3 edits (five): LANDED, harness `af56a57` (§8, human-approved 2026-07-24).** §3 verify
row (re-execution qualified to reproducible output; served set gains `git_*`; non-guarantee
reframed), §5 three-classes split (`eleven`→`ten` ×2), the two-reasons-to-serve paragraph, the
opt-in rider (`--allow-effects` does not lift the git serve), residual bullet → resolved.
claude-ui r1 raised one non-blocking finding (F1: `non_reproducible?` scope) — answered by
keeping it name-only (`classify/2` is name-first, so a colliding external `git_status` is
`:contained` not `:uncontained`) plus the `@non_reproducible_tools ⊆ @contained_tools` guard;
closed at r2. Draft: `docs/reviews/bl-047-contract-draft.md`. Reviews r0/r1/r2 +
`bl-047-review-r1.md` in `docs/reviews/`.

`Source: BL-042 execution (routing gap demonstrated 2026-07-23 at 8021a59); classification
ratified + implemented 2026-07-24 at f41eb12.`

<details><summary>Original ticket (pre-implementation)</summary>

### BL-047 — Verify never re-executes the `git_*` family: exec-server routing gap + a taxonomy decision (#TBD)
**Status:** UNRULED
**Size:** M · **Priority:** medium · **Section:** Harness (aetheris/)

`Verifier` re-executes a recorded tool by sending it to the worker's own dispatch table
(`Client.execute` → `main.rs` `dispatch/3`), which knows only `read_file`, `list_dir`,
`write_file`, `http_call`. But `run_command` and the eleven `git_*` tools are **exec-server
MCP tools** in a live run (`loop.ex` `@exec_server_tools`, `dispatch_mcp_tool/4`). So every
member of that family re-executed as `unknown_tool:<name>` — a per-step `:error`, never a
comparison — while determinism-contract §5 claimed `:contained` tools are "re-executed and
compared".

Demonstrated at BL-042 against unmodified `8021a59`, before any fix:

```
%{error: "unknown_tool:run_command", status: :error, actual_output: nil,
  recorded_output: "{\"duration_ms\":20,\"exit_code\":0,\"stderr\":\"\",\"stdout\":\"connected\\n\"}"}
```

**BL-042 routed `run_command` only** — the tool its own containment proof requires, whose
re-execution BL-025 already ratified, and whose new hazard (egress) is exactly what BL-042's
network namespace contains. The `git_*` family was deliberately left unrouted rather than
fixed by the same three lines, because routing it is not merely a bug fix:

**The real question is whether mutating git operations should re-execute under verify at
all.** `git_add`, `git_commit`, `git_checkout`, `git_cherry_pick` and
`git_cherry_pick_control` mutate a repository. Re-executing `git_commit` against a sandbox
whose HEAD has moved does not reproduce a recorded step, it writes a new one; `git_checkout`
can destroy working-tree state that the recorded run did not have. The read-only members
(`git_status`, `git_diff`, `git_diff_staged`, `git_log`, `git_show`) are a different case
entirely. This is a taxonomy decision of the same weight as BL-025's three classes and it
should be **decided**, not inherited from an accident of routing — which is the whole reason
BL-042 did not quietly extend its own fix over the family.

**Options to adjudicate (not a menu to pick from silently):** route them all as `:contained`;
split the family, re-executing the read-only members and reclassifying the mutating ones as
`:uncontained` (record-and-served); or declare the family unsupported under verify with an
explicit status distinct from `:error`.

**Done when:** the classification of each `git_*` tool is decided and recorded in §5 with a
human-approved edit (§8), the implementation matches the decision, and a recorded `git_*`
trajectory verifies to whatever verdict that decision implies — never to
`unknown_tool:<name>`. §5's routing-gap paragraph and §3's verify row (both landed by BL-042)
are updated to remove the named gap.

**Pre-wired by BL-049, so read this before routing (BL-049 r1 F5).** The volatile-metadata
strip is already in place for `git_*` on the **record** side: it keys off the exec-server id at
dispatch (`loop.ex`, `dispatch_mcp_tool/4` → `exec_server_payload/2`), so all twelve routed
tools are recorded with `duration_ms` in the step envelope, `git_*` included, and
`VolatileMetadataTest` unit-covers the `git_*` response shape. The **verify** side is not:
`Verifier`'s `@exec_server_tools` is `run_command` alone, and both `reexecute/3` and
`normalize_recorded/2` key off it. So routing the family is one edit to that list — but the
invariant between the two lists is **subset containment**, not equality: a name in `Verifier`'s
list that `Loop` does not route would be normalized on read yet recorded unstripped, which is
BL-049's failure mode reintroduced for exactly that tool. Confirm both sides agree when you
route them.

`Source: BL-042 execution, demonstrated 2026-07-23 at 8021a59. §5 correction landed with
BL-042's contract edit; this row closes the gap that correction names. Pre-wiring note added
from BL-049 review r1, 2026-07-24.`

</details>

**THE CLOSE — 2026-08-25. Done-when met on all four clauses, RE-DERIVED at harness `7436aa1` rather than inherited from the row's own 2026-07-24 done-check.**

1. *Classification decided and recorded in §5 with a human-approved (§8) edit.* `docs/aetheris/determinism-contract.md` §5 (`## 5. Verify re-execution: effect classes and containment`) carries it at `:221-240`: the ten `git_*` tools are `:contained` for safety and **served, not re-executed**, and that serve is not lifted by `--allow-effects`. The §8 edit is `af56a57`, resolved as an object rather than quoted — `git -C ../aetheris cat-file -t af56a57` → `commit`, `af56a57a9f5d7a460688054077cdedfd4c0902b1`, 2026-07-24, touching `docs/aetheris/determinism-contract.md` alone, 42 insertions / 19 deletions.
2. *The implementation matches the decision.* `lib/aetheris/execution/effect_class.ex:62-65` is `@git_tools`, the ten names single-sourced; `:70` folds them into `@contained_tools`; `:80` is `@non_reproducible_tools @git_tools`; `:165-166` is `non_reproducible?/1`. `verifier.ex:488` records the `⊆` invariant.
3. *A recorded `git_*` trajectory verifies to the verdict the decision implies, never to `unknown_tool:<name>`.* Established at `f41eb12` by the row's own done-check, and **re-derived independently at `7436aa1` by the BL-184 round**, whose subject is verify's re-execution behaviour and which states the property from the outside while sizing a different hazard: *"`git_*` is served and never re-executed (BL-047)"* (`docs/backlog-2026-06.md`, BL-184, the Population paragraph). Cited, not re-narrated — that round is BL-184's record and stays there.
4. *§5's routing-gap paragraph and §3's verify row no longer name the gap.* §5 `:228-240` now states the gap in the PAST tense and names both resolutions (BL-042 routes `run_command`; BL-047 decides `git_*` the other way). §3's verify row names the `git_*` family as served-not-verified in both its guarantee and its non-guarantee column. Neither says `unknown_tool` as a live defect.

**WHAT THIS CLOSE COSTS, named rather than left to be discovered.** This row moves to `backlog-2026-06-closed.md`, and that file **is not in the project-knowledge store**. A manifest row for it is added in the commit after this one, which changes what the *next* export carries and uploads nothing — so from this commit until an export actually runs, **BL-047 leaves the store's sight**: a store-side reader searching the exported backlog for `BL-047` gets nothing back, where before this commit they got the open row. That is the price of the move and it is paid deliberately; the alternative is a terminal row left in the open file, which is the invariant `fda1466` was written to repair. The id remains the address and resolves over the union from the repo.

---

## The close — 2026-08-26

**One row, arriving as a move plus a new depth-0 `**Status:**` field and a close record.** BL-184's
heading is superseded in place with a dated note: it named the defect (*"re-execution mounts no
overlay"*), which was true when written and is false as of harness `a748861`. The body below the
heading travels **byte-identical** — it is the record of what the row declared before the work,
including its four-candidate OPEN DESIGN QUESTION, and rewriting it to match the answer would
destroy the one thing it exists to hold. The close record is appended below it, not woven into it.

**Placement follows the archive's own convention**, as `fda1466` states it and `d0e4213` last
applied it: an arrival lands under a new dated `## The close — …` container at EOF, not under the
topic container reproduced from the open file (BL-184 sat under `## Harness (aetheris/)` there).

### BL-184 — DONE 2026-08-26 · verify mounts an overlay; a failed mount stops attesting itself (#TBD)
**Status:** DONE
**Size:** M · **Priority:** high · **Section:** Harness (aetheris/)

`[Superseded 2026-08-26, corrected in place with this dated note per the harness supersession rule
(`../aetheris/CLAUDE.md` §Continuous learning → Workflow patterns, *An artifact's kind decides how a
correction is made; its push state decides only whether the correction may be silent*). This row is a
PUBLISHED RECORD, not a ratified decision, so the licence to correct it silently lapsed the moment it
acquired readers.*

*TWO LINES CHANGED and no others. (1) The heading, which previously read:*

> BL-184 — `mix aetheris verify` writes into the operator's real repository: re-execution mounts no overlay (#TBD)

*(2) The depth-0 `**Status:**` field, `OPEN` -> `DONE`. That line is REPLACED rather than joined by a
second one: BL-184 carries no `<details>` block, so unlike BL-047 at `d0e4213` there is no archived
status to preserve beside a new live one, and two depth-0 fields would fail
`backlog_status.py --check` outright.*

*Both were TRUE when written. This is a SUPERSESSION, not R32 — neither was wrong from the start, and
the heading's *"re-execution mounts no overlay"* was an accurate statement of harness `7436aa1`.*

*EVERYTHING BELOW THIS NOTE IS BYTE-IDENTICAL to the row as it stood in `docs/backlog-2026-06.md` at
`ed8b6eb`, its four-candidate OPEN DESIGN QUESTION included. It is the record of what the row declared
BEFORE the work; the answer is appended after it, never woven into it. sha256 of that remainder,
computed before the write: `ddd3bdb4f755bffb5d946bd23f3cf8ddceb2645c8eaac2eedc3d55ff9f312c99`.]*


**The hazard.** A bare `mix aetheris verify <trajectory>` — no flags — re-executes the
recorded `write_file` steps **into the run's real `sandbox_path`**. That path is the
operator's working tree, not a copy of it. Verifying a recorded run therefore mutates the
repository the run was recorded in, as a side effect of asking whether it reproduces.

**What was demonstrated.** In the BL-047 read-only round, a throwaway clone used as the
sandbox came back dirty after a bare verify: `git status` reported
`M test/fixtures/m10/broken_source.ex`. That file is tracked
(`aetheris` `test/fixtures/m10/broken_source.ex`, 630 bytes) and the verify had no business
writing it. This row records that demonstration as its origin; the mechanism below was
resolved independently against `aetheris` `7436aa1` rather than carried from it.

**Mechanism — anchors resolved at `aetheris` `7436aa1`.**

- `Verifier.execute_planned_steps/4` (`lib/aetheris/execution/verifier.ex`, `:110`) starts
  the re-execution worker with `run_id`, `sandbox_path`, `network_namespace` and
  `mode: :verify` (`:113`–`:123`). It passes **no `:overlay`**. The word `overlay` does not
  occur in `verifier.ex` at all, while `Aetheris.Worker.Client` reads `:overlay` as a real
  start option and forwards it into the init payload (`lib/aetheris/worker/client.ex:232`,
  `:117`) — so this is a default that was never set, not a capability the worker lacks.
  §5 of the determinism contract states the same fact from the other side, as a
  *reproducibility* premise: *"verify passes no overlay, so OverlayFS is not mounted on this
  path"*.
- With no overlay, the worker's mount namespace confines writes to `sandbox_path` — and
  `sandbox_path` **is** the operator's tree. `Verifier.resolve_sandbox_path/2` (`:210`) takes
  the caller's `:sandbox_path` when given and otherwise reads `meta["sandbox_path"]` from the
  trajectory (`:213`), which is where the recorded run actually ran.
- `write_file` re-executes because it is *supposed* to: `EffectClass.classify("write_file")`
  is `:contained` and `EffectClass.non_reproducible?("write_file")` is `false`, so
  `plan_step/2` (`:154`) sends it down the `:execute` arm. **There is no misclassification
  here.** The tool is correctly classed, the sandbox correctly confines it, and the
  destination is wrong — which is why no test asserting effect classes can catch this.

**It fires with `--allow-effects` OFF, so the documented dangerous flag is not the guard.**
That flag reaches exactly two things: the `:uncontained` serve arm in `plan_step/2` (`:162`),
and `network_isolated = not allow_effects` in `execute_planned_steps/4` (`:111`). Neither
touches a `:contained` tool's re-execution or its write destination. An operator following
`docs/aetheris/runbook.md` §Verifying a run exactly, passing nothing, gets the writes — and
the runbook offers `--allow-effects` as *the* thing to be careful about.

**Population.** In this machine's trajectory corpus at `7436aa1` — `priv/runs/*/`, which is
gitignored (`.gitignore:55`), so this is working state and not a claim about the tree —
`python3` over `priv/runs/*/trajectory.json` counting `tool_called` payloads finds 43,665
trajectories, of which **10** carry any `git_*` call and **9** of those also carry
`git_add`/`git_commit`; **114** carry a `write_file` call. Re-derive with the census script
rather than trusting these figures: they move whenever a run is recorded or swept. The
`write_file` figure is the one that sizes this row — `git_*` is served and never
re-executed (BL-047), so the git population is the *adjacent* hazard, not this one, and it
matters here only because those nine are recorded runs that committed to a real repository
and whose `write_file` neighbours would be replayed into it.

**The runbook reads as isolation and is not.** `docs/aetheris/runbook.md:250` says verify
re-executes "in a fresh sandboxed worker". Both words are true and neither means what a
reader takes from them: the worker is new, and it is namespaced, and the sandbox root it is
confined to is the operator's own directory. **That sentence is deliberately left alone** —
what it should say depends on which fix below is taken.

**OPEN DESIGN QUESTION — stated, not answered.** This row does not choose, and the round
that filed it was fenced from choosing. The candidates, with what each costs:

1. **Overlay.** Pass `:overlay` from `Verifier`, so re-execution lands on a throwaway upper
   layer. Preserves the verdict; the writes become invisible, including the ones an operator
   might want to inspect. Interacts with `sandbox.rs`'s existing overlay path, which record
   runs already use.
2. **Refusal.** Verify declines to re-execute any write-effecting `:contained` tool and
   serves it instead, as `git_*` is served. Safe and cheap; shrinks what verify verifies, and
   needs a third serve reason beside the two that now exist.
3. **Prompt.** Verify names the destination and asks before writing. Honest, and unavailable
   on the non-interactive paths verify is actually run from.
4. **Flag.** Re-execution of write-effecting tools becomes opt-in, off by default. Mirrors
   `--allow-effects`; adds a second effects flag whose relationship to the first has to be
   specified, and defaults verify to a weaker verdict for everyone.

**Done when:** the question above is answered and recorded with a human-approved edit where
the answer is normative (determinism-contract §5 if the taxonomy moves, §8 per its own change
discipline), the implementation matches the answer, a bare verify over a trajectory
containing a `write_file` step leaves the sandbox tree unmodified *or* says plainly that it
will not, and `runbook.md`'s "fresh sandboxed worker" sentence is corrected to whatever the
answer makes true.

`Source: the BL-047 read-only round (the demonstration). Mechanism, classifications, anchors
and corpus figures resolved at `aetheris` `7436aa1` by the round that filed this row, which
was fenced from repairing it. Filed 2026-08-25.`

---

**THE CLOSE — 2026-08-26. The OPEN DESIGN QUESTION above is answered: CANDIDATE 1, OVERLAY.
Anchors RESOLVED against the commits that carry them, not transcribed from the round that filed
this row.** Two harness commits: `7faa269` (C1) and `a748861` (C2).

**What was ruled, and the one thing the row's candidate 1 did not contain.** Candidate 1 said
*"Pass `:overlay` from `Verifier`, so re-execution lands on a throwaway upper layer."* That is C2.
It rests on a premise the row could not have known was false: that `containment.overlay` reports
whether the mount happened. It did not. `mount_overlay` printed a failed `libc::mount(2)` and fell
through to a trailing `Ok(())`, so `main.rs` set `overlay_established = true` and the `ready`
handshake published `"overlay": true` for a sandbox with no overlay. A design making every verify
depend on that field had to make it honest first, which is why the fix is two commits and why C1
landed green before C2 was written.

1. *The question is answered and recorded with a human-approved edit where the answer is
   normative.* **The taxonomy did not move**, which is the condition this clause attaches to:
   `EffectClass.classify("write_file")` is still `:contained`, `non_reproducible?/1` is still
   `false` for it, and it is still re-executed. Nothing about the three classes changed — what
   changed is the destination a `:contained` re-execution writes to, which §5 documents as fact
   rather than declares as taxonomy. So no §8 edit is owed *by this clause*.
   **`determinism-contract.md` was NOT edited, and it now needs to be.** Four passages in §5 are
   falsified by `a748861` and one of them carries BL-047's argument. That is filed as **BL-186**,
   which stays open — it is deliberately NOT recorded inside this row, because a finding written
   into the row that the same commit closes has a record and no executor.
2. *The implementation matches the answer.* `lib/aetheris/execution/verifier.ex:122` passes
   `overlay: verify_overlay(allow_effects, verify_run_id, sandbox_path)` into the `Client.start`
   at `:113`–`:124` — the option the row identified as absent at `7436aa1`. `verify_overlay/3`
   (`:175`, `:177`) returns `nil` under `--allow-effects` and otherwise derives the map through
   `Agent.Supervisor.derive_overlay/3` (`lib/aetheris/agent/supervisor.ex:100`), which was split
   out of `derive_overlay/1` (`:84`, `:86`) so there is one builder rather than two.
3. *A bare verify over a trajectory containing a `write_file` step leaves the sandbox tree
   unmodified, **or** says plainly that it will not.* **The first disjunct, not the second.**
   `test/aetheris/execution/verify_overlay_test.exs` asserts it from the host after the worker
   exits — `refute File.exists?(Path.join(sandbox_path, "written.txt"))` on a re-executed
   `write_file`, with `report.verified == 1` beside it so the assertion is about a step that
   really ran. Its paired opposite asserts the file **is** there under `--allow-effects`.
   Mutation-checked: removing the `:overlay` option reds the first test with the file in
   `/tmp/test-verify-overlay-130/written.txt`.
4. *`runbook.md`'s "fresh sandboxed worker" sentence is corrected to whatever the answer makes
   true.* `../aetheris/docs/aetheris/runbook.md:255` onward now states where a re-executed write
   lands, gives the path shape, says the layer is not deleted so the writes can be inspected, says
   nothing reads it back, and says verify declines when the mount fails. `:308` states what
   `--allow-effects` changes. The old wording is quoted there rather than merely replaced, so a
   reader working from memory of it is corrected.

**AND THE REFUSAL, which no candidate contained.** Verify declines a requested-but-failed overlay
rather than degrading (`client.ex:360` `startup_verdict/5`, the arm at `:380`; the operator message
at `verify.ex:148`). A warning-and-continue would have reinstated this row's defect under a message
nobody reads. `--allow-effects` cannot reach that arm, because it requests no overlay — which is
what makes "writes through" a waiver rather than a refusal in different words. The governing
sentence, now in `runbook.md:308` and in `verifier.ex`: **`--allow-effects` waives DESTINATION and
EFFECT, never CAPABILITY** — which is why it drops the network namespace and the write overlay and
does not drop the seccomp filter (BL-056).

**WHAT THIS ROW DOES NOT CLAIM, stated because the difference is invisible from the outside.** The
fix is **established on this platform** — Linux `6.8.0-136-generic`, unprivileged user namespaces
permitted, `overlay` in `/proc/filesystems`, verified by a live worker run under the exact verify
start options. It is **not** established for a host that cannot mount an OverlayFS, and this row
does not assert that it is. What covers those hosts is not a demonstration but **C1's honest
attestation**: where the mount does not take, `containment.overlay` now reads `false` instead of
`true`, so verify **refuses** with a message naming the destination and the `SYS_ADMIN` requirement
rather than silently writing into the operator's tree. The row's hazard is closed there by a
refusal, not by an overlay — which is a different thing and is worth reading as one. What is not
covered anywhere is a *recorded* run on such a host, which continues into `sandbox_path` by the
documented `overlay_base_dir: nil` fallback; that is unchanged by this row and deliberately so.

**Also not claimed: that anything runs these checks by default.** The two live destination tests are
`:requires_worker`, which `test/test_helper.exs` excludes — they pass when run and nothing runs them
in the default `mix test`. The refusal is asserted at `startup_verdict/5` in
`containment_gate_test.exs`, which **does** run in the default gate; it tests the policy, not the
one line in `Client.init/1` that supplies `overlay_requested`, and that line is covered by nothing.
The A1 round's read (b) found the whole overlay facility living behind exclusions and this row does
not change that. What it changes is that the property is asserted at all.

**The demonstration that opened this row is not re-run and is not owed.** It was a throwaway clone
coming back `M test/fixtures/m10/broken_source.ex` after a bare verify; the property it demonstrated
is now asserted by a test with a mutation control, which is a better instrument than a second
anecdote. The fixture is an agent input and no test reads it, which is why nothing went red when a
verify wrote to it — that remains true and is why the test had to be written rather than found.

**WHAT THIS CLOSE COSTS, named rather than left to be discovered.** This row moves to
`backlog-2026-06-closed.md`, which is manifest-tracked (`d0e4213`) but whose row goes stale the
moment this commit lands. From here until an export actually runs, **BL-184 leaves the project-
knowledge store's sight**: a store-side reader searching the exported backlog for `BL-184` gets
nothing where before they got the open row. Same cost `d0e4213` paid and named for BL-047, paid for
the same reason — the alternative is a terminal row left in the open file. The id remains the
address and resolves over the union from the repo.

`Source: implemented 2026-08-26 across harness `7faa269` (C1) and `a748861` (C2), and closed here.
The A1 gate round of 2026-08-25 established that OverlayFS is available to a verify run on this
platform and found the attestation defect as its §F1; its packet is a session scratchpad file
(`bl-184-a1-gate-packet.md`) and is in neither tree, so it is named rather than cited.`

---

## The close — 2026-08-26 (second round)

**A second container on the same date, deliberately.** The convention `fda1466` states and
`d0e4213` last applied is that an arrival lands under a new dated `## The close — …` container at
EOF. The container above is dated 2026-08-26 and opens *"One row, arriving as a move"* — adding a
second row to it would falsify that sentence about a round it does not belong to. So the date is
qualified rather than reused, and the two rounds stay separable by a reader.

### BL-186 — DONE 2026-08-26 · §5's overlay premise restated at every surface that asserted it (#TBD)
**Status:** DONE
**Size:** S · **Priority:** high · **Section:** Harness (aetheris/)

`[Heading superseded 2026-08-26, corrected in place with this dated note per the harness
supersession rule (`../aetheris/CLAUDE.md` §Continuous learning → Workflow patterns, *An artifact's
kind decides how a correction is made; its push state decides only whether the correction may be
silent*). This row is a PUBLISHED RECORD, not a ratified decision. The heading previously read:*

> `### BL-186 — `determinism-contract.md` §5 says verify mounts no overlay, and since BL-184 it does (#TBD)`

*and the depth-0 `**Status:**` field is REPLACED, `OPEN` -> `DONE`; BL-186 carries no `<details>`
block, so unlike BL-047 at `d0e4213` there is no archived status to preserve beside a live one, and
two depth-0 fields would fail `backlog_status.py --check` outright. The heading was TRUE WHEN
WRITTEN — §5 did say it — and is false as of harness `ca11d35`. A SUPERSESSION, not R32.*

*EVERYTHING BETWEEN THIS NOTE AND THE CLOSE RECORD IS BYTE-IDENTICAL to the row as it stood in
`docs/backlog-2026-06.md` at `5c57d40`, its four-site divergence table and its Done-when included.
It is the record of what the row declared BEFORE the work; the answer is appended after it, never
woven into it. sha256 of that body, computed before the write: `efbf88b8741ec0b45e735b10c28c72c5377f8d1d5ddc5a7996b7c04b932e34b3`.]`

Filed 2026-08-26 by the round that created the divergence, in the commit that closed BL-184 — a
deferred finding needs an executor in the round it is deferred, and it needs a row that STAYS OPEN,
which is why it is here and not inside BL-184's close record.

**Why this is not BL-184's to fix.** §8 of that document makes any edit altering a guarantee a
human-approved change in the review cycle. The BL-184 round was fenced from making one and reported
instead. This row is the executor for the edit.

**The divergence — four passages, anchors resolved at `aetheris` `a748861`.** All in §5
(`## 5. Verify re-execution: effect classes and containment`).

| site | what it says | status |
|---|---|---|
| `:271`–`:272`, §Containment boundary (from source) | "verify passes no overlay, so OverlayFS is not mounted on this path" | **FALSE.** Direct contradiction of `verifier.ex:122`. |
| `:237`, §The three classes | BL-047: `git_*` "are not verify-reproducible — verify reconstructs no repo working-tree or history (**it mounts no overlay**)" | **Premise false, conclusion intact.** |
| `:400`, §Reporting: served is not verified | the same argument restated: "because verify mounts no overlay, so the recorded run's repo working-tree and history are absent" | **Same.** Two surfaces of one argument. |
| `:291`, §When containment cannot be established | "Verify depends on **two** containment primitives" — with `:302` citing `startup_verdict/4` and the subsection enumerating two refusal messages | **Three, `/5`, three messages.** |

**The `git_*` sites are the ones that matter, and BL-047 is NOT reopened.** The overlay's lower
layer *is* `sandbox_path`, so a re-executed `git_*` would now see a repo rather than an absent one
— the stated premise fails. The conclusion does not: the tree it would see is the repo **as it is
now**, not as it was when the run was recorded, and `git_commit` would still embed a fresh
nondeterministic SHA. So `git_*` remains served-not-verified, on a restated reason. **A reader of §5
today gets a true conclusion from a false premise**, which is the specific harm here: the next
person to reason from that premise will reason wrongly, and nothing in the text warns them.

**Two constraints on the edit, so the next round does not have to re-derive them.**

- **De-numeralise `:291`'s "two", do not raise it to three.** It is a count over a set that has now
  grown twice, and correcting the number preserves the mechanism that broke it — the standing rule
  under `CLAUDE.md` §Learning — m6-cloudcost. The `startup_verdict/4` citation at `:302` is a
  different thing and is simply stale: repoint it.
- **`:237` and `:400` are one argument with two surfaces, so they change together or not at all.**
  Editing one leaves the other asserting the false premise, and a reader who finds the stale one
  first has no way to know it was superseded.

**Done when:** §5 no longer asserts that verify mounts no overlay; the `git_*` serve reason is
restated from "there is no repo" to "there is no recorded-state repo" at both `:237` and `:400`;
`:291`'s count is de-numeralised and its `startup_verdict/4` citation and two-message enumeration
are brought current; and the edit is human-approved per §8 in the same review cycle.

`Source: BL-184 C2 (harness `a748861`) created the divergence; the round reported it rather than
editing, per §8. Sites resolved at that commit, not transcribed.`

---

**THE CLOSE. Two commits: harness `ca11d35`, agents this one.** The §8 approval is the human's and
is given by their push of this round; the edit was authored by the arbiter and landed as given.

**Done-when, clause by clause.**

1. *§5 no longer asserts that verify mounts no overlay.* §Containment boundary loses *"verify
   passes no overlay, so OverlayFS is not mounted on this path"* and gains a paragraph stating that
   a default verify mounts an OverlayFS whose lower layer is the recorded run's `sandbox_path` —
   confirmed at source, not inferred: `Agent.Supervisor.derive_overlay/3` builds the map with
   `"lower" => sandbox_path`, and `Verifier.verify_overlay/3` returns `nil` under `--allow-effects`
   and otherwise derives a fresh base per invocation.
2. *The `git_*` serve reason is restated from "there is no repo" to "there is no recorded-state
   repo".* Done at **all four** §5 surfaces under R1 — the `:contained` bullet, §Reporting's
   restatement, its `--allow-effects` clause, and §The opt-in — not the two this row named. The
   row's own constraint was that `:237` and `:400` are one argument with two surfaces; reading the
   section for the CLASS rather than the phrase found two more carrying the same premise, and
   leaving either would have left a reader who meets the stale one first with no warning.
3. *`:291`'s count is de-numeralised and its `startup_verdict/4` citation and two-message
   enumeration are brought current.* The count is de-numeralised rather than raised to three, per
   the standing rule under `CLAUDE.md` §Learning — m6-cloudcost, and the paragraph now names
   `startup_verdict/5` as the authority so a primitive added there does not stale it. The citation
   is repointed — arity resolved from `client.ex`, not transcribed. The overlay refusal joins the
   two message blocks, its text resolved by rendering `Verify.overlay_unavailable_message/0` and
   diffed against the published block: identical. The paragraph that followed argued from *how
   many* messages there are; it is rewritten onto the axis that actually distinguishes them —
   whether `--allow-effects` is the way past.
4. *Human-approved per §8 in the same review cycle.* §8 prescribes approval, not a block form, so
   the dated block follows this document's own convention at its `:15`
   (`**Amended … (BL-nnn, human-approved in-cycle per §8):**`).

**BEYOND THIS ROW'S FOUR SITES, because the table above was a lead and not a census.** Six harness
surfaces that *instruct* carried the same false premise and take the same clauses: `effect_class.ex`
(three — the `@git_tools` comment, the `@non_reproducible_tools` comment, and
`non_reproducible?/1`'s `@doc`), `verify_report.ex`'s `serve_reason` typedoc, `verifier.ex`'s
two-reasons comment, and `verify_git_test.exs`'s moduledoc. §The opt-in gains the overlay waiver and
its *"both guards"* is de-numeralised; `runbook.md` §Verifying a run names what an operator buys
reaching for `--allow-effects` past a failed mount — the network waiver and the `:uncontained`
re-execution come with it, and there is no flag that waives the overlay alone.

**DELIBERATELY NOT EDITED, a ruling rather than an omission.**
`docs/aetheris/milestones/bl-047-implementation-notes.md` carries the false premise and stays as it
is: a point-in-time milestone record, where rewriting to match the present erases the context it
exists to preserve. R31 — arrival decides. BL-047's archived row is corrected the other way, in
place with a dated note, because a row is a published record rather than a milestone snapshot. **Its
text is not rewritten and BL-047 is not reopened**: Option 3 stands, `git_*` remains
served-not-verified and not lifted by `--allow-effects`.

**WHAT THE CONCLUSION RESTS ON NOW.** Not *"there is no repo"* — there is one, and since BL-184 it
is the recorded `sandbox_path` itself. It is that the repo a re-executed `git_*` op would read is
that tree **as it is now**, not as it was when the step was recorded, and that `git_commit` embeds a
fresh SHA either way. That holds under `--allow-effects` too, where the overlay is waived and the op
reads `sandbox_path` directly — the same repo in the same present state. The premise moved; the
conclusion did not.

**Gates.** Harness: `deps.get`, `hex.audit`, `compile --warnings-as-errors`, `format
--check-formatted`, `credo --strict`, `dialyzer`, `test` (981 tests, 0 failures, 135 excluded), and
`cargo test` in both native crates (34 and 17 passed). Agents: `drift_check.py --strict`,
`backlog_status.py --check` and `--census`, and the Python whole-suite gate.

**WHAT THIS CLOSE COSTS.** This row never appeared in an export: filed and closed between
boundaries, it leaves the open file having never been in the store's copy of it. The archive row is
born green — pinned at the commit that last touched the file, which makes check 8 compare equal —
and that is a currency result, never evidence of an upload. Same cost `d0e4213` and the container
above named, paid for the same reason.

`Source: authored by the arbiter; landed 2026-08-26 across harness `ca11d35` and this commit. The
divergence was created by BL-184 C2 (`a748861`) and filed by that round rather than fixed, per §8.
Every anchor here was resolved against the tree at the commit under test, not carried from the
filing row.`

---

## The close — 2026-09-10

**One row, arriving as a move, and the first row this backlog has closed on work an autonomous
session produced.** BL-065 was implemented end to end by the ticket session of backlog-loop
experiment run 1, batch-reviewed and accepted as-is, and merged to harness `main` at `185b4c9`.
The review packet is `../aetheris/docs/reviews/bl-065-review.md` and the run's own record is
`../aetheris/docs/aetheris/research/experiments/auto-run-1-report.md` §6; both live in the harness
repo, so they are repo-qualified here rather than cited as if they resolved in this one.

**Placement follows the archive's own convention**, as `fda1466` states it and the 2026-08-26
containers last applied it: an arrival lands under a new dated `## The close — …` container at EOF,
not under the topic container reproduced from the open file (BL-065 sat under
`## Harness (aetheris/)` there). A new round gets a new dated container.

**The row was closed in two commits, not one, and the split is the point.** At `e8a73ab` this
repository recorded the implementation while the work sat on an unmerged local branch and
deliberately HELD the status at `OPEN` — `scripts/backlog_status.py --check` enforces that a
terminal row lives in this file, and declaring DONE against a branch `main` did not carry would
have made the archive assert a fix a fresh clone did not have. The merge is what made the
declaration true; this commit is what makes it. A row is terminal when the code is, not when the
review is.

### BL-065 — DONE 2026-09-10 · a failed trajectory write no longer reports the run as `done` (#TBD)
**Status:** DONE
**Size:** S · **Priority:** medium · **Section:** harness (`../aetheris/lib/aetheris/agent/server.ex`)

`[Heading superseded 2026-09-10, corrected in place with this dated note per the harness
supersession rule (`../aetheris/CLAUDE.md` §Continuous learning → Workflow patterns, *An artifact's
kind decides how a correction is made; its push state decides only whether the correction may be
silent*). This row is a PUBLISHED RECORD, not a ratified decision. The heading previously read:*

> `### BL-065 — A failed trajectory write still reports the run as `done` (#TBD)`

*and the depth-0 `**Status:**` field is REPLACED, `OPEN` -> `DONE`; BL-065 carries no `<details>`
block, so there is no archived status to preserve beside a live one, and two depth-0 fields would
fail `backlog_status.py --check` outright. The heading was TRUE WHEN WRITTEN — the defect was real
at harness `6f89261` and at every commit before it — and is false as of harness `185b4c9`. A
SUPERSESSION, not R32.*

*EVERYTHING BETWEEN THIS NOTE AND THE **Implemented, reviewed and merged** PARAGRAPH IS
BYTE-IDENTICAL to the row as it stood in `docs/backlog-2026-06.md` at `f29f6fd`, its Done-when
included. It is the record of what the row declared BEFORE the work; the answer is appended after
it, never woven into it. sha256 of that body, computed before the write:
`35cdaa462a36c9eab4d3f5006c6380cae43a6c57b79752a8a3933f971bb5b0fa`.*

*WHAT FOLLOWS IT IS NOT BYTE-IDENTICAL AND IS NOT CLAIMED TO BE.* Those paragraphs are the close
record this repository wrote at `e8a73ab`, REWRITTEN here to cite the merge and to drop the
hold-at-OPEN language, whose stated condition — *"its terminal declaration and archive move belong
to whoever merges `auto/run-1`"* — has now been met. Nothing depended on the earlier wording: it
was written and superseded between export boundaries, so it never reached the store, and the text
it replaces is readable at `e8a73ab`.]`

Raised by BL-030 r1 and carried through r2. Not introduced there — latent since
the write was added.

**The defect.** `execute_run/…` calls the trajectory write and then branches on a
*different* value (`server.ex:680-684`):

```elixir
    Aetheris.Trajectory.File.write(config.run_id, events, meta)

    case result do
      :ok -> GenServer.cast(server_pid, {:run_complete, :done})
      {:error, reason} -> GenServer.cast(server_pid, {:run_failed, reason})
    end
```

`result` is the **loop's** result. `File.write/3`'s `{:ok, path} | {:error, …}` is
never examined, so a disk-full, permission or rename failure produces a run whose
status reads `done`, with no trajectory file and no error recorded anywhere. The
same pattern is at the resume path (`server.ex:952`).

**Class:** Silent-wrong-answer (harness `CLAUDE.md`) — the failure renders as a
normal completion, which is exactly what lets it survive. Ask what a broken write
looks like from outside: identical to a successful one.

**Consequence already relied upon.** BL-030 r1's completion transition treats
terminal status as "the harness has finished writing", *not* "the file exists",
and its reload is best-effort for this reason — on this path Rig stays in the
reconstructed view with its terminal banner. That degradation is correct and
should stay correct after this is fixed; fixing it here means the operator also
learns the write failed.

**Done when:** a failed trajectory write is surfaced — the run does not report
`done` on a write failure, or the failure is recorded as an event/log with the
reason — and both call sites (`:680`, `:952`) are covered. Exercise the gap
explicitly (a write forced to fail must not produce a `done` run), not just the
happy path.

**Implemented, reviewed and merged.** Produced 2026-09-10 by the autonomous ticket session of
backlog-loop experiment run 1, batch-reviewed and **ACCEPTED AS-IS**, no edit required before
landing. Committed as harness `e28e009` on `auto/run-1` and merged to harness `main` at
**`185b4c9`** (`--no-ff`; the branch is kept rather than deleted, the run-1 report citing it).
Both call sites bind `Aetheris.Trajectory.File.write/3`'s return value and branch on a new private
`run_outcome/2` (three clauses) instead of on the loop's `result` alone; a write failure now casts
`{:run_failed, {:trajectory_write_failed, reason}}` rather than `{:run_complete, :done}`. Two new
tests, one per call site, red before the fix and green after, with per-site mutation confirming
each test binds to its own call site rather than both binding to `:680`. BL-030 r1's degradation is
preserved: terminal status still means *the harness has finished writing*, not *the file exists*,
and the reload path is untouched.

**Done-when, arm by arm.** The first arm — *the run does not report `done` on a write failure* — is
**discharged at both call sites**. The second arm — *or the failure is recorded as an event/log
with the reason* — is a disjunct, so this Done-when is satisfied without it; it remains
**undischarged by design**, the run-1 addenda having ruled that branch unavailable for this row.
The reason reaches only a transient `WaitRegistry` payload today: `handle_cast({:run_failed, …})`
appends no event and SQLite stores only `"failed"`. That is a real residue and it is deliberately
**not filed** — it is the row's own second arm, narrowed by ruling rather than left undone, and
recorded here so a later reader meets it rather than rediscovers it.

**One reviewer finding, recorded and not reopened.** The loop-failed-**and**-write-failed
combination is untested. `run_outcome/2`'s clause 1 gives the loop's own reason precedence, and
dialyzer confirms all three clauses reachable, but the existing adapter-error tests exercise clause
1 with a *successful* write only. In a change whose point is *stop discarding the write result*,
the one arm that deliberately discards it rests on reading rather than on a test. It did not block
acceptance — a run whose loop failed already does not report `done`, so the Done-when is met — and
it is a candidate follow-up, not a row.

**Gates at the merge.** `mix test` on harness `main` at `185b4c9`: **983 tests, 0 failures, 135
excluded**, exit 0 — 981 before the merge plus the two new ones. At the ticket commit the session
also ran `mix format --check-formatted`, `mix credo --strict`, `mix dialyzer` (0 errors) and
`mix compile --warnings-as-errors`, all exit 0. **`mix hex.audit` is RED, exit 1** — two upstream
`mint` advisories, unrelated to this change, carried openly and now tracked as **BL-204**; it is
named with its ref rather than relaxed, re-pointed or downgraded. Agents-side,
`scripts/backlog_status.py --check` is green at this move.

**What this close costs.** The row is moving into a file whose manifest row is on the `on-demand`
surface, so check 8 compares nothing about it and this move produces no `project_knowledge` WARN in
either direction. That is a property of the surface, not evidence that the archive and the store
agree — the distinction **BL-203** exists to state at the point a reader meets the column.

---

## The close — 2026-09-10 (second round)

**A second container on the same date, on the precedent of `## The close — 2026-08-26 (second
round)` above.** The container above is dated 2026-09-10 and opens *"One row, arriving as a
move, and the first row this backlog has closed on work an autonomous session produced"* —
BL-204 is neither, so adding it there would falsify that sentence about a round it does not
belong to. The date is qualified rather than reused.

### BL-204 — DONE 2026-09-10 · `mint` bumped to 1.10.0 and `mix hex.audit` is green (#TBD)
**Status:** DONE
**Kind:** code · **Size:** S · **Priority:** medium
**Section:** Harness (`../aetheris/mix.lock`)

`[Heading superseded 2026-09-10, corrected in place with this dated note per the harness
supersession rule (`../aetheris/CLAUDE.md` §Continuous learning → Workflow patterns). This row is
a PUBLISHED RECORD, not a ratified decision. The heading previously read:*

> `### BL-204 — `mix hex.audit` is red on two upstream `mint` advisories (#TBD)`

*and the depth-0 `**Status:**` field is REPLACED, `OPEN` -> `DONE`; BL-204 carries no `<details>`
block, so there is no archived status to preserve beside a live one, and two depth-0 fields would
fail `backlog_status.py --check` outright. The heading was TRUE WHEN WRITTEN — the gate was red at
harness `94e7adc` and at every commit before it — and is false as of harness `3a85d85`. A
SUPERSESSION, not R32.*

*EVERYTHING BETWEEN THIS NOTE AND THE **Closed by the bump upstream made available** PARAGRAPH IS
BYTE-IDENTICAL to the row as it stood in `docs/backlog-2026-06.md` at `86c8196`, lines 9250–9292,
its Done-when included. It is the record of what the row declared BEFORE the work; the answer is
appended after it, never woven into it. sha256 of that body, computed before the write:
`760cdc13a3e3ed323eeaf93f0dcd3ee949bf4ab6cbddc6c4550a362ccb5dfdf8`.*

*WHAT FOLLOWS IT IS NOT BYTE-IDENTICAL AND IS NOT CLAIMED TO BE.*]`

**The gate.** `mix hex.audit` exits 1 in the harness checkout. Whole output as captured
2026-09-10:

```
Advisories:
  mint 1.9.3 - EEF-CVE-2026-82729 (MEDIUM)
    aka: CVE-2026-82729, GHSA-7p8w-j234-7qc8
    Quadratic chunk-size parsing in Mint.HTTP1.Parse allows CPU-exhaustion DoS
    https://osv.dev/vulnerability/EEF-CVE-2026-82729

  mint 1.9.3 - EEF-CVE-2026-82728 (HIGH)
    aka: CVE-2026-82728, GHSA-g83f-2j6r-q6m4
    Unbounded HTTP/1 status-line and chunk-extension buffering in Mint causes memory-exhaustion DoS
    https://osv.dev/vulnerability/EEF-CVE-2026-82728

Found packages with security advisories
```

**Upstream-triggered, and unrelated to the ticket that found it.** `mint` is a transitive
dependency; nothing in this repository or the harness caused either advisory to appear, and
the change under review when the red surfaced — **BL-065**, the trajectory-write branch —
touches `lib/aetheris/agent/server.ex` and two test files only. The red is here because an
off-territory gate was run at a ticket boundary, which is the mechanism `CLAUDE.md`
§Definition of done describes: *"Gates that only run when a ticket happens to touch their
territory rot invisibly."* Filing it the day it was found is that rule's other half.

**Not BL-060.** The nearest existing row is **BL-060**, which is **DONE and about `bandit`**,
a different package and a different advisory set. It is not reopened, altered, or closed by
this row. The negative was established with positive controls rather than reported bare:
`grep -cniE "mint|advisor|hex\.audit"` over the two backlog halves returns **17** in the open
file and **111** in the closed one — CI-workflow prose and `mint` in the *minted* sense, none
of them a live row — so the search demonstrably reaches.

**Done when:** `mix hex.audit` exits 0 in the harness checkout, by whichever route upstream
makes available — a `mint` release carrying both fixes pulled through `mix deps.update mint`
and the resulting `mix.lock` change committed, or, if no fixed release exists yet, a dated
note in this row recording the check and the next date to re-check. **The gate is not
relaxed, re-pointed, or downgraded to a warning to get a clean run** (`CLAUDE.md` §Definition
of done). Until it closes, the red is **named with this row's ref** in any packet whose ticket
boundary runs it, and re-triaged by nobody.

`Source: found 2026-09-10 by the autonomous ticket session of backlog-loop experiment run 1, running the harness gate set off-territory at the BL-065 ticket boundary; captured as finding 1 of `../aetheris/docs/reviews/bl-065-review.md` (§Verification 5 carries the whole output quoted above) and named there rather than filed, that session being forbidden to file. Filed by the operator at the run-1 landing, per the same packet's own reading of the gate rule. The run-1 report records it at `../aetheris/docs/aetheris/research/experiments/auto-run-1-report.md` §8.2.`

**Closed by the bump upstream made available.** `mint 1.10.0` carries both fixes and states no
breaking changes; it satisfies `finch 0.23.0`'s `{:mint, "~> 1.8"}`, so `mix deps.update mint`
took it and `mix.exs` did not change. The `mix.lock` diff is **one line** — `mint 1.9.3 ->
1.10.0` — and no other package moved, `hpax 1.0.4` included; `castore` is optional and absent
from the lock. Committed as harness **`3a85d85`** on `main` and pushed, lock-only.

**Done-when, arm by arm.** The Done-when is a disjunction and the FIRST arm was taken: *`mix
hex.audit` exits 0 in the harness checkout*, by the route it names — a `mint` release carrying
both fixes, pulled through `mix deps.update mint`, the resulting `mix.lock` change committed.
The second arm — *a dated note recording the check and the next date to re-check* — was for the
case where no fixed release existed, and is **not reachable from here**. Nothing at this site
should be read as a deferral. The gate was **not** relaxed, re-pointed or downgraded.

**Before and after, both whole.** Before, at harness `94e7adc`: exit **1**, twelve lines, the
two advisories quoted in the body above and nothing else. After, at `3a85d85`: exit **0**, one
line, `No retired or security advisory packages found`. Both captures are complete rather than
excerpted — the BL-020 lesson under **Complete-output** is that `hex.audit`'s summary line
carries no count, so a fragment cannot be told from the whole.

**Gates at the commit**, all from the harness checkout at `3a85d85`, all exit 0: `mix test`
**983 tests, 0 failures, 135 excluded**; `mix format --check-formatted`; `mix credo --strict`
(*2068 mods/funs, found no issues*); `mix dialyzer` (*Total errors: 0*); `mix compile
--warnings-as-errors`, run with `--force` so it recompiled all 107 files rather than passing on
an up-to-date build. A minor bump that broke a gate would have been a finding; none did.

**What this close does not touch.** **BL-205** — the cloudcost seat-idleness test red on a
calendar boundary — is a separate row and stays OPEN and red. The Python whole-suite gate is
not run or reported here.

**What this close costs.** The row moves into a file whose manifest row is on the `on-demand`
surface, so check 8 compares nothing about it and this move produces no `project_knowledge`
WARN in either direction — a property of the surface, not evidence that the archive and the
store agree, the distinction **BL-203** exists to state.

---

## The close — 2026-09-10 (third round)

**A third container on the same date, on the precedent of the second above.** That container's
own note explains itself by BL-204's non-membership in the first round; BL-205 belongs to
neither, so the date is qualified again rather than reused.

### BL-205 — DONE 2026-09-10 · the seat test's reference date is pinned and it asserts the post-t3 outcome (#TBD)
**Status:** DONE
**Kind:** defect — a green test that expires · **Size:** TBD — the fix is a judgement, not yet ruled · **Priority:** medium
**Section:** cloudcost (`cloudcost/tests/test_fetch_github.py`, `cloudcost/scripts/detect_orphans.py`)

`[Heading superseded 2026-09-10, corrected in place with this dated note per the harness
supersession rule (`../aetheris/CLAUDE.md` §Continuous learning → Workflow patterns). The heading
previously read:*

> `### BL-205 — the cloudcost seat-idleness test asserts `candidates == 0` against today's date, so it went red on a calendar boundary (#TBD)`

*and the depth-0 `**Status:**` field is REPLACED, `OPEN` -> `DONE`; BL-205 carries no `<details>`
block, so there is no archived status to preserve beside a live one. The heading was TRUE WHEN
WRITTEN and is false as of `cloudcost/tests/test_fetch_github.py` at this commit. The `**Size:**`
field is carried unchanged and still reads `TBD — the fix is a judgement, not yet ruled`; the
judgement is ruled below, and the field is left as the row filed it rather than back-filled.
EVERYTHING BETWEEN THIS NOTE AND THE **Neither candidate was taken** PARAGRAPH IS BYTE-IDENTICAL
to the row as it stood in `docs/backlog-2026-06.md` at `34b1575`, lines 9250–9304, its Done-when
included. sha256 of that body, computed before the write and verified against this file after it:
`5f271ee0a4aee5f7576bbbaa2ba5c90fa5dcac1419cd898e5876f00f2ade8a87`. WHAT FOLLOWS IT IS NOT
BYTE-IDENTICAL AND IS NOT CLAIMED TO BE.]`

**The failure.** `cloudcost/tests/test_fetch_github.py::test_the_normalized_inventory_is_readable_by_the_shared_rule_engine`
fails at its last assertion, `assert counts["candidates"] == 0` → `assert 1 == 0`. Reproducer,
one line from the repo root:

```
python3 -m pytest -q "cloudcost/tests/test_fetch_github.py::test_the_normalized_inventory_is_readable_by_the_shared_rule_engine"
```

**The mechanism.** The test calls `detect_orphans.py` with no `--reference-date`, so every age
rule resolves against **today**. The seat rule fires above `DEFAULT_SEAT_INACTIVE_DAYS = 30`
(`cloudcost/scripts/detect_orphans.py:92`). The recorded seat at
`last_activity_at: 2026-08-06T11:09:27+05:30` crossed 30 days on **2026-09-06**, which is when
the assertion started failing; it is one candidate today. The remaining five recorded seats sit
at `2026-08-13`, and they cross next — at which point the count rises again and the test fails
differently, with a different number.

**The crossing schedule, probed rather than reasoned.** The fixture set
(`cloudcost/tests/fixtures/github_copilot_seats.json`) holds six seats: one at `2026-08-06` and
**five** at `2026-08-13`, of which one is `05:25+05:30` — i.e. `2026-08-12T23:55Z`, a day earlier
in UTC than its local date reads. Running `detect_orphans.py` over the inventory the test itself
produces, with `--reference-date` swept, gives: `2026-09-05` → 0, **`2026-09-06` → 1**,
`2026-09-10` → 1 (today), **`2026-09-12` → 2**, **`2026-09-13` → 6**, `2026-09-14` → 6;
`skipped` stays 0 throughout. So there are two further step changes, not one, and the second
takes the count to **6**. `[The filing instruction for this row said the next seat crosses on
2026-09-13 "at which point the count becomes 2". That pairs the right date with the wrong count:
2 arrives on 2026-09-12, from the UTC-shifted seat, and 2026-09-13 brings 6. Noted rather than
followed, and the sweep above is the truth-maker.]`

**Provenance.** Found 2026-09-10 by the off-territory gate run recorded in
`filter-rev1-packet.md` §7c — a session-scratchpad packet, in neither tree, so it is cited by
filename and cannot be opened by anyone but its author. **Not caused by that work:** both of its
commits are Markdown-only. That is inference from the diff — **the gate was NOT re-run at the
base commit to confirm**, and this row does not claim it was.

**Predicted, and arrived.** The `## Learning — m6-cloudcost` entry in harness `CLAUDE.md` says
of the unexercised seat arm that it *"closes on its own the first time a seat on this account
crosses 30 days idle. No ticket owns it and none should."* It closed, exactly as written. What
that entry did not anticipate is that closing it turns a **green test red** — the arm's first
exercise arrives as a gate failure rather than as coverage.

**Two candidate fixes, NEITHER ruled.** (1) Pin `--reference-date` in the test: deterministic,
and it retires a live assertion — the test stops tracking the account and starts tracking a
frozen date. (2) Give seats a rule, which is what the test's own comment defers to t3.

**One thing to establish first.** That comment reads: *"t3 is the ticket that gives seats a rule.
Until it lands, a legible seat yields no candidate, and that is the correct result rather than a
gap."* If **t3 has landed**, the assertion is guarding something other than what the comment
says it guards, and which fix is right cannot be chosen until that is settled.

**Done when:** the gate is green **and** this row records which candidate was taken and why. A
fix that retires the live assertion **says so explicitly** rather than leaving the retirement to
be inferred from the diff.

`Source: filed 2026-09-10 by claude-code at agents `1b72708`. The failure and the reference-date sweep were reproduced in this session against that tree; the fixture dates are read from `cloudcost/tests/fixtures/github_copilot_seats.json` at the same commit.`

**Neither candidate was taken, because the row's one-thing-to-establish settles them both.**
t3 **has** landed — `97c61a0`, 2026-08-14, *"feat(m6 t3): the seat orphan rule"*, which is where
`rule_idle_seat` and `DEFAULT_SEAT_INACTIVE_DAYS = 30` come from (`git log -S 'def rule_idle_seat'`
returns that commit and no other). So candidate (2), *give seats a rule*, was already discharged
four weeks before this row was filed, and candidate (1), *pin `--reference-date`*, was diagnosed as
the whole fix when it is half of one: the assertion was **obsolete**, not merely date-sensitive. Its
comment deferred to a ticket that had landed, and `candidates == 0` had been asserting the absence
of a rule that exists. A pin alone would have frozen a wrong expectation into a deterministic one.

**What landed.** `--reference-date 2026-09-10` on the `detect_orphans.py` invocation, and
`candidates == 1` in place of `candidates == 0`, with the comment replaced by one stating why the
date is pinned and what it selects. `returncode == 0` and `skipped == 0` are untouched — they are
the test's stated purpose, the adapter/rule-engine seam, and they are not what broke.

**The count was measured, not reasoned.** Before the assertion was written, `detect_orphans.py`
was run over the inventory the test itself produces, at the pin:

```
$ python3 scripts/detect_orphans.py <tmp>/github_inventory_2026-07.json \
      --output-dir <tmp> --reference-date 2026-09-10          # exit 0
{"resources": 6, "candidates": 1, "reported": 0, "excluded": 0, "skipped": 0}
```

The single candidate is `idle_seat` on seat `10000004`, whose own evidence string reads *"last
activity 2026-08-06 — idle 34d at ref 2026-09-10; threshold >30d"*. **34, not 35** — the engine
floors a timestamp difference against a midnight reference, so the seat's `05:39:27Z` costs it a
day against the calendar count. The nearest non-firing seat is 28d. The pin therefore sits between
28 and 34 with margin on both sides, and is not on the rule's `>30` boundary; the row's own swept
schedule (`2026-09-12` → 2, `2026-09-13` → 6) is now inert, because a frozen reference date cannot
reach either step.

**The live assertion is retired, and this says so rather than leaving it to the diff.** Before the
pin this test tracked the account: the six recorded seats aged against today, and the assertion
would have changed value twice more this month. After it, the test tracks a frozen date and asserts
what the rule engine does with a fixed inventory. That is a real loss of coverage and it is the
right trade here — the seam this test exists to assert is `skipped == 0` over a shape the engine
has never seen, which is date-independent, and the four other cross-stage tests in the suite
(`test_detect_orphans.py`, `test_compose_report_data.py`, `test_fetch_linode.py`,
`test_optimization_signals.py`) all pin a reference date for exactly this reason. This test was the
only one that did not.

**Gates**, all from the agents repo root at this commit. `python3 -m pytest -q
cloudcost/tests/test_fetch_github.py` — **55 passed**, exit 0. `python3 -m pytest -q -m "not
integration and not dormant"` under `timeout 1800` — **1621 passed, 3 skipped, 325 deselected
(integration=114, dormant=211), 7 xfailed in 213.18s**, exit 0, the exit read from the pytest
command itself and not from a wrapping shell; the run finished well inside its cap rather than
being cap-killed. `python3 scripts/backlog_status.py --check` — exit 0, *204 of 204 row ids*.

**`drift_check --strict` is owed after this commit, not inside it.** Check 8 reads committed
history, so its verdict on a commit that edits `docs/backlog-2026-06.md` — a manifest-tracked row
on the `export` surface — cannot be established by a run that precedes the commit, and a result
asserted here would be a claim landing in the same commit as the thing that would make it true.
Run pre-commit at `34b1575` it was **exit 0, 19 PASS 0 FAIL 3 WARN 8 INFO**, the three WARNs all
`project_knowledge` staleness (`backlog-2026-06.md`, `docs/aetheris/research/index.md`,
`docs/methodology/milestone-methodology.md`). The post-commit prediction is the **same three
members** — this commit re-stales `backlog-2026-06.md`'s row rather than adding one, and
`backlog-2026-06-closed.md` sits on the `on-demand` surface where check 8 compares nothing. The
run and its verdict are in this round's packet. The manifest is not re-pinned.

**Not touched:** `detect_orphans.py`, the fixtures, any other test, `lib/`, the manifest.

---

## The close — 2026-09-11

**One row, and the first this backlog has closed on a ratified contract edit.** The container is
dated rather than qualified: no other close carries this date.

### BL-197 — DONE 2026-09-11 · `tools_hash` over the DECLARED tool surface, recorded at three sites (#TBD)
**Status:** DONE
**Kind:** feature · **Census items:** n/a — the first deliverable is the population (see Done-when) · **Contract:** `../aetheris/docs/aetheris/determinism-contract.md` §2 (definitions) and §4 (the fork guarantee); the research inputs below
**Size:** S · **Priority:** medium — a **BL-008 D9 prerequisite**, so it lands before BL-008's P0
**Section:** harness (`../aetheris/lib/aetheris/execution/`, `../aetheris/lib/aetheris/agent/server.ex`)

`[Heading superseded 2026-09-11, corrected in place with this dated note per the harness
supersession rule (`../aetheris/CLAUDE.md` §Continuous learning → Workflow patterns). This row is
a PUBLISHED RECORD, not a ratified decision. The heading previously read:*

> `### BL-197 — `tools_hash`: the script, tool and skill surface a run can reach is hashed into run identity (#TBD)`

*and the depth-0 `**Status:**` field is REPLACED, `OPEN` -> `DONE`; BL-197 carries no `<details>`
block, so there is no archived status to preserve beside a live one, and two depth-0 fields would
fail `backlog_status.py --check` outright. The heading was NOT true when written and is the one
thing this close corrects rather than supersedes: it says the hashed surface is the one a run
**can reach**, and the population that landed is the one a run **declares**. The difference is
not a narrowing of scope — it is the finding. `run_command` is not confined to the sandbox root
(**BL-207**), so the reachable set is the host filesystem and no definition over it exists to
give. The `**Size:**` field is carried unchanged at `S` and is wrong; see **Size was filed S and
was M** below, where it is ruled rather than back-filled.*

*EVERYTHING BETWEEN THIS NOTE AND THE **Landed at** PARAGRAPH IS BYTE-IDENTICAL to the row as it
stood in `docs/backlog-2026-06.md` at `1cd4647`, lines 8833–8872, its Done-when and its
Collides-with included. It is the record of what the row declared BEFORE the work; the answer is
appended after it, never woven into it. sha256 of that body, computed before the write and
verified against this file after it: `37b395199da28d9b12aefebe2541f00160b0e8194b74921778ac9efa420827e2`.*

*WHAT FOLLOWS IT IS NOT BYTE-IDENTICAL AND IS NOT CLAIMED TO BE.*]`

Filed 2026-09-08 from the research batch landed at harness `2c1a6b6`. The idea is
the external schema analysis's item #1, dispositioned at
`../aetheris/docs/aetheris/research/research-reconciliation-2026-07-26.md` §2 as
*"tools_hash S-ticket idea, orthogonal to BL-025's EffectClass"* and never filed;
the BL-008 synthesis brief makes it a dependency
(`bl-008-synthesis-2026-08.md` D9: *"Skill bodies live as files under the
content-hashed tool surface (tools_hash family), so run identity captures the exact
skill content a run could read"*; the 2026-09-08 margin note under its §3 says it
lands before P0), and the pi brief's Take 2 and the dsh brief's L4 both point at it.

**The code today, read at harness `bb42099`.** Nothing hashes a tool surface: `tools_hash`,
`config_hash` and `tool_surface` occur nowhere under `lib/` (0 hits; control, the
same search for `fork_from` finds it). What a run records about its tools is the
**names** — `"tools" => config.tools` in the trajectory meta
(`lib/aetheris/agent/server.ex:669`, `:941`) — and what a fork reads back is the
same list (`lib/aetheris/execution/fork.ex:181`). So two runs whose `run_command`
reaches a script that changed between them are identical by every field the
harness records, and verify cannot tell which script a recorded step ran.

**Done when:** (1) the population is written down first — which files count as the
tool surface (the `tools` list; the scripts and skill files under the agent root that
`run_command` can invoke; MCP server identities if they are in scope) — as a stated
rule in the contract, not an inferred one; (2) a content hash over that population is
computed at run start and captured with the run's config (`config_json` and the
trajectory meta, the same two sites that carry `model`), so fork and verify can read
it; (3) the mutation test is on the record: change one byte of one in-surface script
between record and verify and the hash differs, with a test that fails if it does
not. The hash is a **field**, not a gate — what a mismatch *means* to verify is
decided by the row that consumes it, not here.

**Not done-when:** hashing the tool names only, which the meta already carries.

**Collides with:** **BL-008** — D9's interim rule is BL-025 `:contained`
record-and-serve on reads under the skills path *"if the hashed-surface item has not
landed"*; this row is that item, and BL-008's milestone doc should cite it rather than
carry the interim. **BL-025** (closed) — EffectClass is orthogonal, per the
reconciliation's own disposition; do not fold. **BL-198** — the two are the D9
pair; independent, no ordering between them.

`Source: filed 2026-09-08 by claude-code at agents `1e9cb57` and harness `2c1a6b6`, from `research-reconciliation-2026-07-26.md` §2, `bl-008-synthesis-2026-08.md` D9 and §3, `pi-harness-2026-07.md` Take 2 and `dsh-model-visible-logged-2026-08.md` L4, all opened in the landed batch. The code citations were opened at harness `bb42099` before that batch landed; the two research commits after it touch no `lib/` file.`

**Landed at** harness `a1bda7e` (the implementation) and `cb909c9` (a trim of the amendment note
this row's own work added to the contract header, on the prose budget). Both pushed. The contract
carries §2 **Tool surface** and §4 **Anything outside the tool surface**, arbiter-ratified wording
landed **verbatim** — established by diffing the supplied text against the landed text with
whitespace normalised, not asserted.

What the three Done-when clauses got:

1. **The population is written down first, as a stated rule in the contract.** §2 defines it as
   every git-tracked path under the run's `sandbox_path` at hash time plus every path in
   `tool_surface_extras`, and says in terms that it is **declared, not reachable**.
2. **The hash is computed at run start and captured with the run's config.** One stamp, in
   `Agent.Server.init/1` — the single site both `handle_call(:run, …)` and
   `handle_call(:resume_from_checkpoint, …)` pass through, so a resume is not silently nil — and
   it reaches `config_json` via `encode_config/1` and both trajectory meta maps.
3. **The mutation test is on the record.** See directly below; this is the clause that was
   satisfied differently from how it was written.

**Clause 3 was satisfied differently from how it was written, and that is the ROW'S LOOSENESS
rather than a short delivery.** It asked for one byte changed "between record and verify". A
record/verify cycle has nothing to assert here, because this row's own last sentence says the
hash is **a field, not a gate** — verify consumes it nowhere, so there is no verdict for a
mutation to move. What landed is the property the clause was reaching for, asserted at the level
where it actually is assertable: six mutations at the `ToolSurface` level, each applied to a
working-copy backup and each restore verified by sha **and** by a present→absent control on the
mutated string — path dropped from the digest, content digest replaced by a constant, extras
dropped, the tracked set replaced by a filesystem walk, and the two recording sites broken
separately. Plus two named inverse cases in the green suite: an in-surface byte change moves the
hash, an untracked change under the same root does not. The row is closed on that, and the
substitution is recorded here rather than left to be inferred from the diff.

**Size was filed S and was M.** A contract edit, two `RunConfig` fields, a new module, a
run-start stamp, three recording sites, six mutation tests with their controls, and a measured
cost figure. Not a complaint — the work was correctly scoped and the ticket said what it wanted.
Recorded so the next sizing of a **contract-touching** row has the precedent: the code was S and
the contract was not, and nothing in the S estimate was carrying the ratification, the verbatim
check, or the non-guarantee that had to be written beside it.

**Cost, measured rather than estimated.** 467 paths, 23.4 ms on a cold first call in a fresh
BEAM, 19–21 ms warm across five consecutive calls, over the harness root — `sandbox_path:
File.cwd!()`, which `../aetheris/agents/codebase_qa.exs:9` uses. **Not optimised**, by
instruction. Corroboration at the other end: `init/1`, and therefore this hash, runs on every
agent server the harness suite starts, and the suite finishes in 91.5 s.

**What it unblocks: m14's P0.** `../aetheris/docs/aetheris/milestones/m14-skills-auto-extraction.md`
§2 names this row as a hard gate — *"No P0 ticket starts until BL-197 lands."* It has landed.
**m14 is NOT edited**: the gate clause stays exactly as written, and this row's close is where
the fact that it is satisfied lives. A gate clause rewritten to say it was met is a gate that can
no longer be read as a condition by the next person who needs to apply one.

**Left open by design, each with a home.**

- **BL-207** — `run_command` is not confined to the sandbox root. The contract states this as a
  **non-guarantee** (§4) rather than closing it, which is exactly why that row exists and why
  this one could be closed without it. Open.
- **BL-208** — the sha256 content-digest idiom now has four sites and no shared home;
  `tool_surface.ex` is the fourth, reusing the format and not the code. Filed this round, out of
  this row's scope by instruction. Open.
- **This row's own `:669`/`:941` citations.** They are cited for `model` and are the `"tools"
  => config.tools` lines; `model` is at `:665` and `:937`, in the same two meta maps. The row
  names the right two sites and the wrong two lines. Recorded in
  `../aetheris/docs/aetheris/milestones/bl-197-implementation-notes.md` §The correction the row's
  citations need, and **deliberately not edited into the row above** — the body is the record of
  what was declared before the work, and correcting it in place would destroy the one thing the
  byte-identity claim is protecting.

**Not touched:** `m14-skills-auto-extraction.md`, the manifest, `Aetheris.API.RunPolicy` (whose
closed `@known_client_fields` allowlist rejects both new fields, which is the correct default and
is recorded in the implementation notes as a silent consequence rather than an edit), and the
three duplicate `hash_content/1` helpers.

`Source: closed 2026-09-11 by claude-code. Implementation at harness `a1bda7e`, trim at
`cb909c9`, both pushed; the round's evidence is `bl-197-review-packet.md`, a session-scratchpad
packet in neither tree and cited by filename because nobody but its author can open it. The
citations in this close were resolved at harness `cb909c9` and agents `1cd4647`.`

---

## The close — 2026-09-11 (second round)

### BL-208 — DONE 2026-09-11 · the sha256 content-digest idiom has four sites and no shared home (#TBD)
**Status:** DONE

`[Heading superseded 2026-09-11, corrected in place with this dated note per the harness
supersession rule (`../aetheris/CLAUDE.md` §Continuous learning → Workflow patterns). This row is
a PUBLISHED RECORD, not a ratified decision. The heading previously read:*

> `### BL-208 — the sha256 content-digest idiom has four sites and no shared home (#TBD)`

*and the depth-0 `**Status:**` field is REPLACED, `OPEN` -> `DONE`.*

*EVERYTHING BETWEEN THIS NOTE AND THE **Landed at** PARAGRAPH IS BYTE-IDENTICAL to the row as it
stood in `docs/backlog-2026-06.md` at `74ba746`, lines 9421–9455, its `Source:` included. It is
the record of what the row declared BEFORE the work; the answer is appended after it, never woven
into it. sha256 of that body, computed before the write and verified against this file after it:
`06f53ce6430cfafdecbf694ec868a16aeeab8a61da2842d3c67ec47da29756bb`.*

*WHAT FOLLOWS IT IS NOT BYTE-IDENTICAL AND IS NOT CLAIMED TO BE.*]`

**Kind:** hardening · **Size:** XS · **Priority:** low — latent; nothing is wrong today
**Section:** harness (`../aetheris/lib/aetheris/`)

**The census, four sites.** Three are byte-identical private helpers:

```elixir
defp hash_content(data),
  do: "sha256:" <> Base.encode16(:crypto.hash(:sha256, data), case: :lower)
```

at `lib/aetheris/skill/extractor.ex:248`, `lib/aetheris/eval/runner.ex:304` and
`lib/aetheris/execution/loop.ex:1127`. The fourth is
`lib/aetheris/execution/tool_surface.ex:68`, which reuses the **format** and not the
code — it hashes an accumulated digest rather than taking `data`, so it is not a
fourth copy of the function, but it is a fourth place that produces the string.

**Why it is latent.** Nothing breaks today: all four emit the same shape over the same
algorithm, and the three copies are private, so no caller can pick the wrong one. It
bites when one site's format changes and the others do not — a prefix, a case, a
truncation, a move to a different algorithm — because the values are written into
trajectories and compared across runs, and **no check compares the four**. A change at
one site is silent at the other three until something that reads two of them disagrees.

**Done when:** one shared function exists, the four sites call it, and a decision is
recorded ON THIS ROW about how a FIFTH site is prevented: by a check that fails when
the string is produced anywhere else, or by there being only one way to produce it and
the shared function being it. The row is not closed by the refactor alone — four call
sites pointed at one function is the easy half, and it is exactly the state that made
three copies look harmless.

`Source: census taken 2026-09-11 during BL-197, which put the refactor out of scope and
recorded the four sites in
`../aetheris/docs/aetheris/milestones/bl-197-implementation-notes.md` §Deviations. All
four citations were re-read at harness `cb909c9` when this row was filed; BL-197's
commits touch none of the three helper files.`

**Landed at** harness `56d6ee9` (the refactor) and agents — this commit (this close). Neither
pushed at the time of writing; the round reports before pushing.

**THE RULING THE ROW LEFT OPEN: a fifth site is prevented BY BOTH mechanisms, and the module alone
prevents nothing.** The Done-when offered two ways — *"a check that fails when the string is
produced anywhere else, or ... there being only one way to produce it and the shared function
being it"* — as alternatives. They are not alternatives, and the row's own next sentence is why:
*"four call sites pointed at one function is the easy half, and it is exactly the state that made
three copies look harmless."*

A shared module makes the right thing available. It does not make the wrong thing unavailable:
`"sha256:" <> Base.encode16(:crypto.hash(:sha256, data), case: :lower)` is four tokens of stock
Elixir that any future author can type without ever learning `Aetheris.Hash` exists, and nothing
would tell them — or the reviewer — that they had just recreated the condition this row closed.
That is precisely how the three copies arose: there was no prohibition, only an absence. So the
row closes on both mechanisms, and the check is the load-bearing half.

**Mechanism 1 — the shared module.** `Aetheris.Hash` at `../aetheris/lib/aetheris/hash.ex`, placed
at the top level beside `Aetheris.ID`, which is the repo's precedent for a small single-purpose
utility (no `util/` or `support/` namespace exists). **Two** functions, because the four sites were
not uniform, exactly as the census recorded:

- `content/1` — data to string. The three byte-identical private helpers.
- `format/1` — a raw, already-computed digest to string. `Execution.ToolSurface`, which accumulates
  with `hash_init/hash_update/hash_final` and shared only the FORMAT.

All four sites call it; the three private `hash_content/1` helpers are gone rather than left as
delegating wrappers, so there is one function and not four plus one.

**Mechanism 2 — the check.** `../aetheris/test/aetheris/hash_test.exs` fails when the `"sha256:`
format literal appears anywhere in `lib/` outside `hash.ex`. Three properties it was built to have:

1. It matches **the format string, not the expression**. A fifth site written differently —
   interpolation, a pipeline, `hash_init/update/final` — still has to write that prefix. The
   positive control below is deliberately spelled `"sha256:#{hex}"` with a pipeline, and is caught.
2. It excludes the shared module **by path**, not by content, so the exclusion cannot drift.
3. It anchors the scan to `Path.expand("../../lib", __DIR__)` rather than to the process cwd. A
   wildcard resolved against cwd answers a question about where the suite was started and returns
   a clean empty list when that is somewhere else.

It reads whole lines and does not except comments. That is deliberate and stated in the failure
message: a module that documents the format should point at `Aetheris.Hash` rather than write the
literal.

**What the round found that the row did not predict: no test anywhere pinned a digest VALUE.**
Every existing assertion was `"sha256:" <> _` or `String.starts_with?(…, "sha256:")` — shape, not
value. Under a value-changing mutation applied to all four sites at once, the whole suite returned
**1017 tests, 1 failure**: three of the four sites were completely uncovered, and only
`loop_tool_error_test.exs`, which recomputes the expected digest inline as an independent oracle,
noticed. So the row's premise — *"no check compares the four"* — was understated: nothing checked
even one of them against a value. Golden assertions were added at the three uncovered sites, which
is what makes the mutation evidence below possible at all:

- `tool_surface_test.exs` — the empty-surface digest pinned by value. An absent root is the one
  fully deterministic digest the module produces, so it is the right place to pin the format.
- `runner_test.exs` — `prompt_hash` pinned by value, and separately against `Hash.content/1` of the
  task's own prompts.
- `extractor_test.exs` — a recording adapter captures the synthesis request and asserts
  `context_hash` is the digest OF the messages that request ships. The extractor dispatches with a
  bare `GenServer.call(adapter_pid, {:call, request})`, so a test process can serve it; `Stub`
  discards the request, which is why nothing could assert this before. No `lib/` change was needed.

**Digest values are unchanged, and here is the method rather than the belief.** A probe capturing
every digest the four sites can produce was run at harness `e1c38e6` BEFORE any edit and again
after, and the digest sections are byte-identical — md5 `c387df805dda1876fb6d6a3af52dd043` both
times, `diff` exit 0. It covers `ToolSurface.hash/2` end to end over a fixed non-git root plus its
three per-entry digests, and the three-site idiom over eight vectors including empty, binary and
the real `Jason.encode!` shapes. The comparison carries a negative control: one hex digit altered
in the after-file makes `diff` exit 1, so a zero difference is agreement and not a blind
comparison. `Hash.content/1` was additionally checked equal to the literal old expression on every
vector — 0 mismatches — and structurally it is the same three operations in the same order.

**Mutation evidence, one site at a time.** Each restore was from a working-copy backup verified by
`sha256sum -c`, never `git checkout --`, and the mutation marker was confirmed absent afterwards.

| site | mutation | result |
|---|---|---|
| `skill/extractor.ex` | digest input changed | 1 failure — the new `context_hash` test |
| `eval/runner.ex` (both calls) | digest input changed | 1 failure — `prompt_hash`, under `--include integration` |
| `execution/loop.ex` | digest input changed | 1 failure — `loop_tool_error_test.exs` |
| `execution/tool_surface.ex` | `format/1` swapped for `content/1` | 1 failure — the empty-surface value |

And the check's own positive control, run against `lib/` rather than a fixture, as the round
required: a fifth site was added at `lib/aetheris/bl208_control.ex` spelled `"sha256:#{hex}"` with
a pipeline; the check failed naming `lib/aetheris/bl208_control.ex:11`; the file was deleted and
the check passed. Both outputs are in the round's report.

**Not touched.** `Aetheris.Eval.Scorer.FsHash` — it compares a payload it does not compute, and was
never one of the four. `ToolSurface.content_digest/1` produces a per-entry digest with **no**
prefix and is not a fifth site; the check matching on the prefix leaves it alone by construction,
which is one reason to match the format string rather than the hash expression.

**Size was filed XS and was S.** A module, four call sites, a new test file with a source-scanning
check, and three golden assertions that had to be invented because no value was pinned anywhere.
The refactor alone was XS; discovering that the mutation evidence the close requires was
unobtainable against the existing suite was not.

`Source: closed 2026-09-11 by claude-code. Refactor at harness `56d6ee9`, this close in the agents commit
carrying this edit, neither pushed. The four sites were re-read at harness `e1c38e6` before the work —
all four still at the line numbers BL-197's census recorded — and the whole-of-`lib/` search that
found them is `grep -rn '"sha256:' lib/`, which after the refactor returns hits in `hash.ex` only.`

### BL-216 — DONE 2026-09-12 · `[R38]` has no row in the ratified-decisions registry (#TBD)
**Status:** DONE
**Kind:** process · **Contract:** none
**Size:** XS · **Priority:** low
**Section:** agents (`docs/milestones/hc-consolidation.md`)

R36 and R37 each carry a row in the ratified-decisions registry. R38, added to the harness
methodology file and tagged there, did not. Until the registry row is written the tag points at
nothing: a reader meeting `[R38]` in the methodology has no way to reach when it was ruled, by
whom, or on what instance, which is the whole function the registry serves for its two
predecessors.

Filed and closed in one commit, per its own instruction: writing the entry is one row in one file,
and filing the work as future work would have cost more than doing it.

**Done when.** `[R38]` resolves in the registry the same way `[R36]` and `[R37]` do — one entry,
pointing at the harness methodology rather than restating it.

**Landed at** agents — this commit. The entry is `hc-consolidation.md:960`, written in the form
R36 and R37 use: the ruling date, the single home of the text, the tag it resolves, the motivating
instance, and the authority it landed under (R22).

`Source: m14 T6, 2026-09-12. The methodology text is harness `3de3908`,
`docs/methodology/milestone-methodology.md:89`–`:94`, carrying the `[R38]` tag at `:90`; that
commit is pushed, which is what this rule requires of the citation above. R36 and R37 are
`hc-consolidation.md:948` and `:954`, re-resolved before filing.`

---

## The close — 2026-09-12

**One row, closed on a Done-when its own milestone assigns to a phase rather than to the
milestone's end.** The container is dated rather than qualified: no other close carries this date.

### BL-008 — DONE 2026-09-12 · Skills auto-extraction + Rig skills view (compounding) (#49)
**Status:** DONE

`[Heading superseded 2026-09-12, corrected in place with this dated note per the harness
supersession rule (`../aetheris/CLAUDE.md` §Continuous learning → Workflow patterns). This row is
a PUBLISHED RECORD, not a ratified decision. The heading previously read:*

> `### BL-008 — Skills auto-extraction + Rig skills view (compounding) (#49)`

*and the depth-0 `**Status:**` field is REPLACED, `OPEN` -> `DONE`. BL-008 carries no `<details>`
block, so there is no archived status to preserve beside a live one.*

*EVERYTHING BETWEEN THIS NOTE AND THE **Landed at** PARAGRAPH IS BYTE-IDENTICAL to the row as it
stood in `docs/backlog-2026-06.md` at `c497ae7`, lines 1698–1726, its `Section:` field and its
2026-09-11 dated note included. It is the record of what the row declared BEFORE the work; the
answer is appended after it, never woven into it. sha256 of that body, computed before the write
and verified against this file after it:
`cb6b5ad04a58ac07adc67949a845f02316ade9132a96483bf51dcd08f07270f2`.*

*WHAT FOLLOWS IT IS NOT BYTE-IDENTICAL AND IS NOT CLAIMED TO BE.*]`

**Size:** L · **Priority:** medium-low
**Section:** harness (`../aetheris/docs/aetheris/milestones/m14-skills-auto-extraction.md`)

The "compounding/dreaming" idea from the Burr HN thread, grounded in what
exists: `skills` table schema-complete (`store.ex:817`), write path live
(`insert_skill`, `store.ex:132/619`), public API `Aetheris.extract_skill`
(`lib/aetheris.ex:111`) — but nothing calls it automatically and nothing
reads the table. Operationally empty.

Scope sketch:
- Harness: post-run hook (opt-in via RunConfig flag) that calls
  `extract_skill` for successful runs matching criteria (e.g. ≥N steps,
  `reason: agent_finished`); populate `source_run_ids_json`.
- Dedup/quality gate before insert (don't accumulate near-identical
  skills from repeated sprint runs).
- Rig: read-only Skills section under Harness (one command, one view —
  follow the harness.rs / RunList.tsx pattern per runbook's "Adding a
  new module" steps).
- Relation to `api/tenant/scripts/extract_skill_hints.py` (separate,
  domain-specific): document the distinction or unify deliberately.
- Schema/command/doc changes → drift_check in the same commit.

**Done when:** milestone docs exist; a normal sprint run leaves at least
one skill row behind and Rig can show it.

`[2026-09-11: the milestone doc landed at harness `65862bb` and was approved
that day — thirteen tickets over P0–P3, of which P0 is gated on BL-197. That
is the Done-when's FIRST clause only; nothing here is done, and the remaining
two clauses are untouched.]`

**Landed at** harness `f5249d2` and agents `c497ae7`, both pushed — the state at which P1 was
discharged. The evidence is `../aetheris/docs/aetheris/milestones/m14-p1-discharge.md`, committed
at `f5249d2`.

**This close does not close m14.** The milestone's §1 rules that BL-008's Done-when *"is
discharged at the end of P1 by T5, T6 and T7, not at the end of the milestone"*, and P1 ended at
the two commits above. T8–T13 are unstarted or in flight and m14 continues; no other row is
touched by this one. A milestone whose backlog row closes mid-flight is unusual enough that the
reason is stated here rather than left to be reconstructed from §1.

What the three Done-when clauses got:

1. **Milestone docs exist.** `m14-skills-auto-extraction.md`, landed at harness `65862bb` and
   approved 2026-09-11 — already recorded in the row's own dated note above, which correctly said
   at the time that this was the first clause only.
2. **A normal sprint run leaves at least one skill row behind.** `SELECT COUNT(*) FROM skills`
   went 0 → 4 on the live store (`priv/aetheris.db`), four `use_case: "payslip"` rows all carrying
   `source_run_ids: ["payslip-orch-5Jhdvw"]`, a real payslip orchestrator run rather than a
   fixture. `Curator.Report`: `inserted: 4, duplicates: 0, superseded: 0, evicted: 0,
   mismatches: 0, rejected: 0`. See the substitution below — this clause was satisfied
   differently from how it was written.
3. **Rig can show it.** The `/skills` view was opened by clicking **Skills** in the nav of the
   running Rig binary against the live DB — rendered, not asserted — showing
   `Active (4) · Superseded (0) · Retired (0) · All (4)`, one card per row. T7 is agents
   `95b1161`, pushed.

**Clause 2 was satisfied differently from how it was written, and that is a DESIGN SUPERSESSION
rather than a short delivery.** The clause says a *sprint run* leaves a row behind, and the scope
sketch above says how: *"post-run hook (opt-in via RunConfig flag) that calls `extract_skill`"*.
No such hook was built and none should have been. T5's scope rules the opposite in terms — the
extractor *"is a normal recorded run, not a hook in `Agent.Server`; its failure cannot affect the
source run"* — so extraction is a second run over a completed trajectory, not something the source
run does on its way out. What discharged the clause is therefore a normal recorded payslip run
(`payslip-orch-5Jhdvw`, 39 events, terminal `run_complete`, 0 `error` events) whose trajectory the
extractor then read, followed by the curator writing the four rows. The property the clause was
reaching for — real runs, not fixtures, produce durable skill rows — holds; the mechanism the
clause named does not exist and was deliberately replaced. Recorded here rather than left to be
inferred, and the row body above is not edited to match, because it is the record of what was
declared before the work.

**The `Section:` field was added before this close, not by it.** Agents `ad7d9f4`, 2026-09-11,
pointing at the milestone document — the milestone's §8 item 3 asked for it *"when this document
is approved"*, and it was approved and executed that day. The field travels into this archive
inside the byte-identical block above. §8 item 3 is marked resolved in the milestone doc in a
separate harness commit, per R38.

**Left open by design, each with a home.**

- **m14 T8–T13.** The remaining tickets, in the milestone doc. P1's discharge record names its own
  honest limit: one trajectory of one use case, the shape the segmenter is most likely to get
  right. That is not a defect of this row's Done-when, which never asked for a heterogeneous
  corpus, but it is why the row closing is not the milestone closing.
- **BL-211 through BL-219**, the deferred findings the T5, T6 and T7 reviews and the discharge run
  filed. All open, none folded into this close. **BL-213** (the curator's mismatch record) did not
  bear on the discharge run — `mismatches: 0` — and stays open on its own terms; **BL-215**
  (envelope truncation) was avoided by trajectory choice rather than fixed, which the discharge
  record states.
- **`api/tenant/scripts/extract_skill_hints.py`.** The scope sketch's last-but-one bullet asked to
  *"document the distinction or unify deliberately"*. Neither was done and neither is owed by the
  Done-when, which does not mention it. Named here so a reader does not have to establish from the
  diff that a scope-sketch bullet went unaddressed; a scope sketch is not a Done-when, and the row
  closes on the latter.

**Not touched:** any other backlog row, the manifest, `docs/use-cases.md`, and the milestone doc's
ticket sections — the harness commit that accompanies this one edits §8 item 3 and nothing else.

`Source: closed 2026-09-12 by claude-code. Discharge evidence at harness `f5249d2`
(`m14-p1-discharge.md`), P1's three tickets at harness `9b8f5a7` (T5) and `3de3908` (T6) and
agents `95b1161` (T7), the milestone doc at harness `65862bb`, the `Section:` field at agents
`ad7d9f4` — every one of them pushed. The four-row count was re-read from the live store at close
time and agrees with the discharge record. The round's evidence is `m14-t8-review-packet.md`, a
session-scratchpad packet in neither tree and cited by filename because nobody but its author can
open it.`

---

## The close — 2026-09-14

**The closing sweep.** Rows whose fix had landed and whose row was never closed, each verified against its own Done-when at harness `ee7f529` / agents `e6f0227`, both pushed. Each row's body is moved verbatim; only its heading and its `**Status:**` value change, and everything after the body is appended at this close.

### BL-007 — DONE 2026-09-14 · Replay / fork from step (Rig p9 candidate) (#48)
**Status:** DONE
**Size:** L · **Priority:** medium

Feasibility confirmed (report Gap C + §3.1): trajectory files store full
untruncated prompts (`meta.system_prompt`/`user_prompt`) and complete
tool-call/tool-result payloads, so the conversation at step N is
mechanically reconstructable for completed runs — `run_checkpoints` is
only needed for live ones. No recording changes required.

Scope sketch for the milestone docs:
- ~~Harness: `Aetheris.fork_run(run_id, step)` — rebuild messages up to
  step N from the trajectory, start a new run with provenance back-link
  (consider reusing `agent_trees` for the parent/child relation).~~
  **Already built — struck 2026-07-17, see the annotation below.**
- ~~Rig: one Tauri command + a "Fork from here" affordance on a step group
  in TrajectoryView. *(Verified absent — this is the real work.)*~~
  **Built — struck 2026-07-20.** Shipped exactly as sketched: the `fork_run`
  Tauri command (t3) and a per-step "Fork from here" affordance with a
  provenance banner in `TrajectoryView` (t4, `6dd2d55`).
- Decide divergence semantics up front: forked run gets a fresh run_id
  and records normally; original is never mutated.
- New event types or config fields → event.ex/specs §6 in the same
  commit (drift_check enforces).

> **Verified state 2026-07-17 (BL-022's source check — this sketch was stale).**
> The harness half of the sketch describes work that already shipped:
>
> | Claimed as work | Verified state |
> |---|---|
> | `Aetheris.fork_run(run_id, step)` | **exists** — `lib/aetheris.ex:73` |
> | "rebuild messages up to step N" | **exists** — `Fork.from_step/3`, `lib/aetheris/execution/fork.ex`, since 2026-05-17 |
> | "provenance back-link" | **exists** — `fork_from` / `fork_step` are first-class `RunConfig` fields (`run_config.ex:82,196`), set at `fork.ex:119`, and **persisted into the trajectory's `meta`** by `maybe_add_fork_meta` (`agent/server.ex:717-720`). Shipped as a direct field link, not via `agent_trees` — the sketch's parenthetical was a suggestion, and a simpler design won. |
> | — | `:fork` is first-class in the mode union (`run_config.ex:115`); CLI `cli/commands/fork.ex`; tests in `execution/fork_test.exs` and `cli/commands/fork_test.exs` |
>
> ~~**Verified absent:** the Rig side — no fork command in `rig/src-tauri/src/*.rs`, no
> frontend references, nothing in `specs.md` §4.~~ **Closed 2026-07-20:** all three
> now exist — `fork_run` in `rig/src-tauri/src/commands/fork.rs:34`, the
> `useFork`/`TrajectoryView` frontend path, and the `specs.md` §4 command row.
>
> Not re-scoped here; that is the planning session's job. Noting only that the shape
> has changed: provenance, determinism contract, and Rig UX **on top of an existing
> core**, rather than a from-scratch build.
>
> **Milestone scoping starts from source, not this sketch.**

**Done when:** milestone README + issue docs exist; implementation gated
on them, per the p3 pattern (docs → mock/real split if useful → UI).

**Closed 2026-09-14 (closing sweep).** The row was stale, not the roadmap: BL-007 closed 2026-07-20 (`../aetheris/ROADMAP.md` Horizon 0; `docs/handoffs/handoff-bl007-close-2026-07-20.md` §State). Done-when:

1. *Milestone README exists* — `docs/rig/milestones/bl-007/README.md`, milestone summary RATIFIED 2026-07-20 (its `## Milestone summary` heading).
2. *Issue docs exist* — the ticket sections t0–t5 under that README's `## Tickets` (:114), plus `bl-007-t0-caused-by.md`; per-ticket GitHub issues were waived by the README's own issue-tracking decision of 2026-07-18 (`## Sequencing`), epic #48 tracking. The README says per-ticket docs are `bl-007-t*.md`; on disk only t0 has one, and t1–t5's are the README sections.
3. *Implementation gated on them* — the README was drafted 2026-07-17; t0–t5 merged 2026-07-18 to 07-20 against it, reviews at `docs/reviews/bl-007-t0-review.md`…`t5-review.md`; last harness commit `7e77951`.

---

### BL-010 — DONE 2026-09-14 · Clean order_formatter output: strip extra sheets and clear stale template formulas (#51)
**Status:** DONE
**Size:** S · **Priority:** now

Two output defects observed on first real run:

1. **Extra sheets in output xlsx.** `--template` and `--catalog` point to the
   same file (`Updated_Boxy_MSRP_Sales_Order_Form.xlsx`), which contains all
   five `{N}000 Price List` and `{N}000 Order Form` sheets. openpyxl loads and
   saves the whole workbook, so the output carries all those sheets. Only
   `2000 Order Form` should be in the output file.

2. **`#NAME?` errors in unused template rows.** The template has VLOOKUP
   formulas pre-filled in rows 12–67. The formatter writes items into rows
   12–N, but rows N+1 through 67 retain the original VLOOKUP formulas. When
   openpyxl saves the workbook, named-range references in those formulas break,
   producing `#NAME?` errors visible in Excel.

**Fix (both in `scripts/order_formatter.py`):**
- After loading the template workbook, delete all sheets except `2000 Order Form`.
- After writing all line items and fee placeholder rows, clear all cells in
  columns B–K (cols 2–11) for rows `(last_written_row + 1)` through `67`. Set to `None`.

**Touches.**
- `scripts/order_formatter.py`
- `tests/test_order_formatter.py` — add tests: output has exactly one sheet;
  no `#NAME?` errors beyond last written row (`@pytest.mark.integration`)
- `docs/runbook.md` — update §"Understanding the output": rows beyond fee
  placeholders are now blank, not VLOOKUP

**Do not generate.**
- Changes to any other script
- Changes to `schema.py`

**Done-check.**
```bash
cd aetheris-agents/boxy-pipeline
pip install -r requirements.txt -q
python3 -m pytest tests/test_order_formatter.py -v
python3 main.py \
  --drawings data/samples/Joey-_Kitchen_2D_Plans_V2.pdf \
             data/samples/Joey-_Kitchen_Plan_V2.pdf \
  --catalog  data/samples/Updated_Boxy_MSRP_Sales_Order_Form.xlsx \
  --template data/samples/Updated_Boxy_MSRP_Sales_Order_Form.xlsx \
  --project  Joey_Kitchen_V2 \
  --upper-finish "2001:Ivory White:2000" \
  --lower-finish "2004:Mingo Oak:2000"
python3 -c "
import openpyxl
wb = openpyxl.load_workbook('output/Joey_Kitchen_V2_order_form.xlsx')
print('Sheets:', wb.sheetnames)
assert wb.sheetnames == ['2000 Order Form'], 'Expected exactly one sheet'
ws = wb.active
errors = [(r, c, ws.cell(r,c).value) for r in range(31,68) for c in range(1,12)
          if ws.cell(r,c).value and '#NAME?' in str(ws.cell(r,c).value)]
assert not errors, f'#NAME? errors found: {errors}'
print('OK — one sheet, no #NAME? errors')
"
```

**Claude-code prompt.**
> Fix two output defects in `scripts/order_formatter.py` per
> `docs/backlog-2026-06.md §BL-010`.
>
> 1. After loading the template workbook with openpyxl, delete all sheets
>    except `"2000 Order Form"` before writing any data.
> 2. After writing all line items and fee placeholder rows, clear all cells
>    in columns B–K (cols 2–11) for rows `(last_written_row + 1)` through
>    `67` by setting each cell's value to `None`.
>
> Update `tests/test_order_formatter.py`:
> - Unit test: output workbook has exactly one sheet named `"2000 Order Form"`.
> - Integration test (`@pytest.mark.integration`): no cell in rows 31–67
>   contains a string with `"#NAME?"` after a full pipe run.
>
> Update `docs/runbook.md` §"Understanding the output": replace the note
> about rows 42–67 retaining VLOOKUP formulas with a note that all rows
> beyond the fee placeholders are blank.
>
> Run the done-check from §BL-010 and include actual output (including the
> Python verification snippet result) in your review packet.

**Closed 2026-09-14 (closing sweep).** Landed at agents `ab2fca6`, `63e3069`. The row has no Done-when; its Fix and Done-check are the test, and the live Done-check run is recorded nowhere, so each defect is established from code and tests instead:

1. *Output has only `2000 Order Form`* — `boxy-pipeline/scripts/order_formatter.py` deletes every other sheet on load (:55–:57); `test_output_has_single_sheet` passes.
2. *No stale formulas past the last written row* — the clear loop sets columns B–K to `None` through `TEMPLATE_LAST_ROW` (:99–:102). The integration test checks rows 42–67 empty rather than rows 31–67 for `#NAME?`, and boxy-pipeline is dormant, so it is not in the gate.
3. *Runbook updated* — `boxy-pipeline/docs/runbook.md` §Understanding the output.

The harness's older BL-010 (the OpenRouter adapter, harness `5a6b1cf`) is a different item in a different repository's id space; it is not this row.

---

### BL-097 — DONE 2026-09-14 · Orchestrator: selecting a Recent prompt covers Run and the env disclosure (#TBD)
**Status:** DONE
**Size:** XS · **Priority:** medium · **Section:** aetheris-agents (`rig/`)

Filed 2026-08-04. On the Orchestrator idle view, clicking a **Recent** entry renders a card over the
Run button and the "Additional env vars" disclosure. The screen is unusable — env cannot be set, no
other prompt can be picked, the run cannot be started — until you navigate away and back.

**Mechanism (one line).** The overlaying element is the *filter-suggestions* dropdown, not the
Recent list: it is absolutely positioned (`absolute left-0 right-0 top-full mt-1 z-10`,
`OrchestratorView.tsx:170-171`) inside the `relative` wrapper that holds only the textarea (`:159`),
so it paints over everything below — the env disclosure (`:186-239`) and Run (`:241-246`). Its
visibility is derived **purely** from `suggestions.length > 0` (`:169`), and `suggestions` is
`history.filter(h => h.toLowerCase().includes(request.toLowerCase()))` (`:133-135`). Selecting a
Recent entry calls `setRequest(h)` (`:257`), after which `h` trivially contains itself — so the
dropdown opens and **can never close**, because the condition that opens it is now permanently true.
Navigating away "fixes" it only by unmounting the component and resetting `request`.

The Recent list itself is innocent and correctly hides once the box is populated (`:247`, gated on
an empty request).

**Wider than the reported repro.** The same permanent overlay appears whenever *typed* text
substring-matches any stored history entry — Recent selection is just the reliable way to reach it,
since it guarantees an exact self-match. There is no blur, Escape, or selection dismissal anywhere.

**Minimal fix (this row).** Give the dropdown an explicit open flag instead of deriving visibility
from the filter result: opened by typing, closed by selection, Escape, and blur. No relayout, no
relocation, no change to the `extra_env` panel or `ParamsStrip`.

**Done when:** selecting a Recent entry populates the request box and dismisses cleanly; Run and the
env disclosure stay clickable; a second selection works inline with no click-away; `bun run lint`
and `bun run build` green.

**Follow-up, deliberately NOT in scope here:** move Recent into a scrollable right-side panel. That
is a UX enhancement — it would also make Recent reachable while the box is populated, which the
current design intentionally does not do — and it should be decided on its own merits, not folded
into an unbreak.

`Source: BL-097, 2026-08-04 (reported from the Rig UI during the cloudcost batch).`

**Closed 2026-09-14 (closing sweep).** Landed at agents `779018d`; click-through recorded at `b35daca`. Done-when:

1. *Selecting a Recent entry populates the box and dismisses cleanly* — explicit open flag in `rig/src/views/OrchestratorView.tsx` (:146, :178–:182, :192–:193, :273).
2. *Run and the env disclosure stay clickable; a second selection works inline* — operator click-through, 2026-08-04, `docs/rig/milestones/bl-097-recent-prompt-overlay-implementation-notes.md` (:81–:85).
3. *`bun run lint` and `bun run build` green* — recorded in the same notes (:58) at landing; not re-run at this close.

---

### BL-146 — DONE 2026-09-14 · a row's status marker can be a quotation of a different row's disposition (#TBD)
**Status:** DONE
**Kind:** defect · **Census items:** n/a (surfaced by gc t1's row census) · **Contract:** none
**Size:** S · **Priority:** low–medium
**Section:** process / backlog hygiene (`docs/backlog-2026-06.md`)

Filed 2026-08-12 at gc t3. **This row poses the question; it does not settle it.**

**What happened.** gc t1's status extraction classified **BL-137** as closed. It is not. The marker
it matched is at `:8155`, and it is a **quotation of a row in `cloudcost/m2-milestone.md`** — BL-137's
body quotes that row's disposition, in the same bold-marker form a row uses for its own status, as a
lead for BL-137's own census. BL-137 was filed 2026-08-10 and is open. The extraction was corrected
by hand and the exclusion recorded; the point of this row is that **the correction was a human
judgement, not something the file's structure made available**.

*(The offending marker is described above rather than reproduced. Quoting it literally — as the
first draft of this row did — made **this** row trip the same extraction, which the done-check
caught. That is the hazard demonstrating itself, and it is recorded here rather than left armed: a
row that reads as closed to any marker-keyed reader is not a row that stays open.)*

**Why the existing rules do not cover it.** Any status extraction keyed on bold markers inside a row
body will read a quoted marker as the row's own. There is no syntactic difference between a row
saying it is closed and a row quoting something else that is closed. The same trap caught a second
row from the other direction — **BL-014**, whose body carries no status at all and which a
span-bounding defect briefly credited with a marker from a table about other rows.

**Determine whether row status should be structurally distinguishable from quoted text** — a
dedicated field, a fixed position, or a rule that quoted dispositions are fenced. Any answer must
survive the file's actual practice, in which rows quote other rows' dispositions routinely and
usefully; the goal is not to stop that.

**Done when:** either a structural convention is stated and the existing rows conform to it, or the
hazard is recorded as accepted with the reason, so a later extraction author is warned rather than
surprised.

**Costs:** S. The population is small — one confirmed false positive across 143 rows — but the cost
of the failure is a wrong closed/open answer that reads as confident.

`Source: gc t1's row census, 2026-08-11; the BL-137 false positive and the BL-014 span defect are
recorded at docs/milestones/gc-t1-implementation-notes.md §I. Filed gc t3, 2026-08-12, per D4.`

**Closed 2026-09-14 (closing sweep), on the Done-when's first branch.** Landed at agents `7841060` (ds t0). Done-when:

1. *A structural convention is stated* — the depth-0 `**Status:**` field at offset 1, closed three-word vocabulary, `scripts/backlog_status.py` module docstring (:1–:7) and defeat 4 (:43–:58).
2. *Existing rows conform* — `python3 scripts/backlog_status.py --check` at `e6f0227`: "246 of 246 row ids carry exactly one field", exit 0.

This overrides `docs/milestones/ds-t0-implementation-notes.md`'s *"BL-146 stays open"* (legacy expressions still carry the hazard): the Done-when does not require the legacy expressions to be removed, and `--census` already reports them as occurrence counts, never per-row claims, for exactly that reason.

---

### BL-220 — DONE 2026-09-14 · a recorded eval-suite split does not survive a store round-trip (#TBD)
**Status:** DONE
**Kind:** defect · **Contract:** D8
**Size:** S · **Priority:** high
**Section:** harness (`../aetheris/lib/aetheris/store.ex`, `../aetheris/lib/aetheris/eval/`)

`Eval.Suite` gained `:split` at m14 T8. `eval_suites` has five columns and no split column, and
`Store.row_to_eval_suite/1` does not set the field, so a suite reloaded from the store comes back
`split: nil` — `split_status/1` `:none`, holding nothing out. Verified at T8 by a round-trip probe
on an in-memory test DB.

The failure is safe rather than silent at the struct level: the reload reports no split rather than
a wrong one. It is **not** safe at the gate level. m14 T9 cannot distinguish "no split was ever
recorded" from "the split did not survive the reload" — both read `:none` from the struct alone —
so a gate that reloads its suite silently runs with nothing held out and reports a clean result.
That is the **Silent-wrong-answer** class, in the component whose whole purpose is holding the same
tasks out across runs.

**Sequencing.** Must land before m14 T9. Ruled at the T8 review.

**Done when.** A recorded split survives insert and reload with both sides intact and in order; a
suite that never had one still reads `:none`; and a test asserts the two are distinguishable after
a round-trip, not merely that the happy path works.

`Source: m14 T8, 2026-09-12, harness `1c459cd`. Citations re-resolved at that commit: the DDL is
`lib/aetheris/store.ex:965`–`:971` (five columns), the insert `:2066`, the three read paths `:2087`,
`:2101` and `:2115`, and `row_to_eval_suite/1` `:2125`. `lib/aetheris/eval/store.ex` carries no
second path — `insert_suite/1`, `get_suite/1`, `get_suite_by_name/1` and `list_suites/0` (`:81`,
`:89`, `:97`, `:103`) delegate to `Aetheris.Store`. The struct's own moduledoc records the gap under
§Not persisted (`lib/aetheris/eval/suite.ex:63`–`:70`).`

**Closed 2026-09-14 (closing sweep).** Landed at harness `32d8524`. Done-when:

1. *A recorded split survives insert and reload, both sides intact and in order* — `test/aetheris/eval/store_test.exs` "a recorded split reloads with both sides intact and identically ordered" (:253), over the `split_json` column (`lib/aetheris/store.ex:1018`).
2. *A suite that never had one still reads `:none`* — same file (:270).
3. *A test asserts the two are distinguishable after a round-trip* — "an empty recorded split stays distinguishable from no split after a reload" (:288): `:current` vs `:none` with `held_out` empty on both.

---

### BL-221 — DONE 2026-09-14 · eval runs carry no availability marker, so a baseline can be contaminated by skill-available runs (#TBD)
**Status:** DONE
**Kind:** defect · **Contract:** D8
**Size:** M · **Priority:** high
**Section:** harness (`../aetheris/lib/aetheris/eval/`)

`Runner.run_task/2` stores every eval run under the task's own id, with nothing recording whether a
skill entry was available to that run. A later `Baseline.lock/2` over a held-in task pulls those
runs into the no-skill baseline. `AB.run_forked/5` executes through `Runner.run_task/2`, so both
arms of control 1 land the same way.

**Why high rather than medium.** D8's control 1 compares an arm with the entry available against an
arm without. If the "without" baseline silently contains runs that had it, the comparison measures
nothing and still reports a number — **Silent-wrong-answer**, in the measurement m14's P2 exists to
produce.

**Sequencing.** Must land before any real `Gate.run/3`, not merely before m14 T10. A gate run
against a contaminated baseline is worse than none, because it produces a figure that will be
cited.

**Done when.** An eval run records whether a skill entry was available to it; `Baseline.lock/2`
selects on that; and a test asserts a mixed-availability task cannot produce a no-skill baseline
containing available runs.

`Source: m14 T9, harness `6633a4b` (pushed); authorised by the arbiter at the T9 review. Citations
resolved at that commit: `run_task/2` is `lib/aetheris/eval/runner.ex:47`, persisting at `:193`
(scored) and `:219` (failed); the `eval_runs` DDL is `lib/aetheris/store.ex:980`–`:994`, no
availability column; `Baseline.lock/2` is `lib/aetheris/eval/baseline.ex:110`, reading every run for
the task at `:113` and taking the K most recent at `:118`; `AB`'s executor calls `Runner.run_task`
at `lib/aetheris/eval/ab.ex:112`. T9's notes name the gap at
`docs/aetheris/milestones/m14-t9-implementation-notes.md:58`–`:62`.`

**Closed 2026-09-14 (closing sweep).** Landed at harness `ab98249`. Done-when:

1. *An eval run records whether a skill entry was available* — `Eval.Run.skill_availability/1` (`lib/aetheris/eval/run.ex:75`–`:82`), set on both Runner save paths (`runner.ex:230`, `:257`) and persisted (`store.ex:1042`); three-valued, a deviation recorded in `bl-221-implementation-notes.md`.
2. *`Baseline.lock/2` selects on it* — `lock_unavailable/3` (`lib/aetheris/eval/baseline.ex:139`–`:142`).
3. *A test: a mixed-availability task cannot produce a no-skill baseline containing available runs* — `test/aetheris/eval/skill_availability_test.exs` (:102): two failing `:unavailable` runs among six newer passing `:available`/`:unknown` ones lock `run_count == 2`, `pass_rate == 0.0`.

---

### BL-223 — DONE 2026-09-14 · approved skill bodies have no file substrate, so D2's served path points at nothing (#TBD)
**Status:** DONE
**Kind:** defect · **Contract:** D2, D9, D10; `../aetheris/docs/aetheris/determinism-contract.md` §2 *Tool surface*, §4
**Size:** M · **Priority:** high
**Section:** harness (`../aetheris/lib/aetheris/skill/`, `../aetheris/lib/aetheris/store.ex`)

D2 says index injection serves `(id, name, description, path)` and the body is read on demand. No
body file exists. Bodies live in the `skills` table's `prompt_template` column; the table carries no
path, and no m14 ticket creates one. m04 kept the body in the table because it injected content
directly.

m14 T12 cannot land without this: it is the ticket that serves the path. T13 inherits it —
consultation is measured as `read_file` events under the skills path, so with no files there are no
reads to count. P3 is blocked entirely.

**RULED at the T12 scope check, 2026-09-13. The row implements this; it does not reopen it.**

The injector never writes a body file. A file written at run start is not git-tracked, so it is
outside the tool surface BL-197 declared (git-tracked files under `sandbox_path` plus
`tool_surface_extras`). The determinism contract §4 places anything outside the tool surface outside
the fork guarantee, so an injector-written body either escapes `tools_hash` — two runs with identical
hashes reading different content, which is the failure the hash exists to prevent — or forces the
surface to widen at runtime, which is the same as having no declared surface. m14 §6's
machine-written-documents non-goal agrees, but the contract argument stands on its own.

Bodies are human-committed files: git-tracked under the agent root, declared in
`tool_surface_extras`, read through `read_file` so the read is a recorded event. Approval remains a
human decision (q3) and now has a human artifact attached to it.

**Done when.**
- A skills row can name its body file, and the name is set as part of approval rather than at
  insert — an unapproved row has no served body. m14 T11 made approval one-way in the store's own
  statement; whatever carries the path must not reopen that.
- An approved row whose file is absent, or present but outside the declared tool surface, is NOT
  served and the omission is visible — never served as a path that fails to read, and never silently
  dropped from the catalog. Absent is unknown, and a catalog that quietly omits an entry is the same
  silent-wrong-answer class as one that serves a dead path.
- A test asserts the surface membership check, not merely that the file exists on disk.
- The relationship to `content_hash` is decided and stated: whether the row's hash covers the file,
  the table's prose, or both, and what happens when they disagree.

**Do not generate.** Any injector-side write. Any change to m14 T12's serving design beyond giving it
a substrate to serve — T12 is written and waiting.

`Source: the m14 T12 scope check, 2026-09-13, at harness `737a8b4` (pushed); ruled by the arbiter.
Citations resolved at that commit: the `skills` columns are the `INSERT` at
`lib/aetheris/store.ex:1333`–`:1337`, none a path; the tool surface is
`docs/aetheris/determinism-contract.md` §2 *Tool surface* and `lib/aetheris/run_config.ex:64`–`:67`;
the outside-surface clause is §4 *Anything outside the tool surface*; T13's consultation measure is
`docs/aetheris/milestones/m14-skills-auto-extraction.md` §4 T13 *Scope*.`

**Corrected at the BL-223 review, 2026-09-13.** This row's ruling said a body is "declared in
`tool_surface_extras`". That is over-specific: the invariant is membership of the run's DECLARED
TOOL SURFACE, which `tools_hash` covers by both branches — git-tracked under `sandbox_path`, or
named in `tool_surface_extras`. A body tracked under `sandbox_path` is in the hash and is a
committed human artifact, so requiring an extras entry adds ceremony with no determinism content.
`Skill.Body.resolve/2` as implemented checks surface membership and is correct; this row's wording
was not. The Done-when's "outside the declared tool surface" already read correctly.

Approval remains stricter than resolution by design: `approval/2` requires the file to be
git-tracked under `:root` with no extras, because the body must be a committed artifact; resolution
requires only that the run's surface covers it. Both tighten safely. Implemented at harness
`017f4e2`.

**Closed 2026-09-14 (closing sweep).** Landed at harness `017f4e2`. Done-when:

1. *A row names its body file, set at approval, one-way* — insert refuses a body (`lib/aetheris/store.ex:1357`–`:1366`); the only write is approval's `UPDATE … WHERE status = 'validated'` (:1505–:1509); tests `store_test.exs` (:141), lifecycle `:already_approved` (:150).
2. *Absent or outside-surface body not served, omission visible* — `Skill.Body.classify_body` (`body.ex:153`–`:164`), warning logged inside `resolve/2` (:141–:148); `body_test.exs` (:89, :151).
3. *A test asserts surface membership, not file existence* — `body_test.exs` (:74): an existing file is `{:withheld, :outside_surface}` until it is in the surface.
4. *`content_hash` relationship stated* — `body.ex` moduledoc (:35–:45): `content_hash` covers the table's prose, `body_hash` the approved file; a mismatched file is withheld (`body_test.exs` :104).

---

### BL-229 — DONE 2026-09-14 · `use_case` reaches a run through no path but a hand-written agent file (#TBD)
**Status:** DONE
**Kind:** defect · **Contract:** D2, D7
**Size:** M · **Priority:** high
**Section:** harness (`../aetheris/lib/aetheris/execution/tool/spawn_agent.ex`, `../aetheris/lib/aetheris/api/run_policy.ex`)

`RunConfig` gained `use_case` at m14 T12, and `nil` serves nothing — correctly, absent is unknown. Two
producers never set it, so their runs are served nothing while appearing to be ordinary runs:

- `spawn_agent` builds child configs without it. Sub-agents doing the repeated work of a fan-out are
  exactly the population an extracted skill would help.
- The playground API's `RunPolicy` builds its sanitized map key by key, and `use_case` is not a key.

One row because it is one defect: `use_case` fails to propagate everywhere except where a human types
it. Fixing one producer and not the other leaves the same hole.

**Done when.** A spawned child inherits its parent's `use_case` unless overridden; the playground API
accepts one and passes it through; a test per producer asserts the run's recorded config carries it.
Inheritance is a decision the implementing round states, with why inherit rather than require.

`Source: m14 T12, harness `95f3ccb` (pushed); named in T12's notes under Exposures. Citations resolved
at that commit: `build_child_config/4` is `lib/aetheris/execution/tool/spawn_agent.ex:122`, its
`%RunConfig{}` at `:126` with no `use_case`; `build_sanitized/2` is `lib/aetheris/api/run_policy.ex:418`,
consumed by `RunConfig.from_map/2` at `lib/aetheris/api/playground_router.ex:90`, which reads
`use_case` at `lib/aetheris/run_config.ex:194`. **Deviation from the filing prompt:** it named the
payslip orchestrator as a nine-child spawner; at agents `8a2737e` that file's `tools` is
`["run_command"]` (`payslip/agents/payslip_orchestrator.exs:21`) and it spawns nothing. The
`spawn_agent` declarers there are `eduloka/agents/eduloka_orchestrator.exs:143`,
`provenance/agents/classification_orchestrator.exs:41` and `provenance/agents/zip_orchestrator.exs:41`.`

**Third producer, appended at the BL-221 review, 2026-09-13.**
`Runner.build_run_config/3` sets neither `use_case` nor `tool_surface_extras`, so no
eval run is served anything — including Gate's held-in 'with entry' runs and
control 1's arm B, whatever `make_available` does to the task template. BL-221's
marker reports those runs truthfully as `:unavailable`; the point is that the
'with' arm cannot be made available at all.

This producer is what blocks m14 P2's discharge: the discharge is one real
`Gate.run/3`, and the gate cannot serve an entry through Runner as it stands.
Cited at harness `ab98249`.

`Citations resolved at harness `ab98249` (pushed): `build_run_config/3` is
`lib/aetheris/eval/runner.ex:268`, its `%RunConfig{}` at `:272`–`:288` with neither field; Gate's
held-in arm applies `make_available` at `lib/aetheris/skill/gate.ex:448` and runs through
`Runner.run_task/2` (default at `:442`); control 1's arm B is `with_entry` at `:365`, in `fork_one/5`
(`:363`).
The append was not amended into the row because the row is pushed.`

Done-when corrected at the BL-229 review, 2026-09-13. The clause 'a spawned
child inherits its parent's use_case unless overridden' is wrong, and the
implementation is right to have no override. The only channel an override could
arrive through is the model's spawn_agent call, and the model is not the party
that chooses which approved entries its own run is served — the same boundary
that keeps tool_surface_extras off the playground's client field list. Read the
clause as: a spawned child inherits its parent's use_case, with no per-spawn
override. Implemented at harness `c2c7099`.

`Citations resolved at harness `c2c7099` (pushed): the no-override statement is
`lib/aetheris/execution/tool/spawn_agent.ex:15`–`:22`; `tool_surface_extras` is stated not to be a
client field at `lib/aetheris/api/run_policy.ex:29`. Appended, not amended: the row is pushed.`

**Sequencing void, 2026-09-14.** m14's P2 kill criterion fired at harness `1c717cf` (pushed), so
there is no discharge run for this row to block, which is what the sentence above claims it does. The
defect stands and its priority is unchanged; what is void is the deadline, not the row. Recorded per
R40: a deferral is recorded on the row it defers.

**Correction, 2026-09-14.** The *Sequencing void* append above says *"The defect stands"*. It did not: the fix had landed at harness `c2c7099` (2026-09-13 15:18 +0530), about 16.5 hours before that append (agents `1ae2db1`, 2026-09-14 07:53 +0530), and this row already recorded *"Implemented at harness `c2c7099`"*. Only the voided deadline is accurate. The append is left as written.

**Closed 2026-09-14 (closing sweep).** Landed at harness `c2c7099`. Done-when, as corrected at the BL-229 review:

1. *A spawned child inherits its parent's `use_case`, no per-spawn override* — `lib/aetheris/execution/tool/spawn_agent.ex:154`–`:155` copies it from the parent.
2. *The playground API accepts one and passes it through* — `lib/aetheris/api/run_policy.ex` (:75, :192, :437), read by `RunConfig.from_map` (`run_config.ex:202`).
3. *A test per producer on the recorded config* — `spawn_agent_test.exs` (:175), `playground_runs_test.exs` (:204–:212), and for the third producer, Runner, `skill_availability_test.exs` (:75).
4. *Why inherit rather than require, stated* — `spawn_agent.ex` moduledoc (:15–:22) and `bl-229-implementation-notes.md` §Decisions.

---

### BL-232 — DONE 2026-09-14 · `AB.run_forked/5` does not fork: control 1's arms run from scratch (#TBD)
**Status:** DONE
**Kind:** defect · **Contract:** D8
**Size:** L · **Priority:** high
**Section:** harness (`../aetheris/lib/aetheris/eval/ab.ex`, `../aetheris/lib/aetheris/eval/runner.ex`)

D8's control 1 *"forks both variants from `fork_run_id` at `fork_step`, sharing the common prefix"*.
`AB.run_forked/5` sets `fork_from` and `fork_step` on each arm's template and `Runner` copies them
into the `RunConfig`, but only `fork_context` builds a prefix and `Runner` never sets it, so both arms
start from nothing. Established by reading the code at the BL-221 round, not by a run.

**Why high.** m14 T9's gate harness was built and reviewed against this executor. Its structure is
sound; what it measures is not what D8 specifies. Two arms run from scratch differ by every source of
run-to-run variance, not only by the entry's availability, which is what sharing a prefix exists to
remove. A cost delta measured this way is noisier than the effect it looks for, and nothing says so
where the number is produced. Second consequence: no fork prefix can carry a served body into an arm,
so the "with entry" arm cannot inherit one.

**Done when.** `run_forked/5` builds the shared prefix D8 specifies, or the gap is closed the other
way — the function is renamed and D8's control 1 is re-specified with the arbiter's ruling on the
record. A function whose name asserts a property it does not have is not a resolution.

`Source: the BL-221 review, 2026-09-13; harness `ab98249` (pushed), named in
`docs/aetheris/milestones/bl-221-implementation-notes.md` under Exposures. Citations resolved at that
commit: `run_forked/5` is `lib/aetheris/eval/ab.ex:77`, documented at `:69` as sharing the prefix;
`apply_fork/3` (`:130`) puts `mode`, `fork_from` and `fork_step` at `:133`–`:135`;
`build_run_config/3` (`lib/aetheris/eval/runner.ex:268`) copies the two at `:285`–`:286` and sets no
`fork_context`. The prefix is read only where `fork_context != []`: `lib/aetheris/agent/server.ex:632`
and `lib/aetheris/execution/loop.ex:71`. Its one builder is `Fork.from_step/3`
(`lib/aetheris/execution/fork.ex:40`, `fork_context` at `:186`), called from `lib/aetheris.ex:74` and
`lib/aetheris/cli/commands/fork.ex:115`, never from `Eval`. D8's wording is quoted at
`docs/aetheris/milestones/m14-skills-auto-extraction.md:147`; Gate defaults to this executor at
`lib/aetheris/skill/gate.ex:341`.`

**Closed 2026-09-14 (closing sweep), on the Done-when's first branch.** Landed at harness `86b4287`; direction (a), `bl-232-implementation-notes.md:3`. Done-when:

1. *`run_forked/5` builds the shared prefix D8 specifies* — `Runner.with_fork_prefix/1` builds it with `Fork.from_step/3` (`lib/aetheris/eval/runner.ex:125`–`:128`, `:146`–`:156`) and refuses rather than running from scratch; `gate_test.exs` end-to-end (:881) asserts both arms' `fork_context` equals the recorded prefix and the first prompt's `message_count` its length, and (:938) the refusal. The name now holds, so the rename branch is not taken.

---

### BL-239 — DONE 2026-09-14 · the held-in arm's comparison differs by more than the candidate (#TBD)
**Status:** DONE
**Kind:** defect · **Contract:** D8
**Size:** M · **Priority:** high
**Section:** harness (`../aetheris/lib/aetheris/skill/gate.ex`, `../aetheris/lib/aetheris/eval/baseline.ex`, `../aetheris/lib/aetheris/skill/injector.ex`)

BL-236 serves a measured run the use_case's eligible catalog plus the listed candidate, so control 1's
arms differ by exactly the candidate. The held-in arm does not have that property. It compares a
measured run (catalog + candidate) against a baseline `lock/2` builds only from runs BL-221 marks
`:unavailable` — runs with no `skill_injected` event, which carry no catalog at all. Where the use_case
has any approved entry, the held-in comparison differs by the whole catalog plus the candidate.

**Why high.** The held-in arm exists to reject a candidate that regresses tasks outside the held-out
split, and a held-in regression rejects regardless of what control 1 shows. A regression it attributes
to the candidate may belong to the catalog, and an improvement may mask one.

Distinct from BL-234, which is historical contamination of baselines locked before BL-221; this is a
structural mismatch between what a measured run carries and what its baseline carries.

**Done when.** The held-in comparison's two sides differ by the candidate alone — either the baseline
is locked from runs carrying the same catalog, or the measured held-in run carries only the candidate —
and a test asserts the difference. The resolution states which direction and why; both change what a
baseline means.

`Source: the BL-236 review, 2026-09-13, by the round that created the condition; harness `901f7d1`
(pushed). Citations resolved at that commit: `serve_measured/3` serves the eligible catalog beside the
listed entries at `lib/aetheris/skill/injector.ex:122`–`:136`; the held-in arm is given the same
measurement at `lib/aetheris/skill/gate.ex:459` and compared against `EvalStore.get_latest_baseline/1`
at `:479`, documented at `:62`–`:64`; `lock/2` keeps only `:unavailable` runs at
`lib/aetheris/eval/baseline.ex:140`; `:unavailable` is "no `skill_injected` event" at
`lib/aetheris/eval/run.ex:75`–`:80`.`

**Closed 2026-09-14 (closing sweep).** Landed at harness `8ea4194` (docs `b9f3ca2`). Done-when:

1. *The held-in comparison's two sides differ by the candidate alone* — the held-in measurement withholds the catalog (`lib/aetheris/skill/gate.ex:287`–`:288`, `:476`), so the injector serves only the listed entry (`injector.ex:129`–`:143`), against a baseline of served-nothing runs (`baseline.ex:139`–`:140`).
2. *A test asserts the difference* — `gate_test.exs` "with an approved catalog in scope, the held-in run is served the candidate only…" (:950–:987).
3. *Which direction and why* — direction (ii), `bl-239-implementation-notes.md:3`, :10–:18: it leaves `lock/2` and what a baseline means unchanged.

---

### BL-242 — DONE 2026-09-14 · the frequency prior compares whole-run sequences against segment-sized candidates (#TBD)
**Status:** DONE
**Kind:** defect · **Contract:** D3, D8
**Size:** L · **Priority:** high
**Section:** harness (`../aetheris/lib/aetheris/skill/frequency_prior.ex`, `../aetheris/lib/aetheris/skill/gate.ex`)

`FrequencyPrior` computes the dominant tool sequence per whole run. `Skill.Candidate` emits one candidate
per segment. `re_encodes?/2` tests equality between the two, so a segment-sized candidate equals the
dominant only when a whole run is a single segment. The four live `payslip` rows normalise to
`[run_command]`, `[spawn_agent]`, `[wait_for_all]` and `[]`; their source run normalises to
`run_command → spawn_agent → wait_for_all`.

On a multi-segment corpus every non-empty candidate is therefore `:distinct` and every empty one is
`:no_sequence`. Control 2 cannot reject there, and cannot be made to by tuning its constants: they
decide whether a dominant exists, not what unit it is.

Neither half is wrong at its own granularity. D8 specified the prior when m04's extractor produced
whole-run skills; m14 D3 replaced that with segmentation, and nothing re-derived the prior against the
new shape.

**Why high.** P2's kill criterion is "no candidate beats the frequency prior across the eval suite".
With control 2 structurally abstaining, that verdict rests on control 1 alone, and a discharge run would
report two controls where one ran. T9's Do-not-generate exists because "a gate that validates on
control 1 alone is the prior art's named failure".

**Done when.** Control 2 compares like with like — the prior is computed over the same unit a candidate
describes — and a test asserts a candidate that DOES re-encode its scope's dominant pattern, on a corpus
of multi-segment runs, is rejected. That test is the row's point. State whether `min_corpus_runs` and
the majority rule still hold at the new granularity; they were unmeasured at the old one.

Must land before m14 P2's discharge.

`Source: the BL-239 review, 2026-09-13; harness `8ea4194` (pushed). Established from code, not from a
run. Citations resolved at that commit: one sequence per whole run at
`lib/aetheris/skill/frequency_prior.ex:149`–`:156`, counted at `:94`–`:97`; `re_encodes?/2` at
`:121`–`:122`; the constants at `:2` and `:158`–`:164`. One candidate per segment is `extract/2` at
`lib/aetheris/skill/candidate.ex:104`, its `tool_sequence` bounded to the segment at `:191`. Control 2 is
`lib/aetheris/skill/gate.ex:316`–`:333`, rejecting only at `:517`. D3 is
`docs/aetheris/research/bl-008-synthesis-2026-08.md:80`, D8's control 2 `:127`–`:129`; m14's whole-run →
segment row is `docs/aetheris/milestones/m14-skills-auto-extraction.md:44`, P2's kill `:425`, T9's
Do-not-generate `:484`–`:486`. The four rows are the `use_case = 'payslip'` rows of `priv/aetheris.db`'s
`skills` table, all `candidate`, all citing `payslip-orch-5Jhdvw`, whose `tool_called` events read
`run_command`, `spawn_agent` ×3, `wait_for_all`. **Deviation from the filing prompt:** it said no input
can make control 2 reject. One can: a corpus whose runs are one segment each, which is T10's own fixture
(`test/aetheris/skill/gate_test.exs:28`, the rejection test at `:145`) — every corpus run there is a
single-tool sequence a hand-built candidate can equal. The claim holds for multi-segment corpora, which
is what segmentation exists to produce. Nor does the live table have a dominant: one source run is a
thin corpus, so the sequence above is that run's, not a computed prior.`

**Sequencing void, 2026-09-14.** m14's P2 kill criterion fired at harness `1c717cf` (pushed), so
there is no discharge run for this row to precede, which *"Must land before m14 P2's discharge"*
requires. The defect stands and its priority is unchanged; what is void is the deadline, not the row.
Recorded per R40: a deferral is recorded on the row it defers.

**Correction, 2026-09-14.** The *Sequencing void* append above says *"The defect stands"*. It did not: the fix had landed at harness `95c6840` (2026-09-13 19:12 +0530), about 12h41m before that append (agents `1ae2db1`, 2026-09-14 07:53 +0530), with the D8 amendments `b41f81b`, `552dbb9` and `19ba133` also before it. Only the voided deadline is accurate. The append is left as written.

**Closed 2026-09-14 (closing sweep).** Landed at harness `95c6840`, amended by `021be49`, `b41f81b`, `552dbb9`, `19ba133`. Done-when:

1. *The prior is computed over the unit a candidate describes* — each corpus run is read through `Candidate.extract` (`lib/aetheris/skill/frequency_prior.ex:224`–`:231`), segment patterns counted once per run (:165) into a dominant set (:254–:259) that `re_encodes?/2` tests (:199).
2. *A test: a re-encoding candidate on multi-segment runs is rejected* — `gate_test.exs` "on multi-segment runs, a candidate re-encoding the dominant segment pattern is rejected" (:195–:229): three segments per run, `segments_read == 3 * min_corpus_runs()`, `verdict == :rejected`.
3. *Whether `min_corpus_runs` and the majority rule still hold* — `bl-242-implementation-notes.md` (:49–:50, :62–:65) and `docs/aetheris/research/bl-008-synthesis-2026-08.md` (:144–:154).

---

### BL-235 — DONE 2026-09-14 · eval test files tagged `:integration` are excluded from every gate run (#TBD)
**Status:** DONE
**Kind:** defect
**Size:** S · **Priority:** medium
**Section:** harness (`../aetheris/test/test_helper.exs`, `../aetheris/test/aetheris/eval/`)

`runner_test.exs` and `baseline_test.exs` carry `@moduletag :integration`, which `test_helper.exs`
excludes, so `mix test` never runs them. Discovered at the BL-221 round, when a Done-when test placed
in one of them would not have executed. The gate set has been reported green all through m14 with
these files never running.

**Census at harness `ab98249`.** `mix test` reports `1194 tests, 0 failures, 136 excluded`; the
excluded figure spans all five tags in `exclude:`. For `:integration`:

- **Eval files:** `runner_test.exs` 10, `baseline_test.exs` 17, and a third the filing prompt did not
  name, `ab_test.exs` 14 — each from `mix test <file>`, which printed `N tests, 0 failures, N excluded`.
- **Every `@moduletag :integration` file** — those three plus `integration/checkpoint_resume_test.exs`,
  `codebase_qa_test.exs`, `fork_join_test.exs`, `mcp_github_test.exs`, `mcp_http_test.exs`,
  `skill_extraction_test.exs`, `spawn_agent_test.exs`, `wait_for_event_test.exs` and
  `worker/client_internet_test.exs`. `mix test` over exactly those files printed
  `71 tests, 0 failures, 65 excluded`; the 6 that ran are `skill_extraction_test.exs`'s first module,
  the tag being on its second.
- **`@tag :integration` on single tests:** `skill/segmenter_test.exs:330` is the one in a gated file
  (`12 tests, 0 failures, 1 excluded`). `codebase_qa_test.exs:34`, `mcp_github_test.exs:42` and
  `worker/client_test.exs:171` sit in modules already excluded.

**Done when.** Either the files run under the standard gate, or the exclusion is deliberate and
recorded where a reader of the gate output can see what it does not cover.

`Source: the BL-221 review, 2026-09-13; harness `ab98249` (pushed), named in
`docs/aetheris/milestones/bl-221-implementation-notes.md` under Deviations. Citations resolved at that
commit: `:integration` is in `exclude:` at `test/test_helper.exs:12`; the eval tags are
`test/aetheris/eval/runner_test.exs:3`, `baseline_test.exs:3` and `ab_test.exs:3`; the other module
tags are found by `git grep -n "@moduletag :integration" -- test`, the single-test tags by
`git grep -n "@tag :integration" -- test`. Harness `CLAUDE.md:204`–`:206` lists all three eval files
as `@moduletag :integration`, so the tag is documented; the gate's output does not say it.`

**Closed 2026-09-14.** Landed at harness `55bd2f8` (pushed). The Done-when offered two directions and the implementation took both; each clause is met on its own.

1. *The files run under the standard gate* — `@moduletag :integration` is gone from `runner_test.exs`, `baseline_test.exs` and `ab_test.exs`: `git grep -n '@moduletag :integration' 55bd2f8 -- test/aetheris/eval/` returns 0 lines, and the same command over `test` returns 9. `mix test` at `55bd2f8` printed `1227 tests, 0 failures, 95 excluded`, against `136 excluded` before (the commit's own figure); 41 = 10 + 17 + 14, the census above.
2. *The gate output records what it does not cover* — `test/support/exclusion_report.ex`, registered at `test/test_helper.exs:2` and `:8`, ends every run with the excluded tests grouped by filter, with their modules. At `55bd2f8` it printed `Not run by this gate: 95 excluded test(s), by filter`, four groups summing to 95, with no `Aetheris.Eval.*` module in any group.

No criterion was applied to the rest of the `:integration` population (`bl-235-implementation-notes.md`, Decision 3). BL-249 owns that audit.

---

### BL-237 — DONE 2026-09-14 · `baseline_test.exs` has been red since BL-221, invisible behind its tag (#TBD)
**Status:** DONE
**Kind:** defect · **Contract:** D8
**Size:** S · **Priority:** medium
**Section:** harness (`../aetheris/test/aetheris/eval/baseline_test.exs`)

6 of 17 tests in `test/aetheris/eval/baseline_test.exs` fail with `{:error, {:no_unavailable_runs, _}}`.
BL-221 made `lock/2` select `:unavailable` runs only; these tests insert runs with no marker, which
decode to `:unknown`, which `lock/2` correctly refuses. The file carries `@moduletag :integration`
and is excluded from `mix test`, so BL-221's own round reported the gate green with these failures
present.

BL-235 owns the exclusion. This row owns the red: the tests encode `lock/2`'s pre-BL-221 contract and
need converting to the new one, not deleting. A deleted assertion is a lost invariant.

**Done when.** Each of the six either asserts the post-BL-221 contract or is recorded as an invariant
no longer held, with the reason; the file is green under whatever tag regime BL-235 settles on.

`Source: the BL-229 review, 2026-09-13; harness `c2c7099` (pushed). Reproduced at that commit by
`mix test --include integration test/aetheris/eval/baseline_test.exs`, which printed
`17 tests, 6 failures`, with `no_unavailable_runs` on 6 lines of its output. The six:
`lock/2 computes and persists a baseline` (`:124`), `lock/2 takes only k most recent runs` (`:137`),
`compare/2 detects regression when pass rate drops below threshold` (`:159`),
`compare/2 reports no regression when pass rate holds` (`:180`), `compare/2 respects custom threshold`
(`:199`), `compare/2 includes step_delta when step data available` (`:222`). The tag is `:3`;
`lock/2` is `lib/aetheris/eval/baseline.ex:124`, filtering at `:140` and refusing at `:142`. BL-221
is harness `ab98249`.`

**Closed 2026-09-14.** Landed at harness `55bd2f8` (pushed). Done-when:

1. *Each of the six asserts the post-BL-221 contract, or is recorded as no longer held* — all six are converted and none retired. Every run a `lock/2` call selects is built by `make_unavailable_run/4` (`test/aetheris/eval/baseline_test.exs:30`), at `:132`–`:133`, `:148`–`:149`, `:171`, `:192`, `:211` and `:233`. The guarantee each test now asserts is tabulated in `bl-237-implementation-notes.md` Decision 1.
2. *The file is green under BL-235's tag regime* — the tag is removed (BL-235, direction (i)). `mix test test/aetheris/eval/baseline_test.exs` at `55bd2f8` printed `17 tests, 0 failures` and `Not run by this gate: nothing excluded.` The full `mix test` there printed `1227 tests, 0 failures, 95 excluded`, with `Aetheris.Eval.BaselineTest` in no exclusion group.

---

### BL-236 — DONE 2026-09-14 · the gate cannot serve the candidate it is gating (#TBD)
**Status:** DONE
**Kind:** defect · **Contract:** D7, D8
**Size:** L · **Priority:** high
**Section:** harness (`../aetheris/lib/aetheris/skill/gate.ex`, `../aetheris/lib/aetheris/skill/injector.ex`, `../aetheris/lib/aetheris/skill/body.ex`)

`Skill.Gate` accepts only `status: "candidate"`. `Skill.Injector` serves only approved rows, and
`Skill.Body` withholds any other status. So D8's control 1 — "arm B the task with the entry made
available" — cannot make a candidate available, and arm B is arm A for every entry the gate can gate.

This is circular in the ratified design, not in the code: D7 requires validation before approval,
D8's validation requires serving, and serving requires approval. No m14 ticket could have surfaced
it — T9 deferred `make_available` to T12's injection, and T12 built serving for the approved path,
each correct in isolation.

**RULED at the BL-229 review, 2026-09-13.** This row implements the ruling; it does not reopen it.

The gate serves its candidate through the SAME injector, selected by explicit entry list rather than
by status eligibility, and the run records that it was served under a gate measurement. Two
alternatives were rejected: approving before validating makes approval a stamp on unmeasured
entries, which is what D8 exists to prevent; a gate-only content path rebuilds m04's injector under
another name, which m14 T12 retired so two injectors could not coexist.

The "only approved" rule protects production runs from unvetted content. A gate run is the vetting —
the one context where serving an unapproved entry is the point. Explicit and recorded, not bypassed:
the marker is what keeps the invariant checkable.

**Done when.** `Gate.run/3` can serve the candidate under measurement; the serving path takes an
explicit entry list only from the gate and from nowhere else; a run that was served a non-approved
entry carries a recorded marker saying so; a test asserts a run WITHOUT that marker cannot have been
served a non-approved entry — that assertion is the row's point, not the happy path. State where the
marker lives and why a caller cannot forge or omit it.

**Do not generate.** Any status change to reach serving. Any second injector or content-injection
path.

`Source: the BL-229 review, 2026-09-13; harness `c2c7099` (pushed). Citations resolved at that
commit: `fetch_candidate/1` admits only `"candidate"` at `lib/aetheris/skill/gate.ex:271`;
`eligible?/2` admits only `"approved"` at `lib/aetheris/skill/injector.ex:78`; `classify/2` withholds
every other status at `lib/aetheris/skill/body.ex:135`–`:136`. D7's "Only approved entries are served
by the injector" is `docs/aetheris/research/bl-008-synthesis-2026-08.md:117`, D8's control 1 `:126`;
T9's deferral is `docs/aetheris/milestones/m14-t9-implementation-notes.md:16`.`

**Still open, 2026-09-14 (closing sweep).** Unmet: *"the serving path takes an explicit entry list only from the gate and from nowhere else"* — `Runner.run_task/2` accepts `:skill_measurement` from any caller (`../aetheris/lib/aetheris/eval/runner.ex:67`), and `bl-236-implementation-notes.md:28` records that a test or hand-written `.exs` can build one. The other four clauses hold at harness `901f7d1`.

**Closed 2026-09-14.** Landed at harness `2845995` (pushed), the residual round, on the four clauses closed at `901f7d1` and the one the closing sweep left open. Done-when:

1. *`Gate.run/3` can serve the candidate under measurement* — `gate_test.exs:1020`, end to end with the default executors: arm B and the held-in run each carry one `skill_injected` event with payload `served_under: "gate_measurement"`, `status: "candidate"` (`:1057`–`:1067`), and the row stays `candidate` (`:1074`).
2. *The serving path takes an explicit entry list only from the gate, and from nowhere else* — **met, with three bounds.** A `Measurement` is sealed only in `Gate.measurement/3` by `seal/2` (`lib/aetheris/skill/gate.ex:308`–`:317`); `Gate.issued?/1` accepts only that seal over the measurement's own entries and catalog (`:202`–`:206`). `Injector.serve/2` refuses any other with `:measurement_not_from_gate` before the store is read (`lib/aetheris/skill/injector.ex:94`–`:98`), and `Runner.run_task/2` refuses before any run starts or is recorded (`lib/aetheris/eval/runner.ex:72`–`:75`). `RunConfig.from_map/2` does not read the field: `git grep -n skill_measurement 2845995 -- lib/aetheris/run_config.ex` returns the doc (`:74`), the default (`:133`) and the type (`:253`) only. `gate_test.exs:894` asserts a measurement built outside the gate is served by none of `Runner.run_task/2`, `Aetheris.start_run/1`, `Injector.serve/2`; `:978` asserts `issued?/1` refuses seven forgery shapes against a positive control. The bounds:
   - **A caller-supplied executor may retain a sealed measurement for the entries the gate chose.** `run/3`'s `run_forked` and `run_task` options (`gate.ex:409`, `:510`) receive it; `test/support/gate_issued.ex` uses this channel.
   - **A fresh gate seal over the same entries and catalog is accepted**, on any struct carrying it; `gate_test.exs:1016` asserts it.
   - **A term crafted through `binary_to_term/1`, or a replaced `Gate` module, is outside what any in-VM check refuses.**

   All three are recorded at `docs/aetheris/milestones/bl-236-implementation-notes.md:58`–`:63` (§Residual, *What the seal does not stop*), the first as the executor channel of Deviation 1 (`:70`–`:73`).
3. *A run served a non-approved entry carries a recorded marker* — written only in `Injector.payload/2`'s listed clause (`injector.ex:207`–`:213`), appended at step 0 (`:198`–`:201`); `served_under_measurement?/1` reads it (`:77`–`:81`).
4. *A test asserts a run without the marker cannot have been served a non-approved entry* — `injector_test.exs:264`–`:291`, over every non-approved status and seven configs, with a positive control at `:288`; and `:360` over events from both paths.
5. *Where the marker lives and why a caller cannot forge or omit it* — `bl-236-implementation-notes.md:11`–`:19` (the marker) and `:43`–`:51` (acceptance).

`mix test test/aetheris/skill/gate_test.exs test/aetheris/skill/injector_test.exs` at `2845995` printed `67 tests, 0 failures` and `Not run by this gate: nothing excluded.` The residual round's mutation pass (M1–M5, each red on its named test and restored by sha) is in that round's packet, `scratchpad/packet.md` of its session, in neither tree.

A run that fails before serving is recorded `:unavailable`, found by M2 in that round. BL-250 owns it.

---

### BL-145 — DONE 2026-09-14 · the backlog has two status surfaces and says so nowhere (#TBD)
**Status:** DONE
**Kind:** defect · **Census items:** n/a (surfaced by gc t1's row census) · **Contract:** none — the file states no status convention
**Size:** S to decide, M to fix · **Priority:** medium
**Section:** process / backlog hygiene (`docs/backlog-2026-06.md`)

Filed 2026-08-12 at gc t3. **This row poses the question; it does not settle it.**

**What happened.** gc t1 needed every row's status to cross-join against gate claims, and derived it
programmatically. It found **two** surfaces that carry status and **they disagree in both
directions**. Row bodies carry `DONE`/`CLOSED`/`Closed <date>` markers for **33** rows. The
`## Suggested order` table at `:5662` carries ✔ marks for **28**. The union is **48**, and neither
surface alone is right: **20** rows are closed in their body and not ticked in the table
(BL-069, BL-070, BL-073, BL-074, BL-083, BL-090, BL-092, BL-095, BL-096, BL-099, BL-100, BL-101,
BL-104, BL-105, BL-106, BL-107, BL-121, BL-127, BL-131, BL-132), and **15** are ticked with no
closure marker in the body (BL-001, BL-002, BL-003, BL-004, BL-005, BL-009, BL-015, BL-028, BL-029,
BL-031, BL-038, BL-039, BL-050, BL-055, BL-056). Every one of the 20 the table misses closed on or
after 2026-08-04; the table has not been maintained since 2026-07-26.

**Why the existing rules do not cover it.** Nothing in the file says there are two surfaces, so a
reader consulting either alone gets a confident wrong answer about a different 20 or 15 rows — and
the wrongness is invisible from inside whichever surface was consulted. `drift_check` has no check
over this file. The nearest analogous rule, *A document that quotes repo state is a snapshot with no
invalidation* (`aetheris/CLAUDE.md`), binds a reader who suspects staleness; here there is nothing to
prompt the suspicion, because both surfaces read as authoritative.

**Determine what the backlog's status convention is** — one surface or two, which is authoritative,
and whether the second is a view that must be regenerated or a duplicate that should be retired.
The `## Suggested order` table carries a second thing the row bodies do not: a sequencing opinion.
Whether that survives a de-duplication is part of the question and not assumed here.

**RULED 2026-08-12 by the arbiter, at the gc t3 review. The question this row posed is answered;
the execution is not done, and this row owns it.**

**The row bodies are authoritative. The `## Suggested order` ✔ table is retired.** The ruling is on
the ground the row states: the table has not been maintained since 2026-07-26 and misses every one
of the 20 rows that closed on or after 2026-08-04, while the bodies are written by the session that
changes a row's state and are therefore current by construction. Two surfaces where one is
maintained is not a redundancy, it is a trap.

**What the ruling does not decide**, and what this row must therefore still establish: the table
carries a **sequencing opinion** the bodies do not — an ordering of what to do next — and retiring
the table drops it unless it is reconstructed somewhere. Whether that opinion is worth preserving,
and where, is execution and belongs here.

**Done when:** the `## Suggested order` table is either **retired** or **reconstructed from the row
bodies** as a derived view that cannot drift; the file **states in its own text which surface
answers the question**, so a reader is not left to infer it; and, if the table is retired, its
sequencing opinion is either carried somewhere named or dropped with the reason recorded.

**Costs:** M. The ruling removes the decision cost; what remains is 28 ✔ rows to reconcile against
48 closures, and one judgement about the sequencing opinion.

`Source: gc t1's row census, 2026-08-11 — 143 rows, extraction and both controls published at
docs/milestones/gc-t1-implementation-notes.md §A and §H. The two figures and the two disagreement
sets above are derived, not counted by eye. Filed gc t3, 2026-08-12, per D4. Ruled by the arbiter
2026-08-12 at the gc t3 review; the ruling is recorded here rather than in the round document
because it is a fact about this file, and the round that surfaced it does not own it.`

**Still open, 2026-09-14 (closing sweep).** Unmet: the first and third clauses — the `## Suggested order` table is still in the file with its ✔ marks, neither retired nor derived, and its sequencing opinion has no disposition. The second clause is met by the marker under that heading and the file's header.

**Closed 2026-09-14.** The `## Suggested order` table is deleted and its sequencing opinion dropped, because nothing else needs it: the milestone doc is the execution authority (arbiter ruling R3, 2026-09-14).

---

### BL-252 — DONE 2026-09-14 · backlog index split — open rows reduced to field lists, bodies moved to docs/evidence/ (#TBD)
**Status:** DONE
**Kind:** documentation + code · **Size:** not stated · **Priority:** not stated
**Section:** aetheris-agents (`docs/backlog-2026-06.md`, `docs/evidence/`, `scripts/backlog_status.py`, `scripts/drift_check.py`)

Filed 2026-09-14 to execute the arbiter's rulings R1–R3 of that date: Markdown is the status authority, the open backlog becomes an index, and BL-145 closes.

**Truth-maker.** The open file is 716,946 bytes over 10,358 lines at `fd53474` (`wc -c -l docs/backlog-2026-06.md`). That the store cannot answer "what next" from it is the arbiter's observation of 2026-09-14, not measured here.

**Done when:** every open row is a field list ≤ 12 lines with a resolvable evidence link; all three readers pass on the new shape; `drift_check --strict` is at baseline.

**Closed 2026-09-14.** Done-when, each clause read on this commit's tree before it was committed:

1. *Every open row is a field list ≤ 12 lines with a resolvable evidence link* — `python3 scripts/backlog_status.py --check`: `shape: 153 row ids index-shaped, 99 legacy`, `OK: 252 of 252 row ids carry exactly one field, …`. The index-shape check enforces the line cap and the link; `tests/test_backlog_status.py::test_the_open_file_holds_index_rows_only` asserts no legacy row is left in the open file.
2. *All three readers pass on the new shape* — `backlog_status.py` as above; `drift_check.py`'s `backlog_resolution` PASS; the harness KNOWN_RED resolver, unchanged, accepts a row from each file and refuses a nonexistent id (`python3 -m pytest -q -m integration tests/test_known_red_resolver.py`: `1 passed, 1 deselected in 0.05s`).
3. *`drift_check --strict` at baseline* — `19 PASS  0 FAIL  4 WARN  11 INFO` post-commit at `7ff79b6`, this commit's parent; the four WARNs are the baseline files.

**Sizes.** `docs/backlog-2026-06.md`: 716,946 bytes at `fd53474` → 73,978 bytes here (`wc -c`). `docs/evidence/`: absent at `fd53474` → 153 files, 709,897 bytes here (`ls docs/evidence/*.md | wc -l`; `cat docs/evidence/*.md | wc -c`). This row's own evidence file is removed at its close; its body is the section above.

---

## The close — 2026-09-15

### BL-103 — The store may hold documents the manifest does not describe, and "remove all" is undefined against them
- state: done
- type: not stated
- area: aetheris-agents
- priority: medium · size: S
- evidence: docs/evidence/BL-103.md
- done-when: `claude/aetheris-agents--inbox-brief.md`'s writer is established rather than inferred, and whether it is expected to persist; the manifest states whether non-manifest documents may coexist and are out of scope; BL-002 Step 5's remove-all names its scope; and the post-upload verification's check 3 says what an older timestamp means *given* that policy, rather than leaving the reader the fork it leaves today.
- disposition: superseded

---

### BL-075 — `mix test` flakes on a fixed 300 ms inactivity window in `RunHelpersTimeoutTest`
- state: done
- type: not stated
- area: harness
- priority: low · size: XS–S
- evidence: docs/evidence/BL-075.md
- done-when: either the flake is reproduced with its name captured (run the suite in a loop with full output retained, e.g. `mix test --seed 0` plus repeated seeded runs) and folded into BL-054 or filed on its own, or three further full-output runs come back clean and this row is closed as unreproducible with that stated.
- disposition: superseded

---

### BL-150 — standing: documentation-system findings, append-only
- state: done
- type: standing
- area: process / documentation system
- priority: medium · size: n/a — does not close on any single item
- evidence: docs/evidence/BL-150.md
- done-when: the collection question is answered in one named document with its scope — or declined, with the reason recorded and this row's fate stated either way.
- disposition: evidence-only

---

### BL-151 — standing: code findings, append-only
- state: done
- type: standing
- area: code / cloudcost and any use case
- priority: medium · size: n/a — does not close on any single item
- evidence: docs/evidence/BL-151.md
- done-when: the sweep-and-retirement question is answered in one named document with its scope — or declined, with the reason recorded and this row's fate stated either way.
- disposition: evidence-only

---

### BL-064 — Fork with additional instructions
- state: done
- type: not stated
- area: TBD
- priority: TBD · size: TBD
- evidence: docs/evidence/BL-064.md
- done-when: not stated — see evidence
- disposition: rejected

---

### BL-253 — split the project-knowledge manifest: boundary records and inclusion rulings move to docs/export-boundaries/
- state: done
- type: method
- area: process / project knowledge
- priority: medium · size: M
- evidence: docs/evidence/BL-253.md
- done-when: the manifest holds header + table + `## Inclusion rulings` + `## Export boundary log` and nothing else; every moved block is byte-verbatim under docs/export-boundaries/ with a provenance header; and the whole-corpus splice at 1592c95 reproduces the original manifest byte-for-byte (the step-8 identity assertion).
- disposition: fixed

---

### BL-165 — `bl-002` Step 5 states the remove half as a hand enumeration of document kinds, not as the manifest set
- state: done
- type: defect
- area: process / project knowledge
- priority: medium · size: S
- evidence: docs/evidence/BL-165.md
- done-when: Step 5's remove half states the manifest set as its scope, by rule or by pointer with the choice recorded; the `claude/` namespace's exclusion from *remove-all* is legible to the operator at the point of the deletion; and the history question above is answered or recorded as unanswerable.
- disposition: fixed

---

### BL-196 — the export procedure says nothing about upload ROUTES: a route that namespaces a new bare filename put two manifest-tracked documents under `claude/`, where neither post-upload check could see them
- state: done
- type: decision — the gap is a procedural defect; which of its two repairs to take is not a session's to choose
- area: process / project knowledge
- priority: medium — owed before the next boundary that uploads by the second route, which is the only route claude-ui can drive · size: S
- evidence: docs/evidence/BL-196.md
- done-when: the procedure states which upload routes are permitted, or the discriminator in both checks no longer depends on the namespace.
- disposition: fixed

---

### BL-201 — kernel budget: a `drift_check` arm that warns when the `export`+`both` rows exceed the manifest's stated cap
- state: done
- type: mechanism
- area: aetheris-agents
- priority: low until the backlog split lands — the figure is dominated by one row the split removes, and an arm landed before it is red from its first run · size: S
- evidence: docs/evidence/BL-201.md
- done-when: a `kernel_budget` arm in `drift_check.py` sums `git show HEAD:<path> | wc -c` over `export_rows()` in each row's own repo, reads the cap from the manifest header's **Kernel budget** line, and WARNs — not strict-exempt — when the sum exceeds it, printing the sum, the cap and the largest rows; a red fixture test whose cap sits below its fixture's sum; and the header's `[not yet mechanised — BL-201]` marker removed in the same commit.
- disposition: fixed

---

### BL-195 — two email orchestrators with one label: `email_orchestrator.exs` is what Rig, the sprint and the spec wire; `email_orchestrator2.exs` is what the guide's pattern and the live run use; nothing says which is current
- state: done
- type: debt
- area: aetheris-agents
- priority: high — **blocking `docs/milestones/m-payslip-release.md`**, its §5 dependency 1 · size: S
- evidence: docs/evidence/BL-195.md
- done-when: exactly one email orchestrator file exists under `email/agents/`; it carries the eval-time `raise` for `PAYSLIP_MONTH` and the `timeout_ms` hints; every site in the table names it — `OrchestratorView.tsx`, `sprint.sh`, the orchestrator spec — and the capability matrix's Email section is **regenerated**, not hand-edited, per `CLAUDE.md` §Learning — m6-cloudcost (*a generated artefact with consumers is a wiring place in its own right*), so it lists one email agent.
- disposition: fixed

---

### BL-192 — `email_send.py` crashes on a malformed month instead of degrading: `strptime` is called for display, so its validation is incidental
- state: done
- type: defect
- area: aetheris-agents
- priority: low · size: S
- evidence: docs/evidence/BL-192.md
- done-when: `email_send.py` rejects a non-`YYYY-MM` month with a message and `sys.exit(1)` before doing any work, and a test pins the rejection.
- disposition: fixed

---

### BL-193 — the Rig step card's "step timed out after 5 minutes" is the orchestrator describing its own wait, rendered as a statement about the step; it is emitted by this repo, not by the harness
- state: done
- type: defect
- area: aetheris-agents
- priority: medium · size: S
- evidence: docs/evidence/BL-193.md
- done-when: on a `Task.yield` expiry the step card no longer asserts that the *step* timed out — the emitted `error` names the orchestrator's own wait as its subject and states the bound it actually applied; **and** the operator can reach the harness's `await_run` diagnosis, either by giving the orchestrator's cap headroom over the harness's inactivity bound so the accurate message wins, or by dropping the outer cap and letting `await_run` be the one clock; **and** the replacement message does not arrive quote-wrapped — whatever hop 2 becomes, it must not hand the card `inspect/1` of a string that was already prose.
- disposition: fixed

---

### BL-200 — scheduler safety audit against the moadim brief's Cluster 2: seven items, each answered has / lacks deliberately / lacks by omission
- state: done
- type: verification
- area: harness
- priority: medium — a scheduled run here can carry irreversible effects (payslip release, cleanup execution), which is the brief's reason the *missed-fire* item is a stated rule and not an accident · size: S
- evidence: docs/evidence/BL-200.md
- done-when: a seven-row table is on the record — in this row's DONE section or in a committed implementation-notes file it names — giving each item one of the three verdicts **with the `file:line` that establishes it**, and for every *lacks by omission* verdict either a filed row or the arbiter's recorded decision not to file one.
- disposition: evidence-only

---

### BL-194 — misplaced payslip objects in Drive period folders have no owner: `2026-07/` holds 36 May files and nothing is filed to remove them
- state: done
- type: defect
- area: aetheris-agents
- priority: medium · size: S
- evidence: docs/evidence/BL-194.md
- done-when: `2026-07/` passes the identity test — every object's filename month prefix equals its containing period folder's name — with the 36 misplaced May objects in a quarantine outside `payslips/`, and a committed-or-archived dry-run report naming every `source → quarantine` pair.
- disposition: fixed

---

### BL-110 — the payslip case asserts a reference employee the run cannot produce
- state: done
- type: not stated
- area: harness
- priority: medium · size: XS
- evidence: docs/evidence/BL-110.md
- done-when: the reference employee the assertion names is one the run can actually produce — either by keying the check to an id read out of the CSV the orchestrator was given, or by running the assertion leg against `sample_payroll.csv` explicitly rather than depending on whether `payroll.csv` exists.
- disposition: fixed

---

### BL-191 — `drive/runbook.md` documents two folder-ID env vars nothing has read since `72367ac`, and the sprint's drive arm gates on both
- state: done
- type: defect
- area: aetheris-agents and harness
- priority: medium · size: M
- evidence: docs/evidence/BL-191.md
- done-when: 1. `drive/runbook.md` names `DRIVE_ROOT_FOLDER_ID` throughout, including the troubleshooting entry currently keyed to a message the script cannot emit (`### DRIVE_OUTPUT_FOLDER_ID not set`), and the sibling docs are swept with it. 2. `sprint.sh`'s drive arm gates on the variable the scripts read, and its `email_download_template.py` invocation passes the one that script reads. 3. The Expected-output block matches what the script prints, verified by running it rather than by reading the source. 4. The sweep is enumerated **in the fixing ticket** at that ticket's commit — not in this row, whose counts will already be stale by then.
- disposition: fixed

---

### BL-257 — no global concurrency cap: nothing limits how many runs the harness admits at once
- state: done
- type: defect — found by audit, not demonstrated live
- area: harness
- priority: unset — the arbiter's · size: unset
- evidence: docs/evidence/BL-257.md
- done-when: run admission passes through one chokepoint (INV-2) that admits or refuses with a named reason; a global cap bounds concurrency; **the cap is a production admission cap, not an absolute process/resource ceiling**; the cap and live count rebuild from live runs at startup so a restart cannot exceed it; the refusal-reason set is extensible for later rows; the cap is a config key with a conservative default stated in the ticket; a test asserts the (N+1)th concurrent run is refused and the count rebuilds from live runs after restart.
- disposition: fixed

---

### BL-259 — no global lock: nothing halts all scheduled fires and triggers at once
- state: done
- type: defect — found by audit, not demonstrated live
- area: harness
- priority: unset — the arbiter's · size: unset
- evidence: docs/evidence/BL-259.md
- done-when: a single global pause sentinel (INV-1) halts every run start — due tick, manual trigger, and startup catch-up; the sentinel is store-backed and survives a harness restart; the due query and both start paths honor it; enable/disable is a CLI+API action; the sentinel is the single point later scheduler rows extend, exposed by a test fixture; a test asserts no path starts a run under pause, that unpause resumes, and that a pause set before a restart still holds after it.
- disposition: fixed

---

### BL-256 — scheduler overlap: a due schedule starts a new run while its previous run is still live
- state: done
- type: defect — found by audit, not demonstrated live
- area: harness
- priority: unset — the arbiter's · size: unset
- evidence: docs/evidence/BL-256.md
- done-when: overlap is a refusal reason `overlap-live` at INV-2's chokepoint, not a separate path; a due schedule whose previous run is live starts no new run, the skip is recorded as an event, and next_run_at advances; a test asserts a due tick against a live prior run is refused with `overlap-live`, and that a paused scheduler (INV-1) skips before the overlap check.
- disposition: fixed

---

### BL-258 — same-minute double fire: a manual trigger and a due tick both start runs for one schedule
- state: done
- type: defect — found by audit, not demonstrated live
- area: harness
- priority: unset — the arbiter's · size: unset
- evidence: docs/evidence/BL-258.md
- done-when: the same-minute dedup guard sits at INV-2's chokepoint, shared by the tick and trigger paths — one dedup point, not two; a test asserts a same-minute trigger+tick yields exactly one admitted run, and that both paths honor INV-1.
- disposition: fixed

---

### BL-260 — missed fires catch up silently: a schedule due while the harness was down runs on startup, with no alert
- state: done
- type: defect — found by audit, not demonstrated live
- area: harness
- priority: unset — the arbiter's · size: unset
- evidence: docs/evidence/BL-260.md
- done-when: missed fires do not auto-run — a fire whose time passed while the harness was down starts no run; the scheduler emits an alert event naming the schedule and the missed count so it is never silent, then advances next_run_at; the alert fires regardless of pause (INV-1 gates run-starts, of which there are none here). Adopts the moadim brief's alert-only rule (:76-80) over catch-up, on the ground that a scheduled run can carry irreversible effects (payslip release). A test asserts N missed intervals → zero runs + one alert carrying N, and that the schedule advances.
- disposition: fixed

---

### BL-261 — retention family: no solo-run max-runtime stop, and no reaping or eviction of run artifacts
- state: done
- type: defect — found by audit, not demonstrated live
- area: harness — retention (the moadim brief's E6 candidate)
- priority: unset — the arbiter's · size: unset
- evidence: docs/evidence/BL-261.md
- done-when: (a) a run exceeding RunConfig.max_duration is stopped by a lib watchdog (not only orbs) with a terminal event that decrements INV-2's live count; (b) run artifacts carry a stated retention with two arms — TTL reaping that never touches a live run, and oldest-first, finished-only eviction under a disk ceiling — each implemented or ruled out on the record, plus an on-demand reap command; a test covers each arm, including that a watchdog-stopped run frees admission. May split 261a/261b at implementation.
- disposition: fixed

---

### BL-262 — cap composition: per-schedule runtime and TTL values must be tighten-only
- state: done
- type: defect — found by audit, not demonstrated live
- area: harness
- priority: unset — the arbiter's · size: unset
- blocked-by / trigger: BL-257, BL-261
- evidence: docs/evidence/BL-262.md
- done-when: per-schedule runtime/TTL values are clamped against INV-2's cap and BL-261's max_duration/TTL by name; from_map refuses or clamps a value looser than either named cap; a test asserts a looser value is clamped/refused and a tighter one honored; lands after BL-257 and BL-261.
- disposition: fixed

---

### BL-267 — worker `:DOWN` does not persist `failed`: the run row can read `running` indefinitely
- state: done
- type: defect
- area: harness — Agent.Server
- priority: unset — the arbiter's · size: S _(proposed)_
- evidence: docs/evidence/BL-267.md
- done-when: a worker :DOWN whose run is not already terminal durably writes runs.status = failed through Store.upsert_run; a run already terminal is not overwritten; a test kills the worker client and asserts the persisted status in both cases.
- disposition: fixed

---

### BL-266 — no streaming transport for run/trajectory updates: a UI must poll
- state: done
- type: missing capability
- area: harness — API (Rig/UI consumer)
- priority: medium _(proposed)_ · size: L _(proposed; docs-first per repo convention)_
- evidence: docs/evidence/BL-266.md
- done-when: a UI can follow a run without polling over BOTH an SSE stream and a WebSocket, each auth-gated by the existing token model, built on a transport-neutral core (tranches T0 core, T1 SSE, T2 WebSocket, T3 Rig consumer); wakeups originate inside Store after commit, never a server-side poll-and-forward; no cursor replays from the start and a cursor resumes after it; events arrive in seq order; each frame carries the full event body (the EventRow projection: id, run_id, step, seq, event_type, payload, timestamp) rather than the trajectory summary; once runs.status is terminal the stream delivers every event with seq ≤ runs.terminal_seq, sends a stream_end control frame and closes; non-terminal runs stream only from the hosting VM; a slow or disconnected client neither wedges the run nor leaks; harness playground-api.md documents the endpoints (T1/T2) and Rig's specs.md documents its consumer with drift green (T3); tests assert subscribe → append N → receive N in seq order → terminal closes, and that an unauthenticated subscribe is refused. Design: docs/aetheris/backlog/bl-266-run-event-streaming.md. T1 is blocked by BL-267.
- disposition: fixed

---

### BL-276 — harness runbook entry for run event streaming (BL-266 runbook-update rule)
- state: done
- type: docs
- area: harness — runbook
- priority: unset — the arbiter's · size: S _(proposed)_
- evidence: docs/evidence/BL-276.md
- done-when: the harness runbook documents the streaming endpoints' operational surface — the four config keys, the working token recipe with the BL-275 trap named, reverse-proxy requirements, and the capacity refusal — and the runbook introduces the `/api/playground/*` namespace, its bearer auth and `api_bind` default, so the streaming section does not reference surfaces the file never establishes.
- disposition: fixed

---

### BL-280 — the amend rule's trigger is push state, not citation
- state: done
- type: docs
- area: aetheris-agents — `CLAUDE.md` §Definition of done
- priority: unset — the arbiter's · size: XS _(proposed)_
- evidence: docs/evidence/BL-280.md
- done-when: `CLAUDE.md` §Definition of done states the amend rule on all three limbs — amend while unpushed and append once pushed; amend a commit a packet has been issued against only on the arbiter's instruction; and an amend superseding a SHA an issued packet named states that SHA in its message and says what cited it — with push state named as protecting resolvability and the packet as protecting review integrity, and the superseded wording quoted once in a dated block.
- disposition: fixed

---

### BL-255 — the kernel-ceiling decrease-only rule sets zero headroom, so the next backlog filing fails --strict
- state: done
- type: defect
- area: process / project knowledge
- priority: low · size: XS
- evidence: docs/evidence/BL-255.md
- done-when: the manifest header's Kernel ceiling rule states how much headroom a downward ratchet leaves — a fixed slack or a round-up — so that lowering the ceiling cannot make an ordinary backlog filing fail kernel_budget under --strict; and the rule names what re-tightens the slack as the kernel shrinks toward the target.
- disposition: fixed

---

### BL-278 — the kernel ceiling's headroom is consumed mainly by backlog filings, not manifest bookkeeping, and the ceiling is DECREASE-ONLY
- state: done
- type: gate
- area: aetheris-agents — project-knowledge kernel budget (`drift_check.py` `kernel_budget`, BL-002 boundary)
- priority: unset — the arbiter's · size: S _(proposed)_
- evidence: docs/evidence/BL-278.md
- done-when: _(proposed)_ a boundary can be run without the manifest's own growth being what consumes the remaining headroom — by bounding or relocating the growing sections, or by a recorded ruling that resets the ceiling on a stated basis; carried by a measured figure at a boundary or by a recorded disposition.
- disposition: fixed

---

### BL-279 — `mix hex.audit` is red on `mint` 1.10.0, EEF-CVE-2026-82672 (MEDIUM)
- state: done
- type: defect (supply chain)
- area: harness — `../aetheris/mix.exs` + `mix.lock`
- priority: unset — the arbiter's · size: XS _(proposed)_
- evidence: docs/evidence/BL-279.md
- done-when: _(proposed)_ `mix hex.audit` exits 0 from the harness root, or the residual advisory carries a recorded rationale and the gate runs expected-red named with this ref; carried by a version bump or a recorded disposition.
- disposition: fixed

---

### BL-281 — two documents still state the amend rule's superseded citation trigger; both edits are transcription, nothing is left to decide
- state: done
- type: docs
- area: harness — `docs/methodology/milestone-methodology.md` `[R44]`; aetheris-agents — `docs/milestones/hc-consolidation.md` R22 note
- priority: unset — the arbiter's · size: XS _(proposed)_
- evidence: docs/evidence/BL-281.md
- done-when: _(proposed)_ `[R44]:134` states its "unamended" as following from BL-280's review-integrity limb — *once a packet has been issued against a commit, amend it only on the arbiter's instruction* — rather than from the superseded amend-while-uncited wording, R44's conclusion unchanged; and the `hc-consolidation.md` R22 note carries a dated supersession block quoting the superseded sentence in the position it occupied. Both are restatements against a rule already settled at BL-280; carried by the two edits.
- disposition: fixed

---

### BL-114 — the recent-activity modifier has never fired against any real inventory, on any provider
- state: done
- type: defect
- area: cloudcost
- priority: low · size: XS–S
- evidence: docs/evidence/BL-114.md
- done-when: not stated — see evidence
- disposition: accepted-risk

---

### BL-125 — C3: name the timestamp field set once instead of hardcoding the pair
- state: done
- type: contract consequence
- area: cloudcost
- priority: low · size: XS
- evidence: docs/evidence/BL-125.md
- done-when: not stated — see evidence
- disposition: superseded

---

### BL-134 — verify the seven comment-anchored census claims, and hand-classify the eight the sweep could not reach
- state: done
- type: verification
- area: cloudcost
- priority: low–medium · size: S
- evidence: docs/evidence/BL-134.md
- done-when: not stated — see evidence
- disposition: accepted-risk

---

### BL-136 — decision H's consequent: a read-only cross-provider cost summary over the persisted per-provider snapshots
- state: done
- type: feature
- area: cloudcost
- priority: medium · size: S–M
- blocked-by / trigger: a milestone claims it
- evidence: docs/evidence/BL-136.md
- done-when: not stated — see evidence
- disposition: superseded

---

### BL-072 — Cost Optimization Hub / Compute Optimizer optimization milestone
- state: done
- type: not stated
- area: Milestones
- priority: low · size: L
- blocked-by / trigger: a milestone claims it
- evidence: docs/evidence/BL-072.md
- done-when: milestone docs exist (docs-first, per repo convention); t4's real-bill read seeds the scope (which signals are worth surfacing, what noise looks like); read-only, gated behind its own IAM.
- disposition: superseded

---

### BL-207 — `run_command` is not confined to the sandbox root; `read_file` and `write_file` are
- state: done
- type: hardening
- area: harness
- priority: high — a permitted basename with an out-of-root argument executes today, and the containment the two file tools enforce is absent from the tool that spawns processes · size: TBD — the row states the severity; scoping belongs to the round that takes it
- evidence: docs/evidence/BL-207.md
- done-when: a decision is recorded on this row: (a) `pivot_root` in the worker's mount namespace plus a shared confinement crate, or (b) `run_command` declared uncontained as a standing position in the determinism contract.
- disposition: superseded

---

### BL-284 — an HTTP client cannot start a run from an existing .exs and supply only the user turn
- state: done
- type: missing capability
- area: harness — API
- priority: medium _(proposed)_ · size: M _(proposed; docs-first per repo convention)_
- evidence: docs/evidence/BL-284.md
- done-when: POSTing agent_path + user_prompt gets 202 with run_id; prompt_built carries the supplied user_prompt and the file's tool list, no system_prompt in the request; path confined to the agents root. Design: docs/aetheris/backlog/bl-284
- disposition: fixed

---

### BL-285 — the runbook's HTTP API section never names AETHERIS_AGENTS_ROOT, the root BL-284's route resolves agent_path against
- state: done
- type: documentation
- area: harness — runbook.md
- priority: unset — the arbiter's · size: XS _(proposed)_
- evidence: docs/evidence/BL-285.md
- done-when: the existing HTTP API section names AETHERIS_AGENTS_ROOT, the default, and that ct-bot/agents/main.exs is relative to it.
- disposition: fixed

---

### BL-286 — a CORS preflight to the playground API is answered by the auth plug with 401, so no browser origin can call BL-284's route
- state: done
- type: missing capability
- area: harness — API
- priority: unset — the arbiter's · size: S _(proposed)_
- evidence: docs/evidence/BL-286.md
- done-when: OPTIONS from that origin returns 204 before auth, and a POST with no bearer still returns 401.
- disposition: fixed
