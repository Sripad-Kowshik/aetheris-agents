# BL-287 — Owner-threaded runs (design brief)

**Status:** closed 2026-10-06. T1 and T2 landed in the harness —
`4dc1b5b` (optional owner_id/thread_id stamps on agent-file runs) and
`91d6a85` (the `threads` store table, `POST /api/playground/threads`,
and the two §3.9 reads) — with the four done-when arms discharged; the
closure record is appended in `docs/evidence/BL-287.md`, and the row is
closed in the archive (`state: done`, `disposition: fixed`). One
**C1/C2 deviation, noted in the closure record**: T2 added
`POST /api/playground/threads` (§3.8) — a third route this brief had
left to T1's STOP list without naming it.
**Type:** design brief. A contract for the implementation cc:prompt,
cited by item number.
**Date:** 2026-10-06
**Row:** BL-287 (open, `docs/backlog-2026-06.md` §Harness).
**Evidence:** `docs/evidence/BL-287.md` (the finding; cites the survey).
**Citations:** `H` = harness `aetheris` at `327a30e`; `A` =
`aetheris-agents` at `c733910`.
**Docs-first:** this brief is T0; T1 is a harness-repo commit. No route
path is named here — that is the implementation ticket's.

---

## 1. Scope

The capability BL-287 files: **a host can keep a chat thread for an owner
across machines.** A run started from an agent file can be stamped with
the owner and thread it belongs to; the owner's threads can be listed;
the stamp rides the existing BL-284 route, whose two-field request gains
exactly two optional fields. The store is the harness, not the browser —
one SQLite file, no replication, no second writer (the evidence file's
multi-machine reading; BL-269 is a different row).

## 2. Tranches

### T0 — this document (filed)

The row, the evidence file, and this brief, each citing the others. No
code, no route, no harness edit.

### T1 — the implementation ticket (harness commit)

- T1.1 Two optional request fields on the agent-file-runs route:
  `owner_id`, `thread_id` (§3 C2). Absent fields change nothing (C1).
- T1.2 The stamp: after `Aetheris.start_run` succeeds, write both values
  onto the run row (`upsert_run/2`, `store.ex:160@H`) (C2). Carried on
  the run row; the thread-metadata table is only for title and ordering
  (store note).
- T1.3 Stamp failure: log it, still `202` with the `run_id` (C3).
- T1.4 Two new read routes, `GET`: the owner's threads, and a thread's
  runs — same bearer as every playground route (C5, C6). Paths are named
  in T1, not here.
- T1.5 The contract docs: `docs/aetheris/playground-api.md` §3.7 gains
  the two fields and any new routes are documented there (C7) — amended
  by T1, not this brief.
- T1.6 Tests: the done-when's four arms, plus stamp-failure-still-202
  with the failure logged.

## 3. Contract

**C1 — Absent thread fields: current behaviour.** A POST without
`owner_id`/`thread_id` is today's call and today's `202` with `run_id`.
Nothing about the existing BL-284 flow changes.

**C2 — Present `owner_id` + `thread_id`: stamp the run.** After
`start_run` returns success, the run row is stamped with both values
(`upsert_run/2`). The stamp happens after the run exists, never blocks on
the LLM loop, and never alters `status`, `config_json`, or any existing
column.

**C3 — Stamp failure: log and still 202.** A failed stamp (store
unavailable, error return from `upsert_run/2`) is logged with the
`run_id` and the reason; the response is still `202` with the `run_id`.
The run started; the stamp is metadata, not the run's success. No
compensation, no retry loop in the request path.

**C4 — `system_prompt` stays in the .exs.** The request never carries
it — BL-284 C1.1 is unchanged and restated here for the extended field
list: the request is `agent_path` + `user_prompt`, plus exactly the two
optional stamp fields. No third ad-hoc key is created by this capability;
only these two names join the known list.

**C5 — `owner_id` is caller-asserted scoping, not an auth claim.** It
names a scope the caller wants the run grouped under; it grants nothing,
identifies nobody, and is not checked against any identity. `AuthPlug`
is unchanged: the same bearer token gates every playground route, and a
caller stamps and lists under whatever `owner_id` string its token
already entitled it to reach. "That owner's threads" in the row's
done-when means the threads named by the `owner_id` on the request, not
"the authenticated principal" — there is no principal beyond the shared
bearer signer.

**C6 — List and get are new read routes, same bearer.** `GET` the
owner's threads (with titles and ordering if the thread-metadata table
exists); `GET` one thread's runs. Read-only, open to the same bearer as
§3.4@H, never to an unauthenticated caller, and never returning
`config_json` (the C8.4@H rule carries over: frames and listings carry
no config).

**C7 — Docs ownership.** `docs/aetheris/playground-api.md` is amended by
the implementation ticket, not here — the C13@H rule. The capabilities
appendix (`docs/aetheris/harness-capabilities-appendix.md@H`) is likewise
an implementation-ticket edit if T1 wants the survey to know the fields.

**Store note.** The `runs` table can gain columns through the established
ensure-column pattern — one guarded `ALTER TABLE … ADD COLUMN` at a time,
SQLite having no `ADD COLUMN IF NOT EXISTS`
(`lib/aetheris/store.ex:1234-1309@H`; the runs table already gained
`label` this way, `ensure_runs_label_column` after its DDL at
`:1048@H`). Estimated: two `TEXT` columns, nullable. A separate
thread-metadata table (thread_id → title, ordering) exists only if it
earns it — it holds nothing a run does not; T1 decides, and an
ensure-table for it follows the store's DDL pattern. No second database,
no migration beyond the one file.

## 4. Scout facts relied on

- F1 The runs table schema has no thread/owner/session/conversation
  column: `run_id, status, config_json, started_at, finished_at, label,
  terminal_seq` — `lib/aetheris/store.ex:1033-1046@H`.
- F2 Zero hits for `thread|owner_id|session` in `lib/aetheris/api/` at
  `H` (grep).
- F3 The closed schema refuses a third key — `playground-api.md`
  §3.3@H's unknown_field rule and BL-284 C1.2; §3.7@H is the two-field
  request.
- F4 `upsert_run/2` is the established run-row write path and takes a
  map of attrs — `lib/aetheris/store.ex:160-162@H`.
- F5 The ensure-column pattern is established and already used on the
  runs table itself (`label`) — `lib/aetheris/store.ex:1234-1309, 1048@H`.
- F6 SQLite is the only DB — one Exqlite file behind a single-store
  GenServer (BL-266 F1, `store.ex@H`); a non-terminal run is live only on
  its hosting VM (BL-266 C1.1/C6) — the one-node fact under the
  multi-machine reading.
- F7 The survey (`docs/aetheris/harness-capabilities-appendix.md@H`)
  carries no owner/thread/session concept on the run surface.
- F8 BL-284 is closed with the route live (row `2026-10-06`, disposition
  fixed; live run `ct-bot-main-4IeDhw` cited in its brief status).

## 5. Open for plan STOPs

- The two read routes' paths (this brief deliberately names none).
- The stamp column names (`owner_id`/`thread_id` as columns vs one
  thread key), and which thread-metadata table fields, if any.
- List pagination and the GET response shape (title/ordering source if
  the metadata table is not built).
- Whether the stamp fields also apply to the legacy
  `POST /api/playground/runs` (inline-prompt route) — out of T1's named
  surface; T1 decides or leaves it open.
