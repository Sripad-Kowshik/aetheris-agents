# T6 Implementation Notes — ct-rpg rpg-main.exs wired (the gate chain)

**Date:** 2026-10-28 · **Touches:**
`ct-rpg/agents/rpg-main.exs` (wired), 
`ct-rpg/docs/milestones/m-ct-rpg-t6-implementation-notes.md` (this file).
**No harness edit. No child edited. No new agent. Not committed.**

---

## The wire (this ticket's decision — it discharges T3/T4/T5's open note)

The parent's WIRE section is now the real chain. Recorded facts, as the
ticket requires:

- **Hop order (four hops, one at a time):**
  1. gate 0 preflight
  2. gate 2 migrate
  3. gate 3 verify (parity)
  4. gate 4 api

  Spawn a hop, wait for it, read its result, then spawn the next — never in
  parallel, never the next hop before the previous one has finished.

- **The field read from wait_for_all:** the wait returns one map per run —
  `run_id`, `status`, `final_message`, `steps`. The parent reads
  **`final_message`** as the channel (the hop's last text) beside
  **`status`**, which gates the chain:
  - a **terminal** status (for example "done") is a finished hop — read
    `final_message` and continue (a finished hop is never reported as
    timed out);
  - a **non-terminal** status is a failed chain — report which hop failed
    and that the rest did not run, and stop; do not retry, do not spawn
    the next hop.

- **A failed hop stops the chain.** Both failure arms — a non-terminal
  wait, and a finished hop whose `final_message` reports its gate FAILED
  (a non-zero exit code, a `[FAIL]` / error line, an explicit failure
  report) — produce the same behaviour: report which hop failed, do not
  spawn the rest, do not retry. This is the spec's own
  stop-on-first-failure rule applied to the spawn order.

- **Spawn is now decided.** T3/T4/T5 each recorded "spawn not decided";
  T6 decides it: `spawn_agent`'s `task_prompt` carries exactly two things
  — the child's role body and the parameter. `spawn_agent` does not load
  the standalone wraps (the ct-bot T7 finding), so the role bodies travel
  inside the parent's prompt and are copied into each task_prompt.

## The role bodies: the children's own marked sections, extracted at eval time

The parent does not restate the gate rules. At eval time it extracts each
child's role body — the marked gate section from the child's own
`system_prompt` — by slicing between that child's `=== GATE n — … ===` /
`=== END GATE n — … ===` markers and embeds the four bodies between
equally named blocks inside the wire (`PREFLIGHT` / `MIGRATE` / `VERIFY` /
`API ROLE BODY`). The extraction **fails fast at eval time**: a missing
wrap or an unpaired marker raises instead of producing a half-prompt (the
at1cmd skill-hint pattern, as in ct-bot's T7 wire). Done-when proof: each
embedded body is byte-identical (modulo outer trim) to the marked section
in its child — the children are the single source; the parent copied, and
restated nothing.

**Parameter passthrough:** each task_prompt's second element is one line —
`Migration repo root: <the value from the user prompt>` — exactly the
parameter every child's invocation contract already expects. The parent
never invents, substitutes, or hard-codes a path; if the user prompt
carries no value, it runs no hop and says so.

## What changed in the file (and what did not)

- The spec body (`runbook-gates.md`, 163 lines) remains byte-for-byte
  identical — re-diffed after the rebuild (the file was reassembled by
  `cat` so the copy could not drift).
- The T1 wire's interim clause — "until the T3–T5 wraps land, the chain
  stops there" — is **deleted**: it is false now, and its replacement is
  the four-hop chain above.
- Wrapper fields unchanged: `run_id ct-rpg-main-…`, `label "CT-RPG
  Migration Gate Orchestrator"`, `mode: :record`, `context_strategy:
  :full`, `overlay_base_dir: nil`, `max_steps: 12` (4 spawns + 4 waits +
  the report fit with headroom), **`tools: ["spawn_agent", "wait_for_all"]`
  — nothing else**, fixture `user_prompt` one line ("T6 fixture turn — not
  a live run. Parameter: migration repo root = `<MIGRATION_REPO_ROOT>`.
  Begin.").
- No child touched, no new agent, no harness edit. Gates 1 (services) and
  5 (tests) remain non-hops — the chain is exactly the milestone's four.

---

## Done-check record

- **Evaluation, stub against the RunConfig field list** (the harness
  checkout has no `deps/`; the T0+T1 stub precedent): the file evaluates
  under plain `elixir` (1.18.5) — including the four eval-time
  extractions — and yields `run_id ct-rpg-main-…`, `label "CT-RPG
  Migration Gate Orchestrator"`, `tools ["spawn_agent", "wait_for_all"]`,
  `max_steps 12`, prompt of 26,141 chars / 301 lines, fixture
  `user_prompt` as above.
- **Wire proofs (mechanical):** the four hop lines appear in order
  (preflight → migrate → verify → api); the sentences "A failed hop stops
  the chain", "Do not retry", "NON-TERMINAL status is a FAILED CHAIN",
  the terminal-status rule, "ONE at a time", the parameter-passthrough
  line, and "You do not restate the gate rules" are all present; each of
  the four embedded role bodies is byte-identical (modulo outer trim) to
  the marked section in its own child.
- **Verbatim proof on the spec copy:** re-diffed after the rebuild —
  byte-for-byte identical to `ct-rpg/docs/specs/runbook-gates.md`.
- `check_run_classifier.py`: PASS (label unchanged, classifies under the
  existing `ct-rpg` prefix).
- `python3 -m pytest ct-rpg/tests/ -q`: 6 passed.
