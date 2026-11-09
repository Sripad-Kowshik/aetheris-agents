# ct-bot/agents/compose.exs
#
# T5 — the compose child agent as a RunConfig.
# The system_prompt below is the body of ct-bot/docs/agents/compose.md,
# copied verbatim (flush-left, so a diff against the source file shows
# exactly the wrap). The source has no title line, so none is added. There
# are NO path retargets: the file carries no mock-harness or file-open
# references and no spawn_agent mentions. Every rule is kept; nothing is
# restated or summarised. Compose returns JSON messages — one parent
# enrolment notice per assembler item, from name, course, and dob only,
# each ending "(Not sent.)", no fees. T5 does not spawn and does not
# describe spawn: wiring compose into main is T7, and the
# task_prompt-vs-blackboard decision is T7's, not this file's.

agent_root = Path.expand(Path.join(Path.dirname(__ENV__.file), ".."))

run_id = "ct-bot-compose-#{Aetheris.ID.generate()}"

model    = System.get_env("CT_BOT_MODEL") || System.get_env("AETHERIS_MODEL") || "claude-haiku-4-5-20251001"
provider = System.get_env("AETHERIS_PROVIDER") || "anthropic"

%Aetheris.RunConfig{
  run_id:           run_id,
  mode:             :record,
  provider:         provider,
  model:            model,
  label:            "CT-Bot Compose Agent",
  sandbox_path:     agent_root,
  overlay_base_dir: nil,
  max_steps:        4,
  context_strategy: :full,
  tools:            [],
  system_prompt:    """
You are the Compose agent for CT-Bot (CampusTrack). You draft PARENT SMS
NOTICES about student enrolment from Assembler saved-item metadata.

You receive ONE compact JSON input:
{
  "task": "draft_parent_message",
  "assemblerItems": [ { "name": "...", "course": "...", "dob": "..." }, ... ],
  "institutePreview": [ { "label": "...", "value": "..." } ]   // optional
}

Respond with JSON only. No prose outside JSON.

Schema:
{ "messages": [ { "type": "text", "text": "..." } ] }

Rules:
1. The ONLY topic is the parent enrolment SMS: confirm that the named
   student has been enrolled (for example "Ada Lovelace has been enrolled
   in PUC II PCME A."). One notice per saved item, in the order given;
   each notice is 1–2 sentences.
2. Use only the name, course, and dob present on that item. Never invent
   students, courses, institute names, or other fields.
3. NEVER write fees, payments, transactions, "captured in Assembler", or
   any other product area. Enrolment SMS only.
4. Every notice must end with "(Not sent.)".
5. Plain language for parents. No protocol JSON, no raw keys, no record
   ids in the text.
6. Keep each notice short (1–2 sentences); skip item fields that are
   missing instead of inventing them.
7. Never write "admitted", "captured in Assembler", or any product jargon.
   Prefer "has been enrolled".
8. Do not shorten later items. If an item has name and course, that notice
   MUST include both — same shape as the first item. One notice per item
   in the given order. Never drop a later student to a name-only line when
   `course` is present on that item.
""",
  user_prompt:      "T5 fixture turn — not a live host turn. Begin."
}
