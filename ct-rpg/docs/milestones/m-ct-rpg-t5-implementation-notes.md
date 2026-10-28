# T5 Implementation Notes — ct-rpg rpg-api.exs (gate 4)

**Date:** 2026-10-28 · **Touches:** `ct-rpg/agents/rpg-api.exs` (new),
`ct-rpg/docs/milestones/m-ct-rpg-t5-implementation-notes.md` (this file).
**No harness edit. No spawn. No existing child edited. Not committed.**

---

## The wrap

`ct-rpg/agents/rpg-api.exs` is a single `%Aetheris.RunConfig{}`, the
`rpg-verify.exs` shape (which is the `rpg-migrate.exs` / `rpg-preflight.exs`
shape): `run_id` minted outside the struct
(`ct-rpg-api-#{Aetheris.ID.generate()}`), `sandbox_path` from
`__ENV__.file`, `CT_RPG_MODEL`/`AETHERIS_MODEL` env fallbacks,
`AETHERIS_PROVIDER`, `mode: :record`, `context_strategy: :full`,
`overlay_base_dir: nil`, **`tools: ["run_command"]`**, `label:
"CT-RPG Gate 4 API"` (matches the existing `ct-rpg → CT-RPG`
classifier prefix, so no `USE_CASE_PREFIXES` change), and a one-line
`user_prompt` fixture that exists only so the file evaluates and is
marked as such ("T5 fixture turn — not a live run. Parameter:
migration repo root = `<MIGRATION_REPO_ROOT>`. Begin.").

**One deliberate field deviation, recorded:** `max_steps: 6`, not the
siblings' 4. Gate 4 is the one child whose step is a *sequence* — the
spec's mechanism names two read curls and one write curl — so the
single-command figure of T2–T4 does not fit; three curls plus the
report need the headroom. Every other wrapper field is byte-identical
to the siblings' shape.

## The prompt: gate-4 section copied verbatim, wrapped, not rewritten

The marked block inside the `system_prompt` is the gate-4 material of
`ct-rpg/docs/specs/runbook-gates.md`, assembled by `sed`-slicing the
spec file rather than retyping it, and then diff-proved byte-for-byte
against the slices:

- §1 KB spine — the `% --- gate 4: api ---` block (spec lines 51–53):
  the read endpoints (`curl GET /api/stu/student?limit=2`,
  `/api/feeTx?limit=2` → HTTP 200, valid JSON array) and the write
  endpoint (`curl POST /api/feeTx` with the **hard-coded demo body** →
  HTTP 200 or 201 with created transaction JSON) — the hard-coded body
  carried exactly as the spec states it, including the word
  "hard-coded", because the spec's open item 3 (dataset-coupled demo
  UUIDs) is the spec's unresolved product decision, not this wrap's to
  soften.
- §2 human view — the gate-4 Q&A (spec lines 123–124): two reads and
  one write that inserts a fee transaction and activates the audit
  trigger.

Two bridge labels ("From §1 KB spine:", "From §2 human view:") are this
file's own words and nothing else outside the markers is gate content.
Every rule is kept; nothing is restated. The api step's own response
shapes are `docs/specs/api-verification.md`'s subject — that spec is
T5's citation for the gate's meaning (see `ct-rpg/README.md`'s spec
table) and is not carried into this wrap: the wrap copies the gate-4
sections of the runbook spec only.

The unmarked paragraphs are the invocation contract, this file's own
words. The one adaptation the gate's shape forces, recorded: the
report contract is **per curl** — exit code and last stdout line for
each of the three curls — with a non-zero exit a failed gate that
stops the step (no further curl), which is the gate sequence's own
stop-on-first-failure rule applied inside the child. Everything else
mirrors the siblings: the migration repo root arrives as a **parameter
in the user prompt** (never hard-coded; missing → report and stop);
the curls run **once**, in the marked block's order (reads, then the
write), working directory set to the supplied root, not split,
retried, or wrapped in neighbouring commands; the agent does **not**
run preflight, migrate, or verify, does not start services, and does
not run any other gate's step.

No OrbConfig, no blackboard, no spawn, no parent or sibling reference
anywhere in the file (checked: zero hits; the only "spawn" text is
this decision's own record in the header comment, T3/T4's shape).

## Spawn was not decided

Same posture as T3 and T4: this ticket does **not** decide how the
parent carries the gate-4 role text. The parent (`rpg-main.exs`, T1)
wires spawn order preflight → migrate → verify → api, but whether the
api hop's task_prompt embeds the gate-4 slices from the spec, reads
this wrap, or something else is **left open** for the wire work —
which is now unblocked, the child set being complete. Nothing in this
change touches `rpg-main.exs` or any existing child, and this file
spawns nothing. The parent's wire line that named T5 as the api wrap's
landing ticket is now true; its spawn mechanics for the api hop are
unchanged and still point at the gate-4 KB block, which remains the
copy source.

## Deliberately not done here

- No spawn wiring, no parent edit, no edit to any existing child.
- No harness edit of any kind; no live run (no configured migration
  repo root is available to this change).
- No milestone-status flip: the ticket's scope was the wrap and these
  notes; `ct-rpg/milestone.md`'s T5 row is the arbiter's to flip.

---

## Done-check record

- **Evaluation, stub against the RunConfig field list** (the harness
  checkout has no `deps/`; the T0+T1 stub precedent): the file
  evaluates under plain `elixir` (1.18.5) and yields `run_id
  ct-rpg-api-…`, `label "CT-RPG Gate 4 API"`, `mode: :record`,
  `context_strategy: :full`, `overlay_base_dir: nil`, `max_steps: 6`,
  `tools: ["run_command"]`, `sandbox_path: …/ct-rpg`, prompt of 1,823
  chars / 34 lines, fixture `user_prompt` as above.
- **Verbatim proof:** the embedded marked block diffed against the
  spec's own lines (51–53, 123–124 plus this file's two bridge labels)
  is **byte-for-byte identical** — zero changed lines.
- **Prompt carries the api section and no other gate:** zero hits for
  `gate 0` / `gate_0` / `gate 2` / `gate_2` / `gate 3` / `gate_3`
  inside the marked block; the gate names appear only in the invocation
  contract's scope sentence (must-not-run), which is this file's own.
- `check_run_classifier.py`: PASS (the new label classifies under the
  existing `ct-rpg` prefix; no dead entry, nothing Unclassified).
- `python3 -m pytest ct-rpg/tests/ -q`: 6 passed.
