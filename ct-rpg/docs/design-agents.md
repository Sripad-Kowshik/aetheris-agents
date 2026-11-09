# ct-rpg — Design Doc: the agents' side of the migration

> Companion to `ct-rpg/docs/design-migration.md`, which describes the migration
> repository (`r2pg-migration/`) as it actually behaves. This document describes
> what the four ct-rpg agents and their parent own, what they deliberately leave
> to that repository's scripts, and how a live run is invoked. It describes; it
> does not change anything.

---

## 1. Purpose

The ct-rpg agents orchestrate four fixed gate commands that live in the
migration repo. They do not invent scripts, mappings, or collection names:
the migration logic lives entirely in `r2pg-migration/scripts/migrations/*.py`
(30 fixed, one-per-collection ETL scripts with hardcoded field maps) plus the
two post-SQL files, exactly as `design-migration.md` §1 states — "the repo
does not generate migrations". Each agent's entire authority is one command
string, one parameter set, and one reply shape; the gate's meaning comes from
the scripts' own outputs (exit codes and marker lines), never from the
agent's judgement. The parent (`ct-rpg/agents/rpg-main.exs`) owns only the
order of the gates and the decision to stop.

---

## 2. What the agents own

**The parent wire** (`ct-rpg/agents/rpg-main.exs`). The system prompt is the
wire section only — no spec text travels in it. It owns:

- Hop order: hop 1 gate 0 preflight → readiness check → hop 2 gate 2 migrate
  → hop 3 gate 3 verify → hop 4 gate 4 api. One hop at a time; never the next
  before the previous has finished. Gates 1 (services) and 5 (tests) are not
  hops.
- Stop-on-first-failure, with pinned detection: a hop is FAILED when its
  `final_message` contains the word "failed" as the verdict or its quoted
  exit code is anything other than 0; a `[FAIL]` string inside a successful
  run's quoted output is not a failure. A terminal wait with an empty
  `final_message` is FAILED. A `spawn_agent` error or a missing run_id is
  FAILED. On any of these: report which hop failed and stop; no retry.
- The services readiness check between hop 1 and hop 2, run by the parent
  itself: `curl <API base>/health`, pass = exit 0 and the response contains
  "Healthy"; anything else stops the chain before hop 2. Services are never
  started by the agents.
- The SUCCESS summary block, emitted only after a clean hop 4:
  `### Onboarding Status: SUCCESS` with PASS lines for gates 0/2/3/4 and the
  scope line "Gates 1 (services) and 5 (tests) are not hops in this
  milestone." The block is earned, never assumed; no teardown step.
- Hop spawn parameters: `tools: ["run_command"]`, `max_steps: 6`,
  `timeout_ms: 300000`; the wait is also `timeout_ms: 300000`, passed
  explicitly.
- The task_prompt recipe: each hop's prompt is exactly the child's role text
  (extracted, see below) plus its parameter lines — hops 1–3 get
  `Migration repo root: <the value from the user prompt>`; hop 4 gets that
  plus `API base: <CT_RPG_API_BASE>` and `Fee-tx body: <CT_RPG_FEE_TX_BODY>`.

**The four child invocation contracts** (`ct-rpg/agents/rpg-preflight.exs`,
`ct-rpg/agents/rpg-migrate.exs`, `ct-rpg/agents/rpg-verify.exs`,
`ct-rpg/agents/rpg-api.exs`). Each system prompt is the contract only — the
command, the parameter it expects, and the reply shape:

- preflight: `bash scripts/verify-prerequisites.sh`, exactly once, working
  directory = the supplied migration repo root; reply quotes the script's
  `[PREFLIGHT PASS]` or `[FAIL]` line plus the exit code.
- migrate: `set -o pipefail; docker compose run --rm rpg-migrator --all | tail -n 80`
  (the tail keeps the end of the long result; the pipefail keeps the exit
  code the migrator's), `timeout_ms: 300000`; reply quotes the orchestrator's
  `[=] MIGRATION SUMMARY` line when visible, else the last visible line —
  and a `[!] Warning during post-migration SQL execution` in the tailed
  output fails the gate even at exit 0.
- verify: `docker compose run --rm --entrypoint python rpg-migrator
  verify_raven_to_postgres.py`, once; reply quotes the verifier's
  `[SUCCESS]` line or its `[FAILURE] DATA PARITY ISSUES DETECTED` line plus
  the exit code.
- api: three commands, each ending `-w "\n%{http_code}"` so the HTTP status
  lands on its own last stdout line — the two reads
  (`<API base>/api/stu/student?limit=2`, `<API base>/api/feeTx?limit=2`) and
  the write (`curl -X POST -H "Content-Type: application/json" -d '<the
  body>' <API base>/api/feeTx`). Pass rule: exit 0 AND status 200 for the
  reads, 200 or 201 for the write. The reply quotes, per curl, the exit code
  and at most the last 80 characters of the last non-empty line — never the
  full JSON.

**The eval-time role-text extraction** (`gate_role` in
`ct-rpg/agents/rpg-main.exs`). The parent reads each child's file at eval
time, slices out the child's own `system_prompt` (its invocation contract),
and embeds the four texts between named ROLE TEXT markers in the wire. It
fails fast at eval time on a missing wrap or an unterminated heredoc.
Nothing is hard-coded in the parent; the children are the single source of
their own contracts.

**The env-var seam.** Three variables, read at eval time, never hard-coded:

- `CT_RPG_SANDBOX_PATH` — the run's sandbox; falls back to the `ct-rpg/`
  directory beside the parent file when unset or empty.
- `CT_RPG_API_BASE` — hop 4's API base (and the readiness check's target).
  Unset or empty becomes a MISSING marker: the wire reports it and hop 4
  does not run; hops 1–3 still do.
- `CT_RPG_FEE_TX_BODY` — hop 4's demo fee-tx body, passed through untouched.
  Unset or empty: MISSING marker, hop 4 does not run.

The model/provider fallbacks (`CT_RPG_MODEL` || `AETHERIS_MODEL`,
`AETHERIS_PROVIDER`) follow the same eval-time pattern.

---

## 3. What the agents leave to the scripts

Per `design-migration.md` §3 and §5: the migration logic is entirely the
scripts' — 30 fixed per-collection ETLs with hardcoded field maps and table
names, the two post-SQL files, the verifier's 42-pair audit, the API's fixed
payload shapes. The agents do not:

- **choose modules** — the only migration command is `--all`; `--module` is a
  human-side tip and would break gate 2's "42 tables" criterion (§5.5);
- **write SQL or new scripts** — adding a domain is a code change in the
  migration repo, not an agent action (§5.2);
- **reshape the fee-tx body** — the POST body is fixed verbatim and arrives
  via `CT_RPG_FEE_TX_BODY`; the child is told not to invent or reshape it,
  because the ids are dataset-coupled and dangling references persist
  silently (§5.3, §7.10);
- **start services** — `docker compose up -d --build rpg-api` is the
  migration design's only service-starting command (§5.4), and the ct-rpg
  chain does not invoke it at all: services must already be up, and the
  readiness check proves it or stops the chain;
- **invent success strings or verdicts** — every marker line the children
  quote (`[PREFLIGHT PASS]`, `[=] MIGRATION SUMMARY`, `[SUCCESS]` /
  `[FAILURE]`, the HTTP status codes) is the scripts' own output, quoted
  verbatim with the exit code (§5.8).

Everything else the gate needs — module registry order, identity derivation,
enum transforms, parity semantics, the API's response shapes — lives in the
scripts and is described in `design-migration.md` §2–§4.

---

## 4. Differences from the migration repo

| item | migration repo (`design-migration.md`) | ct-rpg agents |
|---|---|---|
| Who owns the command string | `agent_runbook.md` names the four `docker compose` gate commands and the host-side checks (§6); the operator types them | each child's invocation contract owns its exact command string; the parent owns none of them (it only spawns and waits) |
| Success criterion | the runbook's criteria, two of which are unsatisfiable as worded (the gate-2 criterion string is never printed — §7.5; "valid JSON array" vs the `{"data":[…]}` envelope — api-verification.md §4 open item 1) | the children pass on the scripts' real, observable signals: exit code, the summary/SUCCESS lines, and — for the api hop — the HTTP status captured with `-w` |
| Who handles a non-zero exit | the runbook's global stop-on-error rule; inside `migrate_all.py` there is no stop-on-first-failure (children continue, exit 1 at the end) | the parent wire: a FAILED hop (non-zero quoted exit, "failed" verdict, empty message, spawn error) stops the chain; the migrate child additionally runs the pipe under `set -o pipefail` so the exit code survives the tail |
| Who applies the post-SQL warning rule | nobody in the migration repo: `migrate_all.py` swallows post-SQL failures as warnings and exits 0 (§7.6) | the migrate child: `[!] Warning during post-migration SQL execution` in the tailed output fails the gate even at exit 0 |
| Who emits the SUCCESS block | `agent_runbook.md`'s summary contract: "Onboarding Status: SUCCESS" with PASS per step 0–5 when all gates succeed | the parent wire, after a clean four-hop chain — with the scope line stating gates 1 and 5 are not hops, so the block cannot be read as the full six-step claim |
| Who starts services | the agent runs gate 1 (`docker compose up -d --build rpg-api`) at its position in the sequence | nobody in the chain: the readiness check (`curl <API base>/health`, "Healthy") proves services are up or the chain stops before hop 2; teardown is the operator's call in both designs |
| Gate-4 curls | host-side `curl -s -f` against hard-coded `http://localhost:5000` (§6) | base supplied via `CT_RPG_API_BASE` (a non-localhost base is recommended, not enforced — the live run used localhost:5000; the port is whatever the base carries), status captured with `-w "\n%{http_code}"` and checked by rule, body supplied via `CT_RPG_FEE_TX_BODY` |
| Gate 5 (xUnit tests) | the agent runs `docker compose run --rm rpg-tests` | declared non-hop; the audit-trigger assertion therefore never runs in a ct-rpg chain — the summary block says so |

---

## 5. How a live run is invoked

From the harness checkout (`../aetheris`, with `deps/` present):

```bash
mix aetheris run ../aetheris-agents/ct-rpg/agents/rpg-main.exs
```

Environment the run needs:

- `CT_RPG_API_BASE` — the deployed API's base URL, e.g.
  `https://rpg-api.example.net`. A non-localhost base is recommended, not
  enforced — the live trajectory used `http://localhost:5000` and the run
  completed — and `API_PORT` remains configurable in the migration repo.
  Unset: readiness cannot be confirmed and hop 4 has no base — the chain
  stops before hop 2 (hop 1 has run; hops 2, 3, and 4 have not).
- `CT_RPG_FEE_TX_BODY` — the demo fee-tx POST body, verbatim, e.g.
  `{"studentId":"cc93c106-82ea-4610-9873-3db87f1307c6","amount":500.00,"status":"Active","feeId":"a7e2851c-2321-4adc-993a-387deefee3a8","refNo":"AGENT-DEMO-01"}`
  (the fixed body from `design-migration.md` §5.3/§6). Unset: same MISSING
  handling as the API base.
- `CT_RPG_SANDBOX_PATH` — optional; the run's sandbox. Falls back to
  `ct-rpg/` beside the parent file.
- `CT_RPG_MODEL` or `AETHERIS_MODEL`, and `AETHERIS_PROVIDER` — the agent
  runtime's model/provider, per the wrapper's fallbacks (plus whatever API
  key the provider needs).

The migration repo root is **not** an environment variable and **not**
hard-coded anywhere in `ct-rpg/agents/`. It arrives in the run's user
prompt, one line, and the parent passes it through verbatim to every hop:

```text
Migration repo root: /home/sripad/Work/bitloka/docs/r2pg-migration
```

If the user prompt carries no root, the parent runs no hop and says so.

---

## 6. Open items the agents inherit

`design-migration.md` §7 lists the migration repo's unresolved divergences.
Split by whether the agents can see them in their own outputs:

**Observable by the agents:**

- **Silent post-SQL warning (§7.6).** The warning prints before the summary
  line, so the migrate child's `tail -n 80` captures it. The child's
  contract fails the gate on it even at exit 0 — the agent's verdict is
  honest, but the view/triggers are still missing; repairing that is a
  migration-repo decision.
- **Unordered verifier paging (§7.3).** The verifier's RQL has no
  `order by id()`, so on a live source the audit can skip or duplicate
  documents undetected. The agent observes the consequence, not the cause:
  a `[SUCCESS]` line it cannot distinguish from a complete audit.
- **Missing PowerShell preflight (§7.1).** `verify-prerequisites.ps1` does
  not exist; the preflight child runs the bash script, so on a Windows host
  the command fails and the child reports the failure — the divergence is
  visible in the child's own error path.

**Not observable by the agents:**

- **`tx_no` collisions (§7.10).** Same-millisecond inserts produce duplicate
  `tx_no` silently, and the POST returns 201 either way. The api hop sees
  status 201 — the collision is invisible to it, and to every gate except a
  dedicated query.
- **The unused `deleted_students` counter (§7.12).** Initialised, never
  incremented — a planned delete/reconciliation step with no runtime trace.
  Nothing in any gate's output reveals it.

The same invisibility applies to the remaining §7 items that live inside
script behaviour (the verifier's silent PG defaults, the PKCS#12 temp-key
leak, `--core-only` being a no-op, the unparseable-status "Active"
fallback, `todaysAbsenteesOnly`): the agents quote the scripts' outputs and
check the scripts' exit codes; divergences that never reach either are
outside what an agent can report. Filing or fixing them is migration-repo
work.

---

*End of document. The agents own the wire and the contracts; the scripts own
the migration.*
