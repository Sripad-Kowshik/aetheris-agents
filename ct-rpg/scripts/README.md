# ct-rpg scripts

No deterministic helpers yet. The migration's real scripts
(`verify-prerequisites.sh`, `migrate_all.py`,
`verify_raven_to_postgres.py`, `wait-for-api.sh`) live in the migration
repo and are run there, inside its Docker containers, by the ct-rpg
agents — see `ct-rpg/agents/` and `ct-rpg/docs/specs/runbook-gates.md`.

This directory stays empty until a helper is genuinely needed here.
