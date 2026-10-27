# ct-rpg Runbook

## What you can run today

The docs-existence tests (no dormant marker — the use case is active
from T1) and the registration checks:

```bash
python3 -m pytest ct-rpg/tests/ -v
python3 -m pytest tests/test_use_case_registry.py -q
python3 scripts/drift_check.py --check use_case_registry
python3 scripts/check_run_classifier.py
```

Evaluating the wraps (needs the harness; see `ct-bot/milestone.md` T1 for
the stub-against-RunConfig fallback when the harness checkout has no
`deps/`):

```bash
cd ../aetheris
mix run --eval 'Code.eval_file("../aetheris-agents/ct-rpg/agents/rpg-main.exs")'
mix run --eval 'Code.eval_file("../aetheris-agents/ct-rpg/agents/rpg-preflight.exs")'
```

## Running the gate chain (T3–T5 pending)

Only the preflight child exists. A live chain run needs a **migration
repo root** — passed as a parameter in the user prompt, never hard-coded
— that meets gate 0's own prerequisites (Docker running, `.env` filled,
RavenDB `.pfx` in `scripts/certs/`; the full list is
`ct-rpg/docs/specs/runbook-gates.md` §2, and its unresolved items — the
missing `.ps1`, the hard-coded demo UUIDs and port — are that spec's
open items, not this runbook's).

```bash
cd ../aetheris
mix aetheris run ../aetheris-agents/ct-rpg/agents/rpg-main.exs
```

The parent spawns preflight first; until the T3–T5 wraps land it stops
after gate 0 and says which gate is next. A failed gate stops the chain
by design — that is the runbook's own stop-on-first-failure rule.

## Prerequisites

| Tool | Purpose |
|------|---------|
| Aetheris harness (`../aetheris`) | Agent runtime |
| `ANTHROPIC_API_KEY` (or provider equiv.) | LLM calls |
| A configured migration repo checkout | The system under migration — Docker, `.env`, cert |
| `python3` | This repo's test/registration suites |

No ct-api credentials, no direct RavenDB/Postgres access from here:
the migration repo's containers own all of that.
