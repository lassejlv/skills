---
name: use-design-system
description: Create or evolve an app design system from a brief, existing app or repo, screenshots, website, or design file. Use for reusable foundations, semantic tokens, components, states, and usage patterns on a dedicated design-system page. Defaults to Paper, then Figma, and asks questions when missing details affect the result. Not for a single screen mockup or implementation-only task.
---

# Use Design System

Turn what the user points to into a coherent, editable system that another designer or agent can use to build the app consistently. Deliver the actual design artifact, with reusable foundations, component contracts, and examples in context. Scale the system to the product; a large component catalog is not evidence of quality.

Work in this order: understand the source, resolve important gaps, choose the destination page, establish foundations, prove a representative app pattern, expand component coverage, inspect the result, and hand it over. Fix shared decisions before multiplying specimens.

## 1. Understand the starting point

Resolve links, attachments, selected objects, paths, and phrases such as “this app” from the conversation. Inspect the referenced material before asking the user to describe information already available there.

| Starting point | Inspect and derive |
| --- | --- |
| Existing app or repo | Representative screens and flows, existing tokens/components, repeated visual rules, platform conventions, and inconsistencies. Read code without changing the app. |
| Design file or selected frame | Page structure, foundations, styles/variables, components, states, and existing system documentation. Reuse sound work. |
| Website or live reference | Rendered styles and relevant interactions; distinguish a source to preserve from inspiration to adapt. |
| Screenshots | Visible hierarchy, geometry, colors, type, and component families. Label estimates and proposed unseen states. |
| Product brief or idea | Users, primary tasks, target platform, content density, brand constraints, and the component families those tasks need. |

Write a short working brief: product and users, platforms/input methods, key flows, visual direction, required themes, source role, scope, and destination. It can live in your working notes and become the page's introduction; do not create a separate planning document unless useful or requested.

For an existing app, preserve its identity and consolidate repeated rules by default. Separate observed rules from proposed corrections; do not canonize an accidental inconsistency. For inspiration, transfer useful design principles while adapting structure and content to the user's product. A design-system task does not authorize a product redesign or code implementation.

For an update, inspect the existing system's canonical definitions and usage before making changes. Work on the gaps in the request; preserve stable names, page/object identities, and working instances where possible. Do not rebuild the whole system or create a second system page just because it is easier to start over. Document changes that affect consumers; avoid silently repurposing a token or variant they already use.

## 2. Ask questions that change decisions

Ask when inspection cannot resolve something that would materially change the result. Prefer a small batch of concise questions with a recommended option when one is sensible. Typical gaps are:

- What the app does and who uses it, when no product context can be found.
- Desktop, web, or mobile, when the answer changes navigation, sizing, or input behavior.
- Preserve the source faithfully, consolidate it, or develop a new direction, when the user's intent is ambiguous.
- An unresolved destination file/team, conflicting brand requirements, or a theme requirement that affects the whole system.

Do not repeat supplied information, ask the user to pick every token, or require a questionnaire before inspecting the source. Choose routine details using the brief and state consequential assumptions. Use the available question tool or conversation; continue independent inspection while waiting, but defer work that depends on a required answer. Do not treat silence as acceptance of a consequential choice.

If the brief is sufficient, proceed. A request to create the system is authorization to do the scoped design work; do not insert approval gates for each phase. Ask again only when a newly discovered conflict or missing choice matters.

## 3. Choose the design app and its own page

An explicit app or destination takes precedence over defaults. A reference in Figma does not by itself make Figma the destination; distinguish source links from instructions to edit that file.

Apply the fallback order below only when the destination is not pinned by the user. If an explicitly chosen app/file cannot be edited, explain the missing capability and ask before changing destinations. Check whether existing native features can be used through another supported interface before declaring the app unusable.

1. Discover available design integrations and their documented capabilities. Prefer native design tools, then supported UI automation. Check both access and the ability to create/edit, rather than merely the presence of a connector.
2. **Use Paper by default.** If Paper is unavailable or cannot perform the required editing, try Figma. A read-only Figma integration does not fulfill a creation task; check for supported editing through another available interface.
3. If neither is usable, discover other available design apps, recommend a workable option, and ask the user to resolve the destination when necessary. Continue source analysis and drafting specifications. Do not silently substitute a report, static image, or HTML playground for the requested editable design system. Do not install tools or move the user's existing work just to satisfy a default.
4. Resolve the intended file and workspace/team before writing. Use the user's target file when supplied; otherwise create a dedicated file in an unambiguous destination. Ask only if choosing would guess between plausible targets.
5. **The system must have its own page inside that file.** In Paper this means an actual Paper page; in Figma, a Figma page. Name it `Design System` or `<App Name> / Design System`. A similarly named artboard, frame, or group is not a page.
6. Inspect the pages first. Update the existing system page when it is clearly the intended system; otherwise create one. Put foundations, components, usage notes, and composed examples together on that page, arranged into readable artboards/frames. Keep product-screen pages separate and preserve unrelated work.

Read the live tool guide/schema before unfamiliar operations. Do not bake in remembered tool names, connection details, or API syntax. When library/CLI documentation is needed, use the current documentation workflow required by the workspace.

If access remains blocked, identify the exact missing capability and deliver any useful draft as provisional. Do not claim an editable system or dedicated page exists until it has actually been created and verified.

## 4. Establish the system's foundations

Read [references/system-spec.md](references/system-spec.md) when defining tokens, component contracts, and usage documentation. Use it as a specification model, not a requirement to create every listed family.

Choose a small set of product-specific principles, such as information density, emphasis hierarchy, or platform feel. Make each principle affect a visible decision. Avoid automatically applying a fashionable visual style unrelated to the source or brief.

Define the foundations the app needs:

- Color roles for surfaces, text, borders, actions, selection, focus, and meaningful statuses.
- Typography roles with available fonts, size, weight, line height, and fallback behavior.
- Spacing and sizing rules, content widths, layout behavior, and density appropriate to the platform.
- Radius, borders, elevation, and icon conventions with clear roles.
- Interaction and motion rules, including keyboard focus, touch behavior when relevant, and reduced motion.

Use semantic token names such as `color/text/secondary` and `color/action/primary/background`. Keep base values distinct from semantic roles; alias repeated values where supported. Add component-specific tokens only when a component needs a real exception. Themes should change semantic values while preserving role names and component contracts. Build only the themes and densities required by the brief.

Use native shared tokens/variables/styles and bind specimens where supported. Verify that bindings exist; labels beside hardcoded swatches are not shared tokens. Where the app lacks binding or alias support, maintain an explicit canonical token table and document that limitation. Keep artwork and that table consistent.

Check font and asset availability early. Use editable vector icons where possible, with a coherent source, size, stroke, and alignment. State material substitutions. Never conceal an estimated measurement as an exact extraction.

## 5. Build components and patterns

Create a compact coverage inventory from the key flows, recording each needed family, its use, whether to reuse or build it, required states, and completion/verification status. Prioritize the app's actual controls, navigation, forms, feedback, and content/data patterns. Include their meaningful variants and states; do not fill the page with unrelated components or every possible state combination.

For each family, define its purpose, anatomy, semantic tokens, sizes/variants, relevant states, behavior, and usage guidance. Cover default, focus, disabled, loading, selected, error, or open states where meaningful. Avoid hover-only instructions for touch interfaces. Show realistic content, long labels, and useful empty/loading/error cases.

Use reusable native components, variants, and instances where the design app supports them. Otherwise create consistently named, editable, grouped specimens that are easy to duplicate and explicitly identify them as specimens. Do not claim linked instances or playable interactions that the artifact cannot provide.

Before expanding the catalog, build a small working set of shared components and compose one representative app pattern: for example, a settings form, searchable list/detail view, or mobile navigation flow. Inspect it at normal app scale and a relevant constrained size to check hierarchy, density, typography, action emphasis, and content growth. Correct shared foundations and component contracts before copying those decisions across the system. Ask about the direction only if an unresolved choice would materially change this work; the pilot is not a mandatory approval gate.

Expand the required families and additional useful patterns from that proven base. Include only patterns that fit the product. These examples belong on the system page and demonstrate how the system works together.

Document decisions beside the relevant specimen: when to use a variant, which action receives emphasis, how labels/errors behave, and how layout responds to available space. Specify responsive behavior with resizing, wrapping, or reflow rules, not just a collection of fixed-width screenshots.

Keep annotations visually separate from specimens. Organize the page from overview and foundations to component families, composed patterns, and usage notes. Use clear layer names such as `Button / Primary / Loading`; board count and page decoration are not goals.

Add a compact **Start here** index at the top of the page pointing to canonical tokens/styles, component definitions, and app patterns. Use verified object links or identifiers where supported. Make it clear which definitions to reuse and how to extend a missing rule; another agent should not need to reverse-engineer the examples to build the next screen.

## 6. Inspect and deliver

Inspect rendered views of every completed section, including representative normal and constrained sizes. Fix clipping, missing fonts, misaligned icons, inconsistent token use, unreadable documentation, and weak hierarchy before delivery.

Verify:

- The system is on its own real page in the intended file, and the page can be reopened.
- Foundations, component values, and composed examples agree; native bindings/instances work where claimed.
- The coverage inventory matches the product's scoped flows and required states/themes.
- Measure representative text/background and required control/focus/surface color pairs, including changed states and themes. Record the actual contrast ratio, applicable target, and pass/fail result; fix failures. Check visible focus, non-color status cues, target sizing, and content growth for the platform. Use the evidence format in [references/system-spec.md](references/system-spec.md); if measurement is unavailable, label the check unverified.
- Documented keyboard, focus, dismissal, validation, and reduced-motion behavior is clear. Test it when an interactive prototype exists; static state boards establish specifications, not working behavior.
- Proposed rules, estimates, substitutions, unsupported native features, and unverified interactions are labeled precisely.

Use computed values and visual inspection together. Do not claim an accessibility audit or runtime validation from design screenshots alone.

Verify native reuse through binding/instance metadata and resolved styles. If propagation needs a behavioral check, create an isolated disposable copy of the token/component with linked test specimens, change only that copy, inspect the dependent instances, and remove the test. Do not edit canonical definitions just to test them. When only grouped specimens are supported, verify their documented shared values and state that automatic propagation is unavailable.

Deliver a direct link to the file and system page when available, summarize the included foundations/components/patterns, and state material gaps. Verify link or page identifiers rather than inventing a page URL. Token exports or implementation mapping are optional when requested or useful; changing the app's code or publishing a shared library requires that scope from the user.
