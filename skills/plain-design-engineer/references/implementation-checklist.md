# Implementation Checklist

Run this before finalizing a frontend task with `plain-design-engineer`.

## Design

- Generic decorative elements were replaced with technical artifacts or concrete product evidence.
- The palette is neutral and not dominated by purple, blue gradients, beige, dark navy, or novelty accents.
- Borders, radii, typography, and spacing are consistent.
- Cards are used only for repeated items, framed tools, pricing tiers, quotes, or screenshots.
- There are no cards inside cards.
- Copy names the product, user, technical claim, and constraints clearly.
- The first viewport includes or strongly previews a real artifact.

## Responsive

- Mobile preserves the main hierarchy and at least one technical proof point.
- Tables either scroll horizontally or convert into compact rows.
- Code/log panels wrap or scroll without breaking layout.
- Buttons, nav, headings, and long words do not overflow.
- Hero content leaves a hint of the next section when this is a landing page.

## Implementation

- Reused local components, tokens, routing, and icon libraries where possible.
- Did not introduce a new design system unless needed.
- No decorative SVG hero illustration was added when product evidence would be better.
- Animations are restrained and do not block scanning.
- Dark technical panels have sufficient contrast.
- Images/assets render and are not cropped so hard that the product cannot be inspected.

## Verification

- Run the repo formatter/checks when available.
- Start the dev server for app/site changes when needed.
- Inspect desktop and mobile viewports.
- For interactive/canvas/3D work, verify the rendered surface is nonblank and framed correctly.
- In the final response, mention commands run and any verification not performed.
