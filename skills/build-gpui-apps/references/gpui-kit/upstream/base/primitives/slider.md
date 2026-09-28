---
url: /base/primitives/slider.md
description: A state-driven range input with independently styleable track, indicator, and thumb.
---

# Slider

A state-driven range input with independently styleable track, indicator, and thumb.

Like every `gpui-base` primitive, Slider supplies behavior and semantic structure without imposing a product visual language. Apply GPUI styles and compose the exported parts to match your design system.

## Example

The [single native Cargo entrypoint](https://github.com/longbridge/gpui-kit/blob/main/crates/base/examples/native/src/bin/components.rs) selects this primitive from the [shared showcase implementation](https://github.com/longbridge/gpui-kit/blob/main/crates/base/examples/showcase/mod.rs). The same showcase is compiled once for the WASM preview above.

```bash
cargo run -p gpui-base-examples -- slider
```

## Import

```rust
use gpui_kit::base::{Slider, SliderState};
```

## Anatomy and API

The example composes `Slider`, `SliderState`. GPUI's standard styling and event traits provide presentation; these base types provide the interaction structure.

The authoritative module is [`components/slider.rs`](https://github.com/longbridge/gpui-kit/blob/main/crates/base/examples/showcase/components/slider.rs). Native and browser previews compile this same file.

## State and events

`SliderState` owns bounds and value; track, indicator, and thumb are separate visual parts.

Keep controlled state on the parent render type or in a GPUI entity. Update it in callbacks and call `cx.notify()`; do not recreate persistent entities during every render.

## Complete Rust example

The complete implementation used by the runnable showcase is embedded directly from Rust source:

```rust
use super::*;
use gpui::relative;

impl BaseShowcase {
    pub(in super::super) fn slider(&self, cx: &mut Context<Self>) -> impl IntoElement {
        let percentage = self.slider.read(cx).percentage().end;
        let thumb_size = 14.;
        div()
            .w_56()
            .text_xs()
            .child(
                div()
                    .mb_2()
                    .flex()
                    .justify_between()
                    .child("Volume")
                    .child("Drag to adjust"),
            )
            .child(
                Slider::new(&self.slider).w_full().h_7().child(
                    SliderTrack::new(&self.slider)
                        .relative()
                        .w_full()
                        .h_full()
                        .child(
                            div()
                                .absolute()
                                .top(px(13.))
                                .left_0()
                                .w_full()
                                .h(px(2.))
                                .bg(super::example_rgb(0xd4d4d4)),
                        )
                        .child(
                            SliderIndicator::new(&self.slider)
                                .absolute()
                                .top(px(13.))
                                .left_0()
                                .w_full()
                                .h(px(2.))
                                .child(
                                    div()
                                        .absolute()
                                        .top_0()
                                        .bottom_0()
                                        .left_0()
                                        .right(relative(1. - percentage))
                                        .bg(super::example_rgb(0x171717)),
                                ),
                        )
                        .child(
                            SliderThumb::new(&self.slider)
                                .absolute()
                                .top(px(7.))
                                .left(relative(percentage))
                                .ml(px(-thumb_size / 2.))
                                .size(px(thumb_size))
                                .bg(super::example_rgb(0xffffff))
                                .border_1()
                                .border_color(super::example_rgb(0x171717)),
                        ),
                ),
            )
    }
}
```

The command above supplies application initialization, window creation, and shared `BaseShowcase` state.

## Accessibility

Expose label, current value, and bounds; support keyboard increments.

## Notes

Use stable element IDs where accepted. Verify focus, hover, active, selected, disabled, reduced-motion, and high-contrast appearances in the consuming design system.

> Documentation license: original prose and illustrations for which GPUI Kit holds licensing rights are also offered under CC BY 4.0. When copying or adapting, credit GPUI Kit, link the source (https://gpui-kit.com/base/primitives/slider) and https://creativecommons.org/licenses/by/4.0/, and indicate changes. Code examples and software source use Apache-2.0; third-party material retains its terms; existing Apache-2.0 permissions remain.

> Bundled from [GPUI Kit](https://gpui-kit.com/base/primitives/slider.md). Documentation prose: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); code examples: [Apache-2.0](https://github.com/longbridge/gpui-kit/blob/main/LICENSE). Changes: documentation links localized, asset URLs made absolute, and this attribution added.
