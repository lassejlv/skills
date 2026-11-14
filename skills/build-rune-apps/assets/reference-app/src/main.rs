//! A small task list built with Rune and rune-kit: the build-rune-apps skill's compile-checked
//! reference app. One state, one view of it, rune-kit controls, keyed rows, scenes for headless
//! renders and tests that drive the real view.
//!
//! ```sh
//! cargo run                                                  # the window
//! cargo run -- --snap out/many.png --scene many --theme dark # a PNG, no window
//! cargo run -- --tree out/tree.json                          # elements and accessibility
//! cargo run -- --script scripts/add-task.json --snap out/after.png --at mark:end
//! cargo test
//! ```

use std::sync::LazyLock;

use rune::tok::radius;
use rune::{AppSpec, Chord, Cx, El, KeyEvent, ScrollSpec, TextEdit, Tx, col, row, text};
use rune_kit::{Button, ButtonVariant, Checkbox, Kit, Switch, TextInput};

/// ⇧⌘H on macOS, Ctrl+Shift+H elsewhere.
static HIDE_DONE: LazyLock<Chord> =
    LazyLock::new(|| Chord::parse("mod+shift+h").expect("a valid chord"));

struct Task {
    id: u32,
    title: String,
    done: bool,
}

struct State {
    tasks: Vec<Task>,
    next: u32,
    draft: TextEdit,
    hide_done: bool,
}

impl State {
    fn new() -> Self {
        let mut s = State {
            tasks: Vec::new(),
            next: 0,
            draft: TextEdit::new(""),
            hide_done: false,
        };
        for title in [
            "Read the skill",
            "Render a scene headless",
            "Inspect the tree",
        ] {
            s.push(title);
        }
        s.tasks[0].done = true;
        s
    }

    fn push(&mut self, title: &str) {
        self.tasks.push(Task {
            id: self.next,
            title: title.to_owned(),
            done: false,
        });
        self.next += 1;
    }

    /// Adds the draft as a task and empties the field, keeping its focus. A blank draft does nothing.
    fn add_draft(&mut self) {
        let title = self.draft.text.trim().to_owned();
        if title.is_empty() {
            return;
        }
        self.push(&title);
        self.draft.clear();
    }

    fn toggle(&mut self, id: u32) {
        if let Some(task) = self.tasks.iter_mut().find(|t| t.id == id) {
            task.done = !task.done;
        }
    }

    fn remove(&mut self, id: u32) {
        self.tasks.retain(|t| t.id != id);
    }
}

fn view(s: &State, cx: &mut Cx<State>) -> El {
    let k = Kit::neutral(cx.system_dark());
    let c = &k.c;

    let field = TextInput::new(&s.draft)
        .placeholder("New task")
        .label("New task")
        .width(None)
        .on_edit(|s: &mut State| &mut s.draft)
        .on_submit(|s: &mut State, _: &mut Tx| s.add_draft())
        .build(&k)
        .key("draft");
    let add = Button::new("Add")
        .variant(ButtonVariant::Contrast)
        .disabled(s.draft.text.trim().is_empty())
        .on_press(|s: &mut State| s.add_draft())
        .build(&k)
        .key("add");
    let composer = row()
        .key("composer")
        .w_full()
        .gap(8.0)
        .center_y()
        .child(col().grow(1.0).child(field))
        .child(add);

    // Rows are keyed by the task's id, so they keep their identity (and animate in and out) as
    // the list changes. rune-kit keys its own parts, so app keys inside a row go by path:
    // "task-3/check".
    let mut list = col().key("tasks").w_full().gap(2.0);
    let mut shown = 0;
    for task in s.tasks.iter().filter(|t| !(s.hide_done && t.done)) {
        shown += 1;
        let id = task.id;
        let check = Checkbox::new(task.done)
            .label(task.title.clone())
            .on_toggle(move |s: &mut State| s.toggle(id))
            .build(&k)
            .key("check");
        let remove = Button::new("Remove")
            .variant(ButtonVariant::GhostMuted)
            .on_press(move |s: &mut State| s.remove(id))
            .build(&k)
            .key("remove");
        list = list.child(
            row()
                .key(format!("task-{id}"))
                .w_full()
                .h(36.0)
                .px(8.0)
                .gap(8.0)
                .center_y()
                .radius(radius::SM)
                .child(col().grow(1.0).child(check))
                .child(remove),
        );
    }
    if shown == 0 {
        let note = if s.tasks.is_empty() {
            "No tasks yet"
        } else {
            "Everything is done"
        };
        list = list.child(text(note).key("empty").font(k.ty.body).color(c.text_muted));
    }

    let done = s.tasks.iter().filter(|t| t.done).count();
    let footer = row()
        .key("footer")
        .w_full()
        .gap(12.0)
        .center_y()
        .child(
            text(format!("{done} of {} done", s.tasks.len()))
                .key("count")
                .font(k.ty.small)
                .color(c.text_muted)
                .grow(1.0),
        )
        .child(
            Switch::new(s.hide_done)
                .label("Hide done")
                .on_toggle(|s: &mut State| s.hide_done = !s.hide_done)
                .build(&k)
                .key("hide-done"),
        );

    col()
        .key("window")
        .w_full()
        .h_full()
        .padding(20.0)
        .gap(12.0)
        // `page` is the window behind components; `bg_base` is a card on it.
        .fill(c.page)
        .child(
            text("Tasks")
                .key("title")
                .font(k.ty.ui_medium)
                .color(c.text_base),
        )
        .child(composer)
        // A bounded scroll viewport: shrink and min_h(0) let it give up height instead of
        // pushing the footer out of the window.
        .child(
            list.scroll(ScrollSpec {
                stick_bottom: false,
            })
            .shrink()
            .min_h(0.0),
        )
        .child(footer)
}

fn on_key(s: &mut State, ev: &KeyEvent, tx: &mut Tx) -> bool {
    if HIDE_DONE.matches_tx(ev, tx) {
        s.hide_done = !s.hide_done;
        return true;
    }
    false
}

fn spec() -> AppSpec<State> {
    AppSpec::<State> {
        min_size: Some((360.0, 320.0)),
        scenes: &[
            ("empty", |s| s.tasks.clear()),
            ("many", |s| {
                for n in 4..44 {
                    s.push(&format!("Task {n}"));
                }
            }),
            ("hide-done", |s| s.hide_done = true),
            ("draft", |s| {
                s.draft = TextEdit::new("Write the forward tests")
            }),
        ],
        on_key: Some(on_key),
        ..AppSpec::new("Tasks", (420.0, 520.0), State::new, view)
    }
}

fn main() {
    // Starts the GPU device while the platform starts; the first window takes it.
    rune::prewarm_gpu();
    rune::App::new(spec()).run();
}

#[cfg(test)]
mod tests {
    use super::*;
    use rune::{Env, Runtime};

    fn runtime(state: State) -> Runtime<State> {
        let mut rt = Runtime::new(state, view, (420.0, 520.0), Env::new(false, 2.0));
        rt.frame(0.0);
        rt
    }

    fn tap(rt: &mut Runtime<State>, key: &str) {
        let (x, y) = rt
            .find(key)
            .unwrap_or_else(|| panic!("no element keyed {key:?}"));
        rt.pointer_down(x, y);
        rt.pointer_up(x, y);
        for _ in 0..30 {
            rt.frame(1.0 / 60.0);
        }
    }

    #[test]
    fn add_turns_the_draft_into_a_row_and_empties_the_field() {
        let mut state = State::new();
        state.draft = TextEdit::new("  Ship it  ");
        let mut rt = runtime(state);
        tap(&mut rt, "add");
        assert_eq!(rt.state.tasks.len(), 4);
        assert_eq!(rt.state.tasks[3].title, "Ship it");
        assert!(rt.state.draft.text.is_empty());
        assert!(rt.find("task-3").is_some(), "the new row is drawn");
    }

    #[test]
    fn a_blank_draft_disables_add() {
        let mut rt = runtime(State::new());
        tap(&mut rt, "add");
        assert_eq!(rt.state.tasks.len(), 3);
    }

    #[test]
    fn the_checkbox_toggles_its_own_task() {
        let mut rt = runtime(State::new());
        tap(&mut rt, "task-1/check");
        assert!(rt.state.tasks[1].done);
        assert!(!rt.state.tasks[2].done);
    }

    #[test]
    fn hiding_done_tasks_removes_their_rows_and_shows_the_empty_note() {
        let mut rt = runtime(State::new());
        tap(&mut rt, "hide-done");
        assert!(rt.state.hide_done);
        assert!(rt.find("task-0").is_none());
        assert!(rt.find("task-1").is_some());

        for id in [1, 2] {
            tap(&mut rt, &format!("task-{id}/check"));
        }
        assert!(rt.find("empty").is_some());
    }

    #[test]
    fn remove_drops_only_that_task() {
        let mut rt = runtime(State::new());
        tap(&mut rt, "task-1/remove");
        let ids: Vec<u32> = rt.state.tasks.iter().map(|t| t.id).collect();
        assert_eq!(ids, [0, 2]);
    }

    #[test]
    fn the_field_and_rows_reach_assistive_technology() {
        let rt = runtime(State::new());
        let tree = rt.accessibility_json().to_string();
        assert!(tree.contains("New task"), "the field is named");
        assert!(
            tree.contains("Render a scene headless"),
            "each checkbox is named by its task"
        );
    }
}
