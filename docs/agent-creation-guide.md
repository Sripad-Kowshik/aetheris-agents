# Agent Creation Guide

Practical guidelines for building new agents in `aetheris-agents`.
Based on the uc-payslip experience. Updated as new agents are built.

---

## Core principle: scripts do, agents decide

The most important design decision for any new agent:

| LLM (agent) | Script (Python/shell) |
|-------------|----------------------|
| Read context and decide what to do | Parse and transform data |
| Choose which employees/items to process | Apply business rules |
| Orchestrate parallel sub-agents | Arithmetic and formatting |
| Synthesise results into a report | Read and write files |
| Understand ambiguous instructions | Call external APIs deterministically |

**Never ask the LLM to generate file content programmatically.**
If you catch yourself writing "the agent will construct the HTML and call
write_file", stop. Write a Python script that constructs the HTML. The agent
calls the script.

The test: could a junior developer write a pytest for it without involving
Aetheris? If yes, it belongs in a script.

---

## Repository structure

Each use case is self-contained:

```
aetheris-agents/
  {use_case}/
    agents/
      {use_case}_orchestrator.exs   # entry point
    data/
      sample_{data}.csv             # committed (anonymised)
      {template}                    # committed
      .gitignore                    # excludes real data and output/
    docs/
      t*-implementation-notes.md    # written after each ticket
    output/                         # gitignored
      .gitkeep
    scripts/
      {computation}.py              # deterministic logic
      {generation}.py               # file generation
    tests/
      conftest.py                   # skip markers for missing tools
      test_{computation}.py
      test_{generation}.py
    milestone.md
    README.md
    runbook.md
```

`.gitignore` rules for every use case:
```
# Real data — never commit
data/{real_data_file}

# Generated output — local only
output/*
!output/.gitkeep
```

---

## Agent file conventions

### Always use `__ENV__.file` for `sandbox_path`

```elixir
agent_root = Path.expand(Path.join(Path.dirname(__ENV__.file), ".."))

%Aetheris.RunConfig{
  sandbox_path: agent_root,
  ...
}
```

This makes the agent work regardless of where `mix aetheris run` is invoked.
`File.cwd!()` returns the aetheris repo directory, not the use-case directory.
`__ENV__.file` is always the script's own location.

### Always set `overlay_base_dir: nil` when output must persist

```elixir
overlay_base_dir: nil,  # intentional — output files are the deliverable
```

OverlayFS captures writes in a per-run `upper/` layer. Use it for agents
that modify source code or config files. Never use it when the output files
(PDFs, reports, generated docs) must survive the run.

### Context strategy for multi-step agents

```elixir
context_strategy:  :rolling,
max_context_steps: 6,
```

Prevents context overflow on longer runs. `:rolling` is cheaper than
`:summarise` and sufficient for most orchestration work where the LLM
only needs recent context to decide the next step.

### Standard RunConfig fields

```elixir
%Aetheris.RunConfig{
  run_id:            "{use_case}-orch-#{Aetheris.ID.generate()}",
  mode:              :record,
  provider:          "anthropic",
  model:             "claude-haiku-4-5-20251001",
  label:             "{Use Case} Orchestrator",
  sandbox_path:      agent_root,         # always __ENV__.file based
  overlay_base_dir:  nil,                # nil unless you need isolation
  max_steps:         20,                 # orchestrators rarely need more
  max_spawn_depth:   2,                  # prevents runaway recursion
  context_strategy:  :rolling,
  max_context_steps: 6,
  tools:             [...],
  system_prompt:     "...",
  user_prompt:       "..."
}
```

### Runtime parameters in orchestrators

Use `System.get_env/1` at eval time and interpolate into the prompt string.
Build the prompt as a named variable first — do not inline `System.get_env`
calls inside the struct literal:

```elixir
month = System.get_env("PAYSLIP_MONTH") || raise "PAYSLIP_MONTH not set"
system_prompt = """
  Send payslip emails for #{month}.
  ...
"""

%Aetheris.RunConfig{
  system_prompt: system_prompt,
  ...
}
```

This keeps the struct readable and makes the variable visible at the top of
the file where it is easy to spot and validate.

---

## Orchestrator patterns

### Bank Statement HTTP MCP agent

`agents/bank_statement_agent.exs` loads `mcp/http/bank-statement/config.exs`
into `RunConfig.mcp_servers`, following the environment-gated registration pattern
in `provenance/agents/search_agent.exs`. Its native `tools` list is empty:
the harness discovers descriptions and input schemas through MCP `tools/list`
and invokes the selected tools through `tools/call`. There is no local statement
processing logic or manually defined MCP schema.

Set these variables in the environment inherited by the harness:

| Variable | Meaning |
|---|---|
| `BANK_STATEMENT_MCP_ENABLED` | Only the exact value `true` enables the server; otherwise no server is registered. |
| `BANK_STATEMENT_MCP_URL` | Required when enabled: the full MCP endpoint, including its path. HTTPS is required except on loopback. No embedded credentials. |
| `BANK_STATEMENT_MCP_TIMEOUT_MS` | Positive integer; default `30000`. |
| `BANK_STATEMENT_MCP_HEADER_<NAME>` | Authentication/context header value. The suffix becomes lowercase with underscores replaced by hyphens. For example, `BANK_STATEMENT_MCP_HEADER_AUTHORIZATION` sends `authorization`; `BANK_STATEMENT_MCP_HEADER_X_TENANT_ID` sends `x-tenant-id`. Use the names and values required by your server; no backend-specific headers are assumed. Empty or multiline values fail evaluation. |
| `AETHERIS_PROVIDER`, `AETHERIS_MODEL` | Standard provider/model overrides; defaults to Anthropic and `claude-haiku-4-5-20251001`. The provider's credentials must also be configured. |

Keep credentials in your local environment/secret manager, not committed files.
Use an authorized test account: the harness records tool inputs/results, which
can contain sensitive financial data. Supply every required auth/context header
before running; authorization errors must not be treated as empty statements.
The agent uses a general fixed prompt. For a specific task, edit its `user_prompt`
in `agents/bank_statement_agent.exs` before running it.

From the sibling `aetheris/` harness, after setting the URL and server headers:

```bash
export BANK_STATEMENT_MCP_ENABLED=true
timeout -k 5s 180s mix aetheris run ../aetheris-agents/agents/bank_statement_agent.exs
```

For a specific task, set the agent's `user_prompt` to a request such as
`List my available bank statements.`, `Find my bank statement.`, or
`Convert the bank statement to hledger format.` Supply identifying information
if the discovered schema requires it. The agent asks for missing information in
its final response; provide it on a new run.

Validation from the `aetheris-agents/` root:

```bash
timeout -k 5s 120s python3 -m pytest tests/test_bank_statement_mcp.py -v
# Opt-in real server + LLM acceptance check (requires the sibling harness):
BANK_STATEMENT_MCP_TEST_LIVE=true timeout -k 5s 600s \
  python3 -m pytest tests/test_bank_statement_mcp.py -v -k live_agent_flow
```

The live check requires a seeded test server where all example requests have
enough information to succeed. It checks recorded calls and responses for
`bank_statement_list`, `find_bank_statement`, and `bank_statement_to_hledger`.
Inspect the local trajectory and final response to confirm the returned statement
and hledger content match the seeded account. Elixir config tests are marked
`integration` because they require an external runtime.

This checkout does not carry the Bank Statement server or sibling harness.
Local config evaluation is testable separately; live discovery, tool invocation,
and final response validation require those services and provider credentials.
The Rig HTTP registry currently does not resolve environment URLs or forward
headers; this agent uses `RunConfig` directly rather than changing core MCP/Rig.

### Tool set

```elixir
tools: ["run_command", "spawn_agent", "wait_for_all"]
```

Orchestrators almost never need `read_file` or `write_file` directly.

### System prompt structure

```
You are a {description} orchestrator.

Workflow — follow these steps in order:

1. Call run_command with:
     command: "python3"
     args: ["scripts/{compute_script}.py", "data/{input_file}"]
   Parse the JSON output. Extract the list of {items}.

2. For each {item}, call spawn_agent with:
   - tools: ["run_command"]
   - max_steps: 10
   - task_prompt: (template below — replace {id} with the item identifier)

   Task prompt template:
   ---
   Process {item_type} {id}.

   Call run_command with:
     command: "python3"
     args: ["scripts/{generation_script}.py", "{id}"]

   Report the output from the command.
   ---

3. Collect all run_ids. Call wait_for_all with timeout_ms: 300000.

4. Report: total processed, any failures.

Rules:
- All paths are relative to the sandbox root.
- overlay_base_dir is nil. Output files must persist on disk.
```

### Be explicit about run_command format

Always show the exact JSON fields, not a shell command string:

```
# GOOD — unambiguous
Call run_command with:
  command: "python3"
  args: ["scripts/compute.py", "data/input.csv"]

# BAD — the LLM will guess and may include "python3" in args too
Run: python3 scripts/compute.py data/input.csv
```

The LLM commonly duplicates the command name in both `command` and `args`,
producing `python3 python3 script.py`. Being explicit prevents this.

---

## Sub-agent patterns

### `spawn_agent` maps `task_prompt` to `system_prompt`

The sub-agent gets `task_prompt` as its `system_prompt` and `"Begin."` as its
`user_prompt`. The Anthropic API requires at least one user message — without
`"Begin."` the sub-agent fails with HTTP 400.

This is handled automatically by Aetheris (the `user_prompt: "Begin."` is set
in `spawn_agent.ex`). You do not need to add it manually.

### Sub-agent tool set

For agents that only call scripts:
```elixir
tools: ["run_command"]
```

For agents that need to read context files:
```elixir
tools: ["run_command", "read_file"]
```

For agents that synthesise and write reports:
```elixir
tools: ["run_command", "read_file", "write_file"]
```

Avoid giving sub-agents `spawn_agent` unless they genuinely need to delegate
further. `max_spawn_depth: 2` on the orchestrator prevents accidents.

### Sub-agent `max_steps`

| Task | max_steps |
|------|-----------|
| Single script call + report | 5–10 |
| Script + conditional retry | 10–15 |
| Multi-step with read/write | 15–30 |

Orchestrators: 15–20. Sub-agents calling one script: 10.

### Sub-agent `task_prompt` should be self-contained

The sub-agent has no memory of the orchestrator's context. The task_prompt
must include everything it needs: what to do, exact tool call format, where
to write output, what to report back.

---

## Script design

### One script per responsibility

| Script | Does |
|--------|------|
| `{name}_compute.py` | CSV/data → structured JSON |
| `generate_{name}.py` | JSON + template → output files + merge |
| `merge_{name}.py` | File collection → single merged output |

Splitting compute from generation means you can test computation without
needing output tools (wkhtmltopdf, etc.) installed.

### `--output-dir` flag on generation scripts

Always add `--output-dir` with a sensible default:

```python
parser.add_argument("--output-dir", default="output")
```

This makes tests clean (write to `tmp_path`) and lets the sprint script
point to a test-specific location.

### Scripts must be runnable standalone

```bash
cd ~/sandbox/elixirws/aetheris-agents/{use_case}
python3 scripts/{compute}.py data/sample.csv
python3 scripts/generate_{name}.py BTL_999
```

If you can't run the script standalone, the agent can't either.

### Python package naming

Never create `__init__.py` in a directory whose name collides with a Python
stdlib package. The common case in this repo is `email/` — creating
`email/__init__.py` shadows the stdlib `email` package and breaks pytest
(which uses `email.message` internally).

**Fix:** omit `__init__.py` at the top level and use `conftest.py` to insert
the scripts directory into `sys.path` directly:

```python
# email/tests/conftest.py
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
```

Tests then import by module name (`from email_send import ...`) rather than
via the package namespace (`from email.scripts.email_send import ...`), which
would resolve to the stdlib package instead.

Check for collisions before naming a new use-case directory:
`python3 -c "import {name}"` — if it succeeds, pick a different name or
omit the top-level `__init__.py` and use the conftest pattern.

### Subprocess for calling other scripts

```python
result = subprocess.run(
    ["python3", "scripts/other_script.py", arg],
    capture_output=True, text=True
)
if result.returncode != 0:
    print(result.stderr, file=sys.stderr)
    sys.exit(result.returncode)
```

Never use `python3 -c "..."` with inline scripts. These produce massive
argument strings that hit the 30-second MCP call timeout.

---

## Testing strategy

### Three layers

| Layer | Tool | What it tests |
|-------|------|---------------|
| Unit | pytest | Business rules, computation, edge cases |
| Integration | pytest + `@pytest.mark.integration` | Full script with real files |
| Sprint | `./scripts/sprint.sh {name}` | End-to-end with real LLM |

### conftest.py template

```python
import shutil
import pytest

def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "integration: marks tests requiring external tools"
    )

def pytest_collection_modifyitems(config, items):
    missing = [t for t in ["wkhtmltopdf", "gs"] if shutil.which(t) is None]
    if missing:
        skip = pytest.mark.skip(reason=f"missing: {', '.join(missing)}")
        for item in items:
            if item.get_closest_marker("integration"):
                item.add_marker(skip)
```

Adjust the tool list to match your use case's dependencies.

### Use `tmp_path` for integration tests

```python
def test_generates_output(tmp_path):
    result = subprocess.run(
        [sys.executable, SCRIPT, "BTL_999", "--output-dir", str(tmp_path)],
        cwd=USE_CASE_ROOT, capture_output=True, text=True
    )
    assert result.returncode == 0
    assert (tmp_path / "BTL_999" / "2026-04.html").exists()
```

Always pass `cwd=USE_CASE_ROOT` so scripts resolve `data/` and `scripts/`
relative to the use-case root, not the test file's location.

---

## Sprint case

Every use case gets a sprint case in `aetheris/scripts/sprint.sh`:

```bash
if [[ "$TARGET" == "{name}" ]]; then
  section "uc-{name} — {Description}"

  # 1. Check prerequisites
  for tool in python3 {tool1} {tool2}; do
    command -v "$tool" &>/dev/null || { fail "$tool not found"; exit 1; }
    ok "$tool found"
  done

  # 2. Ensure input data
  [[ -f "$DATA_FILE" ]] || cp "$SAMPLE_FILE" "$DATA_FILE"

  # 3. Run orchestrator
  run_agent "uc-{name}" "$OUT_DIR/{name}/run.json" \
    "../aetheris-agents/{name}/agents/{name}_orchestrator.exs"

  # 4. Verify output
  [[ -d "$OUTPUT_DIR" ]] && ok "output exists" || fail "output missing"

  # 5. Summary stats
fi
```

---

## Common failure modes

### HTTP 400: messages: at least one message is required

Sub-agent has `message_count: 0`. `spawn_agent` maps `task_prompt` to
`system_prompt`; `user_prompt` defaults to `"Begin."` (handled by Aetheris
since T0). If you see this on an older Aetheris version, check that
`spawn_agent.ex` sets `user_prompt: "Begin."`.

### run_command has no stdin parameter — scripts must accept --input FILE

`run_command` cannot pipe data to a script's stdin. If your orchestrator needs
to pass a JSON payload (e.g. a doc spec) to a generation script, the script
must also accept `--input FILE` so the orchestrator can write the payload with
`write_file` first, then call the script with `--input output/payload.json`.

Attempting to use `sh -c "cat file | python3 script.py"` is fragile — the LLM
does not follow this pattern reliably and the script will hang waiting for stdin.

**Rule:** any script that reads JSON from stdin must also support `--input FILE`
before it can be called from an orchestrator via `run_command`.

`Source: m-docbuilder-m1 t7`

### GenServer timeout on run_command

The sub-agent is passing a massive inline script via `python3 -c "..."`.
The argument string exceeds the MCP call buffer or execution time.
Fix: move the logic to a script file; call it as
`python3 scripts/my_script.py arg1 arg2`.

### run_command duplicates command in args

The LLM called `{"command": "python3", "args": ["python3", "script.py"]}`.
This runs `python3 python3 script.py`. Fix: be explicit in the prompt:
```
command: "python3"
args: ["scripts/my_script.py", "arg1"]
```

### Sub-agent tool calls resolve to wrong directory

`sandbox_path` is nil or set to `File.cwd!()` (the aetheris repo).
Fix: use `__ENV__.file` in the orchestrator and confirm `spawn_agent`
inherits `sandbox_path` (requires Aetheris ≥ uc-payslip T0).

### Output files missing after run

`overlay_base_dir` is set. Writes went to a per-run `upper/` layer.
Fix: set `overlay_base_dir: nil` for use cases where output must persist.

### Env vars and worker lifetime

The exec server spawns workers at invocation time and they inherit the
environment at that point. If you export an env var after starting the server
(or change it mid-session), running workers won't see the new value.

**Fix:** export all required env vars before running `mix aetheris run`.
If vars changed mid-session, kill stale workers first:

```bash
pkill -f aetheris_worker
```

Then re-export and re-run.

### Shared Drive required for service account uploads

Service accounts have no personal storage quota and cannot create files in a
regular My Drive folder. Attempting to upload produces:

```
HttpError 403: storageQuotaExceeded
```

**Fix:** the output folder must be a Shared Drive (formerly Team Drive). Create
a Shared Drive in Google Drive, add the service account email as a Contributor,
and use that folder's ID as `DRIVE_ROOT_FOLDER_ID` (the payslip pipeline reads and
writes every month's folder under that one root).

All `files().list()` and `files().create()` calls must include
`supportsAllDrives=True` (and `includeItemsFromAllDrives=True` for list calls)
or the Shared Drive folder will appear empty.

### Orchestrator goes off-script after sub-agent failures

The LLM tries to recover by exploring files or re-running scripts.
Add to the Rules section of the system prompt:
```
- If wait_for_all returns failures, report which items failed and stop.
  Do not attempt to investigate or retry manually.
```

---

## Pre-flight checklist for a new agent

Before running the first sprint:

- [ ] `scripts/{compute}.py` runs standalone with sample data
- [ ] `scripts/generate_{name}.py` runs standalone for one item
- [ ] `python3 -m pytest {use_case}/tests/` passes
- [ ] `agents/{name}_orchestrator.exs` evaluates without error:
      `mix run --eval 'Code.eval_file("agents/{name}_orchestrator.exs")'`
- [ ] `sandbox_path` uses `__ENV__.file` pattern
- [ ] `overlay_base_dir: nil` set intentionally
- [ ] Sub-agent tools are minimal (`["run_command"]` if possible)
- [ ] System prompt shows exact `run_command` format with `command:` and `args:`
- [ ] Rules section includes "report failures and stop"
- [ ] `{use_case}/.gitignore` excludes real data and `output/`
- [ ] `mix aetheris doctor` shows ✅ or ⚠ (not ❌) for all required tools
- [ ] Sprint case added to `aetheris/scripts/sprint.sh`

---

## Applying to upcoming agents

### uc-drive (Google Drive reader)

Expected shape:
- `scripts/drive_download.py` — downloads files from Drive to `data/`
  (thin wrapper around the Drive API or gcloud)
- `scripts/drive_upload.py` — uploads files from `output/` to Drive
- Orchestrator: download → spawn processing sub-agents → upload results
- Design principle applies: Drive API calls are in scripts, not in the LLM

Key question to answer before starting: does the Drive agent need to
authenticate per-run, or is a service account credential file sufficient?
That determines whether credentials go in `data/` (gitignored) or
environment variables.

### uc-email (Email payslip agent)

Expected shape:
- `scripts/send_email.py` — sends one email with attachment
  (SMTP or API-based; credentials from environment)
- Orchestrator: for each employee, spawn sub-agent that calls send script
- Output of uc-payslip (`output/{id}/merged.pdf`) is the input here
- These two use cases compose: payslip output → email input

Key question: does each sub-agent send one email (simple, parallel) or does
the orchestrator send them all sequentially (simpler but slower)?
Parallel is better; one sub-agent per recipient, `wait_for_all`.
