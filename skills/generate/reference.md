# Stitch-style `design.md` reference

This plugin follows the public Stitch `design.md` concept and the mirrored Google Labs `design-md` skill guidance:

- `design.md` acts as the source of truth for generating new screens that stay aligned with an existing design language.
- The document should describe the system in natural language, but keep precise values where they matter.
- Colors should be named semantically and paired with exact values.
- Technical styling should be translated into human terms that a designer or model can reuse.

## Recommended structure

Use this structure unless the repo clearly needs a close variant:

```markdown
# Design System: [Project Name]

## 1. Visual Theme & Atmosphere
## 2. Color Palette & Roles
## 3. Typography Rules
## 4. Component Stylings
## 5. Layout Principles
```

## Good output traits

- Start with the overall mood before listing tokens.
- Explain each important color's role, not just its appearance.
- Convert radii and shadows into physical language such as "sharp", "subtly rounded", or "whisper-soft elevation".
- Describe components by behavior and appearance together.
- Document whitespace, alignment, and grid habits so future layouts remain consistent.

## Guardrails

- Do not invent a polished design system if the repo has weak evidence.
- Do not dump raw CSS without interpretation.
- Do not omit exact values for key colors and recurring tokens.
- Do not use generic labels like "blue" or "rounded" when a more descriptive phrase is justified by the evidence.
