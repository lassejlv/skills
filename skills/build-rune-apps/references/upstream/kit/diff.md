> Upstream: [crates/rune-kit/README.md § Diff](https://github.com/anomalyco/rune/blob/65f8eb43f710e078f92cb82039212de50cb03113/crates/rune-kit/README.md#diff) at `65f8eb43f710`, MIT © Anomaly. Bundled by build-rune-apps; links point at this snapshot or at GitHub at that rev.

## Diff

`rune_kit::diff` shows code changes for review. `diff::parse(patch)` reads `git diff` output
(several files, renames with similarity, mode changes, binary files, `\ No newline at end of
file`, quoted paths) and `FileDiff::from_texts(path, old, new)` diffs two texts (Myers, line
by line, three lines of context; `from_texts_with_context` keeps another count). Changed lines
that pair up get word-level changes. The app keeps a `DiffState` in
its state and draws it with `DiffView`:

```rust
let mut diff = DiffState::new(diff::parse(&patch));
diff.set_annotations(vec![Annotation::new(0, LineRef::new(Side::New, 19), "c1")]);

DiffView::new(|s: &App| &s.diff, |s: &mut App| &mut s.diff)
    .annotation(|s: &App, a: &Annotation| comment(&s.comments[&a.id]))
    .on_comment(|s: &mut App, lines: LineRange, _| s.draft = Some(lines))
    .on_visible_file(|s: &mut App, f| s.tree.reveal(f))
    .build(s, &k)
```

- **Unified or split** (`set_mode`). Rows keep their keys across modes, so a switch inside
  `tx.motion(..)` moves rows rather than replacing them. Long lines scroll sideways, or wrap
  with `set_wrap(true)`; split always wraps.
- **Colours** come from the kit's palette: added and removed lines take a tint of the success
  and danger colours, word changes a stronger one, with a bar at the edge. Syntax colours sit
  under them (`rune_kit::syntax`, swappable with `set_highlighter`). Tabs line up at
  four-column stops and copy as tabs.
- **Unchanged ranges** between hunks fold into a row that opens 20 lines up, 20 down, or all
  (`expand`). A parsed patch has no whole files, so only diffs built from two texts have folds that open.
- **Files** have a header with the path, a rename arrow, +/− counts, a collapse chevron and
  an app slot (`header_actions`). The header of the file in view sticks to the top.
- **Annotations** are the app's widgets under a line, keyed by file, side and line, such as
  review comments. Rows grow to fit them.
- **Line selection**: click a line number, Shift-click to extend, or drag down the numbers;
  `on_select` gets the range. With `on_comment`, a "+" shows by the hovered line's number.
  Cmd-C copies the selected lines of one side, without numbers or markers; a text selection
  over the code copies the side it started on.
- **Keys**: call `diff.key(ev, tx)` from `on_key` for `j`/`k` (next/previous hunk), `]`/`[`
  (next/previous file) and Escape. Shift-click needs `App::modifier_keys`. Rows read as
  "added line 12: ..." to accessibility.
- **Beside a file tree**: `scroll_to_file(i, tx)` and `scroll_to_line` scroll to it, and
  `on_visible_file` reports the file at the top as the list scrolls.
- **Long diffs** are a virtual list built by index, so a commit costs the rows in view, not
  the length: two 50,000-line texts diff in about 40 ms, the first frame takes about 20 ms,
  and a commit takes as long as a 300-line diff's. `cargo test -p rune-kit --profile perf
  --test diff diff_50k_time -- --ignored --nocapture` measures it.

`cargo run -p rune-kit --example diff` shows a five-file review with a comment and a folded
range; stills: [unified](https://github.com/anomalyco/rune/blob/65f8eb43f710e078f92cb82039212de50cb03113/demo/kit/diff-unified-light.png) and
[split](https://github.com/anomalyco/rune/blob/65f8eb43f710e078f92cb82039212de50cb03113/demo/kit/diff-split-dark.png).
