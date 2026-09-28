---
url: /base/primitives/popup.md
description: A low-level trigger and anchored floating-content host.
---

# Popup

`Popup` owns trigger measurement, anchor positioning, deferred rendering, and window-edge snapping. The application owns open state, content, appearance, and motion. Higher-level primitives such as Popover build on the same floating-surface ideas.

## Example

The [single native Cargo entrypoint](https://github.com/longbridge/gpui-kit/blob/main/crates/base/examples/native/src/bin/components.rs) selects this primitive from the [shared showcase implementation](https://github.com/longbridge/gpui-kit/blob/main/crates/base/examples/showcase/mod.rs). The same showcase is compiled once for the WASM preview above.

```bash
cargo run -p gpui-base-examples -- popup
```

## Import

```rust
use gpui_kit::base::Popup;
```

## Anatomy and API

The example composes `Popup`. GPUI's standard styling and event traits provide presentation; these base types provide the interaction structure.

The authoritative module is [`components/popup.rs`](https://github.com/longbridge/gpui-kit/blob/main/crates/base/examples/showcase/components/popup.rs). Native and browser previews compile this same file.

## State and events

The caller owns trigger, anchor, open state, content, and dismissal policy.

Keep controlled state on the parent render type or in a GPUI entity. Update it in callbacks and call `cx.notify()`; do not recreate persistent entities during every render.

## Complete Rust example

The complete implementation used by the runnable showcase is embedded directly from Rust source:

```rust
use gpui::{
    Context, IntoElement, ParentElement as _, Styled as _, div, prelude::FluentBuilder as _,
    relative,
};
use gpui_base::{Button, Popup};

use super::super::BaseShowcase;

impl BaseShowcase {
    pub(in super::super) fn popup(&self, cx: &mut Context<Self>) -> impl IntoElement {
        let open = self.popup_open;
        let entity = cx.entity().downgrade();
        Popup::new(
            "example-popup",
            Button::new("popup-trigger")
                .h_7()
                .line_height(relative(1.))
                .px_3()
                .flex()
                .items_center()
                .justify_center()
                .bg(gpui::black())
                .text_color(gpui::white())
                .on_click(move |_, _, cx| {
                    _ = entity.update(cx, |this, cx| {
                        this.popup_open = !this.popup_open;
                        cx.notify();
                    });
                })
                .child(if open { "Close popup" } else { "Open popup" }),
        )
        .when(open, |this| {
            this.content(
                div()
                    .w_64()
                    .p_2()
                    .text_xs()
                    .bg(super::example_rgb(0xffffff))
                    .border_1()
                    .border_color(super::example_rgb(0x171717))
                    .child("Anchored surface")
                    .child(
                        div()
                            .mt_1()
                            .text_sm()
                            .text_color(super::example_rgb(0x737373))
                            .child("Popup positions content relative to its trigger."),
                    ),
            )
        })
    }
}
```

The command above supplies application initialization, window creation, and shared `BaseShowcase` state.

## Accessibility

The caller must supply suitable menu, listbox, or dialog semantics and focus policy.

## Notes

Use stable element IDs where accepted. Verify focus, hover, active, selected, disabled, reduced-motion, and high-contrast appearances in the consuming design system.

> Documentation license: original prose and illustrations for which GPUI Kit holds licensing rights are also offered under CC BY 4.0. When copying or adapting, credit GPUI Kit, link the source (https://gpui-kit.com/base/primitives/popup) and https://creativecommons.org/licenses/by/4.0/, and indicate changes. Code examples and software source use Apache-2.0; third-party material retains its terms; existing Apache-2.0 permissions remain.

> Bundled from [GPUI Kit](https://gpui-kit.com/base/primitives/popup.md). Documentation prose: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); code examples: [Apache-2.0](https://github.com/longbridge/gpui-kit/blob/main/LICENSE). Changes: documentation links localized, asset URLs made absolute, and this attribution added.
