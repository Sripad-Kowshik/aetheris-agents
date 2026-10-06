# ct-bot Runbook

**Not runnable until T1.** This use case is registered and dormant: it has
docs, an empty tools manifest, and existence tests — no `.exs` agent exists
yet. `mix aetheris run` against this directory will fail until T1 lands
`ct-bot/agents/main.exs`.

---

## What you can run today

The docs-existence tests (dormant in the whole-suite gate, runnable scoped):

```bash
python3 -m pytest ct-bot/tests/ -v
```

The registration checks:

```bash
python3 -m pytest tests/test_use_case_registry.py -q
python3 scripts/drift_check.py --check use_case_registry
```

---

## What lands next

| Ticket | Lands | Notes |
|--------|-------|-------|
| T1 | `agents/main.exs` | System prompt = `docs/agents/main.md`, copied, not rewritten |
| T2–T6 | one `.exs` per hop | Each system prompt = its `docs/agents/*.md` source |
| T7 | wire in `main.exs` | sanitize → parse → validate via `spawn_agent` |

The six prompt sources are **operator-supplied**: they are copied into
`docs/agents/` by the operator, outside the repo's ticket flow. This repo
never edits them; T1–T6 convert them.

---

## Prerequisites (once T1 lands)

| Tool | Purpose |
|------|---------|
| Aetheris harness (`../aetheris`) | Agent runtime |
| `ANTHROPIC_API_KEY` | LLM calls |
| `python3` | Deterministic helpers (T2–T4) |

No ct-api credentials: this use case does not call ct-api.
