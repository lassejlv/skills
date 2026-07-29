# Visual Language

Use these values as a calibration range, not a mandatory theme. Map them into the target project's tokens.

## Palette

### Dark

```css
--page: #0d0d0d;
--surface: #111111;
--text: #e7e7e7;
--muted: #9a9a9a;
--rule: #727272;
--rule-strong: #b8b8b8;
--link: #00a9ef;
--action: #ff4f00;
```

### Light

```css
--page: #fbfbfa;
--surface: #ffffff;
--text: #171717;
--muted: #6f6f6f;
--rule: #c9c9c6;
--rule-strong: #8e8e8a;
--link: #4f7fc8;
--action: #ee4b16;
```

Use one link accent consistently. Reserve the action color for the main CTA or a small section marker. Check WCAG contrast after mapping colors.

## Type

Start with the project's licensed mono. If none exists:

```css
font-family:
  ui-monospace,
  "SFMono-Regular",
  "Cascadia Code",
  "Roboto Mono",
  Menlo,
  Consolas,
  monospace;
```

Suggested scale:

```css
--text-xs: clamp(0.75rem, 0.72rem + 0.12vw, 0.8125rem);
--text-sm: clamp(0.875rem, 0.83rem + 0.18vw, 1rem);
--text-body: clamp(1rem, 0.94rem + 0.24vw, 1.1875rem);
--text-lead: clamp(1.125rem, 1rem + 0.42vw, 1.5rem);
--text-title: clamp(1.5rem, 1.15rem + 1.25vw, 2.75rem);
```

- Set body line height to `1.55-1.75`.
- Set headings to `1.1-1.3`.
- Use `600-700` for claims and section labels; keep body text at `400`.
- Use underlines for linked or navigational headings.
- Avoid all-caps paragraphs. Short labels may use caps only when the brand already does.
- Keep line length around `60-90ch`; broad technical sections can reach `100ch`.

## Grid and spacing

```css
.shell {
  width: min(calc(100% - 2rem), 88rem);
  margin-inline: auto;
}

.section {
  padding-block: clamp(3rem, 7vw, 7rem);
}

.prose {
  max-width: 88ch;
}
```

- Use `16-32px` mobile gutters and `32-64px` desktop gutters.
- Anchor all major content to one shell.
- Repeat a small spacing set such as `8, 12, 16, 24, 32, 48, 72, 112`.
- Prefer large gaps between sections and compact gaps inside related copy.
- Do not center every section. Left alignment is the default.

## Rules

- Use `1px solid` rules for grids, tables, navigation divisions, and customer matrices.
- Use `1px dashed` or a spaced dotted rule between editorial chapters.
- Keep border color quiet enough that content leads.
- Avoid doubled grid borders with shared parent borders or negative margins.
- On high-density displays, verify dashed rules remain visible without becoming bright decoration.

Example chapter divider:

```css
.chapter + .chapter {
  border-top: 1px dashed var(--rule-strong);
}
```

## Navigation

- Keep the nav one row on desktop.
- Separate groups with thin vertical rules.
- Use a compact logo, then primary links, then account and CTA actions.
- Make the primary CTA rectangular with little or no radius.
- Hide lower-priority links behind an accessible menu on narrow screens.
- Give every control a minimum `44px` touch target even when the visible treatment is compact.

## Opening section

Prefer a compact claim over a giant promotional H1:

```text
Infrastructure that survives the boring failures.

Run production workloads across regions with automatic failover,
observable deploys, and no proprietary runtime.

Read the architecture →
```

Use a short colored rule, caret, or bracket as the only decorative marker. Follow the opening with concrete proof.

## Product table

Use a semantic `<table>` for products, pricing, benchmark results, or plan comparisons.

- Keep 2-4 meaningful columns.
- Use rules rather than tinted cards.
- Make the entire row scannable; align numeric content.
- On mobile, allow horizontal scroll with a visible edge cue or convert each row into labeled fields.

## Customer or ecosystem matrix

- Use CSS grid with shared 1px borders.
- Normalize logo boxes, not logo artwork: preserve each mark's aspect ratio.
- Use authorized SVGs or text names. Never extract marks from the reference screenshot.
- Keep each cell generous and visually equal.
- Prefer 5 columns on wide layouts, 3 around tablet, and 2 on mobile.
- Include accessible names for every logo.

## Editorial chapters

Use chapters for reliability, security, performance, cost, migration, or architecture:

- Underlined section label.
- Two or three evidence-rich paragraphs.
- Linked bullet list using `*`, `→`, or `+` markers.
- Optional quote with a single left rule and muted attribution.
- Dashed divider before the next chapter.

Do not turn each chapter into a rounded card.

## Footer

Build the main footer as a bordered grid:

- 4-6 link columns on desktop.
- Underlined bold group headings.
- Compact vertical link rhythm.
- A legal row inside the enclosing border.
- A separate social row below.
- On mobile, use 1-2 columns and preserve the dividers.

Keep legal text muted but readable. Use the current year dynamically where the framework supports it.

## Light and dark selection

Choose one strong default based on product identity:

- Use light for documentation-forward, open, or minimal products.
- Use dark for infrastructure, terminal-adjacent, or high-contrast technical products when it fits the brand.
- Support both only if the existing product already has a reliable theme system or the user asks for it.

Do not invert the screenshots mechanically. Re-check all border, link, muted text, logo, and focus colors in the chosen theme.
