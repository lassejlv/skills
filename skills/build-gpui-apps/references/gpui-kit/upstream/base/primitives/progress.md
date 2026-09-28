---
url: /base/primitives/progress.md
description: Composable track and indicator parts for reporting task completion.
---

# Progress

Composable track and indicator parts for reporting task completion.

Like every `gpui-base` primitive, Progress supplies behavior and semantic structure without imposing a product visual language. Apply GPUI styles and compose the exported parts to match your design system.

## Example

The [single native Cargo entrypoint](https://github.com/longbridge/gpui-kit/blob/main/crates/base/examples/native/src/bin/components.rs) selects this primitive from the [shared showcase implementation](https://github.com/longbridge/gpui-kit/blob/main/crates/base/examples/showcase/mod.rs). The same showcase is compiled once for the WASM preview above.

```bash
cargo run -p gpui-base-examples -- progress
```

## Import

```rust
use gpui_kit::base::{Progress, ProgressIndicator, ProgressTrack};
```

## Anatomy and API

The example composes `Progress`, `ProgressIndicator`, `ProgressTrack`. GPUI's standard styling and event traits provide presentation; these base types provide the interaction structure.

The authoritative module is [`components/progress.rs`](https://github.com/longbridge/gpui-kit/blob/main/crates/base/examples/showcase/components/progress.rs). Native and browser previews compile this same file.

## State and events

Set the value on `Progress`; size and position `ProgressIndicator` inside `ProgressTrack`.

Keep controlled state on the parent render type or in a GPUI entity. Update it in callbacks and call `cx.notify()`; do not recreate persistent entities during every render.

## Complete Rust example

The complete implementation used by the runnable showcase is embedded directly from Rust source:

```rust
use gpui::{IntoElement, ParentElement as _, Styled as _, div, px};
use gpui_base::{Progress, ProgressIndicator, ProgressTrack};

use super::super::BaseShowcase;

impl BaseShowcase {
    pub(in super::super) fn progress(&self) -> impl IntoElement {
        div()
            .w_64()
            .flex()
            .flex_col()
            .gap_2()
            .text_xs()
            .child(
                div()
                    .flex()
                    .justify_between()
                    .child("Uploading assets")
                    .child("68%"),
            )
            .child(
                Progress::new("example-progress").value(68.).child(
                    ProgressTrack::new()
                        .w_full()
                        .h(px(7.))
                        .border_1()
                        .border_color(super::example_rgb(0x171717))
                        .child(
                            ProgressIndicator::new()
                                .w(px(177.))
                                .h_full()
                                .bg(super::example_rgb(0x171717)),
                        ),
                ),
            )
            .child(
                div()
                    .flex()
                    .justify_between()
                    .text_sm()
                    .text_color(super::example_rgb(0x737373))
                    .child("Optimizing bundle")
                    .child("32%"),
            )
            .child(
                Progress::new("example-progress-secondary")
                    .value(32.)
                    .child(
                        ProgressTrack::new()
                            .w_full()
                            .h(px(6.))
                            .border_1()
                            .border_color(super::example_rgb(0xa3a3a3))
                            .child(
                                ProgressIndicator::new()
                                    .w(px(83.))
                                    .h_full()
                                    .bg(super::example_rgb(0x737373)),
                            ),
                    ),
            )
    }
}
```

The command above supplies application initialization, window creation, and shared `BaseShowcase` state.

## Accessibility

Expose task label and numeric value; use indeterminate state only when progress is unknown.

## Notes

Use stable element IDs where accepted. Verify focus, hover, active, selected, disabled, reduced-motion, and high-contrast appearances in the consuming design system.

> Documentation license: original prose and illustrations for which GPUI Kit holds licensing rights are also offered under CC BY 4.0. When copying or adapting, credit GPUI Kit, link the source (https://gpui-kit.com/base/primitives/progress) and https://creativecommons.org/licenses/by/4.0/, and indicate changes. Code examples and software source use Apache-2.0; third-party material retains its terms; existing Apache-2.0 permissions remain.

> Bundled from [GPUI Kit](https://gpui-kit.com/base/primitives/progress.md). Documentation prose: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); code examples: [Apache-2.0](https://github.com/longbridge/gpui-kit/blob/main/LICENSE). Changes: documentation links localized, asset URLs made absolute, and this attribution added.
