"""Every producer adopts the run record, and each adoption says what verifies it (ds t2).

One file rather than five, because the property is a **census over the producer set**: that
each of the six producers records, that no other use case pretends to, and that the six are
the six the registry plus the producer criterion yield. Split per use case, the census
clause — the one that catches a seventh producer landing unrecorded — would have no home.

**How the six are derived, since `docs/use-cases.md` alone does not yield them.** The
registry has TEN rows and carries no producer column; its membership criterion
(`D/tests/conftest.py` + `D/scripts/`) is about separately-testable code. The registry
supplies the population and this criterion supplies the subset:

    a producer writes a durable local artifact that a later reader inspects
    to establish what a run produced.

`api/gateway` and `api/tenant` write no local files at all. `drive` and `email` write only
*inbound* fetches (`drive_download.py`, `email_download_template.py` pull a remote file into
`data/`) — input-fetchers, not producers. The remaining six are the producers. Both halves
are asserted below, so the set cannot drift silently in either direction.

**What each adoption is verified by** is the second thing this file records, because the
six are not equally exercised and a uniform-looking test file would imply they were:

| use case | verified by |
|---|---|
| `docbuilder` | its own CLI subprocess tests — `docbuilder/tests/test_run_record_adoption.py` |
| `cloudcost`  | its own suite drives both instrumented stages; asserted here structurally |
| `payslip`    | its suite drives the generator loop; asserted here structurally |
| `eduloka`    | structural only — its stages need a live search provider |
| `provenance` | structural only — its report stage needs a populated DuckDB |
| `boxy-pipeline` | **dormant**; `boxy-pipeline/tests/test_run_record_adoption.py`, deselected from the gate |
"""

import ast
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from run_record import RECORD_RELPATH, run_record  # noqa: E402

#: The producer set, and the ONE script in each that this ticket instrumented. A second
#: instrumented script in a use case is fine; this names the one whose absence would mean
#: the adoption had been reverted.
PRODUCERS = {
    "boxy-pipeline": ["scripts/order_formatter.py"],
    "cloudcost": ["scripts/compose_report_data.py", "scripts/render_report.py"],
    "docbuilder": ["scripts/rename_output.py", "scripts/upload_output.py"],
    "eduloka": ["scripts/fetch.py", "scripts/map.py", "scripts/enrich.py"],
    "payslip": ["scripts/generate_employee_payslips.py"],
    "provenance": ["scripts/inventory_report.py"],
}

#: Registry rows that are NOT producers, with the reason. Asserted so the negative half of
#: the census is a claim rather than an omission.
NON_PRODUCERS = {
    "api/gateway": "writes no local file",
    "api/tenant": "writes no local file",
    "ct-bot": "no agent file yet (T0); its scripts land with T2-T4",
    "ct-rpg": "no producer scripts yet (T0+T1); the gate scripts run in the migration repo's containers",
    "drive": "fetches a remote file inbound; produces nothing of its own",
    "email": "fetches a remote file inbound; produces nothing of its own",
}


def _registry_rows():
    """The registry's own reproducing command, run here rather than quoted."""
    import subprocess

    out = subprocess.run(
        ["git", "ls-files", "*/tests/conftest.py"],
        cwd=REPO_ROOT, capture_output=True, text=True, check=True,
    ).stdout.split()
    rows = {p[: -len("/tests/conftest.py")] for p in out}
    return rows - {"tests"}


def test_the_producer_set_partitions_the_registry():
    """Producers and non-producers together are exactly the registry, with no leftovers."""
    rows = _registry_rows()
    claimed = set(PRODUCERS) | set(NON_PRODUCERS)
    assert claimed == rows, (
        f"registry moved: only-in-registry={sorted(rows - claimed)}, "
        f"only-in-this-file={sorted(claimed - rows)} — a new use case must be classified "
        f"as producer or not, and instrumented if it is"
    )
    assert not (set(PRODUCERS) & set(NON_PRODUCERS))


@pytest.mark.parametrize("use_case,scripts", sorted(PRODUCERS.items()))
def test_every_producer_script_imports_the_shared_record(use_case, scripts):
    """Parsed, not grepped: a mention inside a docstring is not an import."""
    for rel in scripts:
        path = REPO_ROOT / use_case / rel
        assert path.is_file(), path
        tree = ast.parse(path.read_text())
        imported = {
            alias.name
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom) and node.module == "run_record"
            for alias in node.names
        }
        assert "run_record" in imported, f"{use_case}/{rel} does not import run_record"


@pytest.mark.parametrize("use_case,scripts", sorted(PRODUCERS.items()))
def test_every_producer_script_actually_opens_a_record(use_case, scripts):
    """THE BROKEN STATE an import alone would pass: imported and never called."""
    for rel in scripts:
        tree = ast.parse((REPO_ROOT / use_case / rel).read_text())
        called = any(
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "run_record"
            for node in ast.walk(tree)
        )
        assert called, f"{use_case}/{rel} imports run_record but never calls it"


@pytest.mark.parametrize("use_case,scripts", sorted(PRODUCERS.items()))
def test_every_producer_script_accepts_a_run_id(use_case, scripts):
    """`--run-id` is the seam; where no run reaches the script it stays None, not invented."""
    for rel in scripts:
        source = (REPO_ROOT / use_case / rel).read_text()
        assert '"--run-id"' in source, f"{use_case}/{rel} has no --run-id flag"


@pytest.mark.parametrize("use_case,reason", sorted(NON_PRODUCERS.items()))
def test_non_producers_do_not_record(use_case, reason):
    """The negative half of the census, with a positive control on the same search."""
    scripts = sorted((REPO_ROOT / use_case / "scripts").glob("*.py"))
    if not scripts:
        # ct-bot at T0 is the first registry row whose scripts/ holds no .py at all
        # (helpers land with T2-T4). The negative search has no population, so the
        # claim is vacuously true — skipped visibly rather than failed by a guard
        # whose subject has not arrived. Any NON_PRODUCER with scripts still runs
        # the search below.
        pytest.skip(f"{use_case}: no .py scripts yet ({reason}) — nothing to search")
    hits = [p.name for p in scripts if "run_record" in p.read_text()]
    assert hits == [], f"{use_case} ({reason}) unexpectedly records: {hits}"

    # Positive control: the identical search over a producer returns non-empty, so the
    # zero above is a fact about these files rather than about the search.
    control = [
        p.name for p in (REPO_ROOT / "docbuilder" / "scripts").glob("*.py")
        if "run_record" in p.read_text()
    ]
    assert control, "positive control found nothing — the search is broken, not the result"


@pytest.mark.parametrize("use_case", sorted(PRODUCERS))
def test_every_producer_gitignores_its_record(use_case):
    """The record names artifacts and their hashes; it is ignored like the artifacts."""
    import subprocess

    for name in ("run-records.json", "run-records.json.lock"):
        rc = subprocess.run(
            ["git", "check-ignore", "-q", f"{use_case}/{RECORD_RELPATH.parent}/{name}"],
            cwd=REPO_ROOT,
        ).returncode
        assert rc == 0, f"{use_case}/data/{name} is not gitignored"


def test_the_record_relpath_is_outside_output(tmp_path):
    """Never under `output/`: payslip's `output/runs.log` dies with the tree the sprint
    `rm -rf`s (`../aetheris/scripts/sprint.sh:1006`), taking the attestation with it."""
    assert RECORD_RELPATH.parts[0] == "data"
    assert "output" not in RECORD_RELPATH.parts

    (tmp_path / "data").mkdir()
    (tmp_path / "output").mkdir()
    (tmp_path / "output" / "a.txt").write_bytes(b"x")
    with run_record(tmp_path, "r", "s") as rec:
        rec.add(tmp_path / "output" / "a.txt")

    import shutil
    shutil.rmtree(tmp_path / "output")          # what the sprint's guard does
    assert (tmp_path / RECORD_RELPATH).is_file(), "the record must survive the guard"


# ------------------------------------------------------- the seam, at every call site


def _discovered_call_sites():
    """Every `run_record(...)` call in every producer's `scripts/`, derived from the tree.

    Derived rather than listed. A hardcoded site list is the defect class this cycle already
    carries — it would pass unchanged on the day a new producer script bypasses the seam,
    which is exactly the failure this arm exists to catch. Walking the tree means a site that
    did not exist when this test was written is still covered.

    Returns `[(relpath, lineno, root_expr)]`, where `root_expr` is a short description of the
    first positional argument: `"use_case_root_for(__file__)"` when it is that call, else the
    source text of whatever was passed.
    """
    sites = []
    for use_case in sorted(PRODUCERS):
        for path in sorted((REPO_ROOT / use_case / "scripts").glob("*.py")):
            source = path.read_text()
            tree = ast.parse(source)
            for node in ast.walk(tree):
                if not (isinstance(node, ast.Call)
                        and isinstance(node.func, ast.Name)
                        and node.func.id == "run_record"):
                    continue
                if not node.args:
                    expr = "<no positional argument>"
                else:
                    arg = node.args[0]
                    if (isinstance(arg, ast.Call)
                            and isinstance(arg.func, ast.Name)
                            and arg.func.id == "use_case_root_for"
                            and len(arg.args) == 1
                            and isinstance(arg.args[0], ast.Name)
                            and arg.args[0].id == "__file__"):
                        expr = "use_case_root_for(__file__)"
                    else:
                        expr = ast.get_source_segment(source, arg) or "<unparsed>"
                sites.append((str(path.relative_to(REPO_ROOT)), node.lineno, expr))
    return sites


def test_every_call_site_obtains_its_root_through_the_seam():
    """THE BROKEN STATE: a call site passing its own root constant instead of the seam.

    `AETHERIS_RUN_RECORD_ROOT` is read in exactly one place — `run_record.use_case_root_for`
    — so a site that passes any other expression is invisible to it. The consequence is not
    a wrong record but a **silent** one: each use case's autouse `_isolate_run_records`
    fixture goes inert for that site, its tests write into the checked-out tree, and because
    the record file is gitignored `git status` cannot see it. A guard returning a clean
    result while guarding nothing.

    Found in ds t2 stage 3: eduloka's `fetch.py`, `map.py` and `enrich.py` all passed
    `_USE_CASE_ROOT`, and every test in this file passed anyway — because they asserted that
    `run_record` is CALLED and never how its root is obtained. Fixed at stage 4.
    """
    bypassing = [(f, ln, expr) for f, ln, expr in _discovered_call_sites()
                 if expr != "use_case_root_for(__file__)"]
    assert bypassing == [], (
        "these call sites bypass the AETHERIS_RUN_RECORD_ROOT seam, so their use case's "
        "isolation fixture is inert for them:\n"
        + "\n".join(f"  {f}:{ln} passes {expr}" for f, ln, expr in bypassing)
    )


def test_the_discovered_call_sites_cover_every_declared_producer_script():
    """The derived set is checked against the census the other tests derive.

    Discovery walking the tree could silently find nothing — a wrong glob, a renamed
    directory — and `test_every_call_site_obtains_its_root_through_the_seam` would then pass
    vacuously over an empty list. This is that test's positive control, and it is a real
    assertion rather than a smoke check: every script `PRODUCERS` declares must appear among
    the discovered sites, and `PRODUCERS` is itself checked against the registry by
    `test_the_producer_set_partitions_the_registry`.
    """
    sites = _discovered_call_sites()
    assert sites, "discovery found no call sites at all — the walk is broken, not the tree"

    files_with_sites = {f for f, _ln, _expr in sites}
    declared = {f"{uc}/{rel}" for uc, rels in PRODUCERS.items() for rel in rels}
    assert declared <= files_with_sites, (
        f"declared instrumented scripts with no discovered run_record call: "
        f"{sorted(declared - files_with_sites)}"
    )
    # Every declared script contributes at least one site, so the count is at least the
    # census size. Stated as an inequality, not an equality: a script legitimately carries
    # more than one call site (payslip's loop would, if it were ever split per month).
    assert len(sites) >= len(declared)
