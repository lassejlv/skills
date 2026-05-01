---
name: plain-design-engineer
description: Create, redesign, or review frontend interfaces with a plain, technical infrastructure-product style. Use for developer tools, databases, observability, APIs, CLIs, SaaS dashboards, docs, and landing pages that should feel precise, editorial, content-led, and credible instead of glossy or generic.
---

# Plain Design Engineer

## Intent

Design interfaces like a serious infrastructure product: precise, editorial, technical, fast, and unglossy. Let content, hierarchy, and useful product artifacts carry the page. Avoid decorative SaaS polish.

PlanetScale is the reference point: white or near-white backgrounds, black text, restrained gray surfaces, thin rules, compact technical labels, dense comparison tables, code/database artifacts, benchmark charts, and blunt product copy.

## Modes

Infer the mode from the request:

- `create`: build a new page, component, or product surface.
- `redesign`: restyle an existing UI while preserving working behavior.
- `review`: audit design quality without editing unless asked.
- `landing`: developer or infrastructure landing page.
- `dashboard`: dense product, admin, analytics, billing, or ops UI.
- `docs`: technical docs, API docs, changelog, or product education surface.

## First Pass

Before designing or editing, inspect the project enough to avoid fighting the codebase:

- Existing design system, component primitives, icon library, CSS framework, Tailwind config, tokens, fonts, and layout conventions.
- Current product/domain evidence: real features, CLI commands, API examples, schema, metrics, workflows, screenshots, logs, or docs.
- Existing responsive patterns and route/page ownership.
- The actual design problem: generic SaaS polish, weak hierarchy, low density, fake artifacts, poor mobile behavior, or unclear product claim.

Preserve the project's component library, tokens, routing, and layout conventions unless they are the source of the design problem.

## Core Rules

- Prefer plain surfaces over ornamental cards.
- Use typographic hierarchy, spacing, borders, and content density instead of gradients, glows, blobs, or illustrations.
- Put at least one real technical artifact in important product/marketing screens.
- Keep shapes crisp: 0-8px radii, 1px borders, and shadows only when depth is functional.
- Use neutral color as the base; use accent color sparingly for links, status, charts, and callouts.
- Make the first viewport immediately say what the product is, who it is for, and what technical claim it makes.
- Do not hide all technical proof on mobile.

## Visual Baseline

- Background: `#ffffff`, `#fafafa`, `#f7f7f5`, or `#f4f4f2`.
- Text: `#0a0a0a`, `#171717`, or `#2a2a2a`.
- Muted text: `#666666`, `#737373`, or `#8a8a8a`.
- Borders: `#e5e5e5`, `#d9d9d6`, or `#cfcfca`.
- Technical surfaces: `#111111`, `#181818`, or `#f2f2ef`.
- Typography: system sans, Inter, Geist, or local neutral sans; mono for code, IDs, metrics, table labels, and diagrams.
- Layout: full-width sections separated by thin rules, aligned grids, compact rows, editorial columns, useful tables, and visible product evidence.

## References

Load these files only when needed:

- `references/design-audit-rubric.md`: scoring rubric for review and redesign tasks.
- `references/technical-artifacts.md`: artifact recipes for code, data, diagrams, tables, logs, and charts.
- `references/implementation-checklist.md`: final verification checklist for frontend edits.
- `references/copy-rules.md`: copy tone, banned phrases, and stronger alternatives.
- `references/page-patterns.md`: landing, dashboard, docs, and pricing layout patterns.

## Anti-Patterns

Do not use:

- Gradient blobs, decorative orbs, bokeh, glass panels, neon glows, or purple-blue SaaS gradients.
- Huge rounded cards for every section.
- Stock imagery that does not show the actual product, workflow, or domain.
- Oversized hero copy with no technical proof.
- Fake dashboards filled with meaningless numbers.
- Generic feature cards that could belong to any SaaS product.
- Copy such as "seamless", "revolutionary", "next-gen", "beautiful", or "unlock your potential."
- Excess animation that competes with reading and scanning.

## Final Response

Summarize what changed, what product evidence or artifacts were used, and what validation ran. If the task was a review, lead with findings and scores.
