# Use cases — the registry

**This file is the declaration.** A use case's status lives here, in a committed row, and
nowhere else. It is not encoded in the directory layout: the identifier is the address and the
path is never load-bearing. Anything that discovers use cases by scanning directories silently
stops seeing a moved one, and that is indistinguishable from the discovery being broken —
which is why the declaration is a row rather than a location. Relocating a directory is
cosmetics and may be done on its own merits; it must never be taken as the mechanism.

`Landed at ds t1a, 2026-08-19. The ruling this file implements is docs/milestones/ds-milestone.md
§t1a, "The ruling, landed here rather than cited".`

## Membership — what is a row

> **A use case is a directory D — not the repository root — such that both `D/tests/conftest.py`
> and `D/scripts/` exist.**

The conftest is the only signal that is *load-bearing* rather than incidental: it is the file
that puts `D/scripts/` on `sys.path`, so it exists exactly when there is a separately-testable
body of use-case code. The criterion privileges neither `agents/` — which would exclude
`boxy-pipeline`, the one use case this registry exists to declare — nor `docs/`, whose location
varies (`provenance`'s docs are at `docs/provenance/`, not `provenance/docs/`) and which is
exactly the path-is-load-bearing trap the ruling forbids. `rig/` has `scripts/` and no
`tests/conftest.py` and is correctly out: it is the desktop app that *consumes* use cases.

Reproducing command, from the repo root:

```bash
git ls-files '*/tests/conftest.py' | sed 's|/tests/conftest.py||' | grep -v '^tests$'
```

`api` is **two rows, not one.** The parent `api/` has neither a `tests/conftest.py` nor a
`scripts/`; both children have both, and every mechanical surface in the repo already splits
them — two conftests, two `capability_matrix_*.exs`, `assemble_matrix.SECTIONS`' `api_tenant` /
`api_gateway`, and both of Rig's classifier tables. The stated cost: the two rows share one
parent-level `api/tools.json`, so surfaces that key on the manifest see one coarser `api`. That
is a mapping in the check, named in its message, not a second registry.

## The registry

| Use case | Status | Status set | Reason (business state) | Condition for return |
|---|---|---|---|---|
| `api/gateway` | active | 2026-08-19 | Work is not paused. | Nothing pending. It becomes `dormant` when its work is paused and `pytest.mark.dormant` is applied to its tests. |
| `api/tenant` | active | 2026-08-19 | Work is not paused. | Nothing pending. It becomes `dormant` when its work is paused and `pytest.mark.dormant` is applied to its tests. |
| `boxy-pipeline` | dormant | 2026-08-16 | Paused pending the client. | It runs again when boxy-pipeline work resumes. To restore it, delete the `pytestmark = pytest.mark.dormant` lines from `boxy-pipeline/tests/test_*.py`; nothing else was changed for the pause. **What un-pausing will cost is BL-159** — roughly four hours, no finish under either of two caps, one test red deliberately and a second failure not yet identified. Read that row first. |
| `ct-bot` | dormant | 2026-10-06 | Docs only — no agent file yet; T1–T6 pending. | It becomes active when T1 lands: `ct-bot/agents/main.exs`, the RunConfig converted from `ct-bot/docs/agents/main.md`, exists and evaluates. Until then its tests carry `pytestmark = pytest.mark.dormant`; restoring means deleting that line and flipping this row in the same change. |
| `cloudcost` | active | 2026-08-19 | Work is not paused. | Nothing pending. It becomes `dormant` when its work is paused and `pytest.mark.dormant` is applied to its tests. |
| `docbuilder` | active | 2026-08-19 | Work is not paused. | Nothing pending. It becomes `dormant` when its work is paused and `pytest.mark.dormant` is applied to its tests. |
| `drive` | active | 2026-08-19 | Work is not paused. | Nothing pending. It becomes `dormant` when its work is paused and `pytest.mark.dormant` is applied to its tests. |
| `eduloka` | active | 2026-08-19 | Work is not paused. | Nothing pending. It becomes `dormant` when its work is paused and `pytest.mark.dormant` is applied to its tests. |
| `email` | active | 2026-08-19 | Work is not paused. | Nothing pending. It becomes `dormant` when its work is paused and `pytest.mark.dormant` is applied to its tests. |
| `payslip` | active | 2026-08-19 | Work is not paused. | Nothing pending. It becomes `dormant` when its work is paused and `pytest.mark.dormant` is applied to its tests. |
| `provenance` | active | 2026-08-19 | Work is not paused. | Nothing pending. It becomes `dormant` when its work is paused and `pytest.mark.dormant` is applied to its tests. |

**The nine active rows share one reason and one condition, and that is the honest answer rather
than an unfinished one.** The reason field states business state; for a use case that is not
paused the business state *is* "not paused", and nothing in the tree distinguishes the nine.
Nine differently-worded sentences would be nine claims about roadmap intent that no committed
artefact carries. The field earns its keep on the row that has something to say, and
`boxy-pipeline` is that row. When a second use case pauses, its row states why, on the same
shape.

**`Status set` is the date the status in the row's `Status` cell was set** — not the date the
row was written. The nine active rows carry the date this registry landed because that is when
each was first declared active; `boxy-pipeline` carries `2026-08-16`, the date of its pause, and
that date is `pytest.ini`'s too.

## What checks this file

Four checks, homed by whether their subject is this repository's own tracked content or a
correspondence the doc-sync gate's operator reads:

| check | home | what it asserts |
|---|---|---|
| registry ↔ use-case directories | `tests/test_use_case_registry.py` | every directory meeting the membership criterion has a row, and every row a directory |
| registry ↔ `pytest.mark.dormant` markers | `tests/test_use_case_registry.py` | the set of use cases carrying the marker is exactly the set of rows with status `dormant` |
| registry ↔ the separable doc enumerations | `scripts/drift_check.py --check use_case_registry` | the enumerations that a parser can extract without deciding what a sentence means agree with this table |
| registry ↔ Rig's two `USE_CASE_PREFIXES` | `scripts/check_run_classifier.py`, wrapped by `tests/test_run_classifier.py` | Rig's usage view and its run list classify the same use cases |

**What is deliberately NOT checked.** A surface whose enumeration cannot be extracted without
reading English is out of scope, and is fixed by a human edit or de-numeralised — never by a
check that has to locate a list inside paragraphs. That covers `pytest.ini`'s dormancy comment
block and its `markers = dormant: …` sentence, `ROADMAP.md`'s narrative, the manifest's runbook
prose, and `agents/orchestrator.exs`'s few-shot examples. Dormancy loses nothing by it: the
marker's *effect* is `pytestmark = pytest.mark.dormant`, a code literal in seven files, and that
is what the second check reads. `pytest.ini`'s prose stays a human-readable restatement, and its
`CONDITION FOR RETURN` block is the long form of this table's last column.

**Out of scope by subject, not by form:** harness `scripts/sprint.sh`'s case names are
separable and enumerate *sprint cases*, which are not use cases — `provenance` is a use case
with no sprint case, and `drift_check` / `capability_matrix` / `chaos` are sprint cases that are
not use cases. A registry check over them would be an incorrect check that happened to be easy.
