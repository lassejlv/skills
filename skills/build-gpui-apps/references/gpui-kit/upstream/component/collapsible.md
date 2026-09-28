---
url: /component/collapsible.md
description: An interactive element which expands/collapses.
---

# Collapsible

An interactive element which expands/collapses.

## Import

```rust
use gpui_kit::component::collapsible::Collapsible;
```

## Usage

### Basic Use

```rust
Collapsible::new()
    .max_w_128()
    .gap_1()
    .open(self.open)
    .child(
        "This is a collapsible component. \
        Click the header to expand or collapse the content.",
    )
    .content(
        "This is the full content of the Collapsible component. \
        It is only visible when the component is expanded. \n\
        You can put any content you like here, including text, images, \
        or other UI elements.",
    )
    .child(
        h_flex().justify_center().child(
            Button::new("toggle1")
                .icon(IconName::ChevronDown)
                .label("Show more")
                .when(open, |this| {
                    this.icon(IconName::ChevronUp).label("Show less")
                })
                .xsmall()
                .link()
                .on_click({
                    cx.listener(move |this, _, _, cx| {
                        this.open = !this.open;
                        cx.notify();
                    })
                }),
        ),
    )
```

We can use `open` method to control the collapsed state. If false, the `content` method added child elements will be hidden.

### Animated reveal

Opt into a reversible, measured height reveal with a stable motion ID:

```rust
Collapsible::new()
    .motion_id("advanced-options")
    .open(self.open)
    .content(options)
```

The content remains mounted while closed so it can be measured and immediately reverse if toggled mid-animation. Without `motion_id`, the component keeps the immediate mount/unmount behavior. See the [GPUI Base Motion guide](../base/motion.md) for timing, reduced-motion, and performance details.

[Collapsible]: https://docs.rs/gpui-component/latest/gpui_component/collapsible/struct.Collapsible.html

> Documentation license: original prose and illustrations for which GPUI Kit holds licensing rights are also offered under CC BY 4.0. When copying or adapting, credit GPUI Kit, link the source (https://gpui-kit.com/component/collapsible) and https://creativecommons.org/licenses/by/4.0/, and indicate changes. Code examples and software source use Apache-2.0; third-party material retains its terms; existing Apache-2.0 permissions remain.

> Bundled from [GPUI Kit](https://gpui-kit.com/component/collapsible.md). Documentation prose: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); code examples: [Apache-2.0](https://github.com/longbridge/gpui-kit/blob/main/LICENSE). Changes: documentation links localized, asset URLs made absolute, and this attribution added.
