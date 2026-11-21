# Where space hides on a Mac

A catalog of locations, how to clear each one, and how risky it is. Sizes are what was typical on a developer machine; always measure.

## Contents
- Regenerable caches (safe tier)
- Developer tools and their own cleanup commands
- System-level caches (need admin)
- Needs the user's call
- Leave alone
- Why `du` and `df` disagree

## Regenerable caches (safe tier)

| Location | Notes |
|---|---|
| `~/Library/Caches/<app>` | Per-app caches. Skip the ones of running apps, or tell the user to quit first. |
| `/var/folders/xx/yyyy/T` (`getconf DARWIN_USER_TEMP_DIR`) | Temp files. Look for abandoned `cargo-install*`, `jest_*`, `metro-*`, `node-compile-cache`, `xfs-*` (Yarn), build dirs. Delete named stale entries, not the whole folder. |
| `/var/folders/xx/yyyy/C` | Per-user system cache, keyed by bundle id. Leftovers of dev and test builds pile up here. |
| `/var/folders/xx/yyyy/X/*.code_sign_clone` | Chromium-browser code-sign clones (1 GB+). Only when the browser is quit. |
| `~/Library/Caches/*-updater`, `ShipIt` folders | Downloaded app updates; often for apps no longer installed. |
| `~/Library/Logs`, `/Library/Logs` | Logs and crash reports. The second needs admin. |
| `~/Downloads/*.dmg`, `*.pkg` | Installers for apps that are already installed. |
| `~/Library/Caches/ms-playwright` | Check `.links/` first: each file names a project that uses the browsers. Remove only builds whose project is gone. |
| Electron/Chromium app profiles: `Cache`, `Code Cache`, `GPUCache`, `Service Worker/CacheStorage` | Inside `~/Library/Application Support/<App>/`. Cache folders only; never the whole profile without asking. |
| Safari: `~/Library/Containers/com.apple.Safari/Data/Library/Caches/com.apple.Safari/WebKitCache` | Needs Full Disk Access. `WebKit/` next to it is website data (logins), not cache. |
| Stale simulator temp: `/private/var/tmp/com.apple.CoreSimulator.SimDevice.<UUID>` | Keep the ones whose UUID is in `xcrun simctl list devices`. |

## Developer tools and their own cleanup commands

Use the tool's command where one exists: it keeps the tool's bookkeeping consistent, which a bare `rm -rf` does not.

| Tool | Where | Cleanup |
|---|---|---|
| Homebrew | `$(brew --prefix)`, `~/Library/Caches/Homebrew` | `brew cleanup -n --prune=all` then without `-n`; `brew autoremove -n`; `brew uninstall`. Check `brew uses --installed <f>` before removing a formula. A cask uninstall can leave its folder under `share/`. |
| Rust | `~/.cargo`, `~/.rustup`, project `target/` | `cargo uninstall <crate>` (see `cargo install --list`; a path in parentheses means it was built from the user's own source), `rustup toolchain uninstall`, `cargo cache -a` if installed. Build-cache wrappers have their own `gc`. |
| Node | `~/.npm`, `~/.pnpm-store`, `~/.bun`, `~/.yarn`, version managers under `~/.nvm`, `~/.local/share/*` | `npm cache clean --force`, `pnpm store prune`, `bun pm cache rm`, `npm uninstall -g`, `bun remove -g`. Version managers usually have a `clean`/`prune` command; check `--help`. |
| Python | `~/Library/Caches/pip`, `~/.cache/uv`, `~/.pyenv`, python.org framework in `/Library/Frameworks/Python.framework` | `pip cache purge`, `uv cache clean`. Before removing a Python, grep `pyvenv.cfg` files for it and check `which -a python3`. |
| Xcode | `~/Library/Developer/Xcode/DerivedData`, `Archives`, `iOS DeviceSupport`, `~/Library/Developer/CoreSimulator` | DerivedData is safe. `xcrun simctl delete unavailable`. Runtimes: `xcrun simctl runtime list` / `delete`. Archives may be the only copy of a shipped build: ask. |
| Docker / OrbStack / Podman | `~/Library/Containers/com.docker.docker`, `~/.orbstack`, `~/.local/share/containers` | `docker system df`, `docker system prune` (ask: it removes images and volumes). |
| Go | `~/go/pkg/mod`, `~/Library/Caches/go-build` | `go clean -cache -modcache`. |
| Gradle / Android | `~/.gradle/caches`, `~/.android/avd`, SDK folder | Caches are safe; AVDs and SDK platforms need a call. |
| AI models | `~/.ollama`, `~/.lmstudio`, `~/.cache/huggingface` | Large and re-downloadable, but ask: downloads are slow. |
| AI agent CLIs and desktop apps | `~/.cache/*-runtimes`, `~/.local/share/<agent>/versions`, VM images under `~/Library/Application Support/<App>/vm_bundles` | Old versions and VM images re-download. Session history and config are user data: see "Leave alone". |

## System-level caches (need admin)

Run these through one `osascript ... with administrator privileges` call (see SKILL.md).

| Location | Notes |
|---|---|
| `/System/Library/Caches/com.apple.coresymbolicationd` | Symbol cache; grows to 10 GB+ on dev machines. `killall coresymbolicationd`, then empty the folder. Rebuilds itself. |
| `/Library/Caches/com.apple.iconservices.store` | Icon cache, about 1 GB. Remove and `killall iconservicesd iconservicesagent`. Do not kill Finder or the Dock unasked. |
| `/private/var/db/diagnostics`, `/private/var/db/uuidtext` | Unified logs. `log erase --all`; it keeps what is still in use. |
| `/Library/Logs` | `find /Library/Logs -type f -delete`. |
| `/private/var/root`, `/.fseventsd`, `/.Spotlight-V100` | Root-only; measure with an admin `du`. Leave them alone. |

## Needs the user's call

- Spotlight document-processing store: `~/Library/Metadata/CoreSpotlight/DocumentProcessing/PipelineStorage`. A journal backlog can reach several GB. The journal files are **hard-linked into every pipeline stage folder**, so deleting one stage frees nothing; stop `spotlightknowledged.*`, clear each stage's `Journals/*/` contents, and confirm with `df`. It may grow back.
- `/System/Library/AssetsV2`: simulator runtimes, offline developer docs, Apple Intelligence models. SIP-protected (`restricted` flag): even root cannot delete. Remove through the owning app (Xcode settings, `xcrun simctl runtime delete`).
- Old toolchains and runtimes that a project may pin. Check whether they were used recently before proposing them.
- Global CLI binaries. Ask per group, and say which ones were built from the user's own source.
- Messages attachments, Mail, Photos: personal data. Report size only.
- Browser profiles. Report size; clear only the cache folders, and only if the user wants it.

## Leave alone

- `/private/var/vm` (swap, sleep image), `/System`, anything SIP-protected.
- AI coding agent data (`~/.claude*`, `~/.codex`, and similar): session history, memory, config. Report size if asked, propose nothing unless the user raises it.
- Keychains, `~/.ssh`, signing keys, anything that looks like the only copy of a credential.
- Source repositories and their working trees.

## Why `du` and `df` disagree

`df` reports blocks used on the volume; `du` only sums what it is allowed to read. A gap of tens of GB is normal and comes from:

- Folders blocked by macOS privacy (TCC) without Full Disk Access.
- Root-only and SIP-protected stores (system Spotlight index, AssetsV2 model folders).
- Local snapshots: `tmutil listlocalsnapshots /`, `diskutil apfs listSnapshots <data volume>`.
- Space not yet released: files deleted while a process still has them open, and hard-linked files with remaining links.

Report the gap honestly rather than guessing what fills it.
