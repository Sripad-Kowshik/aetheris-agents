# uc-ct-bot — CampusTrack Panel Agents

The CampusTrack **chat path**: a main panel agent assisted by five
single-purpose hops — sanitize, parse, validate, compose, suggestions.
A user request arrives as one context bag; the panel answers with one
assistant reply.

This is **not the TAP track**. `api/` stays the CSV → intent → gateway
write path (at1cmd → cot1 → at1qry against ct-api). ct-bot shares the
CampusTrack domain with it, but does not call ct-api, does not exchange
TAP packets, and owns no gateway.

---

## Status at T0

**Docs and registration only.** No `.exs` agent exists in this directory
yet. T1–T6 (see `milestone.md`) convert the operator-supplied prompt
sources in `docs/agents/` into RunConfig agent files. **Nothing here is
runnable until T1 lands** — see `runbook.md`.

---

## How it will work

| Hop | Output shape | Source file |
|-----|--------------|-------------|
| main | JSON reply | `docs/agents/main.md` |
| sanitize | plain text | `docs/agents/sanitize.md` |
| parse | JSON records | `docs/agents/parse.md` |
| validate | JSON validity | `docs/agents/validate.md` |
| compose | JSON notices | `docs/agents/compose.md` |
| suggestions | JSON chips | `docs/agents/suggestions.md` |

Each agent's system prompt **is** its source file, copied, not rewritten —
the files under `docs/agents/` are the source of truth. T7 wires main to
spawn sanitize → parse → validate via `spawn_agent` and wait; compose and
suggestions stay separate hops.

---

## Folder structure

```
ct-bot/
├── agents/                 # T1–T6 fill this; empty at T0
├── scripts/                # deterministic helpers land with T2–T4
├── tests/
│   ├── conftest.py         # puts scripts/ on sys.path
│   └── test_docs.py        # docs-existence checks (dormant until T1)
├── docs/
│   ├── agents/             # the six prompt-source filenames (index only)
│   └── milestones/         # per-ticket implementation notes
├── output/                 # generated output (gitignored)
├── milestone.md
├── README.md
├── runbook.md
└── tools.json              # empty manifest; entries land with the scripts
```
