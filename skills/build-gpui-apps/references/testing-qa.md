# Testing and runtime QA reference

Use this layer to build a verification plan proportionate to the GPUI change.
Compilation is one ring; input, focus, windows, materials, and visuals require
the running system.

## Contents

- [Build a risk matrix](#build-a-risk-matrix)
- [Run static and compile gates](#run-static-and-compile-gates)
- [Test pure logic](#test-pure-logic)
- [Use GPUI test support](#use-gpui-test-support)
- [Test windows and input](#test-windows-and-input)
- [Launch the product](#launch-the-product)
- [Test platforms and accessibility](#test-platforms-and-accessibility)
- [Use visual acceptance](#use-visual-acceptance)
- [Report evidence](#report-evidence)

## Build a risk matrix

Map changed behavior to evidence before coding:

| Change | Minimum evidence |
|---|---|
| Pure reducer/geometry/token | Unit tests |
| Element styling | Compile, launch, state screenshots |
| Action/focus/control | `#[gpui::test]` plus keyboard/runtime check |
| Text input/IME | Range/composition tests plus a real OS input method |
| Clipboard/drag/drop | Typed command tests plus real cross-app/window exercise |
| Menus/multi-window/restoration | GPUI tests plus native close/relaunch checks |
| Async loading/save | Deterministic async tests, cancellation/stale result |
| List/virtualization | Data mutations, navigation, large fixture |
| Animation/gesture | Pure math, simulated frames/input, runtime interruption |
| Window/chrome/material | Real platform launch and appearance matrix |
| AppKit bridge | Availability, lifecycle, resize/scale, oldest/newest macOS |
| Paper translation | Matched captures and diff loop |

Add regression coverage closest to the bug or contract. Do not create broad
snapshot tests for behavior a focused assertion can express.

## Run static and compile gates

Use repository-native commands. Baseline:

```sh
cargo fmt --check
cargo check -p <owning-crate> --all-targets
cargo test -p <owning-crate> --locked
cargo clippy -p <owning-crate> --all-targets -- -D warnings
git diff --check
```

Adjust when:

- the workspace has documented unrelated failures;
- platform features require separate invocations;
- examples/benches are not in default targets;
- a lockfile is intentionally absent from a library;
- CI uses a project task runner.

Run the smallest relevant check early, then widen. Do not suppress warnings or
change unrelated lint policy to make a UI patch green.

The suite's exact-revision reference fixture can be validated independently:

```sh
skills/build-gpui-apps/scripts/validate_reference_app.sh
```

It is intentionally a small pattern app. Passing it proves that the documented
higher-level GPUI shapes compile at the recorded revision; it does not prove a
target app's platform integration or visuals.

## Test pure logic

Keep these independent from GPUI when possible:

- reducers and state machines;
- selection/navigation rules;
- layout geometry;
- breakpoint decisions;
- material token selection;
- spring/projection/rubber-band math;
- validation and formatting;
- stale-generation policy;
- accessibility labels/state mapping.

Test boundaries and invalid states, not only a happy example. Property tests are
useful for geometry, serialization, and math invariants when the project already
uses them.

The bundled spring can be checked directly:

```sh
rustc --edition=2021 --test assets/spring.rs -o /tmp/gpui-spring-tests
/tmp/gpui-spring-tests
```

## Use GPUI test support

Current upstream provides `#[gpui::test]` and `TestAppContext`. It can construct
entities/windows, control foreground/background executors and clock, dispatch
input/actions, refresh/draw, inspect test windows, and run queued work. Exact
methods vary by pinned revision.

Current basic shape:

```rust
#[gpui::test]
fn changes_state(cx: &mut TestAppContext) {
    let model = cx.new(|_| Model::default());

    model.update(cx, |model, cx| {
        model.select(ItemId(2));
        cx.notify();
    });

    assert_eq!(model.read_with(cx, |model, _| model.selected), Some(ItemId(2)));
}
```

Do not copy method names blindly. Search the pinned `test_context` and nearby
tests.

Use the test executor instead of wall-clock sleeps. Current upstream examples
use methods such as `run_until_parked`, clock advancement, window updates,
keystroke dispatch, and simulated next frames.

Hold async tasks or advance the executor so assertions observe completion.
Random-delay simulation can expose ordering assumptions when current test
support offers it.

## Test windows and input

For a stateful component, test:

- first render/default state;
- pointer down/up/click;
- hover exit/cancellation;
- keyboard action;
- focus acquisition and visible focus;
- Tab and Shift-Tab ordering;
- disabled paths;
- accessibility action;
- notify/render update;
- resize and scale-sensitive layout;
- dismissal and focus restoration;
- input propagation in nested key contexts.

For editable text, menus, drag/drop, and window lifecycle, use the Unicode,
composition, command-state, close-policy, and restoration matrices in
[input-windows.md](input-windows.md). Simulated key presses do not replace a
real IME run.

For a list:

- empty, one, many, and large data;
- insertion/removal/reorder;
- stable selection and identity;
- keyboard navigation;
- focused item scrolled into view;
- virtualized row reuse;
- variable-height content if supported.

For motion:

- deterministic clock;
- reduced motion;
- interruption/retarget;
- cancellation;
- late frame;
- no further frames once settled.

Current upstream itself tests reduced motion by enabling it in the test app,
opening a view, simulating frames, and asserting no extra frame is scheduled.
Follow the pinned equivalent.

## Launch the product

Run the real application in the target configuration. Verify:

1. Startup reaches the intended window without hidden panic/log errors.
2. The modified surface appears with real data.
3. Mouse, keyboard, focus, shortcuts, and scroll work.
4. Resize across min/default/max useful sizes.
5. Move between displays/scales if geometry or material matters.
6. Exercise loading, empty, error, disabled, and cancellation states.
7. Close/reopen the view/window to reveal leaked tasks/native views.
8. Leave it idle and ensure animation/work stops.

When credentials, devices, or external services are unavailable, use the
nearest controlled fixture and report that the credentialed/live path is still
unverified.

Keep launch evidence separate from compilation:

- “compiled” means compiler gate;
- “tests passed” means named test invocations;
- “launched” means a real window opened;
- “behavior verified” means named interactions exercised;
- “visually compared” means captured evidence at normalized bounds.

## Test platforms and accessibility

For each supported platform record:

- build target/backend feature;
- launch environment;
- window chrome/background behavior;
- fonts and text shaping;
- mouse/keyboard/touch;
- accessibility technology;
- appearance and preferences;
- known unverified cases.

Material work on macOS needs:

- oldest supported macOS fallback;
- macOS 26+ native glass path if implemented;
- light/dark;
- active/inactive window;
- reduced transparency;
- increased contrast;
- scale/resize;
- cleanup.

On macOS, use VoiceOver and Accessibility Inspector for new controls. On other
platforms, use the native screen reader/accessibility tooling available.

Cross-compilation is not runtime verification.

## Use visual acceptance

For visual changes:

- define exact viewport/content bounds;
- use deterministic content;
- fix theme and scale;
- capture default plus interaction states;
- compare structure before polish;
- keep baselines reviewable;
- avoid accepting broad pixel diffs caused by window chrome/crop mismatch.

Do not make pixel-perfect tests the only coverage for behavior. Do not update
baselines until the difference is understood.

Read [visual-validation.md](visual-validation.md) for the complete loop.

## Report evidence

Completion report template:

```text
Target:
- GPUI source/version:
- owning crate:
- platforms:

Checks:
- PASS cargo ...
- PASS targeted test ...
- PASS app launch on ...
- PASS keyboard/focus ...
- PASS visual comparison at ...

Unverified:
- platform/path and reason

Remaining:
- known delta or none
```

Include exact failed commands and distinguish new failures from known unrelated
ones. Do not bury a hosted-platform or runtime failure behind green local tests.
