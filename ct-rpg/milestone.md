# ct-rpg — migration gate agents

**Status:** T0 + T1 complete (registration; parent `rpg-main.exs` and the
first child `rpg-preflight.exs`); T2–T5 open
**Repos:** `aetheris-agents` only for T0–T5. The harness (`../aetheris`)
and the migration repo (the system under migration) are out of this
milestone — this repo gates, never migrates.
**Goal:** The extracted migration runbook (`docs/specs/runbook-gates.md`)
executed as a gated, stop-on-first-failure agent chain: a parent that
spawns gate children one at a time and halts on the first failed gate.

---

## Why ct-rpg

The migration runbook is a strictly ordered gate sequence over a system
this repo does not own: the migration repo's Docker containers run the
gate scripts, and the agents only drive them. One parent agent
(`rpg-main`) carries the gate contract as its system prompt — copied from
the spec, never restated — and spawns one child per gate, in order:
preflight (0) → migrate (2) → verify (3) → api (4). The channel between
parent and child is the child's `final_message`; a failed gate stops the
chain and is reported by name. The migration repo root is a parameter on
every turn's user prompt, never a hard-coded path.

ct-rpg shares the CampusTrack domain with `ct-bot` (panel) and `api/`
(TAP write path) but owns none of their machinery and makes no ct-api
call. Three tracks, three registry rows.

---

## What this enables

Once T2–T5 land:

```bash
# From the aetheris repo
mix aetheris run ../aetheris-agents/ct-rpg/agents/rpg-main.exs
```

Main spawns preflight → migrate → verify → api, one at a time, and
reports either the full gate sequence passed or the first failed gate by
name. Until then the parent runs, spawns preflight, and stops — reporting
which gate is next and that its child does not exist yet.

---

## Exit criterion

| Criterion | Status |
|-----------|--------|
| `ct-rpg/agents/rpg-main.exs` exists; its system prompt is the body of `docs/specs/runbook-gates.md`, copied; wire section added, nothing restated | ✅ T1 |
| rpg-main spawns one child at a time — preflight, then migrate, then verify, then api — waits for each, reads `final_message`, stops on the first failed gate and names it | ✅ T1 (behaviour authored; live chain run owed where the harness runs) |
| `ct-rpg/agents/rpg-preflight.exs` exists; system prompt is the gate-0 section of `runbook-gates.md`, copied; runs `scripts/verify-prerequisites.sh` from the migration repo root passed in the user prompt; reports exit code and last stdout line; does not migrate, verify, or call the API | ✅ T1 (wrap) / — T2 (live verification below) |
| preflight verified against a real configured migration repo root (exit 0 path and a fail path) | — T2 |
| migrate child exists per `docs/specs/etl-orchestrator.md` (+ `etl-module-students.md`) | — T3 |
| verify child exists per `docs/specs/parity-verifier.md` | — T4 |
| api child exists per `docs/specs/api-verification.md` | — T5 |
| `python3 -m pytest ct-rpg/tests/ -v` passes at every ticket boundary | ✅ T0+ |
| `drift_check --check use_case_registry` stays green from T1 (ct-rpg is agent-bearing: SECTIONS entry + section agent required and landed) | ✅ T1 |

---

## Delivery sequence

| # | Ticket | Repo | What |
|---|--------|------|------|
| 0 | T0 | aetheris-agents | Docs skeleton, registry row, tools manifest (this change) |
| 1 | T1 | aetheris-agents | rpg-main (parent + wire) and rpg-preflight (gate-0 child) RunConfigs; capability-matrix registration; classifier prefix |
| 2 | T2 | aetheris-agents | rpg-preflight verified live: exit-0 pass and a fail path against a real configured migration repo root |
| 3 | T3 | aetheris-agents | rpg-migrate (gate 2) RunConfig |
| 4 | T4 | aetheris-agents | rpg-verify (gate 3) RunConfig |
| 5 | T5 | aetheris-agents | rpg-api (gate 4) RunConfig |

**Why the preflight wrap lands at T1, not T2:** a parent whose chain has
no spawnable first child cannot be evaluated as a parent — T1 lands the
pair so the spawn/wait/read/stop behaviour exists and is exercisable. T2
is the preflight child's own verification scope (a live pass and a live
fail against a configured migration repo root), not the authoring of the
wrap.

---

## Tickets

---

### T0 — docs and registration ✅

**Repo:** aetheris-agents

**What was built:**

- `ct-rpg/` skeleton: README, milestone, runbook, `tools.json` (empty
  scripts list), `output/.gitkeep`, `scripts/README.md`,
  `tests/conftest.py`, `tests/test_docs.py`,
  `docs/milestones/m-ct-rpg-t0-implementation-notes.md`.
- `docs/use-cases.md`: one row, status `active` — flipped in the same
  change that lands the first `.exs` (T1, below), not deferred.
- Root `README.md` and `CLAUDE.md` table rows;
  `tests/test_tools_manifests.py` SWEPT list;
  `tests/test_run_record_adoption.py` NON_PRODUCERS entry.
- No gate child other than preflight; no live run.

**Done when (all green):**

```bash
python3 -m pytest ct-rpg/tests/ -v
python3 -m pytest tests/test_use_case_registry.py -q
python3 scripts/drift_check.py --check use_case_registry
```

---

### T1 — rpg-main + the first child ✅

**Repo:** aetheris-agents

**What was built:**

- `ct-rpg/agents/rpg-main.exs` — RunConfig; tools
  `["spawn_agent", "wait_for_all"]`; system prompt = the body of
  `ct-rpg/docs/specs/runbook-gates.md`, copied verbatim, plus a clearly
  marked WIRE section (this file's own words only): spawn one child at a
  time in order, wait, read `final_message`, stop on the first failed
  gate and name it.
- `ct-rpg/agents/rpg-preflight.exs` — RunConfig; tools
  `["run_command"]`; system prompt = the gate-0 section of
  `runbook-gates.md`, copied verbatim, plus the invocation contract (path
  as user-prompt parameter; report exit code + last stdout line; gate 0
  only).
- Capability-matrix registration: `agents/capability_matrix_ct-rpg.exs`
  and the `SECTIONS` entry in `scripts/assemble_matrix.py` — required at
  exactly this ticket, because the moment `ct-rpg/agents/` holds an
  `.exs`, ct-rpg is agent-bearing and drift_check's `use_case_registry`
  arms 3–4 require both.
- The `ct-rpg → CT-RPG` prefix in **both** `USE_CASE_PREFIXES` constants
  (`rig/src/components/modules/harness/RunList.tsx`,
  `rig/src-tauri/src/commands/usage.rs`), so the new declared labels
  classify in Rig's run list and usage view.

**Done when (all green):**

```bash
cd ../aetheris
mix run --eval 'Code.eval_file("../aetheris-agents/ct-rpg/agents/rpg-main.exs")'
mix run --eval 'Code.eval_file("../aetheris-agents/ct-rpg/agents/rpg-preflight.exs")'
cd ../aetheris-agents
python3 -m pytest ct-rpg/tests/ -v
python3 scripts/drift_check.py --check use_case_registry
python3 scripts/check_run_classifier.py
```

(The `mix run --eval` line is owed where the harness checkout has
`deps/`; the stub-against-RunConfig evaluation record lives in
`docs/milestones/m-ct-rpg-t0-implementation-notes.md`.)

---

### T2 — rpg-preflight verified live

**Repo:** aetheris-agents

**What will be built:**

- Nothing new in this repo: the wrap landed at T1. T2 is the child's
  verification — one run against a real configured migration repo root
  that passes (exit 0, `[PREFLIGHT PASS]` marker as the last stdout line)
  and one that fails (non-zero exit, `[FAIL]`/`[PREFLIGHT FAIL]` line),
  each reported as exit code + last stdout line, per
  `docs/specs/runbook-gates.md` §1's gate-0 statements.
- Any fix the live run forces goes into the wrap or the notes, with the
  spec still untouched.

**Done when:**

```bash
cd ../aetheris
mix aetheris run ../aetheris-agents/ct-rpg/agents/rpg-preflight.exs
cd ../aetheris-agents
python3 -m pytest ct-rpg/tests/ -v
```

---

### T3 — rpg-migrate (gate 2)

**Repo:** aetheris-agents

**What will be built:**

- `ct-rpg/agents/rpg-migrate.exs` — RunConfig whose system prompt is the
  gate-2 material of `docs/specs/runbook-gates.md` plus, where gate 2's
  own mechanism needs it, `docs/specs/etl-orchestrator.md` and
  `docs/specs/etl-module-students.md` — copied, not rewritten. It runs
  the migrator container command and reports the exit criterion, nothing
  else.

**Done when:** the wrap evaluates; `python3 -m pytest ct-rpg/tests/ -v`.

---

### T4 — rpg-verify (gate 3)

**Repo:** aetheris-agents

**What will be built:**

- `ct-rpg/agents/rpg-verify.exs` — RunConfig whose system prompt is the
  gate-3 material of `docs/specs/runbook-gates.md` plus
  `docs/specs/parity-verifier.md` — copied, not rewritten. Runs the
  parity verifier container command; reports `overall_status`, the
  missing/extra/mismatch counts, and the report artifact path.

**Done when:** the wrap evaluates; `python3 -m pytest ct-rpg/tests/ -v`.

---

### T5 — rpg-api (gate 4)

**Repo:** aetheris-agents

**What will be built:**

- `ct-rpg/agents/rpg-api.exs` — RunConfig whose system prompt is the
  gate-4 material of `docs/specs/runbook-gates.md` plus
  `docs/specs/api-verification.md` — copied, not rewritten. Exercises the
  two reads and the one write; reports status codes and response shapes.
  The spec's open items (hard-coded demo UUIDs, hard-coded port 5000)
  are the spec's, carried verbatim, not resolved here.

**Done when:** the wrap evaluates; `python3 -m pytest ct-rpg/tests/ -v`;
and a full-chain T1 parent run once T3–T5 exist.

---

## Repository structure

### aetheris-agents repo

```
ct-rpg/
├── agents/           # rpg-main.exs, rpg-preflight.exs (T1); rpg-migrate/verify/api (T3–T5)
├── scripts/          # empty by design — the gate scripts live in the migration repo
├── tests/            # conftest.py + test_docs.py
├── docs/specs/       # the extracted specs — the source of truth, cited, never restated
├── docs/milestones/  # per-ticket implementation notes
├── output/           # gitignored
├── milestone.md
├── README.md
├── runbook.md
└── tools.json        # empty manifest
```

### Other repos

- The harness (`../aetheris`): where the wraps are run. No commit in this
  milestone.
- The migration repo: the system under migration. Its gate scripts and
  containers are its own; this repo reads the extracted specs, not the
  migration repo's tree.

---

## Milestone reference row

```
| uc-ct-rpg | migration-gates | T0+T1 | Elixir | Use Case |
skeleton, registry row (active from T1), tools manifest, parent
rpg-main + gate-0 child rpg-preflight as RunConfigs | The extracted
migration runbook driven as a gated agent chain; children copy their
gate sections from docs/specs/ verbatim; stop-on-first-failure is the
spec's own rule, applied to the spawn order |
```
