---
url: /base/primitives/toggle-group.md
description: Coordinates a set of toggle controls as a single- or multiple-selection group.
---

# Toggle Group

Coordinates a set of toggle controls as a single- or multiple-selection group.

Like every `gpui-base` primitive, Toggle Group supplies behavior and semantic structure without imposing a product visual language. Apply GPUI styles and compose the exported parts to match your design system.

## Example

The [single native Cargo entrypoint](https://github.com/longbridge/gpui-kit/blob/main/crates/base/examples/native/src/bin/components.rs) selects this primitive from the [shared showcase implementation](https://github.com/longbridge/gpui-kit/blob/main/crates/base/examples/showcase/mod.rs). The same showcase is compiled once for the WASM preview above.

```bash
cargo run -p gpui-base-examples -- toggle-group
```

## Import

```rust
use gpui_kit::base::{Toggle, ToggleGroup};
```

## Anatomy and API

The example composes `Toggle`, `ToggleGroup`. GPUI's standard styling and event traits provide presentation; these base types provide the interaction structure.

The authoritative module is [`components/toggle_group.rs`](https://github.com/longbridge/gpui-kit/blob/main/crates/base/examples/showcase/components/toggle_group.rs). Native and browser previews compile this same file.

## State and events

The group coordinates single or multiple selection while children reflect group state.

Keep controlled state on the parent render type or in a GPUI entity. Update it in callbacks and call `cx.notify()`; do not recreate persistent entities during every render.

## Complete Rust example

The complete implementation used by the runnable showcase is embedded directly from Rust source:

```rust
use super::*;

impl BaseShowcase {
    pub(in super::super) fn toggle_group(&self, cx: &mut Context<Self>) -> impl IntoElement {
        let italic = self.toggle_group_selection & 1 != 0;
        let underline = self.toggle_group_selection & 2 != 0;
        let entity = cx.entity().downgrade();
        ToggleGroup::new("example-toggle-group")
            .flex()
            .text_xs()
            .gap_0()
            .child(self.toggle(cx))
            .child(
                Toggle::new("italic-toggle")
                    .pressed(italic)
                    .size_7()
                    .flex()
                    .items_center()
                    .justify_center()
                    .border_1()
                    .border_l_0()
                    .border_color(super::example_rgb(0x171717))
                    .when(italic, |this| {
                        this.bg(super::example_rgb(0x171717))
                            .text_color(super::example_rgb(0xffffff))
                    })
                    .accessibility_label("Italic")
                    .child("I")
                    .on_change({
                        let entity = entity.clone();
                        move |next, _, _, cx| {
                            _ = entity.update(cx, |this, cx| {
                                if next {
                                    this.toggle_group_selection |= 1
                                } else {
                                    this.toggle_group_selection &= !1
                                };
                                cx.notify();
                            });
                        }
                    }),
            )
            .child(
                Toggle::new("underline-toggle")
                    .pressed(underline)
                    .size_7()
                    .flex()
                    .items_center()
                    .justify_center()
                    .border_1()
                    .border_l_0()
                    .border_color(super::example_rgb(0x171717))
                    .when(underline, |this| {
                        this.bg(super::example_rgb(0x171717))
                            .text_color(super::example_rgb(0xffffff))
                    })
                    .accessibility_label("Underline")
                    .child("U")
                    .on_change(move |next, _, _, cx| {
                        _ = entity.update(cx, |this, cx| {
                            if next {
                                this.toggle_group_selection |= 2
                            } else {
                                this.toggle_group_selection &= !2
                            };
                            cx.notify();
                        });
                    }),
            )
    }
}
```

The command above supplies application initialization, window creation, and shared `BaseShowcase` state.

## Accessibility

Label the group, expose each selection state, and keep focus order predictable.

## Notes

Use stable element IDs where accepted. Verify focus, hover, active, selected, disabled, reduced-motion, and high-contrast appearances in the consuming design system.

> Documentation license: original prose and illustrations for which GPUI Kit holds licensing rights are also offered under CC BY 4.0. When copying or adapting, credit GPUI Kit, link the source (https://gpui-kit.com/base/primitives/toggle-group) and https://creativecommons.org/licenses/by/4.0/, and indicate changes. Code examples and software source use Apache-2.0; third-party material retains its terms; existing Apache-2.0 permissions remain.

> Bundled from [GPUI Kit](https://gpui-kit.com/base/primitives/toggle-group.md). Documentation prose: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); code examples: [Apache-2.0](https://github.com/longbridge/gpui-kit/blob/main/LICENSE). Changes: documentation links localized, asset URLs made absolute, and this attribution added.
