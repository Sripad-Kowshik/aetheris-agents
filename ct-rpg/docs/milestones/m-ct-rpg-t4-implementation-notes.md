# T4 Implementation Notes — ct-rpg rpg-verify.exs (gate 3)

**Date:** 2026-10-28 · **Touches:** `ct-rpg/agents/rpg-verify.exs` (new),
`ct-rpg/docs/milestones/m-ct-rpg-t4-implementation-notes.md` (this file).
**No harness edit. No api child. No spawn. Not committed.**

---

## The wrap

`ct-rpg/agents/rpg-verify.exs` is a single `%Aetheris.RunConfig{}`, the
`rpg-migrate.exs` shape exactly (which is the `rpg-preflight.exs`
shape): `run_id` minted outside the struct
(`ct-rpg-verify-#{Aetheris.ID.generate()}`), `sandbox_path` from
`__ENV__.file`, `CT_RPG_MODEL`/`AETHERIS_MODEL` env fallbacks,
`AETHERIS_PROVIDER`, `mode: :record`, `context_strategy: :full`,
`overlay_base_dir: nil`, `max_steps: 4` (the single-command figure —
one verify step plus the report needs no more),
**`tools: ["run_command"]`**, `label: "CT-RPG Gate 3 Verify"` (matches
the existing `ct-rpg → CT-RPG` classifier prefix, so no
`USE_CASE_PREFIXES` change), and a one-line `user_prompt` fixture that
exists only so the file evaluates and is marked as such ("T4 fixture
turn — not a live run. Parameter: migration repo root =
`<MIGRATION_REPO_ROOT>`. Begin.").

## The prompt: gate-3 section copied verbatim, wrapped, not rewritten

The marked block inside the `system_prompt` is the gate-3 material of
`ct-rpg/docs/specs/runbook-gates.md`, assembled by `sed`-slicing the
spec file rather than retyping it, and then diff-proved byte-for-byte
against the slices:

- §1 KB spine — the `% --- gate 3: parity ---` block (spec lines
  46–49): the verify mechanism (`docker compose run --rm --entrypoint
  python rpg-migrator verify_raven_to_postgres.py`; 42 collections
  audited, 9 core domains deep-audited), the pass criterion (exit 0;
  the `[SUCCESS] … PARITY CONFIRMED …` marker; JSON `overall_status=
  PASS` with 0 missing / 0 extra / 0 mismatches), and the report
  artifact (`validation/exhaustive-parity-report-<utc-timestamp>.json`).
- §2 human view — the parity Q&A (spec lines 120–121): what the gate
  verifies and what a pass is, restated in the spec's own words.

Two bridge labels ("From §1 KB spine:", "From §2 human view:") are this
file's own words and nothing else outside the markers is gate content.
Every rule is kept; nothing is restated. The parity verifier's own
internals are `docs/specs/parity-verifier.md`'s subject — that spec is
T4's citation for the gate's meaning (see `ct-rpg/README.md`'s spec
table) and is not carried into this wrap: the wrap copies the gate-3
sections of the runbook spec only.

The unmarked paragraphs are the invocation contract, this file's own
words: the migration repo root arrives as a **parameter in the user
prompt** (never hard-coded; missing → report and stop); the agent runs
the verify step the spec names — `docker compose run --rm --entrypoint
python rpg-migrator verify_raven_to_postgres.py` — **once**, working
directory set to the supplied root, not split or retried; it reports
exactly the **exit code and the last stdout line**, and a non-zero
exit is a failed gate, said plainly; it does **not** run preflight,
migrate, or api, does not start services, and does not run any other
gate's step.

No OrbConfig, no blackboard, no spawn, no parent reference anywhere in
the file (checked: the only "spawn" hits are this decision's own
record in the header comment; zero inside the prompt).

## Spawn was not decided

Same posture as T3: this ticket does **not** decide how the parent
carries the gate-3 role text. The parent (`rpg-main.exs`, T1) wires
spawn order preflight → migrate → verify → api, but whether the verify
hop's task_prompt embeds the gate-3 slices from the spec, reads this
wrap, or something else is **left open**, to be decided with the wire
work (T5 lands the api child and completes the set) rather than
presumed here. Nothing in this change touches `rpg-main.exs` or
`rpg-migrate.exs`, and this file spawns nothing. The parent's wire
line that named T4 as the verify wrap's landing ticket is now true;
its spawn mechanics for the verify hop are unchanged and still point
at the gate-3 KB block, which remains the copy source.

## Deliberately not done here

- No api child (T5).
- No spawn wiring, no parent or sibling edit.
- No harness edit of any kind; no live run (no configured migration
  repo root is available to this change).
- No milestone-status flip: the ticket's scope was the wrap and these
  notes; `ct-rpg/milestone.md`'s T4 row is the arbiter's to flip.

---

## Done-check record

- **Evaluation, stub against the RunConfig field list** (the harness
  checkout has no `deps/`; the T0+T1 stub precedent): the file
  evaluates under plain `elixir` (1.18.5) and yields `run_id
  ct-rpg-verify-…`, `label "CT-RPG Gate 3 Verify"`, `mode: :record`,
  `context_strategy: :full`, `overlay_base_dir: nil`, `max_steps: 4`,
  `tools: ["run_command"]`, `sandbox_path: …/ct-rpg`, prompt of 2,311
  chars / 34 lines, fixture `user_prompt` as above.
- **Verbatim proof:** the embedded marked block diffed against the
  spec's own lines (46–49, 120–121 plus this file's two bridge labels)
  is **byte-for-byte identical** — zero changed lines.
- **Prompt carries the verify section and no other gate:** zero hits
  for `gate 0` / `gate_0` / `gate 2` / `gate_2` / `gate 4` / `gate_4`
  inside the marked block; the gate names appear only in the invocation
  contract's scope sentence (must-not-run), which is this file's own.
- `check_run_classifier.py`: PASS (the new label classifies under the
  existing `ct-rpg` prefix; no dead entry, nothing Unclassified).
- `python3 -m pytest ct-rpg/tests/ -q`: 6 passed.
