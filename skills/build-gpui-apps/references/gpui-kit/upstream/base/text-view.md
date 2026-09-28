---
url: /base/text-view.md
description: Render selectable Markdown and HTML directly with gpui-base.
---

# TextView

`gpui-base` owns the complete `TextView` implementation for rendering Markdown and common HTML. It includes document parsing, links, images, lists, tables, code blocks, scrolling, line clamping, plugins, selection, and copying without depending on `gpui-component`.

The live example above uses only `gpui-base`. Its fenced Rust block is intentionally unhighlighted: syntax highlighting is opt-in.

## Set up the window

Call `gpui_kit::base::init` once during application startup and render one `TextSelectionLayer` per window. The layer coordinates selection across `TextView`, [`SelectableText`](text-selection.md), and custom text renderers.

```rust
use gpui_kit::prelude::*;
use gpui_kit::{Context, Render, Window};
use gpui_kit::base::{TextSelectionLayer, TextView};

impl Render for AppView {
    fn render(&mut self, _window: &mut Window, _cx: &mut Context<Self>) -> impl IntoElement {
        div()
            .size_full()
            .child(TextSelectionLayer)
            .child(TextView::markdown(
                "readme",
                "# Hello\n\nSelect and copy this **Markdown**.",
            ))
    }
}
```

If the application already calls `gpui_kit::component::init`, Base initialization is included. A window using `gpui_base::Root`—including one opened by `gpui_kit::open_window`—installs the selection layer automatically; do not render a second layer in its content.

TextView is selectable by default. While dragging a selection near a viewport edge, the shared selection layer scrolls the related `overflow_*_scroll` region automatically; no TextView scroll or selection parameter is required. Use `.selectable(false)` only to disable selection explicitly.

## Markdown and HTML

Use the helpers for call-site-derived IDs, or constructors when an explicit stable ID is useful:

```rust
use gpui_kit::base::{html, markdown, TextView};

let short_markdown = markdown("A **short** message.");
let short_html = html("<p>A <strong>short</strong> message.</p>");

let preview = TextView::markdown("document-preview", markdown_source).scrollable(true);

let article = TextView::html("article", html_source);
```

`scrollable(true)` makes the view fill its container and scroll vertically. Without it, the view grows to fit its content. `max_lines(n)` clamps a non-scrollable preview to at most `n` body-text lines.

## Complete default styling

Every constructor starts with `TextViewStyle::default()`. The default contains readable neutral foreground, muted, link, selection, code-background, border, heading, paragraph, inline-code, and table styles. A Base-only application does not need to construct a style before rendering text.

Override only the values owned by your design system:

```rust
use gpui_kit::base::TextViewStyle;

let style = TextViewStyle::default()
    .with_foreground(app_colors.foreground)
    .with_muted_foreground(app_colors.muted_foreground)
    .with_link(app_colors.link)
    .with_selection(app_colors.selection);

TextView::markdown("themed", source).style(style)
```

Heading refinements receive the Markdown heading level (1-6) and are applied
on top of the built-in size, weight, and spacing for that level:

```rust
use gpui_kit::{StyleRefinement, Styled as _, rems};

let style = TextViewStyle::default().with_heading(|level| match level {
    1 => StyleRefinement::default().pt(rems(1.)).pb(rems(0.75)),
    _ => StyleRefinement::default(),
});
```

`TextViewStyle::from_theme(&theme)` maps the semantic colors from a `gpui_kit::base::Theme`. Applications using the higher-level component theme can use `gpui_kit::component::text::text_view_style(cx.theme())`.

## Syntax highlighting is opt-in

`gpui-base` does not enable syntax highlighting and has no tree-sitter language dependency. Fenced code blocks use the neutral code surface and plain foreground until the application supplies `code_block_highlighter`.

The callback receives a `CodeBlock` and returns byte ranges paired with GPUI `HighlightStyle` values:

```rust
use gpui_kit::HighlightStyle;
use gpui_kit::base::TextView;

TextView::markdown("highlighted", source).code_block_highlighter(|block| {
    my_highlighter(block.lang(), block.code())
        .into_iter()
        .map(|(range, color)| {
            (
                range,
                HighlightStyle {
                    color: Some(color),
                    ..Default::default()
                },
            )
        })
        .collect()
})
```

Ranges are UTF-8 byte ranges relative to `CodeBlock::code()`. Invalid ranges are discarded. The highlighter implementation and its language registrations remain entirely application-owned.

## Markdown extensions

`MarkdownExtensions` starts with CommonMark/GFM-compatible parsing. YAML
frontmatter is disabled by default because it is not part of either standard.
Enable the construct explicitly when a block parser or plugin handles
`markdown_ast::Node::Yaml`:

```rust
use gpui_base::{MarkdownExtensions, TextView};

let extensions = MarkdownExtensions::default().frontmatter();

TextView::markdown("metadata", source)
    .markdown_extensions(extensions)
```

Without a matching plugin, enabled YAML frontmatter uses the existing YAML
code-block fallback. A custom plugin can be attached with `.plugin(...)`;
`gpui-component` provides a themed
`FrontmatterPlugin`; Base remains independent of that presentation.

## Inline plugin

Implement `MarkdownPlugin` and register it with `.plugin(...)`, just like a Block plugin. A `MarkdownPlugin` with the default `is_block() == false` uses `render_inline`; block plugins keep `render`.

```rust
use gpui::{App, Styled, Window, div};
use gpui_base::{
    InlineElement, InlineRenderContext, MarkdownNode,
    MarkdownParseContext, MarkdownPlugin, TextView, markdown_ast,
};

struct FormulaPlugin;

impl MarkdownPlugin for FormulaPlugin {
    fn name(&self) -> &str {
        "formula"
    }

    fn parse(
        &self,
        node: &markdown_ast::Node,
        _: &MarkdownParseContext<'_>,
    ) -> Option<MarkdownNode> {
        let markdown_ast::Node::InlineMath(math) = node else {
            return None;
        };
        Some(
            MarkdownNode::new("formula", math.value.clone())
                .text(math.value.clone())
                .accessibility_label(format!("Formula: {}", math.value)),
        )
    }

    fn render_inline(
        &self,
        node: &MarkdownNode,
        _: &InlineRenderContext,
        _: &mut Window,
        _: &mut App,
    ) -> Option<InlineElement> {
        Some(InlineElement::new(div().italic().child(node.as_text().to_string())))
    }
}

TextView::markdown("inline-formulas", "Formulas $x^2$ and $y^2$")
    .plugin(FormulaPlugin)
```

`render_inline` returns `Some(InlineElement::new(element))` for any GPUI `IntoElement`, including styled text, images, and composed elements. Use native GPUI styling, hover handlers, and child events. The renderer receives `InlineRenderContext` with the effective text style, font size, line height, and rem size. These rendering types are independent of Markdown; parsing and registration in this example remain Markdown-specific.

TextView measures the element's intrinsic size and lays it out as one atom. Set `.with_baseline(px(...))` on `InlineElement` when the content needs an explicit baseline, measured from its top edge in logical pixels. Objects wrap only before or after the whole element. Fixed-size elements retain their dimensions even when wider than a line; constrain their size with GPUI styles where needed. TextView does not scale the entire element subtree.

Use `MarkdownExtensions::parser_revision(config_version)` when parser captures or plugin configuration change without changing the registered names. Keep the revision stable for equivalent registrations rebuilt during rendering; changing it reparses the existing source.

Compose a native `HoverCard` around the trigger to show a profile card. The Markdown example uses a `StyledText` label with a muted `@`, an underlined username, and a `HoverCard` anchored at `Anchor::TopCenter`. Plain copy of `[@huacnlee](mention:huacnlee)` emits the handle; Markdown copy retains the original link syntax.

Selection treats the rendered element as a whole. Double-click selects an object; triple-click selects its mixed text line. Drag selection can cross text and consecutive objects in either direction. Child events remain native GPUI events, so plugin authors should coordinate interactive controls with TextView's selection gestures.

`source_range()` exposes full-document UTF-8 byte offsets including delimiters. `.text(...)` supplies plain copy and fallback text; `.markdown(...)` supplies Markdown copy, defaulting to the original node source. Missing plain text falls back to source. `.accessibility_label(...)` supplies the accessible name, defaulting to the plain text. Returning `None` from `render_inline` uses atomic text fallback. For images, the plugin supplies loading and failure content through `img(...).with_loading(...).with_fallback(...)`.

For asynchronous resources, retain a `TextViewState`, update the application-owned cache, then call `state.invalidate_inline_layout(cx)` through the view's weak entity. This remeasures inline content and virtual-list heights without reparsing or dropping the current logical selection. Associate results with source/font/theme keys and discard obsolete completions. Render callbacks should read prepared resources; do not run an equation engine synchronously during layout. `examples/markdown` contains the formula implementation and a preview zoom control.

Inline math syntax is parsed by default. Register a plugin to customize its rendering; no separate syntax switch is needed. Inline code continues to protect dollar signs from math parsing. When no plugin claims a math node, TextView renders its original `$...$` source as literal text, so prose that merely contains dollar signs — `spent $5 and $10` — reads and copies back unchanged. Block math is parsed too: a `$$` fence becomes a block node, which a block plugin (`is_block() == true`) renders, and which falls back to a code block when no plugin claims it.

## Retained state and streaming updates

Use `TextViewState` when content changes without replacing the view:

```rust
use gpui_kit::base::{TextView, TextViewState};

let document = cx.new(|cx| TextViewState::markdown(initial_source, cx));

// Render
TextView::new(&document)

// Later
document.update(cx, |state, cx| state.set_text(updated_source, cx));
```

`TextViewMotion` is the view's motion policy. Base plays it but ships no
timing: every duration defaults to zero, so an unstyled view adopts streamed
text at once. Give `stream_fade` a duration to fade the text an update
appends in where it lands, and optionally `stream_fade_stagger` to start
each further word of one update a little after the one before it:

```rust
use std::time::Duration;

use gpui_kit::base::{Easing, TextView, TextViewMotion};

TextView::new(&document).motion(
    TextViewMotion::default()
        .with_stream_fade(Duration::from_millis(350))
        .with_stream_fade_stagger(Duration::from_millis(30))
        .with_stream_fade_easing(Easing::EaseOut),
)
```

Without a stagger each update fades as one chunk. With one, appended text is
split into words with their trailing whitespace, and CJK text into
characters; a long update compresses its stagger so the last word starts
within one fade. The tracker compares rendered text rather than source
bytes, so a `set_text` whose text extends the current one counts as an
append, and Markdown that completes as it streams (`**bo` becoming bold
`bold`) fades the changed glyphs rather than the whole paragraph. Only the
blocks the update reaches are compared, and frames are requested only while
something is still fading. Reduced motion skips the fade.

`TextViewState::set_range_highlights` paints backgrounds behind ranges of
`rendered_text()`, the text plain copy produces, so an application can show
its search results or citations without reparsing or restyling the document.
The ranges are painted, not shaped, so they never change layout.
`reveal_range` scrolls the line a range starts on into view, through the
view's own list, an enclosing `gpui::list`, or `TextView::on_reveal` for any
other container; see [Highlight ranges](../component/text-view.md#highlight-ranges)
and [Scroll to a range](../component/text-view.md#scroll-to-a-range).

Selection can copy rendered text or Markdown source through `SelectionFormat`. Link routing, code-block actions, table actions, images, and custom Markdown plugins use the same builders as the compatibility API documented on the [gpui-component TextView page](../component/text-view.md).

## Runnable source

The live preview and native command use the same Base-only source:

```rust
use gpui_base::{TextView, TextViewStyle};

use super::*;
use crate::showcase::palette::ExamplePalette;

pub const MARKDOWN: &str = include_str!("../../../../../examples/fixtures/test.md");

fn text_view_style(palette: ExamplePalette) -> TextViewStyle {
    let is_dark = palette.canvas == ExamplePalette::for_dark(true).canvas;
    TextViewStyle::default()
        .with_foreground(gpui::rgb(palette.foreground).into())
        .with_muted_foreground(gpui::rgb(palette.muted_foreground).into())
        .with_link(gpui::rgb(palette.resolve(0x007fff)).into())
        .with_code_background(gpui::rgb(palette.elevated).into())
        .with_border(gpui::rgb(palette.border).into())
        .with_inline_code(gpui::HighlightStyle {
            background_color: Some(gpui::rgb(palette.elevated).into()),
            ..Default::default()
        })
        .with_dark(is_dark)
}

impl BaseShowcase {
    pub(in super::super) fn text_view(&self, window: &Window) -> impl IntoElement {
        let palette = ExamplePalette::from_window(window);
        let style = text_view_style(palette);
        div()
            .id("text-view-example")
            .debug_selector(|| "text-view-example".into())
            .w_full()
            .h(px(560.))
            .max_h_full()
            .text_color(gpui::rgb(palette.foreground))
            .child(
                div()
                    .debug_selector(|| "text-view-markdown".into())
                    .size_full()
                    .min_h_0()
                    .overflow_hidden()
                    .child(
                        TextView::new(&self.text_view)
                            .size_full()
                            .px_4()
                            .scrollable(true)
                            .style(style),
                    ),
            )
    }
}

#[cfg(test)]
mod tests {
    use std::time::Duration;

    use gpui::{
        Modifiers, MouseButton, ScrollDelta, ScrollWheelEvent, TestAppContext, VisualTestContext,
        point, px,
    };
    use gpui_base::{TextSelection, TextViewStyle};

    use super::text_view_style;
    use crate::showcase::BaseShowcase;
    use crate::showcase::palette::ExamplePalette;

    #[test]
    fn text_view_style_uses_dark_palette_colors() {
        let style = text_view_style(ExamplePalette::for_dark(true));

        assert_eq!(style.foreground(), gpui::rgb(0xffffff).into());
        assert_eq!(style.muted_foreground(), gpui::rgb(0xa3a3a3).into());
        assert_eq!(style.code_background(), gpui::rgb(0x262626).into());
        assert_eq!(style.border(), gpui::rgb(0x404040).into());
        assert_eq!(style.selection(), TextViewStyle::default().selection());
        assert!(style.is_dark());
    }

    #[gpui::test]
    fn text_view_showcase_renders_with_base_defaults(cx: &mut TestAppContext) {
        cx.update(gpui_base::init);
        let (view, cx) =
            cx.add_window_view(|window, cx| BaseShowcase::new("text-view", window, cx));
        let cx: &mut VisualTestContext = cx;

        cx.run_until_parked();
        let example = cx
            .debug_bounds("text-view-example")
            .expect("example bounds");
        let markdown = cx
            .debug_bounds("text-view-markdown")
            .expect("Markdown bounds");
        let document = view.read_with(cx, |view, cx| view.text_view.read(cx).bounds());

        assert_eq!(markdown.left(), example.left());
        assert_eq!(markdown.right(), example.right());
        assert_eq!(document.left() - example.left(), px(16.));
        assert_eq!(example.right() - document.right(), px(16.));
    }

    #[gpui::test]
    fn text_view_showcase_drag_selection_settles(cx: &mut TestAppContext) {
        cx.update(gpui_base::init);
        let (_, cx) = cx.add_window_view(|window, cx| BaseShowcase::new("text-view", window, cx));
        let cx: &mut VisualTestContext = cx;

        cx.run_until_parked();
        let bounds = cx
            .debug_bounds("text-view-example")
            .expect("example bounds");
        // Exercise selection inside the visible, virtualized Markdown blocks.
        let start = point(bounds.left() + px(36.), bounds.top() + px(36.));
        let end = point(bounds.right() - px(36.), bounds.top() + px(180.));
        cx.simulate_mouse_down(start, MouseButton::Left, Modifiers::default());
        cx.simulate_mouse_move(end, MouseButton::Left, Modifiers::default());
        cx.simulate_mouse_up(end, MouseButton::Left, Modifiers::default());

        assert!(cx.update(|window, cx| TextSelection::has_selection(window, cx)));
    }

    #[gpui::test]
    fn text_view_showcase_scrolls_the_document_inside_a_fixed_viewport(cx: &mut TestAppContext) {
        cx.update(gpui_base::init);
        let (view, cx) =
            cx.add_window_view(|window, cx| BaseShowcase::new("text-view", window, cx));
        let cx: &mut VisualTestContext = cx;

        cx.run_until_parked();
        let viewport = cx
            .debug_bounds("text-view-markdown")
            .expect("Markdown viewport bounds");
        let example = cx
            .debug_bounds("text-view-example")
            .expect("TextView example bounds");
        let scroll_before = view.read_with(cx, |view, cx| {
            let offset = view.text_view.read(cx).list_state().logical_scroll_top();
            (offset.item_ix, offset.offset_in_item)
        });
        cx.simulate_event(ScrollWheelEvent {
            position: example.center(),
            delta: ScrollDelta::Pixels(point(px(0.), px(-120.))),
            ..Default::default()
        });
        cx.update(|window, cx| window.draw(cx).clear(cx));
        let after = cx
            .debug_bounds("text-view-markdown")
            .expect("Markdown viewport bounds after scrolling");
        let scroll_after = view.read_with(cx, |view, cx| {
            let offset = view.text_view.read(cx).list_state().logical_scroll_top();
            (offset.item_ix, offset.offset_in_item)
        });

        assert_eq!(
            after, viewport,
            "the TextView viewport itself must stay fixed"
        );
        assert_ne!(
            scroll_after, scroll_before,
            "the TextView's virtual list must consume the wheel event"
        );
    }

    #[gpui::test]
    fn dragging_selection_scrolls_the_containing_region_without_text_view_parameters(
        cx: &mut TestAppContext,
    ) {
        cx.update(gpui_base::init);
        let (view, cx) =
            cx.add_window_view(|window, cx| BaseShowcase::new("text-view", window, cx));
        let cx: &mut VisualTestContext = cx;

        cx.run_until_parked();
        let markdown = cx
            .debug_bounds("text-view-markdown")
            .expect("Markdown section bounds");
        let scroll_before = view.read_with(cx, |view, cx| {
            let offset = view.text_view.read(cx).list_state().logical_scroll_top();
            (offset.item_ix, offset.offset_in_item)
        });
        let start = point(markdown.left() + px(24.), markdown.top() + px(24.));
        let edge = point(markdown.left() + px(120.), markdown.bottom() - px(2.));
        cx.simulate_mouse_down(start, MouseButton::Left, Modifiers::default());
        cx.simulate_mouse_move(edge, MouseButton::Left, Modifiers::default());
        cx.executor().advance_clock(Duration::from_millis(64));
        cx.run_until_parked();
        cx.simulate_mouse_up(edge, MouseButton::Left, Modifiers::default());
        let scroll_after = view.read_with(cx, |view, cx| {
            let offset = view.text_view.read(cx).list_state().logical_scroll_top();
            (offset.item_ix, offset.offset_in_item)
        });

        assert!(
            scroll_after != scroll_before,
            "dragging at the viewport edge must scroll the TextView document"
        );
        cx.executor().advance_clock(Duration::from_millis(64));
        cx.run_until_parked();
        let scroll_stopped = view.read_with(cx, |view, cx| {
            let offset = view.text_view.read(cx).list_state().logical_scroll_top();
            (offset.item_ix, offset.offset_in_item)
        });
        assert_eq!(
            scroll_stopped, scroll_after,
            "selection auto-scroll must stop on mouse-up"
        );
    }
}
```

```bash
cargo run -p gpui-base-examples -- text-view
```

> Documentation license: original prose and illustrations for which GPUI Kit holds licensing rights are also offered under CC BY 4.0. When copying or adapting, credit GPUI Kit, link the source (https://gpui-kit.com/base/text-view) and https://creativecommons.org/licenses/by/4.0/, and indicate changes. Code examples and software source use Apache-2.0; third-party material retains its terms; existing Apache-2.0 permissions remain.

> Bundled from [GPUI Kit](https://gpui-kit.com/base/text-view.md). Documentation prose: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); code examples: [Apache-2.0](https://github.com/longbridge/gpui-kit/blob/main/LICENSE). Changes: documentation links localized, asset URLs made absolute, and this attribution added.
