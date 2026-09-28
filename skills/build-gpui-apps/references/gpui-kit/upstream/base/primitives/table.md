---
url: /base/primitives/table.md
description: Semantic table primitives for composing headers, bodies, rows, and cells.
---

# Table

Semantic table primitives for composing headers, bodies, rows, and cells.

Like every `gpui-base` primitive, Table supplies behavior and semantic structure without imposing a product visual language. Apply GPUI styles and compose the exported parts to match your design system.

## Example

The [single native Cargo entrypoint](https://github.com/longbridge/gpui-kit/blob/main/crates/base/examples/native/src/bin/components.rs) selects this primitive from the [shared showcase implementation](https://github.com/longbridge/gpui-kit/blob/main/crates/base/examples/showcase/mod.rs). The same showcase is compiled once for the WASM preview above.

```bash
cargo run -p gpui-base-examples -- table
```

## Import

```rust
use gpui_kit::base::{Table, TableBody, TableCell, TableHead, TableHeader, TableRow};
```

## Anatomy and API

The example composes `Table`, `TableBody`, `TableCell`, `TableHead`, `TableHeader`, `TableRow`. GPUI's standard styling and event traits provide presentation; these base types provide the interaction structure.

The authoritative module is [`components/table.rs`](https://github.com/longbridge/gpui-kit/blob/main/crates/base/examples/showcase/components/table.rs). Native and browser previews compile this same file.

## State and events

Rows and cells are stateless composition; sorting, selection, and mutations remain in the parent.

Keep controlled state on the parent render type or in a GPUI entity. Update it in callbacks and call `cx.notify()`; do not recreate persistent entities during every render.

## Complete Rust example

The complete implementation used by the runnable showcase is embedded directly from Rust source:

```rust
use super::*;

impl BaseShowcase {
    pub(in super::super) fn table(&self) -> impl IntoElement {
        Table::new("example-table")
            .w_72()
            .text_xs()
            .border_1()
            .border_color(super::example_rgb(0xe5e7eb))
            .overflow_hidden()
            .child(
                TableHeader::new("header").child(
                    TableRow::new("header-row", 1)
                        .flex()
                        .bg(super::example_rgb(0xf5f5f5))
                        .child(
                            TableHead::new("name-head", 1)
                                .w(px(124.))
                                .px_2()
                                .py_1()
                                .child("Component"),
                        )
                        .child(
                            TableHead::new("status-head", 2)
                                .w(px(84.))
                                .px_2()
                                .py_1()
                                .child("Status"),
                        )
                        .child(
                            TableHead::new("version-head", 3)
                                .w(px(92.))
                                .px_2()
                                .py_1()
                                .child("Version"),
                        ),
                ),
            )
            .child(
                TableBody::new("body").children(
                    [
                        ("gpui-base", "Stable", "0.4.1"),
                        ("gpui-component", "Active", "0.4.1"),
                        ("story-web", "Preview", "0.2.8"),
                        ("gpui-web", "Beta", "0.1.0"),
                    ]
                    .into_iter()
                    .enumerate()
                    .map(|(ix, (name, status, version))| {
                        TableRow::new(("body-row", ix), ix)
                            .flex()
                            .border_t_1()
                            .border_color(super::example_rgb(0xe5e7eb))
                            .child(
                                TableCell::new("name", 1)
                                    .w(px(124.))
                                    .px_2()
                                    .py_1()
                                    .child(name),
                            )
                            .child(
                                TableCell::new(("status", ix), 2)
                                    .w(px(84.))
                                    .px_2()
                                    .py_1()
                                    .child(
                                        div()
                                            .px_1()
                                            .border_1()
                                            .border_color(super::example_rgb(0xd4d4d4))
                                            .child(status),
                                    ),
                            )
                            .child(
                                TableCell::new(("version", ix), 3)
                                    .w(px(92.))
                                    .px_2()
                                    .py_1()
                                    .text_color(super::example_rgb(0x737373))
                                    .child(version),
                            )
                    }),
                ),
            )
    }
}
```

The command above supplies application initialization, window creation, and shared `BaseShowcase` state.

## Accessibility

Use headers, preserve reading order, and separately expose sort and selection controls.

## Notes

Use stable element IDs where accepted. Verify focus, hover, active, selected, disabled, reduced-motion, and high-contrast appearances in the consuming design system.

> Documentation license: original prose and illustrations for which GPUI Kit holds licensing rights are also offered under CC BY 4.0. When copying or adapting, credit GPUI Kit, link the source (https://gpui-kit.com/base/primitives/table) and https://creativecommons.org/licenses/by/4.0/, and indicate changes. Code examples and software source use Apache-2.0; third-party material retains its terms; existing Apache-2.0 permissions remain.

> Bundled from [GPUI Kit](https://gpui-kit.com/base/primitives/table.md). Documentation prose: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); code examples: [Apache-2.0](https://github.com/longbridge/gpui-kit/blob/main/LICENSE). Changes: documentation links localized, asset URLs made absolute, and this attribution added.
