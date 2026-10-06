# aetheris-agents

Use-case agent implementations built on the [Aetheris](../aetheris) harness.
Each use case is a self-contained directory with Python scripts, Elixir agent
files, tests, and docs.

No Elixir source lives here — only `.exs` agent scripts that the harness
evaluates. All sprint and agent commands run from `../aetheris/`.

---

## How context reaches Claude

Project knowledge holds a small kernel. The rest of the corpus stays in git and is
fetched on demand through the GitHub connector.

- [`docs/project-knowledge-manifest.md`](docs/project-knowledge-manifest.md) — the
  surface column says where each document lives; the connector notice says how to
  reach the fetched ones.
- [`../aetheris/docs/aetheris/research/hybrid-context-design-2026-08.md`](../aetheris/docs/aetheris/research/hybrid-context-design-2026-08.md)
  — the design and its measurements, in the harness repo.
- [`prompts/bl-002-refresh-project-knowledge.md`](prompts/bl-002-refresh-project-knowledge.md)
  — run this to refresh the store.

---

## Use cases

**`docs/use-cases.md` is the registry** — the committed declaration of what the use cases are
and which are dormant. This table's first column is checked against it by `drift_check.py`'s
`use_case_registry` check; the Status column below is a reader's summary of progress, not the
status the registry declares.

| Directory | What it does | Status |
|-----------|-------------|--------|
| [`payslip/`](payslip/) | Generate monthly payslips from payroll CSV; parallel sub-agents per employee | ✅ |
| [`drive/`](drive/) | Download payroll CSV from Google Drive; upload generated PDFs back | ✅ |
| [`email/`](email/) | Email each employee their payslip PDF | ✅ |
| [`api/tenant/`](api/tenant/) | TAP protocol, tenant side — agent-to-agent enrollment via ct.stu API | ✅ T1–T4 |
| [`api/gateway/`](api/gateway/) | TAP protocol, gateway side — intent execution against ct.stu | ✅ T1–T4 |
| [`boxy-pipeline/`](boxy-pipeline/) | Catalog and sales-order extraction; pure Python, no Aetheris agent | ⏸ dormant since 2026-08-16 |
| [`ct-bot/`](ct-bot/) | CampusTrack panel agents — main, sanitize, parse, validate, compose, suggestions (chat path; not the TAP track, no ct-api) | 🚧 T1 — main agent landed; T2–T7 open |
| [`cloudcost/`](cloudcost/) | Multi-provider cloud spend collection and reporting | ✅ |
| [`docbuilder/`](docbuilder/) | Branded document generation — invoices, offer letters (PDF + DOCX) | ✅ |
| [`eduloka/`](eduloka/) | Discovery milestone | ✅ |
| [`provenance/`](provenance/) | Corpus classification, migration and search over client documents | ✅ |

### Payslip pipeline

```
drive (download)  →  payslip (generate)  →  drive (upload)  →  email (deliver)
```

### TAP protocol track

```
TAP v0 design  →  uc-api-agent T1-T4  →  T5 durable state (planned)
```

---

## Getting started

```bash
# Install Python deps (mise-managed Python 3.12)
python3 -m pip install pytest boto3 pika

# Run tests for a use case
python3 -m pytest api/tenant/tests/ api/gateway/tests/ -v

# Run an agent (from the aetheris sibling repo)
cd ../aetheris
mix aetheris run ../aetheris-agents/api/tenant/agents/at1cmd.exs
```

---

## Repository conventions

See [`CLAUDE.md`](CLAUDE.md) for the full reference. Key points:

**Scripts do; agents decide.** Python handles computation, file I/O, and API
calls. Elixir agent files contain only the `RunConfig` or `OrbConfig` struct.

**`__ENV__.file` for sandbox_path.** Always resolve paths relative to the
agent file, not `File.cwd!()`.

**`context_strategy: :full` for short-lived agents.** `:rolling` truncates old
messages and can leave orphaned `tool_use_id` references, causing HTTP 400.
Use `:full` for any agent that runs fewer than ~20 steps.

**Two repos, two commits.** Sprint cases in `../aetheris/scripts/sprint.sh` are
a separate commit from the agent files here. Do not merge without review.

---

## Docs

| Document | Contents |
|----------|---------|
| [`CLAUDE.md`](CLAUDE.md) | Conventions, commands, critical patterns |
| [`docs/agent-creation-guide.md`](docs/agent-creation-guide.md) | How to build a new use case |
| [`docs/uc-api-agent-design.md`](docs/uc-api-agent-design.md) | TAP protocol architecture |
| [`protocol/TAP-v0-design.md`](protocol/TAP-v0-design.md) | TAP v0 spec |
| [`ROADMAP.md`](ROADMAP.md) | What's next |
