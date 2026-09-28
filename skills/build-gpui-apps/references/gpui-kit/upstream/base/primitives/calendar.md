---
url: /base/primitives/calendar.md
description: A state-driven date grid with selection matchers and custom item rendering.
---

# Calendar

A state-driven date grid with selection matchers and custom item rendering.

Like every `gpui-base` primitive, Calendar supplies behavior and semantic structure without imposing a product visual language. Apply GPUI styles and compose the exported parts to match your design system.

## Example

The [single native Cargo entrypoint](https://github.com/longbridge/gpui-kit/blob/main/crates/base/examples/native/src/bin/components.rs) selects this primitive from the [shared showcase implementation](https://github.com/longbridge/gpui-kit/blob/main/crates/base/examples/showcase/mod.rs). The same showcase is compiled once for the WASM preview above.

```bash
cargo run -p gpui-base-examples -- calendar
```

## Import

```rust
use gpui_kit::base::{Calendar, CalendarState};
```

## Anatomy and API

The example composes `Calendar`, `CalendarState`. GPUI's standard styling and event traits provide presentation; these base types provide the interaction structure.

The authoritative module is [`components/calendar.rs`](https://github.com/longbridge/gpui-kit/blob/main/crates/base/examples/showcase/components/calendar.rs). Native and browser previews compile this same file.

## State and events

Selection lives in `CalendarState`; configure matching and update the state from calendar item interaction.

Keep controlled state on the parent render type or in a GPUI entity. Update it in callbacks and call `cx.notify()`; do not recreate persistent entities during every render.

## Complete Rust example

The complete implementation used by the runnable showcase is embedded directly from Rust source:

```rust
use super::*;

impl BaseShowcase {
    pub(in super::super) fn calendar(&self) -> impl IntoElement {
        Calendar::new("example-calendar", &self.calendar)
            // 7 × 32px cells + 12px padding on each side + 1px borders.
            .w(px(250.))
            .p_3()
            .border_1()
            .border_color(super::example_rgb(0xd4d4d4))
            .item(|item, state, _, _| {
                match state.kind() {
                    CalendarItemKind::Previous | CalendarItemKind::Next => item
                        .size_7()
                        .flex()
                        .items_center()
                        .justify_center()
                        .hover(|s| s.bg(super::example_rgb(0xf5f5f5))),
                    CalendarItemKind::MonthToggle | CalendarItemKind::YearToggle => item
                        .px_1()
                        .h_7()
                        .flex()
                        .items_center()
                        .justify_center()
                        .text_xs()
                        .hover(|s| s.bg(super::example_rgb(0xf5f5f5))),
                    CalendarItemKind::Weekday => item
                        .size_8()
                        .flex()
                        .items_center()
                        .justify_center()
                        .text_xs()
                        .text_color(super::example_rgb(0x737373)),
                    CalendarItemKind::Day => item
                        .size_8()
                        .flex()
                        .items_center()
                        .justify_center()
                        .text_xs()
                        .when(state.is_muted(), |s| {
                            s.text_color(super::example_rgb(0xa3a3a3))
                        })
                        .when(state.is_today() && !state.is_active(), |s| {
                            s.border_1().border_color(super::example_rgb(0xd4d4d4))
                        })
                        .when(state.is_active(), |s| {
                            s.bg(super::example_rgb(0x171717))
                                .text_color(super::example_rgb(0xffffff))
                        })
                        .when(!state.is_disabled() && !state.is_active(), |s| {
                            s.hover(|s| s.bg(super::example_rgb(0xf5f5f5)))
                        }),
                    CalendarItemKind::Month | CalendarItemKind::Year => item
                        .w(px(74.))
                        .h_7()
                        .flex()
                        .items_center()
                        .justify_center()
                        .text_xs()
                        .when(state.is_active(), |s| {
                            s.bg(super::example_rgb(0x171717))
                                .text_color(super::example_rgb(0xffffff))
                        })
                        .when(!state.is_active(), |s| {
                            s.hover(|s| s.bg(super::example_rgb(0xf5f5f5)))
                        }),
                }
                .into_any_element()
            })
            .label(|kind, value| match kind {
                CalendarItemKind::Previous => "‹".into(),
                CalendarItemKind::Next => "›".into(),
                CalendarItemKind::MonthToggle | CalendarItemKind::Month => [
                    "", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct",
                    "Nov", "Dec",
                ][value as usize]
                    .into(),
                CalendarItemKind::Weekday => {
                    ["Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"][value as usize].into()
                }
                _ => value.to_string().into(),
            })
    }
}
```

The command above supplies application initialization, window creation, and shared `BaseShowcase` state.

## Accessibility

Label dates and selected, disabled, and today states; retain arrow-key navigation.

## Notes

Use stable element IDs where accepted. Verify focus, hover, active, selected, disabled, reduced-motion, and high-contrast appearances in the consuming design system.

> Documentation license: original prose and illustrations for which GPUI Kit holds licensing rights are also offered under CC BY 4.0. When copying or adapting, credit GPUI Kit, link the source (https://gpui-kit.com/base/primitives/calendar) and https://creativecommons.org/licenses/by/4.0/, and indicate changes. Code examples and software source use Apache-2.0; third-party material retains its terms; existing Apache-2.0 permissions remain.

> Bundled from [GPUI Kit](https://gpui-kit.com/base/primitives/calendar.md). Documentation prose: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); code examples: [Apache-2.0](https://github.com/longbridge/gpui-kit/blob/main/LICENSE). Changes: documentation links localized, asset URLs made absolute, and this attribution added.
