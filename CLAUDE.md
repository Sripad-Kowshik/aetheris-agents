# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## What this repo is

A collection of use-case agent implementations built on top of the **Aetheris** harness (sibling repo at `../aetheris`). Each use case is a self-contained directory with Python scripts, Elixir agent files, tests, and docs. No Elixir source lives here — only `.exs` agent scripts that the harness evaluates.

The two repos work together:
- `aetheris/` — the harness (`mix aetheris run`, `mix aetheris inspect`, etc.)
- `aetheris-agents/` — this repo; use-case scripts and agent files

All sprint and agent commands are run from `~/sandbox/elixirws/aetheris/`, not from this repo.

**Repos rule (claude-code sessions).** Sessions run with this repo
(`aetheris-agents/`) as the working directory; the harness is the sibling
`../aetheris/`. Paths in tickets and docs are relative to `aetheris-agents/`
unless prefixed with `../aetheris/`. Edits default to this repo; touching the
harness is explicit and called out in the ticket's `Touches` list.
**Every session reads *both* repos' CLAUDE.md learning sections before its first
edit** — promoted rules live in one repo only and are not otherwise reachable from
the other. This is a first-action step, not a background intention: BL-031 was a
cross-repo ticket whose session never opened `../aetheris/CLAUDE.md`, so the entire
review-discipline block was absent while three review packets were written against
it, and Complete-output was re-broken (`tail -3`, BL-031 §1f) by a session that had
never read it. If you have not read the sibling's learning sections, you have not
started the ticket.

`[Widened 2026-08-08 at the m4-cloudcost close. It previously bound "Cross-repo
sessions, and any session that will produce a review packet" — a condition already
nearly universal, since every ticket in the m4 cycle produced a packet, and a
nearly-universal condition is one a session can talk itself out of. **The widening is
what makes rule placement editorial:** with the read universal, a rule living in one
repo only is reachable from either, so a promotion lands where it reads most coherently
beside its siblings. No criterion for choosing a repo is stated here because none
exists — two of the five repo-directed promotions in the one round that has both a
draft and a landing record were re-homed, and a criterion inferred from those two would
be inferred from exactly the data points that went wrong. See
`cloudcost/m4-consolidation.md` §Promotion candidates.]`

**A cc:prompt declares its ROUND TYPE — code, mechanical, or documentation —
before anything else.** A session that receives one without it reports the
omission and asks, before acting. The type is the reviewer's estimate of what
the round will produce, not a contract; its job is to let the arbiter decline a
round whose shape they did not expect. It is a rule rather than a habit because
the reviewer's conventions live only in its prompts, and a convention with no
repo-side home survives exactly as long as the reviewer remembers to restate it
— which this one failed at immediately, being adopted 2026-08-26 and absent from
the very next round's prompt for that exact reason.
`Source: adopted 2026-08-26, on the arbiter's twice-raised concern that
documentation rounds were accumulating with nobody counting them — a declared
type is what makes them countable. Landed here 2026-08-27.`

**The round types are exactly three: `code`, `documentation`, `mechanical`.**
- **code** — the diff changes executable source, tests, build/runtime configuration,
  dependency manifests, or lockfiles.
- **documentation** — the diff contains authored prose or authored procedural
  instructions, and no code-classified change.
- **mechanical** — every change is tool-produced or a semantics-preserving move,
  re-pin, regeneration, or formatting operation, with no authored content and no
  code-classified change.
A mixed diff takes the first type that applies, in the order code → documentation →
mechanical. So a lockfile bump is `code`; a generated index plus authored explanation
is `documentation`; a pure re-pin or index refresh is `mechanical`. `refactor` and
`defect fix (test)` describe a `code` round and are not types. A cc:prompt carries
`ROUND TYPE: <type>` as its first substantive line; the template is
`prompts/cc-prompt-template.md`.
`Source: the arbiter's ruling of 2026-09-21. Earlier instances it subsumes:
docs/reviews/bug-001-review-r2.md:65; docs/evidence/BL-279.md:115.`

**Gates by round type.** A `documentation` or `mechanical` round runs
`python3 scripts/drift_check.py --strict`, `python3 scripts/backlog_status.py --check`
and the triad-loop mirror `diff -q`. A `code` round runs every existing gate.
`Source: the arbiter's ruling of 2026-09-21.`

---

## Commands

**Run the whole-suite gate**, then either deferred set (see §Definition of done for what the gate
excludes and why the two exclusions are never merged):
```bash
# From the aetheris-agents/ root
python3 -m pytest -q -m "not integration and not dormant"
python3 -m pytest -q -m "integration and not dormant"
python3 -m pytest -q -m dormant
```

**Run tests for a use case:**
```bash
# From the aetheris-agents/ root
python3 -m pytest payslip/tests/ -v
python3 -m pytest api/tenant/tests/ api/gateway/tests/ -v

# Single test file
python3 -m pytest payslip/tests/test_payslip_compute.py -v

# Single test
python3 -m pytest payslip/tests/test_payslip_compute.py::test_net_salary -v
```

> `python3` here is the mise-managed Python 3.12 (`mise.toml`). If `python3 -m pytest` reports "No module named pytest", install with `python3 -m pip install pytest`. The system `pip3` (Python 3.10) writes to a different site-packages.

**Run a script standalone:**
```bash
cd ~/sandbox/elixirws/aetheris-agents/payslip
python3 scripts/payslip_compute.py data/sample_payroll.csv | python3 -m json.tool
python3 scripts/generate_employee_payslips.py BTL_999
```

**Run an agent:**
```bash
cd ~/sandbox/elixirws/aetheris
mix aetheris run ../aetheris-agents/payslip/agents/payslip_orchestrator.exs
```

**Evaluate an agent file (syntax/struct check, no LLM call):**
```bash
cd ~/sandbox/elixirws/aetheris
mix run --eval 'Code.eval_file("../aetheris-agents/api/tenant/agents/at1cmd.exs")'
```

**Run a sprint case:**
```bash
cd ~/sandbox/elixirws/aetheris
./scripts/sprint.sh payslip
./scripts/sprint.sh uc_api_agent_t1
```

**Inspect a run:**
```bash
mix aetheris inspect <run_id>
mix aetheris tree show <run_id>
mix aetheris list --limit 20
```

**Aetheris checks (run from `aetheris/` repo, not here):**
```bash
cd ~/sandbox/elixirws/aetheris
mix format --check-formatted
mix credo --strict
mix dialyzer
mix test
```

---

## Architecture

### Core principle

**Scripts do; agents decide.** Python scripts contain all deterministic logic (CSV parsing, computation, file generation, API calls). Elixir agent files contain only the `RunConfig` or `OrbConfig` struct — the LLM reads context, calls scripts via `run_command`, and orchestrates results. Never ask the LLM to construct file content or compute values programmatically.

### Use-case layout

Each use case follows:
```
{use_case}/
  agents/           # .exs files — RunConfig or OrbConfig structs
  scripts/          # Python — deterministic logic, one responsibility per file
  tests/            # pytest — unit + integration; conftest.py per directory
  data/             # input files; .gitignore excludes real data
  docs/             # t*-implementation-notes.md written after each ticket
  output/           # gitignored; .gitkeep committed
```

**The current use cases are the rows of `docs/use-cases.md`** — the committed registry, which
also carries each one's status, the date it was set, and its condition for return. Read the
table rather than a sentence here: at `7841060` this line named `payslip`, `drive`, `email`,
`api` and `boxy-pipeline`, omitting `cloudcost`, `docbuilder`, `eduloka` and `provenance`
outright and collapsing `api` to one — and nothing noticed, which is exactly why the registry
exists. (That enumeration is quoted as the historical fact it is, not maintained.) It is out of scope for
`drift_check.py`'s `use_case_registry` check by that check's own criterion — an enumeration
inside a sentence cannot be extracted without deciding what the sentence means — so it is
de-numeralised into a pointer instead of being kept in step by hand.

### Agent files

Agent `.exs` files evaluate to either a `%Aetheris.RunConfig{}` (solo agent) or a `%Aetheris.OrbConfig{}` (multi-agent). The harness's `mix aetheris run` loads the first positional file — extra file paths passed to `run_orb` in sprint.sh are ignored by the CLI.

**Critical conventions:**

```elixir
# Always use __ENV__.file — never File.cwd!()
agent_root = Path.expand(Path.join(Path.dirname(__ENV__.file), ".."))
# For agents two levels deep (e.g. api/tenant/agents/):
agent_root = Path.expand(Path.join(Path.dirname(__ENV__.file), "../.."))

# Always nil when output must persist
overlay_base_dir: nil,

# context_strategy for orb agents
context_strategy: :full,   # short-lived pipeline agents (<~10 steps)
context_strategy: :rolling, max_context_steps: 6,  # long-running orchestrators only
```

> `:rolling` with a small `max_context_steps` truncates old messages and can leave orphaned `tool_use_id` references, causing HTTP 400. Use `:full` for any agent that runs fewer than ~10 steps.

### Multi-agent orbs (OrbConfig)

Agents communicate via blackboard and `send_message`. The pattern:

1. **Sender** writes to blackboard: `write_blackboard key: "tap:intent:{id}", value: json`
2. **Sender** signals receiver: `send_message to: "{run_id}", message: "...intent_id: {id}"`
3. **Receiver** waits: `wait_for_event condition: "message_received", timeout_ms: 120000`
4. **Receiver** extracts the key from the message body, reads from blackboard

Run IDs must be pre-established in the OrbConfig so send_message targets are known at prompt-write time:
```elixir
orb_id    = "uc-api-t1-#{Aetheris.ID.generate()}"
at1cmd_id = "#{orb_id}-at1cmd"
cot1_id   = "#{orb_id}-cot1"
```

### Python script conventions

- **One responsibility per script.** Compute scripts → JSON. Generation scripts → files. No mixing.
- **stdout is the contract.** Scripts print JSON to stdout; agents parse it. Errors go to stderr.
- **Exit codes:** 0 on success, 1 on recoverable error. Always 0 for analysis/reporting scripts.
- **`--output-dir` flag** on generation scripts (default `"output"`); lets tests write to `tmp_path`.
- **`cwd=USE_CASE_ROOT`** in subprocess calls from tests so `data/` and `scripts/` resolve correctly.
- **No `__init__.py`** in use-case directories whose name collides with stdlib packages. Use `conftest.py` to insert `scripts/` into `sys.path` instead.
- **Done-check thresholds:** set numeric thresholds (e.g. "≥N resolved items") only after running the pipeline against actual sample data. Estimating before examining output consistently produces wrong numbers and requires a correction commit.
- **Slugification belongs in Python, not the LLM.** When file paths depend on user-supplied strings (search terms, names), implement a `slug_term()` function in a script that returns a filesystem-safe slug. The orchestrator calls the script once, receives pre-computed slugs alongside the original values, and passes both to sub-agents — the LLM does string substitution only, never derives slugs itself.
- **Explicit sink selection with fail-fast.** When a pipeline supports multiple operational sinks (e.g., DB upsert vs. file export), select via an env var resolved at agent eval time. A required-but-absent credential must `raise` immediately — never silently fall back to a different sink. Regression-guard the raise in sprint with a hermetic env check: `env -u MISSING_VAR SINK=mode mix run --eval ...`.
- **Parallel sub-agent file isolation.** When an orchestrator spawns parallel sub-agents that each write files for the same logical output, give each sub-agent a per-term directory (e.g., `data/raw/{slug}/`) rather than a shared flat directory. Without isolation, parallel agents silently overwrite each other's output.
- **Stage CLIs degrade, they don't crash.** A pipeline script hitting empty, null, or malformed input (a provider returning `null`, one bad JSONL line) emits a partial result with a `{"status": "partial"}` envelope and `exit 1` — never an uncaught exception that breaks the stdout contract. Guard per-line/per-item (skip + count `skipped`/`errors`), and treat an API's explicit `null` the same as absent (`x or []`, not `dict.get(k, default)`).
- **Bind to the value a library *resolved*, never the one it advertises.** When a library exposes
  both — protocol, API version, endpoint, region — read the resolved one (`resolved_protocol`,
  not `protocol`). The advertised field states a preference; the resolved value is what the
  library's own serializer and parser are actually built from, and the two diverge exactly where
  the library has fallen back. A hand-typed table of the same information is the same bug with
  an extra copy to maintain. The divergence hides until the one case where they differ: the
  cloudcost AWS stub encoded from `ServiceModel.protocol` and nine of its ten services agreed —
  CloudWatch advertises `smithy-rpc-v2-cbor` and resolves to `json`, so encoding to the
  advertised value drove the cbor parser over a json body and raised `MemoryError`. Read what the
  tool resolved; never re-derive it.
  `Source: m2-cloudcost t4 (tests/aws_wire.py; the switch landed alone with the full suite captured per-test before and after, zero pre-existing tests moved).`
- **Verify a foreign table's live DDL before writing raw SQL to it.** When a script writes to a table owned by another system (e.g. an Ecto/ActiveRecord schema), confirm the real column types and write semantics (`\d table`) before trusting an inferred schema — raw SQL breaks on array types (`jsonb[]` vs `jsonb`), `NOT NULL` timestamps with no DB default, and update-field semantics (don't clobber columns the owner manages, e.g. soft-delete `status`). Test against a faithful schema clone, not a hand-rolled table.

### conftest.py pattern

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

def pytest_configure(config):
    config.addinivalue_line("markers", "integration: ...")
```

Integration tests that require external tools (wkhtmltopdf, etc.) get `@pytest.mark.integration` and are auto-skipped if the tool is absent.

When multiple integration tests share an expensive setup (e.g. running the full pipeline once), extract it into a `@pytest.fixture(scope="module")` rather than repeating the subprocess chain in each test body.

### Domain documents (api/ use case)

The `api/domain/` directory holds two JSONL files read by the gateway agent:
- `ct.stu.vocabulary.jsonl` — tenant-visible; intent definitions, field rules, enum lookups
- `ct.stu.behaviour.jsonl` — gateway-internal; execution modes, on_duplicate, outcomes

Each line is a self-contained JSON record. `record_type` is the discriminator. Blank lines are separators, not errors.

### Sprint script

`aetheris/scripts/sprint.sh` is the integration test harness. Add new cases before the `# Summary` section. All paths from sprint.sh to this repo must use `../aetheris-agents/...` (sprint runs from `aetheris/`). The `run_orb` helper passes its args to `mix aetheris run`; only the first file path is loaded.

---

## Definition of done — doc sync

`docs/rig/specs.md`, `docs/rig/runbook.md`, and `docs/rig/architecture.md` must
stay in sync with the Rig source code. Use the drift checker to verify:

```bash
# From aetheris-agents/ root
python3 scripts/drift_check.py

# Or via sprint.sh (from aetheris/)
./scripts/sprint.sh drift_check
```

**Checks run:** event types (event.ex ↔ specs.md §6), Tauri commands (lib.rs ↔ specs.md §4),
DB schema (store.ex ↔ specs.md §2), env vars (Rust code ↔ specs.md §1 ↔ runbook.md),
routes (registry.ts ↔ App.tsx), payload field sampling (live DB ↔ specs.md §6),
milestone README Status: lines, and — since 2026-09-08 — `index_integrity`: for every
manifest row whose path is an `index.md`, each entry resolves at HEAD and every
frontmatter-bearing file in that tree has an entry (the hybrid-context design's §1.1 arm;
the generator is `scripts/gen_index.py`, and a file the generator would refuse is a FAIL
here if committed anyway). The manifest is the list of indexed trees; there is no second one.

**When to run:** after any Rig milestone, after adding commands, event types, env vars,
routes, or DB tables. Zero FAIL findings and zero *unexplained* WARN findings required — for a
**manifest-tracked** edit the `project_knowledge` (check 8) portion is meaningful only
**post-commit** (it reads committed history; see the learning rule below), so run the `--strict`
done-check after that commit and name the expected `project_knowledge` WARNs. Checks 1–7 remain
valid pre-commit.

**Strict mode (`--strict`, BL-009).** The sprint runs `drift_check.py --strict`: any
WARN fails the sprint, so drift cannot accumulate into the next alarm-fatigue cycle.
**One exemption** — `project_knowledge` manifest-*staleness* WARNs stay WARN and do not
fail. Rationale: every doc commit re-stales the manifest until the next export, so
mid-cycle staleness is expected truth, not regression; the export boundary is the
enforcement point (that is where the manifest is regenerated and staleness must clear).
So the strict invariant is **"zero *unexplained* WARNs"**, not "zero WARNs" — a standing
manifest-staleness WARN in day-to-day output is the signal we chose to keep, not a
regression to chase. Structural manifest problems (missing manifest, unknown repo, git
failure) are **not** exempt and still fail under `--strict`.

**A manifest-staleness done-check runs post-commit — a `drift_check --strict` before committing a
manifest-tracked edit is vacuous.** Check 8 (`project_knowledge`) compares the manifest against
committed history (`git log -1 --format=%h -- <file>`), so run *before* the commit it reads the
file's pre-edit hash and cannot see the staleness the edit introduces — it passes green where a
gap exists (the **Silent-wrong-answer** class — harness `CLAUDE.md` — in gate-ordering form). Run the `--strict`
done-check *after* the commit that touches a manifest-tracked file, when check 8 can compare the
new commit hash against the manifest; then **name** the exempt `project_knowledge` staleness
WARNs rather than chasing them (mid-cycle staleness is expected truth, cleared only at the export
boundary — the strict-mode exemption above). Checks 1–7 (source-vs-doc) remain valid pre-commit;
it is check 8's committed-history dependency that forces the ordering.
**And that same dependency decides the WARN *set*, which is a function of the manifest's staleness
backlog and not of the commit under test.** Check 8 compares each row's pinned hash against *that
file's own* last-touching commit, so a file moved by an earlier commit that deliberately did not
re-pin keeps its WARN regardless of what any later commit touches — which makes any prediction of
the WARN count derived from the current commit's changed files wrong. It was: the BL-143 close
predicted exactly one WARN on the ground that `CLAUDE.md` was untouched by that commit, and got two.
`Source: BL-034 (fe8298c — the export-prompt self-staling ordering hazard, real but latent; its "628f15f production-fired" claim withdrawn as false after a clean check-8 sweep of all 38 committed manifests), BL-025 (8021a59/00ddd34 — the vacuity fired on the caveat's own author: pre-commit 1 WARN, post-commit 3).`
`[The WARN-set sentences were added 2026-08-17 as a **correction of an incomplete passage**, not as
a new entry: the text explained check 8's *ordering* and was silent on what determines its *set*,
and that silence produced a wrong prediction at the BL-143 close of 2026-08-16 — exactly one WARN
predicted, two observed. Folded in here rather than appended beside, because two entries about check
8's semantics are two surfaces that will disagree at the next amendment. The instance is
reproducible at `d60c6df`, which touches neither `CLAUDE.md` nor the manifest: `drift_check
--strict` there reports `CLAUDE.md stale — manifest=fd03bf3 current=84c24c7` alongside the backlog's
own WARN.]`

**`drift_check` verifies a pin is current, never that it is complete — read the pinned content
against what it should say, do not trust the green.** Check 8 compares the manifest's commit
column against `git log -1 --format=%h -- <file>`: a currency test, and silent on whether the
pinned document still says what it claims to. A current pin over a document that has gone
incomplete reports exactly the same green as one over a correct document, so the green is
evidence about the export, not about the content.
`Source: cloudcost-in-Rig batch close, 2026-08-04 — recorded only in handoff-linode-provider-three-kickoff-2026-08-04.md §Review-discipline learnings promoted (:87), and found absent from both CLAUDE.md files at the m3-cloudcost close.`

**Export is remove-all-upload-all against the full manifest set, never a hash-driven diff.**
Uploading only what changed leaves the project-knowledge store and the manifest describing
different sets, and the tooling cannot see it: check 8 detects the repo moving ahead of an
export, never a file uploaded without a regen (`docs/project-knowledge-manifest.md`, the header
paragraph above the table). The check is blind in that direction by construction; the procedure
is the only thing covering it.
`Source: cloudcost-in-Rig batch close, 2026-08-04 — recorded only in handoff-linode-provider-three-kickoff-2026-08-04.md §Review-discipline learnings promoted (:89), and found absent from both CLAUDE.md files at the m3-cloudcost close.`

**Ticket text that quotes repo state** (counts, paths, expected outputs) cites the commit
it was verified against; claude-code treats divergence between ticket text and repo reality
as a deviation to note, never to silently follow. Source: BL-001, BL-015, BL-002.

**Amend a commit while it is unpushed; append once it is pushed.** A SHA that has not been pushed
resolves for no one but the executing checkout, so a citation to it is not yet a durable reference
and nothing is protected by refusing to amend it; a pushed SHA resolves for others, and amending it
leaves their citations pointing at a tree that never existed — the unfalsifiable-reference class the
rules in this section exist to remove. **Once a packet has been issued against a commit, amend it
only on the arbiter's instruction** — an unprompted amendment changes bytes the reviewer has already
read. **An amend that supersedes a SHA named in an issued packet states that SHA in its message and
says what cited it.** The limbs protect different things — push state protects **resolvability**, the
packet protects **review integrity** — and a commit can be inside one and outside the other, which is
the case the arbiter's instruction settles.
`Source: the cc:prompt preambles of 2026-08-16, promoted at the handoff of 2026-08-17; trigger
corrected 2026-09-20 on the arbiter's ruling of that date. It lands beside the rule above because
that one says a claim cites the commit it was verified against and this one says what a cited
commit may then do.`
`[Corrected 2026-09-20 (BL-280). The trigger was citation and is now push state, and the packet's
protection is stated as its own limb rather than carried by the trigger. It previously read:
*"Amend a commit while it is private to the ticket and uncited; append once a packet has been issued
against it."* Found by following it — the BL-274 fixture round amended `722e226` on the arbiter's
instruction, a SHA an issued packet's `drift_check` done-check had cited and that had never been
pushed, and the executing session complied and reported the contradiction rather than letting the
two practices diverge; the superseded-SHA obligation above is that round's mitigation promoted. The
three 2026-08-16 landings the superseded entry carried as instances were decided on the citation
trigger and are not carried forward as instances of this one — whether those commits were pushed is
not established here. Evidence: `docs/evidence/BL-280.md`.]`

The **prose budget** in the harness `CLAUDE.md` binds every artifact this repo produces —
packets, notes, reviews, backlog rows, boundary records. It caps expression, not coverage.
Canonical there; do not restate it here.

**Every existing gate runs at the ticket boundaries of a `code` round, even off-territory** (`mix test`,
`tsc -b`/`bun run build`, `bun run lint`, sprint, `drift_check --strict`, the Python
whole-suite gate below). `[Scoped to code rounds 2026-09-21, the arbiter's ruling of that date; see Gates by round type.]` A red gate gets a
tracked ticket the day it's found — never carried silently. Gates that only run when a ticket
happens to touch their territory rot invisibly, and each rot normalizes the next: `mix test`
was red before BL-003, `tsc -b`/`bun run build` red for three weeks (p9-t4), `bun run lint` red
from an undated `eslint-plugin-react-hooks` bump — all three surfaced only because a later
ticket ran the gate off-territory. **`bun run lint` is green as of BL-029 (2026-07-20)**, found
so by an off-territory run; when it went green is unknown, because nothing was watching in
either direction. That is the same invisibility this rule exists to prevent, running the other
way: a gate that silently *heals* trains the same "the note is probably stale" reflex as one
that silently rots, and the stale red note is what makes a real red one ignorable.
A known-red gate that already has a tracked ticket is
**named in the packet with its ticket ref, not re-triaged** — the rule prevents silent carry,
not tracked carry. It is also left **red**: never quietly relaxed, re-pointed at something that
passes, or downgraded to a warning to get a clean run. A quiet downgrade is how a real
regression later goes unnoticed, and it destroys the one thing the carry was preserving — that
the gate still means what it said. BL-069's ≥1-orphan assertion was carried red and named on
every leg of m2 and m3 rather than relaxed. **It closed at m4 t2 by retirement, openly** — the
assertion could only ever be satisfied by keeping a billable resource on a live account, so the
ticket replaced it with one asserting the property it stood in for, closed the row on that basis,
and swept every document that still told an operator to plant. That is not the quiet downgrade
this rule forbids, and the difference is not the outcome but the route: the change *was* the
ticket, with its own review and its own record, rather than an edit made to get past one.
`[corrected 2026-08-06 (m4 t2). The sentence previously read "and it closed by planting the
resource the assertion was always about" — **wrong when written, not superseded since**, and
carried for three days as an endorsement of the practice. Established at
cloudcost/docs/m4-t2-implementation-notes.md §4a.]`

**The Python whole-suite gate is the command, not the outcome.** It is

```bash
# from the aetheris-agents/ repo root
python3 -m pytest -q -m "not integration and not dormant"
```

Say *"the gate is `python3 -m pytest -q -m "not integration and not dormant"` from the repo
root"*, never *"the whole suite passes"* — a done-check phrased as an outcome is still
true-sounding on a day the suite is red, and phrased as a command it can be re-run by a reader.
The exclusion is **not** in `addopts`: making it the default is how it would stop being visible.

**Two exclusions, two markers, never merged — and the gate prints both counts.** Root
`conftest.py` attributes every deselected test to exactly one reason and writes
`deselected by reason: integration=112, dormant=208 (total 320)` into ordinary output, because a
single merged figure is how an exclusion set becomes permanent and unexaminable. Each deferred
set has its own command, so an exclusion is a deferral rather than a deletion:

| marker | what it asserts | its own command |
|---|---|---|
| `integration` | **Test mechanics.** The test's outcome depends on state that is not in this repository at the commit under test. | `python3 -m pytest -q -m "integration and not dormant"` |
| `dormant` | **Business state.** The use case's work is paused, so its tests are deselected rather than gating. Carries a date and a stated condition for return. | `python3 -m pytest -q -m dormant` |

**Apply `integration` by asking one question a reader who has never seen the test can answer:**
would it do its work and pass in a **fresh clone at this commit, offline, with no sibling
repository present**? If it would fail, error, or *silently skip* because the thing it needs is not
there, it is `integration` — a silent skip counts, since "passed here, skipped in a fresh clone" is
exactly outcome-depends-on-state-the-repo-does-not-carry. A subprocess against a script **tracked
in this repo**, on inputs this repo carries, is **not** `integration` however many it spawns; that
is the standard idiom here and it stays in the gate.

Neither marker is ever applied because a test is slow, and neither because it fails: **a red test
is reported red, not marked.** **Dormant tests still collect and still import** — a use case whose
tests stop collecting is one nobody notices has rotted, which is the defect this gate exists to
remove; deselect at run time, never at import. `pytest.ini` is the authority for both markers'
full statements and for `dormant`'s condition for return; `addopts` carries `--strict-markers`, so
an unregistered mark is a collection error rather than a silent selection of nothing.

**Any run that can reach live subprocess work runs under an explicit wall-clock cap, and a
cap-kill is a complete result.** Record the cap and record that the run hit it; do not retry with
a longer one. The two long runs of `2026-08-16` are the standing example, and the thing to carry
from them is that **neither was killed by its cap**: a merged `python3 -m pytest -q -m integration`
run under `timeout 2700` was ended deliberately with `SIGKILL` at 52m21s — 3141s, so it had
**outlived** its own SIGTERM, which is filed on **BL-151** — and a `-m integration boxy-pipeline`
run under `timeout 2400` was ended deliberately at 10m17s, 617s, well inside its cap. Neither
finished, and that is the recorded result rather than a check still owed. **A cap that does not
actually cap is a cap a future session will trust wrongly**, so record what ended the run, not
only the number you set.

`Source: BL-152, 2026-08-16. Until then the wording was "the whole suite, not <use_case>/tests/",
and the literal root command — `python3 -m pytest -q` — aborted during collection and ran nothing
at all, so the gate could not distinguish a green repo from a broken one. Collection is fixed by
the root `pytest.ini` (rootdir pin + `--import-mode=importlib`); see that file's header for the
three module-name collisions it resolves.`
`[Corrected 2026-08-20 at ds t2 stage 4. The example previously read: "The dormant set is the
standing example: the two capped runs covering it were killed deliberately at 52m21s (cap 2700s)
and 10m17s (cap 2400s), neither finishing, and that is the recorded result rather than a check
still owed." **The rule is unchanged and was never wrong; only the example is replaced**, because
that sentence asserted two things that are false. (1) It called them *capped runs* — neither was
cap-killed; both were killed by hand, and the first outlived its 2700s SIGTERM, which is the
opposite of a cap working and is the most useful fact either run produced. (2) It called them runs
*covering the dormant set* — both are `-m integration` runs, the first explicitly "(merged set,
before the split)", and both **predate the `dormant` marker**, created by BL-152 at `2868a3e`.
There was no dormant set to cover. Sources, read at agents `c8aa4e3`:
`docs/milestones/bl-152-implementation-notes.md:306-311` for both runs, and
`docs/backlog-2026-06.md:4874-4882` for the SIGTERM survival. That the dormant set does not
terminate usefully is still true and is **BL-159**'s claim, resting on its own runs rather than on
these two. **Why this landed as its own commit:** the correction was first made at ds t1b and lived
only in a session scratchpad, so ds t2 read this passage, inherited the wrong framing verbatim, and
published it in a review packet — one error, corrected once, made twice. A correction that does not
reach the surface a later session reads has not been made, which is **BL-133**'s class and this is
a worked instance of it.]`

**And no session busy-waits on such a run. It goes in the FOREGROUND under an explicit `timeout`;
if it must be backgrounded, wait on it ONCE, blocking — never an `until … sleep N` poll
loop.** The cap rule above bounds the **run**; this bounds the **wait**. A poll
iteration is not a cheap check: it is a full request that re-reads the entire context and performs
no work, so the loop's cost scales with the window it re-reads rather than with the thing it is
waiting for, and none of it appears in the timings of the run being waited on. Measured across one
ticket: 19m58s of API time against 1h50m36s of wall clock — 82% of the session spent waiting, with
the poll iterations a large share of roughly a hundred requests each re-reading the whole window.

**And bulk output goes to the scratchpad, not into context.** A census, a two-repo sweep or a full
command dump is written to a file and read back narrowly: cite it by path and quote only the
deciding lines. This bounds the **context**, the third thing neither rule above reaches — carrying
bulk inline is what pushes a session past the point where every later request re-reads it, and on
the same ticket 63% of requests ran above 150k. The scratchpad is session-scoped and under `/tmp`,
so it is the working copy and never the record: anything a later reader must be able to open is
quoted into the packet or committed.
`Source: the cc:prompt preambles of 2026-08-16, promoted at the handoff of 2026-08-17. Both rules
were invented and applied in that day's work and written into prompt preambles only — the shape
**BL-162** names, with the preamble as the citing document and no standing home knowing it. **The
figures are the handoff's own, over a ticket it does not name, and no document in either repo
records them except this paragraph**: `git grep -inE '82%|63%|1h50|19m58|150k' -- '*.md'` returns
hits in this file alone, all of them these two paragraphs and the sentence you are reading. The
positive control that the search is not simply blind is the same command with the same flags over
the cap rule's own figures — `git grep -inE '52m21s|10m17s' -- '*.md'` — which returns hits in
several files, this one included. They are carried as telemetry with a named holder, not as repo
state.`
`[Restated 2026-08-21 at ds t3. The claim was previously *"reproducible from neither repo"*,
evidenced by a grep asserted to return 0 — which returned three hits at the moment it was written,
every one of them inside this file, including the line making the claim. Self-falsifying in its own
commit, and the ds t2 stage 4 class: a claim that never reached the surface a later reader checks
it against. The search is NOT narrowed to hide this file; the claim is narrowed to what the search
actually establishes. The positive control's *"8 lines across 4 files"* is de-numeralised rather
than re-counted — the population grows every time a document quotes those figures, so a corrected
number re-arms the same trap for the next quoter.]`

**Before making a soft failure hard, enumerate what else that gate holds.** If flipping it turns
*every* tracked known-red blocking at once, then the enforcement and the exempt/expected-fail
declaration are **one landing, not two** — and the hardening cannot ship while any carried red
is still armed. BL-077 is the worked case: `sprint.sh`'s `fail()` only prints, so a sprint whose
assertions all fail still exits 0. Fixing that alone would have made BL-069 — deliberately armed
— block every sprint the moment it landed, so the counter and an `expected_fail()`/`KNOWN_RED`
declaration keyed by ticket ref have to arrive together. Sequencing a hardening without first
enumerating the reds it will trip is how a correct fix becomes an outage.
Source: BL-016, BL-005 (×2); m2-cloudcost (BL-069 carried red to its close, BL-077 coupling).

**Optional payload fields:** suffix with `?` in the §6 table cell (e.g. `` `stop_reason?` ``) to allow the field to be absent from current DB events without triggering a FAIL. The drift check emits INFO instead. Add the `?` suffix when the field is valid but not yet emitted by the harness version in use; the INFO firing is the trigger to drop the `?` and promote the field to required.

**Tests:** `python3 -m pytest tests/test_drift_check.py -v`

**The export boundary has a mechanism, and it is two scripts.** `scripts/repin_manifest.py`
re-pins the manifest's `commit` **and** `last changed` cells (`git log -1 --format=%h -- <path>`
per row in that row's own repo, then the date **of that resolved commit** — two readings of one
object, so they cannot drift; nothing else in the file touched), and
`scripts/assemble_export_bundle.py DEST` builds the bundle from the manifest's rows, reading each
document out of `git show HEAD:<path>` rather than the working tree. The operator procedure they
sit inside is `prompts/bl-002-refresh-project-knowledge.md`; the export set itself is data, and
lives only in `docs/project-knowledge-manifest.md`'s table. Neither script uploads anything. Who
owns the boundary and on what trigger is **BL-143**, open and untouched by this. Tests:
`python3 -m pytest tests/test_export_bundle.py tests/test_repin_manifest.py -v`

**And a sprint arm drives both through their command lines**, added at ds t3 (BL-161):
`cd ~/sandbox/elixirws/aetheris && ./scripts/sprint.sh export_mechanism`, and it is in `all`. It
exists because those tests reach neither script's `main()` — they call the library functions — so
the entry point, the argument parser, the flag translation and the propagation of `main()`'s return
into an exit code were exercised by nothing. It is hermetic, it writes no tracked file
(`repin_manifest.py` runs under `--dry-run` and the bundle goes to a `mktemp` destination it
removes), and it is **not promoted**: every assertion uses `fail`, so it is counted and
non-blocking. Promotion is a later ticket's act under R7, with that ticket's own red-by-mutation
evidence.

**WHICH BRANCH RAN, said here so no reader has to infer it.** BL-161's Done-when was a
disjunction, and **both branches place their outcome at this site** — branch 1 the arm's
existence, branch 2 a ruling that the tests suffice and *no sprint arm is owed*. Those say
opposite things, so the paragraph above is ambiguous about its own provenance unless it states it.
**Branch 1 was taken. Branch 2 was not taken and is not reachable from here.** BL-161 is **closed
on branch 1** and lives in `docs/backlog-2026-06-closed.md`. Nothing at this site should ever be
read as a ruling that the mechanism's tests were sufficient — they were not, which is why the arm
exists. Branch 1's second clause, *"named in a boundary record"*, was discharged by substitution of
surface (this paragraph, ruled by the arbiter at ds t3) and its executor is **Step 0 of
`prompts/bl-002-refresh-project-knowledge.md`**, which runs the arm before a boundary writes
anything and requires the boundary record's narrative to name it and its verdict.

**The U2 scrub class — what may not leave this machine.** **SCRUBBED:** anything identifying the
account, the people in it, or its internal structure — organisation (`organization`,
`organizationName`), repositories (`repositoryName`), logins, display names, numeric user and
organisation ids, `node_id`, profile and avatar URLs, every one of the fifteen `*_url` fields,
email addresses, and any token-shaped string. **NOT SCRUBBED, because these carry the tests'
meaning:** monetary figures, `product` / `sku` / `unitType` strings, quantities, timestamps, and
the period fields. The class binds the fixtures, the tests, the packet, **and the prose describing
them** — a class covering committed recordings but not the sentences about them is not a boundary.
An address at an RFC 2606 / RFC 6761 reserved documentation domain (`.example`, `example.com`,
`.invalid`, `.test`, `.localhost`) is the standard's designated *non*-address and is **not** an
email address in this sense. The mechanism that looks for the class is `scripts/u2_patterns.txt`,
which holds the patterns and the enumeration of what they do and do not reach; it points back here
and does not restate the class. `[The class statement lives here as of 2026-08-16. It was written
at m6-cloudcost t2 and lived only in `cloudcost/docs/m6-t2-implementation-notes.md` §U2 — a
milestone working artifact the export manifest excludes **by kind**, so the rule governing what may
leave was unreachable from the thing it governs. It moved briefly into the pattern file, which
fixed reachability and not governance, and then here, on the split BL-152 set for the `integration`
marker: the criterion in `CLAUDE.md`, the mechanism in the file implementing it. The notes file is
the historical record of how the class was reached and is not edited.]`

> 2026-08-25 — the class is scoped to THIRD PARTIES, and this is where a later reader comes to
> reopen it. What U2 covers is identifying data belonging to third parties: the accounts, the
> people in them, and the internal structure whose data passes through the harness. It is **not
> a self-anonymisation rule for the operator's own documentation.** The operator's own company
> name or domain, appearing in the operator's own reference documents inside the operator's own
> project store, is **out of the class** — the store already identifies the account by
> construction, so scrubbing the name inside it protects nothing and costs the documents their
> concreteness. Two things this ruling does NOT do, without which it reads as a licence rather
> than a boundary. **First**, it does not reach `docs/aetheris/backlog/uc-inbox.md`: that
> address was substituted on a SEPARATE ground — a brief specifies a mechanism and a live
> endpoint is DEPLOYMENT CONFIGURATION, not specification — which never depended on U2 and does
> not move with this. The sweep was the occasion, never the reason, which is the adjudication
> test below. **Second**, it depends on the store staying the operator's. If the export set is
> ever shared beyond them or published, the calculus changes and this ruling is the thing to
> reopen, because the premise it rests on — that the store already identifies the account to
> everyone who can read it — is exactly what such a change falsifies.
>
> **A property of the instrument, recorded here because it is not a defect and no pattern is
> added for it.** The pattern set has **no pattern for a bare domain**. At the 2026-08-24 export
> `uc-inbox.md` carried two occurrences of the same domain and the sweep matched **one** — the
> one inside an email address, reachable through the email pattern; the bare domain in its §8
> was found by reading the file, not by the instrument. No pattern is added, on two independent
> grounds: under the ruling above the operator's own domain is not in the class, so the pattern
> would have nothing in scope to catch; and a generic domain pattern is unusable here anyway,
> matching ordinary dotted identifiers this repository is full of — `from.id`, `corpus.duckdb`.
> This belongs with the under-reach `scripts/u2_patterns.txt` already enumerates, and that file
> is unchanged.

**The U2 sweep runs by default, and a clean sweep claims something narrower than it sounds.** A
clean sweep claims **no text in the bundle matches these patterns** — never *no identifying
content*. The class members with no lexical signature (logins, display names, organisation and
repository names, numeric ids **in prose**) are ordinary words and ordinary integers, reachable
only contextually, beside a key that names them; that under-reach is enumerated in
`u2_patterns.txt` itself. Use the narrow words when reporting one. The earlier design — a *value*
sweep over literal identifiers via `--needles` — could not be committed (a needle list is a
deanonymisation key), so it had to be derived at run time from raw captures that no longer exist
here and that nothing in either repo locates; it therefore never returned information in either
direction, at any boundary, including one that uploaded. `--needles` survives as an additive sweep
for an operator who does hold captures. What the pattern route does and does not buy is **BL-160**,
open.

**A pattern that fires goes to a human, and the human may change the gate only under this test.**
*An adjudication may change a gate ONLY when the change is derivable from the class definition, or
from a standard independent of the hit, such that you would have written it had you thought of it
first. The hit is the OCCASION, never the REASON.* Removing a pattern because it caught something
inconvenient fails the test; excluding reserved documentation domains from an email pattern passes
it, `@example.com` being the canonical placeholder by a standard that has nothing to do with any
hit. The worked instance is recorded beside the test in `u2_patterns.txt`: the session that hit
three `.example` addresses **refused to clear them and named the candidate fix without making
it** — correctly, because at that moment the only argument for the change was that it would turn
the run green — and the arbiter cleared them and authorised the exclusion on the ground above.
That order is the rule working, and it is the reason the test can be stated at all.

**The manifest set is the scope of *remove-all*, and `claude/` is outside it.** *Remove-all* in
this section's export rule above reads *all of the manifest set*, never *everything in the store*.
A `claude/`-namespaced document carries no row, is out of the export set **by construction**, and
is never removed by this procedure. That namespace is also the boundary between the two
post-upload checks: check 1's set equality against the export-name column governs every store path
not under `claude/`, and check 3 governs `claude/`. The reasoning is **BL-143**'s ruling of
2026-08-16 in `docs/backlog-2026-06.md`; read it there rather than here. It settles this question
only — the ownership-and-trigger pointer above still stands, and that half of the row is still
open.

---

## Key docs to read for each use case

| Use case | Read first |
|----------|-----------|
| payslip | `payslip/docs/t3c-implementation-notes.md` |
| drive | `drive/docs/t3-implementation-notes.md` |
| email | `email/docs/t3-implementation-notes.md` |
| api/tenant | `docs/uc-api-agent-design.md`, `api/docs/t1-implementation-notes.md` |
| api/gateway | `docs/uc-api-agent-design.md`, `api/docs/t1-implementation-notes.md` |
| boxy-pipeline | `boxy-pipeline/docs/m-boxy-pipeline.md`, `boxy-pipeline/docs/m-boxy-pipeline-1a.md`, `boxy-pipeline/docs/runbook.md` |
| ct-bot | `ct-bot/README.md`, `ct-bot/milestone.md`, `ct-bot/docs/agents/README.md` |
| eduloka | `eduloka/runbook.md`, `docs/milestones/m-eduloka-discovery-summary.md` |
| docbuilder | `docbuilder/runbook.md`, `docbuilder/milestone.md` |
| cloudcost | `cloudcost/runbook.md`, `cloudcost/milestone.md`, `cloudcost/m2-milestone.md` |
| provenance | `docs/provenance/runbook.md`, `docs/provenance/overview.md`, `docs/provenance/milestones/` |

The first column is the registry identifier from `docs/use-cases.md`, and
`drift_check.py`'s `use_case_registry` check compares this column against that table — so the
row set here is a checked enumeration, not a reading list someone remembered to extend. `api`
is two rows because the registry splits it; both cite the same design doc, which covers the
protocol both halves implement.

The `docs/agent-creation-guide.md` is the authoritative reference for building new agents.

---

## Learning — m1-docbuilder

Findings that recurred across ≥2 tickets in the docbuilder m1 milestone, promoted per methodology §7.

**`run_command` has no stdin parameter — generation scripts must also accept `--input FILE`.**
The orchestrator cannot pipe a JSON payload to a script's stdin via `run_command`. Any script that reads JSON from stdin must also accept `--input FILE` before it can be called from a `run_command` orchestrator. The first attempt using `sh -c "cat file | python3 script.py"` was unreliable — the LLM timed out on the pipe. See `agent-creation-guide.md` §"Common failure modes".
`Source: m-docbuilder-m1 t7`

**Review packets must include the full done-check output block, opened first.**
A packet without done-check output (test names + PASSED/FAILED + elapsed time + pipeline file listing) is returned unreviewed. The done-check output goes at the top of the packet — not after the diff. This was raised at t4 (blocking) and recurred at t5 and t6 (pipeline file listing absent). The milestone doc prompts for packets now include an explicit "Review packet must open with the full done-check output block" instruction.
`Source: m-docbuilder-m1 t4, t5, t6`

**Implementation notes are a required deliverable, not optional — commit before submitting the review packet.**
A packet missing an implementation notes file is returned unreviewed. The notes file must be committed (not just written) before the packet is sent. For docs-only tickets (no scripts, no agents) a brief notes file is still required: capture decisions made, open items forwarded, and anything that does not survive in the code itself.
`Source: m-docbuilder-m1 t1 (F1 blocking), t8 (F1 — accepted without it for docs ticket)`

---

## Learning — m2a-docbuilder

Findings that recurred across ≥2 tickets in the docbuilder m2a milestone, promoted per methodology §7.

**LLM orchestrators can't reliably round-trip large stdout through `write_file` — give scripts an `--output FILE` (or `--spec FILE`) flag so they write directly.** This is the write-side complement to the m1 `--input FILE` rule. When the orchestrator must capture a script's large stdout (e.g. an ~8K doc-spec JSON) and re-emit it verbatim as a `write_file` `content:` field, the LLM improvises (it wrote `/tmp` scratch scripts instead). Add an `--output FILE` flag: the script writes its payload to the file and prints only the path; the orchestrator passes the path downstream and never handles the blob. Reserve `write_file` for small content the LLM can reproduce exactly.
`Source: m-docbuilder-m2a t6/t7 (render_template `--spec FILE`), t8/t9/t10 (compute_doc `--output FILE`)`

**A new optional doc-spec/template field lands in two steps: the renderer reads it with a fallback default first, `compute_doc` passes it through later.** Add the field to the consuming renderer with `doc_spec.get("field", default)` so it is testable and backward-compatible immediately (tests inject the field directly); wire the `compute_doc` pass-through in a later ticket. When the pass-through lands, the renderer needs no change and live output is unchanged because the demo's values match the prior defaults.
`Source: m-docbuilder-m2a t2 (data_col_start), t3 (table_style), t5 (pass-through)`

**Committed demo/tenant base files must carry the standard named styles and consistent branding across all sheets before the sprint runs.** A placeholder base file built from a minimal template lacks styles like `Heading 1`/`Table Grid`, so renderers fall back (warnings, gridless tables) and branding is asymmetric across sheets. Renderers should degrade rather than crash, but the asset must be regenerated with the needed styles + per-sheet branding before the milestone sprint — otherwise the gap is re-flagged every ticket.
`Source: m-docbuilder-m2a t1, t2, t3 (base-file gap flagged across four tickets)`

**Before re-flagging a carried review finding as "still open", verify it is actually unresolved.** A finding resolved in an earlier commit was re-flagged as open in two later reviews; each time the correction (already fixed in `<commit>`) had to be recorded. Check the current source/commit history for the fix before carrying a finding forward.
`Source: m-docbuilder-m2a t5, t7 (t4 F1 re-flagged after resolution in 6d1d382)`

---

## Learning — m2b-docbuilder

Findings that recurred across ≥2 tickets in the docbuilder m2b milestone, promoted per methodology §7.

**Remove `write_file` from an orchestrator's tools once every phase uses `--output FILE`.** When the last `write_file` user is converted to `--output`, the tool becomes dead capability — drop it from the agent's `tools:` list. Fewer available tools is a smaller surface for the LLM to improvise scratch files. This was the closing piece of the orchestrator scratch-artifact arc (8 → 1 → 0): `--output` on the scripts removed the large-blob round-trip, the explicit "don't investigate" rule removed the re-run-to-inspect habit, and dropping `write_file` removed the capability entirely.
`Source: m-docbuilder-m2b t3 (raised), t7 (confirmed: scratch 0 with tools: ["run_command"])`

**For a JSON env-var default in a shell script, use an `if [ -z ]` guard + single-quoted literal, not `${VAR:-{...}}`.** Bash's `${VAR:-WORD}` mis-parses nested `{...}` in the default WORD: when the var is *already set* to a value ending in `}`, it appends a stray `}`, producing invalid JSON downstream (a `Jason.DecodeError` at the trailing brace). Guard instead: `if [[ -z "${VAR:-}" ]]; then VAR='{"k":"v"}'; fi`. (And keep nounset-safe `${VAR:-}` in any `set -u` script.)
`Source: m-docbuilder-m2b t7 (sprint.sh DOCBUILDER_CONTEXT default; latent since m2a)`

**Factor cross-script plumbing into a shared `_helper.py` module with lazy heavy imports.** When several scripts in a use case share non-trivial plumbing (HTML table markup, Drive auth/navigation/upload), put it in one `scripts/_name.py` rather than duplicating or cross-importing between CLIs. Keep heavy third-party imports *inside the functions* (not at module top) so unit tests can import the helper — and the scripts that use it — without the dependency installed; only the code path that actually calls out needs it.
`Source: m-docbuilder-m2a t10 (_table_html.py), m2b t2/t5 (_drive.py: build_service/find_or_create_folder/upload_file with lazy googleapiclient imports)`

---

## Learning — m3-docbuilder

Findings that recurred across ≥2 tickets in the docbuilder m3 milestone (the context
builder), promoted per methodology §7.

**Derived values are computed by a deterministic script and written to a file; the LLM only orchestrates and never recomputes them — assert this with a byte-identical / end-to-end check.** When an agent must produce values that have real rules (a financial-year invoice sequence, a month-end date), put the rule in a Python script that writes the result to a `--output` file; the agent calls the script, reads the file back, and passes it downstream verbatim. Prove the LLM added nothing by diffing the agent-produced artifact against the script run directly (must be byte-identical), or by an end-to-end render whose output could only come from the script's values. This is the concrete, testable form of "scripts do, agents decide" — when it holds, the agent prompt can shrink to "detect intent → call script → present", which is far more reliable than asking the LLM to do the math.
`Source: m-docbuilder-m3 t3 (resolve_last_run.py; byte-identical confirmed_context.json), t4 (end-to-end render from the script-produced context)`

**When the implementation diverges from the milestone doc, adjudicate the intent, then update the doc — the milestone doc is the single source of truth, so a divergence is closed by changing code *or* the doc, never left as a silent mismatch.** Repeatedly the right call was to keep the (better) implementation and bring the doc to it: single-shot confirmation gate vs an interactive loop; absent-run-log → exit 0 (degrade) vs exit 1; a configurable `DOCBUILDER_CONTEXT_FILE` env var; `DOCBUILDER_AUTOCONFIRM` recorded as not-implemented. Each was adjudicated and the design-decisions table / done-check note updated in the same commit, so the next ticket (and the t5 runbook) is written against the truth rather than a stale spec.
`Source: m-docbuilder-m3 t2 (single-shot gate), t3 (missing-log degrade), t4 (DOCBUILDER_CONTEXT_FILE, DOCBUILDER_AUTOCONFIRM)`

**Pre-list a tool an agent will need next milestone-step, and verify stateful pipelines against their own output record (not a hardcoded value); reset accumulating fixtures for deterministic sprints.** Adding `run_command` to the context builder's `tools:` in t2 — before it was used — made the t3 wiring a prompt-only edit. For the t4 sprint, verifying rendered files against the orchestrator's `renamed.json` (its authoritative PHASE-D record) rather than a hardcoded `…30-Jun-2026…` made the check date-independent; and because `run_log.json` accumulates, the sprint must reset it to a known seed so "same as last month" resolves deterministically (production accumulates; the test seeds).
`Source: m-docbuilder-m3 t2 (run_command pre-listed), t4 (renamed.json verification + run_log seed reset)`

---

## Learning — rig-p9

Findings that recurred across ≥2 tickets in the rig-p9 milestone (Rig per-run env vars +
Docbuilder integration), promoted per methodology §7.

**`run_command` cannot set per-invocation env, and `sh`/`bash` are blocked — per-step env / shell sequencing must live in a `python3` script.** The `run_command` tool schema has no `env` field (`command`/`args`/`working_dir`/`timeout_ms` only), and the exec-server allowlist (`aetheris/native/aetheris_exec_server/src/runner.rs`, `PERMITTED_COMMANDS`) rejects `sh`/`bash` by basename. So an agent cannot do `sh -c "VAR=… cmd"` to set env, nor pass env through the tool. When a step needs per-invocation env (or any shell logic), put it in a Python script (`python3` is allowlisted) that uses `subprocess.run(env=…, cwd=…)`. Verify the allowlist, not just the tool schema, before assuming a command is runnable.
`Source: rig-p9 t3 (sh blocked + no env field → chain_docbuilder.py), t4 (.py heuristic in orchestrate_start)`

**`mix aetheris run` cannot be nested — a chained run must be top-level or sequential, never one agent run inside another.** A nested `mix aetheris run` (inside a running agent's `run_command`) fails: the inner run's `compile.aetheris_worker` does an unconditional `File.copy!` of the worker binary the outer run holds open → `ETXTBSY` ("text file busy"); there is no `--no-compile`/skip escape. To chain Aetheris runs, run the chain **top-level** (e.g. Rig spawns a Python script that runs the sub-agents sequentially) — each sub-run's worker exits and frees the binary before the next, exactly like a shell sprint. This is why the Rig Docbuilder chain is a top-level script, not a wrapping `.exs` agent.
`Source: rig-p9 t3 (nested mix aetheris run → ETXTBSY; verified runs docbuilder-ctx-orch-WRNyiQ/lsjxug), t4 (top-level .py via orchestrate_start)`

---

## Learning — m4-docbuilder

**`mix aetheris run` is single-shot — any design that requires an in-run human reply must be re-modelled as a stop-and-re-run pattern.** The harness has no human-reply channel and `ask_human` is intentionally excluded from the tool set. Interactive-loop designs (confirmation gates, clarification rounds, approval flows) resolve the same way every time: the agent performs its best single-pass (extraction, proposal, self-correction), then stops if human input is required; the operator's "reply" is a re-run with the additional information.
`Source: m-docbuilder-m3 t2 (confirmation gate), m-docbuilder-m4 t2 (clarification round)`

---

## Learning — m5-docbuilder

No recurring findings in this milestone (polish & fresh→render chain). Each t1–t3 review
carried at most one finding, none recurring across ≥2 tickets: t1 (the done-check smoke
command used wrong asset filenames + a `/dev/null` spec that fails JSON-parse → carried to
t4 as a docs fix), t2 (missing live-sprint evidence → re-ran, PASS), t3 (informational
`variant` optional-absent note). The single-shot standing instruction was promoted in the
m5 pre-milestone commit under `## Learning — m4-docbuilder` above.

---

## Learning — m6-docbuilder

Findings that recurred across ≥2 tickets in the m6 milestone (Jinja2 renderer + offer letter),
promoted per methodology §7.

**For a pipeline-integration ticket, run an end-to-end (or agent-eval) check beyond the ticket's stated unit done-check — cross-stage wiring defects pass the unit check and only surface when the real pipeline runs.** Twice the per-ticket done-check went green while the integration was silently broken, caught only by running the full chain: t3 — `compute_doc.py` rebuilt a fresh output dict and dropped `has_jinja`, so the invoice fell back to the Markdown renderer on the `.html.j2` and leaked `{{ }}` (the unit tests + the standalone `generate_html` smoke all passed; the `fetch_data→compute_doc→generate_pdf` end-to-end exposed it). t5 — the docx-jinja render branch over-matched the invoice's docx (`fmt==docx and narrative? and has_jinja?`), and standalone `generate_html.py` does not inject sheet `tables` (only `generate_pdf._narrative_html_jinja` does), so the invoice docx silently lost its Line Items table (the sprint's own assertions passed; opening the rendered `.docx` exposed it). Lesson: when a change touches a multi-stage pipeline (compute → render → rename, or a renderer shared by PDF and DOCX paths), add an end-to-end smoke or an agent-eval that inspects the *final artifact*, not just the stage you changed — and prefer narrowing a generic branch (`…and no_sheets?`) over assuming it only matches the intended bundle.
`Source: m-docbuilder-m6 t3 (compute_doc has_jinja passthrough), t5 (docx-jinja over-match → no_sheets? narrowing)`

**A generic renderer stays generic; pipeline-specific enrichment (sheet tables) lives in the caller, so every code path that renders must perform that enrichment — or be excluded.** `generate_html.py` is a pure Jinja2 renderer (template + context → HTML); the sheet-table injection (`context["tables"] = render_table(...)`) lives in `generate_pdf._narrative_html_jinja`, the PDF caller. The DOCX path that called `generate_html.py` directly therefore had no tables. The fix kept the renderer generic and routed table-bearing docs away from the table-less path, rather than duplicating injection logic into `generate_html.py`. When two output paths share a generic renderer, either both callers enrich identically or the path that can't enrich is restricted to inputs that don't need it.
`Source: m-docbuilder-m6 t3 (tables injected in generate_pdf, not generate_html), t5 (docx path lacked injection → no_sheets? guard)`

---

## Learning — m7-docbuilder

**Write a done-check / sprint command against the *verified* runtime shape, never an assumed one — check the actual data structure, export status, and arg convention before writing the command.** This failure recurred four times across two milestones as different surface manifestations of one root cause: a command was written against what the author *assumed* the shape was, and it broke (or, worse, passed trivially) because the real shape differed. (1) m5 t1 — the §t1 smoke used wrong asset filenames + `--spec /dev/null` (a path arg fed a non-existent/invalid spec), so `grep -c '{{'` returned 0 *trivially* (the renderer never ran). (2) m6 t4b — `compute_doc.py --template X` assumed a flag, but the template is a *positional* arg. (3) m7 t2 — the catalogue done-check did `for e in cat`, but `catalogue.json` is `{"tenant_id":…, "doc_types":[…]}` (a dict); it must iterate `cat["doc_types"]`. (4) m7 t3 — a sprint line read `os.environ['DOCBUILDER_CONTEXT']`, but the value was a shell var (not exported), so under `set -euo pipefail` the `KeyError` killed the run before the agent step; fix was to pass it via argv. **Before writing the command: inspect the file/JSON (`\d`, `head`, a one-line `json.load(...).keys()`), the CLI signature (`--help` / argparse), and whether a var is exported — then write the command to match. A done-check that can pass without exercising the thing it checks is worse than no check.**
`Source: m-docbuilder-m5 t1, m-docbuilder-m6 t4b, m-docbuilder-m7 t2, t3`

---

## Learning — BL-007 (fork: Rig UX + provenance/determinism contract)

Promoted per methodology §7 after the BL-007 milestone-end ritual. Adjudicated
2026-07-20; wording authored by claude-ui, committed by claude-code.

**The packet is the artifact that travels; content in any other channel does not exist.** This supersedes the earlier wording — *a packet section referenced is a packet section absent* — which named existence-in-repo as the failing channel and so did not cover the two that followed. Three channels have now failed: a section committed to the repo and cited rather than inlined; a section placed in the chat response beside the report file, when only the file is relayed; and a **disposition commit, which travels as a claim about its content rather than as content**. The operational split: mechanical closures — a label qualified, an anchor added, a count corrected — stay settleable by a grep count; anything that authored a *mechanism* or a *judgment* is quoted verbatim in the packet, with its before and after. Regenerate rather than reconstruct.
`Source: m-docbuilder-m1 t4, t8; BL-007 t3; t1a, 2026-08-06 (docs/reviews/t1a-review.md:50–51 — the disposition-commit channel, filed there as a §7 promotion candidate: "Mechanical closures stay grep-settleable; anything that authored a mechanism gets quoted").`

**A packet's sprint section shows the run's full output, or states what it elided and why.** The arms are the assertions; the output is the evidence, and a packet that quotes only the `[OK]` lines has published the assertions with the evidence removed. Every sprint report in the m4 cycle did exactly that, while the run also emitted a containment probe, two harness warnings, an orphan-sweep line and an artifact listing that no packet ever carried. This is **Complete-output** bound to the one artifact that travels: elision is allowed, silent elision is not — say what you cut and why, so a reader can tell a clean run from a clean excerpt.
`Source: m4-cloudcost t5c addendum §C; first applied at m4 t5c r0's packet §7. **Promoted as a packet rule, not as a recurrence-derived learning entry** — it lands beside the packet rule above rather than in a §Learning source list, and it is the one m4 promotion candidate that was never a recurrence claim. Its argument in a single instance is the truncated-capture carrier of `Every claim has a truth-maker` (harness `CLAUDE.md`): at m4 t5b r0 a `| tail -60` produced a tally reported as the run's own, and no reader could have told from the packet.`

**An elision justified by "this is inlined above" carries the check that establishes it, or the diff is not elided.** The entry above allows elision and forbids *silent* elision; this is the next thing that goes wrong once you have said what you cut. A packet elided a new file's diff on the ground that its content appeared verbatim earlier in the same packet. The assertion was true of most of the file and read as true of all of it — the omitted remainder held that file's own **measurement stamp**, the paragraph binding every citation in the inlined sections to a commit, so hundreds of verbatim lines were ratified without the sentence saying what they were measured at, and no reader of the packet could have told. So an elision names the ranges it covers **and the lines it does not**, and carries the check that establishes the correspondence: diff the inlined ranges against the committed file and publish the result, rather than asserting they match. And the same check is owed by any block published as VERBATIM, where nothing declares an elision at all. "Verbatim" is a claim about completeness, and a capture command can silently defeat it: a `sed` range prints through its matching line and stops, so a block whose last line is a wrapped sentence ends on a line that reads finished. Nothing in the published text marks the cut — this is the truncated-capture carrier of `Every claim has a truth-maker` (harness `CLAUDE.md`) wearing a label that asserts the opposite. So a block labelled verbatim carries a diff against its committed source, with the result published; a block that carries no such diff is quoted, not verbatim, and is labelled quoted.
`Source: m5-cloudcost t1 r1, 2026-08-10 — claude-code closing a reviewer finding and finding the stronger form of it; the inlined §1+§2 were byte-identical to the committed file on both md5s, and carried 577 of its 634 lines. One recorded instance, and the count is not the basis: this extends the entry above, whose own Source records it as **promoted as a packet rule, not as a recurrence-derived learning entry**. §7's ≥2 is a recurrence filter and does not reach a rule of this kind, so the bar is **not met because it does not apply** — this is not an exception to it. Agents rather than harness because the packet-rule family lives in this section; duplication into both files was considered and declined, the two preambles being near-duplicates with no byte-identity check and drift_check having none either. Promoted at the m5 close, on the human's referral of the question to the reviewer. The VERBATIM half was added 2026-08-25, inside this entry rather than beside it, on the wiring-list repair rule under §Learning — m6-cloudcost: the clause was right and its subject short. It lands with NO INSTANCE, stated rather than omitted. The round that produced it published its block under a verbatim label and a diff established the block was short, but the round's evidence lives in a review packet — sent by default to a session scratchpad, and so in neither tree — and the diff hunk id it was identified by resolves nowhere in either repo. The rule does not depend on the instance.`

**A packet publishes the invocation that produced its result — the command that actually ran, read
only after that command exited.** Two failures, one rule. A packet published a *different*
invocation than the one that ran — one that had failed under a persisting `cd` — beside an `exit=`
literal bound to nothing and a WARN count the published command had not produced: the verification
was sound and the artifact was false. And a gate capture was assembled while its producer was still
running, taking 69 of an eventual 184 lines with every published line accurate — caught by the line
count, because **a partial capture is indistinguishable from a complete one by content alone**. So:
transcribe the command that ran and the status it returned, or re-run and publish the re-run;
never re-run to illustrate a result obtained some other way, because a re-run can bind differently
and the difference is invisible in the output. This is **Packet-integrity** (harness `CLAUDE.md`)
on the assembly side — packets are generated, not retyped.
`Source: hc round close 2026-08-09 (hc-e r4), distilling hc-consolidation.md §Promotion candidates,
"the packet is the artifact that travels, and packet assembly is itself a place claims are made".
The first instance is hc-c r1, diagnosed by claude-code at hc-c r2 §8a correcting the reviewer's
finding; the second is hc-e's opening edit, caught before publication. The 69/184 figures are
claude-code's account from that packet's preamble — **those** packets are not committed, so they
are not reconstructible from the tree, and the rule does not depend on them.`
`[Narrowed 2026-08-21 at ds t3. It read *"packets are not committed in either repo"*, which is
false: `git ls-files | grep -i packet` returns five committed packets in this repo, all under
`docs/reviews/`, and none in the harness. The default is uncommitted — the standing loop sends a
packet to a session scratchpad — but the general claim is not the one the argument needs, and the
narrow one is true and checkable. `docs/reviews/` itself is tracked in both repos and holds many
review files; a claim about *packets* is not a claim about that directory.]`

**A background job's completion notification fires when the LAUNCHING SHELL exits, not when the
job does — so `nohup … &` is reported done immediately while the job runs on, and the output read
at that moment is a partial indistinguishable from a complete one.** This is the mechanism by
which the rule above — *read only after that command exited* — gets broken by an author who
believes they obeyed it: nothing in the notification, the exit status or the output says the job
is still writing. Wait on the process itself, or confirm it is gone before reading.
`Source: the BL-182 rounds, 2026-08-23. A tally was read from a results file while the job writing
it was still running, and the row published *"the one member settled"* where five had; the same
partial also carried the diagnosis *"a latency class that is not a content class"*, which the
completed run falsified — two of the six then-unsettled members disagree on content. One partial
read, one wrong figure and one wrong diagnosis, both in a row whose own subject is recorded
commands that do not mean what their author verified. Both corrections are in that row in
`docs/backlog-2026-06-closed.md`. The behaviour was re-established directly at BL-181 before this
was written: a `nohup` job writing one line a second reported done at launch, and three successive
reads of its file returned 4, 7 and 8 lines, every one of them well-formed.`

**The packet is written as the ticket runs, not assembled at the end.** Open the packet file at the
start and append each section at its stage boundary, before moving on. A packet reconstructed at
the end from whatever the session still happens to be holding cannot be compacted around, and a
crash costs the ticket rather than one stage. This is the assembly-side companion to the rules
above it: they govern what travels and what it must be made of, this governs when it is written
down — and it is what makes them cheap to obey, since a section appended at its own stage boundary
is transcribed from a command that has just exited rather than recalled.
`Source: the cc:prompt preambles of 2026-08-16, promoted at the handoff of 2026-08-17, whose own
packet was written this way as its first application. It lands in this family rather than under
§Definition of done because it is a rule about the packet, and the packet-rule family lives here.`

**No action past a gate until that gate has run and its result is on the record** — covering doc-order gates, test gates, and publish/merge gates alike. Three instances in one milestone, same muscle, different artifact: a doc edited ahead of the gate that should have preceded it; a rider acted on before the milestone doc carried it; and both branches pushed on a "push both branches" instruction before the acceptance e2e was reported green, inverting the agreed reorder → gates → e2e → commit → push order. All three were recoverable only because the held-push discipline caught them — the rule is what makes the discipline unnecessary rather than load-bearing. A cross-repo change needs a cross-repo done-check — any gate that runs in one repo silently passes omissions in the sibling (repo-scoped `git add -A` + single-repo drift check let a one-repo edit push under a two-repo claim).
`Source: BL-007 t2, t4 (×2); b1 post-push correction, 2026-07-21 (d831220)`

**A backlog row gets a GitHub issue when a cycle takes it, and not before; `(#TBD)` in a row's heading means there is no issue and none is owed.** Declared here because it has been transmitted by imitation since the file was created and stated nowhere: every row filed without an issue carries the marker, every reader has copied it, and no document says what it means — so a reader meeting it for the first time cannot tell *"no issue yet"* from *"issue number not yet transcribed"*, and only the second reads as a defect owing work. It is the first. A row is a unit of work that has been *recorded*; an issue is a unit of work that has been *scheduled*, and the backlog deliberately holds far more of the first than anything schedules — which is R23's whole ground. The existing headings are **not** edited to say so: the marker is already uniform, the change would touch every unscheduled row in both the open file and the archive, and the defect was never the marker but the absence of this sentence.
`Source: declared 2026-08-21 at the ds close, on the ds cycle's own evidence — it ran the first tracker this methodology has used since the backlog was created, cut issues for its five tickets, and gave an issue to none of the findings it raised (`docs/milestones/hc-consolidation.md` R30). That is the rule operating; it had simply never been written down. Lands beside the row-filing rule below because that one says when a ROW is owed and this one says when an ISSUE is, and the two questions are adjacent and were being answered by different means — one by a standing instruction, the other by imitation.`

**A deferred finding gets a backlog row in the same round it's deferred — prose in a packet or notes files nothing.** Three times this milestone a deferred item survived only because a later reviewer re-noticed it; prose has no executor. **And the row must be one that stays open: a finding recorded inside a row the same commit closes has a record, not an executor.** That satisfies the rule in letter and defeats it in substance, and the defeat is invisible precisely because the row it lives in is the row being closed — so name the row you are putting it in, and if that row is being disposed in this commit, file a new one.
`Source: BL-007 t1, t2, t3; the closing clause is a precision on the same rule from m5-cloudcost t2, one recorded instance — r0 recorded a residue inside BL-070's disposition and the same commit marked BL-070 DONE, so the residue had no executor from the moment it was written, and it survived only because t2 r1 re-noticed it. Named as a failure mode of this rule rather than promoted as one of its own, because it is not derivable from the claim above: a session applying that claim correctly can still land here.`

**Decisions that constrain ticket N+1 land in N+1's README section before its session starts — implementation notes don't travel forward on the prompt path.** The next session reads its ticket text and contract refs, not the previous ticket's notes; three consecutive tickets proved the carry works when done and bites when skipped.
`Source: BL-007 t2, t3, t4`

**A correction chases the corrected claim into every doc that adopted it, in the same round — and a verified citation decays the moment the file moves; re-verify at HEAD before reuse.** A verification pass's own output goes stale when a later pass corrects it (three instances), and two t5 instances show the decay form: a mirror citation and a line number that was right when read. This is the residual of the "cited-means-read" class, which covers claims *never* verified; this one covers claims verified once and reused after they rotted.
`Source: BL-007 t2, t4, t5`

**One symptom can have several mechanisms: verify a fix against the real counterpart in the operator's environment, not a simulation — and a fix proven for one face doesn't close the symptom until the observed face is captured directly.** Six review rounds at BL-007 t4: a real fix for one face (the store `:busy` crash under a per-statement lock race) was mistaken for closure of a symptom actually caused by another (the StrictMode-dead mount guard), and every simulated adversary passed where the field failed — the simulation verified the simulation. Promoted below §7's ≥2-ticket threshold by explicit human ratification, 2026-07-20 — six rounds of cost within one ticket judged sufficient evidence, exception recorded here so the override is auditable.
`Source: BL-007 t4 r3–r6`

**Promotion wording travels as a review-file artifact, not chat: claude-ui's §7 promotion draft lands in `docs/reviews/` before the promotion commit is cut.** Class E's mechanism hit this milestone's own promotion pipeline twice — the P3–P6 relay gap, then P6 again across the session restart — because the authored wording existed only in conversation.
`Source: BL-007 t5 (§7 ritual, ×2)`

---

## Learning — m6-cloudcost (GitHub: provider four, the first consumption-class adapter)

Findings that recurred across ≥2 tickets in the m6 milestone, promoted per methodology §7 and
ruled at the close, 2026-08-14. All three land here rather than harness-side because destination
follows **which family an entry joins**, not which file a ticket's `Touches` happened to name —
the correction gc's close owes, recorded on BL-150.

**A count in prose about a growing set is de-numeralised, not corrected — correcting *seven* to *eight* re-arms the same trap for the next member.** When a sentence states the size of a set that will grow (canonical types, providers, wiring places, credential keys), the number is a second surface that drifts from the enumeration beside it, and fixing the number preserves the mechanism that broke it. Rewrite to *"the rows below"*, *"the `CLOUDCOST_*` keys"*, *"the places listed here"* — and check the lines the ticket is itself writing, which is where two of the instances came from. **Distinguish three shapes before editing**: a *count claim* whose argument the number does not carry (de-numeralise), a *data enumeration* such as a table row or a literal set (extend it; it is not a count), and a count whose argument genuinely needs the figure (keep it, and say why).
`Source: m6-cloudcost t1 (the sweep that minted the rule, and two count-bearing lines the ticket had just written, de-numeralised before the edit landed), t2b (*"Correcting five to seven would have re-armed the same trap for provider five"*), t4 (fired on both units the ticket named and found two more of the class beside them).`

**A wiring list's clause can be right while its enumeration is short — repair it as an incomplete enumeration, not as a missing clause.** When following a "how to add one of these" list turns up a place the list does not name, the temptation is to add a clause. Usually the clause is already there and correct, and only its instance list is stale — so the fix is to extend the enumeration and say that is what happened, because adding a second clause covering the same ground creates two surfaces that will disagree at the next addition. **And a generated artefact with consumers is a wiring place in its own right**: a document read by a program is not documentation, and the one place a list of this kind reliably forgets.
`Source: m6-cloudcost t2b (followed the list, found `KNOB_CONSTANTS` and *every prose enumeration of the provider set* unnamed), t4 (found the same clause four instances short, took it to eight, and added the capability-matrix regeneration as a place — `docs/capability-matrix.md` is read whole into the planner's system prompt, so a script absent from it is a script the planner cannot plan; BL-090 closed exactly this for provider three without adding the regen to the list, and it was stale again nine days into provider four).`

**A live run exercises only the arm its data happens to be in; every other arm needs a named owner or a stated closing condition — never silence.** A green done-check over real data proves the branch the data selected, and says nothing about the branches it did not reach. So enumerate what the run did *not* render, and give each unexercised arm one of two things: **a ticket that inherits it**, or **a condition that closes it on its own, stated with what would satisfy it**. What is forbidden is the third option, leaving it unmentioned — that is how an arm reaches production having never run anywhere but a unit test. **And a hand-invoked demonstration discharges the render half only**: run it with a control at the real inputs reproducing the live result, label it as not-a-sprint, and split the obligation rather than declaring it closed.
`Source: m6-cloudcost t2c (enumerated what neither of its live legs rendered and named t3 as the inheriting ticket rather than leaving a gap belonging to nobody), t3 (discharged the render half by a labelled hand-invoked chain whose control at the real date reproduced the sprint's zero exactly, and split the rest: *"That closes on its own the first time a seat on this account crosses 30 days idle. No ticket owns it and none should."*).`

---

## Learning — BL-152 (the repo-root `pytest` gate)

Promoted 2026-08-16 by the arbiter at BL-152's closure, and keyed by the **backlog row**
rather than a milestone because BL-152 belongs to none — the precedent is
`## Learning — BL-007` above, which is keyed the same way for the same reason. Neither
entry rests on §7's ≥2-ticket recurrence bar; both are arbiter-issued at a row's close, and
the first of the two is a defect found **in the arbiter's own ruling**, which is not a shape
recurrence can measure.

**A criterion phrased as *"would it pass"* exempts every test that guards itself with a skip — and that is usually the exact population the criterion was written for. Phrase it as *"would it do its work"*.** A self-skipping test *passes* in the environment it was written to exclude itself from, so a pass-phrased criterion answers yes for precisely the tests that most need the marker; the criterion then reads as satisfied while classifying nothing. The failure is quiet in the way this repo's **Silent-wrong-answer** class is quiet — the criterion returns a well-formed verdict on every test, and the verdict is wrong only on the population that motivated it. When writing a classification rule, apply it out loud to the instances that prompted it **before** shipping it, and check that it separates them rather than sweeping them into one bucket. See the `integration` marker's shipped statement under §Definition of done, which counts a silent skip.
`Source: BL-152, 2026-08-16 — the criterion was issued by the arbiter and corrected by the implementing session, which found that applied literally it would have unmarked all ten of the tests it had just been written to justify. Recorded because the defect was in the ruling, not in the work.`

**A count recorded in prose carries the command that reproduces it, or it decays into a claim.** This is the operational half of the harness rule *a count names the commit it was derived at, or a pointer replaces it* — naming the commit tells a later reader the figure is stale; naming the **command** lets them replace it. The difference is not rhetorical: BL-152's integration- and dormant-population figures are true at one commit and move the moment anyone marks a test, and the ones that shipped beside a reproducing invocation can be refreshed in seconds while the ones that did not must be re-derived by hand. So write *`N`, from `<command>`* — never a bare *N* — for any figure over a population the repo will keep changing.
`Source: BL-152, 2026-08-16. The contrast is inside one ticket: the gate's own deselection counts ship with the command that prints them (`CLAUDE.md` §Definition of done, and the gate's summary line), while several per-scope figures in the row body do not.`

---

## Learning — the 2026-08-16 export boundary

Keyed to the **boundary** rather than to a milestone or a single row, on the precedent of
`## Learning — BL-007` and `## Learning — BL-152` above: both are keyed to the unit of work that
produced them, and this boundary's three passes are that unit. Arbiter-issued at the close of the
second amendment; §7's ≥2-ticket recurrence bar is not the basis and does not reach a defect found
once, inside the instrument that found it.

**Restore a mutation from a working-copy backup, never from git, when the file carries uncommitted
work.** `git checkout -- <file>` restores to **HEAD**, so run against a file holding the very edit
the mutation was testing it silently destroys that edit and leaves a file that looks restored. The
two states are indistinguishable by the thing you are watching — the test goes green again either
way, because the mutation is gone either way, and the uncommitted feature is gone too. Copy the
file aside first and restore from the copy, then verify by sha against that copy.
`Source: the 2026-08-16 export boundary, first amendment. A mutation on `scripts/repin_manifest.py`
proved two new tests load-bearing; the restore was `git checkout --`, which reverted the file to
HEAD and destroyed the uncommitted `git_commit_date` change the pass had just written. Caught only
because the verification step counted occurrences and reported `0` — the tests themselves would
have gone green on the reverted file and said nothing. The edit was re-applied and re-verified, and
every later restore in the boundary used a working-copy backup checked by sha. This is the
operational other half of the harness rule **the mutation test has two halves and the restore is
the second one — verify it, never assume it**, which establishes that a restore needs its own
control; this says what a restore must not be *made of* when the file is dirty.`

---

## Learning — ds

Promoted 2026-08-21 at the ds cycle's close. Keyed to the **cycle**, on the precedent of
`## Learning — BL-007`, `## Learning — BL-152` and `## Learning — the 2026-08-16 export boundary`
above — each keyed to the unit of work that produced it.

**The single promotion is the existing de-numeralisation rule extended, not a new rule.** It lives
under `## Learning — m6-cloudcost` — *"a count in prose about a growing set is de-numeralised, not
corrected"* — and it is landed there in its own family; what follows says what this cycle found the
same mechanism doing in two shapes that carry no number at all. Recorded here rather than folded
into that entry because the entry is stated in terms of counts throughout, and rewriting it around
a wider subject would destroy the worked instances that make it usable.

**The mechanism is not the number. It is a second surface that states what another surface
determines, and drifts from it silently.** A count is the commonest carrier because a count is the
cheapest second surface to write. Two more, both found this cycle:

- **A label or name that resolves in one document, used as if it resolved in another.** A `§`
  reference, a marker, a status word or a row id is defined relative to *its own* document's
  vocabulary; carried into a second document it still parses, still looks resolved, and now points
  at whatever that document's vocabulary happens to make of it — or at nothing, which reads the
  same. The ground: a name is a pointer whose target is supplied by context, so moving the name
  without the context silently repoints it, and nothing at either site records that the two
  vocabularies were ever different. Resolve a carried name against the document you are putting it
  in, or repo-qualify it so it cannot be resolved against the wrong one.
- **A negative asserted from session memory rather than from a search.** *"Nothing else says
  this"*, *"this appears nowhere else"*, *"no other document carries it"* — each is a claim about a
  population, and a session that has read part of that population feels entitled to it. The ground:
  what a session remembers reading is not the set it read, still less the set that exists, and the
  gap is invisible from inside — a remembered negative and a searched negative are written in the
  same words. This is the **positive control** rule (harness `CLAUDE.md`, Silent-wrong-answer)
  reached one step earlier: that rule governs a negative you *ran a command for*, this one governs
  a negative you did not.

Both are the de-numeralisation rule's subject with the number removed, so both take its remedy:
where a pointer will do, carry no restatement at all.

---

**And four operational forms this cycle established, recorded because they worked and would
otherwise travel by imitation, which is what the `(#TBD)` rule above exists to stop happening
again.** No instance list: enumerating a cycle's occurrences of each is a count over a set, which
is the rule this section promotes.

- **Predict the manifest WARN **set**, not a count, and publish the prediction in the packet before
  the run.** A set is falsifiable member-by-member against the run's own output; a count agrees with
  the wrong set as readily as the right one, and check 8's WARN population is a function of the
  manifest's staleness backlog rather than of the commit under test (§Definition of done carries
  why). Publishing it *before* is what makes it a prediction rather than a description.
- **A correction round writes into the committed implementation notes it is correcting, not into a
  new document.** The notes file is what the next round in the arc opens; a correction living
  anywhere else has been made and not delivered. The dated block goes at the corrected passage,
  which keeps the superseded wording readable beside its replacement.
- **Cite a packet by filename.** Packets are, by default, sent to a session scratchpad and are not
  in either tree, so a citation into one is unresolvable by anybody but its author — naming the file
  states that the source is a packet and lets a reader see that they cannot open it, which a
  paraphrase presented as repo state does not.
- **Open the packet with a six-item head.** A fixed head is a checklist the reader can run against
  the packet rather than a shape the author chooses per round, and the items that most often go
  missing — the baseline, the deviations, what is owed — are exactly the ones no reviewer can
  discover is absent. The head is written in PLAIN LANGUAGE and the body is not. A head is a
  checklist the reader runs against the packet, and a checklist written in the packet's own
  compressed register cannot be run by anyone who has not already read the packet — which is the
  one reader it exists for. The body moves the other way: it is evidence, and the standing packet
  rules already forbid compressing it. So the two registers are not a matter of taste per round,
  and a head that reads like the body is a head that has stopped working.

`Source: the ds cycle, 2026-08-17 to 2026-08-21 — t0, t1a, t1b, t2, t3 and this close. The two
sub-classes each recurred across more than two of them, meeting §7's bar; the four operational forms
are promoted as forms rather than as recurrence findings, on the precedent of the packet rules under
`## Learning — BL-007`, whose own Source records the same basis. The cycle's rulings are
`docs/milestones/hc-consolidation.md` R28–R30 and the dated entry on R25; its close is
`docs/milestones/ds-milestone.md` §The close. The packet-head item's PLAIN-LANGUAGE half was added 2026-08-25 as a widening of that item and not as a sibling: the two-register convention was applied in every cc:prompt of the 2026-08 boundary arc and written down nowhere, which is the BL-162 shape — a rule alive only in prompt preambles. Nothing already in the item was rewritten.`
