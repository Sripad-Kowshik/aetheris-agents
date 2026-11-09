# T0 Implementation Notes — ct-bot docs and registration

**Date:** 2026-10-06 · **Touches:** `ct-bot/` (new), `docs/use-cases.md`,
`README.md`, `CLAUDE.md`, `pytest.ini`, `tests/test_tools_manifests.py`

---

## The three decisions this ticket records

1. **The source prompts are operator-supplied after this commit.** The six
   files (`main.md`, `sanitize.md`, `parse.md`, `validate.md`,
   `compose.md`, `suggestions.md`) are copied into `ct-bot/docs/agents/`
   by the operator, outside this change. What this commit carries is the
   index of the six filenames (`ct-bot/docs/agents/README.md`) and nothing
   of their content.

2. **T1–T6 convert those files and must not restate them.** Each RunConfig
   system prompt is its source file, copied, not rewritten, summarised, or
   softened. The files under `ct-bot/docs/agents/` are the source of truth
   for the panel agents; any wording that exists only in an `.exs` is a
   defect.

3. **`sprint.sh` is a harness-repo commit, not this one.** The
   `capability_matrix` sprint case's `run_agent` line for ct-bot lands in
   `../aetheris` in a later, separate commit — this change does not touch
   the harness repo at all.

No history of how the prompt sources were produced is recorded here or
anywhere in this repo; they arrive as given.

---

## Deviation from the ticket text — adjudicated before the edit

The ticket text instructed this change to create
`agents/capability_matrix_ct_bot.exs` and the `SECTIONS` entry in
`scripts/assemble_matrix.py` (the agents-repo half of the capability-matrix
registration). That instruction cannot hold at this commit, and the
conflict was put to the arbiter before writing:

- drift_check's `use_case_registry` check (one of the four registry checks
  the ticket says must stay green) compares `SECTIONS` (arm 3) and the
  `agents/capability_matrix_*.exs` stems (arm 4) against the registry
  **filtered to agent-bearing use cases** — a use case is agent-bearing
  only when its `agents/` directory holds at least one `.exs`.
- `ct-bot/agents/` holds only a `README.md` in this change, so ct-bot is
  non-agent-bearing, and registering the matrix half now turns arms 3 and 4
  red. The check's own comment names this as declared design, not accident
  (boxy-pipeline is the precedent: a non-agent-bearing use case is a
  declared absentee from the matrix).
- **The arbiter chose: defer to T1.** No section agent and no `SECTIONS`
  entry in this change. The matrix half of the registration is therefore
  written into **T1's** What-will-be-built and done-when in
  `ct-bot/milestone.md` — it becomes *required* at exactly that ticket,
  because the moment T1 lands `ct-bot/agents/main.exs`, ct-bot is
  agent-bearing and both arms demand the section agent and the `SECTIONS`
  entry. T1's done-when re-runs
  `python3 scripts/drift_check.py --check use_case_registry`.

---

## Registration inventory

- `docs/use-cases.md` — one row: `ct-bot`, status **`dormant`** (a value
  the file already uses), status set 2026-10-06, reason "Docs only — no
  agent file yet", condition for return "T1 RunConfig lands". Dormant was
  the only status consistent with a condition-for-return cell: an `active`
  row's condition is "Nothing pending", and this one has a pending ticket.
  Dormant requires the marker, so `ct-bot/tests/test_docs.py` carries
  `pytestmark = pytest.mark.dormant` in the same change.
- `tests/test_tools_manifests.py` — `SWEPT` assertion gains `"ct-bot"`
  (sorted position after `cloudcost`); the discovery sweep picks ct-bot up
  because it carries a `tools.json`, and the sweep-guard would have failed
  otherwise.
- `tests/test_run_record_adoption.py` — ct-bot enters `NON_PRODUCERS` ("no
  agent file yet; scripts land with T2–T4"): that file's partition test
  requires every registry row to be classified producer or not, and it
  names the requirement in its own failure message. Its
  `test_non_producers_do_not_record` guard assumed every use case already
  has `.py` scripts; a scripts-empty use case now skips visibly (the
  negative search has no population) instead of failing the vacuous-guard
  assert. Every non-producer *with* scripts — drive, email, api/* — still
  runs the search unchanged.
- `pytest.ini` — the dormant long form (the comment block and the
  `markers =` line) gains ct-bot beside boxy-pipeline. Prose, not checked,
  but it is the long form of the registry row's last column.
- Root `README.md` §Use cases and `CLAUDE.md` §Key docs — one row each;
  both tables are arms 1–2 of drift_check's `use_case_registry` check and
  must equal the registry.
- Registry prose (the "nine active rows" paragraph) deliberately untouched:
  it remains true as written and its enumerations are out of the check's
  scope by that check's own criterion.

---

## Deliberately not done here

- No `.exs` agent, no RunConfig, no OrbConfig anywhere in `ct-bot/`.
- No `agents/capability_matrix_ct_bot.exs`, no `assemble_matrix.SECTIONS`
  entry (deferred to T1 — see the deviation above).
- No harness commit of any kind.
- No ct-bot section in `docs/capability-matrix.md` — the matrix is
  generated, and hand-editing a generated file is not registration.
