"""Tests for scripts/assemble_matrix.py (BL-067).

Every derived value in docs/capability-matrix.md must be *counted*, never asserted.
So each test here re-parses the emitted document with its own independent parser and
asserts claimed == counted: the Summary counts and totals against the emitted
Agents/Scripts table rows, the unique-tools line against the emitted Tools cells,
and both Overlap Report tables against overlaps recomputed from the same rows.

Fixtures deliberately contain real overlaps — a shared script name and two agents
whose tool sets match in different cell orders — so the overlap assertions cannot
pass vacuously the way a "No overlaps found" document always would.
"""

import json
import re

import pytest

import assemble_matrix
from assemble_matrix import SECTIONS, parse_tools
from assemble_matrix import assemble as _assemble


def assemble(sections_dir, output, overrides=None):
    """Assemble with no curated overrides unless a test supplies its own.

    The real overrides file (docs/capability-matrix-overrides.json) is keyed to the
    real sections, so it must not leak into fixture runs — every one of its keys
    would be unmatched.
    """
    if overrides is None:
        overrides = sections_dir.parent / "no-overrides.json"
        overrides.write_text("{}", encoding="utf-8")
    return _assemble(sections_dir, output, overrides)


def _overrides_file(tmp_path, payload, name="overrides.json"):
    path = tmp_path / name
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path

# --------------------------------------------------------------------------- #
# Fixture builders                                                             #
# --------------------------------------------------------------------------- #


def _section_md(title, agents, scripts):
    """Render a section file the way the section agents write them."""
    lines = [f"## {title}", "", "### Agents", "", "| Agent file | Label | Tools |", "|------------|-------|-------|"]
    lines += [f"| {file} | {label} | {tools} |" for file, label, tools in agents]
    lines += ["", "### Scripts", "", "| Script | Purpose |", "|--------|---------|"]
    lines += [f"| {name} | {purpose} |" for name, purpose in scripts]
    return "\n".join(lines) + "\n"


def _write_sections(directory, overrides=None, omit=()):
    """Write one file per SECTIONS key; `overrides` replaces the default content.

    Default sections are titled with their Summary label, so a heading maps back
    to a label without guesswork; overridden sections register their real-world
    heading in TITLE_TO_LABEL.
    """
    directory.mkdir(parents=True, exist_ok=True)
    overrides = overrides or {}

    for key, label in SECTIONS:
        if key in omit:
            continue
        content = overrides.get(key)
        if content is None:
            content = _section_md(
                label,
                [(f"{key}_orchestrator.exs", f"{label} Orchestrator", "`run_command`")],
                [(f"{key}_only.py", f"Only script of {label}.")],
            )
        (directory / f"{key}.md").write_text(content, encoding="utf-8")

    return directory


# A fixture set with genuine overlaps:
#   shared.py appears in payslip and drive                     -> script-name overlap
#   api agents share tool sets in *different* cell orders      -> tool-set overlaps
#   api_tenant has two rows from one agent file                -> label disambiguation
#   provenance's search agent has a backtick-free prose cell   -> prose capability
OVERLAPPING = {
    "payslip": _section_md(
        "Payslip",
        [
            ("payslip_orchestrator.exs", "Payslip Orchestrator", "`run_command`"),
            ("payslip_pipeline.exs", "Payslip Pipeline", "`run_command`"),
        ],
        [("shared.py", "Shared by two use cases."), ("payslip_compute.py", "Compute a payslip.")],
    ),
    "drive": _section_md(
        "Drive",
        [("drive_orchestrator.exs", "Drive Orchestrator", "`run_command`, `read_file`")],
        [("shared.py", "Shared by two use cases."), ("drive_upload.py", "Upload to Drive.")],
    ),
    "api_tenant": _section_md(
        "api/tenant — TAP Protocol — Tenant side",
        [
            ("at1cmd.exs", "at1cmd — Dispatcher", "`send_message`, `write_blackboard`"),
            ("at1cmd.exs", "cot1 — Gateway", "`read_blackboard`, `run_command`"),
        ],
        [("parse_csv.py", "Parse a CSV.")],
    ),
    "api_gateway": _section_md(
        "api/ — TAP Protocol — Gateway side",
        [
            ("cot1.exs", "cot1 — Gateway", "`write_blackboard`, `send_message`"),
            ("cot1_stub.exs", "cot1_stub — Gateway Stub", "`run_command`, `read_blackboard`"),
        ],
        [("validate_intent.py", "Validate an intent.")],
    ),
    "provenance": _section_md(
        "Provenance — Corpus Management",
        [("search_agent.exs", "Provenance Search Agent", "MCP servers (corpus_search, lattice)")],
        [("init_db.py", "Initialise the DuckDB schema.")],
    ),
}

# Emitted heading -> Summary label, for the sections whose heading is not the label.
TITLE_TO_LABEL = {
    "Payslip": "payslip",
    "Drive": "drive",
    "Docbuilder": "docbuilder",
    "api/tenant — TAP Protocol — Tenant side": "api/tenant",
    "api/ — TAP Protocol — Gateway side": "api/gateway",
    "Provenance — Corpus Management": "provenance",
}


@pytest.fixture
def overlapping_matrix(tmp_path):
    """Assemble the overlap-bearing fixture set; returns (document, exit code)."""
    sections_dir = _write_sections(tmp_path / "sections", OVERLAPPING)
    output = tmp_path / "capability-matrix.md"
    code = assemble(sections_dir, output)
    return output.read_text(encoding="utf-8"), code


# --------------------------------------------------------------------------- #
# Independent parser — deliberately not the script's own                       #
# --------------------------------------------------------------------------- #

ROW = re.compile(r"^\|(?!\s*[-:| ]+\|?\s*$)(.+)\|\s*$")


def _cells(line):
    return [c.strip() for c in ROW.match(line).group(1).split("|")]


def _emitted_tables(document):
    """{section title: {"agents": [tool cells], "scripts": [names]}} from the document."""
    tables, title, table = {}, None, None

    for line in document.splitlines():
        if line.startswith("## "):
            title = line[3:].strip()
            tables[title] = {"agents": [], "scripts": []}
            table = None
        elif line.strip() == "### Agents":
            table = "agents"
        elif line.strip() == "### Scripts":
            table = "scripts"
        elif line.startswith("### "):
            table = None
        elif table and title and ROW.match(line):
            cells = _cells(line)
            if cells[0] in ("Agent file", "Script"):
                continue
            tables[title][table].append(cells[2] if table == "agents" else cells[0])

    return tables


def _use_case_tables(document):
    """The section tables only — Overlap Report and Summary are not use cases."""
    return {
        title: table
        for title, table in _emitted_tables(document).items()
        if title not in ("Overlap Report", "Summary")
    }


def _summary_rows(document):
    """{use case label: (agents, scripts)} claimed by the Summary table."""
    rows, in_summary = {}, False

    for line in document.splitlines():
        if line.startswith("## "):
            in_summary = line.strip() == "## Summary"
        elif in_summary and ROW.match(line):
            label, agents, scripts = _cells(line)[:3]
            if label == "Use case":
                continue
            rows[label.strip("*")] = (int(agents.strip("*")), int(scripts.strip("*")))

    return rows


def _claimed_tools(document):
    line = [l for l in document.splitlines() if l.startswith("**Unique tools across all use cases:**")]
    assert len(line) == 1, "exactly one unique-tools line expected"
    return re.findall(r"`([^`]+)`", line[0])


def _overlap_table(document, heading):
    """Data rows of one Overlap Report table, as (first cell, second cell) pairs."""
    rows, inside = [], False

    for line in document.splitlines():
        if line.startswith("### "):
            inside = line.strip() == heading
        elif line.startswith("## "):
            inside = False
        elif inside and ROW.match(line):
            cells = _cells(line)
            if cells[0] in ("Script", "Tools"):
                continue
            rows.append((cells[0], cells[1]))

    return rows


def _label_for(title):
    """Map an emitted section heading back to its Summary label."""
    label = TITLE_TO_LABEL.get(title, title)
    assert label in [l for _, l in SECTIONS], f"no SECTIONS label for {title!r}"
    return label


# --------------------------------------------------------------------------- #
# Summary counts — claimed == counted                                          #
# --------------------------------------------------------------------------- #


def test_per_section_agent_counts_match_emitted_rows(overlapping_matrix):
    document, _ = overlapping_matrix
    claimed = _summary_rows(document)

    for title, table in _use_case_tables(document).items():
        assert claimed[_label_for(title)][0] == len(table["agents"]), title


def test_per_section_script_counts_match_emitted_rows(overlapping_matrix):
    document, _ = overlapping_matrix
    claimed = _summary_rows(document)

    for title, table in _use_case_tables(document).items():
        assert claimed[_label_for(title)][1] == len(table["scripts"]), title


def test_totals_match_sum_of_emitted_rows(overlapping_matrix):
    document, _ = overlapping_matrix
    tables = _use_case_tables(document)
    claimed = _summary_rows(document)

    assert claimed["Total"][0] == sum(len(t["agents"]) for t in tables.values())
    assert claimed["Total"][1] == sum(len(t["scripts"]) for t in tables.values())


def test_totals_equal_sum_of_claimed_per_section_rows(overlapping_matrix):
    document, _ = overlapping_matrix
    claimed = _summary_rows(document)
    per_section = [counts for label, counts in claimed.items() if label != "Total"]

    assert claimed["Total"] == (
        sum(agents for agents, _ in per_section),
        sum(scripts for _, scripts in per_section),
    )


def test_counts_follow_the_sections(tmp_path):
    """Perturbing a section moves the counts — the check is not stuck on a constant."""
    base = _write_sections(tmp_path / "before")
    before = tmp_path / "before.md"
    assemble(base, before)

    grown = _write_sections(
        tmp_path / "after",
        {
            "payslip": _section_md(
                "Payslip",
                [("a.exs", "A", "`run_command`"), ("b.exs", "B", "`read_file`")],
                [("one.py", "One."), ("two.py", "Two.")],
            )
        },
    )
    after = tmp_path / "after.md"
    assemble(grown, after)

    claimed_before = _summary_rows(before.read_text(encoding="utf-8"))
    claimed_after = _summary_rows(after.read_text(encoding="utf-8"))

    assert claimed_before["payslip"] == (1, 1)
    assert claimed_after["payslip"] == (2, 2)
    assert claimed_after["Total"][0] == claimed_before["Total"][0] + 1
    assert claimed_after["Total"][1] == claimed_before["Total"][1] + 1


# --------------------------------------------------------------------------- #
# Unique tools line                                                            #
# --------------------------------------------------------------------------- #


def test_unique_tools_line_matches_union_of_emitted_tool_cells(overlapping_matrix):
    document, _ = overlapping_matrix

    counted = []
    for table in _use_case_tables(document).values():
        for cell in table["agents"]:
            for tool in parse_tools(cell):
                if tool not in counted:
                    counted.append(tool)

    assert _claimed_tools(document) == counted


def test_unique_tools_line_includes_prose_capability(overlapping_matrix):
    document, _ = overlapping_matrix

    assert "MCP servers (corpus_search, lattice)" in _claimed_tools(document)


def test_parse_tools_reads_backticks_and_prose():
    assert parse_tools("`read_file`, `run_command`") == ["read_file", "run_command"]
    assert parse_tools("MCP servers (corpus_search, lattice)") == ["MCP servers (corpus_search, lattice)"]
    assert parse_tools("   ") == []


def test_unique_tools_line_follows_the_sections(tmp_path):
    """A tool added to a section appears in the line — the union is recomputed."""
    sections = _write_sections(tmp_path / "sections")
    output = tmp_path / "matrix.md"
    assemble(sections, output)
    assert "spawn_agent" not in _claimed_tools(output.read_text(encoding="utf-8"))

    (sections / "drive.md").write_text(
        _section_md("Drive", [("d.exs", "D", "`run_command`, `spawn_agent`")], [("d.py", "D.")]),
        encoding="utf-8",
    )
    assemble(sections, output)
    assert "spawn_agent" in _claimed_tools(output.read_text(encoding="utf-8"))


# --------------------------------------------------------------------------- #
# Overlap Report — identical tool sets                                         #
# --------------------------------------------------------------------------- #


def test_identical_tool_sets_match_recomputed(overlapping_matrix):
    document, _ = overlapping_matrix

    counted = {}
    for table in _use_case_tables(document).values():
        for cell in table["agents"]:
            tools = frozenset(parse_tools(cell))
            counted[tools] = counted.get(tools, 0) + 1
    expected = {tools for tools, count in counted.items() if count > 1}

    claimed = {frozenset(re.findall(r"`([^`]+)`", tools)) for tools, _ in _overlap_table(document, "### Identical tool sets")}

    assert claimed == expected


def test_identical_tool_sets_list_every_sharing_agent(overlapping_matrix):
    document, _ = overlapping_matrix

    rows = _overlap_table(document, "### Identical tool sets")
    by_tools = {frozenset(re.findall(r"`([^`]+)`", tools)): agents for tools, agents in rows}

    run_command = by_tools[frozenset({"run_command"})].split(", ")
    assert run_command == [
        "payslip_orchestrator (payslip)",
        "payslip_pipeline (payslip)",
        "email_orchestrator (email)",
        "docbuilder_orchestrator (docbuilder)",
        "cloudcost_orchestrator (cloudcost)",
        "ct-bot_orchestrator (ct-bot)",
        "eduloka_orchestrator (eduloka)",
    ]


def test_identical_tool_sets_ignore_cell_order(overlapping_matrix):
    """`send_message, write_blackboard` and `write_blackboard, send_message` are one set."""
    document, _ = overlapping_matrix

    rows = _overlap_table(document, "### Identical tool sets")
    by_tools = {frozenset(re.findall(r"`([^`]+)`", tools)): agents for tools, agents in rows}
    agents = by_tools[frozenset({"send_message", "write_blackboard"})]

    assert agents == "at1cmd:at1cmd — Dispatcher (api/tenant), cot1 (api/gateway)"


def test_duplicate_agent_file_rows_are_disambiguated_by_label(overlapping_matrix):
    """Both api_tenant rows come from at1cmd.exs; the label separates them."""
    document, _ = overlapping_matrix

    agents = "".join(agents for _, agents in _overlap_table(document, "### Identical tool sets"))
    assert "at1cmd:at1cmd — Dispatcher (api/tenant)" in agents
    assert "at1cmd:cot1 — Gateway (api/tenant)" in agents


def test_no_identical_tool_sets_when_every_agent_differs(tmp_path):
    distinct = {
        key: _section_md(
            label.title(), [(f"{key}.exs", label, f"`tool_{index}`")], [(f"{key}.py", "One.")]
        )
        for index, (key, label) in enumerate(SECTIONS)
    }
    output = tmp_path / "matrix.md"
    assemble(_write_sections(tmp_path / "sections", distinct), output)
    document = output.read_text(encoding="utf-8")

    assert "No identical tool sets found." in document
    assert _overlap_table(document, "### Identical tool sets") == []


# --------------------------------------------------------------------------- #
# Overlap Report — script names                                                #
# --------------------------------------------------------------------------- #


def test_script_overlaps_match_recomputed(overlapping_matrix):
    document, _ = overlapping_matrix

    seen = {}
    for title, table in _use_case_tables(document).items():
        for name in table["scripts"]:
            seen.setdefault(name, []).append(_label_for(title))
    expected = {name: use_cases for name, use_cases in seen.items() if len(use_cases) > 1}

    claimed = {
        name: use_cases.split(", ") for name, use_cases in _overlap_table(document, "### Script name overlaps")
    }

    assert claimed == expected
    assert claimed == {"shared.py": ["payslip", "drive"]}


def test_no_script_overlaps_when_every_name_is_unique(tmp_path):
    output = tmp_path / "matrix.md"
    assemble(_write_sections(tmp_path / "sections"), output)
    document = output.read_text(encoding="utf-8")

    assert "No script name overlaps found." in document
    assert _overlap_table(document, "### Script name overlaps") == []


# --------------------------------------------------------------------------- #
# Document-level properties                                                    #
# --------------------------------------------------------------------------- #


def test_two_runs_over_unchanged_sections_are_byte_identical(tmp_path):
    sections = _write_sections(tmp_path / "sections", OVERLAPPING)
    first, second = tmp_path / "first.md", tmp_path / "second.md"

    assert assemble(sections, first) == 0
    assert assemble(sections, second) == 0

    assert first.read_bytes() == second.read_bytes()


def test_section_content_is_pasted_verbatim(tmp_path):
    curated = _section_md(
        "Docbuilder",
        [("context_builder.exs", "Docbuilder Context Builder", "`read_file`, `write_file`")],
        [("generate_pdf.py", "Render to PDF — narrative mode. Jinja2 path added in m6 (`has_jinja: true`).")],
    )
    output = tmp_path / "matrix.md"
    assemble(_write_sections(tmp_path / "sections", {"docbuilder": curated}), output)

    assert curated.rstrip() in output.read_text(encoding="utf-8")


def test_sections_are_emitted_in_the_constant_order(tmp_path):
    output = tmp_path / "matrix.md"
    assemble(_write_sections(tmp_path / "sections"), output)
    document = output.read_text(encoding="utf-8")

    headings = [line for line in document.splitlines() if line.startswith("## ")]
    order = [h for h in headings if h not in ("## Overlap Report", "## Summary")]

    assert order == [f"## {label}" for _, label in SECTIONS]


def test_header_names_the_script_not_the_retired_agent(tmp_path):
    output = tmp_path / "matrix.md"
    assemble(_write_sections(tmp_path / "sections"), output)
    document = output.read_text(encoding="utf-8")

    assert "`scripts/assemble_matrix.py`" in document
    assert "capability_matrix_assemble.exs" not in document
    assert document.splitlines()[2].startswith("_Generated")


# --------------------------------------------------------------------------- #
# Degradation                                                                  #
# --------------------------------------------------------------------------- #


def test_missing_section_degrades_to_partial(tmp_path, capsys):
    sections = _write_sections(tmp_path / "sections", omit=("cloudcost",))
    output = tmp_path / "matrix.md"

    code = assemble(sections, output)
    document = output.read_text(encoding="utf-8")

    assert code == 1
    assert "## cloudcost\n\n_Section not available._" in document
    assert _summary_rows(document)["cloudcost"] == (0, 0)
    assert "cloudcost.md" in capsys.readouterr().err


def test_unknown_section_file_is_reported_not_silently_dropped(tmp_path, capsys):
    sections = _write_sections(tmp_path / "sections")
    (sections / "nosuchuc.md").write_text(_section_md("Nosuchuc", [], []), encoding="utf-8")
    output = tmp_path / "matrix.md"

    code = assemble(sections, output)
    stderr = capsys.readouterr().err

    assert code == 0
    assert "nosuchuc.md" in stderr
    assert "not in SECTIONS" in stderr
    assert "Nosuchuc" not in output.read_text(encoding="utf-8")


def test_section_without_tables_warns_and_counts_zero(tmp_path, capsys):
    sections = _write_sections(tmp_path / "sections", {"email": "## Email\n\nNo tables here.\n"})
    output = tmp_path / "matrix.md"

    code = assemble(sections, output)
    stderr = capsys.readouterr().err

    assert code == 0
    assert "no rows found under '### Agents'" in stderr
    assert _summary_rows(output.read_text(encoding="utf-8"))["email"] == (0, 0)


# --------------------------------------------------------------------------- #
# Curated overrides (BL-068)                                                    #
# --------------------------------------------------------------------------- #


def test_override_replaces_the_generated_cell(tmp_path):
    sections = _write_sections(
        tmp_path / "sections",
        {
            "docbuilder": _section_md(
                "docbuilder",
                [("docbuilder_orchestrator.exs", "Docbuilder Orchestrator", "`run_command`")],
                [("generate_pdf.py", "Render document spec to PDF.")],
            )
        },
    )
    curated = "Render document spec to PDF. Jinja2 path added in m6 (`has_jinja: true`)."
    overrides = _overrides_file(tmp_path, {"docbuilder": {"scripts": {"generate_pdf.py": {"purpose": curated}}}})
    output = tmp_path / "matrix.md"

    assert assemble(sections, output, overrides) == 0
    document = output.read_text(encoding="utf-8")

    assert f"| generate_pdf.py | {curated} |" in document
    assert "| generate_pdf.py | Render document spec to PDF. |" not in document


def test_rows_without_an_override_are_untouched(tmp_path):
    generated = _section_md(
        "docbuilder",
        [("docbuilder_orchestrator.exs", "Docbuilder Orchestrator", "`run_command`")],
        [("generate_pdf.py", "Curated later."), ("fetch_data.py", "Fetch and parse data sources.")],
    )
    sections = _write_sections(tmp_path / "sections", {"docbuilder": generated})
    overrides = _overrides_file(tmp_path, {"docbuilder": {"scripts": {"generate_pdf.py": {"purpose": "Curated."}}}})
    output = tmp_path / "matrix.md"

    assert assemble(sections, output, overrides) == 0
    document = output.read_text(encoding="utf-8")

    assert "| fetch_data.py | Fetch and parse data sources. |" in document
    assert "| docbuilder_orchestrator.exs | Docbuilder Orchestrator | `run_command` |" in document


def test_tools_override_flows_into_unique_tools_and_overlaps(tmp_path):
    """The provenance MCP cell: the §1e leak BL-068 was filed for."""
    generated = _section_md(
        "provenance",
        [
            ("search_agent.exs", "Provenance Search Agent", "(MCP: corpus_search, lattice)"),
            ("scan_orchestrator.exs", "Provenance Scan Orchestrator", "`run_command`"),
        ],
        [("init_db.py", "Initialise the schema.")],
    )
    curated = "MCP servers (corpus_search, lattice)"
    sections = _write_sections(tmp_path / "sections", {"provenance": generated})
    overrides = _overrides_file(
        tmp_path, {"provenance": {"agents": {"search_agent.exs": {"tools": curated}}}}
    )
    output = tmp_path / "matrix.md"

    assert assemble(sections, output, overrides) == 0
    document = output.read_text(encoding="utf-8")

    assert curated in _claimed_tools(document)
    assert "(MCP: corpus_search, lattice)" not in document
    # and the derived block still agrees with the emitted tables
    counted = []
    for table in _use_case_tables(document).values():
        for cell in table["agents"]:
            for tool in parse_tools(cell):
                if tool not in counted:
                    counted.append(tool)
    assert _claimed_tools(document) == counted


def test_override_changes_tool_set_grouping(tmp_path):
    """A curated tools cell is counted, not decorative: it moves an overlap group."""
    sections = _write_sections(
        tmp_path / "sections",
        {
            "payslip": _section_md(
                "payslip",
                [("payslip_orchestrator.exs", "Payslip Orchestrator", "`read_file`")],
                [("payslip_compute.py", "Compute.")],
            )
        },
    )
    output = tmp_path / "matrix.md"

    assemble(sections, output)
    before = _overlap_table(output.read_text(encoding="utf-8"), "### Identical tool sets")
    assert not any("payslip_orchestrator (payslip)" in agents for _, agents in before)

    overrides = _overrides_file(
        tmp_path, {"payslip": {"agents": {"payslip_orchestrator.exs": {"tools": "`run_command`"}}}}
    )
    assemble(sections, output, overrides)
    rows = _overlap_table(output.read_text(encoding="utf-8"), "### Identical tool sets")

    assert rows and "payslip_orchestrator (payslip)" in rows[0][1]


def test_override_key_disambiguates_multi_row_agent_files(tmp_path):
    generated = _section_md(
        "api_tenant",
        [
            ("at1cmd.exs", "at1cmd — Dispatcher", "`send_message`"),
            ("at1cmd.exs", "cot1 — Gateway", "`read_blackboard`"),
        ],
        [("parse_csv.py", "Parse.")],
    )
    sections = _write_sections(tmp_path / "sections", {"api_tenant": generated})
    overrides = _overrides_file(
        tmp_path,
        {"api_tenant": {"agents": {"at1cmd.exs::cot1 — Gateway": {"tools": "`read_blackboard`, `wait_for_event`"}}}},
    )
    output = tmp_path / "matrix.md"

    assert assemble(sections, output, overrides) == 0
    document = output.read_text(encoding="utf-8")

    assert "| at1cmd.exs | at1cmd — Dispatcher | `send_message` |" in document
    assert "| at1cmd.exs | cot1 — Gateway | `read_blackboard`, `wait_for_event` |" in document


def test_bare_file_key_applies_to_every_row_of_that_file(tmp_path):
    """Documented semantics: a bare key is file-wide; `file::label` targets one row.

    Pinned so the runbook's rule ("always use file::label for a multi-row file") stays
    true of the code — if this ever becomes per-row, it should be a deliberate change.
    """
    generated = _section_md(
        "api_tenant",
        [
            ("at1cmd.exs", "at1cmd — Dispatcher", "`send_message`"),
            ("at1cmd.exs", "cot1 — Gateway", "`read_blackboard`"),
        ],
        [("parse_csv.py", "Parse.")],
    )
    sections = _write_sections(tmp_path / "sections", {"api_tenant": generated})
    overrides = _overrides_file(
        tmp_path, {"api_tenant": {"agents": {"at1cmd.exs": {"tools": "`run_command`"}}}}
    )
    output = tmp_path / "matrix.md"

    assert assemble(sections, output, overrides) == 0
    document = output.read_text(encoding="utf-8")

    assert "| at1cmd.exs | at1cmd — Dispatcher | `run_command` |" in document
    assert "| at1cmd.exs | cot1 — Gateway | `run_command` |" in document


def test_override_matching_no_row_fails_the_run(tmp_path, capsys):
    """A renamed script must not silently drop its curation — that is BL-068 itself."""
    sections = _write_sections(tmp_path / "sections")
    overrides = _overrides_file(
        tmp_path, {"docbuilder": {"scripts": {"renamed_away.py": {"purpose": "Curated."}}}}
    )
    output = tmp_path / "matrix.md"

    code = assemble(sections, output, overrides)
    stderr = capsys.readouterr().err

    assert code == 1
    assert "docbuilder.renamed_away.py" in stderr
    assert "matched no row" in stderr


def test_overrides_for_a_missing_section_are_not_reported_as_stale(tmp_path, capsys):
    sections = _write_sections(tmp_path / "sections", omit=("docbuilder",))
    overrides = _overrides_file(
        tmp_path, {"docbuilder": {"scripts": {"generate_pdf.py": {"purpose": "Curated."}}}}
    )
    output = tmp_path / "matrix.md"

    code = assemble(sections, output, overrides)
    stderr = capsys.readouterr().err

    assert code == 1  # partial matrix, the missing section
    assert "matched no row" not in stderr


def test_unreadable_overrides_file_fails_rather_than_dropping_all_curation(tmp_path, capsys):
    sections = _write_sections(tmp_path / "sections")
    broken = tmp_path / "broken.json"
    broken.write_text("{not json", encoding="utf-8")
    output = tmp_path / "matrix.md"

    code = assemble(sections, output, broken)
    stderr = capsys.readouterr().err

    assert code == 1
    assert "not valid JSON" in stderr


def test_absent_overrides_file_warns_and_assembles(tmp_path, capsys):
    sections = _write_sections(tmp_path / "sections")
    output = tmp_path / "matrix.md"

    code = assemble(sections, output, tmp_path / "nope.json")
    stderr = capsys.readouterr().err

    assert code == 0
    assert "overrides file missing" in stderr


def test_override_section_outside_sections_is_reported(tmp_path, capsys):
    sections = _write_sections(tmp_path / "sections")
    overrides = _overrides_file(tmp_path, {"nosuchuc": {"scripts": {"x.py": {"purpose": "y"}}}})
    output = tmp_path / "matrix.md"

    code = assemble(sections, output, overrides)
    stderr = capsys.readouterr().err

    assert code == 0
    assert "override section not in SECTIONS, ignored: nosuchuc" in stderr


def test_comment_keys_are_not_reported_as_unknown_sections(tmp_path, capsys):
    sections = _write_sections(tmp_path / "sections")
    overrides = _overrides_file(tmp_path, {"_comment": ["docs for humans"]})
    output = tmp_path / "matrix.md"

    assert assemble(sections, output, overrides) == 0
    assert "not in SECTIONS" not in capsys.readouterr().err


def test_counts_still_claimed_equals_counted_with_overrides(tmp_path):
    """Overrides apply before counting, so the BL-067 invariant is untouched."""
    sections = _write_sections(tmp_path / "sections", OVERLAPPING)
    overrides = _overrides_file(
        tmp_path,
        {
            "provenance": {"agents": {"search_agent.exs": {"tools": "MCP servers (corpus_search, lattice)"}}},
            "payslip": {"scripts": {"shared.py": {"purpose": "Curated purpose."}}},
        },
    )
    output = tmp_path / "matrix.md"
    assemble(sections, output, overrides)
    document = output.read_text(encoding="utf-8")

    claimed = _summary_rows(document)
    tables = _use_case_tables(document)
    for title, table in tables.items():
        assert claimed[_label_for(title)] == (len(table["agents"]), len(table["scripts"])), title
    assert claimed["Total"] == (
        sum(len(t["agents"]) for t in tables.values()),
        sum(len(t["scripts"]) for t in tables.values()),
    )


def test_overrides_are_byte_stable(tmp_path):
    sections = _write_sections(tmp_path / "sections", OVERLAPPING)
    overrides = _overrides_file(
        tmp_path, {"payslip": {"scripts": {"shared.py": {"purpose": "Curated purpose."}}}}
    )
    first, second = tmp_path / "first.md", tmp_path / "second.md"

    assemble(sections, first, overrides)
    assemble(sections, second, overrides)

    assert first.read_bytes() == second.read_bytes()


def test_repo_overrides_file_is_wellformed():
    """The committed overrides file parses and uses only known section keys/fields."""
    import pathlib

    payload = json.loads(
        (pathlib.Path(__file__).parent.parent / "docs" / "capability-matrix-overrides.json").read_text()
    )
    keys = {key for key, _ in SECTIONS}

    for section, entry in payload.items():
        if section.startswith("_"):
            continue
        assert section in keys, section
        assert set(entry) <= {"agents", "scripts"}, section
        for fields in entry.get("agents", {}).values():
            assert set(fields) <= {"label", "tools"}
        for fields in entry.get("scripts", {}).values():
            assert set(fields) <= {"purpose"}


def test_warnings_do_not_leak_between_runs(tmp_path):
    output = tmp_path / "matrix.md"

    assemble(_write_sections(tmp_path / "partial", omit=("drive",)), output)
    assert assemble(_write_sections(tmp_path / "complete"), output) == 0
    assert assemble_matrix.WARNINGS == []
