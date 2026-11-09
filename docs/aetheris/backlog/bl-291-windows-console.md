# BL-291 — Windows console-less worker start (design brief)

**Status:** T0 filed (this document). T1 not started.
**Type:** design brief. A contract for the implementation cc:prompt,
cited by item number.
**Date:** 2026-10-06
**Row:** BL-291 (open, `docs/backlog-2026-06.md` §Harness).
**Evidence:** `docs/evidence/BL-291.md`.
**Citations:** `H` = harness `aetheris` at `77cb0ab`.
**No harness edit in this ticket.**

---

## 1. Scope

The capability: **a run that starts the worker opens no visible console
window on Windows**, while the worker still starts and the run proceeds.
Two knobs, named here, placed by T1, neither implemented here.

## 2. Tranches

- T0 — this brief.
- T1 — the harness implementation: the two knob placements below (or
  their documented equivalents), plus a test that pins the done-when
  (the port options built by `port_options/2` include `:hide` on
  Windows; the Rust children's build paths are asserted where a test
  can reach them — the exact test shape is T1's).

## 3. Contract

**C1 — The port carries `:hide` on Windows.** `port_options/2`
(`worker/client.ex:132-140@H`) appends `:hide` when
`{:win32, _} = :os.type()` (carrying it on Unix is either harmless or
an ERTS arg-list error — T1 verifies which and documents the choice;
the finding requires the Windows arm only). With `:hide`, Erlang's
`spawn_executable` does not give the child its own console window.

**C2 — Rust children carry `CREATE_NO_WINDOW` on Windows.** Every
`std::process::Command` the worker spawns (`mcp.rs:24@H` for stdio MCP
servers, `mcp.rs:432@H` for the `python3` child, and any future spawn)
sets `creation_flags(0x08000000)` (`CREATE_NO_WINDOW`) under the
Windows `cfg` — the worker's children inherit no console and open none.

**C3 — Behaviour unchanged elsewhere.** The worker still starts, the
ready handshake still works, stdio framing (`{:packet, 4}`) is
untouched, and non-Windows platforms are byte-for-byte unaffected. A
deliberately-visible console never becomes a feature — if T1 wants a
debug exit-hatch, that is a separate decision with its own docs.

**C4 — A run proceeds.** The done-when's second arm: after the knobs,
the run still reaches the loop and completes a tool loop on Windows —
hiding a window must not hide the worker.

## 4. Scout facts

- F1 The port: `Port.open({:spawn_executable, worker_path},
  port_options(sandbox_path))` — `client.ex:243@H`; the options list at
  `:132-140@H` has no `:hide`.
- F2 The children: `std::process::Command::new(path)` at
  `native/aetheris_worker/src/mcp.rs:24@H`; the `python3` child at
  `:432@H`; zero `CREATE_NO_WINDOW`/`creation_flags` anywhere under
  `native/` at `H` (grep).
- F3 Erlang `spawn_executable` on Windows opens a visible console for
  the child unless `:hide` is in the port options (ERTS behaviour;
  the :hide option is Windows-specific because the console subsystem
  is).
- F4 `mcp.rs` already gates platform-specific code paths by `cfg` (the
  pre-filter window); the flags site follows the file's existing shape.
- F5 The operator requires native Windows — no WSL (the finding's
  premise, supplied).

## 5. Open for plan STOPs

- Whether `:hide` travels only on Windows or unconditionally (per C1's
  verification note).
- Whether the two knobs land in one commit (they are one behaviour and
  are tested separately by surface — Elixir ports and Rust children).
- The Rust-side test shape: `creation_flags` assertions may have to be
  build-level (the flags only exist under `windows` cfg); T1 decides
  what the test pins and says so.
