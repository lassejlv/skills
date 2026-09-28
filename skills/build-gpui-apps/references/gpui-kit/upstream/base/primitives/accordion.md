---
url: /base/primitives/accordion.md
description: A disclosure group composed from independently styleable header, trigger, and panel parts.
---

# Accordion

A disclosure group composed from independently styleable header, trigger, and panel parts.

Like every `gpui-base` primitive, Accordion supplies behavior and semantic structure without imposing a product visual language. Apply GPUI styles and compose the exported parts to match your design system.

## Example

The [single native Cargo entrypoint](https://github.com/longbridge/gpui-kit/blob/main/crates/base/examples/native/src/bin/components.rs) selects this primitive from the [shared showcase implementation](https://github.com/longbridge/gpui-kit/blob/main/crates/base/examples/showcase/mod.rs). The same showcase is compiled once for the WASM preview above.

```bash
cargo run -p gpui-base-examples -- accordion
```

## Import

```rust
use gpui_kit::base::{Accordion, AccordionHeader, AccordionItem, AccordionPanel, AccordionTrigger};
```

## Anatomy and API

The example composes `Accordion`, `AccordionHeader`, `AccordionItem`, `AccordionPanel`, `AccordionTrigger`. GPUI's standard styling and event traits provide presentation; these base types provide the interaction structure.

The authoritative module is [`components/accordion.rs`](https://github.com/longbridge/gpui-kit/blob/main/crates/base/examples/showcase/components/accordion.rs). Native and browser previews compile this same file.

## State and events

Controlled by `AccordionItem::open`; `AccordionTrigger::on_change` reports the next expanded state.

Keep controlled state on the parent render type or in a GPUI entity. Update it in callbacks and call `cx.notify()`; do not recreate persistent entities during every render.

## Complete Rust example

The complete implementation used by the runnable showcase is embedded directly from Rust source:

```rust
use super::*;

impl BaseShowcase {
    pub(in super::super) fn accordion(&self, cx: &mut Context<Self>) -> impl IntoElement {
        let items = [
            (
                "What is GPUI Base?",
                "Unstyled, accessible primitives for building native GPUI interfaces.",
            ),
            (
                "Can I bring my own theme?",
                "Yes. Every visual detail remains application-owned.",
            ),
            (
                "Does it support keyboard input?",
                "Focus, activation, and semantic state are built into the primitives.",
            ),
        ];

        Accordion::new("example-accordion")
            .w(px(270.))
            .border_t_1()
            .border_color(super::example_rgb(0xd4d4d4))
            .children(
                items
                    .into_iter()
                    .enumerate()
                    .map(|(index, (question, answer))| {
                        let open = self.accordion_items[index];
                        let entity = cx.entity().downgrade();
                        AccordionItem::new()
                            .open(open)
                            .header(AccordionHeader::new(
                                AccordionTrigger::new(format!("accordion-trigger-{index}"))
                                    .on_change(move |next, _, _, cx| {
                                        _ = entity.update(cx, |this, cx| {
                                            this.accordion_items[index] = next;
                                            cx.notify();
                                        });
                                    })
                                    .w_full()
                                    .flex()
                                    .items_center()
                                    .justify_between()
                                    .h_7()
                                    .border_b_1()
                                    .border_color(super::example_rgb(0xd4d4d4))
                                    .text_xs()
                                    .child(question)
                                    .child(
                                        div()
                                            .text_color(super::example_rgb(0x737373))
                                            .child(if open { "−" } else { "+" }),
                                    ),
                            ))
                            .panel(
                                AccordionPanel::new()
                                    .px_1()
                                    .py_1()
                                    .border_b_1()
                                    .border_color(super::example_rgb(0xd4d4d4))
                                    .text_xs()
                                    .text_color(super::example_rgb(0x525252))
                                    .child(answer),
                            )
                    }),
            )
    }
}
```

The command above supplies application initialization, window creation, and shared `BaseShowcase` state.

## Accessibility

Name every trigger, expose expanded state, and remove collapsed panel content from the focus order.

## Notes

Use stable element IDs where accepted. Verify focus, hover, active, selected, disabled, reduced-motion, and high-contrast appearances in the consuming design system.

> Documentation license: original prose and illustrations for which GPUI Kit holds licensing rights are also offered under CC BY 4.0. When copying or adapting, credit GPUI Kit, link the source (https://gpui-kit.com/base/primitives/accordion) and https://creativecommons.org/licenses/by/4.0/, and indicate changes. Code examples and software source use Apache-2.0; third-party material retains its terms; existing Apache-2.0 permissions remain.

> Bundled from [GPUI Kit](https://gpui-kit.com/base/primitives/accordion.md). Documentation prose: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); code examples: [Apache-2.0](https://github.com/longbridge/gpui-kit/blob/main/LICENSE). Changes: documentation links localized, asset URLs made absolute, and this attribution added.
