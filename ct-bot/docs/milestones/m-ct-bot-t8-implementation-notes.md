# T8 Implementation Notes — ct-bot title.exs

**Date:** 2026-10-06 · **Touches:** `ct-bot/agents/title.exs` (new)

---

## The two-file shape

A child agent under an existing use case adds exactly two files (the
survey's finding, confirmed by T2/T5/T6): this agent file and this notes
file. Accordingly: **no registry row** — `docs/use-cases.md`'s unit is
the use case directory, not the agent, and ct-bot has had its row since
T0; **no matrix edit** — the section agent regenerates the whole section
by listing the directory at matrix-sprint time, and the `use_case_registry`
arms count the use case, not its agents; **no dormant flip** — the use
case has been active since T1.

The one cross-file obligation a new `.exs` carries is the label: **"CT-Bot
Title Agent"** starts with the `ct-bot` prefix landed in T1 in both Rig
`USE_CASE_PREFIXES` constants, so `tests/test_run_classifier.py`'s
every-declared-label-classifies arm sees it grouped — no classifier
change.

## The wrap

`ct-bot/agents/title.exs` is a single `%Aetheris.RunConfig{}`, the
suggestions.exs wrapper unchanged: `run_id` minted outside the struct
with prefix `ct-bot-title-`, `sandbox_path` from `__ENV__.file`,
`CT_BOT_MODEL`/`AETHERIS_MODEL` env fallbacks, `mode: :record`,
`context_strategy: :full`, `overlay_base_dir: nil`, `max_steps: 4`,
**`tools: []`**, and a one-line fixture `user_prompt` ("T8 fixture turn —
not a live host turn. Begin.") that exists only so the file evaluates.

Unlike T1–T6 there is **no prompt source file** under `docs/agents/` —
the ticket authored the rules directly — so the mechanical zero-diff
property has no counterpart; the file header records that. The prompt is
the ticket's rules, written once here: one short title from the first
user message, **plain text only (no JSON)**, **≤ 40 characters**, **no
quotes**, **no trailing period**, plus the never-invent rule (words from
the conversation only) so a title cannot introduce a subject.

## The host posts the title

This agent **does not save anything and touches no store**: it returns
the title text and finishes. The **host posts it** — it is the host's
thread lifecycle (the panel host that created the thread) that takes the
text and posts it as the thread's title (cf. the `threads` table's
nullable `title` column, BL-287 T2), exactly as it posts form submits
and workspace patches. The agent's only consumer surface is the
`final_message` of its run.

## Deliberately not done here

- No spawn wiring; no thread posting from the agent side.
- No registry row, no matrix file, no dormant flip, no harness edit.
- No prompt source file under `docs/agents/` and no `docs/agents/README.md`
  index change — the six indexed filenames are the operator-supplied
  conversion set (T1–T6), and T8 has no source file to index.

## Done-check record

- `mix run --eval` remains unrunnable here (harness mirror without
  `deps/`; Hex unfetchable) — the same stub-against-the-real-defstruct
  check ran instead (recorded in earlier notes files): the file
  evaluates; run_id `ct-bot-title-…`, `tools: []`, label "CT-Bot Title
  Agent".
- Classifier guard: the new declared label classifies under the existing
  `ct-bot` prefix; `tests/test_run_classifier.py` green.
- ct-bot tests still pass.
