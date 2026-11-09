# uc-ct-rpg — CampusTrack Migration Gate Agents

The **migration path**: RunConfig agents that execute the extracted
RavenDB → Postgres migration runbook as a gated, stop-on-first-failure
agent chain — gate 0 preflight → gate 2 migrate → gate 3 verify (parity)
→ gate 4 api — against the migration repo's Docker containers.

This is **not the panel track** (`ct-bot/`, chat) and **not the TAP
write path** (`api/`). The ct-rpg agents own no migration code: the
scripts they gate on (`verify-prerequisites.sh`, `migrate_all.py`,
`verify_raven_to_postgres.py`, `wait-for-api.sh`) live in the migration
repo and run there. The migration repo root is a **parameter** on every
turn's user prompt, never a hard-coded path.

---

## Source of truth

The extracted specs in `docs/specs/` are the source of truth; the agent
system prompts copy them and restate nothing:

| Spec | Gates it carries |
|------|------------------|
| `docs/specs/runbook-gates.md` | the whole gate contract (0–5), incl. the agent execution rules |
| `docs/specs/etl-orchestrator.md` | gate 2 — the 30-module ETL orchestrator |
| `docs/specs/etl-module-students.md` | gate 2 — the sampled `students` module |
| `docs/specs/parity-verifier.md` | gate 3 — Raven/Postgres parity audit |
| `docs/specs/api-verification.md` | gate 4 — the REST read/write curls |

Golden fixtures live under `docs/specs/golden/`; none is yet validated
against a live legacy environment (each spec's own status line says so).

---

## Status at T1

**The parent and the first child are landed.** `agents/rpg-main.exs`
(spawns the gate chain) and `agents/rpg-preflight.exs` (gate 0) exist as
RunConfig wraps. Gates 2–4 wraps are T3–T5 (see `milestone.md`).
**Nothing here is runnable against a live migration repo without its
prerequisites** — see `runbook.md`.

---

## How the chain works

| Child | Gate | Tools | Wrap |
|-------|------|-------|------|
| preflight | 0 | `run_command` | `agents/rpg-preflight.exs` (T1) |
| migrate | 2 | — | T3 |
| verify | 3 | — | T4 |
| api | 4 | — | T5 |

`rpg-main` spawns one child at a time, waits, reads the child's
`final_message`, and stops on the first failed gate — reporting which
gate failed and that the rest did not run.

---

## Folder structure

```
ct-rpg/
├── agents/            # rpg-main.exs (T1), rpg-preflight.exs (T1); T3–T5 fill the rest
├── scripts/           # empty by design — the gate scripts live in the migration repo
├── tests/
│   ├── conftest.py    # puts scripts/ on sys.path
│   └── test_docs.py   # docs-existence checks
├── docs/
│   ├── specs/         # the extracted specs (operator-supplied, cited, never restated)
│   └── milestones/    # per-ticket implementation notes
├── output/            # gitignored
├── milestone.md
├── README.md
├── runbook.md
└── tools.json         # empty manifest; entries land only if a local helper is ever needed
```
