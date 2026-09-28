---
url: /base/primitives/time-field.md
description: A segmented time-of-day editor with a complete keyboard model and 24- or 12-hour clocks.
---

# Time Field

A segmented time-of-day editor with a complete keyboard model and 24- or 12-hour clocks.

Like every `gpui-base` primitive, Time Field supplies behavior and semantic structure without imposing a product visual language. Apply GPUI styles and compose the exported parts to match your design system.

## Example

The [single native Cargo entrypoint](https://github.com/longbridge/gpui-kit/blob/main/crates/base/examples/native/src/bin/components.rs) selects this primitive from the [shared showcase implementation](https://github.com/longbridge/gpui-kit/blob/main/crates/base/examples/showcase/mod.rs). The same showcase is compiled once for the WASM preview above.

```bash
cargo run -p gpui-base-examples -- time-field
```

## Import

```rust
use gpui_kit::base::{HourCycle, TimeField, TimeFieldEvent, TimeFieldState, TimePrecision};
```

## Anatomy and API

The example composes `TimeField` over a `TimeFieldState`. The field renders one `TimeFieldSegment` per hour, minute, optional second and optional AM/PM part, separated by `:`. Lay out and style the root with `Styled`, and decorate each segment through `TimeField::render_segment`; the slot receives a `TimeFieldSegmentState` with the segment, its value and whether it is selected.

The authoritative module is [`components/time_field.rs`](https://github.com/longbridge/gpui-kit/blob/main/crates/base/examples/showcase/components/time_field.rs). Native and browser previews compile this same file.

## State and events

`TimeFieldState` owns the time, its precision (`TimePrecision::Minute` or `Second`) and hour cycle (`HourCycle::H23` by default, or `H12`). `set_time` replaces the value without emitting; user edits emit `TimeFieldEvent::Change`.

The field is one Tab stop. Up/Down step the selected segment and wrap within it without carrying into the next unit, Left/Right and Tab/Shift-Tab move between segments, digits type a value with a two-digit buffer and advance once no further digit fits, `a`/`p` set AM or PM, and Backspace/Delete reset the segment.

Keep controlled state on the parent render type or in a GPUI entity. Update it in callbacks and call `cx.notify()`; do not recreate persistent entities during every render.

## Complete Rust example

The complete implementation used by the runnable showcase is embedded directly from Rust source:

```rust
use gpui::{
    Context, IntoElement, ParentElement as _, Styled as _, div, prelude::FluentBuilder as _,
};
use gpui_base::TimeField;

use super::super::BaseShowcase;

impl BaseShowcase {
    pub(in super::super) fn time_field(&self, cx: &mut Context<Self>) -> impl IntoElement {
        let value = self.time_field.read(cx).time();

        div()
            .w_56()
            .flex()
            .flex_col()
            .gap_1()
            .text_xs()
            .child(div().child("Reminder time"))
            .child(
                TimeField::new("example-time-field", &self.time_field)
                    .flex()
                    .items_center()
                    .h_7()
                    .px_2()
                    .border_1()
                    .border_color(super::example_rgb(0xa3a3a3))
                    .bg(super::example_rgb(0xffffff))
                    .render_segment(|segment, state, _, _| {
                        segment
                            .px_0p5()
                            .when(state.is_selected(), |this| {
                                this.bg(super::example_rgb(0xdbeafe))
                            })
                            .into_any_element()
                    }),
            )
            .child(
                div()
                    .text_color(super::example_rgb(0x737373))
                    .child(format!("Selected {}", value.format("%H:%M:%S"))),
            )
    }
}
```

The command above supplies application initialization, window creation, and shared `BaseShowcase` state.

## Accessibility

The root exposes `Role::TimeInput` with the formatted time as its value. Label the field, and keep the selected segment visibly distinct from the others.

## Notes

Use tabular figures or fixed segment widths so the field does not change width while digits are typed. Verify focus, selected, disabled, and high-contrast appearances in the consuming design system.

> Documentation license: original prose and illustrations for which GPUI Kit holds licensing rights are also offered under CC BY 4.0. When copying or adapting, credit GPUI Kit, link the source (https://gpui-kit.com/base/primitives/time-field) and https://creativecommons.org/licenses/by/4.0/, and indicate changes. Code examples and software source use Apache-2.0; third-party material retains its terms; existing Apache-2.0 permissions remain.

> Bundled from [GPUI Kit](https://gpui-kit.com/base/primitives/time-field.md). Documentation prose: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); code examples: [Apache-2.0](https://github.com/longbridge/gpui-kit/blob/main/LICENSE). Changes: documentation links localized, asset URLs made absolute, and this attribution added.
