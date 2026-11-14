> Upstream: [crates/rune/README.md § Testing stories](https://github.com/anomalyco/rune/blob/65f8eb43f710e078f92cb82039212de50cb03113/crates/rune/README.md#testing-stories) at `65f8eb43f710`, MIT © Anomaly. Bundled by build-rune-apps; links point at this snapshot or at GitHub at that rev.

### Testing stories

A unit test runs a story's triggers and steps headless, as `--playground NAME --variant V`
would, and reads the stage:

```rust
let mut rt = App::new(spec).playground(playground()).headless_runtime((800.0, 500.0), Env::new(false, 1.0));
rt.open_playground("Progress/Upload", Some("Large")); // its 'r' trigger has run
assert_eq!(rt.playground_state::<Upload>().unwrap().phase, "sending");
for _ in 0..36 { rt.frame(1.0 / 60.0); }               // Play::after steps run as the clock reaches them
rt.playground_trigger('f');                            // as the F key or its button does; 'r' replays
let label = rt.playground_element("upload").and_then(|e| e.text);
assert_eq!(rt.state.count, 0);                         // the real state, untouched
```

- `App::headless_runtime(size, env)` builds the runtime a headless render would, with the
  playground attached and closed. It's there when the playground is enabled, which by default
  means debug builds, so `cargo test`.
- `open_playground(story, variant)` takes a path, a name or a slug and a variant by number or name, and
  panics with the list when there's no such story or variant. It and `playground_trigger(key)`
  apply on two frames that advance no time, so a trigger's first step has run when they
  return. Later steps run as `rt.frame(dt)` moves the logical clock.
- `playground_state::<P>()` is the stage's state: a scene's app state, or a story's own. It's
  `None` while closed and on a page, whose stage is `rt.state`. `playground_element(key)` finds
  an element on the stage only, by key or path; `rt.find` and `rt.elements` see the whole
  window, the side column included.
