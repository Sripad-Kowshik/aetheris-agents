# BL-284 — Start a run from an existing agent file over HTTP (design brief)

**Status:** closed 2026-10-06. T1 landed in the harness (`POST
/api/playground/agent-file-runs`), and the live check passed: POSTing
`ct-bot/agents/main.exs` with only a user turn returned `202` with run
`ct-bot-main-4IeDhw`, whose `prompt_built` carried the supplied
`user_prompt` and the file's tools — the C9 test, discharged on a live
run. Row BL-284 closed 2026-10-06 (disposition: fixed). The evidence
file's "live curl owed" sentence is discharged by that run and left
unedited there by the closing ticket's instruction.
**Type:** design brief. A contract for the T1 cc:prompt, cited by item
number (`§3 C2`).
**Date:** 2026-10-06
**Row:** BL-284 (open, `docs/backlog-2026-06.md` §Harness).
**Evidence:** `docs/evidence/BL-284.md`.
**Citations:** `H` = harness `aetheris` at `cf90264`; `A` = `aetheris-agents`
at `20ca539`.
**Docs-first:** this brief is T0; the route is T1 and is a harness-repo
commit — nothing in this ticket edits `../aetheris`.

---

## 1. Scope

The capability BL-284 files: **an HTTP client can start a run from an
existing .exs agent file and supply only the user turn.** Today the only
POST-that-starts-a-run (`POST /api/playground/runs`, §3.3@H) requires
`system_prompt` inline and a closed field list with no `agent_path`
(§4 F1, F2), and `load_agent_file/1` is reachable only from the CLI
(§4 F3). The population served is every `.exs` agent file in the agents
checkout — ten use cases, 36 files at `A` (§4 F7).

In scope for T1: loading a **`%RunConfig{}`** file, overlaying the
request's `user_prompt`, starting the run, returning `202` with a
`run_id`. Out of scope for T1, each a named open question (§5): loading
`%OrbConfig{}` files over HTTP; a cancel endpoint; any second transport —
the caller consumes the streams BL-266 landed (§4 F6).

## 2. Tranches

### T0 — this document (filed)

The finding (evidence file), the row (open backlog §Harness), and this
brief, each citing the others. No code, no route, no harness edit.

### T1 — the harness route

- T1.1 A `POST` route on the existing `/api/` Bandit instance
  (`Aetheris.API.Server`), auth-gated per §5@H like every
  `/api/playground/*` route (§3 C7).
- T1.2 Request body: `agent_path` (string, required) and `user_prompt`
  (string, required) — and nothing else (§3 C1).
- T1.3 Path confinement: `agent_path` resolves only inside a **configured
  agents root**; escape by `..` segments, absolute paths outside the root,
  or symlink escape is refused before any run starts (§3 C2).
- T1.4 Loading: `RunHelpers.load_agent_file/1`
  (`lib/aetheris/cli/commands/run_helpers.ex:357@H`) — the same loader the
  CLI orchestrator (`agents/orchestrator.exs@A`) already uses; no second
  loader (§3 C3). A file evaluating to `%OrbConfig{}` is refused 422 in
  T1 (§5).
- T1.5 Overlay: the request's `user_prompt` replaces the loaded file's
  `user_prompt`; every other field of the loaded config is authoritative
  and cannot be set from the request — no key for it exists (§3 C4).
- T1.6 Start and respond: `Aetheris.start_run(config)` (the §8@H normative
  flow's own call) → `202 {"run_id": "..."}` in §3.3@H's envelope (§3 C5).
- T1.7 Consumption: the caller follows the run on the existing SSE or
  WebSocket event streams (§3.5/§3.6@H) — no new transport, no new frame
  kind (§3 C6).
- T1.8 Docs: `docs/aetheris/playground-api.md` gains the endpoint's
  section (the C13@H ownership rule: the API's normative contract lives
  there) (§3 C8).
- T1.9 The named test (the row's done-when): the run's `prompt_built`
  event carries the **supplied** `user_prompt` and the **file's** tool
  list; the request body carried no `system_prompt` (§3 C9; the event's
  payload shape at §4 F4).

## 3. Contract

**C1 — Request.** The body is exactly two fields: `agent_path`,
`user_prompt`.
- C1.1 `system_prompt` is not a request field. Its presence is a refusal
  (unknown_field under the closed schema, or a dedicated forbidden_field
  entry) — the file on disk is the system prompt's only source. The
  request never overrides role text.
- C1.2 Any third key is refused — closed schema, per §3.3@H's
  unknown_field rule. No pass-through of provider/model/tools/max_steps:
  a file-started run is configured by its file.

**C2 — Path confinement.** `agent_path` is resolved against a configured
agents root and must stay inside it.
- C2.1 Resolution happens before `load_agent_file/1` is called; a path
  that escapes the root (`..`, absolute-outside, symlink) is a 422
  refusal — the trust model is §7@H's: the API must not become an
  arbitrary-file read-and-execute primitive for token holders.
- C2.2 The config key carrying the root is a T1 plan decision (§5).

**C3 — Loading.** `RunHelpers.load_agent_file/1` (`run_helpers.ex:357@H`)
is the only loader; T1 does not fork it and does not `Code.eval_file`
from the route.
- C3.1 A file evaluating to `%OrbConfig{}` is refused 422 in T1 with a
  reason naming the file's shape (§5 open question).

**C4 — Overlay.** The request's `user_prompt` overlays the loaded config's
`user_prompt` field (a struct update after load, before `start_run`).
- C4.1 The file's `system_prompt` is never merged or concatenated with
  anything from the request.
- C4.2 The file's `label`, `tools`, `max_steps`, `context_strategy`,
  `sandbox_path`, `provider`, `model` are authoritative.

**C5 — Response.** `202` with `{"run_id": "..."}`, the §3.3@H envelope;
the §8@H normative submission flow is the template with
`RunConfig.from_map` replaced by the file load. Errors use the §4@H
envelope: `401` (§5@H), `404` (path not under the root / file not found —
the two cases are distinguished in the message, not the code, in T1),
`422` (orb-shaped file, escape refused, missing field), `400` (malformed
JSON).

**C6 — Consumption.** The caller uses the existing event streams
(§3.5/§3.6@H). Run resolution, auth, cursor and frames are theirs and do
not change. BL-284 adds no stream surface.

**C7 — Auth.** Bearer token per §5@H, identical to every
`/api/playground/*` route. No new token, no new scope.

**C8 — Docs ownership.** The endpoint's normative contract lands in
`docs/aetheris/playground-api.md` (the C13@H rule); Rig-side docs change
only if Rig grows a consumer, which is not T1.

**C9 — The named test.** The row's done-when test, stated fully: start a
run from a file whose `tools:` is non-empty and whose `user_prompt:` is
`X`, POSTing `user_prompt: "Y"`. The run's first `prompt_built` event
carries `user_prompt == "Y"` (the overlay) and `tool_schema ==` the
file's `tools` (the file's), and the request body contained no
`system_prompt` key. The file's own `system_prompt` appears in
`prompt_built.system_prompt` — it came from the file, not the request.

## 4. Scout facts relied on

- F1 `POST /api/playground/runs` requires `sandbox_id`, `provider`,
  `model`, `system_prompt` — `docs/aetheris/playground-api.md` §3.3
  "Required fields"@H.
- F2 The API is closed-schema; unrecognised keys (no `agent_path` in the
  known client-settable list) produce a 422 `unknown_field` — §3.3
  "Unknown fields"@H.
- F3 `load_agent_file/1` is CLI-only: `git grep -n "def load_agent_file"
  lib/` at `H` returns one hit, `lib/aetheris/cli/commands/run_helpers.ex:357`;
  `lib/aetheris/api/` defines none.
- F4 `prompt_built`'s payload carries `system_prompt`, `user_prompt`,
  `tool_schema => config.tools` — `lib/aetheris/execution/loop.ex:170-183@H`;
  inclusion is `store_prompts`-gated, default `true`
  (`lib/aetheris/run_config.ex:59-62@H`).
- F5 `RunConfig.from_map/3` exists (`lib/aetheris/run_config.ex:206@H`)
  and is NOT T1's construction path: the request is two fields, not a
  config map; the config comes from the file.
- F6 The event streams exist and are normative — §3.5/§3.6@H (BL-266,
  closed 2026-09-20).
- F7 The served population: `.exs` files evaluating to `%RunConfig{}`
  or `%OrbConfig{}` structs — this repo at `A` (36 agent files across ten
  use cases).
- F8 The 202/`run_id` envelope and the async start are established —
  §3.3@H response and §8@H flow.

## 5. Open for plan STOPs

- The concrete route path (this brief deliberately does not name it).
- The agents-root config key's name and default value.
- Whether `agent_path` is repo-relative to the configured root only, or
  also accepts the use-case subdirectory form.
- `%OrbConfig{}` files over HTTP (refused in T1; a later tranche would
  need the multi-agent start path and a peer-id story that no OrbConfig
  today has over HTTP).
- Whether the 202 response echoes the resolved label (useful for the
  run list's classifier); default: echo nothing beyond `run_id`.
