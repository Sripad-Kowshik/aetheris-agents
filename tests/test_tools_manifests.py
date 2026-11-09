"""Offline conformance checks for the per-use-case `tools.json` manifests (BL-084).

Rig's Tools module is the only consumer. It walks `<AETHERIS_AGENTS_PATH>/<use_case>/
tools.json` and deserializes it into the serde structs at
`rig/src-tauri/src/commands/tools.rs:4-46`. Two properties of that walk are what make an
offline suite worth having:

  * `serde_json::from_str(&raw).ok()` (`tools.rs:526`) — a manifest that violates the schema
    is not an error, it is a `None`. The use case silently falls back to all-undeclared and
    every script wears the amber badge, with nothing anywhere saying why. A malformed
    manifest and an absent one are indistinguishable in the UI.
  * every `scripts/*.py` on disk with no matching `file` entry is synthesised as
    `undeclared: true` (`tools.rs:560-575`) and badged amber (`ToolTree.tsx:71-73`).

So `test_manifest_parses` guards the silent-drop, and `test_no_undeclared_scripts` is the
offline proxy for the amber badge.

**What this suite does not prove.** The schema below is a *transcription* of the serde
structs; it does not run serde. A manifest that passes here and still fails
`serde_json::from_str` would be dropped silently by `tools.rs:526` and this suite would not
see it. The only true proof is a running Rig.

**Proxy boundary.** Rig badges *any* undeclared flat `.py`, including import-only modules.
`test_no_undeclared_scripts` flags only undeclared *runnable CLIs*, which is the adjudicated
predicate for BL-084. `drive/scripts/__init__.py`, `drive/scripts/drive_utils.py`,
`email/scripts/__init__.py` and `payslip/scripts/__init__.py` are undeclared and do wear
amber today; this suite does not flag them. For cloudcost the two coincide, because
`_normalized.py` is declared.
"""

import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent

# Mirrors the walker's own exclusions at `tools.rs:514-518`.
SKIP_DIRS = {"rig", "docs", "agents"}

# `ManifestScript.output` — `tools.rs:41`, and `ToolDetail.tsx:40`.
VALID_OUTPUTS = {"json", "text", "files"}

# `ManifestArg.arg_type` — the values `docs/rig/milestones/p4-tools/p4-001-manifest-spec.md`
# defines. Rust types it as a bare String, so this set is the only thing enforcing it.
VALID_ARG_TYPES = {"string", "file", "directory", "integer", "float", "boolean"}

REQUIRED_TOP_LEVEL = {"manifest_version", "use_case", "description", "scripts"}

# `undeclared` and `env` are the only `#[serde(default)]` fields on ManifestScript.
REQUIRED_SCRIPT_FIELDS = {"name", "file", "description", "args", "output", "example"}

# ManifestArg: `flag` is Option<String>; positionals omit it entirely. Everything else is
# mandatory — `default` is `Option<String>` but the key must be present.
REQUIRED_ARG_FIELDS = {"name", "type", "required", "default", "description"}

# EnvDep carries no #[serde(default)] on any field (`tools.rs:6-13`): all five are mandatory,
# and one missing key drops the whole manifest.
REQUIRED_ENV_FIELDS = {"key", "label", "group", "masked", "placeholder"}


def _is_runnable_cli(path: Path) -> bool:
    """A script Rig can meaningfully Run — i.e. one with an entry point.

    Import-only shared modules (`_normalized.py`, `_drive.py`, `__init__.py`) have none.
    """
    return 'if __name__ == "__main__":' in path.read_text(encoding="utf-8", errors="replace")


def _flat_cli_scripts(use_case: str) -> list[str]:
    """Runnable CLIs in `<use_case>/scripts/*.py`, as manifest-relative paths.

    Flat and `.py`-only, because that is exactly what the walker synthesises undeclared
    entries from (`tools.rs:551-575`). Nested layouts such as `api/tenant/scripts/` are
    invisible to the walker and so are out of scope here too.
    """
    scripts_dir = REPO_ROOT / use_case / "scripts"
    if not scripts_dir.is_dir():
        return []
    return sorted(
        f"scripts/{p.name}" for p in scripts_dir.glob("*.py") if _is_runnable_cli(p)
    )


def _discover() -> list[str]:
    """Use-case dirs that should carry a manifest: those holding runnable CLI scripts.

    A dir whose only `.py` files are import-only modules does not qualify. A dir that
    already carries a manifest qualifies regardless, so an existing manifest can never
    drop out of the sweep unnoticed.
    """
    found = []
    for entry in sorted(REPO_ROOT.iterdir()):
        if not entry.is_dir() or entry.name.startswith(".") or entry.name in SKIP_DIRS:
            continue
        if (entry / "tools.json").exists() or _flat_cli_scripts(entry.name):
            found.append(entry.name)
    return found


SWEPT = _discover()

MANIFEST_BEARING = [uc for uc in SWEPT if (REPO_ROOT / uc / "tools.json").exists()]

# Use cases with runnable CLIs and no manifest. Filed separately from BL-084, which
# implements cloudcost only; BL-084's row carries the other three as "filed or done".
NO_MANIFEST_YET = ("boxy-pipeline", "docbuilder", "provenance")

_NO_MANIFEST_REASON = (
    "no tools.json yet — tracked by BL-089 (filed alongside BL-084, which did cloudcost "
    "first); every runnable CLI in this use case is undeclared and amber in Rig"
)


def _param(use_case: str):
    """Attach the expected-fail marker for a use case with no manifest at all."""
    if use_case in NO_MANIFEST_YET:
        return pytest.param(
            use_case,
            marks=pytest.mark.xfail(strict=True, reason=_NO_MANIFEST_REASON),
        )
    return use_case


def _load(use_case: str) -> dict:
    return json.loads((REPO_ROOT / use_case / "tools.json").read_text(encoding="utf-8"))


def test_discovery_sweep_intact():
    """Guard the sweep itself: a discovery that silently returns less passes everything.

    Asserting the dir set (rather than per-dir counts) keeps this stable when scripts are
    added, while still failing if a use case stops being swept.
    """
    assert SWEPT == [
        "api",
        "boxy-pipeline",
        "cloudcost",
        "ct-bot",
        "ct-rpg",
        "docbuilder",
        "drive",
        "eduloka",
        "email",
        "payslip",
        "provenance",
    ]
    # The subject of BL-084: eight runnable CLIs plus the import-only `_normalized.py`.
    # Six until m3-cloudcost t1 added `fetch_linode.py`, seven until m6-cloudcost t2 added
    # `fetch_github.py`. The count is kept because this assertion's whole argument is that
    # a new CLI and its manifest entry land together; it is the one place the number is the
    # claim rather than decoration. The two DID disagree for one ticket — t2 landed the
    # adapter without the manifest entry — and this arm going red is what said so, which is
    # the whole reason it is a count and not a comment.
    assert len(_flat_cli_scripts("cloudcost")) == 8

    # api's manifest is real, but its scripts live in `api/tenant/scripts/` and
    # `api/gateway/scripts/` — nested, so neither the walker nor this suite scans them.
    # `test_no_undeclared_scripts[api]` therefore passes over an empty set. Asserted here
    # so that vacuity is visible rather than reading as coverage.
    assert _flat_cli_scripts("api") == []


@pytest.mark.parametrize("use_case", [_param(uc) for uc in SWEPT])
def test_manifest_parses(use_case):
    """Valid JSON and schema-conformant, per the serde structs at `tools.rs:4-46`."""
    manifest = _load(use_case)

    assert REQUIRED_TOP_LEVEL <= set(manifest), (
        f"{use_case}: missing top-level {REQUIRED_TOP_LEVEL - set(manifest)}"
    )
    assert manifest["use_case"] == use_case
    assert manifest["manifest_version"] == "1"
    assert isinstance(manifest["description"], str)
    assert isinstance(manifest["scripts"], list)

    for script in manifest["scripts"]:
        name = script.get("name", "<unnamed>")
        assert REQUIRED_SCRIPT_FIELDS <= set(script), (
            f"{use_case}/{name}: missing {REQUIRED_SCRIPT_FIELDS - set(script)}"
        )
        # Rust types these as bare `String`; a non-string is a serde reject, which
        # `tools.rs:526` turns into a silently absent manifest.
        for field in ("name", "file", "description", "example"):
            assert isinstance(script[field], str), (
                f"{use_case}/{name}: {field} must be a string, "
                f"got {type(script[field]).__name__}"
            )
        assert script["output"] in VALID_OUTPUTS, (
            f"{use_case}/{name}: output={script['output']!r} not in {sorted(VALID_OUTPUTS)}"
        )
        assert isinstance(script["args"], list)

        for arg in script["args"]:
            arg_name = arg.get("name", "<unnamed>")
            assert REQUIRED_ARG_FIELDS <= set(arg), (
                f"{use_case}/{name}/{arg_name}: missing {REQUIRED_ARG_FIELDS - set(arg)}"
            )
            assert arg["type"] in VALID_ARG_TYPES, (
                f"{use_case}/{name}/{arg_name}: type={arg['type']!r} "
                f"not in {sorted(VALID_ARG_TYPES)}"
            )
            assert isinstance(arg["required"], bool)
            # Option<String>: null or a string, never a bare int — a numeric default must be
            # quoted or serde rejects the manifest.
            assert arg["default"] is None or isinstance(arg["default"], str), (
                f"{use_case}/{name}/{arg_name}: default must be a string or null, "
                f"got {type(arg['default']).__name__}"
            )


@pytest.mark.parametrize("use_case", MANIFEST_BEARING)
def test_declared_files_exist(use_case):
    """Every declared `file` resolves — `tools_run_script` joins it and execs it."""
    for script in _load(use_case)["scripts"]:
        target = REPO_ROOT / use_case / script["file"]
        assert target.is_file(), (
            f"{use_case}/{script['name']}: declared file {script['file']} does not exist"
        )


@pytest.mark.parametrize("use_case", MANIFEST_BEARING)
def test_env_dep_fields_complete(use_case):
    """`EnvDep` has no serde defaults — one missing field drops the whole manifest.

    This is also the source of Rig's dynamic agent-config rows (`tools.rs:594-604` →
    `AgentConfigTab.tsx`), so a malformed entry costs the config surface too.
    """
    for script in _load(use_case)["scripts"]:
        for dep in script.get("env", []):
            key = dep.get("key", "<unkeyed>")
            assert REQUIRED_ENV_FIELDS <= set(dep), (
                f"{use_case}/{script['name']}/{key}: missing "
                f"{REQUIRED_ENV_FIELDS - set(dep)}"
            )
            assert isinstance(dep["masked"], bool)
            for field in ("key", "label", "group", "placeholder"):
                assert isinstance(dep[field], str)


@pytest.mark.parametrize(
    "use_case",
    [
        pytest.param(
            "payslip",
            marks=pytest.mark.xfail(
                strict=True,
                reason="BL-087 — payslip/tools.json omits a runnable CLI "
                "(merge_employee_payslips.py, undeclared, amber in Rig); "
                "surfaced by this suite, out of BL-084 cloudcost scope",
            ),
        )
        if uc == "payslip"
        else _param(uc)
        for uc in SWEPT
    ],
)
def test_no_undeclared_scripts(use_case):
    """The offline proxy for the amber badge: every runnable CLI is declared."""
    manifest_path = REPO_ROOT / use_case / "tools.json"
    declared = (
        {s["file"] for s in _load(use_case)["scripts"]} if manifest_path.exists() else set()
    )
    undeclared = [f for f in _flat_cli_scripts(use_case) if f not in declared]
    assert undeclared == [], (
        f"{use_case}: undeclared runnable CLI(s) {undeclared} — these render with the "
        f"amber badge and a raw-args box in Rig"
    )
