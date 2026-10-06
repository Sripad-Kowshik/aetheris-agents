# T6 Implementation Notes — ct-bot suggestions.exs

**Date:** 2026-10-06 · **Touches:** `ct-bot/agents/suggestions.exs` (new)

---

## The wrap

`ct-bot/agents/suggestions.exs` is a single `%Aetheris.RunConfig{}`, the
T5 wrapper shape unchanged: `run_id` minted outside the struct with prefix
`ct-bot-suggestions-`, `sandbox_path` from `__ENV__.file`,
`CT_BOT_MODEL`/`AETHERIS_MODEL` env fallbacks, `mode: :record`,
`context_strategy: :full`, `overlay_base_dir: nil`, `max_steps: 4`,
**`tools: []`**. The label ("CT-Bot Suggestions Agent") starts with
`CT-Bot`, so the existing `ct-bot` classifier prefix matches it — no
classifier change this round.

The `system_prompt` is the body of `ct-bot/docs/agents/suggestions.md`
copied **verbatim**, flush-left. Like `compose.md`, the source has **no
title line** (it opens directly with the role sentence), so none is added —
the ticket's "a title line only if the source file has one". The
`user_prompt` is a one-line fixture ("T6 fixture turn — not a live host
turn. Begin.") that exists only so the file evaluates; it is not the role,
not a live host turn, and does not announce T7.

## Path retargets

**None.** The suggestions source carries no mock-harness paths, no
file-open instructions, and no `spawn_agent` mentions. The mechanical diff
below is the proof: zero changed lines.

## Output contract

Suggestions returns **JSON only**: `{suggestions: [{label, text}]}` with
**exactly 3 send_message chips** (rule 1), the `payload.text` capability
family allowlist (rule 2), never navigate, never a repeat of the user's
utterance or the just-completed reply, never an invented product area, and
rule 4a's never-suggest-the-current-route — verbatim from the source.
All of this is the file's own rules 1–6, unchanged.

## Deliberately not done here

- No edit to `main.exs`, `sanitize.exs`, `parse.exs`, `validate.exs`, or
  `compose.exs`.
- No spawn wiring; the task_prompt-vs-blackboard decision stays T7's.
- No registry row, no matrix file, no dormant flip — ct-bot has been
  active since T1 and its registration surfaces are unchanged.

## Done-check record

- `mix run --eval` remains unrunnable here (harness mirror without
  `deps/`; Hex unfetchable) — the milestone's T6 command stays owed where
  the harness runs. The same T1–T5 substitute ran instead: plain `elixir`
  against a stub carrying the real `Aetheris.RunConfig` defstruct —
  the file evaluates; run_id `ct-bot-suggestions-…`, `tools: []`, label
  "CT-Bot Suggestions Agent".
- Mechanical diff of the embedded `system_prompt` against
  `ct-bot/docs/agents/suggestions.md`: **zero changed lines** (32 in,
  32 out).
- Classifier guard: the new declared label classifies under the existing
  `ct-bot` prefix; `tests/test_run_classifier.py` green.
