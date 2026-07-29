---
name: build-planetscale-landing-pages
description: "Design, implement, redesign, or review technical product landing pages with a PlanetScale-inspired visual language: monospace typography, editorial copy, stark light or dark surfaces, ruled grids, tables, proof-heavy sections, and restrained accent color. Use for developer tools, infrastructure, databases, APIs, open-source products, technical SaaS, launch pages, pricing pages, and documentation-like marketing sites. Preserve the product's own identity; do not copy PlanetScale branding or content."
---

# Build PlanetScale Landing Pages

Create technical marketing pages that feel like a confident product document: direct, structured, information-dense, and almost unstyled at first glance. Use the reference grammar, not the PlanetScale brand.

## Start from the product

Before changing code:

1. Inspect the current route, component system, tokens, fonts, icon library, framework, and responsive conventions.
2. Gather real product evidence: features, commands, API calls, schemas, benchmarks, customers, reliability claims, pricing, and screenshots.
3. Decide the page's one primary claim and one primary action.
4. Preserve working behavior, accessibility, routing, analytics, and existing brand assets.
5. Choose light or dark from the product's identity. Do not force dark mode merely because the references include it.

Do not invent customer logos, metrics, quotes, compliance claims, or benchmarks. Use clearly marked placeholders only when the user asks for a mockup.

## Compose the page

Build a coherent editorial sequence rather than a stack of interchangeable cards:

1. Optional one-line announcement strip.
2. Compact navigation divided by thin vertical rules.
3. Claim-led opening with a short technical explanation and direct text or rectangular CTA.
4. Concrete proof near the fold: product table, code sample, benchmark, architecture diagram, or customer grid.
5. Long-form sections separated by dotted or dashed rules.
6. Trust section with authorized customer marks, a real quote, or measurable operating facts.
7. Bordered multi-column footer with legal and social rows.

Use only the sections supported by the product. A short honest page is stronger than a long generic one.

## Apply the visual grammar

- Use one deliberate monospace family for most or all visible type. Prefer an existing project font; otherwise use a high-quality local/system mono stack.
- Use compact bold headings, readable body copy, and generous line height. Keep headings blunt rather than oversized.
- Set the page on a near-black or near-white canvas. Use one main accent for links and one optional CTA accent.
- Create hierarchy with type weight, whitespace, underlines, and 1px rules.
- Align navigation, copy, tables, proof grids, and footer columns to a shared content grid.
- Keep corners square or nearly square. Use shadows only for functional overlays.
- Let empty space create rhythm, but keep the content column broad enough to feel infrastructural rather than blog-like.
- Use real tables when the information is tabular. Use CSS grid for visual matrices and footer navigation.
- Make hover and focus states crisp: underline, foreground shift, background inversion, or a 1px outline.
- Keep motion minimal and functional. Prefer a quick reveal, row highlight, or underline transition; support reduced motion.

Read [references/visual-language.md](references/visual-language.md) for exact tokens, spacing, responsive behavior, and component recipes.

## Use the screenshots deliberately

Inspect the images in `assets/` when the task needs close visual calibration:

- `reference-light-page.png`: light canvas, navigation, opening copy, product table, and long-form rhythm.
- `reference-logo-grid.png`: dark navigation, accent usage, technical copy, and bordered customer matrix.
- `reference-editorial-sections.png`: section rules, linked bullet lists, quote treatment, and long-form density.
- `reference-footer.png`: ruled footer columns, legal row, and social links.

Treat the screenshots as study material. Do not ship their logos, names, exact copy, or trademarked visual assets.

## Adapt instead of cloning

Translate the system through the target brand:

- Replace PlanetScale orange/cyan with the product's strongest existing accent.
- Replace database-specific artifacts with evidence from the actual product.
- Keep an existing logo and recognizable brand type where appropriate.
- Use the project's components and tokens when they can express the system cleanly.
- Preserve useful UI from an existing page; restyle or reorder only where it improves the hierarchy.

## Responsive rules

- Collapse navigation into an accessible menu before links wrap or crowd.
- Change wide proof grids from 5 columns to 2, then 1 only when the content requires it.
- Turn comparison tables into horizontal scroll regions or labeled stacked rows; do not silently remove columns.
- Stack footer columns while preserving rules and headings.
- Reduce outer gutters and section spacing, not body readability.
- Keep at least one concrete proof artifact visible in the first mobile viewport or immediately after it.

## Avoid the wrong look

Do not add:

- Gradient text, ambient glows, glass panels, blobs, or decorative 3D objects.
- Pill-shaped navigation and rounded cards around every paragraph.
- A huge centered slogan followed by three generic feature cards.
- Emoji used as product icons.
- Fake terminal windows, fake metrics, or fabricated social proof.
- Decorative noise, scanlines, or “retro terminal” effects that harm reading.
- Monospace text at tiny sizes or low contrast.
- Dashed borders on every element; reserve them for section structure, tables, and footer grids.
- A direct PlanetScale clone with substituted nouns.

## Implement and verify

Read [references/implementation-and-qa.md](references/implementation-and-qa.md) before editing a production codebase or performing a design review.

Finish by:

1. Run the project's formatter, typecheck, tests, and build at the appropriate scope.
2. Render the page at desktop and mobile sizes.
3. Compare hierarchy, grid alignment, density, wrapping, and border continuity against the intended system.
4. Test keyboard navigation, visible focus, landmarks, heading order, contrast, and reduced motion.
5. Remove placeholders and verify every public claim and link.

In the final response, state what changed, what real product evidence was used, and what validation ran.
