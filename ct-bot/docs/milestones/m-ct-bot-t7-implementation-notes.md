# T7 Implementation Notes — ct-bot main.exs wired

**Date:** 2026-10-06 · **Touches:** `ct-bot/agents/main.exs` (edited only),
`ct-bot/docs/milestones/m-ct-bot-t7-implementation-notes.md` (new)

---

## The wire

`main.exs` gains exactly one struct change — `tools: []` →
`tools: ["spawn_agent", "wait_for_all"]` — and a `## Wire — the buddy_parse
chain (T7)` section appended to its system prompt **after** the verbatim
`main.md` body (the body itself is untouched; the mechanical diff against
`main.md` shows the wire section as added lines and zero changed body
lines). Label stays "CT-Bot Main Panel Agent"; run_id prefix stays
`ct-bot-main-`.

The wire section says, and only what the ticket lists plus the harness's
own mechanics:

- fire only for a buddy_parse / `student.enrol.parse` turn — every other
  turn answers per the main.md rules and spawns nothing;
- hop 1: sanitize role body + the raw notes (`buddy.text`) + the field list;
- hop 2: parse role body + hop 1's `final_message` (sanitized lines) + the
  field list;
- hop 3: validate role body + the records array from hop 2's `final_message`
  (the `surface.records` JSON) + the field list;
- a failed wait stops the chain — report which hop failed and that the rest
  did not run; no retry;
- compose and suggestions are NOT hops in this chain.

## The channel, and the rejection

**`final_message` is the channel.** `wait_for_all` returns the child's
last text; each hop's result is read from it, one hop at a time. A temp
file is named only as the fallback for an empty `final_message` — the file
is never the design.

**Blackboard was rejected.** The task_prompt-vs-blackboard decision,
open since T1, closes here: `spawn_agent` + `final_message` carries the
payload hop-to-hop with no OrbConfig, no pre-minted peer ids, and no
shared key protocol — blackboard would have required all three (the
`at1cmd.exs` precedent needs ids fixed at eval time and keys agreed
beforehand), for a chain that is strictly sequential anyway.

## How the role bodies travel

The parent has no `read_file` tool and `spawn_agent` has no payload field,
and `spawn_agent` does **not** load `ct-bot/agents/sanitize.exs` and the
other standalone wraps — those stay standalone. So the three role bodies
are read at **eval time** from their source files
(`ct-bot/docs/agents/{sanitize,parse,validate}.md`) by a `role_source`
closure — the `at1cmd.exs` skill-hint pattern — raising at eval time if a
source file is missing, and interpolated verbatim into the wire section
between `=== … ROLE BODY ===` markers. Each hop's `task_prompt` copies its
role body plus the turn data; `task_prompt` becomes the child's
`system_prompt` and the child's `user_prompt` is "Begin." — both facts
stated in the wire section as harness mechanics, not choices.

Two safety checks ran before embedding: none of the three bodies contains
`#{` (no interpolation injection) or `"""` (no heredoc break).

**T7 fix — `max_steps` raised 4 → 12.** The wired chain needs six tool
rounds (three spawn_agent calls plus three wait_for_all calls) plus the
final JSON reply; T1's `max_steps: 4` — inherited from the unwired
responder shape — could not finish it. Old value 4, new value 12; nothing
else in the struct or the wire section changed.

One incidental fix inside the same file: the `user_prompt` fixture said
"the context bag arrives with T7" — stale the moment T7 landed — and now
reads "T7 fixture turn — not a live host turn. Begin." Still a fixture;
not a role; not a live host turn.

## Deliberately not done here

- No rewrite of `sanitize.md`, `parse.md`, or `validate.md`; no edit to
  `sanitize.exs`, `parse.exs`, `validate.exs`, `compose.exs`, or
  `suggestions.exs`.
- Compose and suggestions stay out of the chain.
- No OrbConfig, no pre-minted peer ids, no blackboard keys.
- No registry row, no matrix file, no dormant flip; no harness commit —
  the sprint.sh case remains the later harness commit.

## Done-check record

- `mix run --eval` remains unrunnable here (harness mirror without
  `deps/`; Hex unfetchable) — the milestone's T7 command stays owed where
  the harness runs. The same T1–T6 substitute ran instead: plain `elixir`
  against a stub carrying the real `Aetheris.RunConfig` defstruct — the
  file evaluates; `tools: ["spawn_agent", "wait_for_all"]`, label
  "CT-Bot Main Panel Agent", run_id `ct-bot-main-…`, and the assembled
  prompt measures ~26k chars (main.md body + wire section + the three
  role bodies).
- Mechanical diff of the prompt's `main.md`-body region against
  `ct-bot/docs/agents/main.md`: **zero changed lines** (147 in, 147 out;
  the wire section appears only as added lines after the body).
- Mechanical diff of each interpolated role body against its source file:
  **zero changed lines** for all three.
- Classifier guard: label unchanged, `tests/test_run_classifier.py` green.

---

## T7 follow-up — a finished child was reported as timed out (2026-10-06)

**Symptom.** On a live workspace parse turn the parent reported "The
sanitize hop timed out and did not complete" and stopped: no parse run
exists. The child trajectory (`run_dvrE-g`) shows the opposite outcome —
the sanitize child reached `agent_finished` in about 1.5 s carrying the
three schema lines. The hop completed; the parent did not read the
completion.

**Diagnosis.** The T7 wire section pinned the channel but not the call's
shape: it never said what `timeout_ms` to pass, and it described
`wait_for_all`'s return as if it were the text itself. The harness fact
is that the result is one map per run — `run_id`, `status`,
`final_message`, `steps` (`lib/aetheris/agent/server.ex:1046-1064@H`,
`build_run_result/3`; `final_message` is the last `llm_responded` text
event's `raw_response`). Left to improvise both the timeout and the read,
the parent LLM misread a finished child as a timed-out one.

**Fix (the wire section only; no agent file touched, no `max_steps`
change).** The wait bullet now says: pass `timeout_ms: 120000` explicitly
per hop (the `at1cmd` message-wait precedent, generous against the
observed 1.5 s); read the result map's `final_message` **beside**
`status`; a hop with a terminal status is finished — read
`final_message` and continue, never report it as timed out; report a
timeout only when the wait reports the run timed out AND its status is
not terminal; the temp-file fallback stays the empty-`final_message`
fallback on a finished hop. `max_steps` stays 12 — the missed result was
a read defect, not a step deficit, and raising it would have hidden the
miss.
