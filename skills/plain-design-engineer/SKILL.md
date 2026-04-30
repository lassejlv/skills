---
name: plain-design-engineer
description: Create, restyle, or review frontend interfaces with a plain, technical, infrastructure-product visual direction inspired by PlanetScale.com. Use when Codex is asked to make UI feel like PlanetScale, remove generic SaaS styling, design landing pages or dashboards for developer tools, databases, infrastructure, cloud products, observability, CLIs, APIs, or technical documentation, or apply restrained editorial product design with sharp typography, thin borders, grayscale surfaces, data/code diagrams, and content-led layouts.
---

# Plain Design Engineer

## Intent

Style interfaces like a serious infrastructure company: precise, editorial, technical, fast, and unglossy. Let content, hierarchy, and useful diagrams carry the page. Avoid decorative SaaS polish.

Use PlanetScale as the reference point: white or near-white backgrounds, black text, restrained gray surfaces, thin rules, small technical labels, high information density, tabular comparison, ASCII/code/database diagrams, customer proof, benchmark charts, and blunt product copy.

## Design Principles

- Prefer plain surfaces over ornamental cards.
- Use strong typographic hierarchy instead of gradients, blobs, glows, or illustrations.
- Make technical evidence visible: charts, code snippets, schemas, architecture diagrams, metrics, logs, tables, and short quotes.
- Keep shapes crisp. Use 0-8px radii, 1px borders, and subtle shadows only when depth is functional.
- Build layouts that feel like documentation, benchmarks, and product UI meeting in one place.
- Use restrained motion. Small fades, row reveals, tab transitions, and chart updates are enough.
- Make the first viewport immediately say what the product is, who it is for, and what technical claim it makes.

## Visual Language

### Color

Use a mostly neutral palette:

- Background: `#ffffff`, `#fafafa`, `#f7f7f5`, or `#f4f4f2`
- Text: `#0a0a0a`, `#171717`, `#2a2a2a`
- Muted text: `#666666`, `#737373`, `#8a8a8a`
- Borders: `#e5e5e5`, `#d9d9d6`, `#cfcfca`
- Technical surfaces: `#111111`, `#181818`, `#f2f2ef`
- Accent: keep it sparse. Use a single amber, green, blue, or red only for status, links, chart lines, or callouts.

Avoid full-page dark navy, purple gradients, saturated marketing palettes, glassmorphism, bokeh, decorative mesh gradients, and color-coded chaos.

### Typography

- Use a neutral sans-serif: system stack, Inter, Geist, or similar.
- Use a mono font for technical labels, metrics, code, IDs, small caps, and diagrams.
- Keep letter spacing at `0` unless using tiny uppercase mono labels, where slight positive tracking is acceptable.
- Prefer tight, confident headings. Do not make every section hero-sized.
- Keep paragraphs compact and readable: 55-80 characters where possible.

### Layout

- Use full-width sections separated by thin horizontal rules.
- Favor grids, split rows, and editorial columns over floating card stacks.
- Align content to a visible system: 12-column grid, consistent gutters, and repeated baselines.
- Put real product artifacts in the layout: dashboard rows, query plans, database topology, benchmark charts, CLI output, API examples.
- Let wide desktop breathe, but keep information dense. Avoid giant empty marketing bands.
- On mobile, collapse into a clear reading order with the technical artifact still visible.

## Component Recipes

### Hero

- H1 should be literal and technical, not vague: "Managed Postgres for high-write workloads" beats "Scale without limits."
- Pair the claim with 1-2 concise paragraphs.
- Include primary and secondary actions, styled plainly.
- Add a technical artifact in the first viewport: chart, code block, table, query trace, ASCII topology, dashboard strip, or customer workload proof.
- Show a hint of the next section below the fold.

### Navigation

- Keep nav quiet: text links, thin separators, one restrained primary action.
- Use compact dropdowns or command-menu style menus for dense product/resource lists.
- Avoid oversized nav pills, glossy buttons, and heavy shadows.

### Buttons

- Primary: black or near-black background, white text, square-ish radius.
- Secondary: white/transparent with 1px border.
- Use icons only when they clarify the action.
- Keep sizes compact and consistent.

### Cards And Panels

- Use cards only for repeated items, framed tools, pricing tiers, quotes, or product screenshots.
- Avoid cards inside cards.
- Prefer thin borders, subtle background shifts, and simple headings.
- Each panel should contain concrete information, not generic feature blurbs.

### Technical Artifacts

- Code blocks should look like real code or CLI output, not decoration.
- Diagrams can use mono/ASCII styling, boxes, connecting rules, or simple SVG/canvas if needed.
- Charts should emphasize axes, labels, and comparative truth over visual flourish.
- Tables should be crisp, scannable, and useful.

### Copy Tone

- Write directly. Lead with the technical claim.
- Use concrete numbers and constraints when available.
- Avoid generic words like "seamless", "revolutionary", "next-gen", "beautiful", and "unlock your potential."
- Prefer proof: benchmarks, workload sizes, uptime, latency, cost, architecture, migration path, support model.

## Implementation Checklist

Before finishing a UI task with this skill:

- Replace generic decorative elements with technical artifacts or useful product evidence.
- Check the palette is mostly neutral and not dominated by a single trendy hue.
- Verify borders, spacing, radii, and typography are consistent.
- Confirm the page has at least one artifact that makes the product feel real.
- Confirm mobile layouts preserve hierarchy and do not hide the technical proof.
- Remove filler copy and feature descriptions that could belong to any SaaS product.
- Run the repo’s formatter/checks when available.

## Anti-Patterns

Do not use:

- Gradient blobs, decorative orbs, bokeh, glass panels, or neon glows.
- Huge rounded cards for every section.
- Purple-blue SaaS gradients as the default personality.
- Stock imagery that does not show the actual product, workflow, or domain.
- Oversized hero copy with no technical proof.
- Fake dashboards filled with meaningless numbers.
- Marketing copy that says nothing specific.
- Excess animation that competes with reading and scanning.
