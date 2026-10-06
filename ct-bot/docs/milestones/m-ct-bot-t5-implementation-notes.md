# T5 Implementation Notes — ct-bot compose.exs

**Date:** 2026-10-06 · **Touches:** `ct-bot/agents/compose.exs` (new)

---

## The wrap

`ct-bot/agents/compose.exs` is a single `%Aetheris.RunConfig{}`, the T4
wrapper shape unchanged: `run_id` minted outside the struct with prefix
`ct-bot-compose-`, `sandbox_path` from `__ENV__.file`, `CT_BOT_MODEL`/
`AETHERIS_MODEL` env fallbacks, `mode: :record`, `context_strategy: :full`,
`overlay_base_dir: nil`, `max_steps: 4`, **`tools: []`**. The label
("CT-Bot Compose Agent") starts with `CT-Bot`, so the existing `ct-bot`
classifier prefix matches it — no classifier change this round.

The `system_prompt` is the body of `ct-bot/docs/agents/compose.md` copied
**verbatim**, flush-left. Unlike the T2–T4 sources, `compose.md` has **no
title line** (it opens directly with the role sentence), so none is added —
the ticket's "a title line only if the source file has one". The
`user_prompt` is a one-line fixture ("T5 fixture turn — not a live host
turn. Begin.") that exists only so the file evaluates; it is not the role,
not a live host turn, and does not announce T7.

## Path retargets

**None.** The compose source carries no mock-harness paths, no file-open
instructions, and no `spawn_agent` mentions. The mechanical diff below is
the proof: zero changed lines.

## Output contract

Compose returns **JSON messages** — `{messages: [{type: "text", text}]}` —
one parent enrolment SMS notice per assembler item, in the given order,
from **name, course, and dob only**, each notice ending **"(Not sent.)"**,
no fees, no jargon, plain language for parents, and rule 8's no-shortening
of later items — verbatim from the source. All of this is the file's own
rules 1–8, unchanged.

## Deliberately not done here

- No suggestions agent; no edit to `main.exs`, `sanitize.exs`,
  `parse.exs`, or `validate.exs`.
- No spawn wiring; the task_prompt-vs-blackboard decision stays T7's.
- No registry row, no matrix file, no dormant flip — ct-bot has been
  active since T1 and its registration surfaces are unchanged.

## Done-check record

- `mix run --eval` remains unrunnable here (harness mirror without
  `deps/`; Hex unfetchable) — the milestone's T5 command stays owed where
  the harness runs. The same T1–T4 substitute ran instead: plain `elixir`
  against a stub carrying the real `Aetheris.RunConfig` defstruct —
  the file evaluates; run_id `ct-bot-compose-…`, `tools: []`, label
  "CT-Bot Compose Agent".
- Mechanical diff of the embedded `system_prompt` against
  `ct-bot/docs/agents/compose.md`: **zero changed lines** (35 in, 35 out).
- Classifier guard: the new declared label classifies under the existing
  `ct-bot` prefix; `tests/test_run_classifier.py` green.
