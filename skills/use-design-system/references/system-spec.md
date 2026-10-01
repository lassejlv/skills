# Design-system specification model

Use this reference while defining the foundations and component contracts. Adapt it to the product; omit sections that have no purpose in the agreed scope. Put the useful documentation on the dedicated design-system page beside the editable artwork.

## Page introduction

Keep a short introduction that lets the next designer or agent understand:

- Product, users, platforms, main tasks, and supported themes/densities.
- Source links and whether the system preserves, consolidates, or reinterprets them.
- A few design principles tied to decisions, for example “Dense lists keep metadata aligned and reserve accent color for the primary action.”
- Scope, important assumptions, and where the canonical tokens/components live.

Provide a small **Start here** index with the canonical definition locations and a reuse recipe: choose semantic roles, use an existing component and appropriate variant, then follow a documented layout pattern. If something is missing, extend the relevant family or semantic role and update its usage notes rather than creating a parallel convention. For updates, briefly identify consumer-facing changes and the replacement for any deprecated definition.

Distinguish **observed**, **proposed**, and **estimated** rules when deriving a system from an existing source. Make unresolved choices visible rather than scattering competing defaults through the page.

## Foundations and token records

Use a canonical record with these fields, whether it lives in native variables or a visible specification table:

| Field | Meaning |
| --- | --- |
| Name | Stable role-based identifier; use one naming convention throughout. |
| Type and value | Exact color, dimension/unit, font property, duration, or other supported value. |
| Alias | Reference to the shared base or semantic token, when supported. |
| Theme/mode | Values or aliases for each required theme; omit unnecessary modes. |
| Use | What the token controls and any important restriction. |
| Evidence | Observed value, estimate, or proposed decision when source fidelity matters. |

Useful roles, selected according to the app:

| Foundation | Specify |
| --- | --- |
| Color | Canvas, surface levels, primary/secondary text, borders, action emphasis, focus, selection, success/warning/danger; foreground/background pairs for states. |
| Typography | Display/title/body/label/caption/data roles, family/fallback, weight, size, line height, tracking; wrapping and truncation where needed. |
| Space and size | A coherent spacing scale, control heights, icon sizes, content constraints, touch targets, and compact/comfortable density if required. |
| Layout | Shell regions, alignment, container width, resizing/reflow rules, and platform-relevant breakpoints; artboard widths are examples, not breakpoint definitions. |
| Surface treatment | Radius by role, border weight, shadow/elevation purpose, overlays, and stacking relationships. |
| Icons | Source, vector availability, sizes, stroke/fill convention, optical alignment, and labeling of icon-only actions. |
| Motion | Trigger, affected properties, duration/easing, interruption/dismissal behavior, and reduced-motion equivalent. |

Example relationships, using values chosen for this product:

```text
base/neutral/900                       = <exact color>
color/text/primary [light]             -> base/neutral/900
color/action/primary/background        -> base/brand/600
color/action/primary/foreground        = <verified readable color>
color/action/primary/background/hover  -> base/brand/700
space/control/inline                   -> base/space/3
```

These illustrate naming and alias relationships, not a prescribed palette or API/export format. Composite type styles may need native text styles instead of individual variables. Verify the destination's representation rather than claiming unsupported token types.

Avoid naming a reusable token after one screen, creating identical aliases without a semantic purpose, or encoding theme names into role names when the tool supports modes. Add an exception only when you can explain why the shared rule fails.

## Component contract

For each reusable family, record enough to recreate and choose it correctly:

| Part | Questions the contract answers |
| --- | --- |
| Purpose and anatomy | What task does it serve? What are its parts and slots? |
| Variants | What meaning separates variants? Which is the default? |
| Size and layout | Heights, padding, gaps, widths, alignment, content growth, and density differences. |
| Tokens | Which semantic roles control text, surface, border, focus, and state changes? |
| States | Relevant resting, hover, pressed, focus, selected, disabled, loading, validation, expanded/open states. |
| Behavior | Trigger, keyboard/touch behavior, dismissal, focus placement/return, and loading/error effects where relevant. |
| Content | Labels, help/error text, icon rules, localization growth, truncation, and empty values. |
| Usage | When to choose it, common misuse, and how it combines with adjacent components. |
| Artifact support | Native definition/instance or editable specimen; static specification or tested prototype. |

A compact contract example:

```text
Button / Primary
Use: the main action in an action group; choose a quieter variant for secondary actions.
Anatomy: optional leading icon, action label, optional loading indicator.
Geometry: height/padding/radius from the shared control tokens; label grows naturally.
States: default, hover for pointer input, pressed, visible keyboard focus, disabled, loading.
Loading: keep width stable and prevent repeated activation; specify how progress is announced.
Content: describe the action; icon-only versions need an accessible name.
Bindings: identify the actual semantic tokens and native definition, if supported.
```

Use a state matrix when it makes coverage clearer. Show meaningful differences rather than drawing a full Cartesian product of sizes, themes, and states. A label saying “disabled” does not replace a visibly disabled specimen.

## Choosing families from app tasks

| Product need | Likely reusable families and patterns |
| --- | --- |
| Navigation | App shell, tabs/sidebar, breadcrumbs or back behavior, selected state, overflow. |
| Settings or data entry | Labels, fields, selects/toggles, help/validation, save action group, unsaved changes. |
| Finding and inspecting records | Search, filters, list/table, row selection, detail panel, pagination or incremental loading. |
| Status and background work | Badges, inline feedback, notifications, progress, skeletons, empty/error/retry states. |
| Focused or destructive decisions | Menu/popover/dialog, action hierarchy, confirmation text, focus and dismissal rules. |
| Mobile tasks | Touch controls, navigation, safe-area/layout rules, keyboard effects, overflow and content growth. |

This is a routing aid, not a universal component checklist. Domain-specific components often matter more than adding another generic card variant.

## Prove the system in context

Compose a small set of representative product patterns using the documented components. Use realistic synthetic content and include a constraint that can expose a weak rule, such as a long label, dense row, narrow container, error message, or empty result.

Check that a new screen can be assembled without inventing another palette, type scale, spacing convention, or action hierarchy. If the example needs a justified new rule, update the canonical foundation or component contract before finishing the pattern.

## Verification evidence

Keep a concise verification note on the system page. Capture useful evidence, not a claim that all accessibility or runtime behavior has been validated.

| Check | Evidence to record |
| --- | --- |
| Contrast | Foreground/background tokens and resolved values, theme/state, text size/weight or control role, measured ratio, applicable target, and pass/fail. Include alpha compositing where it affects the actual background. |
| Layout/content growth | Pattern, viewport/container size, long or translated content tested, and clipping/reflow outcome. |
| Native reuse | Canonical token/component identity, confirmed binding/instance metadata and resolved values; if propagation was tested, isolated copied definition, linked test specimen, observed change, and removal of the test. |
| Interaction | What was actually exercised in a prototype versus specified only on static boards; record important remaining gaps. |
| Coverage | Required family/state/theme, its canonical location, and whether it was built and visually checked or remains open. |

Use the applicable accessibility standard or platform guidance to choose targets; consult current authoritative documentation when those requirements are unclear. A ratio alone does not establish compliance. Similarly, a native component name does not prove that its specimens are linked instances.

For an update, include representative affected consumers in the scoped check. Avoid deleting old components or breaking unrelated instances as part of an unrequested cleanup.
