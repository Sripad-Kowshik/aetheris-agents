#!/usr/bin/env python3
"""
Deterministic doc-drift checker for Rig documentation.

Checks that docs/rig/specs.md, docs/rig/runbook.md, and related docs
stay in sync with Rust/TypeScript/Elixir source code.

Exit codes:
  0 — no FAIL findings
  1 — one or more FAIL findings

Checks:
  event_types      — event.ex @type vs specs.md §6
  tauri_commands   — lib.rs generate_handler! vs .rs files vs specs.md §4
  db_schema        — store.ex CREATE TABLE vs specs.md §2
  env_vars         — Rust env::var() calls vs specs.md §1 and runbook.md
  routes           — registry.ts paths vs App.tsx Route paths
  payload_fields   — live DB payload sampling vs specs.md §6 (skipped if DB absent)
  milestone_status    — docs/rig/milestones/*/README.md has Status: line
  project_knowledge   — project-knowledge-manifest.md commit hashes vs git HEAD (WARN if stale),
                        plus a WARN when a tracked path has uncommitted edits (BL-041b).
                        Rows on the `on-demand` surface are not compared: HEAD is the
                        surface they are served from, so nothing about them can be stale
                        (hybrid-context design, 2026-09-08); they are counted in the PASS.
  command_fields      — specs.md §4 ```rust struct fields vs commands/*.rs (BL-036)
  use_case_registry   — docs/use-cases.md vs every machine-separable enumeration of use
                        cases: the two doc tables, assemble_matrix.SECTIONS and the section
                        agents (both under the agent-bearing predicate), the overrides keys,
                        SWEPT / NO_MANIFEST_YET, the tools.json set and tools.rs's vec!
                        (ds t1a). No strict exemption.
  backlog_resolution  — every strict-form `BL-nnn` in the scoped corpus (the two backlog
                        files, every docs/evidence/*.md, and every *.py/*.sh in both
                        repos) names a row in the
                        UNION of the open file and the closed archive. FAIL, never WARN;
                        allowlist keyed by (id, file), each entry with its reason (ds t1b).
  index_integrity     — for every manifest row whose path is an `index.md` (an INDEXED
                        TREE, hybrid-context design §1.1): each index entry resolves at
                        HEAD in that row's repo; every markdown file at HEAD in the tree
                        has an entry; every such file carries the frontmatter the index
                        needs (the §1.2 gap committed anyway); an entry whose title or
                        description no longer matches the file's frontmatter is a WARN.
                        The tree list comes from the manifest, never from a second list
                        here. Uncommitted edits under the tree get a strict-exempt WARN on
                        check 8's terms — the reading is about HEAD.
  kernel_budget       — the byte-sum at HEAD of `_manifest.export_rows()`, each row read in
                        its owning repo, against the **Kernel ceiling** in the manifest
                        header (BL-201). Above it: WARN, not strict-exempt. The PASS line
                        reports the distance to the **Kernel design target**, which is
                        never enforced. Header figures unparseable: FAIL.

--strict promotes WARN to FAIL, with one exemption: project_knowledge
manifest-STALENESS WARNs stay WARN and do not affect the exit code (mid-cycle
staleness is expected truth between export boundaries). The uncommitted-edit WARN
is exempt on the same terms — it reports that this run cannot answer the staleness
question yet, not that something regressed. Structural manifest problems (missing
file, unknown repo, git failure) are NOT exempt and still FAIL.
So under --strict the invariant is "zero UNEXPLAINED WARNs", not "zero WARNs".
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.resolve()))
from _frontmatter import FrontmatterError, read_document  # noqa: E402
import _manifest  # noqa: E402

# --------------------------------------------------------------------------- #
# Repo layout                                                                  #
# --------------------------------------------------------------------------- #

SCRIPT_DIR    = Path(__file__).parent.resolve()
REPO_ROOT     = SCRIPT_DIR.parent
HARNESS_ROOT  = REPO_ROOT.parent / "aetheris"
RIG_ROOT      = REPO_ROOT / "rig"

SPECS_MD      = REPO_ROOT / "docs" / "rig" / "specs.md"
RUNBOOK_MD    = REPO_ROOT / "docs" / "rig" / "runbook.md"
EVENT_EX      = HARNESS_ROOT / "lib" / "aetheris" / "trajectory" / "event.ex"
STORE_EX      = HARNESS_ROOT / "lib" / "aetheris" / "store.ex"
LIB_RS        = RIG_ROOT / "src-tauri" / "src" / "lib.rs"
COMMANDS_DIR  = RIG_ROOT / "src-tauri" / "src" / "commands"
RIG_SRC_TAURI = RIG_ROOT / "src-tauri" / "src"
REGISTRY_TS   = RIG_ROOT / "src" / "modules" / "registry.ts"
APP_TSX       = RIG_ROOT / "src" / "App.tsx"
MILESTONES_DIR = REPO_ROOT / "docs" / "rig" / "milestones"
MANIFEST_MD    = REPO_ROOT / "docs" / "project-knowledge-manifest.md"

# --------------------------------------------------------------------------- #
# Findings                                                                     #
# --------------------------------------------------------------------------- #

FINDINGS: list[tuple[str, str, str]] = []
_strict = False

_COLORS = {
    "FAIL": "\033[31m",
    "WARN": "\033[33m",
    "INFO": "\033[36m",
    "PASS": "\033[32m",
}
_RESET = "\033[0m"


def record(level: str, check: str, message: str, strict_exempt: bool = False) -> None:
    # --strict promotes WARN to FAIL, EXCEPT for strict_exempt WARNs (currently
    # only project_knowledge manifest-staleness). Mid-cycle manifest staleness is
    # expected truth between export boundaries, not a regression — see BL-009.
    if level == "WARN" and _strict and not strict_exempt:
        level = "FAIL"
    FINDINGS.append((level, check, message))
    color = _COLORS.get(level, "")
    print(f"{color}[{level}]{_RESET} {check}: {message}")


def _fail(check, msg): record("FAIL", check, msg)
def _warn(check, msg, strict_exempt=False): record("WARN", check, msg, strict_exempt)
def _info(check, msg): record("INFO", check, msg)
def _ok(check, msg):   record("PASS", check, msg)


def _require_file(path: Path, check: str) -> str | None:
    if not path.exists():
        _fail(check, f"file not found: {path}")
        return None
    return path.read_text(encoding="utf-8")


def _require_section(text: str, pattern: str, check: str, anchor: str) -> re.Match | None:
    m = re.search(pattern, text, re.DOTALL)
    if not m:
        _fail(check, f"anchor not found: {anchor!r}")
        return None
    return m

# --------------------------------------------------------------------------- #
# Check 1: event_types                                                         #
# --------------------------------------------------------------------------- #

def _parse_event_types_from_event_ex(text: str, check: str) -> set[str] | None:
    m = _require_section(
        text,
        r"@type event_type ::\s*(.*?)(?=\n\s*@|\Z)",
        check,
        "@type event_type ::",
    )
    if not m:
        return None
    types = re.findall(r":(\w+)", m.group(1))
    if not types:
        _fail(check, "zero event types parsed from @type event_type block")
        return None
    return set(types)


def _parse_event_types_from_specs(text: str, check: str) -> set[str] | None:
    m = _require_section(
        text,
        r"## 6\. Event Type Reference(.*?)(?=\n## |\Z)",
        check,
        "## 6. Event Type Reference",
    )
    if not m:
        return None
    # First column of each pipe-table row is the event type
    types = re.findall(r"^\| `(\w+)` \|", m.group(1), re.MULTILINE)
    if not types:
        _fail(check, "zero event types parsed from specs.md §6 table")
        return None
    return set(types)


def check_event_types() -> None:
    check = "event_types"
    src = _require_file(EVENT_EX, check)
    specs = _require_file(SPECS_MD, check)
    if src is None or specs is None:
        return

    code_types = _parse_event_types_from_event_ex(src, check)
    doc_types  = _parse_event_types_from_specs(specs, check)
    if code_types is None or doc_types is None:
        return

    for t in sorted(code_types - doc_types):
        _fail(check, f"{t!r} in event.ex but missing from specs.md §6")
    for t in sorted(doc_types - code_types):
        _fail(check, f"{t!r} in specs.md §6 but not in event.ex (ghost)")

    if not any(l == "FAIL" and c == check for l, c, _ in FINDINGS):
        _ok(check, f"{len(code_types)} event types match between event.ex and specs.md §6")

# --------------------------------------------------------------------------- #
# Check 2: tauri_commands                                                      #
# --------------------------------------------------------------------------- #

def _parse_commands_from_lib_rs(text: str, check: str) -> set[str] | None:
    m = _require_section(
        text,
        r"generate_handler!\[(.*?)\]",
        check,
        "generate_handler![...]",
    )
    if not m:
        return None
    # Qualified paths: commands::module::fn_name
    names = set(re.findall(r"commands::\w+::(\w+)", m.group(1)))
    if not names:
        _fail(check, "zero commands parsed from generate_handler! block")
        return None
    return names


def _parse_commands_from_command_files(commands_dir: Path) -> set[str]:
    result: set[str] = set()
    for rs_file in sorted(commands_dir.glob("*.rs")):
        text = rs_file.read_text(encoding="utf-8")
        for m in re.finditer(
            r"#\[tauri::command\]\s*\n\s*pub(?:\s+async)?\s+fn\s+(\w+)",
            text,
        ):
            result.add(m.group(1))
    return result


def _parse_commands_from_specs(text: str, check: str) -> set[str] | None:
    m = _require_section(
        text,
        r"## 4\. Tauri Command Shapes(.*?)(?=\n## |\Z)",
        check,
        "## 4. Tauri Command Shapes",
    )
    if not m:
        return None
    section = m.group(1)
    names: set[str] = set()
    # Bold-backtick blocks: **`command_name`**
    names.update(re.findall(r"\*\*`(\w+)`\*\*", section))
    # Table first column: | `command_name` |
    names.update(re.findall(r"^\| `(\w+)` \|", section, re.MULTILINE))
    # Keep only snake_case names (command names always have underscores)
    names = {n for n in names if "_" in n}
    if not names:
        _fail(check, "zero commands parsed from specs.md §4")
        return None
    return names


def check_tauri_commands() -> None:
    check = "tauri_commands"
    lib_text = _require_file(LIB_RS, check)
    specs_text = _require_file(SPECS_MD, check)
    if lib_text is None or specs_text is None:
        return

    lib_cmds  = _parse_commands_from_lib_rs(lib_text, check)
    file_cmds = _parse_commands_from_command_files(COMMANDS_DIR)
    doc_cmds  = _parse_commands_from_specs(specs_text, check)
    if lib_cmds is None or doc_cmds is None:
        return

    for n in sorted(file_cmds - lib_cmds):
        _warn(check, f"{n!r} has #[tauri::command] but is not in generate_handler!")
    for n in sorted(lib_cmds - doc_cmds):
        _warn(check, f"{n!r} is registered but not documented in specs.md §4")
    for n in sorted(doc_cmds - lib_cmds):
        _fail(check, f"{n!r} documented in specs.md §4 but not in generate_handler! (ghost)")

    if not any(l == "FAIL" and c == check for l, c, _ in FINDINGS):
        _ok(check, f"{len(lib_cmds)} commands checked: lib.rs / .rs files / specs.md §4")

# --------------------------------------------------------------------------- #
# Check 3: db_schema                                                           #
# --------------------------------------------------------------------------- #

def _extract_table_body(text: str, open_paren_pos: int) -> str:
    """Return the text between the opening '(' and its matching closing ')'.

    Uses paren-depth tracking so nested parens (REFERENCES, UNIQUE) don't
    truncate the body prematurely.
    """
    depth = 1
    i = open_paren_pos
    while i < len(text) and depth > 0:
        c = text[i]
        if c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
        i += 1
    return text[open_paren_pos : i - 1]


def _extract_tables_from_sql(text: str) -> dict[str, set[str]]:
    tables: dict[str, set[str]] = {}
    for m in re.finditer(r"CREATE TABLE (?:IF NOT EXISTS )?(\w+)\s*\(", text):
        name = m.group(1)
        body = _extract_table_body(text, m.end())
        cols = set(re.findall(r"^\s+([a-z_][a-z0-9_]*)\s+\S", body, re.MULTILINE))
        tables[name] = cols
    return tables


def _parse_tables_from_store_ex(text: str, check: str) -> dict[str, set[str]] | None:
    tables = _extract_tables_from_sql(text)
    if not tables:
        _fail(check, "zero CREATE TABLE blocks parsed from store.ex")
        return None
    for m in re.finditer(r"ALTER TABLE (\w+) ADD COLUMN (\w+)", text):
        t, col = m.group(1), m.group(2)
        if t in tables:
            tables[t].add(col)
    return tables


def _parse_tables_from_specs(text: str, check: str) -> dict[str, set[str]] | None:
    m = _require_section(
        text,
        r"## 2\. Harness DB Schema(.*?)(?=\n## |\Z)",
        check,
        "## 2. Harness DB Schema",
    )
    if not m:
        return None
    tables = _extract_tables_from_sql(m.group(1))
    if not tables:
        _fail(check, "zero CREATE TABLE blocks parsed from specs.md §2")
        return None
    return tables


def check_db_schema() -> None:
    check = "db_schema"
    store_text = _require_file(STORE_EX, check)
    specs_text = _require_file(SPECS_MD, check)
    if store_text is None or specs_text is None:
        return

    code_tables = _parse_tables_from_store_ex(store_text, check)
    doc_tables  = _parse_tables_from_specs(specs_text, check)
    if code_tables is None or doc_tables is None:
        return

    for table_name, doc_cols in doc_tables.items():
        if table_name not in code_tables:
            _fail(check, f"table {table_name!r} in specs.md §2 but not in store.ex")
            continue
        code_cols = code_tables[table_name]
        for col in sorted(doc_cols - code_cols):
            _fail(check, f"{table_name}.{col} in specs.md §2 but not in store.ex")
        for col in sorted(code_cols - doc_cols):
            _info(check, f"{table_name}.{col} in store.ex but not in specs.md §2")

    if not any(l == "FAIL" and c == check for l, c, _ in FINDINGS):
        _ok(check, f"{len(doc_tables)} documented tables match store.ex schema")

# --------------------------------------------------------------------------- #
# Check 4: env_vars                                                            #
# --------------------------------------------------------------------------- #

def _parse_env_vars_from_rust_text(text: str) -> set[str]:
    # SCREAMING_SNAKE_CASE with at least one underscore (project config vars)
    return set(re.findall(r'env::var\("([A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+)"\)', text))


def _parse_env_vars_from_rust(src_dir: Path, check: str) -> set[str]:
    result: set[str] = set()
    for rs_file in src_dir.rglob("*.rs"):
        result.update(_parse_env_vars_from_rust_text(rs_file.read_text(encoding="utf-8")))
    return result


def _parse_env_vars_from_doc(text: str, section_pattern: str, check: str, anchor: str) -> set[str] | None:
    m = _require_section(text, section_pattern, check, anchor)
    if not m:
        return None
    rows = re.findall(r"^\| `([A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+)` \|", m.group(0), re.MULTILINE)
    if not rows:
        _fail(check, f"zero env vars parsed from {anchor!r}")
        return None
    return set(rows)


def check_env_vars() -> None:
    check = "env_vars"
    specs_text   = _require_file(SPECS_MD, check)
    runbook_text = _require_file(RUNBOOK_MD, check)
    if specs_text is None or runbook_text is None:
        return

    code_vars    = _parse_env_vars_from_rust(RIG_SRC_TAURI, check)
    specs_vars   = _parse_env_vars_from_doc(
        specs_text,
        r"## 1\. Environment Variables(.*?)(?=\n## |\Z)",
        check,
        "## 1. Environment Variables",
    )
    runbook_vars = _parse_env_vars_from_doc(
        runbook_text,
        r"## Environment variables(.*?)(?=\n## |\Z)",
        check,
        "## Environment variables",
    )
    if specs_vars is None or runbook_vars is None:
        return

    for v in sorted(code_vars - specs_vars):
        _warn(check, f"{v!r} read by Rig Rust but not listed in specs.md §1")
    for v in sorted(specs_vars - runbook_vars):
        _warn(check, f"{v!r} in specs.md §1 but absent from runbook.md env table")
    # vars in specs but not in code — some are agent-side (INFO, not WARN)
    for v in sorted(specs_vars - code_vars):
        _info(check, f"{v!r} in specs.md §1 but not read via env::var() in Rig (may be agent-side)")

    if not any(l in ("FAIL", "WARN") and c == check for l, c, _ in FINDINGS):
        _ok(check, f"env vars consistent: {len(specs_vars)} in specs, {len(code_vars)} read in Rust")

# --------------------------------------------------------------------------- #
# Check 5: routes                                                              #
# --------------------------------------------------------------------------- #

# Routes present in App.tsx that are not required in registry.ts
_ROUTE_EXCEPTIONS = {"/", "/settings"}


def _parse_routes_from_registry(text: str, check: str) -> set[str] | None:
    paths = re.findall(r"path:\s*'([^']+)'", text)
    if not paths:
        _fail(check, "zero paths parsed from registry.ts")
        return None
    return set(paths)


def _parse_routes_from_app_tsx(text: str, check: str) -> set[str] | None:
    paths = re.findall(r'path="([^"]+)"', text)
    if not paths:
        _fail(check, "zero paths parsed from App.tsx")
        return None
    return set(paths) - _ROUTE_EXCEPTIONS


def check_routes() -> None:
    check = "routes"
    reg_text = _require_file(REGISTRY_TS, check)
    app_text = _require_file(APP_TSX, check)
    if reg_text is None or app_text is None:
        return

    registry_paths = _parse_routes_from_registry(reg_text, check)
    app_paths      = _parse_routes_from_app_tsx(app_text, check)
    if registry_paths is None or app_paths is None:
        return

    for p in sorted(registry_paths - app_paths):
        _fail(check, f"{p!r} in registry.ts but no matching Route in App.tsx")
    for p in sorted(app_paths - registry_paths):
        _warn(check, f"{p!r} in App.tsx but no matching entry in registry.ts")

    if not any(l == "FAIL" and c == check for l, c, _ in FINDINGS):
        _ok(check, f"{len(registry_paths)} registry paths all have matching App.tsx routes")

# --------------------------------------------------------------------------- #
# Check 6: payload_fields                                                      #
# --------------------------------------------------------------------------- #

def _parse_payload_fields_from_specs(
    text: str, check: str
) -> dict[str, dict[str, bool]] | None:
    """Return {event_type: {field_name: is_optional}}.

    A field suffixed with ? in the cell (e.g. `stop_reason?`) is optional:
    the check will not FAIL when it is absent from sampled DB events.
    """
    m = _require_section(
        text,
        r"## 6\. Event Type Reference(.*?)(?=\n## |\Z)",
        check,
        "## 6. Event Type Reference",
    )
    if not m:
        return None

    result: dict[str, dict[str, bool]] = {}
    for row in re.finditer(r"^\| `(\w+)` \| (.*?) \|$", m.group(1), re.MULTILINE):
        event_type  = row.group(1)
        fields_cell = row.group(2)
        # Strip enum values listed after " — " (e.g. `reason` — `done` | `failed`)
        fields_part = fields_cell.split(" — ")[0]
        # `field?` → optional; `field` → required
        fields = {
            name.rstrip("?"): name.endswith("?")
            for name in re.findall(r"`(\w+\??)`", fields_part)
        }
        if fields:
            result[event_type] = fields

    if not result:
        _fail(check, "zero payload field rows parsed from specs.md §6 table")
        return None
    return result


def _evaluate_payload_fields(
    event_type: str, field_map: dict[str, bool], seen_keys: set[str]
) -> None:
    check = "payload_fields"
    for field, is_optional in field_map.items():
        if field not in seen_keys:
            if is_optional:
                _info(check, f"{event_type}.{field} optional in specs.md §6 — not yet observed in DB")
            else:
                _fail(check, f"{event_type}.{field} in specs.md §6 but not seen in DB")
    for key in sorted(seen_keys - set(field_map)):
        _info(check, f"{event_type}.{key} in DB events but not listed in specs.md §6")


def check_payload_fields() -> None:
    check = "payload_fields"

    db_path_str = os.environ.get("AETHERIS_DB_PATH")
    if not db_path_str:
        _warn(check, "AETHERIS_DB_PATH not set — skipping live payload sampling")
        return

    db_path = Path(db_path_str).expanduser()
    if not db_path.exists():
        _warn(check, f"AETHERIS_DB_PATH={db_path} not found — skipping")
        return

    specs_text = _require_file(SPECS_MD, check)
    if specs_text is None:
        return

    doc_fields = _parse_payload_fields_from_specs(specs_text, check)
    if doc_fields is None:
        return

    try:
        import sqlite3
        conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        conn.row_factory = sqlite3.Row
    except Exception as e:
        _warn(check, f"could not open {db_path}: {e}")
        return

    try:
        for event_type, field_map in doc_fields.items():
            count = conn.execute(
                "SELECT COUNT(*) FROM events WHERE type = ?", (event_type,)
            ).fetchone()[0]
            if count == 0:
                _info(check, f"no {event_type!r} events in DB — cannot verify payload fields")
                continue

            # Use json_each to get all distinct payload keys across every event
            seen_keys: set[str] = {
                row[0]
                for row in conn.execute(
                    "SELECT DISTINCT je.key"
                    " FROM events e, json_each(e.payload_json) je"
                    " WHERE e.type = ?",
                    (event_type,),
                ).fetchall()
            }

            _evaluate_payload_fields(event_type, field_map, seen_keys)
    finally:
        conn.close()

    if not any(l == "FAIL" and c == check for l, c, _ in FINDINGS):
        _ok(check, "sampled DB payload fields consistent with specs.md §6")

# --------------------------------------------------------------------------- #
# Check 7: milestone_status                                                    #
# --------------------------------------------------------------------------- #

def check_milestone_status() -> None:
    check = "milestone_status"

    if not MILESTONES_DIR.exists():
        _warn(check, f"milestones directory not found: {MILESTONES_DIR}")
        return

    milestone_dirs = sorted(d for d in MILESTONES_DIR.iterdir() if d.is_dir())
    if not milestone_dirs:
        _warn(check, "no milestone subdirectories found")
        return

    missing: list[str] = []
    for d in milestone_dirs:
        readme = d / "README.md"
        if not readme.exists():
            _warn(check, f"{d.name}/README.md not found")
            missing.append(d.name)
        elif "Status:" not in readme.read_text(encoding="utf-8"):
            _warn(check, f"{d.name}/README.md has no 'Status:' line")
            missing.append(d.name)

    if not missing:
        _ok(check, f"{len(milestone_dirs)} milestone READMEs all have Status: lines")

# --------------------------------------------------------------------------- #
# Check 8: project_knowledge                                                   #
# --------------------------------------------------------------------------- #

# Regex for manifest data rows:
#   | `export-name` | `repo/path` | repo-name | `abc1234` | YYYY-MM-DD | surface |
# Rows with _(this export)_ as commit are skipped (manifest self-reference). The trailing
# `surface` cell (2026-09-08) is captured when present and None on the five-cell shape
# the table had before it, which is read as `export` — the surface every row had then.
_MANIFEST_ROW_RE = re.compile(
    r"^\| `[^`]+` \| `([^`]+)` \| (\S+) \| `([0-9a-f]{5,})`"
    r"(?: \| \S+ \| (export|on-demand|both) \|)?",
    re.MULTILINE,
)

_REPO_DIR_MAP = {
    "aetheris-agents": REPO_ROOT,
    "aetheris":        HARNESS_ROOT,
}


def _git_head_hash(repo_dir: Path, path: str) -> str | None:
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%h", "--", path],
            cwd=repo_dir,
            capture_output=True,
            text=True,
            timeout=10,
        )
        return result.stdout.strip() or None
    except Exception:
        return None


def _git_is_dirty(repo_dir: Path, path: str) -> bool | None:
    """True if `path` has uncommitted working-tree changes in `repo_dir`.

    Returns None when git could not answer (structural problem, not exempt).
    Counterpart to `_git_head_hash`, which reads committed history only — see
    the BL-041(b) guard in check_project_knowledge.
    """
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain", "--", path],
            cwd=repo_dir,
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode != 0:
            return None
        return bool(result.stdout.strip())
    except Exception:
        return None


def check_project_knowledge() -> None:
    check = "project_knowledge"

    if not MANIFEST_MD.exists():
        _warn(check, f"docs/project-knowledge-manifest.md not found — skipping staleness check")
        return

    text = MANIFEST_MD.read_text(encoding="utf-8")
    rows = _MANIFEST_ROW_RE.findall(text)  # [(repo_path, repo_name, commit, surface), ...]

    if not rows:
        _fail(check, "zero data rows parsed from project-knowledge-manifest.md")
        return

    stale: list[str] = []
    uncommitted: list[str] = []
    structural: list[str] = []
    on_demand: list[str] = []
    for repo_path, repo_name, manifest_commit, surface in rows:
        if surface == "on-demand":
            # Served from HEAD, never from the store: the pin is a map entry, not a claim
            # about an upload, and comparing it would report staleness where none can
            # exist. Counted, so the PASS line says how many rows were not compared.
            on_demand.append(repo_path)
            continue
        repo_dir = _REPO_DIR_MAP.get(repo_name)
        if repo_dir is None:
            _warn(check, f"unknown repo name {repo_name!r} in manifest — cannot verify {repo_path}")
            structural.append(repo_path)
            continue

        # BL-041(b): this check compares COMMITTED history, so an uncommitted edit
        # to a tracked path is invisible to it — the run reports the manifest clean
        # whether or not the edit was made. Say so, per path, in the row's OWN repo
        # (the harness rows live in the sibling checkout, not REPO_ROOT).
        dirty = _git_is_dirty(repo_dir, repo_path)
        if dirty is None:
            # Structural (same class as a git log failure) — NOT strict-exempt.
            _warn(check, f"{repo_path}: git status failed — cannot check for uncommitted edits")
            structural.append(repo_path)
        elif dirty:
            _warn(
                check,
                f"{repo_path} has uncommitted working-tree changes — this check compares "
                f"committed history, so its staleness reading for this path is vacuous; "
                f"re-run --strict after committing",
                strict_exempt=True,
            )
            uncommitted.append(repo_path)

        current = _git_head_hash(repo_dir, repo_path)
        if current is None:
            _warn(check, f"{repo_path}: git log failed — cannot verify")
            structural.append(repo_path)
            continue

        if current != manifest_commit:
            # Staleness is strict-exempt: expected between export boundaries (BL-009).
            # Structural manifest problems above (missing file, unknown repo, git
            # failure) are NOT exempt — they still FAIL under --strict.
            _warn(
                check,
                f"{repo_path} stale — manifest={manifest_commit} current={current}",
                strict_exempt=True,
            )
            stale.append(repo_path)

    # No PASS unless every row was actually verified. "N manifest entries all match
    # git HEAD" is a well-formed answer to a question this run could not answer
    # whenever a row is uncommitted (BL-041b) or was skipped structurally (unknown
    # repo, git log/status failure — BL-041b review F1); with the gate in place
    # len(rows) is the count actually checked wherever the PASS prints.
    if not stale and not uncommitted and not structural:
        compared = len(rows) - len(on_demand)
        _ok(
            check,
            f"{compared} kernel manifest entries all match git HEAD"
            + (f"; {len(on_demand)} on-demand row(s) not compared — HEAD is their surface"
               if on_demand else ""),
        )

# --------------------------------------------------------------------------- #
# Check 9: command_fields                                                      #
# --------------------------------------------------------------------------- #

_RUST_FENCE_RE = re.compile(r"```rust\n(.*?)```", re.DOTALL)
_RUST_STRUCT_RE = re.compile(r"pub struct (\w+)\s*\{(.*?)\n\}", re.DOTALL)
# `pub field: Type` / `pub field?: Type` — one field per line, trailing comma optional.
# Line-based rather than comma-split: a type may itself contain a comma
# (e.g. HashMap<String, String>).
_RUST_FIELD_RE = re.compile(r"^\s*pub\s+(\w+\??)\s*:\s*(.+?),?\s*$")


def _parse_rust_struct_fields(body: str) -> dict[str, str]:
    """Return {field_name: type} for a struct body, comments and attributes stripped.

    Field names keep any `?` suffix (the §6 optionality convention, reused here).
    Types are whitespace-normalised so `Vec< T >` and `Vec<T>` compare equal.
    """
    fields: dict[str, str] = {}
    for line in body.splitlines():
        line = re.sub(r"//.*$", "", line)          # /// doc comments and trailing // notes
        if not line.strip() or line.strip().startswith("#["):
            continue
        m = _RUST_FIELD_RE.match(line)
        if m:
            fields[m.group(1)] = re.sub(r"\s+", "", m.group(2))
    return fields


def _parse_structs_from_rust_text(text: str) -> dict[str, dict[str, str]]:
    return {
        m.group(1): _parse_rust_struct_fields(m.group(2))
        for m in _RUST_STRUCT_RE.finditer(text)
    }


def _parse_command_structs_from_specs(text: str, check: str) -> dict[str, dict[str, str]] | None:
    """Parse the ```rust fenced blocks under specs.md §4 into {struct: {field: type}}."""
    m = _require_section(
        text,
        r"## 4\. Tauri Command Shapes(.*?)(?=\n## |\Z)",
        check,
        "## 4. Tauri Command Shapes",
    )
    if not m:
        return None

    result: dict[str, dict[str, str]] = {}
    for block in _RUST_FENCE_RE.finditer(m.group(1)):
        # One fenced block may declare more than one struct (TrajectoryFile).
        result.update(_parse_structs_from_rust_text(block.group(1)))

    if not result:
        _fail(check, "zero structs parsed from specs.md §4 ```rust blocks")
        return None
    return result


def _parse_command_structs_from_source(commands_dir: Path) -> dict[str, dict[str, str]]:
    result: dict[str, dict[str, str]] = {}
    for rs_file in sorted(commands_dir.glob("*.rs")):
        result.update(_parse_structs_from_rust_text(rs_file.read_text(encoding="utf-8")))
    return result


def _field_types_match(doc_type: str, src_type: str, optional: bool) -> bool:
    """Compare a documented type against the Rust one.

    LIMITATION (BL-041b review F2): matching is TEXTUAL over whitespace-normalised
    type strings. A path-qualified source type (`Vec<crate::EventRow>`) or one behind
    a `type` alias will draw a false mismatch against an unqualified §4 spelling.
    Nothing in §4 documents such a type today; when one lands, either spell it the
    same way on both sides or teach this function to normalise the qualification.
    """
    if doc_type == src_type:
        return True
    # §6 convention reused: a documented `field?` is satisfied by Option<T>.
    return optional and src_type == f"Option<{doc_type}>"


def check_command_fields() -> None:
    check = "command_fields"
    specs_text = _require_file(SPECS_MD, check)
    if specs_text is None:
        return

    doc_structs = _parse_command_structs_from_specs(specs_text, check)
    if doc_structs is None:
        return
    src_structs = _parse_command_structs_from_source(COMMANDS_DIR)

    field_count = 0
    for struct_name, doc_fields in sorted(doc_structs.items()):
        src_fields = src_structs.get(struct_name)
        if src_fields is None:
            _warn(
                check,
                f"struct {struct_name!r} documented in specs.md §4 but not found in "
                f"commands/*.rs (ghost)",
            )
            continue

        for doc_name, doc_type in doc_fields.items():
            field_count += 1
            optional = doc_name.endswith("?")
            name = doc_name.rstrip("?")
            if name not in src_fields:
                _warn(
                    check,
                    f"{struct_name}.{name} documented in specs.md §4 but not in the Rust struct",
                )
            elif not _field_types_match(doc_type, src_fields[name], optional):
                _warn(
                    check,
                    f"{struct_name}.{name} type mismatch — specs.md §4 {doc_type!r}, "
                    f"Rust {src_fields[name]!r}",
                )

        documented = {n.rstrip("?") for n in doc_fields}
        for name in sorted(set(src_fields) - documented):
            _warn(check, f"{struct_name}.{name} in the Rust struct but not documented in specs.md §4")

    if not any(l in ("FAIL", "WARN") and c == check for l, c, _ in FINDINGS):
        _ok(
            check,
            f"{len(doc_structs)} documented §4 structs ({field_count} fields) "
            f"match commands/*.rs",
        )


# --------------------------------------------------------------------------- #
# Check 14: stream_envelope (BL-266 T3.8)                                      #
# --------------------------------------------------------------------------- #
# Envelope parity for the run event stream, across three sides parsed from
# source: the harness frame typespecs (`lib/aetheris/stream/frame.ex`), Rig's
# Rust wire types (`commands/run_stream.rs`), and specs.md §9. There is no DB
# table to sample. Every divergence is a FAIL, and so is a serde attribute on a
# wire type that this arm does not interpret — a mis-parse must never read as
# agreement. `command_fields` cannot do this: it skips attributes and enums.

FRAME_EX      = HARNESS_ROOT / "lib" / "aetheris" / "stream" / "frame.ex"
RUN_STREAM_RS = COMMANDS_DIR / "run_stream.rs"

# UiFrame kinds that Rig originates and the wire never carries (specs.md §9.4).
_UI_ONLY_KINDS = {"client_error", "client_status"}
_WIRE_RUST_TYPES = ("WireFrame", "StreamEvent", "StreamControl", "StreamEndReason")
_EX_TYPES = {"String.t()": "string", "integer()": "integer"}
_RUST_SCALARS = {"String": "string", "i64": "integer", "StreamControl": "string", "StreamEndReason": "string"}


def _snake(name: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


def _brace_body(text: str, open_pos: int) -> str | None:
    """The text between the `{` at open_pos and its matching `}`."""
    depth = 0
    for i in range(open_pos, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return text[open_pos + 1:i]
    return None


def _split_top(body: str, opens: str, closes: str) -> list[str]:
    """Split on commas outside any bracket pair."""
    parts, depth, cur = [], 0, []
    for ch in body:
        if ch in opens:
            depth += 1
        elif ch in closes:
            depth -= 1
        if ch == "," and depth == 0:
            parts.append("".join(cur))
            cur = []
        else:
            cur.append(ch)
    parts.append("".join(cur))
    return [p.strip() for p in parts if p.strip()]


def _parse_ex_map(body: str, prefix: str, out: dict, check: str) -> bool:
    """Elixir map typespec → {dotted_key: (type, required)}; nested maps flatten."""
    for part in _split_top(body, "{([", "})]"):
        m = re.fullmatch(r"(required|optional)\(:(\w+)\)\s*=>\s*(.+)", part, re.DOTALL)
        if m:
            required, key, typ = m.group(1) == "required", m.group(2), m.group(3).strip()
        else:
            m = re.fullmatch(r"(\w+):\s*(.+)", part, re.DOTALL)
            if not m:
                _fail(check, f"frame.ex: cannot read map field {part!r}")
                return False
            required, key, typ = True, m.group(1), m.group(2).strip()
        name = prefix + key
        if typ.startswith("%{") and required:
            inner = _brace_body(typ, 1)
            if inner is None or not _parse_ex_map(inner, name + ".", out, check):
                return False
        elif typ in _EX_TYPES:
            out[name] = (_EX_TYPES[typ], required)
        else:
            _fail(check, f"frame.ex: unrecognised type {typ!r} for {name}")
            return False
    return True


def _parse_stream_frames_from_frame_ex(text: str, check: str) -> dict | None:
    m = _require_section(text, r"@type reason ::(.*?)(?=\n\s*@type)", check, "@type reason ::")
    if not m:
        return None
    reasons = set(re.findall(r":(\w+)", m.group(1)))
    if not reasons:
        _fail(check, "zero reasons parsed from frame.ex @type reason")
        return None

    fields: dict[str, dict[str, tuple[str, bool]]] = {}
    for frame, anchor in (("event", "@type event_frame ::"), ("control", "@type control_frame ::")):
        m = _require_section(text, re.escape(anchor) + r"\s*%\{", check, anchor)
        if not m:
            return None
        body = _brace_body(text, m.end() - 1)
        parsed: dict[str, tuple[str, bool]] = {}
        if body is None or not _parse_ex_map(body, "", parsed, check):
            return None
        if parsed.pop("kind", None) is None:
            _fail(check, f"frame.ex {anchor} has no kind key")
            return None
        if not parsed:
            _fail(check, f"zero fields parsed from frame.ex {anchor}")
            return None
        fields[frame] = parsed

    guarded: set[str] = set()
    carrying: set[str] = set()
    for g in re.finditer(
        r"def stream_end\(\s*reason\s*,\s*run_id\s*,\s*(_?status)\s*\)\s*when reason in \[([^\]]*)\]", text
    ):
        atoms = set(re.findall(r":(\w+)", g.group(2)))
        guarded |= atoms
        if g.group(1) == "status":
            carrying |= atoms
    if not guarded:
        _fail(check, "zero stream_end/3 guard clauses parsed from frame.ex")
        return None
    if guarded != reasons:
        _fail(check, f"frame.ex stream_end/3 guards cover {sorted(guarded)} but @type reason is {sorted(reasons)}")
        return None

    kinds = set(re.findall(r'\bkind: "(\w+)"', text))
    controls = set(re.findall(r'\bcontrol: "(\w+)"', text))
    if not kinds or not controls:
        _fail(check, "frame.ex: kind/control discriminator literals not found")
        return None
    return {"fields": fields, "reasons": reasons, "carrying": carrying, "kinds": kinds, "controls": controls}


def _rust_items(text: str) -> dict[str, dict]:
    """{name: {"serde": [attr bodies], "body": str}} for every `pub enum|struct X {`."""
    items: dict[str, dict] = {}
    for m in re.finditer(r"((?:^[ \t]*(?:#\[.*\]|///.*)\n)*)^[ \t]*pub (?:enum|struct) (\w+)\s*\{", text, re.M):
        body = _brace_body(text, m.end() - 1)
        if body is not None:
            items[m.group(2)] = {"serde": re.findall(r"#\[serde\((.*)\)\]", m.group(1)), "body": body}
    return items


def _rust_members(body: str) -> list[tuple[str, list[str], dict[str, str] | None]]:
    """Enum variants or struct fields: [(name, inner_attrs, {field: type} | None)].

    For a struct the "fields" slot is None and the member's type is under key "".
    """
    body = re.sub(r"//.*$", "", body, flags=re.M)
    out = []
    for part in _split_top(body, "{([<", "})]>"):
        attrs = re.findall(r"#\[(.*?)\]\s*", part)
        part = re.sub(r"#\[.*?\]\s*", "", part).strip()
        part = re.sub(r"^pub\s+", "", part)
        m = re.fullmatch(r"(\w+)\s*:\s*(.+)", part, re.DOTALL)
        if m:
            out.append((m.group(1), attrs, {"": re.sub(r"\s+", "", m.group(2))}))
            continue
        m = re.fullmatch(r"(\w+)\s*(\{(.*)\})?", part, re.DOTALL)
        if not m:
            out.append((part, attrs, None))
            continue
        fields = None
        if m.group(2):
            fields = {}
            for fname, fattrs, ftype in _rust_members(m.group(3)):
                attrs.extend(fattrs)
                fields[fname] = (ftype or {}).get("", "")
        out.append((m.group(1), attrs, fields))
    return out


def _serde_container(attrs: list[str], name: str, check: str) -> dict[str, str] | None:
    """Interpret `tag` and `rename_all = "snake_case"`; anything else FAILs."""
    result: dict[str, str] = {}
    for attr in attrs:
        for kv in _split_top(attr, "(", ")"):
            m = re.fullmatch(r'(\w+)\s*=\s*"([^"]*)"', kv)
            if m and m.group(1) == "tag":
                result["tag"] = m.group(2)
            elif m and m.group(1) == "rename_all" and m.group(2) == "snake_case":
                result["rename_all"] = m.group(2)
            else:
                _fail(check, f"run_stream.rs: uninterpreted serde attribute on {name}: {kv!r}")
                return None
    return result


def _rust_type(typ: str) -> tuple[str, bool] | None:
    m = re.fullmatch(r"Option<(.+)>", typ)
    inner, optional = (m.group(1), True) if m else (typ, False)
    if inner in _RUST_SCALARS:
        return _RUST_SCALARS[inner], not optional
    if inner == "StreamEvent" and not optional:
        return "object", True
    return None


def _variant_name(name: str, serde: dict[str, str]) -> str:
    return _snake(name) if serde.get("rename_all") == "snake_case" else name


def _parse_stream_types_from_rust(text: str, check: str) -> dict | None:
    items = _rust_items(text)
    for name in _WIRE_RUST_TYPES + ("UiFrame",):
        if name not in items:
            _fail(check, f"run_stream.rs: `pub enum|struct {name}` not found")
            return None

    serde = {}
    for name in _WIRE_RUST_TYPES + ("UiFrame",):
        s = _serde_container(items[name]["serde"], name, check)
        if s is None:
            return None
        serde[name] = s
    if serde["StreamEvent"]:
        _fail(check, f"run_stream.rs: uninterpreted serde attribute on StreamEvent: {serde['StreamEvent']}")
        return None

    members = {name: _rust_members(items[name]["body"]) for name in _WIRE_RUST_TYPES + ("UiFrame",)}
    for name in _WIRE_RUST_TYPES:
        for member, attrs, _ in members[name]:
            if any(a.startswith("serde") for a in attrs):
                _fail(check, f"run_stream.rs: uninterpreted serde attribute inside {name}::{member}")
                return None

    event_fields: dict[str, tuple[str, bool]] = {}
    for fname, _, ftype in members["StreamEvent"]:
        t = _rust_type((ftype or {}).get("", ""))
        if t is None or t[0] == "object":
            _fail(check, f"run_stream.rs: StreamEvent.{fname} has an unrecognised type")
            return None
        event_fields[fname] = t

    tag = serde["WireFrame"].get("tag")
    if tag is None:
        _fail(check, "run_stream.rs: WireFrame has no serde tag")
        return None
    fields: dict[str, dict[str, tuple[str, bool]]] = {}
    for variant, _, vfields in members["WireFrame"]:
        kind = _variant_name(variant, serde["WireFrame"])
        parsed: dict[str, tuple[str, bool]] = {}
        for fname, ftype in (vfields or {}).items():
            t = _rust_type(ftype)
            if t is None:
                _fail(check, f"run_stream.rs: WireFrame::{variant}.{fname} has an unrecognised type {ftype!r}")
                return None
            if t[0] == "object":
                parsed.update({f"{fname}.{k}": v for k, v in event_fields.items()})
            else:
                parsed[fname] = t
        fields[kind] = parsed

    ui_fields = {
        _variant_name(v, serde["UiFrame"]): set(vf or {}) for v, _, vf in members["UiFrame"]
    }
    return {
        "tag": tag,
        "ui_tag": serde["UiFrame"].get("tag"),
        "fields": fields,
        "reasons": {_variant_name(v, serde["StreamEndReason"]) for v, _, _ in members["StreamEndReason"]},
        "controls": {_variant_name(v, serde["StreamControl"]) for v, _, _ in members["StreamControl"]},
        "event_fields": set(event_fields),
        "ui_fields": ui_fields,
    }


def _parse_stream_docs(text: str, check: str) -> dict | None:
    m = _require_section(text, r"## 9\. Emitted Tauri Events(.*?)(?=\n## |\Z)", check, "## 9. Emitted Tauri Events")
    if not m:
        return None
    section = m.group(1)
    subs = {}
    for num, anchor in (("2", "### 9.2"), ("3", "### 9.3"), ("4", "### 9.4")):
        s = _require_section(section, rf"### 9\.{num} (.*?)(?=\n### |\Z)", check, anchor)
        if not s:
            return None
        subs[num] = s.group(1)

    fields: dict[str, dict[str, tuple[str, bool]]] = {}
    for frame, field, typ, req in re.findall(r"^\| `(\w+)` \| `([\w.]+)` \| (\w+) \| (yes|no) \|", subs["2"], re.M):
        fields.setdefault(frame, {})[field] = (typ, req == "yes")
    reasons = dict(re.findall(r"^\| `(\w+)` \| (yes|no) \|", subs["3"], re.M))
    ui_kinds = set(re.findall(r"^\| `(\w+)` \|", subs["4"], re.M))
    for label, parsed in (("§9.2 wire fields", fields), ("§9.3 reasons", reasons), ("§9.4 UI kinds", ui_kinds)):
        if not parsed:
            _fail(check, f"zero rows parsed from specs.md {label}")
            return None
    return {
        "fields": fields,
        "reasons": set(reasons),
        "carrying": {r for r, carries in reasons.items() if carries == "yes"},
        "ui_kinds": ui_kinds,
    }


def _diff_sets(check: str, what: str, a_name: str, a: set, b_name: str, b: set) -> None:
    for x in sorted(a - b):
        _fail(check, f"{what} {x!r} in {a_name} but not in {b_name}")
    for x in sorted(b - a):
        _fail(check, f"{what} {x!r} in {b_name} but not in {a_name}")


def _diff_fields(check: str, a_name: str, a: dict, b_name: str, b: dict) -> None:
    _diff_sets(check, "frame", a_name, set(a), b_name, set(b))
    for frame in sorted(set(a) & set(b)):
        _diff_sets(check, f"{frame} field", a_name, set(a[frame]), b_name, set(b[frame]))
        for field in sorted(set(a[frame]) & set(b[frame])):
            (ta, ra), (tb, rb) = a[frame][field], b[frame][field]
            if ta != tb:
                _fail(check, f"{frame}.{field} type: {a_name} {ta}, {b_name} {tb}")
            if ra != rb:
                _fail(check, f"{frame}.{field} required: {a_name} {ra}, {b_name} {rb}")


def _evaluate_stream_envelope(frame_ex: str, rust: str, specs: str, check: str = "stream_envelope") -> None:
    h = _parse_stream_frames_from_frame_ex(frame_ex, check)
    r = _parse_stream_types_from_rust(rust, check)
    d = _parse_stream_docs(specs, check)
    if h is None or r is None or d is None:
        return

    _diff_fields(check, "frame.ex", h["fields"], "run_stream.rs", r["fields"])
    _diff_fields(check, "frame.ex", h["fields"], "specs.md §9.2", d["fields"])
    _diff_sets(check, "reason", "frame.ex", h["reasons"], "run_stream.rs", r["reasons"])
    _diff_sets(check, "reason", "frame.ex", h["reasons"], "specs.md §9.3", d["reasons"])
    _diff_sets(check, "status-carrying reason", "frame.ex", h["carrying"], "specs.md §9.3", d["carrying"])

    _diff_sets(check, "kind literal", "frame.ex", h["kinds"], "run_stream.rs", set(r["fields"]))
    _diff_sets(check, "control literal", "frame.ex", h["controls"], "run_stream.rs", r["controls"])
    if r["tag"] != "kind":
        _fail(check, f"run_stream.rs WireFrame tag is {r['tag']!r}, frame.ex discriminates on 'kind'")
    if r["ui_tag"] != r["tag"]:
        _fail(check, f"run_stream.rs UiFrame tag {r['ui_tag']!r} differs from WireFrame tag {r['tag']!r}")

    if "cursor" not in r["fields"].get("event", {}):
        _fail(check, "run_stream.rs: cursor missing from the WireFrame event variant")
    if "cursor" in r["event_fields"]:
        _fail(check, "run_stream.rs: StreamEvent carries cursor, which reaches the webview")
    for kind, names in sorted(r["ui_fields"].items()):
        if "cursor" in names:
            _fail(check, f"run_stream.rs: UiFrame::{kind} carries cursor, which reaches the webview")

    ui_kinds = set(r["ui_fields"])
    _diff_sets(check, "UiFrame kind", "run_stream.rs UiFrame", ui_kinds,
               "wire kinds + UI-only kinds", set(r["fields"]) | _UI_ONLY_KINDS)
    _diff_sets(check, "UiFrame kind", "run_stream.rs UiFrame", ui_kinds, "specs.md §9.4", d["ui_kinds"])
    for kind in sorted(_UI_ONLY_KINDS & (h["kinds"] | set(r["fields"]))):
        _fail(check, f"UI-only kind {kind!r} appears on the wire")

    if not any(l == "FAIL" and c == check for l, c, _ in FINDINGS):
        n = sum(len(f) for f in h["fields"].values())
        _ok(check, f"{len(h['fields'])} frames ({n} fields), {len(h['reasons'])} reasons: "
                   f"frame.ex / run_stream.rs / specs.md §9")
    _info(check, "UI-only UiFrame kinds, documented in §9.4 and absent from the wire: "
                 + ", ".join(sorted(_UI_ONLY_KINDS)))


def check_stream_envelope() -> None:
    check = "stream_envelope"
    frame_ex = _require_file(FRAME_EX, check)
    rust = _require_file(RUN_STREAM_RS, check)
    specs = _require_file(SPECS_MD, check)
    if frame_ex is None or rust is None or specs is None:
        return
    _evaluate_stream_envelope(frame_ex, rust, specs, check)


# --------------------------------------------------------------------------- #
# Check 10: use_case_registry                                                  #
# --------------------------------------------------------------------------- #
# docs/use-cases.md is the declaration of what the use cases are and which are dormant
# (ds t1a). This check compares it against every OTHER enumeration of use cases whose
# content a parser can extract WITHOUT DECIDING WHAT A SENTENCE MEANS — a markdown table
# column, a Python/Rust literal, a set of file paths, a JSON key set. That criterion is
# ds t1a's, and it is constraint 2 made decidable: a document mixing prose and enumeration
# is checked and failed, never rewritten by a script that has to locate a list inside
# paragraphs. Surfaces whose enumeration lives in prose (pytest.ini's dormancy comment and
# its `markers = dormant: …` sentence, ROADMAP.md, the manifest's runbook prose,
# orchestrator.exs's few-shot examples) are OUT OF SCOPE and are fixed by a human edit or
# de-numeralised — never by this check.
#
# It also inherits gc t3's discharge predicate structurally rather than by implementing one:
# a markdown table row and a Rust literal cannot be confused with an enumeration quoted
# inside a dated correction block, and prose is out of scope, so there is no live-vs-quoted
# distinction left for this check to get wrong.
#
# NOT re-checked here: docs/capability-matrix.md's `## ` headings, which are DERIVED from
# assemble_matrix.SECTIONS and are already asserted against it by
# tests/test_assemble_matrix.py. Checking the generated output and calling the input verified
# is the seam ds t1a exists to close, so this check reads SECTIONS itself.

USE_CASES_MD  = REPO_ROOT / "docs" / "use-cases.md"
ASSEMBLE_PY   = REPO_ROOT / "scripts" / "assemble_matrix.py"
OVERRIDES_JSON = REPO_ROOT / "docs" / "capability-matrix-overrides.json"
TOOLS_MANIFEST_TEST = REPO_ROOT / "tests" / "test_tools_manifests.py"
TOOLS_RS      = RIG_ROOT / "src-tauri" / "src" / "commands" / "tools.rs"
README_MD     = REPO_ROOT / "README.md"
AGENTS_CLAUDE_MD = REPO_ROOT / "CLAUDE.md"

_REGISTRY_ROW_RE = re.compile(
    r"^\|\s*`([a-z0-9/_-]+)`\s*\|\s*(\w+)\s*\|", re.M
)
# A doc table's identifier column is read STRUCTURALLY, not lexically: take the contiguous
# pipe-row block, drop its header row and its `---` separator, and read cell 1 of the rest.
# A lexical rule ("cells that look like identifiers") would have to decide what a heading
# means, which is the thing this whole check is defined to never do.
_TABLE_SEP_RE = re.compile(r"^\|[\s:|-]+\|$")


def _first_column(section: str) -> list[str]:
    rows = [ln.strip() for ln in section.splitlines() if ln.strip().startswith("|")]
    sep = next((i for i, ln in enumerate(rows) if _TABLE_SEP_RE.match(ln)), None)
    if sep is None:
        return []
    cells = [ln.split("|")[1].strip() for ln in rows[sep + 1:] if ln.count("|") >= 2]
    out = []
    for c in cells:
        c = re.sub(r"^\[(.*)\]\(.*\)$", r"\1", c)   # [`payslip/`](payslip/) -> `payslip/`
        out.append(c.strip("`").rstrip("/"))
    return [c for c in out if c]


def _parse_registry(check: str) -> list[tuple[str, str]] | None:
    text = _require_file(USE_CASES_MD, check)
    if text is None:
        return None
    m = _require_section(text, r"\n## The registry\n(.*?)(?=\n## |\Z)", check, "## The registry")
    if not m:
        return None
    rows = _REGISTRY_ROW_RE.findall(m.group(1))
    if not rows:
        _fail(check, "zero rows parsed from docs/use-cases.md '## The registry' table")
        return None
    return rows


def _table_ids(path: Path, section_pattern: str, anchor: str, check: str) -> set[str] | None:
    """First-cell identifiers of the pipe table inside a named section."""
    text = _require_file(path, check)
    if text is None:
        return None
    m = _require_section(text, section_pattern, check, f"{path.name} {anchor}")
    if not m:
        return None
    ids = set(_first_column(m.group(1)))
    if not ids:
        _fail(check, f"zero identifiers parsed from {path.name} {anchor}")
        return None
    return ids


def _compare(check: str, label: str, expected: set[str], actual: set[str], subset: bool) -> None:
    """One arm. `subset` arms legitimately cover part of the registry, by design."""
    extra = sorted(actual - expected)
    missing = sorted(expected - actual)
    if subset:
        if extra:
            _fail(check, f"{label}: {extra} not in the registry (subset arm — extras are the failure)")
        else:
            _ok(check, f"{label}: {len(actual)} entr(ies), all in the registry (subset arm)")
        return
    if extra or missing:
        _fail(
            check,
            f"{label} disagrees with docs/use-cases.md — "
            f"absent from the registry: {extra}; missing from this surface: {missing}",
        )
    else:
        _ok(check, f"{label}: {len(actual)} entr(ies) == the registry")


def check_use_case_registry() -> None:
    check = "use_case_registry"

    rows = _parse_registry(check)
    if rows is None:
        return
    registry = {rid for rid, _ in rows}

    # Two derived keyings, both stated in the messages that use them:
    #   matrix key   api/tenant -> api_tenant   (the capability matrix's identifier shape)
    #   sweep key    api/tenant -> api          (surfaces keyed on the parent manifest dir)
    sweep_keys = {rid.split("/")[0] for rid in registry}

    # The agent-bearing predicate. The capability matrix's unit is an AGENT: each section is
    # produced by an agents/capability_matrix_<key>.exs run, and the assembled document is read
    # whole into the planner's system prompt. Comparing SECTIONS to the FULL registry would
    # oblige us to author a section agent for a dormant use case — adding planner capability for
    # paused work, and asserting a capability nothing can currently exercise. So SECTIONS is
    # compared to the registry FILTERED to use cases that have agents, and boxy-pipeline's
    # omission from the matrix becomes DECLARED rather than accidental. The predicate is named
    # in the message below so a failure says which set it is comparing.
    agent_bearing = {
        rid for rid in registry if list((REPO_ROOT / rid / "agents").glob("*.exs"))
    }
    matrix_keys = {rid.replace("/", "_") for rid in agent_bearing}

    _info(
        check,
        f"registry: {len(registry)} use case(s); agent-bearing: {len(agent_bearing)}; "
        f"non-agent-bearing (excluded from capability-matrix arms): "
        f"{sorted(registry - agent_bearing)}",
    )

    # --- Arm 1: agents CLAUDE.md §Key docs table --------------------------------------
    ids = _table_ids(
        AGENTS_CLAUDE_MD,
        r"\n## Key docs to read for each use case\n(.*?)(?=\n## |\Z)",
        "§Key docs to read for each use case",
        check,
    )
    if ids is not None:
        _compare(check, "CLAUDE.md §Key docs table", registry, ids, subset=False)

    # --- Arm 2: README.md §Use cases table ---------------------------------------------
    ids = _table_ids(
        README_MD, r"\n## Use cases\n(.*?)(?=\n## |\n### |\Z)", "§Use cases", check
    )
    if ids is not None:
        _compare(check, "README.md §Use cases table", registry, ids, subset=False)

    # --- Arm 3: assemble_matrix.SECTIONS ------------------------------------------------
    text = _require_file(ASSEMBLE_PY, check)
    if text is not None:
        m = _require_section(text, r"\bSECTIONS = \[(.*?)\n\]", check, "assemble_matrix.py SECTIONS")
        if m:
            keys = set(re.findall(r'\(\s*"([a-z0-9_-]+)"\s*,', m.group(1)))
            _compare(
                check,
                "assemble_matrix.SECTIONS vs the registry filtered to AGENT-BEARING use cases",
                matrix_keys,
                keys,
                subset=False,
            )

    # --- Arm 4: the capability-matrix section agents ------------------------------------
    exs = {
        p.stem.replace("capability_matrix_", "")
        for p in (REPO_ROOT / "agents").glob("capability_matrix_*.exs")
    }
    if exs:
        _compare(
            check,
            "agents/capability_matrix_*.exs vs the registry filtered to AGENT-BEARING use cases",
            matrix_keys,
            exs,
            subset=False,
        )
    else:
        _fail(check, "zero agents/capability_matrix_*.exs files found")

    # --- Arm 5: capability-matrix-overrides.json keys (subset by design) -----------------
    text = _require_file(OVERRIDES_JSON, check)
    if text is not None:
        try:
            keys = {k for k in json.loads(text) if not k.startswith("_")}
        except json.JSONDecodeError as exc:
            _fail(check, f"capability-matrix-overrides.json is not valid JSON: {exc}")
        else:
            _compare(check, "capability-matrix-overrides.json keys", matrix_keys, keys, subset=True)

    # --- Arms 6+7: tests/test_tools_manifests.py SWEPT and NO_MANIFEST_YET ---------------
    # Keyed on the SWEEP keying: these surfaces walk top-level dirs, so api/tenant and
    # api/gateway present as one `api`.
    text = _require_file(TOOLS_MANIFEST_TEST, check)
    if text is not None:
        m = _require_section(text, r"assert SWEPT == \[(.*?)\]", check, "assert SWEPT == [")
        if m:
            swept = set(re.findall(r'"([a-z0-9/_-]+)"', m.group(1)))
            _compare(
                check,
                "test_tools_manifests SWEPT literal (registry keyed by top-level dir)",
                sweep_keys,
                swept,
                subset=False,
            )
        m = _require_section(text, r"NO_MANIFEST_YET = \((.*?)\)", check, "NO_MANIFEST_YET = (")
        if m:
            nmy = set(re.findall(r'"([a-z0-9/_-]+)"', m.group(1)))
            _compare(check, "test_tools_manifests NO_MANIFEST_YET", sweep_keys, nmy, subset=True)

    # --- Arm 8: the committed tools.json file set (subset by design) ---------------------
    manifests = {p.parent.name for p in REPO_ROOT.glob("*/tools.json")}
    _compare(check, "committed <use_case>/tools.json set", sweep_keys, manifests, subset=True)

    # --- Arm 9: Rig tools.rs's hardcoded manifest list (subset by design) ----------------
    text = _require_file(TOOLS_RS, check)
    if text is not None:
        m = re.search(r"vec!\[((?:\s*\"[a-z0-9/_-]+\"\s*,?)+)\]", text)
        if not m:
            _fail(check, "anchor not found: tools.rs committed-manifest vec![...]")
        else:
            names = set(re.findall(r'"([a-z0-9/_-]+)"', m.group(1)))
            _compare(check, "tools.rs discovery_finds_every_committed_manifest vec!", sweep_keys, names, subset=True)


# --------------------------------------------------------------------------- #
# Main                                                                         #
# --------------------------------------------------------------------------- #


# --------------------------------------------------------------------------- #
# 11. backlog_resolution — every BL-nnn in the scoped corpus names a real row   #
# --------------------------------------------------------------------------- #

# The backlog is two files since ds t1b, and the row set is their UNION. The id is
# the address and the path is never load-bearing, so this check is what makes that
# claim testable rather than aspirational: a reference resolves, or it FAILS.
BACKLOG_FILES = (
    REPO_ROOT / "docs" / "backlog-2026-06.md",
    REPO_ROOT / "docs" / "backlog-2026-06-closed.md",
)

# Strict three-digit form WITH A BOUNDARY on both sides. The boundary is the point:
# a bare `BL-\d+` truncates the metasyntactic placeholders the docs use — `BL-0xx`,
# `BL-0NN`, `BL-1xx`, and the quoted grep pattern `BL-09[02]` — into `BL-0`, `BL-1`
# and `BL-09`, and would report each as a dangling reference. Removing them
# structurally is cheaper and more honest than allowlisting them one by one.
BACKLOG_REF_RE = re.compile(r"(?<![0-9A-Za-z])BL-(\d{3})(?![0-9])")
BACKLOG_ROW_RE = re.compile(r"^### ((?:BL-\d+)(?:\s*\+\s*BL-\d+)*)\s*—", re.M)

# Scope: the backlog files themselves, plus every executable in both repos. NOT all
# committed prose — a July review packet naming a row folded before it was filed is
# a true historical statement, not a defect this split creates. "Executable" is by
# extension, not by the mode bit: `git ls-files -s` records ZERO files as 100755 in
# aetheris-agents, so the bit would exclude every script the check exists to cover.
BACKLOG_SCOPE_GLOBS = ("*.py", "*.sh")

# BL-252: open rows' bodies live in `docs/evidence/<ID>.md`, so the references they carry
# are scoped there. Read from the filesystem, not `git ls-files`, so an evidence file is
# checked before the commit that adds it.
BACKLOG_EVIDENCE_DIR = REPO_ROOT / "docs" / "evidence"

# An unresolvable reference FAILS. It is deliberately NOT a WARN: the two standing
# `project_knowledge` staleness WARNs are strict-exempt and read as expected truth,
# and a dangling-id WARN sitting beside them would inherit that reading — which is
# the one thing this check must not do.
#
# The allowlist is keyed by (id, repo-relative path) and every entry carries its
# reason. Keyed by BOTH so that an id excused in one file is not silently excused
# everywhere it might later appear.
BACKLOG_REF_ALLOW: dict[tuple[str, str], str] = {
    ("BL-063", "docs/backlog-2026-06-closed.md"):
        "the same historical statement, inside BL-030's own body — which is DONE and "
        "so travelled to the archive at ds t1b. Two occurrences, one per file, is a "
        "consequence of the split and is why the allowlist is keyed by (id, FILE): "
        "before the split both sat in one file and one key covered them.",
    # This file is in its own corpus, and its allowlist names ids in order to excuse
    # them — so the reason strings above are themselves scanned. That is `CLAUDE.md`'s
    # *a census recorded inside the document it censuses*, and the honest remedy is an
    # explicit entry rather than excluding the checker from its own scope, which would
    # blind it to a real dangling id written into it later.
    ("BL-063", "scripts/drift_check.py"):
        "self-reference: this allowlist's own key and reason text.",
    ("BL-999", "scripts/drift_check.py"):
        "self-reference: this allowlist's own key and reason text.",
    ("BL-998", "scripts/drift_check.py"):
        "self-reference, as above — naming the canonical nonexistent id in a reason "
        "string is itself a reference to it. Every id excused below adds one of these; "
        "that is the cost of keeping the checker inside its own corpus, and it is the "
        "cheaper side of the trade.",
    **{
        (f"BL-{n}", "tests/test_drift_check.py"):
            "synthetic fixture id for THIS check's own tests. Deliberately in a range "
            "no real row uses: an earlier draft used BL-101/BL-102, which happen to be "
            "real rows, so the live arm passed on a coincidence rather than on the "
            "fixture being sound."
        for n in ("201", "202", "203", "204", "205")
    },
    ("BL-998", "tests/test_drift_check.py"):
        "the canonical NONEXISTENT id, used by the dangling-reference tests and by "
        "the mutation probe. It must never become a real row.",
    ("BL-999", "../aetheris/scripts/sprint.sh"):
        "documentation sentinel: sprint.sh's own comment uses BL-999 as the "
        "canonical well-formed-but-dangling reference. Not resolving IS the point.",
    **{
        (f"BL-{n}", "tests/test_backlog_status.py"):
            "synthetic fixture id for the parser's own tests; never a real row."
        for n in ("900", "901", "902", "903", "904", "905", "906", "907", "908",
                  "910", "911", "912", "920", "930", "940", "950",
                  # defeat 5 (`<details>` depth): 960/961 the live-and-archived
                  # pair, 970 the archived-only row, 980 the no-field-at-any-depth
                  # control. Extended as a DATA ENUMERATION, per agents CLAUDE.md
                  # §Learning — m6-cloudcost: this is the set itself, not a count
                  # of it, so it grows by a member rather than by a corrected number.
                  "960", "961", "970", "980",
                  # the prose-and-fence masking regression: 990 the row whose
                  # PROSE names the tag, 991 the heading quoted inside a fence,
                  # 992 the row after it that must survive both.
                  "990", "991", "992",
                  # BL-252's index shape: 993 the index row, 994 the wrong-id and
                  # second-row fixtures, 995 the legacy row beside it, 996 placement.
                  "993", "994", "995", "996")
    },
    ("BL-998", "tests/test_known_red_resolver.py"):
        "the canonical NONEXISTENT id, as the resolver test's dangling-reference control.",
}


def _backlog_row_ids() -> set[str]:
    ids: set[str] = set()
    for path in BACKLOG_FILES:
        if not path.exists():
            return set()
        for group in BACKLOG_ROW_RE.findall(path.read_text()):
            ids.update(re.findall(r"BL-\d+", group))
    return ids


def _backlog_scope_files() -> list[tuple[Path, str]]:
    """(absolute path, label) for every file in scope, from git's own file list."""
    out: list[tuple[Path, str]] = []
    for path in BACKLOG_FILES:
        out.append((path, str(path.relative_to(REPO_ROOT))))
    for path in sorted(BACKLOG_EVIDENCE_DIR.glob("*.md")):
        out.append((path, f"docs/evidence/{path.name}"))
    for root, prefix in ((REPO_ROOT, ""), (HARNESS_ROOT, "../aetheris/")):
        try:
            listed = subprocess.run(
                ["git", "-C", str(root), "ls-files", "-z", *BACKLOG_SCOPE_GLOBS],
                capture_output=True, text=True, check=True,
            ).stdout
        except (subprocess.CalledProcessError, FileNotFoundError):
            return []
        for rel in filter(None, listed.split("\0")):
            out.append((root / rel, prefix + rel))
    return out


def check_backlog_resolution():
    check = "backlog_resolution"
    rows = _backlog_row_ids()
    if not rows:
        _fail(check, f"zero backlog rows parsed from {[str(p) for p in BACKLOG_FILES]}")
        return
    files = _backlog_scope_files()
    if not files:
        _fail(check, "could not list the scoped corpus from git")
        return

    unresolved: list[tuple[str, str, int]] = []
    allowed = 0
    scanned = 0
    for path, label in files:
        try:
            text = path.read_text(errors="replace")
        except OSError:
            _fail(check, f"scoped file not readable: {label}")
            return
        scanned += 1
        hits: dict[str, int] = {}
        for m in BACKLOG_REF_RE.finditer(text):
            ref = "BL-" + m.group(1)
            if ref in rows:
                continue
            hits[ref] = hits.get(ref, 0) + 1
        for ref, n in sorted(hits.items()):
            if (ref, label) in BACKLOG_REF_ALLOW:
                allowed += n
            else:
                unresolved.append((ref, label, n))

    for ref, label, n in unresolved:
        _fail(check, f"{ref} referenced {n}x in {label} but names no row in the "
                     f"backlog union — add a row, or allowlist it by (id, file) "
                     f"with a reason in BACKLOG_REF_ALLOW")
    if unresolved:
        return
    _ok(check, f"{len(rows)} rows over the union; {scanned} scoped files; every "
                 f"BL-nnn reference resolves ({allowed} allowlisted occurrence(s), "
                 f"{len(BACKLOG_REF_ALLOW)} allowlist entr(ies))")



# --------------------------------------------------------------------------- #
# Check 12: index_integrity (hybrid-context design §1.1)                        #
# --------------------------------------------------------------------------- #
#
# An INDEXED TREE is a directory whose generated `index.md` carries a manifest row —
# the manifest is the top-level map, so the tree list is read from it and never kept
# as a second list here. For each tree, at HEAD in the row's own repo:
#
#   direction 1 — every index entry's path resolves to a file at HEAD      (FAIL)
#   direction 2 — every markdown file at HEAD in the tree has an entry      (FAIL)
#   the §1.2 gap — a file at HEAD with missing/unreadable/incomplete
#                  frontmatter, i.e. a document the generator would have
#                  refused, committed anyway                                (FAIL)
#   staleness   — an entry whose title or description differs from the
#                  file's frontmatter: the index was not regenerated         (WARN)
#
# HEAD rather than the working tree, on check 8's terms: the committed index is the
# artifact that travels, and an uncommitted edit under the tree makes this run's reading
# vacuous for that tree — reported as a strict-exempt WARN, not hidden.
#
# The file-with-no-entry direction mechanises a repair performed by hand twice: harness
# bcf3b65 (the activegraph brief, 2026-08-24) and bb42099 (the hybrid note, 7 on disk vs
# 6 linked, gap accepted 2026-09-07).

_INDEX_ENTRY_RE = re.compile(r"^- \[(.*)\]\(([^)]+)\) - (.*)$")
_INDEX_REQUIRED = ("type", "title", "description")


def _unescape_link_text(text: str) -> str:
    return text.replace("\\[", "[").replace("\\]", "]")


def _parse_index_entries(text: str) -> dict[str, tuple[str, str]]:
    """{relative path: (title, description)} from a generated index's entry lines."""
    entries: dict[str, tuple[str, str]] = {}
    for line in text.splitlines():
        m = _INDEX_ENTRY_RE.match(line)
        if m:
            entries[m.group(2)] = (_unescape_link_text(m.group(1)), m.group(3))
    return entries


def _git_show_text(repo_dir: Path, path: str) -> str | None:
    try:
        result = subprocess.run(
            ["git", "show", f"HEAD:{path}"],
            cwd=repo_dir, capture_output=True, timeout=30,
        )
    except Exception:
        return None
    if result.returncode != 0:
        return None
    return result.stdout.decode("utf-8", "replace")


def _git_ls_tree_md(repo_dir: Path, tree: str) -> list[str] | None:
    """Every `*.md` path at HEAD under `tree` (repo-relative), or None if git failed."""
    try:
        result = subprocess.run(
            ["git", "ls-tree", "-r", "--name-only", "HEAD", "--", tree],
            cwd=repo_dir, capture_output=True, text=True, timeout=30,
        )
    except Exception:
        return None
    if result.returncode != 0:
        return None
    return [ln for ln in result.stdout.splitlines() if ln.endswith(".md")]


def _indexed_trees() -> list[tuple[str, str, str]] | None:
    """[(repo_name, tree, index_path)] from manifest rows whose path is an index.md.

    None when the manifest cannot be read at all (structural, reported by the caller).
    """
    if not MANIFEST_MD.exists():
        return None
    text = MANIFEST_MD.read_text(encoding="utf-8")
    trees: list[tuple[str, str, str]] = []
    for repo_path, repo_name, _commit, _surface in _MANIFEST_ROW_RE.findall(text):
        if Path(repo_path).name == "index.md":
            trees.append((repo_name, str(Path(repo_path).parent), repo_path))
    return trees


def check_index_integrity() -> None:
    check = "index_integrity"

    trees = _indexed_trees()
    if trees is None:
        _warn(check, "docs/project-knowledge-manifest.md not found — no indexed tree can be read")
        return
    if not trees:
        _warn(check, "the manifest carries no `index.md` row — no indexed tree to check; "
                     "the hybrid architecture requires at least one")
        return

    for repo_name, tree, index_path in trees:
        label = f"{repo_name}:{tree}"
        repo_dir = _REPO_DIR_MAP.get(repo_name)
        if repo_dir is None:
            _warn(check, f"{label}: unknown repo name {repo_name!r} in manifest — cannot verify")
            continue

        index_text = _git_show_text(repo_dir, index_path)
        if index_text is None:
            _fail(check, f"{label}: {index_path} is not at HEAD — the manifest names an index "
                         f"that is not committed")
            continue
        entries = _parse_index_entries(index_text)
        if not entries:
            _fail(check, f"{label}: {index_path} carries zero entries — not a generated index")
            continue

        files = _git_ls_tree_md(repo_dir, tree)
        if files is None:
            _warn(check, f"{label}: git ls-tree failed — cannot enumerate the tree at HEAD")
            continue
        files = [f for f in files if f != index_path]

        dirty = _git_is_dirty(repo_dir, tree)
        if dirty is None:
            _warn(check, f"{label}: git status failed — cannot check for uncommitted edits")
        elif dirty:
            _warn(
                check,
                f"{label} has uncommitted working-tree changes — this check reads HEAD, so "
                f"its reading for this tree is about the committed index and tree only; "
                f"re-run after committing",
                strict_exempt=True,
            )

        problems = 0
        # direction 1: every entry resolves at HEAD
        files_rel = {str(Path(f).relative_to(tree)) for f in files}
        for rel in sorted(entries):
            if rel not in files_rel:
                _fail(check, f"{label}: index entry `{rel}` does not resolve at HEAD")
                problems += 1

        # direction 2 + the §1.2 gap: every file at HEAD is indexable and indexed
        stale: list[str] = []
        for repo_path in sorted(files):
            rel = str(Path(repo_path).relative_to(tree))
            text = _git_show_text(repo_dir, repo_path)
            if text is None:
                _warn(check, f"{label}: git show failed for {repo_path}")
                problems += 1
                continue
            try:
                doc = read_document(text)
            except FrontmatterError as exc:
                _fail(check, f"{label}: `{rel}` has unreadable frontmatter ({exc}) — the "
                             f"generator would refuse it; it is invisible to retrieval")
                problems += 1
                continue
            fm = doc.frontmatter
            if fm is None:
                _fail(check, f"{label}: `{rel}` has no frontmatter — the generator would refuse "
                             f"it; it is invisible to retrieval")
                problems += 1
                continue
            missing = [
                f for f in _INDEX_REQUIRED
                if not isinstance(fm.get(f), str) or not fm.get(f, "").strip()
            ]
            if missing:
                _fail(check, f"{label}: `{rel}` lacks required frontmatter "
                             f"{', '.join(missing)} — the generator would refuse it")
                problems += 1
                continue
            if rel not in entries:
                _fail(check, f"{label}: `{rel}` is at HEAD with frontmatter and has no index "
                             f"entry — regenerate {index_path}")
                problems += 1
                continue
            if entries[rel] != (fm["title"], fm["description"]):
                stale.append(rel)

        if stale:
            _warn(check, f"{label}: {len(stale)} entr{'y' if len(stale) == 1 else 'ies'} no "
                         f"longer match the file's frontmatter (title or description) — "
                         f"regenerate {index_path}: " + ", ".join(stale))
            problems += 1

        if problems == 0 and dirty is False:
            _ok(check, f"{label}: {len(entries)} index entries ↔ {len(files)} files at HEAD, "
                       f"every file indexed and every entry current")


# --------------------------------------------------------------------------- #
# Check 13: kernel_budget (hybrid-context design §2.1, BL-201)                  #
# --------------------------------------------------------------------------- #
#
# The kernel is `_manifest.export_rows()`, each row read by `_manifest.git_show` in the
# repo `_manifest.REPO_DIRS` names — the assembler's own read, so the arm measures
# exactly what the bundle carries. Both figures come from the manifest header's
# **Kernel budget** paragraph. The ceiling is a decrease-only ratchet and the enforced
# bar; the design target is reported as a distance and never enforced.

_KERNEL_BUDGET_RE = re.compile(r"^\*\*Kernel budget\*\*.*?(?=\n[ \t]*\n|\Z)", re.MULTILINE | re.DOTALL)
_KERNEL_TARGET_RE = re.compile(r"\*\*Kernel design target:[^*\n]*\*\* \((\d[\d,]*) bytes\)")
_KERNEL_CEILING_RE = re.compile(r"\*\*Kernel ceiling: (\d[\d,]*) bytes\*\*")


def _parse_kernel_budget(text: str) -> tuple[int, int] | None:
    """(design target, ceiling) in bytes from the Kernel budget paragraph, or None."""
    para = _KERNEL_BUDGET_RE.search(text)
    if not para:
        return None
    target = _KERNEL_TARGET_RE.search(para.group(0))
    ceiling = _KERNEL_CEILING_RE.search(para.group(0))
    if not target or not ceiling:
        return None
    return int(target.group(1).replace(",", "")), int(ceiling.group(1).replace(",", ""))


def check_kernel_budget() -> None:
    check = "kernel_budget"

    if not MANIFEST_MD.exists():
        _fail(check, "docs/project-knowledge-manifest.md not found — no kernel to measure")
        return
    text = MANIFEST_MD.read_text(encoding="utf-8")

    budget = _parse_kernel_budget(text)
    if budget is None:
        _fail(check, "the manifest's **Kernel budget** paragraph carries no parseable "
                     "`**Kernel ceiling: N bytes**` and `**Kernel design target: … (N bytes)**` — "
                     "a budget arm that cannot find its cap is broken, not passing")
        return
    target, ceiling = budget

    try:
        rows = _manifest.export_rows(_manifest.parse_rows(text))
        sizes = [
            (len(_manifest.git_show(_manifest.repo_dir(row), row.repo_path)), row.export_name)
            for row in rows
        ]
    except (_manifest.ManifestError, OSError, subprocess.SubprocessError) as exc:
        _fail(check, f"cannot measure the kernel: {exc}")
        return

    total = sum(n for n, _ in sizes)
    if total > ceiling:
        largest = ", ".join(f"{name} {n:,}" for n, name in sorted(sizes, reverse=True)[:3])
        _warn(check, f"kernel {total:,} bytes over {len(sizes)} rows exceeds the ceiling "
                     f"{ceiling:,} by {total - ceiling:,}; largest: {largest}")
    else:
        distance = (f"{total - target:,} bytes above" if total > target
                    else f"{target - total:,} bytes under")
        _ok(check, f"kernel {total:,} bytes over {len(sizes)} rows ≤ ceiling {ceiling:,}; "
                   f"{distance} the {target:,}-byte design target")


CHECKS = [
    check_event_types,
    check_tauri_commands,
    check_db_schema,
    check_env_vars,
    check_routes,
    check_payload_fields,
    check_milestone_status,
    check_project_knowledge,
    check_command_fields,
    check_stream_envelope,
    check_use_case_registry,
    check_backlog_resolution,
    check_index_integrity,
    check_kernel_budget,
]

_CHECK_NAMES = {fn.__name__.replace("check_", ""): fn for fn in CHECKS}


def main() -> int:
    global _strict

    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--strict", action="store_true", help="promote WARN to FAIL")
    parser.add_argument(
        "--check",
        action="append",
        metavar="NAME",
        choices=list(_CHECK_NAMES),
        help="run only this check (repeat for multiple)",
    )
    args = parser.parse_args()
    _strict = args.strict

    selected = [_CHECK_NAMES[n] for n in args.check] if args.check else CHECKS

    print(f"Rig doc-drift checker — {len(selected)} check(s)\n")
    for fn in selected:
        fn()

    fails  = sum(1 for l, _, _ in FINDINGS if l == "FAIL")
    warns  = sum(1 for l, _, _ in FINDINGS if l == "WARN")
    passes = sum(1 for l, _, _ in FINDINGS if l == "PASS")
    infos  = sum(1 for l, _, _ in FINDINGS if l == "INFO")

    print(f"\nSummary: {passes} PASS  {fails} FAIL  {warns} WARN  {infos} INFO")
    return 1 if fails > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
