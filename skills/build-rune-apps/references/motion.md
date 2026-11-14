# Motion

Views give targets; Rune animates between them on analytic springs. The
framework's motion rules are the defaults, so most app motion is choosing a
spring and keeping keys stable. Upstream: [rune-motion](upstream/rune-motion.md),
[what exists](upstream/rune/what-exists.md) ("Animation"),
[shared-element motion](upstream/rune/shared-element-motion.md),
[finite choreography](upstream/rune/finite-choreography.md),
[high-frequency values](upstream/rune/high-frequency-values.md).

## Rules Rune already enforces

- Springs are duration plus bounce (SwiftUI's `Spring(duration:bounce:)`), bounce
  0 by default; exits run shorter than entrances.
- Interrupting keeps position and velocity. Stationary edges never move; layout
  animates per edge, and width can lead (`.width_leads()`).
- Nothing animates on the first frame or first mount.
- Direct manipulation (drags) is instant; release animates.
- Elements added or removed after the first frame animate in and stay drawn
  until their exit settles.
- Reduce Motion snaps travel, scale and blur and turns presence, opacity and
  colour into a short fade. Don't add a parallel reduced-motion path; an app
  setting feeds `cx.reduced_motion(on)` from the view, and a scene that turns it
  on lets headless renders check it.

## Choosing motion

| Want | Use |
| --- | --- |
| An element's layout and paint to spring | `.motion(spring)` with a token: `tok::motion::SNAPPY` (0.25 s) for controls, `DEFAULT`/`SETTLE` (0.3 s) for most moves, `REFLOW` (0.4 s) for layout shifts, `POP` or `MORPH` when a little bounce is earned |
| A custom spring | `Spring::new(duration, bounce)`; keep bounce ≤ 0.2 for UI |
| Enter/exit | `.transition(Transition::..)`: `opacity`, `scale`, `offset`, `move`, `push`, `slide`, `blur_replace`, `asymmetric`, `combined` |
| One element flying between two layouts | `.matched(id)` on both places (`examples/matched`) |
| Press feedback on tiles | `.press_scale(0.97)` (rune-kit buttons deliberately don't scale) |
| Pulses and spinners | `.looping(LoopSpec::opacity(..))` or `LoopSpec::rotation(period)`; they pause when hidden |
| Rolling digits and labels | rune-kit `RollingText`, `Button::rolling(key)` |
| Values that change every frame (meters, cursors, camera) | `Live<T>` with `.live_opacity`, `.live_offset`, `.live_scale`, and `LiveText`; no view re-run |
| A sequence of steps | `Choreography` cues, `Stagger` |

## Turning motion off for a change

- `tx.instant()`: this change lands without animation (launch-time state,
  restored sessions, settings read from disk, a first network answer).
- `El::instant_changes()`: a subtree whose contents swap instantly (search
  results) while the element's own entrance, exit and colours still animate.
- `tx.settle()`: every track lands and removed nodes unmount at once.
- `tx.color_motion(spring)`: the spring for this change's colours (theme switches
  use a calm one).

## Checking motion

- Headless runs use a fixed virtual clock, so the same script produces the same
  frames. Use `--at <seconds>` for a moment mid-flight, `--strip` for a contact
  sheet, `--video` for a recording (needs ffmpeg).
- `--trace run.jsonl` records keyed elements' motion per frame;
  `python3 scripts/trace-quality.py run.jsonl` in a Rune checkout scores it.
- `rune::motion_gate` drives the real app in `cargo test` and fails on pops,
  jumps, overshoot, flicker and motion that never settles; see the
  [motion audit](upstream/scripts-motion-audit.md).
- A `Runtime` test can assert travel: sample `rt.presented(key)` across
  `rt.frame(1.0 / 60.0)` calls (`examples/hello`'s test checks the knob moves
  monotonically and lands exactly).

## Don'ts

- Don't animate with timers, `wake_after` loops or per-frame `poll` state
  changes; set targets.
- Don't change keys to "restart" an animation; that remounts the element.
- Don't animate on launch or on data that arrives just after launch; the first
  second stays still.
- Don't put `on_hover_change` state on every row to animate hover; use `.hover(..)`
  styles, which never re-run the view.
