> Upstream: [crates/rune/README.md § Depending on Rune](https://github.com/anomalyco/rune/blob/65f8eb43f710e078f92cb82039212de50cb03113/crates/rune/README.md#depending-on-rune) at `65f8eb43f710`, MIT © Anomaly. Bundled by build-rune-apps; links point at this snapshot or at GitHub at that rev.

### Depending on Rune

An app pins a `dev` rev and patches the same four crates Rune does, from the same rev. A
dependency's `[patch]` doesn't reach the workspace that depends on it, and without these the app
builds against stock crates: winit's patch carries macOS input-method and Windows window-creation
fixes, parley_engine's carries bidi and shaping fixes.

```toml
[dependencies]
rune = { git = "https://github.com/anomalyco/rune", rev = "<rev>" }

[patch.crates-io]
winit = { git = "https://github.com/anomalyco/rune", rev = "<rev>" }
parley_engine = { git = "https://github.com/anomalyco/rune", rev = "<rev>" }
wgpu-hal = { git = "https://github.com/anomalyco/rune", rev = "<rev>" }
accesskit_windows = { git = "https://github.com/anomalyco/rune", rev = "<rev>" }
```

The list is the `[patch.crates-io]` table in Rune's root `Cargo.toml`; when a bump adds an entry
there, add it here too.
