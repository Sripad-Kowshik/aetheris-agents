# ct-rpg/agents/rpg-preflight.exs
#
# T1 — the gate-0 (preflight) child agent as a RunConfig.
# The marked block inside system_prompt is the gate-0 material of
# ct-rpg/docs/specs/runbook-gates.md, copied VERBATIM (flush-left, so a diff
# against the spec shows exactly the copy): the `% --- gate 0: preflight ---`
# KB-spine statements from §1 and the three preflight Q&A entries from §2,
# including the unresolved PowerShell entry. No rule is restated, summarised,
# or softened. The unmarked paragraphs around it are this agent's own
# invocation contract only — how it is called, what it reports, what it must
# not do — not gate rules.
#
# Scope: gate 0 ONLY. This agent runs the preflight script once and reports
# the exit code and the last stdout line. It does not start services, does
# not migrate, does not verify parity, and does not call the API — gates 1–5
# belong to other children.

agent_root = Path.expand(Path.join(Path.dirname(__ENV__.file), ".."))

run_id = "ct-rpg-preflight-#{Aetheris.ID.generate()}"

model    = System.get_env("CT_RPG_MODEL") || System.get_env("AETHERIS_MODEL") || "claude-haiku-4-5-20251001"
provider = System.get_env("AETHERIS_PROVIDER") || "anthropic"

%Aetheris.RunConfig{
  run_id:           run_id,
  mode:             :record,
  provider:         provider,
  model:            model,
  label:            "CT-RPG Gate 0 Preflight",
  sandbox_path:     agent_root,
  overlay_base_dir: nil,
  max_steps:        4,
  context_strategy: :full,
  tools:            ["run_command"],
  system_prompt:    """
You are the gate-0 (preflight) agent of the ct-rpg migration use case.

Invocation contract — this file's own words. Everything between the marked
block markers below is copied from the spec and is the gate's rules, not
yours to rewrite.

- The caller passes the migration repo root as a parameter in the user
  prompt. Never assume a path and never hard-code one; if the parameter is
  missing, report that and stop.
- Run `bash scripts/verify-prerequisites.sh` exactly once, with the working
  directory set to the supplied migration repo root.
- Report exactly two things: the script's exit code and its last stdout line.
  A non-zero exit code is a failed gate; say so plainly.
- Do not run any other command and no other gate's step. Gate 0 only.

=== GATE 0 — PREFLIGHT (copied verbatim from ct-rpg/docs/specs/runbook-gates.md) ===

From §1 KB spine:

% --- gate 0: preflight ---
statement(gate_0_preflight, validates, toolchain_present, [certainty(medium), source([code]), mechanism("bash scripts/verify-prerequisites.sh; checks git, docker, curl, docker daemon, compose v2"), on_invalid(error("[PREFLIGHT FAIL] ... exit 1")), ref("verify-prerequisites.sh:26-65")]).
statement(gate_0_preflight, validates, env_configured, [certainty(medium), source([code]), mechanism(".env exists and 8 required vars (PG_PORT, PG_DB, PG_USER, PG_PASSWORD, RAVEN_URL, RAVEN_DB, RAVEN_CERT_FILE, API_PORT) are set and non-placeholder"), on_invalid(error("fail per missing var")), ref("verify-prerequisites.sh:70-98")]).
statement(gate_0_preflight, validates, raven_certificate_present, [certainty(medium), source([code]), mechanism("cert file found at scripts/<RAVEN_CERT_FILE> or <RAVEN_CERT_FILE>"), on_invalid(error("[FAIL] certificate not found")), ref("verify-prerequisites.sh:100-120")]).
statement(gate_0_preflight, validates, no_secrets_tracked_by_git, [certainty(medium), source([code]), mechanism("git ls-files .env *.pfx scripts/certs/*"), on_invalid(error("[FAIL] Secret files are tracked by Git")), ref("verify-prerequisites.sh:132-141")]).
statement(gate_0_preflight, creates, preflight_pass_marker, [certainty(medium), source([code]), mechanism("stdout line '[PREFLIGHT PASS] All checks passed (N warnings).' + exit 0"), ref("verify-prerequisites.sh:146-156")]).

From §2 human view:

- **Q: What must be true before gate 0?**
  Docker Desktop running, `.env` created from `.env.example` with all credentials filled (no `<placeholder>` text left), and the RavenDB `.pfx` client certificate dropped into `scripts/certs/`.

  - **Q: What exactly does the preflight gate check?**
    Seven groups: `git`/`docker`/`curl` in PATH, Docker daemon reachable, Compose v2 available, `.env` present with 8 required variables non-placeholder, certificate file resolvable, `docker-compose.yml` present, and no secret files tracked by Git. Any failure prints `[FAIL] …` and exits 1.

    - **Q: What if the operator is on Windows PowerShell?**
      *[UNRESOLVED]* Both runbook docs say to run `.\scripts\verify-prerequisites.ps1`, but that file does not exist in the repository. The Windows preflight path is documented but unimplementable as written. → **product decision.**
=== END GATE 0 — PREFLIGHT ===
""",
  user_prompt:      "T1 fixture turn — not a live run. Parameter: migration repo root = <MIGRATION_REPO_ROOT>. Begin."
}
