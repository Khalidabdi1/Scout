---
name: generate
description: Scan the current project and create or refresh a Stitch-style design.md file grounded in the codebase's actual design tokens, component patterns, and layout rules.
argument-hint: [output-path]
disable-model-invocation: true
---

# Generate `design.md`

Use this skill when the user wants a repository scanned and converted into a `design.md` or `DESIGN.md` file.

Before writing anything, gather grounded evidence from the current project:

```!
python3 "${CLAUDE_SKILL_DIR}/scripts/scan_project.py" --project-root "$PWD" --format markdown --max-files 160
```

## Working contract

- The default output file is `design.md` in the current working directory.
- If `$ARGUMENTS` is provided and ends with `.md`, use that exact path.
- If `$ARGUMENTS` is provided and does not end with `.md`, treat it as a directory and write `$ARGUMENTS/design.md`.
- If the target file already exists, update it in place instead of creating a duplicate.
- If the project has very little UI evidence, still create the file, but add a short `Gaps & Assumptions` section instead of inventing specifics.

## Required workflow

1. Read the scanner output above carefully.
2. Open at least 3 representative source files before drafting:
   - one styling source such as CSS, Tailwind config, or tokens
   - one layout or screen file
   - one shared UI component
3. Use [reference.md](reference.md) to stay aligned with Stitch-style `DESIGN.md` expectations.
4. Use [template.md](template.md) as the output skeleton.
5. Write the final file to the resolved output path.

## Writing rules

- Ground every claim in evidence from the repo whenever possible.
- Favor semantic, designer-friendly language over raw implementation jargon.
- Include exact values when they matter, especially hex colors, font families, spacing scales, radii, and shadow cues.
- Translate implementation details into human descriptions.
  - Example: `rounded-full` becomes "pill-shaped".
  - Example: `rounded-xl` becomes "generously rounded corners".
- Keep the document concise and useful. Aim for a practical design-system brief, not a dump of every class name.
- Prefer lower-case `design.md` unless the user explicitly asked for `DESIGN.md` or another path.

## Final quality bar

The finished document should help Claude or Stitch generate new screens that feel consistent with the existing product. It should explain:

- the visual theme and atmosphere
- the functional color roles
- the typography and hierarchy rules
- the component styling patterns
- the layout and spacing principles

If evidence is mixed or incomplete, say so plainly in `Gaps & Assumptions`.
