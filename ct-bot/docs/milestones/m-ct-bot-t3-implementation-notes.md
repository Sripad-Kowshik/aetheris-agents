# T3 Implementation Notes — ct-bot parse.exs

**Date:** 2026-10-06 · **Touches:** `ct-bot/agents/parse.exs` (new)

---

## The wrap

`ct-bot/agents/parse.exs` is a single `%Aetheris.RunConfig{}`, the T2
wrapper shape unchanged: `run_id` minted outside the struct with prefix
`ct-bot-parse-`, `sandbox_path` from `__ENV__.file`, `CT_BOT_MODEL`/
`AETHERIS_MODEL` env fallbacks, `mode: :record`, `context_strategy: :full`,
`overlay_base_dir: nil`, `max_steps: 4`, **`tools: []`**. The label
("CT-Bot Parse Agent") starts with `CT-Bot`, so the existing `ct-bot`
classifier prefix matches it — no classifier change this round.

The `system_prompt` is the body of `ct-bot/docs/agents/parse.md` copied
**verbatim**, flush-left, including the file's own `# CT-Bot buddy parse
child agent` title line — the reading that keeps the mechanical diff at
zero changes (the ticket names it explicitly). The `user_prompt` is a
one-line fixture ("T3 fixture turn — not a live host turn. Begin.") that
exists only so the file evaluates; it is not the role, not a live host
turn, and does not announce T7.

## Path retargets

**None.** The parse source names siblings by role ("the sanitize hop")
and the host by name; it carries no mock-harness paths, no file-open
instructions, and no `spawn_agent` mentions. The mechanical diff below is
the proof: zero changed lines.

## Output contract

Parse returns **JSON records** — the `chatText` + `buddy-enrol-workspace`
`surface` envelope with `records[]`, `parse` summary, the mandatory span
contract, and the never-invent rules — verbatim from the source. It does
not talk to the user (the host relays its JSON), which is the file's own
opening rule, unchanged.

## Deliberately not done here

- No validate, compose, or suggestions agent; no edit to `main.exs` or
  `sanitize.exs`.
- No spawn wiring; the task_prompt-vs-blackboard decision stays T7's.
- No registry row, no matrix file, no dormant flip — ct-bot has been
  active since T1 and its registration surfaces are unchanged.

## Done-check record

- `mix run --eval` remains unrunnable here (harness mirror without
  `deps/`; Hex unfetchable) — the milestone's T3 command stays owed where
  the harness runs. The same T1/T2 substitute ran instead: plain `elixir`
  against a stub carrying the real `Aetheris.RunConfig` defstruct —
  the file evaluates; run_id `ct-bot-parse-…`, `tools: []`, label
  "CT-Bot Parse Agent".
- Mechanical diff of the embedded `system_prompt` against
  `ct-bot/docs/agents/parse.md`: **zero changed lines** (107 in, 107 out).
- Classifier guard: the new declared label classifies under the existing
  `ct-bot` prefix; `tests/test_run_classifier.py` green.
