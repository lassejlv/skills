# GPUI Kit Design Guides

The guide is [upstream/docs/design-guides.md](upstream/docs/design-guides.md). It is
a requirement, not inspiration. Read the guide file itself before doing UI
work. Do not answer from this page, from an existing screen in the codebase, or
from training data.

The complete guide is bundled here together with the
[Coding Guides](upstream/docs/coding-guides.md). No separate design skill is
required. The source snapshot, attribution, and refresh procedure are in the
[documentation index](upstream/index.md).

## How to read it

Read the whole guide for a new screen or a redesign. For a narrow change, read
"Design thesis" and "Start from the task" first, then the section for the
change. Sections, in order (`grep -n '^## ' upstream/docs/design-guides.md`):

| Section                              | Read when                                                              |
| ------------------------------------ | ---------------------------------------------------------------------- |
| Design thesis                        | Always                                                                 |
| Learning from Shadcn                 | Choosing what to borrow from web component libraries                   |
| Start from the task                  | Always; task hierarchy, interaction promise, what to leave out         |
| Visual language                      | Color, typography, spacing, radius, borders, elevation, density, icons |
| Layout patterns                      | Window structure, sidebars, toolbars, panels, forms, resizable regions |
| Components and composition           | Picking a component, composing parts, when to build a new one          |
| Interaction states                   | Hover, focus, pressed, selected, disabled, loading, validation, danger |
| Feedback and overlays                | Dialog, sheet, popover, menu, notification, tooltip, dismissal, focus  |
| Motion                               | Any animation or transition                                            |
| Designing data-heavy interfaces      | Tables, lists, trees, dashboards, dense inspectors                     |
| Interface language                   | Any user-facing text: labels, buttons, titles, errors, empty states    |
| Internationalization and platform fit | Multi-locale copy, Chinese terminology, macOS/Windows conventions     |
| Guidance for AI-generated interfaces | Always when an agent produces UI                                       |
| Accessibility checklist              | Before finishing                                                       |
| Design review checklist              | Before finishing; run every item against the work                     |

## Non-negotiables

A floor, not a substitute for the guide.

- **Desktop before web convention.** Keyboard access, window chrome, menus,
  dense data views, resizable regions, persistent navigation.
- **`Button` vs `Link`.** `Button` for every in-app command, `ghost` or
  `outline` when it should read quietly. `Link` only for external URLs and
  email addresses.
- **Tokens before values.** No raw hex or `rgb(...)`; use `cx.theme()`
  semantic tokens and rem-based helpers. Any spacing number quoted in the guide
  is the current default scale, not a literal to repeat.
- **State must be visible.** Hover, focus, selection, disabled, loading,
  validation, and destructive states each need distinct, consistent treatment.
- **Overlays.** Escape dismisses the topmost surface and returns focus to its
  trigger.
- **Copy.** Name the object and the verb: `Delete "Roadmap"?` with a `Delete`
  button, not `Are you sure?` with `OK`.

Finish by running the Design review checklist against the work.


> Adapted from [GPUI Kit Design Guides skill](https://github.com/longbridge/gpui-kit/blob/main/skills/gpui-kit-design-guides/SKILL.md), [Apache-2.0](https://github.com/longbridge/gpui-kit/blob/main/LICENSE). Merged 2026-09-28; cross-skill references now resolve within this package.
