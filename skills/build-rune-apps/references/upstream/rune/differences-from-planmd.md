> Upstream: [crates/rune/README.md § Differences from PLAN.md](https://github.com/anomalyco/rune/blob/65f8eb43f710e078f92cb82039212de50cb03113/crates/rune/README.md#differences-from-planmd) at `65f8eb43f710`, MIT © Anomaly. Bundled by build-rune-apps; links point at this snapshot or at GitHub at that rev.

## Differences from PLAN.md

- wgpu (Metal backend) on macOS instead of the own thin HAL over raw Metal.
- winit for the window instead of an own shell (edge overlays move winit's view into a
  non-activating panel; no glass underlays).
- Animation is evaluated on the main thread at frame time, not on a render thread. View functions still
  never run for animation: views produce targets, and tracks animate between them.
- One pipeline with three fragment paths instead of separate quad and text pipelines (draw order is free).
- No AccessKit or inspector socket (the CLI flags stand in). Scrolling is
  vertical only.
