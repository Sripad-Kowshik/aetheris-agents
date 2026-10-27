# T0+T1 Implementation Notes — ct-rpg registration and the first agents

**Date:** 2026-10-27 · **Touches:** `ct-rpg/` (new), `ct-rpg/agents/rpg-main.exs` (new),
`ct-rpg/agents/rpg-preflight.exs` (new), `agents/capability_matrix_ct-rpg.exs` (new),
`docs/use-cases.md`, `README.md`, `CLAUDE.md`, `scripts/assemble_matrix.py`,
`tests/test_tools_manifests.py`, `tests/test_run_record_adoption.py`,
`rig/src/components/modules/harness/RunList.tsx`, `rig/src-tauri/src/commands/usage.rs`

This change is T0 (registration) **and** T1 (parent + first child) in one
commit, so the registry row never has to pass through `dormant`: the row
is `active` in the same change that lands `ct-rpg/agents/rpg-main.exs`,
which is exactly the flip rule. No `pytest.mark.dormant` marker exists in
`ct-rpg/tests/`, no `pytest.ini` change, and the registry's dormancy
check (markers ≡ dormant rows) agrees trivially.

---

## The specs are the source of truth; the wraps copy, never restate

- `rpg-main.exs`'s `system_prompt` is the **body of
  `ct-rpg/docs/specs/runbook-gates.md`, byte-for-byte** — assembled by
  `cat`-ing the spec file into the heredoc rather than retyping it, so a
  diff against the source shows the wrap exactly. No retargets: the
  spec's legacy-repo references (`agent_runbook.md`,
  `verify-prerequisites.sh`, `references/campustrack.md`,
  `specs/golden/`) are the spec's own citations and stay verbatim. After
  the copy, one clearly marked WIRE section (this file's own words) adds
  the spawn behaviour; it adds no gate rule.
- `rpg-preflight.exs`'s `system_prompt` copies the **gate-0 section** of
  the same spec: the `% --- gate 0: preflight ---` KB statements (§1) and
  the three preflight Q&A entries (§2), including the unresolved
  PowerShell entry — carried verbatim because an unresolved product
  decision is not ours to resolve in a system prompt. The unmarked
  paragraphs around the copy are the invocation contract only: the
  migration repo root arrives as a **parameter in the user prompt** (the
  fixture `user_prompt` carries the placeholder `<MIGRATION_REPO_ROOT>`;
  it is not a live turn), the script runs once from that root, the report
  is the exit code and the last stdout line, and nothing outside gate 0
  is touched.

## Why the preflight child lands at T1, not T2

A parent whose chain has no spawnable first child cannot be evaluated as
a parent, so T1 lands the pair: the spawn → wait → `final_message` →
stop-on-first-failure behaviour exists and is exercisable from T1. T2's
scope is therefore the preflight child's **live verification** (a real
configured migration repo root, one pass and one fail), not the
authoring of the wrap — `ct-rpg/milestone.md` states this on both
tickets.

## The parent→child channel

The child's `final_message` is the channel; `spawn_agent` +
`wait_for_all` is the whole mechanism, as proven by ct-bot T7
(`ct-bot/milestone.md`'s timeout-ms bullet). The wire section pins
`timeout_ms: 120000` per wait, treats a terminal-status child as FINISHED
(a finished child is never reported as timed out), and forbids retrying
or spawning past a failed gate. Stop-on-first-failure is the spec's own
execution rule, applied to the spawn order — not a new rule.

## Registration inventory (every surface, and why)

- `docs/use-cases.md` — one row: `ct-rpg`, status **`active`**, status
  set 2026-10-27, the shared active reason and condition. Inserted after
  `ct-bot`, the table's sorted position.
- `tests/test_tools_manifests.py` — `SWEPT` assertion gains `"ct-rpg"`
  after `"ct-bot"`; the discovery sweep picks ct-rpg up because it
  carries a `tools.json`, and the sweep-guard would fail otherwise.
- `tests/test_run_record_adoption.py` — ct-rpg enters `NON_PRODUCERS`
  ("no producer scripts yet (T0+T1); the gate scripts run in the
  migration repo's containers"): that file's partition test requires
  every registry row to be classified producer or not, and its failure
  message says so. `ct-rpg/scripts/` holds no `.py`, so the negative
  search skips visibly (the ct-bot-at-T0 precedent, already in that
  test).
- Root `README.md` §Use cases and `CLAUDE.md` §Key docs — one row each;
  both tables are arms 1–2 of drift_check's `use_case_registry` check and
  must equal the registry.
- `scripts/assemble_matrix.py` — `SECTIONS` entry `("ct-rpg", "ct-rpg")`
  after `("ct-bot", "ct-bot")`, and `agents/capability_matrix_ct-rpg.exs`
  (copy of the ct-bot section agent; five values changed: agents dir,
  scripts dir, section file `docs/.sections/ct-rpg.md`, heading
  `## CT-RPG`, run_id/label). **Required at exactly this ticket** (unlike
  ct-bot T0, which deferred both to T1): this change lands `.exs` files
  under `ct-rpg/agents/`, so ct-rpg is agent-bearing at this commit and
  drift_check arms 3–4 demand the entry and the section agent now.
  Filename spelled with the hyphen — `capability_matrix_ct-rpg.exs` — per
  the ct-bot T1 finding (arm 4 compares `stem.replace("capability_matrix_",
  "")` against the registry id).
- `rig/src/components/modules/harness/RunList.tsx` and
  `rig/src-tauri/src/commands/usage.rs` — `ct-rpg → CT-RPG` added to both
  `USE_CASE_PREFIXES` constants, adjacent in both files. Every declared
  label matches: `"CT-RPG Migration Gate Orchestrator"` and
  `"CT-RPG Gate 0 Preflight"` under the new prefix; the section agent's
  `"cap-matrix: ct-rpg"` under the existing `cap-matrix` prefix. `rig/`
  is this repo, not the harness.
- `docs/capability-matrix.md` deliberately untouched — generated, and
  hand-editing a generated file is not registration (the ct-bot T1
  precedent). `docs/.sections/` is gitignored; the assembler tolerates a
  missing section file with a WARN until a section-agent run generates it.
- `rig/src-tauri/src/commands/tools.rs`'s manifest vec deliberately
  untouched — already missing newer manifests (ct-bot among them); the
  drift_check arm over it is a subset arm and Rust tests are not part of
  this repo's gate.

## Deliberately not done here

- No migrate, verify, or api child (T3–T5).
- No live preflight run (T2) — no configured migration repo root is
  available to this change.
- No harness commit of any kind.
- No section file committed (gitignored, generated).
- No golden capture — every spec's own status line already records that
  the goldens await a live legacy environment.

---

## Done-check record

- **Wrap evaluation — stub against the real RunConfig field list** (the
  harness checkout has no `deps/`; same ground as ct-bot T1's note): both
  `.exs` files evaluate under plain `elixir` (1.18.5) against a stub
  carrying the RunConfig fields this repo's agents actually use, and
  yield the expected shapes — `rpg-main.exs`: run_id `ct-rpg-main-…`,
  `tools: ["spawn_agent", "wait_for_all"]`, `max_steps: 12`,
  `context_strategy: :full`, `overlay_base_dir: nil`,
  `sandbox_path: …/ct-rpg`; `rpg-preflight.exs`: run_id
  `ct-rpg-preflight-…`, `tools: ["run_command"]`, `max_steps: 4`.
  Verbatim-body proof: the embedded system prompt of `rpg-main.exs`
  minus the WIRE section is byte-identical to
  `ct-rpg/docs/specs/runbook-gates.md` (the copy was assembled by
  concatenation, and the diff over the copied range is empty).
- `python3 scripts/drift_check.py --check use_case_registry` — green;
  agent-bearing count up one, `ct-rpg` among them.
- `python3 scripts/check_run_classifier.py` — green; both constants agree
  with the new prefix, no dead entry, no Unclassified declared label.
- `python3 -m pytest ct-rpg/tests/ tests/ -q` — green.
