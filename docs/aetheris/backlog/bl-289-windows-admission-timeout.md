# BL-289 — Windows first-run admission timeout (design brief)

**Status:** T0 filed (this document). T1 not started.
**Type:** design brief. A contract for the implementation cc:prompt,
cited by item number.
**Date:** 2026-10-06
**Row:** BL-289 (open, `docs/backlog-2026-06.md` §Harness).
**Evidence:** `docs/evidence/BL-289.md`.
**Citations:** `H` = harness `aetheris` at `77cb0ab`.
**No harness edit in this ticket** — the row, the evidence, and this
brief are T0; the fix is a harness commit.

---

## 1. Scope

The capability: **a cold first run on native Windows returns 202 inside
the admission window.** Today two 5-second walls — the outer admission
call's effective GenServer default timeout (`admission.ex:182@H`, no
explicit argument) and the worker ready handshake's `after 5_000`
(`worker/client.ex:295@H`) — can be exceeded by Windows process creation
and antivirus scanning of the freshly built worker binary, killing the
run before the loop starts.

**The brief names two candidate fixes as plan STOPs and picks
neither.** They are not mutually exclusive, and the implementation
ticket may take one, both, or a sequenced pair:

- **STOP A — skip-the-worker in admission.** Admission decides capacity
  and starts supervision; it need not synchronously wait for the worker
  handshake. The handshake moves out of the admission path (async inside
  the run's supervision, surfacing a handshake failure as run failure
  data the way post-admission failures already surface), and the outer
  5 s wall stops being on the handshake's critical path.
- **STOP B — raise the timeouts.** The worker handshake keeps its
  synchronous place, with its budget made explicit and the outer
  admission timeout made **strictly longer than the worker handshake**
  (one bounded constant or a config key; the invariant is outer >
  handshake so the two cannot race) — and both budgets documented where
  operators read them.

## 2. Tranches

- T0 — this brief (filed, with the row and the evidence file).
- T1 — the harness implementation: whichever STOP(s) the ticket takes,
  with the done-when's test passing on Windows and the two budgets
  documented if STOP B's arm is taken.

## 3. Contract

**C1 — The behaviour the row closes on.** An agent-file-runs POST that
only lists harness-managed tools returns `202` within the admission
window on Windows — **or** the outer admission timeout is provably
longer than the worker handshake **and both budgets are documented**
(playground/runbook ownership per the C13@H/BL-276 rules). The row
closes on behaviour or on documented walls; the mechanism is T1's.

**C2 — No Unix regression.** Any budget change is additive (an explicit
timeout where the default currently stands, or a moved handshake) and
must not shorten anything today-fitting on Unix. The 30 s tool-call
timeout (`client.ex@H`) is out of scope.

**C3 — Refusal semantics unchanged.** Admission refusals (`:cap_full` et
al.) keep their shapes; a handshake timeout, wherever it lands, stays a
run-visible failure — never an admission "admitted" that silently never
starts a worker.

**C4 — Docs ownership.** The budget(s) end up documented in the same
commit that changes them — `playground-api.md` §3.7/§4 if admission
latency is operator-visible there, else the runbook (BL-276's rule).

## 4. Scout facts relied on

- F1 `GenServer.call(__MODULE__, {:admit_and_supervise, config, origin,
  schedule})` with **no timeout argument** — GenServer's default 5 000
  ms applies — `lib/aetheris/admission.ex:182@H`.
- F2 The worker init handshake requires `{"status": "ready"}` within 5 s
  — `lib/aetheris/worker/client.ex:9-10@H` (documented) and
  `:295@H` (`after 5_000 → {:stop, :worker_init_timeout}`).
- F3 The handshake runs synchronously inside `init/1` — `client.ex:9@H`
  — so a slow start is felt by whoever waits on the run.
- F4 Zero Windows-specific admission/handshake budget anywhere — grep
  over `admission.ex`/`client.ex` at `H` returns no `windows|msys|mingw`
  hits.
- F5 The operator requires native Windows, no WSL — the finding's
  premise, supplied.

## 5. Open for plan STOPs

- **Which STOP(s) to take** — the brief deliberately does not pick:
  skip-the-worker (A), raise-and-document (B), or a sequenced pair.
- If B: the one span or two, constant vs config key.
- If A: where the handshake failure surfaces (run status vs `worker_init_timeout`
  as today) and how admission tests pin the new shape.
