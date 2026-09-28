---
url: /base/primitives.md
description: The complete catalog of user-facing gpui-base primitives.
---

# Primitives

GPUI Base primitives provide behavior without prescribing presentation. Each page documents the public import and the smallest useful composition. The live example above the page is built from `crates/base/examples` and can also run as a native GPUI application.

## Primitive catalog

- [Accordion](https://gpui-kit.com/base/accordion.md) — A disclosure group composed from independently styleable header, trigger, and panel parts.
- [Alert Dialog](https://gpui-kit.com/base/alert-dialog.md) — A modal confirmation surface for actions that need an explicit decision.
- [Avatar](https://gpui-kit.com/base/avatar.md) — An image with composable fallback content for a person or entity.
- [Button](https://gpui-kit.com/base/button.md) — An unstyled, accessible pressable with semantic state and keyboard activation.
- [Calendar](https://gpui-kit.com/base/calendar.md) — A state-driven date grid with selection matchers and custom item rendering.
- [Checkbox](https://gpui-kit.com/base/checkbox.md) — A controlled tri-state check control with a separately styled indicator.
- [Collapsible](https://gpui-kit.com/base/collapsible.md) — A composable region that shows or hides content without prescribing its trigger styling.
- [Color Picker](https://gpui-kit.com/base/color-picker.md) — State and interaction foundations for selecting colors in a custom picker UI.
- [Combobox](https://gpui-kit.com/base/combobox.md) — A text input paired with keyboard-navigable suggestions and selection behavior.
- [Date Picker](https://gpui-kit.com/base/date-picker.md) — A focus-aware date input that composes calendar behavior with a popup.
- [Dialog](https://gpui-kit.com/base/dialog.md) — A composable modal surface with focus management, backdrop, title, and close parts.
- [Hover Card](https://gpui-kit.com/base/hover-card.md) — A delayed floating card associated with a pointer or keyboard trigger.
- [Input](https://gpui-kit.com/base/input.md) — A single-line text input with selection, masking, validation, and number stepping.
- [Textarea](https://gpui-kit.com/base/textarea.md) — A multi-line text field with fixed rows, wrapping, and auto-grow behavior.
- [Editor](https://gpui-kit.com/base/editor.md) — A source-code editor foundation with highlighting, gutter, folding, decorations, and LSP hooks.
- [Link](https://gpui-kit.com/base/link.md) — An accessible link-like control with application-defined styling.
- [Nav Stack](https://gpui-kit.com/base/nav-stack.md) — A navigation stack of views with push, pop, forward, and replace, and an animatable transition lifecycle.
- [Number Input](https://gpui-kit.com/base/number-input.md) — A numeric input with reusable increment, decrement, and step behavior.
- [OTP Input](https://gpui-kit.com/base/otp-input.md) — A multi-cell one-time-code input driven by a shared text state.
- [Pagination](https://gpui-kit.com/base/pagination.md) — A controlled page navigator with explicit current and total page state.
- [Popover](https://gpui-kit.com/base/popover.md) — An anchored floating surface with controlled or internally managed open state.
- [Popup](https://gpui-kit.com/base/popup.md) — A low-level trigger and anchored floating-content host.
- [Progress](https://gpui-kit.com/base/progress.md) — Composable track and indicator parts for reporting task completion.
- [Radio](https://gpui-kit.com/base/radio.md) — A controlled single-choice item with selectable and disabled semantics.
- [Radio Group](https://gpui-kit.com/base/radio-group.md) — Groups radio items and provides keyboard navigation for a single selection.
- [Resizable](https://gpui-kit.com/base/resizable.md) — Panel groups and resize handles for user-adjustable split layouts.
- [Scrollbar](https://gpui-kit.com/base/scrollbar.md) — An unstyled scrollbar connected to GPUI scroll or uniform-list handles.
- [Select](https://gpui-kit.com/base/select.md) — A button-like selection control backed by an anchored, keyboard-navigable popup.
- [Sheet](https://gpui-kit.com/base/sheet.md) — A modal surface that enters from an edge while managing dismissal and focus.
- [Slider](https://gpui-kit.com/base/slider.md) — A state-driven range input with independently styleable track, indicator, and thumb.
- [Switch](https://gpui-kit.com/base/switch.md) — A controlled on/off control with separately styleable track and thumb.
- [Table](https://gpui-kit.com/base/table.md) — Semantic table primitives for composing headers, bodies, rows, and cells.
- [Tabs](https://gpui-kit.com/base/tabs.md) — A tab list and accessible tab controls with controlled selection.
- [Time Field](https://gpui-kit.com/base/time-field.md) — A segmented time-of-day editor with a complete keyboard model and 24- or 12-hour clocks.
- [Toast](https://gpui-kit.com/base/toast.md) — A managed, animated stack of temporary status messages.
- [Toggle](https://gpui-kit.com/base/toggle.md) — A controlled two-state pressable for persistent choices such as formatting.
- [Toggle Group](https://gpui-kit.com/base/toggle-group.md) — Coordinates a set of toggle controls as a single- or multiple-selection group.
- [Tooltip](https://gpui-kit.com/base/tooltip.md) — A delayed, positioned description associated with a trigger element.
- [Tree](https://gpui-kit.com/base/tree.md) — A virtualized hierarchical list with explicit expansion and selection state.

> Documentation license: original prose and illustrations for which GPUI Kit holds licensing rights are also offered under CC BY 4.0. When copying or adapting, credit GPUI Kit, link the source (https://gpui-kit.com/base/primitives) and https://creativecommons.org/licenses/by/4.0/, and indicate changes. Code examples and software source use Apache-2.0; third-party material retains its terms; existing Apache-2.0 permissions remain.

> Bundled from [GPUI Kit](https://gpui-kit.com/base/primitives.md). Documentation prose: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); code examples: [Apache-2.0](https://github.com/longbridge/gpui-kit/blob/main/LICENSE). Changes: documentation links localized, asset URLs made absolute, and this attribution added.
