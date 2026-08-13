# Motion, gestures, and input reference

Use this layer for transitions, springs, direct manipulation, drag, momentum,
touch gestures, and input arbitration.

## Contents

- [Motion contract](#motion-contract)
- [Choose the mechanism](#choose-the-mechanism)
- [Use GPUI animation safely](#use-gpui-animation-safely)
- [Integrate an interruptible spring](#integrate-an-interruptible-spring)
- [Design direct manipulation](#design-direct-manipulation)
- [Handle gesture arbitration](#handle-gesture-arbitration)
- [Respect accessibility](#respect-accessibility)
- [Protect frame performance](#protect-frame-performance)
- [Test motion](#test-motion)
- [Starting values](#starting-values)

## Motion contract

Animation should explain state, preserve spatial continuity, or provide
immediate input feedback. It should not delay work or decorate every update.

For each motion, write:

- trigger and semantic purpose;
- start and end state;
- property set;
- interruption/retarget behavior;
- input behavior while moving;
- reduced-motion result;
- completion/cancellation ownership;
- performance budget;
- test oracle.

Prefer transform/opacity-like presentation changes over relayout when either
can express the same feedback. Still verify text sharpness and hit testing.

## Choose the mechanism

| Need | Mechanism |
|---|---|
| Short decorative state transition | GPUI finite animation |
| Hover/press style | Element state styling, often no timeline |
| Direct manipulation | Explicit gesture state updated 1:1 |
| Retargetable settling | Spring state plus animation-frame requests |
| Momentum scrolling | Existing scroll/list behavior before custom physics |
| Repeated loading indicator | Existing progress component or bounded loop |
| Complex custom painted motion | `canvas`/custom element only when justified |

Do not implement a custom spring for a color fade. Do not use a fixed-duration
ease for an object the user can grab and reverse mid-flight.

## Use GPUI animation safely

Current GPUI 0.2.2 exposes `AnimationExt::with_animation` for finite element
animation. Its implementation accounts for `App::reduce_motion`. Pinned
versions can differ, so inspect the local trait and existing call sites.

Use finite animation for:

- small disclosure transitions;
- opacity/scale feedback;
- state changes with known duration;
- anchored entry/exit where interruption is simple.

Rules:

- keep the product state authoritative;
- derive the animated presentation from elapsed fraction;
- use the same spatial anchor for enter and exit;
- keep pointer/keyboard handling available;
- avoid animating large layout subtrees when a smaller presentation layer works;
- avoid completion callbacks as the only way state becomes correct.

GPUI's `request_animation_frame` documentation tells callers to consider reduced
motion for decorative animation. Custom loops must check it explicitly.

## Integrate an interruptible spring

Use [spring.rs](../assets/spring.rs) as pure math. Copy it into the target,
adapt types, and keep GPUI timing/lifecycle outside it.

State needed:

```rust
struct MotionState {
    spring: Spring1D,
    last_frame: Option<Instant>,
    dragging: bool,
}
```

Integration flow:

1. On press, capture pointer/touch ID, current presentation value, and grab
   offset.
2. During drag, set presentation directly from input and estimate filtered
   velocity.
3. On release, project a bounded destination and retarget the spring while
   preserving velocity.
4. Request another frame only while the spring is unsettled.
5. Compute elapsed time from a monotonic clock.
6. Cap/subdivide long time steps.
7. Call `cx.notify()` when a step changes rendered output.
8. On a new press, stop settling and continue from current presentation state.
9. For reduced motion, snap to semantic state and clear velocity.

Schematic GPUI shape:

```rust
fn animate(&mut self, window: &mut Window, cx: &mut Context<Self>) {
    if cx.reduce_motion() {
        self.motion.spring.snap_to(self.motion.spring.target);
        self.motion.last_frame = None;
        cx.notify();
        return;
    }

    let now = Instant::now();
    let dt = self.motion.last_frame.replace(now)
        .map_or(0.0, |last| (now - last).as_secs_f32());

    if self.motion.spring.step(dt, self.spring_config) {
        window.request_animation_frame();
    } else {
        self.motion.last_frame = None;
    }
    cx.notify();
}
```

The current exact location of `reduce_motion` and animation-frame callbacks is
version-sensitive. Copy the target's pattern.

### Preserve velocity

Retarget from:

- current presentation position, not the old model endpoint;
- current velocity, not zero;
- current input direction.

Resetting velocity on every target change creates a visible hitch.

### Project safely

The bundled helper uses an exponential-decay projection. Always clamp projected
destinations to semantic stops. Projection chooses a likely destination; the
spring performs settling.

### Rubber-band deliberately

Apply diminishing resistance only outside allowed bounds. Keep the actual model
value in range and render an overshoot presentation separately. Snap or spring
back on release.

Do not rubber-band destructive values, precise sliders, or controls where an
out-of-range visual implies invalid data.

## Design direct manipulation

Direct manipulation should feel attached to input:

- preserve the initial grab offset;
- update on every input event without an ease;
- distinguish presentation from committed model value;
- do not move the hit target away from the visual;
- continue receiving events when the pointer leaves the original bounds if the
  pinned input capture pattern supports it;
- commit/cancel according to clear thresholds;
- preserve keyboard alternatives.

For drag-and-drop:

- make lift/selection visible immediately;
- keep the origin placeholder stable;
- distinguish valid and invalid drop targets without color alone;
- auto-scroll only near edges and at bounded speed;
- restore or commit focus after drop;
- announce the result where accessibility support permits.

## Handle gesture arbitration

Do not build a parallel gesture arena if current GPUI input already provides the
needed recognizers. At the 2026-08-13 upstream snapshot, GPUI's touch gesture
tuning included:

- touch slop: 8 logical pixels;
- multi-tap timeout: 400 ms;
- multi-tap distance: 16 logical pixels;
- long press: 500 ms;
- momentum decay: 0.998 per millisecond;
- minimum fling velocity: 50 logical pixels per second.

These are implementation details, not permanent public design tokens. Read the
pinned source before relying on or changing them.

Arbitration policy:

1. A small movement remains a tap candidate.
2. A drag recognizer wins after slop in its intended axis.
3. Scroll containers should beat child drags unless the child has an explicit
   handle or directional lock.
4. Long press cancels when movement or another recognizer wins.
5. Pinch/multi-touch cancels incompatible single-pointer gestures.
6. Cancellation resets pressed visuals and temporary state.

Mouse, trackpad, touch, and stylus are not identical. Support the platform/input
types the product actually targets and state what is unverified.

## Respect accessibility

Reduced motion must change behavior, not only duration:

- snap navigation/context changes;
- use a short fade when continuity still matters;
- remove parallax, elastic overshoot, and large spatial travel;
- keep progress indicators meaningful;
- never disable functional feedback.

Do not use motion as the sole indicator of selection, validation, completion,
or drag destination. Pair it with persistent visual/semantic state.

Avoid rapid flashing, large repeated zoom, and unbounded oscillation. Let users
interrupt and dismiss transient movement.

## Protect frame performance

- Request frames only while presentation changes.
- Avoid filesystem/network/parsing work in the frame path.
- Precompute stable geometry and assets.
- Keep per-frame allocation bounded.
- Avoid rerendering an entire large list for one animated row when the
  architecture can isolate it.
- Cap elapsed time after stalls.
- Prefer one coordinator for a group of related material/motion surfaces.
- Profile release-like builds; debug timing can mislead.

Animation is not smooth if it reaches 60/120 fps only on an empty screen. Test
with production-like content, blur/material paths, scrolling, and window resize.

## Test motion

Unit-test pure math:

- convergence;
- no NaN/infinity after long frames;
- retarget velocity continuity;
- bounds/projection;
- rubber-band symmetry;
- reduced-motion snap.

GPUI-test behavior:

- press gives immediate visual state;
- drag preserves grab offset;
- cancellation clears state;
- release chooses correct target;
- re-grab during settling is continuous;
- keyboard performs equivalent action;
- focus remains visible;
- only active motion requests more frames.

Runtime-test:

- low/high refresh displays when available;
- app inactive/reactivated mid-motion;
- window resize and scale move;
- slow frame or debugger pause;
- trackpad/mouse/touch paths;
- reduced motion.

## Starting values

Use values as hypotheses, then tune in context:

- press feedback: immediate;
- tiny decorative transition: roughly 100–180 ms;
- small anchored presentation: roughly 180–280 ms;
- larger navigation transition: roughly 240–420 ms;
- spring response: 0.28–0.45 s;
- damping ratio: 0.82–1.0;

Desktop interfaces usually need less travel and less bounce than marketing
animation. Content distance, scale, input velocity, and interruption matter
more than a universal duration.

See [sources.md](sources.md) for Apple and GPUI primary sources.
