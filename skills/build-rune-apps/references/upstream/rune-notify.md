> Upstream: [crates/rune-notify/README.md](https://github.com/anomalyco/rune/blob/65f8eb43f710e078f92cb82039212de50cb03113/crates/rune-notify/README.md) at `65f8eb43f710`, MIT © Anomaly. Bundled by build-rune-apps; links point at this snapshot or at GitHub at that rev.

# rune-notify

System notifications for Rune apps: `UNUserNotificationCenter` on macOS, toast notifications on
Windows. Off those, `available()` is false and every call does nothing. Notifications are silent.

| Call | What it does |
| --- | --- |
| `register(&Identity::new(id, name).icon(path))` | Windows: gives the process its `AppUserModelID` (which also groups its windows on the taskbar) and registers the name and icon its toasts show, under `HKEY_CURRENT_USER\Software\Classes\AppUserModelId\<id>`. Call it first thing in `main`, before a window opens. macOS reads both from the bundle. |
| `adopt(&Identity)` | Windows: the same identity in the process, written nowhere, for an app whose installer registered the `AppUserModelId\<id>` key and the activation scheme: toasts post under that id and open that scheme. A second call with the same id only changes the scheme, so an app can add it once it knows its install. |
| `available()` | Whether the app can post: a bundled app on macOS, a registered one on Windows. |
| `post(&Notification)`, `remove(ids)` | Posts a notification with an id, title, body and string user info, or takes it back out of the system's list. On macOS the first post asks for permission. |
| `on_click(f)` | Calls `f` with the clicked notification's id and user info, from any thread. Install it at launch. On Windows a click reaches the process that posted the toast while it runs. |
| `Identity::activation(scheme)`, `click_from_url(url)` | Windows: toasts open `<scheme>://notification/<id>?<user info>` when clicked, so a toast left in the notification center starts the app after it quit. `register` points the scheme at the running executable for the user. Hand the links the app receives (`rune::App::on_open_url`, with `rune::single_instance` so a click while it runs reaches the running process) to `click_from_url`, which returns the click for the app's own links. |
| `app_focused()`, `bring_to_front()` | Whether one of the app's windows is in front (skip notifying then), and bringing the frontmost window forward and focusing it, restoring it if minimized, for a click. |

```rust
fn main() {
    let _ = rune_notify::register(&rune_notify::Identity::new("com.example.app", "Example").icon(icon_png));
    rune_notify::on_click(|click| open(click.get("session")));
    // Later, while the window isn't focused:
    rune_notify::post(&rune_notify::Notification::new("n-1", "Response ready").body("Fix the build").info("session", "ses_1"));
}
```

`rune_mac::notify` re-exports this crate.
