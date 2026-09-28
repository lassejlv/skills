---
url: /base/primitives/tree.md
description: A virtualized hierarchical list with explicit expansion and selection state.
---

# Tree

A virtualized hierarchical list with explicit expansion and selection state.

Like every `gpui-base` primitive, Tree supplies behavior and semantic structure without imposing a product visual language. Apply GPUI styles and compose the exported parts to match your design system.

## Example

The [single native Cargo entrypoint](https://github.com/longbridge/gpui-kit/blob/main/crates/base/examples/native/src/bin/components.rs) selects this primitive from the [shared showcase implementation](https://github.com/longbridge/gpui-kit/blob/main/crates/base/examples/showcase/mod.rs). The same showcase is compiled once for the WASM preview above.

```bash
cargo run -p gpui-base-examples -- tree
```

## Import

```rust
use gpui_kit::base::{Tree, TreeItem, TreeState};
```

## Anatomy and API

The example composes `Tree`, `TreeItem`, `TreeState`. GPUI's standard styling and event traits provide presentation; these base types provide the interaction structure.

The authoritative module is [`components/tree.rs`](https://github.com/longbridge/gpui-kit/blob/main/crates/base/examples/showcase/components/tree.rs). Native and browser previews compile this same file.

## State and events

`TreeState` owns items, expansion, and selection; tree actions update that entity.

Keep controlled state on the parent render type or in a GPUI entity. Update it in callbacks and call `cx.notify()`; do not recreate persistent entities during every render.

## Complete Rust example

The complete implementation used by the runnable showcase is embedded directly from Rust source:

```rust
use super::*;
use gpui::{Image, ImageFormat, StyleRefinement, img};
use std::sync::Arc;

const CHEVRON_RIGHT_SVG: &[u8] = br##"<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="none"><path d="m6 3.5 4.5 4.5L6 12.5" stroke="#171717" stroke-width="1.5" stroke-linecap="square" stroke-linejoin="miter"/></svg>"##;
const CHEVRON_DOWN_SVG: &[u8] = br##"<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="none"><path d="m3.5 6 4.5 4.5L12.5 6" stroke="#171717" stroke-width="1.5" stroke-linecap="square" stroke-linejoin="miter"/></svg>"##;

impl BaseShowcase {
    pub(in super::super) fn tree(&self) -> impl IntoElement {
        Tree::new(&self.tree)
            .w_64()
            .h_48()
            .list_style(StyleRefinement::default().flex_grow_1().size_full())
            .relative()
            .text_sm()
            .border_1()
            .border_color(super::example_rgb(0xd4d4d4))
            .py_1()
            .item(|_, entry, state, _, _| {
                let depth = entry.depth();
                let icon = entry.is_folder().then(|| {
                    let bytes = if entry.is_expanded() {
                        CHEVRON_DOWN_SVG
                    } else {
                        CHEVRON_RIGHT_SVG
                    };
                    img(Arc::new(Image::from_bytes(
                        ImageFormat::Svg,
                        bytes.to_vec(),
                    )))
                    .size_3()
                    .flex_none()
                });
                div()
                    .h_8()
                    .mx_1()
                    .px_2()
                    .flex()
                    .items_center()
                    .gap_1()
                    .when(state.is_selected(), |this| {
                        this.bg(super::example_rgb(0xf0f0f0))
                    })
                    .when(depth > 0, |this| {
                        this.child(div().flex_none().w(px(depth as f32 * 12.)))
                    })
                    .child(
                        div()
                            .size_3()
                            .flex_none()
                            .flex()
                            .items_center()
                            .justify_center()
                            .children(icon),
                    )
                    .child(entry.item().label.clone())
                    .into_any_element()
            })
    }
}
```

The command above supplies application initialization, window creation, and shared `BaseShowcase` state.

## Accessibility

Expose hierarchy, level, expansion, and selection; preserve keyboard movement and visible focus.

## Notes

Use stable element IDs where accepted. Verify focus, hover, active, selected, disabled, reduced-motion, and high-contrast appearances in the consuming design system.

> Documentation license: original prose and illustrations for which GPUI Kit holds licensing rights are also offered under CC BY 4.0. When copying or adapting, credit GPUI Kit, link the source (https://gpui-kit.com/base/primitives/tree) and https://creativecommons.org/licenses/by/4.0/, and indicate changes. Code examples and software source use Apache-2.0; third-party material retains its terms; existing Apache-2.0 permissions remain.

> Bundled from [GPUI Kit](https://gpui-kit.com/base/primitives/tree.md). Documentation prose: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); code examples: [Apache-2.0](https://github.com/longbridge/gpui-kit/blob/main/LICENSE). Changes: documentation links localized, asset URLs made absolute, and this attribution added.
