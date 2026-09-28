---
url: /base/primitives/tabs.md
description: A tab list and accessible tab controls with controlled selection.
---

# Tabs

A tab list and accessible tab controls with controlled selection.

Like every `gpui-base` primitive, Tabs supplies behavior and semantic structure without imposing a product visual language. Apply GPUI styles and compose the exported parts to match your design system.

## Example

The [single native Cargo entrypoint](https://github.com/longbridge/gpui-kit/blob/main/crates/base/examples/native/src/bin/components.rs) selects this primitive from the [shared showcase implementation](https://github.com/longbridge/gpui-kit/blob/main/crates/base/examples/showcase/mod.rs). The same showcase is compiled once for the WASM preview above.

```bash
cargo run -p gpui-base-examples -- tabs
```

## Import

```rust
use gpui_kit::base::{Tab, Tabs};
```

## Anatomy and API

The example composes `Tab`, `Tabs`. GPUI's standard styling and event traits provide presentation; these base types provide the interaction structure.

The authoritative module is [`components/tabs.rs`](https://github.com/longbridge/gpui-kit/blob/main/crates/base/examples/showcase/components/tabs.rs). Native and browser previews compile this same file.

## State and events

The parent owns selected index/value; each tab reflects it and click handlers update the parent.

Keep controlled state on the parent render type or in a GPUI entity. Update it in callbacks and call `cx.notify()`; do not recreate persistent entities during every render.

## Complete Rust example

The complete implementation used by the runnable showcase is embedded directly from Rust source:

```rust
use super::*;

impl BaseShowcase {
    pub(in super::super) fn tabs(&self, cx: &mut Context<Self>) -> impl IntoElement {
        let selected = self.selected_tab;
        div()
            .w_72()
            .text_xs()
            .border_1()
            .border_color(super::example_rgb(0xd4d4d4))
            .child(
                Tabs::new("example-tabs")
                    .flex()
                    .px_2()
                    .pt_1()
                    .border_b_1()
                    .border_color(super::example_rgb(0xd4d4d4))
                    .children(
                        ["Overview", "Activity", "Settings"]
                            .into_iter()
                            .enumerate()
                            .map(|(index, label)| {
                                let entity = cx.entity().downgrade();
                                Tab::new(index)
                                    .selected(self.selected_tab == index)
                                    .px_2()
                                    .h_7()
                                    .flex()
                                    .items_center()
                                    .border_b_2()
                                    .border_color(if self.selected_tab == index {
                                        super::example_rgb(0x171717)
                                    } else {
                                        super::example_rgb(0xffffff)
                                    })
                                    .when(self.selected_tab == index, |this| {
                                        this.font_weight(gpui::FontWeight::SEMIBOLD)
                                    })
                                    .on_click(move |_, _, cx| {
                                        _ = entity.update(cx, |this, cx| {
                                            this.selected_tab = index;
                                            cx.notify();
                                        });
                                    })
                                    .child(label)
                            }),
                    ),
            )
            .child(
                div().min_h_20().p_3().child(match selected {
                    0 => div().child("Workspace overview").child(
                        div()
                            .mt_1()
                            .text_color(super::example_rgb(0x737373))
                            .child("12 components · 4 contributors · updated today"),
                    ),
                    1 => div().child("Recent activity").child(
                        div()
                            .mt_1()
                            .text_color(super::example_rgb(0x737373))
                            .child("Button example was updated 8 minutes ago."),
                    ),
                    _ => div().child("Project settings").child(
                        div()
                            .mt_1()
                            .text_color(super::example_rgb(0x737373))
                            .child("Manage notifications and member access."),
                    ),
                }),
            )
    }
}
```

The command above supplies application initialization, window creation, and shared `BaseShowcase` state.

## Accessibility

Associate tabs with panels, expose selection, and support keyboard traversal.

## Notes

Use stable element IDs where accepted. Verify focus, hover, active, selected, disabled, reduced-motion, and high-contrast appearances in the consuming design system.

> Documentation license: original prose and illustrations for which GPUI Kit holds licensing rights are also offered under CC BY 4.0. When copying or adapting, credit GPUI Kit, link the source (https://gpui-kit.com/base/primitives/tabs) and https://creativecommons.org/licenses/by/4.0/, and indicate changes. Code examples and software source use Apache-2.0; third-party material retains its terms; existing Apache-2.0 permissions remain.

> Bundled from [GPUI Kit](https://gpui-kit.com/base/primitives/tabs.md). Documentation prose: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); code examples: [Apache-2.0](https://github.com/longbridge/gpui-kit/blob/main/LICENSE). Changes: documentation links localized, asset URLs made absolute, and this attribution added.
