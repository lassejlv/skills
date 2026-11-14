> Upstream: [crates/rune/README.md § Moving a story table onto it](https://github.com/anomalyco/rune/blob/65f8eb43f710e078f92cb82039212de50cb03113/crates/rune/README.md#moving-a-story-table-onto-it) at `65f8eb43f710`, MIT © Anomaly. Bundled by build-rune-apps; links point at this snapshot or at GitHub at that rev.

### Moving a story table onto it

An app that keeps its own storybook (a `Story` trait with a group, a name, knobs and keys, a
grouped list, and a knobs column) maps onto `App::playground` like this:

| The app's storybook                         | `App::playground`                                                      |
| ------------------------------------------- | ---------------------------------------------------------------------- |
| a story type implementing the trait         | `Story::new(name, init, view)`, or `Playground::page` for real state   |
| a registered table of stories               | a loop of `Story::new(row.path, move \|\| .., move \|s, cx\| ..)`, closures capturing the row |
| `group()` and `name()`                      | one path, `"Group/Name"` or `"Group/Subgroup/Name"`; groups keep the order they first appear in, or `Playground::group_order` |
| the story's keys (`Action`s)                | `Story::trigger(key, label, step)`, or `trigger_tx` for a `Fn(&mut S, &mut Tx)`; `'r'` runs after each replay |
| timed steps after a key                     | `Play::after(secs, step)`, on the logical clock                        |
| a step that presses a key                   | `Play::press(Key::Down)`: through focus and `on_key`, counted as input; a letter reaches the app, not the story's triggers |
| the knobs column                            | `.side(view)`: `rune_knobs::inline` fills the column's width; `actions` fits it, up to 300 pt |
| keys for the knobs                          | `.side_keys(view, rune_knobs::side_key(groups, lens))`: ↑↓ pick a knob, ←→ step it, Esc leaves |
| a choice knob flipped with 1–9              | `Story::variant(name, apply)`; 1–9 pick, and picking remakes the state |
| setup from the app's state                  | `Story::from_real(name, derive, view)`, or `Playground::fresh`         |
| collapsible groups                          | built in at every level: click a header, or ← → ↵ on it; `Playground::folds(load, save)` keeps them between runs, `start_folded(true)` starts them folded |
| a search field over the list                | built in: / focuses it, and it keeps the stories whose path matches    |
| a key sheet                                 | built in: the side column shows each key beside its row, and a hint    |
| open, leave, Esc, ⌘⇧D                       | built in: ⌘⇧D, Esc, Back, and `tx.open_playground()`                   |
| a link to a story                           | `rune::playground::slug(path)`, and `tx.open_playground_at(slug, variant)` from `App::on_open_url` |
| a background poll                           | `Story::poll`                                                          |
| a tall page, or a window-sized story        | `Story::stage(Stage::Scroll)` or `Stage::Fill`                         |
| counts beside the headers, motion marks    | built in                                                               |
