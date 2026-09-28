---
url: /base/primitives/switch.md
description: A controlled on/off control with separately styleable track and thumb.
---

# Switch

A controlled on/off control with separately styleable track and thumb.

Like every `gpui-base` primitive, Switch supplies behavior and semantic structure without imposing a product visual language. Apply GPUI styles and compose the exported parts to match your design system.

## Example

The [single native Cargo entrypoint](https://github.com/longbridge/gpui-kit/blob/main/crates/base/examples/native/src/bin/components.rs) selects this primitive from the [shared showcase implementation](https://github.com/longbridge/gpui-kit/blob/main/crates/base/examples/showcase/mod.rs). The same showcase is compiled once for the WASM preview above.

```bash
cargo run -p gpui-base-examples -- switch
```

## Import

```rust
use gpui_kit::base::{Switch, SwitchThumb, SwitchTrack};
```

## Anatomy and API

The example composes `Switch`, `SwitchThumb`, `SwitchTrack`. GPUI's standard styling and event traits provide presentation; these base types provide the interaction structure.

The authoritative module is [`components/switch.rs`](https://github.com/longbridge/gpui-kit/blob/main/crates/base/examples/showcase/components/switch.rs). Native and browser previews compile this same file.

## State and events

Pass the controlled boolean to `checked`; `on_change` emits the requested next value.

Keep controlled state on the parent render type or in a GPUI entity. Update it in callbacks and call `cx.notify()`; do not recreate persistent entities during every render.

## Complete Rust example

The complete implementation used by the runnable showcase is embedded directly from Rust source:

```rust
use super::*;

impl BaseShowcase {
    pub(in super::super) fn switch(&self, cx: &mut Context<Self>) -> impl IntoElement {
        let checked = self.switch_checked;
        let entity = cx.entity().downgrade();
        div()
            .w_64()
            .text_xs()
            .flex()
            .items_center()
            .justify_between()
            .child(
                div().child("Automatic updates").child(
                    div()
                        .mt_1()
                        .text_xs()
                        .text_color(super::example_rgb(0x737373))
                        .child("Install stable releases automatically."),
                ),
            )
            .child(
                Switch::new("example-switch")
                    .checked(checked)
                    .on_change(move |next, _, _, cx| {
                        _ = entity.update(cx, |this, cx| {
                            this.switch_checked = next;
                            cx.notify();
                        });
                    })
                    .child(
                        SwitchTrack::new("example-switch-track")
                            .checked(checked)
                            .w(px(36.))
                            .h(px(20.))
                            .p(px(2.))
                            .bg(if checked {
                                super::example_rgb(0x171717)
                            } else {
                                super::example_rgb(0xd4d4d4)
                            })
                            .child(
                                SwitchThumb::new(checked)
                                    .size_4()
                                    .bg(super::example_rgb(0xffffff))
                                    .ml(if checked { px(16.) } else { px(0.) }),
                            ),
                    ),
            )
    }
}
```

The command above supplies application initialization, window creation, and shared `BaseShowcase` state.

## Accessibility

Label the setting, expose checked state, and keep the accessible name stable.

## Notes

Use stable element IDs where accepted. Verify focus, hover, active, selected, disabled, reduced-motion, and high-contrast appearances in the consuming design system.

> Documentation license: original prose and illustrations for which GPUI Kit holds licensing rights are also offered under CC BY 4.0. When copying or adapting, credit GPUI Kit, link the source (https://gpui-kit.com/base/primitives/switch) and https://creativecommons.org/licenses/by/4.0/, and indicate changes. Code examples and software source use Apache-2.0; third-party material retains its terms; existing Apache-2.0 permissions remain.

> Bundled from [GPUI Kit](https://gpui-kit.com/base/primitives/switch.md). Documentation prose: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); code examples: [Apache-2.0](https://github.com/longbridge/gpui-kit/blob/main/LICENSE). Changes: documentation links localized, asset URLs made absolute, and this attribution added.
