# Implementation and QA

## Implementation workflow

1. Identify the route entry, layout shell, component primitives, global styles, font loading, and breakpoint system.
2. Inventory existing public copy and product evidence before rewriting.
3. Sketch the section order using plain text.
4. Define or map a minimal token set: page, surface, text, muted, rule, link, action, shell width, type scale, and spacing.
5. Build semantic structure first: header, nav, main, sections, tables/lists/figures, and footer.
6. Add the shared shell and rule system.
7. Add responsive behavior before visual polish.
8. Add only small interaction states after the static hierarchy works.
9. Render, compare, and tighten.

Preserve the target project's framework. Do not introduce a new UI library just to produce borders, grids, or typography.

## Component boundary

Extract a component when it repeats, owns behavior, or encodes a stable content model. Useful boundaries include:

- `SiteHeader`
- `AnnouncementBar`
- `EditorialSection`
- `ProofTable`
- `CustomerGrid`
- `Quote`
- `RuledFooter`

Avoid wrappers such as `Card`, `SectionCard`, and `FeatureCard` when they add only a rounded rectangle.

## Semantic recipes

### Ruled grid without doubled borders

```css
.ruled-grid {
  display: grid;
  border-block-start: 1px solid var(--rule);
  border-inline-start: 1px solid var(--rule);
}

.ruled-grid > * {
  border-inline-end: 1px solid var(--rule);
  border-block-end: 1px solid var(--rule);
}
```

### Mobile-safe table

```css
.table-scroll {
  overflow-x: auto;
  overscroll-behavior-inline: contain;
  scrollbar-gutter: stable;
}

.table-scroll table {
  min-width: 44rem;
  width: 100%;
  border-collapse: collapse;
}
```

Wrap the region with an accessible label when the table's caption is not sufficient.

### Crisp focus

```css
:where(a, button, input, select, textarea):focus-visible {
  outline: 2px solid var(--link);
  outline-offset: 3px;
}
```

Never remove focus outlines without a replacement.

## Copy rules

- Lead with a product truth, not a mood.
- Name the user, workload, or constraint.
- Prefer verbs such as deploy, inspect, route, query, migrate, recover, and measure.
- Pair every large claim with proof nearby.
- Use exact units and conditions for benchmarks.
- Explain unfamiliar technical terms once.
- Keep CTAs direct: `Read the docs`, `View benchmarks`, `Start a project`, `See pricing`.

Reject copy such as:

- “Revolutionize your workflow.”
- “Unlock limitless possibilities.”
- “The future of innovation is here.”
- “Seamlessly supercharge your stack.”

## Visual QA

Render at minimum:

- `1440x1000` desktop
- `1024x768` compact desktop/tablet
- `390x844` mobile

Check:

- The first viewport states the product and shows or leads directly to proof.
- Major left edges align.
- Body copy does not become an unreadably wide wall.
- Navigation does not wrap.
- Rules meet cleanly with no accidental 2px seams.
- Dashed dividers are structural, not visual noise.
- Tables and proof grids remain usable on mobile.
- Logos keep aspect ratio and accessible names.
- No horizontal page overflow exists.
- Link, muted text, borders, and focus states pass contrast requirements.
- Text remains usable at 200% zoom.
- Reduced-motion mode removes nonessential animation.

## Functional QA

- Exercise all navigation, CTA, menu, pricing, and external links.
- Verify heading order and one primary page heading.
- Verify landmarks and skip navigation.
- Verify keyboard-only use, menu dismissal, and focus return.
- Verify images have meaningful alternatives or are intentionally decorative.
- Verify analytics and forms still work after a redesign.
- Run formatter, lint, typecheck, tests, and production build at the project's normal scope.

## Design review output

When reviewing without editing, report:

1. The three highest-impact mismatches.
2. The specific component or section affected.
3. Why it weakens the technical-document system.
4. A concrete change with token, spacing, or layout guidance.
5. Any claim, accessibility, or responsive risk.

Do not reduce the review to “make it more minimal.” Name the broken relationship.
