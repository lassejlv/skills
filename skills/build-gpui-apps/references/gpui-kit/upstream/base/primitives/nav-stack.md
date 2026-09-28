---
url: /base/primitives/nav-stack.md
description: A navigation stack of views with push, pop, forward, and replace, and an animatable transition lifecycle.
---

# Nav Stack

A last-in-first-out stack of views, one visible at a time: push a view over the current one, pop back to the one below, or replace the top. It is SwiftUI's `NavigationStack`, Qt's `StackView`, and WinUI's `Frame`. Underneath it is a [History](../history.md) whose active entries run from the root through the current page. A popped page becomes a forward entry until the next push discards that forward branch, so `forward` brings it back the way WinUI's `GoForward` does.

Like every `gpui-base` primitive, Nav Stack supplies behavior and semantic structure without imposing a product visual language. The pages are views you create, and how a change between them moves is decided by your item renderer.

## Example

The [single native Cargo entrypoint](https://github.com/longbridge/gpui-kit/blob/main/crates/base/examples/native/src/bin/components.rs) selects this primitive from the [shared showcase implementation](https://github.com/longbridge/gpui-kit/blob/main/crates/base/examples/showcase/mod.rs). The same showcase is compiled once for the WASM preview above.

```bash
cargo run -p gpui-base-examples -- nav-stack
```

## Import

```rust
use gpui_kit::base::{NavMotion, NavOperation, NavPage, NavStack, NavStackState};
use gpui_kit::base::motion::{PresencePhase, Transition};
```

## Anatomy and API

`NavStackState` is the stack. It lives in a GPUI entity, holds `AnyView`s root first, and emits `NavStackEvent` after every change.

| Method                                                             | Does                                                                                                                                    |
| ------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------- |
| `push(view, motion, cx)`                                           | Pushes over the current top. Into an empty stack it is immediate, like Qt's `initialItem`.                                              |
| `pop(motion, cx)`                                                  | Pops the top and returns it. The root is never popped, so this returns `None` at a depth of one.                                        |
| `pop_to_root(motion, cx)`                                          | Pops everything above the root in one transition and returns those views.                                                               |
| `forward(motion, cx)`                                              | Brings back the most recently popped view over the current top and returns it. `None` when nothing has been popped since the last push. |
| `replace(view, motion, cx)`                                        | Swaps the top for `view` and returns the one replaced, keeping the forward views. On an empty stack it pushes.                          |
| `clear(cx)`                                                        | Empties the stack and the forward views immediately.                                                                                    |
| `depth()`, `is_empty()`, `current()`, `views()`, `forward_views()` | Read the stack. Show a back button when `depth() > 1`, a forward button when `forward_views()` is not empty.                            |

`NavStack` is the element. It holds the entity, takes a `transition` to run each change under, and hands every mounted view to the `item` renderer as a `NavPage`. Style the element for size, background and clipping; it is positioned so that the two pages of a change can overlap.

`NavPage` is what the renderer receives. It already fills the container. Read `phase()` (`Entering`, `Present` or `Exiting`), `operation()` (`Push`, `Pop` or `Replace`, or `None` once settled) and `progress()` (eased, `0.0` to `1.0`, shared by both pages of one change), refine the page with GPUI styles, and return it.

The authoritative module is [`components/nav_stack.rs`](https://github.com/longbridge/gpui-kit/blob/main/crates/base/examples/showcase/components/nav_stack.rs). Native and browser previews compile this same file.

## Animation

Animation is decided at two levels, and both default to none:

- **The stack.** `NavStack` without a `transition` never animates; every change switches on the spot. Give it a `Transition` to animate changes, and an `item` renderer to say how.
- **The change.** Each `push`, `pop`, `pop_to_root` and `replace` takes a `NavMotion`, as UIKit's `animated:` and Qt's `StackView.Immediate` do per call. `NavMotion::Animated` runs the stack's transition; `NavMotion::Immediate` switches on the spot even on an animated stack, which is what restoring a stack at launch or jumping to a page from a command wants.

```rust
stack.update(cx, |stack, cx| stack.push(detail, NavMotion::Animated, cx));
stack.update(cx, |stack, cx| stack.push(restored, NavMotion::Immediate, cx));
```

## Transitions

After a push, pop or replace, the outgoing view stays mounted until the element's `Transition` finishes. Paint order follows the operation: a pushed or replacing page paints over the page it covers, and a popped page paints over the page it reveals, so a slide reads correctly in both directions.

```rust
NavStack::new(&self.stack)
    .size_full()
    .overflow_hidden()
    .transition(Transition::new(Duration::from_millis(220)))
    .item(|page, _, _| {
        let offset = match (page.phase(), page.operation()) {
            (PresencePhase::Entering, Some(NavOperation::Push)) => 1.0 - page.progress(),
            (PresencePhase::Exiting, Some(NavOperation::Pop)) => page.progress(),
            _ => 0.0,
        };
        page.left(relative(offset)).into_any_element()
    })
```

The stack also switches immediately when the platform asks for reduced motion, whatever the renderer would have drawn. A new operation while a transition is running supersedes it, and the pages reverse from where they are rather than jumping. While a change runs, neither page takes pointer input.

## State and events

Keep the `NavStackState` entity on the view that renders the stack and observe it, so a push from anywhere re-renders the host. A page that needs to navigate holds a `WeakEntity` of the stack, as the showcase page does.

`views()` and `forward_views()` are enough for a history menu: list both, and pop or forward until the chosen page is current. The showcase page draws that list as a trail of page numbers, the pages ahead greyed out.

Focus is not moved by the stack. `AnyView` carries no focus handle; a page that wants focus takes it when it is pushed, as it would anywhere else.

## Complete Rust example

The complete implementation used by the runnable showcase is embedded directly from Rust source:

```rust
use super::*;
use gpui::{AnyElement, WeakEntity, relative};
use gpui_base::NavPage;
use gpui_base::motion::{PresencePhase, Transition};
use std::time::Duration;

/// One page of the stack. A page knows its depth and holds the stack it lives
/// in, so its own buttons can push over it, replace it, or pop it.
pub(in super::super) struct ShowcasePage {
    depth: usize,
    stack: WeakEntity<NavStackState>,
}

impl ShowcasePage {
    pub(in super::super) fn new(depth: usize, stack: WeakEntity<NavStackState>) -> Self {
        Self { depth, stack }
    }

    /// A click handler that builds a page at `depth` and hands it to `apply`:
    /// a pushed page sits one deeper, a replacement at the same depth.
    fn navigate(
        &self,
        depth: usize,
        apply: impl Fn(&mut NavStackState, gpui::Entity<ShowcasePage>, &mut Context<NavStackState>)
        + 'static,
    ) -> impl Fn(&gpui::ClickEvent, &mut Window, &mut App) + 'static {
        let stack = self.stack.clone();
        move |_, _, cx| {
            _ = stack.update(cx, |state, cx| {
                let page = cx.new(|_| ShowcasePage::new(depth, stack.clone()));
                apply(state, page, cx);
            });
        }
    }
}

impl Render for ShowcasePage {
    fn render(&mut self, _: &mut Window, cx: &mut Context<Self>) -> impl IntoElement {
        let depth = self.depth;
        // The trail is the stack's `History`: the pages behind this one, then
        // the pages popped off it, which `forward` brings back one at a time.
        let (behind, ahead) = self
            .stack
            .upgrade()
            .map(|stack| {
                let stack = stack.read(cx);
                (stack.depth(), stack.forward_views().len())
            })
            .unwrap_or((depth, 0));
        let button = |id: &'static str, label: &'static str| {
            Button::new(id)
                .h_7()
                .px_2()
                .flex()
                .items_center()
                .border_1()
                .border_color(example_rgb(0x171717))
                .bg(example_rgb(0xffffff))
                .child(label)
        };
        div()
            .size_full()
            .flex()
            .flex_col()
            .gap_3()
            .p_3()
            .bg(example_rgb(if depth % 2 == 1 {
                0xffffff
            } else {
                0xf5f5f5
            }))
            .child(
                div()
                    .font_weight(gpui::FontWeight::SEMIBOLD)
                    .child(format!("Page {depth}")),
            )
            .child(
                div()
                    .flex()
                    .gap_1()
                    .text_color(example_rgb(0x737373))
                    .children((1..=behind + ahead).map(|page| {
                        div()
                            .px_1()
                            .when(page == depth, |this| {
                                this.text_color(example_rgb(0x171717))
                                    .font_weight(gpui::FontWeight::SEMIBOLD)
                            })
                            .when(page > behind, |this| this.text_color(example_rgb(0xd4d4d4)))
                            .child(page.to_string())
                    })),
            )
            .child(
                div()
                    .flex()
                    .gap_2()
                    .child(button("push", "Push").on_click(
                        self.navigate(depth + 1, |stack, page, cx| {
                            stack.push(page, NavMotion::Animated, cx)
                        }),
                    ))
                    .child(button("replace", "Replace").on_click(self.navigate(
                        depth,
                        |stack, page, cx| {
                            stack.replace(page, NavMotion::Animated, cx);
                        },
                    )))
                    .when(depth > 1, |this| {
                        let stack = self.stack.clone();
                        this.child(button("pop", "Pop").on_click(move |_, _, cx| {
                            _ = stack.update(cx, |stack, cx| {
                                stack.pop(NavMotion::Animated, cx);
                            });
                        }))
                    })
                    .when(ahead > 0, |this| {
                        let stack = self.stack.clone();
                        this.child(button("forward", "Forward").on_click(move |_, _, cx| {
                            _ = stack.update(cx, |stack, cx| {
                                stack.forward(NavMotion::Animated, cx);
                            });
                        }))
                    }),
            )
    }
}

impl BaseShowcase {
    pub(in super::super) fn nav_stack(&self) -> impl IntoElement {
        NavStack::new(&self.stack)
            .w_72()
            .h_40()
            .overflow_hidden()
            .border_1()
            .border_color(example_rgb(0xd4d4d4))
            .transition(Transition::new(Duration::from_millis(220)))
            .item(|page, _, _| slide(page))
    }
}

/// A pushed page slides in from the right and slides back out when popped;
/// the page underneath drifts a little to show depth. A replacement slides in
/// over the page it replaces. The showcase's own shell uses this too.
pub(in super::super) fn slide(page: NavPage) -> AnyElement {
    let offset = match (page.phase(), page.operation()) {
        (PresencePhase::Entering, Some(NavOperation::Push | NavOperation::Replace)) => {
            1.0 - page.progress()
        }
        (PresencePhase::Exiting, Some(NavOperation::Pop)) => page.progress(),
        (PresencePhase::Exiting, Some(NavOperation::Push)) => -0.3 * page.progress(),
        (PresencePhase::Entering, Some(NavOperation::Pop)) => -0.3 * (1.0 - page.progress()),
        _ => 0.0,
    };
    page.left(relative(offset)).into_any_element()
}
```

The command above supplies application initialization, window creation, and shared `BaseShowcase` state.

## Accessibility

Announce the page change in the page itself: a heading at the top of each page gives assistive technology a landmark to land on after a push. The stack keeps only the current page interactive once a transition has finished.

## Notes

Pages are entities. The stack retains the ones on it and the ones popped since the last push, which `forward` can bring back, so a page's own subscriptions and timers live until a push discards it or the stack is cleared. Verify reduced-motion behavior in the consuming design system.

> Documentation license: original prose and illustrations for which GPUI Kit holds licensing rights are also offered under CC BY 4.0. When copying or adapting, credit GPUI Kit, link the source (https://gpui-kit.com/base/primitives/nav-stack) and https://creativecommons.org/licenses/by/4.0/, and indicate changes. Code examples and software source use Apache-2.0; third-party material retains its terms; existing Apache-2.0 permissions remain.

> Bundled from [GPUI Kit](https://gpui-kit.com/base/primitives/nav-stack.md). Documentation prose: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); code examples: [Apache-2.0](https://github.com/longbridge/gpui-kit/blob/main/LICENSE). Changes: documentation links localized, asset URLs made absolute, and this attribution added.
