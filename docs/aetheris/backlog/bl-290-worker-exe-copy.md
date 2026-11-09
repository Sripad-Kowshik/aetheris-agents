# BL-290 — Windows worker-binary copy suffix (design brief)

**Status:** T0 filed (this document). T1 not started.
**Type:** design brief. Short by design: the change is the extension
conditional in `copy_binary/3`.
**Date:** 2026-10-06
**Row:** BL-290 (open, `docs/backlog-2026-06.md` §Harness).
**Evidence:** `docs/evidence/BL-290.md`.
**Citations:** `H` = harness `aetheris` at `77cb0ab`.

---

## 1. Scope

`mix compile` succeeds on Windows: `copy_binary/3` finds cargo's
actually-emitted name (`aetheris_worker.exe` on Windows, plain
`aetheris_worker` elsewhere) and the copied binary under `priv/worker/`
carries the `.exe` suffix. The extension conditional is the change; the
runtime consumer paths (`worker/client.ex:241@H`, `doctor.ex:37@H`) must
resolve whatever the copy produces — the implementation ticket picks one
of two shapes and applies it at both ends.

## 2. The change, stated

In `lib/mix/tasks/compile/aetheris_worker.ex`:

- `copy_binary/3` gains the Windows form: source is
  `native/target/release/#{name}.exe` when `{:win32, _} =
  :os.type()` (the extension conditional), plain `#{name}` otherwise.
- The copied output is `priv/worker/#{name}.exe` on Windows (the
  done-when's suffix requirement) — **and** the two consumer paths
  (`worker/client.ex:241`, `doctor.ex:37`) resolve the suffixed name on
  Windows, or the copy writes both names (one line more, zero consumers
  touched). T1 picks; the two ends must agree, and the done-when checks
  the copied file's name.

`@exec_server_binary` gets the identical treatment — same cargo rule,
same consumers discipline.

## 3. Contract

**C1 — done-when (the row's arm).** `mix compile` succeeds on Windows,
and the binary present under `priv/worker/` carries the `.exe` suffix.

**C2 — Both ends agree.** However the suffix is decided, the runtime
workers' resolution (`priv/worker/aetheris_worker` today) must read the
same file the copy wrote — either the consumers grow the conditional or
the copy writes both names; a passing compile with a runtime that
cannot find its binary is not a fix.

**C3 — Unix unchanged.** On non-Windows, nothing moves: same names, same
paths, same `chmod`. `File.chmod!` is a no-op-tolerant operation on
Windows and stays where it is.

**C4 — `mix hex.audit` / CI unaffected.** This is a mix-task change; no
dependency moves.

## 4. Scout facts

- F1 The literal and the bare-join copy: `lib/mix/tasks/compile/aetheris_worker.ex:9-10, 43-49@H`.
- F2 Cargo emits `.exe` for both packages into `native/target/release/`
  on Windows (standard behaviour; the target's own naming).
- F3 The consumed path is nonsuffixed today: `client.ex:241@H`,
  `doctor.ex:37@H`; zero `exe` anywhere in the chain at `H` (grep).

## 5. Open for plan STOPs

- Suffix conditional at copy only + both-names output, or consumer-side
  conditionals — T1's pick, applied at both ends (C2).
