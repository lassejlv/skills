> Upstream: [crates/rune-knobs/README.md](https://github.com/anomalyco/rune/blob/65f8eb43f710e078f92cb82039212de50cb03113/crates/rune-knobs/README.md) at `65f8eb43f710`, MIT © Anomaly. Bundled by build-rune-apps; links point at this snapshot or at GitHub at that rev.

# rune-knobs

Live tuning values for Rune apps. A `Knob` is a named number (a slider, or a choice between
labels) with a range and a default; knobs live in `Group`s, each tied to the key of the element
it tunes. ⌘⇧K opens a panel that tunes them while the app runs:

- **Side panel** (`side`): slides in down the window's right edge and pushes the page over. Its
  groups list in one scroll as a folding tree of pages and their parts, with sticky headers and a
  dot on the parts on screen; typing filters. Its left edge drags to resize it.
- **Floating panel** (`layer`): floats over the window with a tab per group.
- **Rows** (`inline`, `actions`): the same rows for an app's own layout, a storybook's column
  say. Choices lay out as a segmented control, a grid when they don't fit, or a ‹ › stepper over
  the whole list past ten options.

Each group has Random, Reset, Undo, Copy (`name = value` lines) and presets, declared in code or
saved from the panel. Hovering a group's header outlines its part of the window, and the target
button picks a part by pointing at it. With the panel focused, ↑/↓ pick a row, ←/→ fold, open or
step it (⇧ for 10×), and Esc closes.

The panel is a dev tool. Without the `panel` feature, `side` returns the page alone, `layer`
draws nothing, `key` takes nothing and `Knobs::get` returns each knob's default, so a shipped
build runs on the constants:

```toml
[dependencies]
rune-knobs = { git = "https://github.com/anomalyco/rune", rev = "…" }

[features]
dev = ["rune-knobs/panel"]
```

## A knob in an app

```rust
use rune_knobs::{Group, Knob, Knobs, Style};

const RADIUS: Knob = Knob::new("Card radius", 0.0, 32.0, 14.0).about("How round the card's corners are");
const TINT: Knob = Knob::choice("Card tint", &["Plain", "Accent", "Raised"], 0);
const GROUPS: &[Group] = &[Group::new("Card", "card", &[RADIUS, TINT])];

struct State { knobs: Knobs, /* … */ }

fn view(s: &State, _: &mut Cx<State>) -> El {
    let card = col().key("card").radius(s.knobs.get(&RADIUS)) /* … */;
    let page = col().key("page").grow(1.0).h_full().center().child(card);
    rune_knobs::side(page, &s.knobs, GROUPS, Style::dark(), |s: &mut State| &mut s.knobs)
}

fn on_key(s: &mut State, ev: &KeyEvent, tx: &mut Tx) -> bool {
    let taken = rune_knobs::key(&mut s.knobs, ev); // ⌘⇧K, and Esc while open
    if taken { tx.motion(s.knobs.slide()) } // the page slides over with the panel
    taken
}
```

`examples/knobs` is this app. `Knobs` is plain data: save `values`, `saved` and `width` with the
app's other state so tuning survives a relaunch. `Knobs::settled` marks what the app is set to,
so a choice row shows a dot on that option while others are tried.

## In the playground

`App::playground`'s side column takes any view, so a story's knobs go there as rows. The rows
act on whatever state the side view is built for, so give the story's state a `Knobs` field:

```rust
Story::new("Cards/Card", Card::default, card_view)
    .side(|c: &Card, _| rune_knobs::inline(&c.knobs, GROUPS, Style::dark(), |c: &mut Card| &mut c.knobs, false))
```

`inline` fills its parent's width (the column's 240 pt or more), and its rows lay out from the
width they get: a slider's track grows with the column, and a choice sits beside its label or
under it as the room allows. The floating panel keeps its own 300 pt. `Style::light()` is the
light look. `examples/knobs` has this story (`-- --playground Knobs`).

`Playground::side(scene, view)` does the same for one of the app's scenes, against a scene's
fresh copy of the app state.
