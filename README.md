# design-md Claude Code Plugin

This repository is a Claude Code plugin that scans a project, extracts design signals from the codebase, and helps Claude write a Stitch-style `design.md` file.

The links in the request point to Claude Code plugin docs and Stitch `DESIGN.md` guidance, so this plugin targets Claude Code and defaults to writing `design.md` in the current project.

## What the plugin does

- Scans the current project for design evidence from `package.json`, CSS, Tailwind config, theme files, and UI components.
- Summarizes colors, typography, spacing, radius, shadows, and component patterns with file references.
- Guides Claude to turn that evidence into a semantic design system document for Stitch-style prompting.
- Writes `design.md` by default, or any custom Markdown path you pass to the skill.

## Install and run

For local development and testing:

```bash
claude --plugin-dir /absolute/path/to/Scout
```

Then, inside the project you want to document, run:

```text
/design-md:generate
```

Optional output path examples:

```text
/design-md:generate DESIGN.md
/design-md:generate docs/design.md
```

## Skill behavior

When you invoke `/design-md:generate`, the plugin:

1. Runs a local Python scanner to summarize the repository's frontend design signals.
2. Verifies those signals against a few representative files.
3. Creates or updates `design.md` with a structured design-system summary.

The generated document follows the core Stitch guidance:

- describe the overall atmosphere in natural language
- name colors semantically and include exact color values
- translate technical styling into human-readable component rules
- capture layout principles so future screens stay consistent

## Repository layout

```text
.claude-plugin/plugin.json
skills/generate/SKILL.md
skills/generate/reference.md
skills/generate/template.md
skills/generate/scripts/scan_project.py
tests/test_scan_project.py
```

## Notes

- Stitch examples and community mirrors often use `DESIGN.md` in uppercase. This plugin defaults to `design.md` because that is what was requested, but you can pass `DESIGN.md` as the output path if you prefer.
- The scanner uses only the Python standard library, so there are no runtime dependencies to install.

## Validate locally

```bash
python3 -m unittest discover -s tests
python3 skills/generate/scripts/scan_project.py --project-root . --format markdown
```
