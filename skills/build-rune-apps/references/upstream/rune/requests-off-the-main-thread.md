> Upstream: [crates/rune/README.md § Requests off the main thread (`rune::Latest`)](https://github.com/anomalyco/rune/blob/65f8eb43f710e078f92cb82039212de50cb03113/crates/rune/README.md#requests-off-the-main-thread-runelatest) at `65f8eb43f710`, MIT © Anomaly. Bundled by build-rune-apps; links point at this snapshot or at GitHub at that rev.

### Requests off the main thread (`rune::Latest`)

A search box, a mention list or a path completer asks once per keystroke and wants only the newest
answer. Doing it in the handler blocks the window for the whole round trip; debug builds warn when a
handler or `poll` spends 8 ms waiting. `Latest<T>` runs the request on a worker and lands the newest
answer:

```rust
// init: build it once, with its debounce.
results: Latest::default().debounce(Duration::from_millis(60)),
// setup: the waker runs `poll` when an answer lands. Pending state and debounce stay.
s.results.set_waker(waker);
// A handler, on every keystroke:
s.results.request(query.clone(), |q| index.search(&q));
// poll: true only when an answer landed.
let Some(hits) = s.results.take() else { return false };
s.hits = hits;
true
```

- **Latest wins.** Each request supersedes the earlier ones. One that hasn't started never runs; one
  already running finishes, and its answer is dropped, even if it finishes after the newer one.
- **One wake per answer.** The waker fires once when an answer lands, and `take` returns it once, so
  `poll` returns true once and an idle window stays idle. `is_pending` drives a spinner.
- **Skip without waking.** `request_opt(input, |q| -> Option<T>)` lands nothing when the work
  returns `None` and doesn't wake the window. It still supersedes older requests, so their
  answers stay dropped.
- **Call it from `poll`.** `request_if_changed(&key, |k| ..)` does nothing when `key == ` the last
  such request's key (`K: Clone + PartialEq`), so work isn't restarted nor its debounce pushed
  back. `request`, `request_opt` and `cancel` forget the key.
- **Debounce** (optional) waits for that long without a newer request before starting one.
- **No thread per request.** Up to four shared workers, started on demand, exit after ten idle
  seconds. On the web the work runs on the main thread from `spawn_local`, after the debounce.
- **Cancel** drops pending and running requests; dropping the `Latest` cancels it. State outlives a
  closed window, so call `cancel` from `App::on_close` to stop requests on close.

Only the closure runs on the worker; the answer reaches state in `poll`, on the UI thread.
