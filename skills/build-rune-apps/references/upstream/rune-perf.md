> Upstream: [crates/rune-perf/README.md](https://github.com/anomalyco/rune/blob/65f8eb43f710e078f92cb82039212de50cb03113/crates/rune-perf/README.md) at `65f8eb43f710`, MIT © Anomaly. Bundled by build-rune-apps; links point at this snapshot or at GitHub at that rev.

# rune-perf

Local, bounded performance diagnostics for native apps. The crate has no Rune,
GPU, async-runtime or network dependency. A process opts in by supplying its
name and directory; fixtures and production policy belong to the application.

```rust,no_run
use rune_perf::{Config, Frame, Outcome, Recorder};
let config = Config::new("diagnostics/my-app-dev", "My App").build("1.4.0");
let recorder = Recorder::start(config)?;
recorder.record(
    Frame::new(1, 42, Outcome::Drawn)
        .update_ms(2.0)
        .render_ms(1.0)
        .allocated_bytes(rune_perf::take_allocated_bytes()),
);
// Off the UI thread, at orderly shutdown:
recorder.shutdown().expect("writer panicked");
# Ok::<(), std::io::Error>(())
```

`Config` and `Frame` are built with methods, so new fields never break callers.
Every `Frame` setter takes a value or an `Option`; an unset field is unavailable.
Keep the recorder alive for the process. `record` timestamps, sanitizes optional
durations, and tries a fixed-size send. It never formats, allocates in steady
state, writes files, takes a drawable, or asks for a frame. Full queues drop
samples and count them. All directory creation, locking, sampling and JSON runs
on one background thread. Drop is nonblocking; `shutdown` joins off-UI. A
replacement waits for the previous writer's directory lock, and cancellation
also interrupts this wait. Samples queued before cancellation can be lost if the
writer has not acquired the lock; an active writer drains on shutdown.

## Hook contract

From the app's existing compositor, measure the update time and the time
around its compositor work. In `App::on_frame_encoded`, submit the corresponding
sample; preserve any existing callback by calling both from that closure. Never
replace a custom compositor just to install diagnostics. Report `None` when a
skipped/unchanged frame had no timing. Give each window a stable numeric ID and
its own sequence/timing state. `source` is an optional stable numeric site ID,
not user content. Attribution must come from the app; this crate cannot infer it.

At an input handler, retain the oldest `Tx::input_time()` not yet matched to a
drawn frame. At the encoding callback subtract it from `FrameEncoded::at()`;
only then clear it. This is **input receipt to encoding**, not input-to-screen.
Unchanged and skipped frames do not consume pending input. GPU time is an
optional **resolved GPU timestamp** supplied by a backend; never wait for GPU
queries on the UI thread. Rune's current public frame callback supplies neither
GPU execution time nor actual presentation time, so those counters remain null.

### Explicit allocator installation

The library never installs a global allocator. It reads procwatch's counting
allocator, the same one Rune's `frame-profile` tooling uses, so a binary has one.
In the binary's main module:

```rust,ignore
#[global_allocator]
static ALLOCATOR: procwatch::alloc::Counting = procwatch::alloc::Counting::system();
```

Use `procwatch::alloc::Counting::new(inner)` to wrap an allocator the binary
already has. Pass `rune_perf::take_allocated_bytes()` with each report from the
UI thread. It returns the bytes this thread requested since its previous call:
`None` without the counting allocator, and `None` on a thread's first call, which
only sets the baseline. There is no per-thread enable. Traffic includes
successful alloc/zeroed/realloc requests (full new realloc size), excludes frees,
other threads, native and GPU allocation, and does not mean retained heap.

## Files and limits

| Resource | Bound |
| --- | --- |
| Pending samples | 256 fixed-size records |
| Rolling history | 60 seconds and 600 reports |
| Snapshot | Atomic `perf.json`, with each write of incidents, and at shutdown when the run wrote anything, 256 KiB max |
| Anomaly logs | `perf.log` + `perf.log.1`, 4 MiB each, kept open for appending; ten frame lines/second, held in memory and written once 2 seconds pass with no new finding (and at shutdown) |
| Process log | A line every 30 seconds while frames arrive, kept in memory (the last 20) and written only beside a finding |
| Incidents | 16 reusable `perf-incident-NN.json` slots, 256 KiB each |
| Dedup keys | 64 recent rule/window/source keys; scoped to this app/build/launch |
| Growth history | Six minute buckets |

Snapshots keep a stable schema-1 core (frame totals, work percentiles, memory,
dropped samples) and add app/build/launch identity,
capability availability, input/GPU percentiles, fds and incident counts. Missing
measurements are null, including lifetime peaks. Capabilities describe observed
data in the current window, not a permanent backend promise. Process counters
come from `procwatch::usage()`, which reads memory and descriptors without walking
threads. macOS supplies resident/physical/lifetime-peak footprint and fds; other
platforms currently report those unavailable. Failed reads also return unknown.
Memory is checked against the incident rules as frames arrive, at most every 2 seconds and never on a timer, so an idle app wakes nothing; a run with no finding writes no file. The snapshot's timestamp says when it was written.

An incident preserves the bounded recent history and dropped-sample count. Slot
paths are reused: consumers should copy a file promptly if they need durable
retention. `Config::incidents` takes a bounded `SyncSender<PathBuf>`.
After a successful file write, the writer attempts one notification. A slow,
full or disconnected consumer cannot block recording; lost notifications are
counted and files remain available. External automation can route these paths
to an incident tracker. There is no network export or automatic
task creation in Rune.

## Rules

Rules warn and provide evidence plus a suggested next measurement:

- `long-frames`: three measured update+compositor frames ≥16.67 ms within one
  second for the same window/source.
- `frame-stall`: measured update+compositor work ≥250 ms. Idle gaps are never
  treated as stalls; a permanently hung UI needs an external watchdog.
- `memory-growth`: five completed, consecutive minute footprint floors strictly
  rise by at least 64 MiB and 20% in total.
- `fd-growth`: the same pattern, at least 32 descriptors and 20%.

Spikes, plateaus, missing reads and gaps do not qualify as leaks. Growth remains
a suspicion: cache warmup may produce the same pattern. A repeated key needs a
60-second cooldown and ≥25% worsening. A global two-second interval bounds
incident traffic; suppressed incidents are counted. Restart resets dedup state.

## Checks

```sh
cargo test -p rune-perf -p procwatch
cargo test --profile perf -p rune-perf instrumentation_overhead -- --ignored --nocapture --test-threads=1
```

Tests cover unavailable counters, zero-allocation report paths, queue overflow,
window separation, growth false positives, rotation, failures, callback pressure,
replacement locking/cancellation, and a binary without the counting allocator.
procwatch's tests cover multithreaded allocation byte accounting.
The paired component benchmark alternates order for 21 measured rounds after
warmup, retaining all outliers and reporting nearest-rank p50/p95. It measures
counting-allocator overhead, same-thread timestamp/send/receive, and background writes.
It does not establish live-window CPU percentage, GPU cost, native idle behavior,
or input-to-screen latency.

## Rollout

1. Adopt in one app's existing frame hooks and delete its writer/allocator copy.
   Preserve the app's production/dev/fixture directory policy and CLI reader.
2. Each native Rune example and downstream app uses the same startup recipe,
   unique app/build identity, dev directory, per-window hooks, and explicit main
   allocator. A fixture opts into an isolated scratch directory, never live data.
3. A future standard-runner integration should compose existing hooks and
   compositors, default on only for debug native runs, and expose an opt-out.
   This crate deliberately does not make that policy decision invisibly.
4. Add platform process adapters and asynchronous GPU timestamps separately;
   unsupported counters stay unavailable until measured. Web needs a different
   storage worker; this native file writer is not a browser backend.
5. Add source-site maps, phase/subtree capture and an external coverage/doctor
   command after the basic recorder lands. The numeric source seam is ready;
   automatic source attribution and detailed captures are not implemented here.

App fixtures should cover list/history scaling with a fixed viewport, text,
images, repeated open/close cycles, idle and teardown. Preserve allocation/work
counts in CI; evaluate timing with optimized, paired headless runs and separately
measure native idle/presentation. The proposed <1% CPU / <0.1 ms p95 whole-frame
overhead and <4 MiB total recorder-memory budgets still require application-level
measurement; fixed collection bounds alone do not prove those targets.
