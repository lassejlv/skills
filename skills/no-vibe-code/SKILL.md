---
name: no-vibe-code
description: Review frontend source and rendered UI for generic generated design patterns using the bundled static linter. Use for requests to remove AI-slop styling or a focused design-quality pass. Preserve intentional brand choices; this skill does not establish the primary visual direction.
---

# No Vibe Code

Find unintentional design defaults and replace them with choices grounded in the
product, content, and brief. Static matches are review candidates, not proof of
poor design or AI authorship.

## Establish intent and scope

Read the brief and inspect the existing design system and relevant UI. Preserve
requested colors, fonts, components, and reference fidelity. Use an available
design skill when the task needs a new visual direction; this skill works on its
own for a focused review.

For a review request, report findings without editing. For an implementation or
cleanup request, fix confirmed issues within the requested surface. Do not add a
CI gate or redesign unrelated screens merely because the linter finds a match.

## Scan the relevant source

Run the bundled [slop-check.mjs](slop-check.mjs) with Node 18 or newer; it has no
package dependencies. Resolve the skill directory and pass the driver by absolute
path so invocation works from the project's checkout:

```bash
node /absolute/path/to/no-vibe-code/slop-check.mjs ./src
```

The driver accepts multiple files or directories. Prefer the changed UI and shared
styles it uses; scan the whole frontend when the request covers it.

- `--json`: outputs `{files, counts, findings, failing}`.
- `--quiet`: prints only the summary and result.
- `--strict`: fails on MEDIUM as well as HIGH; use when that threshold is requested.
- Exit `0`: no matches at the selected failing severity. Exit `1`: matches need
  triage. Exit `2`: missing target arguments. Treat execution errors as incomplete
  scans, not design findings.

The scanner reads HTML, CSS, SCSS, JS, TS, JSX, TSX, Vue, Svelte, and Astro files.
It skips common dependency, generated-output, and coverage directories. Markdown
is not scanned. Missing paths can silently yield no files, and unknown flags are
not validated: check the command and file count. Zero files scanned is not a pass.

## Triage before changing the design

Each finding includes a rule ID, location, matched snippet, and suggested fix.
Review HIGH findings first, then MEDIUM and relevant LOW findings. Severity is the
tool's configured priority, not an objective measure of visual quality.

The rules flag patterns such as violet accents, purple-blue gradients, clipped
gradient text, Inter, emoji, repeated card grids, blur, and default tokens. Inspect
the match in context before applying its suggested fix:

- **Unintentional default:** change it to serve the content, hierarchy, and brief.
  Prefer a coherent palette, typography, and layout over isolated cosmetic swaps.
- **Intentional choice:** keep it when supported by the brief, design system, or a
  clear functional reason. Report the rule and reason if it remains at failing
  severity; do not claim the linter passed.
- **False positive:** leave valid code alone and explain the mismatch. The scanner
  uses text patterns, not a parser or rendered styles: comments, strings, body-copy
  emoji, and unrelated elements can match. Multiline or dynamic styles can escape
  detection.

Do not change brand colors, remove useful status indicators, replace a legible
font, or introduce asymmetry merely to clear a rule. Do not evade detection by
nudging colors or rearranging source. The driver has no suppression mechanism;
document justified exceptions in the result without changing its thresholds.

## Verify and finish

After edits, rerun the same scan and inspect the rendered result at relevant
viewport sizes. Check hierarchy, spacing, typography, contrast, and affected
interactive states. Run the project's relevant functional checks when markup or
behavior changes. If rendering is unavailable, disclose that the review was static.

Finish when confirmed issues in scope are resolved and remaining findings are
accounted for. Report changes or review findings, the actual lint result and file
count, any justified exceptions, and visual verification limits. A clean scan
alone does not establish design quality or accessibility.

When modifying the driver itself, run both regression fixtures:

```bash
node /absolute/path/to/no-vibe-code/slop-check.mjs /absolute/path/to/no-vibe-code/samples/slop.html --quiet
node /absolute/path/to/no-vibe-code/slop-check.mjs /absolute/path/to/no-vibe-code/samples/clean.html --quiet
```

The [slop fixture](samples/slop.html) must exit `1`; the
[clean fixture](samples/clean.html) must exit `0`. Check targeted cases for any
changed rule as well; these samples do not establish detector accuracy.
