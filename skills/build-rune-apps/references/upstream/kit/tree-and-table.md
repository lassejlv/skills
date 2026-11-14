> Upstream: [crates/rune-kit/README.md § Tree and Table](https://github.com/anomalyco/rune/blob/65f8eb43f710e078f92cb82039212de50cb03113/crates/rune-kit/README.md#tree-and-table) at `65f8eb43f710`, MIT © Anomaly. Bundled by build-rune-apps; links point at this snapshot or at GitHub at that rev.

## Tree and Table

Both are virtualised, so only the rows on screen are built, and both are one focusable control
whose keys act on a cursor kept in app state: a row scrolled out of view still moves with the
arrows. Selection fills, rules and type come from the kit, and they follow reduced motion.

**Tree** draws a `TreeModel<T>` the app keeps in its state. `FileTree::new().build(paths)` turns
`(path, data)` pairs into one: folders before files, names in natural order (`icon2` before
`icon10`), and a chain of single-child folders shown as one row (`docs/guide/intro`).
`Tree::new(get, get_mut, label).row(|node, row| TreeItem::file(node, row).changes(12, 3))`
builds it. Each row has an indent guide, a chevron that springs open, an icon, the label and
trailing content (`changes`, `dot`, `badge` or any `trailing` element). Up and Down move,
Right opens or steps in, Left closes or climbs, Home, End and Page Up and Down jump, Return and Space toggle a
folder or open a file (`on_open`), and typing a name jumps to it. `multi_select(true)` adds
Shift and Cmd. `filter(|n| ..)` keeps the folders that lead to a match open. `reveal(id, tx)`
opens, selects and scrolls to a row, so a tree can follow an editor or a diff. Rows report
`treeitem` with their level, open state and selection. 50,000 files scroll at 0.4 ms a frame
(p50) and 4 ms when rows mount (p95); building the model takes about 35 ms
(`cargo test --profile perf -p rune-kit --test tree -- --ignored --nocapture`).
[Light](https://github.com/anomalyco/rune/blob/65f8eb43f710e078f92cb82039212de50cb03113/demo/kit/tree-light.png) and [dark](https://github.com/anomalyco/rune/blob/65f8eb43f710e078f92cb82039212de50cb03113/demo/kit/tree-dark.png) stills:
`cargo run -p rune-kit --example tree`.

**Table** reads the app's rows through `Table::new(get, get_mut, len, row_id)` and keeps
selection, sort and column widths in a `TableState`. `TableColumn::new(id, title)` takes a
`width` or `flex` weight, `min` and `max`, an `align`, and `sortable()`. The header stays put
over the rows, and a drag on a header edge resizes a column within its bounds (a double-click
resets it). A header click calls `on_sort(column, direction)` and the app sorts; the header
shows the direction. Cells come from `cell(|s, i, column| Cell::text(..))`; text cut short
shows its whole text as a tooltip. `zebra(true)` stripes rows. The keys are the arrows, Page
Up and Down, Home, End, Return (`on_open`), and in a multi-select table Shift and Cmd-A. Roles
are `grid`, `row`, `columnheader` and `gridcell`. 100,000 rows scroll at 0.4 ms a frame (p50)
and 3.4 ms when rows mount (p95) (`--test table`).
[Light](https://github.com/anomalyco/rune/blob/65f8eb43f710e078f92cb82039212de50cb03113/demo/kit/table-light.png) and [dark](https://github.com/anomalyco/rune/blob/65f8eb43f710e078f92cb82039212de50cb03113/demo/kit/table-dark.png) stills:
`cargo run -p rune-kit --example table`. `MarkdownStyle::table_like(&TableStyle::from_kit(k))`
draws Markdown tables with the same font, padding and rules.
