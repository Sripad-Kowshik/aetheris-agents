# agents/capability_matrix_ct-rpg.exs
#
# Capability matrix sub-agent: ct-rpg use case.
# Reads agents and scripts under ct-rpg/ and writes docs/.sections/ct-rpg.md.
#
# Run as part of the capability_matrix sprint case, or standalone:
#   mix aetheris run ../aetheris-agents/agents/capability_matrix_ct-rpg.exs

agent_root = Path.expand(Path.join(Path.dirname(__ENV__.file), ".."))

model    = System.get_env("AETHERIS_MODEL") || "claude-haiku-4-5-20251001"
provider = System.get_env("AETHERIS_PROVIDER") || "anthropic"

%Aetheris.RunConfig{
  run_id:           "cap-matrix-ct-rpg-#{Aetheris.ID.generate()}",
  mode:             :record,
  provider:         provider,
  model:            model,
  label:            "cap-matrix: ct-rpg",
  sandbox_path:     agent_root,
  overlay_base_dir: nil,
  max_steps:        15,
  context_strategy: :full,
  tools:            ["list_dir", "read_file", "write_file"],
  system_prompt:    """
  You are a documentation agent. Read the source files in this use case and
  write a capability section in Markdown.

  Workflow — follow these steps in order:

  Step 1: List agents.
    Call list_dir with path: "ct-rpg/agents"
    Collect .exs filenames only. Ignore non-.exs files.

  Step 2: For each .exs agent file:
    Call read_file with path: "ct-rpg/agents/{filename}"
    Extract:
      - The label: "..." value (agent's human name)
      - The tools: [...] list
      - If OrbConfig: extract tools from each agent_config entry separately,
        labelling each by its label field.

  Step 3: List scripts.
    Call list_dir with path: "ct-rpg/scripts"
    Collect .py and .exs filenames. Skip __init__.py and conftest.py.

  Step 4: For each .py or .exs script:
    Call read_file with path: "ct-rpg/scripts/{filename}"
    Read the file and extract the one-line purpose from the opening docstring
    (for .exs files, use the first non-blank # comment line instead of a docstring)
    (the line immediately after the opening triple-quote, before any blank
    lines or argument descriptions). Example:
      \"\"\"parse_csv.py <csv_path>\\n\\nReads payroll CSV...\"\"\"
      → purpose is "Reads payroll CSV..."
      (skip the usage line, use the first descriptive sentence)

  Step 5: Write the section file.
    Call write_file with:
      path: "docs/.sections/ct-rpg.md"
      content: the Markdown section (format below)

  Output format:

  ## CT-RPG

  ### Agents

  | Agent file | Label | Tools |
  |------------|-------|-------|
  | {file}.exs | {label} | `{tool1}`, `{tool2}` |

  ### Scripts

  | Script | Purpose |
  |--------|---------|
  | {script}.py | {one-line purpose} |

  Rules:
  - One row per agent file. For OrbConfig, expand to one row per agent_config.
  - Keep purpose to one line — first descriptive sentence of docstring only.
  - If a directory is empty or missing, write "None." under that heading.
  - Do not include test files, output/ directories, or __pycache__.
  - Write the section file once at Step 5.
  """,
  user_prompt: "Generate the capability section for the ct-rpg use case. Begin."
}
