---
url: /base/primitives/pagination.md
description: A controlled page navigator with explicit current and total page state.
---

# Pagination

A controlled page navigator with explicit current and total page state.

Like every `gpui-base` primitive, Pagination supplies behavior and semantic structure without imposing a product visual language. Apply GPUI styles and compose the exported parts to match your design system.

## Example

The [single native Cargo entrypoint](https://github.com/longbridge/gpui-kit/blob/main/crates/base/examples/native/src/bin/components.rs) selects this primitive from the [shared showcase implementation](https://github.com/longbridge/gpui-kit/blob/main/crates/base/examples/showcase/mod.rs). The same showcase is compiled once for the WASM preview above.

```bash
cargo run -p gpui-base-examples -- pagination
```

## Import

```rust
use gpui_kit::base::{Pagination, PaginationState};
```

## Anatomy and API

The example composes `Pagination`, `PaginationState`. GPUI's standard styling and event traits provide presentation; these base types provide the interaction structure.

The authoritative module is [`components/pagination.rs`](https://github.com/longbridge/gpui-kit/blob/main/crates/base/examples/showcase/components/pagination.rs). Native and browser previews compile this same file.

## State and events

`PaginationState` owns current and total pages; `on_change` reports valid requested pages.

Keep controlled state on the parent render type or in a GPUI entity. Update it in callbacks and call `cx.notify()`; do not recreate persistent entities during every render.

## Complete Rust example

The complete implementation used by the runnable showcase is embedded directly from Rust source:

```rust
use gpui::{
    Context, IntoElement, ParentElement as _, Styled as _, div, prelude::FluentBuilder as _, px,
};
use gpui_base::{Button, Pagination, PaginationItem, PaginationState};

use super::super::BaseShowcase;

impl BaseShowcase {
    pub(in super::super) fn pagination(&self, cx: &mut Context<Self>) -> impl IntoElement {
        let entity = cx.entity().downgrade();
        let state = PaginationState::new(self.page, 8).on_change(move |page, _, cx| {
            _ = entity.update(cx, |this, cx| {
                this.page = page;
                cx.notify();
            });
        });
        let items = state.items();
        Pagination::new("example-pagination", state.clone())
            .flex()
            .items_center()
            .gap_2()
            .text_xs()
            .children(items.into_iter().map(move |item| {
                match item {
                    PaginationItem::Page(page) => {
                        let state = state.clone();
                        Button::new(("page", page))
                            .size_7()
                            .p_0()
                            .flex()
                            .items_center()
                            .justify_center()
                            .border_1()
                            .border_color(super::example_rgb(0xd4d4d4))
                            .when(page == state.current_page(), |this| {
                                this.bg(super::example_rgb(0x171717))
                                    .text_color(super::example_rgb(0xffffff))
                            })
                            .on_click(move |_, window, cx| state.request_page(page, window, cx))
                            .child(page.to_string())
                            .into_any_element()
                    }
                    PaginationItem::Ellipsis(_) => div()
                        .w(px(20.))
                        .h_7()
                        .flex()
                        .items_center()
                        .justify_center()
                        .child("…")
                        .into_any_element(),
                }
            }))
    }
}
```

The command above supplies application initialization, window creation, and shared `BaseShowcase` state.

## Accessibility

Identify current page, label previous/next, and disable unavailable boundary actions.

## Notes

Use stable element IDs where accepted. Verify focus, hover, active, selected, disabled, reduced-motion, and high-contrast appearances in the consuming design system.

> Documentation license: original prose and illustrations for which GPUI Kit holds licensing rights are also offered under CC BY 4.0. When copying or adapting, credit GPUI Kit, link the source (https://gpui-kit.com/base/primitives/pagination) and https://creativecommons.org/licenses/by/4.0/, and indicate changes. Code examples and software source use Apache-2.0; third-party material retains its terms; existing Apache-2.0 permissions remain.

> Bundled from [GPUI Kit](https://gpui-kit.com/base/primitives/pagination.md). Documentation prose: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); code examples: [Apache-2.0](https://github.com/longbridge/gpui-kit/blob/main/LICENSE). Changes: documentation links localized, asset URLs made absolute, and this attribution added.
