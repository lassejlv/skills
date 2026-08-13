# Accessibility and platform behavior reference

Use this layer for roles, names, actions, keyboard and focus behavior,
accessibility preferences, typography, localization, and platform-specific
polish.

## Contents

- [Build semantics with behavior](#build-semantics-with-behavior)
- [Create stable accessible identity](#create-stable-accessible-identity)
- [Support keyboard and focus](#support-keyboard-and-focus)
- [Respect display preferences](#respect-display-preferences)
- [Use readable typography](#use-readable-typography)
- [Handle state and contrast](#handle-state-and-contrast)
- [Design for localization and input diversity](#design-for-localization-and-input-diversity)
- [Test accessibility](#test-accessibility)
- [Review checklist](#review-checklist)

## Build semantics with behavior

Accessibility is the control contract, not a label added after painting.
For every interactive element provide:

- role;
- accessible name;
- value/state where applicable;
- supported action;
- disabled/selected/expanded/checked state;
- keyboard path;
- visible focus;
- adequate hit target;
- deterministic reading/focus order.

Current GPUI builds accessibility information through AccessKit. In the current
source, an accessibility node needs a role, and action handling can be attached
with `.on_a11y_action(...)`. A click handler can register the accessible Click
action automatically, but that does not provide a correct role, name, state,
keyboard behavior, or focus style by itself.

Prefer the target project's accessible Button, Checkbox, TextField, Link, List,
Menu, and Dialog components. New primitives need screen-reader and keyboard
tests before broad reuse.

Do not put click handlers on anonymous layout containers when the element is
semantically a button or link.

## Create stable accessible identity

AccessKit node IDs must be stable and globally unique for the relevant tree.
Tie identity to domain data plus role:

```rust
.id(("project-row", project.id))
```

Do not use:

- render-order indices for reorderable rows;
- a static ID in a loop;
- random values created during render;
- localized text;
- transient pointer coordinates.

Current GPUI source warns that `text!` can derive identity from source location.
Calling the same macro expansion in a loop can duplicate accessibility IDs.
Give repeated text/row nodes explicit stable identity and inspect the resulting
tree.

When virtualizing, ensure recycled presentation does not make assistive
technology believe one row became another without identity change.

## Support keyboard and focus

Keyboard behavior should match platform expectations:

- Tab/Shift-Tab traverse actionable controls predictably.
- Space activates buttons/toggles where expected.
- Enter submits/defaults or activates according to role.
- Escape dismisses transient surfaces in the innermost-first order.
- Arrow keys navigate menus, lists, tabs, or segmented controls when the role
  calls for it.
- Command shortcuts are typed actions and scoped by key context.

Use GPUI focus handles and current focus/tab-stop APIs from the pinned checkout.
Focus is durable interaction state, not a border that appears on click.

Rules:

1. Give focus only to meaningful interaction targets.
2. Show focus visibly for keyboard navigation; avoid suppressing it globally.
3. Opening a dialog/menu moves focus to a meaningful initial target.
4. Closing it restores focus to the source when it still exists.
5. Disabling/removing the focused item moves focus predictably.
6. Do not trap focus outside modal scope.
7. Keep the focused item visible when scrolling or resizing.
8. Separate hover from focus; both can be true.

Current GPUI examples use focus tracking, tab stops, focus-visible styling,
actions, and key contexts. Copy a local working primitive rather than inventing
a raw key-down handler for every control.

## Respect display preferences

On macOS, `NSWorkspace` exposes accessibility display preferences and a
notification when they change, including:

- reduce motion;
- reduce transparency;
- increase contrast;
- differentiate without color.

GPUI currently has application reduced-motion state
(`App::reduce_motion`/`set_reduce_motion` in the research snapshot), and finite
`with_animation` integrates with it. Verify whether the target platform layer
already synchronizes OS preferences. If not, add one central observer rather
than querying AppKit in every component.

Map preferences:

| Preference | UI response |
|---|---|
| Reduce motion | Snap or short fade; remove parallax, bounce, large travel |
| Reduce transparency | Opaque material preserving hierarchy |
| Increase contrast | Stronger text/border/focus separation |
| Differentiate without color | Add icon, label, shape, stroke, or pattern |

Update live when the OS changes. Clean up native notification observers with
their owner.

On other platforms, use their supported preference/settings APIs or explicit
application settings. Do not hardcode macOS preferences as universal.

## Use readable typography

Apple's macOS guidance uses the system typeface and role-appropriate text
styles. A common regular body size is 13 pt; Apple advises avoiding text below
10 pt. Treat these as platform guidance, not a command to set every label to 13.

Rules:

- use system font roles for native-feeling macOS UI;
- preserve the user's scaling/zoom preference where the app provides one;
- maintain readable line height and measure;
- do not encode hierarchy by size alone;
- test real font availability and weights;
- avoid ultra-light text on translucent material;
- keep placeholder/secondary text distinguishable but readable;
- allow labels to expand for localization;
- verify high-DPI text and baseline alignment.

macOS does not use iOS Dynamic Type in the same way. Desktop apps should still
support app/system text scaling where applicable and avoid layouts that break
when text grows.

## Handle state and contrast

Every state must remain perceivable:

- default;
- hover;
- pressed;
- focused;
- selected/checked;
- disabled;
- invalid/error;
- loading/busy;
- active/inactive window.

Do not encode selected versus unselected only through subtle alpha or hue.
Pair color with at least one of shape, icon, stroke, text, or position.

Disabled controls should remain identifiable and legible. Do not reduce opacity
so far that their label disappears. Expose disabled state semantically and
prevent all activation paths.

Focus rings must not be clipped by parent overflow. Make them visible over both
solid and glass materials.

For content over dynamic/translucent backgrounds, evaluate the worst background
state. Native material adaptation helps but does not absolve the app from
choosing readable text and fallback.

## Design for localization and input diversity

- Keep strings out of geometry and identity.
- Expect 30–100% expansion for labels depending on language.
- Avoid fixed-width buttons that clip translated text.
- Mirror directional layout/icons for right-to-left locales where semantic.
- Do not mirror universal media controls or brand marks blindly.
- Use locale-aware formatting for numbers, dates, and pluralization.
- Preserve mnemonic/shortcut conventions for each platform.
- Provide text alternatives for icons.

Support pointer, trackpad, keyboard, and touch according to target hardware.
Hover must not reveal the only route to an action. Tooltips supplement labels;
they do not repair an unlabeled control for assistive technology.

Hit targets should be comfortably operable even when the visual glyph is
compact. Keep adjacent destructive controls separated. Use the target product's
desktop sizing conventions rather than importing mobile dimensions wholesale.

## Test accessibility

### Static and unit checks

- stable IDs for looped/reordered items;
- state-machine coverage for disabled/selected/expanded/error states;
- semantic label construction;
- preference-to-theme/motion mapping;
- localization expansion.

### GPUI tests

- Tab order and focus-visible state;
- keyboard activation;
- Escape/dismissal and focus return;
- action routing in nested key contexts;
- disabled controls ignore pointer, keyboard, and accessibility activation;
- list navigation and selection;
- reduced-motion behavior where test support exposes it.

### Runtime checks

On macOS, use VoiceOver and Accessibility Inspector:

1. Navigate without a mouse.
2. Confirm role, name, value, state, and actions.
3. Confirm reading order matches visual order.
4. Open and dismiss overlays.
5. Reorder/virtualize lists and confirm identity.
6. Toggle Reduce Motion, Reduce Transparency, Increase Contrast, and
   Differentiate Without Color while the app runs.
7. Test light/dark and active/inactive windows.
8. Increase app text/zoom settings.

Repeat with platform assistive technologies on every supported OS available.
Report unverified paths.

## Review checklist

- [ ] Every control has correct role, name, state, and action
- [ ] IDs are stable and globally unique
- [ ] No repeated `text!` source-location identity
- [ ] Full keyboard path and visible focus
- [ ] Overlay focus scope and restoration
- [ ] Disabled state blocks all activation paths
- [ ] Reduced motion/transparency and contrast preferences mapped
- [ ] Meaning does not depend on color or motion alone
- [ ] Typography remains readable and expandable
- [ ] Screen-reader/runtime testing performed

See [sources.md](sources.md) for GPUI, AccessKit, and Apple primary sources.
