# ct-bot — panel agents

**Status:** T0 complete (docs + registration); T1–T7 open
**Repos:** `aetheris-agents` only for T0–T7. The harness (`../aetheris`, incl. its
`sprint.sh` case) and the Angular panel host are out of this milestone.
**Goal:** The CampusTrack panel agents — main, sanitize, parse, validate,
compose, suggestions — as RunConfig agent files converted from
operator-supplied prompt sources. Chat path, not the TAP write path.

---

## Why ct-bot

The TAP track (`api/`) is the write path: CSV → intent packet → gateway →
ct-api. The panel path is different work — a conversational surface where a
user request arrives as one context bag and the answer is one assistant
reply, shaped by six narrow single-purpose agents rather than one monolithic
prompt. Splitting the panel into sanitize/parse/validate/compose/suggestions
hops keeps each hop testable and each system prompt small enough to copy
verbatim from its source file, which is the whole conversion contract:
the operator's prompt sources are the source of truth, and T1–T6 restate
nothing.

ct-bot shares the CampusTrack domain with `api/` but owns none of its
machinery: no ct-api calls, no TAP packets, no blackboard protocol between
tenants. The two tracks stay separate use cases and separate registry rows.

---

## What this enables

Once T1–T7 land:

```bash
# From the aetheris repo
mix aetheris run ../aetheris-agents/ct-bot/agents/main.exs
```

Main receives the context bag, spawns sanitize → parse → validate in
sequence, and returns one JSON reply. Compose (JSON notices) and
suggestions (JSON chips) remain separately invokable hops. Until then this
directory is a registered, dormant use case: docs, empty manifests, and
existence tests only.

---

## Exit criterion

| Criterion | Status |
|-----------|--------|
| `ct-bot/agents/main.exs` exists; its system prompt is `docs/agents/main.md`, copied | — T1 |
| main replies with JSON and requires no tools; it does not call ct-api | — T1 |
| sanitize replies with plain text | — T2 |
| parse replies with JSON records | — T3 |
| validate replies with JSON validity and does not save | — T4 |
| compose replies with JSON notices | — T5 |
| suggestions replies with JSON chips | — T6 |
| main spawns sanitize, then parse, then validate via `spawn_agent` and wait; no OrbConfig, no pre-minted peer ids | — T7 |
| `python3 -m pytest ct-bot/tests/ -v` passes at every ticket boundary | — T0+ |
| Panel transport (Angular host, port 4001) | **Not this milestone** — named here so nobody looks for it in T7. |

The harness sprint case is a later `../aetheris` commit, not part of any
ticket in this table.

---

## Delivery sequence

| # | Ticket | Repo | What |
|---|--------|------|------|
| 0 | T0 | aetheris-agents | Docs skeleton, registry row, tools manifest (this change) |
| 1 | T1 | aetheris-agents | main RunConfig + capability-matrix registration |
| 2 | T2 | aetheris-agents | sanitize RunConfig |
| 3 | T3 | aetheris-agents | parse RunConfig |
| 4 | T4 | aetheris-agents | validate RunConfig |
| 5 | T5 | aetheris-agents | compose RunConfig |
| 6 | T6 | aetheris-agents | suggestions RunConfig |
| 7 | T7 | aetheris-agents | wire: main spawns the three hops |

---

## Repos

| Ticket | Repo | Notes |
|--------|------|-------|
| T0–T7 | `aetheris-agents` | No harness commit, no Angular host commit in this milestone |
| after T7 | `../aetheris` | Sprint case (later harness commit, not this milestone) |
| after T7 | Angular host | Panel transport, port 4001 — not this milestone |

---

## Tickets

---

### T0 — docs and registration

**Repo:** aetheris-agents

**What will be built:**

- `ct-bot/` skeleton: README, milestone, runbook, `tools.json` (empty
  scripts list), `.gitignore`, `output/.gitkeep`, `agents/README.md`,
  `scripts/README.md`, `tests/conftest.py`, `tests/test_docs.py`,
  `docs/agents/README.md` (the six source filenames, nothing else).
- `docs/use-cases.md`: one row, status `dormant`, condition for return T1.
- Root `README.md` and `CLAUDE.md` table rows; `pytest.ini` dormant
  long-form; `tests/test_tools_manifests.py` SWEPT list.
- No `.exs` agent anywhere in `ct-bot/`.

**Done when:**

```bash
python3 -m pytest tests/test_use_case_registry.py -q
python3 -m pytest ct-bot/tests/ -v
python3 scripts/drift_check.py --check use_case_registry
git ls-files 'ct-bot/**' | grep -c '\.exs$'   # → 0
```

---

### T1 — main

**Repo:** aetheris-agents

**What will be built:**

- `ct-bot/agents/main.exs` — RunConfig whose system prompt is
  `ct-bot/docs/agents/main.md`, **copied, not rewritten**. JSON reply.
  No tools required. Does not call ct-api.
- The capability-matrix registration deferred from T0 (arbiter's call,
  2026-10-06 — see `docs/milestones/m-ct-bot-t0-implementation-notes.md`):
  `agents/capability_matrix_ct_bot.exs` and the `SECTIONS` entry in
  `scripts/assemble_matrix.py`. Required at exactly this ticket, because
  the moment `ct-bot/agents/` holds an `.exs`, ct-bot becomes
  agent-bearing and drift_check's `use_case_registry` arms require both.

**Done when:**

```bash
cd ~/sandbox/elixirws/aetheris
mix run --eval 'Code.eval_file("../aetheris-agents/ct-bot/agents/main.exs")'
cd ~/sandbox/elixirws/aetheris-agents
python3 -m pytest ct-bot/tests/ -v
python3 scripts/drift_check.py --check use_case_registry
```

---

### T2 — sanitize

**Repo:** aetheris-agents

**What will be built:**

- `ct-bot/agents/sanitize.exs` — RunConfig whose system prompt is
  `ct-bot/docs/agents/sanitize.md`, copied, not rewritten. Plain text
  output.

**Done when:**

```bash
cd ~/sandbox/elixirws/aetheris
mix run --eval 'Code.eval_file("../aetheris-agents/ct-bot/agents/sanitize.exs")'
cd ~/sandbox/elixirws/aetheris-agents
python3 -m pytest ct-bot/tests/ -v
```

---

### T3 — parse

**Repo:** aetheris-agents

**What will be built:**

- `ct-bot/agents/parse.exs` — RunConfig whose system prompt is
  `ct-bot/docs/agents/parse.md`, copied, not rewritten. JSON records
  output.

**Done when:**

```bash
cd ~/sandbox/elixirws/aetheris
mix run --eval 'Code.eval_file("../aetheris-agents/ct-bot/agents/parse.exs")'
cd ~/sandbox/elixirws/aetheris-agents
python3 -m pytest ct-bot/tests/ -v
```

---

### T4 — validate

**Repo:** aetheris-agents

**What will be built:**

- `ct-bot/agents/validate.exs` — RunConfig whose system prompt is
  `ct-bot/docs/agents/validate.md`, copied, not rewritten. JSON validity
  output. Does not save.

**Done when:**

```bash
cd ~/sandbox/elixirws/aetheris
mix run --eval 'Code.eval_file("../aetheris-agents/ct-bot/agents/validate.exs")'
cd ~/sandbox/elixirws/aetheris-agents
python3 -m pytest ct-bot/tests/ -v
```

---

### T5 — compose

**Repo:** aetheris-agents

**What will be built:**

- `ct-bot/agents/compose.exs` — RunConfig whose system prompt is
  `ct-bot/docs/agents/compose.md`, copied, not rewritten. JSON notices
  output.

**Done when:**

```bash
cd ~/sandbox/elixirws/aetheris
mix run --eval 'Code.eval_file("../aetheris-agents/ct-bot/agents/compose.exs")'
cd ~/sandbox/elixirws/aetheris-agents
python3 -m pytest ct-bot/tests/ -v
```

---

### T6 — suggestions

**Repo:** aetheris-agents

**What will be built:**

- `ct-bot/agents/suggestions.exs` — RunConfig whose system prompt is
  `ct-bot/docs/agents/suggestions.md`, copied, not rewritten. JSON chips
  output.

**Done when:**

```bash
cd ~/sandbox/elixirws/aetheris
mix run --eval 'Code.eval_file("../aetheris-agents/ct-bot/agents/suggestions.exs")'
cd ~/sandbox/elixirws/aetheris-agents
python3 -m pytest ct-bot/tests/ -v
```

---

### T7 — wire

**Repo:** aetheris-agents

**What will be built:**

- `ct-bot/agents/main.exs` gains `spawn_agent` and `wait_for_all`: it
  spawns sanitize, then parse, then validate, in that order. No OrbConfig,
  no pre-minted peer ids. Compose and suggestions stay separate hops.
- Whether the hop-to-hop payload rides `task_prompt` or the blackboard is
  **decided at T7 from the payload size**, not here: blackboard only if
  `spawn_agent` cannot pass the payload.

**Done when:**

```bash
cd ~/sandbox/elixirws/aetheris
mix aetheris run ../aetheris-agents/ct-bot/agents/main.exs
mix aetheris tree show <run_id>   # shows main → sanitize → parse → validate
cd ~/sandbox/elixirws/aetheris-agents
python3 -m pytest ct-bot/tests/ -v
```

---

## Repository structure

### aetheris-agents repo

```
ct-bot/
├── agents/           # main.exs, sanitize.exs, parse.exs, validate.exs, compose.exs, suggestions.exs (T1–T6)
├── scripts/          # deterministic helpers (T2–T4)
├── tests/            # conftest.py + test_docs.py at T0; per-hop tests after
├── docs/agents/      # the six prompt-source files (operator-supplied) + README index
├── docs/milestones/  # per-ticket implementation notes
├── output/           # gitignored
├── milestone.md
├── README.md
├── runbook.md
└── tools.json
```

### Other repos

None in this milestone. The harness sprint case and the Angular panel
host (port 4001) are later, separate commits.

---

## Milestone reference row

```
| uc-ct-bot | panel-agents | T0 | Python + Elixir | Use Case |
docs skeleton, registry row (dormant), tools manifest | CampusTrack
panel agents on the chat path; source prompts converted verbatim in
T1–T6; wire at T7 |
```
