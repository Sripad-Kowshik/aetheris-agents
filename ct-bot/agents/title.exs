# ct-bot/agents/title.exs
#
# T8 — the title agent: one short title for the conversation.
# A child agent under the existing use case, so no registry row, no matrix
# edit, no dormant flip (the survey's two-file shape). The wrapper is the
# suggestions.exs shape: run_id ct-bot-title- minted outside the struct,
# sandbox_path from __ENV__.file, env-driven model/provider with the same
# fallbacks, mode :record, context_strategy :full, overlay_base_dir: nil,
# max_steps 4, tools []. There is no prompt source file for this agent —
# the rules below are the ticket's, written once here; the mechanical
# zero-diff property does not apply. The agent does not save anything:
# it returns the title text, and the HOST posts it (as the thread's title;
# cf. the threads table's nullable title column). Plain text only — no
# JSON, no markdown fences.

agent_root = Path.expand(Path.join(Path.dirname(__ENV__.file), ".."))

run_id = "ct-bot-title-#{Aetheris.ID.generate()}"

model    = System.get_env("CT_BOT_MODEL") || System.get_env("AETHERIS_MODEL") || "claude-haiku-4-5-20251001"
provider = System.get_env("AETHERIS_PROVIDER") || "anthropic"

%Aetheris.RunConfig{
  run_id:           run_id,
  mode:             :record,
  provider:         provider,
  model:            model,
  label:            "CT-Bot Title Agent",
  sandbox_path:     agent_root,
  overlay_base_dir: nil,
  max_steps:        4,
  context_strategy: :full,
  tools:            [],
  system_prompt:    """
You are the Title agent for CT-Bot. Return one short title for the
conversation, derived from the first user message.

Plain text only — no JSON, no markdown fences, no commentary before or
after.

Rules:
1. One title per run: a single line, nothing else.
2. No more than 40 characters.
3. No quotes — not single, not double, not smart.
4. No trailing period.
5. Use only the words of the conversation; never invent a subject.
""",
  user_prompt:      "T8 fixture turn — not a live host turn. Begin."
}
