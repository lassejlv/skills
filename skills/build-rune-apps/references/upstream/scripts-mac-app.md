> Upstream: [scripts/mac-app.md](https://github.com/anomalyco/rune/blob/65f8eb43f710e078f92cb82039212de50cb03113/scripts/mac-app.md) at `65f8eb43f710`, MIT © Anomaly. Bundled by build-rune-apps; links point at this snapshot or at GitHub at that rev.

# Installing a Rune app

`scripts/mac-app --name Demo --id com.example.demo --exe demo --bin target/release/demo`
stages and signs a bundle beside its destination, asks the running app to quit,
atomically exchanges the bundles, then launches the replacement. `--icon`,
`--scheme`, `--mic`, `--wait-idle SECONDS`, `MAC_APP_SIGN`, and arguments after `--`
work as before. Launches are normal, not occluded: an occluded first frame can
prevent Rune from reaching readiness.

Use `--bundle path/to/Demo.app` instead of `--bin` to install an already signed
bundle. `--only-relaunch` updates a closed app without opening it. When no explicit
app arguments are supplied, running instances' exact arguments are preserved.
`--stamp PATH --revision REV` publishes a revision stamp under the install lock
only after success. These options also serve remote updaters; transfer each bundle
to its own directory and invoke this installer on the destination machine.

The replacement must write its Rune ready receipt within 15 seconds. Each launch
gets a unique `RUNE_READY_DIR`; the receipt must identify its PID and bundle ID.
`--no-rune-ready` is only for binaries built before Rune's readiness protocol.
Failed launch or readiness restores the previous bundle with another atomic
exchange and reopens it. If the failed app refuses Cocoa quit, the installed
bundle is still restored, but no overlapping copy is opened. Desktop apps are
never force-quit.

## Shared install protocol

Rune and HiveMind land use the same protocol:

1. Resolve the target path, then take an exclusive POSIX `flock` on the persistent
   sibling `.<bundle filename>.install.lock`. Never unlink the lock file.
2. Hold the lock through staging, idle/busy waits, process capture, swap, readiness,
   rollback and cleanup. A caller delegating to this installer must not hold the
   same lock in its parent process.
3. Stage in a unique sibling `.<bundle filename>.install-*` directory. Existing
   bundles are exchanged using `renamex_np(RENAME_SWAP)` on macOS. There is no
   remove-then-rename fallback. First installs use a single rename.
4. The staging path now contains the previous bundle. Delete it only after the
   replacement is ready or rollback has restored the previous bundle.

An uncatchable interruption leaves a complete bundle at the live path and the
other complete bundle at the unique staging path. Recovery failures retain that
path and report it. Never sweep these retained backups as part of another install.
The lock is released by the kernel when its owner exits.

During rollout, let installers using the old protocol finish before admitting
new installs. An already-running old installer cannot be made to honor a new lock.

Regression tests use fake bundles only:

```sh
python3 scripts/mac_app_install_tests.py
```
