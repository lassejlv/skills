> Upstream: [examples/motion-bento/README.md](https://github.com/anomalyco/rune/blob/65f8eb43f710e078f92cb82039212de50cb03113/examples/motion-bento/README.md) at `65f8eb43f710`, MIT © Anomaly. Bundled by build-rune-apps; links point at this snapshot or at GitHub at that rev.

# Motion bento

A 1440×900 control center whose twelve tiles all move at once: a segmented scene picker, a
thermostat ring, light switches, mixer faders, an XY pad, a card deck, an activity feed, and a
bottom row of five tiles that reflow around whichever one has focus. A seeded chaos schedule taps
them (a few times a second, with bursts of six to twelve taps 30–60 ms apart), so nearly every
frame has springs in flight.

`chaos/` (`motion-bento-chaos`) holds everything that isn't Rune: the model, the schedule, the
look (colours, grid, spring tunings) and the frame meter. It has no Rune dependency, so another
toolkit can build the same window and play the same schedule.

```sh
cargo run -p motion-bento --profile perf -- --seed 7 --duration 30 --intensity 1.5 --hud
```

| Flag | Default | |
| --- | --- | --- |
| `--seed N` | 1 | Names one schedule, and every random choice its taps make. |
| `--duration S` | 20 | Seconds of chaos. The window quits a second later. Rune's headless runs read it too. |
| `--intensity X` | 1 | Scales the rate of taps: 2 is twice as many. |
| `--variant NAME` | `default` | Spring tuning: `default`, `bouncy` or `stiff`. |
| `--metrics PATH` | | Write the frame meter's JSON when the run ends (a headless run: at `--duration` + 1 s). |
| `--hud` | off | Show the frame meter from the start. `H` toggles it. |
| `--stay` | off | Keep the window open after the schedule ends. |
| `--emit-script PATH` | | Write the schedule as a Rune headless script and exit. |
| `--load N` | | Stress mode: a wall of N live controls instead of the bento. |
| `--ramp A:B` | | Stress mode, growing from A to B controls by ×√2 a step. Sets `--duration` unless given. |
| `--hold S` | 2.5 | Seconds a ramp spends at each step. |
| `--naive` | off | Stress mode: build the whole wall again every frame instead of binding live values. |
| `--frames PATH` | | Write every frame as CSV when the run ends: show time, load, build, work, start, and CPU time since the frame before (thread and process). |
| `--hud-from PATH` | | Stress mode: the HUD replays a `--frames` CSV from an earlier run, so a capture run shows what a clean run measured at the same moment. |

## Stress mode

`--load` and `--ramp` swap the bento for a wall of controls (`chaos/src/stress.rs`): each a card
with a glowing status dot, a name, a status word, a reading that changes every frame, a
percentage, eight gradient bars that retarget every few hundred milliseconds, a progress track
and a switch. The wall reshuffles every 2 s, one in twelve controls goes double width (reselected
every 1.7 s), hues and statuses change on their own clocks, and a new control scales and fades in.
What the wall shows is a pure function of the seed, the show time and the load, so the GPUI build
draws the same wall frame for frame.

```sh
motion-bento --seed 7 --ramp 32:1024 --frames ramp.csv --snap end.png --at 29.6 --size 1440x900 --scale 2 --fps 120
```

With `--hud`, the header shows a frame-time readout and graph against the 120 Hz and 60 Hz budgets.

The wall is built the way a Rune app should build it (`src/stress/live.rs`): each card's inside is
a `memo` built once per size, and its reading, bars, switch, progress and colours are `Live`
values that `poll` sets, so the view runs and commits only when the wall reshuffles or grows.
`--naive` (`src/stress/naive.rs`) rebuilds every card every frame, as a first port would.

## Headless

Every action is a tap on a keyed element (`Action::key`), so the schedule is also a script:

```sh
motion-bento --seed 7 --duration 8 --emit-script chaos.json
motion-bento --seed 7 --duration 8 --script chaos.json --video bento.mp4 --size 1440x900
motion-bento --seed 7 --duration 8 --script chaos.json --tree end.json --at mark:end
```

With a script, the window plays its taps instead of the schedule, and both reach the same state
(`script_taps_reach_the_same_state_as_the_schedule`).

## The meter

Measured from `App::on_frame_encoded`, for drawn frames only:

- **work**: `update_ms + encode_ms`, from the frame's start (after its drawable came) until its
  commands were submitted: events, `poll`, the view, layout, paint, uploads and encode. CPU wall
  time, not GPU time.
- **build**: `update_ms` alone: events, `poll`, the view, layout and paint, without the encode.
  The GPUI build can only time this part, so compare GPUI with this number.
- **interval**: time between frame starts. A display-paced window starts each frame on a refresh,
  so this is the gap between frames on screen.
- **late**: intervals over 1.5 refreshes (`FrameEncoded::refresh_hz`), and the refreshes they
  skipped. Gaps over 100 ms are the window resting, not late frames.
- **CPU** and **footprint**: process CPU time over the run's wall time, and the physical footprint,
  from `procwatch`.
