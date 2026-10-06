# T2 Implementation Notes — ct-bot sanitize.exs

**Date:** 2026-10-06 · **Touches:** `ct-bot/agents/sanitize.exs` (new)

---

## The wrap

`ct-bot/agents/sanitize.exs` is a single `%Aetheris.RunConfig{}`, the
T1 wrapper shape: `run_id` minted outside the struct with prefix
`ct-bot-sanitize-`, `sandbox_path` from `__ENV__.file`, `CT_BOT_MODEL`/
`AETHERIS_MODEL` env fallbacks, `mode: :record`, `context_strategy: :full`,
`overlay_base_dir: nil`, `max_steps: 4`, **`tools: []`**. The label
("CT-Bot Sanitize Agent") starts with `CT-Bot` so the existing
`ct-bot` classifier prefix (landed in T1, both `USE_CASE_PREFIXES`
constants) matches it — no classifier change this round.

The `system_prompt` is the body of `ct-bot/docs/agents/sanitize.md` copied
**verbatim**, flush-left, including the file's own `# CT-Bot buddy
sanitize child agent` title line. Reading "the body" as title-stripped
would have made the mechanical diff show a non-retarget deletion, so the
whole file is embedded and the diff is zero-change. The `user_prompt` is a
one-line fixture ("T2 fixture turn — not a live host turn. Begin.") that
exists only so the file evaluates; it is not the role and not a live host
turn, and it does not announce T7.

## Path retargets

**None.** Unlike `main.md`, the sanitize source names every sibling by
role ("the parse child agent", "the main CT-Bot chat agent") and carries
no mock-harness paths, no file-open instructions, and no `spawn_agent`
mentions. The mechanical diff (below) is the proof: zero changed lines.

## Output contract

Sanitize returns **plain text** — one schema line per student, empty slots
kept as adjacent commas, impossible dates verbatim, no JSON, no records,
no surface. This is the file's own rule 2 and output-shape section,
unchanged.

## Deliberately not done here

- No parse, validate, compose, or suggestions agent; no edit to
  `main.exs`.
- No spawn wiring; the task_prompt-vs-blackboard decision stays T7's.
- No registry row, no matrix file, no dormant flip — ct-bot has been
  active since T1 and its registration surfaces are unchanged.

## Done-check record

- `mix run --eval` remains unrunnable here (harness mirror without
  `deps/`; Hex unfetchable) — the milestone's T2 command stays owed where
  the harness runs. The same T1 substitute ran instead: plain `elixir`
  against a stub carrying the real `Aetheris.RunConfig` defstruct —
  the file evaluates; run_id `ct-bot-sanitize-…`, `tools: []`,
  label "CT-Bot Sanitize Agent".
- Mechanical diff of the embedded `system_prompt` against
  `ct-bot/docs/agents/sanitize.md`: **zero changed lines** (45 in, 45 out).
- Classifier guard: the new declared label classifies under the existing
  `ct-bot` prefix; `tests/test_run_classifier.py` green.
