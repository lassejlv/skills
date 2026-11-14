> Upstream: [crates/rune/README.md § State machines (`rune::machine`)](https://github.com/anomalyco/rune/blob/65f8eb43f710e078f92cb82039212de50cb03113/crates/rune/README.md#state-machines-runemachine) at `65f8eb43f710`, MIT © Anomaly. Bundled by build-rune-apps; links point at this snapshot or at GitHub at that rev.

### State machines (`rune::machine`)

Anything with modes (a hover delay, a drag, a request and its retries, a dialog flow) is one
`enum State` whose variants carry only what is valid in them, and one transition that returns
what should happen instead of doing it:

```rust
use rune::machine::{Attempt, Effects, Seq};

enum Tip { Idle, Waiting { attempt: Attempt, due: f64 }, Open }
enum Event { Enter { now: f64 }, Leave, Due { attempt: Attempt, now: f64 } }
enum Effect { WakeAt(f64) }

fn step(seq: &mut Seq, tip: &mut Tip, event: Event) -> Effects<Effect> {
    match (&*tip, event) {
        (Tip::Idle, Event::Enter { now }) => {
            let (attempt, due) = (seq.next(), now + 0.4);
            *tip = Tip::Waiting { attempt, due };
            Effects::one(Effect::WakeAt(due))
        }
        (Tip::Waiting { attempt, due }, Event::Due { attempt: a, now }) if *attempt == a && now >= *due => {
            *tip = Tip::Open;
            Effects::none()
        }
        (_, Event::Leave) => { *tip = Tip::Idle; Effects::none() }
        _ => Effects::none(),
    }
}
// A handler steps with `tx.clock()` and carries the effects out:
for e in step(&mut s.seq, &mut s.tip, Event::Enter { now: tx.clock() }) {
    match e { Effect::WakeAt(due) => tx.wake_at(due) }
}
```

- **Illegal states don't exist.** `Waiting` without a deadline, or `Open` with one, can't be
  built, so no code has to clear a flag another forgot.
- **Timers are events.** Deadlines are on `Tx::clock` (the clock `poll` gets, virtual in headless
  runs); `Tx::wake_at(due)` wakes `poll`, which feeds `Due` back into `step`.
- **Attempts fence answers.** `Seq::next` issues an `Attempt` per request, timer or dialog; an
  answer carrying an attempt the state no longer holds falls through to `_` and changes nothing.
- **Effects stay inline.** `Effects<E>` holds up to two effects without allocating; `push` and
  `extend` add more, and it iterates in order.
