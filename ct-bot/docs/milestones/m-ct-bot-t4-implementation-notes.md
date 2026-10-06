# T4 Implementation Notes — ct-bot validate.exs

**Date:** 2026-10-06 · **Touches:** `ct-bot/agents/validate.exs` (new)

---

## The wrap

`ct-bot/agents/validate.exs` is a single `%Aetheris.RunConfig{}`, the T3
wrapper shape unchanged: `run_id` minted outside the struct with prefix
`ct-bot-validate-`, `sandbox_path` from `__ENV__.file`, `CT_BOT_MODEL`/
`AETHERIS_MODEL` env fallbacks, `mode: :record`, `context_strategy: :full`,
`overlay_base_dir: nil`, `max_steps: 4`, **`tools: []`**. The label
("CT-Bot Validate Agent") starts with `CT-Bot`, so the existing `ct-bot`
classifier prefix matches it — no classifier change this round.

The `system_prompt` is the body of `ct-bot/docs/agents/validate.md` copied
**verbatim**, flush-left, including the file's own `# CT-Bot buddy validate
child agent` title line — the reading that keeps the mechanical diff at
zero changes (the ticket names it explicitly). The `user_prompt` is a
one-line fixture ("T4 fixture turn — not a live host turn. Begin.") that
exists only so the file evaluates; it is not the role, not a live host
turn, and does not announce T7.

## Path retargets

**None.** The validate source names every sibling by role ("the parse
agent", "the sanitize agent", "the main CT-Bot chat agent") and the host by
name; it carries no mock-harness paths, no file-open instructions, and no
`spawn_agent` mentions. The mechanical diff below is the proof: zero
changed lines.

## Output contract

Validate returns **JSON only**: `{records: [{id, valid, reasons}]}` — one
entry per input record keyed by the received `id`, fail-closed semantics
(a missing entry, an invented id, missing `required` structure), the
stale-rejection rule, and the Never list — verbatim from the source. It
does not save, parse notes, or emit a surface, which is the file's own
opening and closing rules, unchanged.

## Deliberately not done here

- No compose or suggestions agent; no edit to `main.exs`, `sanitize.exs`,
  or `parse.exs`.
- No spawn wiring; the task_prompt-vs-blackboard decision stays T7's.
- No registry row, no matrix file, no dormant flip — ct-bot has been
  active since T1 and its registration surfaces are unchanged.

## Done-check record

- `mix run --eval` remains unrunnable here (harness mirror without
  `deps/`; Hex unfetchable) — the milestone's T4 command stays owed where
  the harness runs. The same T1–T3 substitute ran instead: plain `elixir`
  against a stub carrying the real `Aetheris.RunConfig` defstruct —
  the file evaluates; run_id `ct-bot-validate-…`, `tools: []`, label
  "CT-Bot Validate Agent".
- Mechanical diff of the embedded `system_prompt` against
  `ct-bot/docs/agents/validate.md`: **zero changed lines** (59 in, 59 out).
- Classifier guard: the new declared label classifies under the existing
  `ct-bot` prefix; `tests/test_run_classifier.py` green.
