# T3 Implementation Notes — ct-rpg rpg-migrate.exs (gate 2)

**Date:** 2026-10-28 · **Touches:** `ct-rpg/agents/rpg-migrate.exs` (new),
`ct-rpg/docs/milestones/m-ct-rpg-t3-implementation-notes.md` (this file).
**No harness edit. No verify or api child. No spawn. Not committed.**

---

## The wrap

`ct-rpg/agents/rpg-migrate.exs` is a single `%Aetheris.RunConfig{}`, the
`rpg-preflight.exs` shape exactly: `run_id` minted outside the struct
(`ct-rpg-migrate-#{Aetheris.ID.generate()}`), `sandbox_path` from
`__ENV__.file`, `CT_RPG_MODEL`/`AETHERIS_MODEL` env fallbacks,
`AETHERIS_PROVIDER`, `mode: :record`, `context_strategy: :full`,
`overlay_base_dir: nil`, `max_steps: 4` (the preflight single-command
figure — one migrate step plus the report needs no more),
**`tools: ["run_command"]`**, `label: "CT-RPG Gate 2 Migrate"` (matches
the existing `ct-rpg → CT-RPG` classifier prefix, so no
`USE_CASE_PREFIXES` change), and a one-line `user_prompt` fixture that
exists only so the file evaluates and is marked as such ("T3 fixture
turn — not a live run. Parameter: migration repo root =
`<MIGRATION_REPO_ROOT>`. Begin.").

## The prompt: gate-2 section copied verbatim, wrapped, not rewritten

The marked block inside the `system_prompt` is the gate-2 material of
`ct-rpg/docs/specs/runbook-gates.md`, assembled by `sed`-slicing the
spec file rather than retyping it, and then diff-proved byte-for-byte
against the slices:

- §1 KB spine — the `% --- gate 2: migration ---` block (spec lines
  41–44): the migrate mechanism (`docker compose run --rm rpg-migrator
  --all` → `python migrate_all.py`, 30 ETLs in fixed order, then the
  view + trigger SQL), the exit-criterion (`exits 1 if any module
  failed; else 0`), and the table-count criterion (`\dt` lists 42).
- §2 human view — the two migration Q&A entries (spec lines 114–118):
  what counts as success, and the module-failure behaviour (per-module
  `[!]`, tallies, post-SQL if at least one module succeeded, exits 1,
  the runbook's stop-on-error rule). The unresolved gate-2 open item
  (the success-string mismatch, spec open item 2) lives in the spec's
  §4 and is not carried into this wrap — the wrap copies the gate-2
  sections only.

Two bridge labels ("From §1 KB spine:", "From §2 human view:") are this
file's own words and nothing else outside the markers is gate content.
Every rule is kept; nothing is restated.

The unmarked paragraphs are the invocation contract, this file's own
words: the migration repo root arrives as a **parameter in the user
prompt** (never hard-coded; missing → report and stop); the agent runs
the migrate step the spec names — `docker compose run --rm rpg-migrator
--all` — **once**, working directory set to the supplied root, not
split or retried; it reports exactly the **exit code and the last
stdout line**, and a non-zero exit is a failed gate, said plainly; it
does **not** run preflight, verify, or api, does not start services,
and does not run any other gate's step. The table-count criterion of
the spec's gate-2 copy is the gate's rule, carried verbatim — this
wrap's report contract is the two-field report above, not a second
definition of success.

No OrbConfig, no blackboard, no spawn, no parent reference anywhere in
the file (checked: zero hits).

## Spawn was not decided

This ticket does **not** decide how the parent carries the gate-2 role
text. The parent (`rpg-main.exs`, T1) wires spawn order preflight →
migrate → verify → api and, per its wire section, copies child role
texts into `task_prompt` — but whether the migrate hop's task_prompt
embeds the gate-2 slices from the spec, reads this wrap, or something
else is **left open**, to be decided with the wire work (with the
verify and api children landing, T4–T5) rather than presumed here.
Nothing in this change touches `rpg-main.exs`, and this file spawns
nothing. The parent's wire line that named T3 as the migrate wrap's
landing ticket is now true; its spawn mechanics for the migrate hop are
unchanged and still point at the gate-2 KB block, which remains the
copy source.

## Deliberately not done here

- No verify child (T4), no api child (T5).
- No spawn wiring, no parent edit.
- No harness edit of any kind; no live run (no configured migration
  repo root is available to this change).
- No milestone-status flip: the ticket's scope was the wrap and these
  notes; `ct-rpg/milestone.md`'s T3 row is the arbiter's to flip.

---

## Done-check record

- **Evaluation, stub against the RunConfig field list** (the harness
  checkout has no `deps/`; the T0+T1 stub precedent): the file
  evaluates under plain `elixir` (1.18.5) and yields `run_id
  ct-rpg-migrate-…`, `label "CT-RPG Gate 2 Migrate"`, `mode: :record`,
  `context_strategy: :full`, `overlay_base_dir: nil`, `max_steps: 4`,
  `tools: ["run_command"]`, `sandbox_path: …/ct-rpg`, prompt of 2,266
  chars / 36 lines, fixture `user_prompt` as above.
- **Verbatim proof:** the embedded marked block diffed against the
  spec's own lines (41–44, 114–118 plus this file's two bridge labels)
  is **byte-for-byte identical** — zero changed lines.
- **Prompt carries the migrate section and no other gate:** zero hits
  for `gate 0` / `gate_0` / `gate 3` / `gate_3` / `gate 4` / `gate_4`
  inside the marked block; the gate names appear only in the invocation
  contract's scope sentence (must-not-run), which is this file's own.
- `check_run_classifier.py`: PASS (the new label classifies under the
  existing `ct-rpg` prefix; no dead entry, nothing Unclassified).
- `python3 -m pytest ct-rpg/tests/ -q`: 6 passed.
