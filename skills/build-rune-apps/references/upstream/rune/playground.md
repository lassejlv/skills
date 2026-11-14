> Upstream: [crates/rune/README.md § Playground](https://github.com/anomalyco/rune/blob/65f8eb43f710e078f92cb82039212de50cb03113/crates/rune/README.md#playground) at `65f8eb43f710`, MIT © Anomaly. Bundled by build-rune-apps; links point at this snapshot or at GitHub at that rev.

## Playground

`App::playground` is a storybook built into the window. ⌘⇧D (Ctrl+Shift+D off macOS) opens it;
in debug builds a 26 pt bar along the bottom opens it too. Its stories are the app's scenes plus
its own pages and `Story`s, grouped by the path in their names: `"Sidebar/Filter buttons/Compact"`
lists Compact in Filter buttons, a group inside Sidebar, indented a step. One shows at a time on
a plain stage, live and interactive, with a column beside it for that story's controls and
triggers.

```rust
App::new(spec).playground(
    Playground::<State>::new()                            // named, or the closures can't infer it
        .page("Lists/Live devices", devices)              // the real state, live
        .trigger("Lists/Many devices", 'a', "Add device", |s, _| s.devices.push("New"))
        .side("Lists/Many devices", device_count)         // the app's own controls, beside the stage
        .story(
            Story::new("Progress/Upload", upload_init, upload_view)
                .poll(upload_poll)
                .trigger('r', "Run, pause, resume", |u, play| {
                    u.running = true;
                    play.after(0.6, |u, _| u.running = false);
                }),
        )
        .story(Story::overlay("Toasts/Sync toast", &TOAST, toast_init)),
)
```

- **State.** A scene gets a fresh state (`init`, then the scene) each time it's chosen. A story
  keeps its own state, made by its `init`, until the playground closes. A page draws the real
  state. Handlers on the stage act on that state; the real state keeps polling throughout and
  is back, untouched, after Back.
- **Triggers** are single-letter keys, listed beside the stage. R replays: it makes the state
  again, then runs the story's `'r'` trigger if it has one. `Play::after(secs, step)` queues
  follow-up steps on the runtime's logical clock, timed from when the previous step was due, so
  a replay runs the same every time, headless included. `Play::clear()` drops every step still
  queued, a loop's next one included, so a trigger can take over from a running one:
  `play.clear(); play.after(0.2, ..)` runs only the new steps. It leaves the state and running
  animations alone. `play.press(Key::Down)` (or a `KeyEvent`, for modifiers) sends a real key on
  the step's frame, as a person's with the stage holding the keyboard, so a replay that stands in
  for a keypress counts as input to the motion gate. J and K can't be trigger keys. `trigger_tx(key, label, |s, tx| ..)` takes a
  step that needs only the `Tx`, such as a handler the app already has.
- **Closures.** A story's `init`, `view`, `poll`, triggers, steps, variants and side view, and a
  scene's triggers, variants and side views, take closures as well as fns, so a story table can
  make its stories in a loop, each capturing its row. In a hot build, views that are fns or
  closures capturing nothing are patched live; a closure that captures runs as built.
- **Variants.** `Story::variant(name, |p| ..)` and `Playground::variant(scene, name, |s| ..)` list
  variants in the side column; with the keyboard there, 1–9 pick one, which makes the state again
  on it. A story starts on its first variant.
- **Groups.** Each `/` in a story's path nests a group, as deep as the path goes, and every
  level folds: click its header, or ← → ↵ on it. Folds last while the app runs;
  `Playground::folds(load, save)` keeps them from one run to the next (in `rune::prefs::Prefs`,
  say), each group by its path (`"Sidebar/Filter buttons"`). `Playground::start_folded(true)`
  starts every group folded but the open story's, which unfold each time the playground opens,
  a link at launch included; with it, `folds` saves the groups left open instead. Groups keep
  the order they first appear in, scenes first; `Playground::group_order(&["Prototypes",
  "Fixtures"])` lists those top-level groups first, scenes and stories alike.
- **Filter.** A field over the list keeps the stories whose path has every word typed, and the
  groups above them, unfolded. / or a click focuses it, and it edits as any field does. ↓ goes
  down to the first match and gives the list the keyboard, where ↑ from the first match goes
  back up; Return opens the first match; Esc clears it, then leaves.
- **Keys.** The keyboard is in one column at a time, the list, the stage or the side column, and
  a click in a column moves it there. The column that has it shows its selection in the accent
  (the stage a ring), and the hint under the side column lists its keys.
  - In the list, ↑↓ walk the headers and the stories that show, J K skip the headers, ⌘↑ ⌘↓ go
    to the first and last. ← on a story goes to its group; on a header it folds the group, then
    goes to the one around it. → unfolds a header, then steps into it. R replays and trigger
    letters run. → on a story or Tab moves to the side column, ⇧Tab to the stage, and Esc (after
    the stage has had it) or ⌘⇧D leaves.
  - In the side column, ↑↓ move between controls, 1–9 pick a variant, trigger letters run, and
    ←, Tab or Esc go back to the list.
  - On the stage, keys are the story's: its focused element's, then the stage's `on_key`. Esc it
    leaves goes back to the list.
  - Keys the list and side column leave, ⌘-chords and digits included, go to the stage's
    `on_key` wherever the keyboard is, so a story's shortcuts work as soon as it opens.

  `.shortcut(None)` turns the shortcut off; `tx.open_playground()` opens it from the app.
  `Playground::typing(|s| ..)` gives the stage's `on_key` every key first, wherever the keyboard
  is, for a field drawn in it.
- **Keys for side controls.** `Story::side_keys(view, key)` (or `Playground::side_keys(scene,
  view, key)`) is `.side(view)` for controls that take keys. → or Tab from the list puts the
  keyboard on them, `view` gets `active: true` while it's there to mark what the keys move,
  and `key` gets each key first, only while the keyboard is there. Esc and Tab always leave; ←
  doesn't. Keys it leaves work as elsewhere in the side column. For knobs it's one line:
  `.side_keys(|s, active, cx| rune_knobs::inline(&s.knobs, GROUPS, style(cx), lens, active), rune_knobs::side_key(GROUPS, lens))`,
  where ↑↓ pick a knob and ←→ step it.
- **The real state.** `Playground::fresh(|real| ..)` starts scenes from the real state and
  `Story::from_real(name, |real| .., view)` derives a story's state from it, each time it's
  made. `Playground::keep(|stage, real| ..)` copies a scene's stage back before R, a switch or
  Back, and `Tx::keep_playground()` runs it on demand, say from a `Playground::side_real` control
  that draws from both states. `Playground::dark(|s| ..)` makes the chrome follow the app's own
  light/dark setting. `Playground::scenes(|name| ..)` picks which scenes the list shows.
- **Links.** `tx.open_playground_at(story, variant)` opens it on a story from the app, by path,
  name or slug, with a variant by number or name: the same lookup as `--playground` and
  `--variant`. Called from `App::on_open_url`, a `myapp://story/timeline-send` link opens
  straight onto the story, at launch too, with no frame of the app first. A story it doesn't
  have is logged and opens the list; an unknown variant is logged and ignored.
  `rune::playground::slug("Timeline/Send")` is `"timeline-send"`: the path lowercased, each run
  of characters that aren't letters or digits made one `-`, none at the ends. The rule won't
  change, so a bookmarked link keeps working while the story keeps its path.
- **Overlays.** `Story::overlay` draws an overlay's view in a dashed frame of its size, so it
  shows in the window and in headless renders.
- **Stage layout.** A story sits in the stage's middle, sized as a window sizes its root: to the
  stage, or to the size picked beside it. `Story::stage(Stage::Scroll)` (or
  `Playground::stage(scene, Stage::Scroll)`) makes it a page: laid out at the stage's width
  inside a 24 pt margin, at its own height, from the top, and the stage scrolls.
  `Stage::Fill` puts it edge to edge across the whole stage, whatever size is picked.
- **The list.** Each group's header shows how many stories it holds, folded or not, and a
  story or scene with triggers has a small motion mark at the end of its row.
- **Off.** It's on in debug builds; `.enabled(bool)` overrides that and `RUNE_PLAYGROUND=0`
  turns it off. `.bar(false)` drops the bar, so the app lays out as if there were no
  playground. Snapshots, `--scene` renders and goldens leave it out; `--playground [story]`
  opens it at launch, headless too, and `--variant N|name` opens that story on a variant.
  A `--snap` with `--playground` is the story's stage only, by default; `--whole-window` snaps
  the whole window, list, stage and side column (`--out`, `--video` and `--strip` frames are
  always the whole window). `--crop KEY` crops a `--snap` to an element's laid-out rect, by
  key or path: one on the stage, or with `--whole-window` anywhere in the window, say
  `--crop playground-list`, `playground-side` or `playground-group-N` (the header of the group
  whose first story is `playground-item-N`). Each `WindowSpec` can have its own.
