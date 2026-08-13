//! Compile-checked reference patterns for the `build-gpui-apps` skill.
//!
//! This is deliberately a small application, not a component framework. Copy
//! patterns only after checking the target project's pinned GPUI revision,
//! theme, component library, and platform policy.

use std::{
    ops::Range,
    time::{Duration, Instant},
};

use gpui::{
    App, AppContext as _, Bounds, Context, EventEmitter, FocusHandle, KeyBinding, Menu, MenuItem,
    Render, Rgba, Role, SharedString, Subscription, Task, UniformListScrollHandle, Window,
    WindowBounds, WindowOptions, actions, div, prelude::*, px, rgb, size, uniform_list,
};
use gpui_platform::application;

#[path = "../../spring.rs"]
mod spring;

use spring::{Spring1D, SpringConfig, projected_position, rubber_band};

actions!(
    gpui_reference_app,
    [Increment, Reset, StartLoad, NewWindow, Quit]
);

#[derive(Clone, Debug, PartialEq, Eq)]
enum LoadState {
    Idle,
    Loading { generation: u64 },
    Ready { generation: u64, rows: usize },
}

impl LoadState {
    fn label(&self) -> SharedString {
        match self {
            Self::Idle => "Ready to load".into(),
            Self::Loading { generation } => format!("Loading request {generation}").into(),
            Self::Ready { generation, rows } => {
                format!("Request {generation} loaded {rows} rows").into()
            }
        }
    }
}

#[derive(Clone)]
struct ReferenceItem {
    id: u64,
    label: SharedString,
}

#[derive(Clone, Copy)]
struct DisplayPreferences {
    dark: bool,
    active_window: bool,
    reduce_transparency: bool,
    increase_contrast: bool,
}

#[derive(Clone, Copy)]
struct MaterialTokens {
    canvas: Rgba,
    surface: Rgba,
    border: Rgba,
    text: Rgba,
    secondary_text: Rgba,
    accent: Rgba,
    focus_ring: Rgba,
}

fn material_tokens(preferences: DisplayPreferences) -> MaterialTokens {
    let mut tokens = if preferences.dark {
        MaterialTokens {
            canvas: rgb(0x111318),
            surface: rgb(0x252932),
            border: rgb(0x454b59),
            text: rgb(0xf4f6fb),
            secondary_text: rgb(0xa9b0bf),
            accent: rgb(0x77a8ff),
            focus_ring: rgb(0xa8c6ff),
        }
    } else {
        MaterialTokens {
            canvas: rgb(0xf1f3f7),
            surface: rgb(0xffffff),
            border: rgb(0xc9ced8),
            text: rgb(0x17191f),
            secondary_text: rgb(0x5f6673),
            accent: rgb(0x225cc5),
            focus_ring: rgb(0x174fae),
        }
    };

    if preferences.reduce_transparency {
        // This sample uses an opaque fallback. It does not claim native blur.
        tokens.surface = if preferences.dark {
            rgb(0x20242c)
        } else {
            rgb(0xffffff)
        };
    }

    if preferences.increase_contrast {
        tokens.border = if preferences.dark {
            rgb(0xd9deea)
        } else {
            rgb(0x20242c)
        };
        tokens.secondary_text = tokens.text;
    }

    if !preferences.active_window {
        tokens.accent = tokens.secondary_text;
    }

    tokens
}

struct CountChanged(i32);

struct ReferenceView {
    count: i32,
    announcement: SharedString,
    load_state: LoadState,
    generation: u64,
    _load_task: Option<Task<()>>,
    items: Vec<ReferenceItem>,
    scroll_handle: UniformListScrollHandle,
    focus_handle: FocusHandle,
    _count_subscription: Subscription,
    spring: Spring1D,
    spring_config: SpringConfig,
    last_frame: Option<Instant>,
}

impl EventEmitter<CountChanged> for ReferenceView {}

impl ReferenceView {
    fn new(window: &mut Window, cx: &mut Context<Self>) -> Self {
        let count_subscription = cx.subscribe_self(|this: &mut Self, event: &CountChanged, cx| {
            this.announcement = format!("Count changed to {}", event.0).into();
            cx.notify();
        });

        let focus_handle = cx.focus_handle();
        focus_handle.focus(window, cx);

        Self {
            count: 0,
            announcement: "Count is zero".into(),
            load_state: LoadState::Idle,
            generation: 0,
            _load_task: None,
            items: (1..=250)
                .map(|id| ReferenceItem {
                    id,
                    label: format!("Stable row {id}").into(),
                })
                .collect(),
            scroll_handle: UniformListScrollHandle::new(),
            focus_handle,
            _count_subscription: count_subscription,
            spring: Spring1D::new(0.0),
            spring_config: SpringConfig::default(),
            last_frame: None,
        }
    }

    fn apply_increment(&mut self, cx: &mut Context<Self>) {
        self.count += 1;
        self.spring.retarget(self.count as f32);
        self.last_frame = Some(Instant::now());
        cx.emit(CountChanged(self.count));
        cx.notify();
    }

    fn increment(&mut self, _: &Increment, _window: &mut Window, cx: &mut Context<Self>) {
        self.apply_increment(cx);
    }

    fn reset(&mut self, _: &Reset, _window: &mut Window, cx: &mut Context<Self>) {
        self.count = 0;
        self.spring.retarget(0.0);
        self.last_frame = Some(Instant::now());
        cx.emit(CountChanged(self.count));
        cx.notify();
    }

    fn start_load(&mut self, _: &StartLoad, _window: &mut Window, cx: &mut Context<Self>) {
        self.begin_load(cx);
    }

    fn begin_load(&mut self, cx: &mut Context<Self>) {
        self.generation += 1;
        let generation = self.generation;
        self.load_state = LoadState::Loading { generation };
        cx.notify();

        // Replacing the held task cancels the older request. The generation
        // also rejects a result if cancellation cannot stop external work.
        self._load_task = Some(cx.spawn(async move |this, cx| {
            cx.background_executor()
                .timer(Duration::from_millis(120))
                .await;

            this.update(cx, |view, cx| {
                if view.generation != generation {
                    return;
                }

                view.load_state = LoadState::Ready {
                    generation,
                    rows: view.items.len(),
                };
                cx.notify();
            })
            .ok();
        }));
    }

    fn tick_spring(&mut self, window: &mut Window, cx: &mut Context<Self>) {
        if self.spring.is_settled(self.spring_config) {
            self.last_frame = None;
            return;
        }

        if cx.reduce_motion() {
            self.spring.snap_to(self.spring.target);
            self.last_frame = None;
            return;
        }

        let now = Instant::now();
        let elapsed = self
            .last_frame
            .replace(now)
            .map_or(0.0, |last| (now - last).as_secs_f32());

        if self.spring.step(elapsed, self.spring_config) {
            window.request_animation_frame();
        } else {
            self.last_frame = None;
        }
    }
}

impl Render for ReferenceView {
    fn render(&mut self, window: &mut Window, cx: &mut Context<Self>) -> impl IntoElement {
        self.tick_spring(window, cx);

        let preferences = DisplayPreferences {
            dark: true,
            active_window: window.is_window_active(),
            reduce_transparency: false,
            increase_contrast: false,
        };
        let tokens = material_tokens(preferences);
        let loading = matches!(self.load_state, LoadState::Loading { .. });
        let status = self.load_state.label();
        let total_items = self.items.len();
        let projected_count = projected_position(self.spring.value, self.spring.velocity, 0.9);
        let resisted_overshoot = rubber_band(self.spring.value - self.spring.target, 100.0, 0.55);

        // The repeated controls are intentionally explicit: each has a stable
        // identity, semantic role, keyboard context, disabled policy, and
        // focus-visible treatment.
        let increment = div()
            .id("increment")
            .accessibility_id("reference.increment")
            .key_context("ReferenceIncrement")
            .focusable()
            .tab_stop(true)
            .role(Role::Button)
            .aria_label("Increment count")
            .aria_keyshortcuts("Enter Space")
            .px(px(12.0))
            .py(px(7.0))
            .rounded(px(8.0))
            .border_1()
            .border_color(tokens.border)
            .bg(tokens.surface)
            .text_color(tokens.text)
            .cursor_pointer()
            .hover(|style| style.bg(rgb(0x333947)))
            .focus_visible(|style| style.border_color(tokens.focus_ring))
            .on_click(cx.listener(|this, _, _, cx| this.apply_increment(cx)))
            .child("Increment");

        let reset = div()
            .id("reset")
            .accessibility_id("reference.reset")
            .key_context("ReferenceReset")
            .focusable()
            .tab_stop(true)
            .role(Role::Button)
            .aria_label("Reset count")
            .aria_keyshortcuts("Enter Space")
            .px(px(12.0))
            .py(px(7.0))
            .rounded(px(8.0))
            .border_1()
            .border_color(tokens.border)
            .bg(tokens.surface)
            .text_color(tokens.text)
            .cursor_pointer()
            .hover(|style| style.bg(rgb(0x333947)))
            .focus_visible(|style| style.border_color(tokens.focus_ring))
            .on_click(cx.listener(|this, _, window, cx| this.reset(&Reset, window, cx)))
            .child("Reset");

        let load = div()
            .id("load")
            .accessibility_id("reference.load")
            .key_context("ReferenceLoad")
            .focusable()
            .tab_stop(!loading)
            .role(Role::Button)
            .aria_label(if loading { "Loading rows" } else { "Load rows" })
            .aria_keyshortcuts("Enter Space")
            .px(px(12.0))
            .py(px(7.0))
            .rounded(px(8.0))
            .border_1()
            .border_color(tokens.border)
            .bg(if loading {
                rgb(0x2b3039)
            } else {
                tokens.accent
            })
            .text_color(tokens.text)
            .when(!loading, |this| {
                this.cursor_pointer()
                    .hover(|style| style.bg(rgb(0x477bd7)))
                    .focus_visible(|style| style.border_color(tokens.focus_ring))
                    .on_click(cx.listener(|this, _, _, cx| this.begin_load(cx)))
            })
            .child(if loading { "Loading…" } else { "Load rows" });

        div()
            .id("reference-root")
            .accessibility_id("reference.application")
            .role(Role::Application)
            .aria_label("GPUI reference application")
            .track_focus(&self.focus_handle)
            .on_action(cx.listener(Self::increment))
            .on_action(cx.listener(Self::reset))
            .on_action(cx.listener(Self::start_load))
            .size_full()
            .flex()
            .flex_col()
            .gap(px(12.0))
            .p(px(16.0))
            .bg(tokens.canvas)
            .text_color(tokens.text)
            .child(
                div()
                    .flex()
                    .items_center()
                    .justify_between()
                    .child(
                        div()
                            .flex()
                            .flex_col()
                            .gap(px(3.0))
                            .child(
                                div()
                                    .text_size(px(20.0))
                                    .font_weight(gpui::FontWeight::SEMIBOLD)
                                    .child("Compile-checked GPUI patterns"),
                            )
                            .child(
                                div()
                                    .text_size(px(13.0))
                                    .text_color(tokens.secondary_text)
                                    .child("Opaque material fallback; no fake backdrop blur"),
                            ),
                    )
                    .child(
                        div()
                            .id("count-status")
                            .role(Role::Status)
                            .aria_label(self.announcement.clone())
                            .text_color(tokens.accent)
                            .child(format!(
                                "Count {} · spring {:.2} · projected {:.2} · resistance {:.2}",
                                self.count, self.spring.value, projected_count, resisted_overshoot,
                            )),
                    ),
            )
            .child(
                div()
                    .flex()
                    .items_center()
                    .gap(px(8.0))
                    .child(increment)
                    .child(reset)
                    .child(load)
                    .child(
                        div()
                            .id("load-status")
                            .role(Role::Status)
                            .aria_label(status.clone())
                            .ml(px(4.0))
                            .text_size(px(12.0))
                            .text_color(tokens.secondary_text)
                            .child(status),
                    ),
            )
            .child(
                div()
                    .id("row-list")
                    .accessibility_id("reference.rows")
                    .role(Role::List)
                    .aria_label("Reference rows")
                    .flex_1()
                    .min_h_0()
                    .overflow_hidden()
                    .rounded(px(10.0))
                    .border_1()
                    .border_color(tokens.border)
                    .bg(tokens.surface)
                    .child(
                        uniform_list(
                            "reference-items",
                            total_items,
                            cx.processor(move |this, range: Range<usize>, _, _| {
                                range
                                    .filter_map(|index| {
                                        this.items.get(index).map(|item| {
                                            div()
                                                .id(("reference-row", item.id))
                                                .accessibility_id(format!(
                                                    "reference.row.{}",
                                                    item.id
                                                ))
                                                .role(Role::ListItem)
                                                .aria_label(item.label.clone())
                                                .aria_position_in_set(index + 1)
                                                .aria_size_of_set(total_items)
                                                .h(px(34.0))
                                                .px(px(10.0))
                                                .flex()
                                                .items_center()
                                                .border_b_1()
                                                .border_color(tokens.border)
                                                .child(item.label.clone())
                                        })
                                    })
                                    .collect::<Vec<_>>()
                            }),
                        )
                        .size_full()
                        .track_scroll(&self.scroll_handle),
                    ),
            )
    }
}

fn open_reference_window(cx: &mut App) {
    let bounds = Bounds::centered(None, size(px(760.0), px(620.0)), cx);
    cx.open_window(
        WindowOptions {
            focus: true,
            window_bounds: Some(WindowBounds::Windowed(bounds)),
            ..Default::default()
        },
        |window, cx| cx.new(|cx| ReferenceView::new(window, cx)),
    )
    .expect("open reference window");
}

fn new_window(_: &NewWindow, cx: &mut App) {
    open_reference_window(cx);
}

fn quit(_: &Quit, cx: &mut App) {
    cx.quit();
}

fn platform_key_bindings() -> Vec<KeyBinding> {
    let mut bindings = vec![
        KeyBinding::new("enter", Increment, Some("ReferenceIncrement")),
        KeyBinding::new("space", Increment, Some("ReferenceIncrement")),
        KeyBinding::new("enter", Reset, Some("ReferenceReset")),
        KeyBinding::new("space", Reset, Some("ReferenceReset")),
        KeyBinding::new("enter", StartLoad, Some("ReferenceLoad")),
        KeyBinding::new("space", StartLoad, Some("ReferenceLoad")),
    ];

    #[cfg(target_os = "macos")]
    bindings.extend([
        KeyBinding::new("cmd-n", NewWindow, None),
        KeyBinding::new("cmd-q", Quit, None),
    ]);

    #[cfg(not(target_os = "macos"))]
    bindings.extend([
        KeyBinding::new("ctrl-n", NewWindow, None),
        KeyBinding::new("ctrl-q", Quit, None),
    ]);

    bindings
}

fn main() {
    application().run(|cx: &mut App| {
        cx.on_action(new_window);
        cx.on_action(quit);
        cx.bind_keys(platform_key_bindings());
        cx.set_menus([Menu::new("Reference").items([
            MenuItem::action("New Window", NewWindow),
            MenuItem::separator(),
            MenuItem::action("Quit", Quit),
        ])]);
        cx.on_window_closed(|cx, _| {
            if cx.windows().is_empty() {
                cx.quit();
            }
        })
        .detach();

        open_reference_window(cx);
        cx.activate(true);
    });
}

#[cfg(test)]
mod tests {
    use super::*;
    use gpui::{TestAppContext, VisualTestContext};

    #[test]
    fn opaque_and_high_contrast_materials_are_explicit() {
        let regular = material_tokens(DisplayPreferences {
            dark: true,
            active_window: true,
            reduce_transparency: false,
            increase_contrast: false,
        });
        let accessible = material_tokens(DisplayPreferences {
            dark: true,
            active_window: true,
            reduce_transparency: true,
            increase_contrast: true,
        });

        assert_ne!(regular.surface, accessible.surface);
        assert_eq!(accessible.secondary_text, accessible.text);
    }

    #[gpui::test]
    fn entity_event_updates_the_owned_announcement(cx: &mut TestAppContext) {
        let view = cx.new(|cx| {
            let count_subscription =
                cx.subscribe_self(|this: &mut ReferenceView, event: &CountChanged, cx| {
                    this.announcement = format!("Count changed to {}", event.0).into();
                    cx.notify();
                });

            ReferenceView {
                count: 0,
                announcement: "Count is zero".into(),
                load_state: LoadState::Idle,
                generation: 0,
                _load_task: None,
                items: Vec::new(),
                scroll_handle: UniformListScrollHandle::new(),
                focus_handle: cx.focus_handle(),
                _count_subscription: count_subscription,
                spring: Spring1D::new(0.0),
                spring_config: SpringConfig::default(),
                last_frame: None,
            }
        });

        view.update(cx, |view, cx| view.apply_increment(cx));

        assert_eq!(
            view.read_with(cx, |view, _| view.announcement.clone()),
            SharedString::from("Count changed to 1")
        );
    }

    #[gpui::test]
    fn action_dispatch_changes_entity_state(cx: &mut TestAppContext) {
        let window = cx.update(|cx| {
            cx.open_window(Default::default(), |window, cx| {
                cx.new(|cx| ReferenceView::new(window, cx))
            })
            .unwrap()
        });
        let mut cx = VisualTestContext::from_window(window.into(), cx);
        let view = window.root(&mut cx).unwrap();
        let focus_handle = view.read_with(&cx, |view, _| view.focus_handle.clone());

        cx.update(|window, cx| {
            focus_handle.dispatch_action(&Increment, window, cx);
        });

        assert_eq!(view.read_with(&cx, |view, _| view.count), 1);
    }

    #[gpui::test]
    fn replacing_load_rejects_the_old_generation(cx: &mut TestAppContext) {
        let view = cx.new(|cx| {
            let count_subscription =
                cx.subscribe_self(|_: &mut ReferenceView, _: &CountChanged, _| {});

            ReferenceView {
                count: 0,
                announcement: "Count is zero".into(),
                load_state: LoadState::Idle,
                generation: 0,
                _load_task: None,
                items: (1..=5)
                    .map(|id| ReferenceItem {
                        id,
                        label: format!("Row {id}").into(),
                    })
                    .collect(),
                scroll_handle: UniformListScrollHandle::new(),
                focus_handle: cx.focus_handle(),
                _count_subscription: count_subscription,
                spring: Spring1D::new(0.0),
                spring_config: SpringConfig::default(),
                last_frame: None,
            }
        });

        view.update(cx, |view, cx| {
            view.begin_load(cx);
            view.begin_load(cx);
        });
        cx.run_until_parked();
        cx.executor().advance_clock(Duration::from_millis(120));
        cx.run_until_parked();

        assert_eq!(
            view.read_with(cx, |view, _| view.load_state.clone()),
            LoadState::Ready {
                generation: 2,
                rows: 5,
            }
        );
    }
}
