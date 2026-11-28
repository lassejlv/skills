# Finding and wiping one app or tool

Use this when the user asks to "find everything from X", "wipe X completely", or "delete all X data".

## 1. Find (read-only)

Run `bash <skill-dir>/scripts/find-app-data.sh <name> [bundle-id-fragment ...]` (the script is in the `scripts/` folder of this skill). Add extra patterns when the app's identifiers differ from its name: the bundle id from `defaults read "/Applications/X.app/Contents/Info" CFBundleIdentifier`, the vendor name, a ToDesktop-style id (`com.todesktop.<hash>`), and joined or CamelCase variants (`MyApp` for "My App").

Then fill the gaps the script cannot see:

- Break down the data folders (`du -hd2`) and list their contents, so you can tell config from cache from user content.
- Check when it was last used: `stat -f %Sa` on the binary, and `grep` the shell history for the command name.
- Look for copies in second package managers (a tool can be installed through both Bun and npm).
- If an external drive holds the source, say so; it only shows up while mounted.

## 2. Report

Group what you found, with sizes, so the user can choose a scope:

1. **The app itself**: the bundle, CLI launchers, package-manager installs.
2. **Its data**: Application Support, config dirs (`~/.config/x`, `~/.x`), caches, HTTPStorages, WebKit, preferences, saved state.
3. **Credentials**: keychain items by name. Call out any that look like an encryption key for user documents.
4. **Other tools' references**: cached info about X in other apps, agent skills, MCP server entries, shell config blocks.
5. **Things that only share the name**: mail attachments, browser site data, icons bundled in other apps, themes in a source repo. Recommend leaving these.

Say what each item is in a few words. State plainly that nothing was changed.

## 3. Scope

The user's words decide the scope. "Delete its data" keeps the app installed; "wipe it completely" removes the app too. "Everything to do with X" still does not automatically cover:

- **Signing keys and document-encryption keys.** Deletion cannot be undone and can lock the user out of their own releases or documents. Name them, explain the consequence, and get a specific yes.
- **Builds of the user's own projects whose source is not on this Mac.** `cargo install --list` shows a source path in parentheses; check it exists, and check for a remote repo.
- **Source repositories**, including on external drives.
- **Anything the user has told you to keep**, in this conversation or in memory. A later broad "delete it all" does not override an earlier specific "keep X".

Do everything else, and list the held items with the reason for each. One question at the end is better than a pause before any work is done.

## 4. Delete

Check the app is not running (`pgrep -f "/Applications/X.app"`). If it is and the user asked for a wipe, quit it gracefully (`osascript -e 'quit app "X"'`); do not kill it.

Order that keeps things consistent:

1. Package managers first: `brew uninstall`, `npm uninstall -g`, `bun remove -g`, `cargo uninstall`, `pipx uninstall`. Then remove whatever they left behind (a Bun `trustedDependencies` entry, a cask's `share/` folder).
2. `defaults delete <domain>` before removing the plist, otherwise `cfprefsd` can write it back.
3. Data, caches, launchers, the app bundle. Move them with `trash -v -s` (macOS 15 and later) so the user can restore a wrong call from Finder; caches can be deleted outright.
4. Keychain: `security delete-generic-password -s "<service>"` in a loop until it fails; one call deletes one item. Use `-a "<account>"` when only the account name identifies it.
5. Shell config: remove only the tool's own marked block (`# >>> x installer >>>` to `# <<< x installer <<<`). Do it with a script that checks the markers appear exactly once, then syntax-check the file (`zsh -n ~/.zshrc`, `bash -n ~/.bashrc`), and restore the original if the check fails. Do not print the surrounding lines: shell configs often hold secrets.
6. Agent skills and their symlinks: remove the symlink only if its target is the skill being removed, and drop the entry from the skills lock file so an update does not reinstall it.
7. Root-owned pieces (LaunchDaemons, `/Library/PrivilegedHelperTools`, `/usr/local/bin`, pkg receipts via `pkgutil --forget`) in one admin prompt.

## 5. Verify

Re-run the name search, the keychain grep and `defaults domains`. Background item records (`sfltool dumpbtm`) stay behind after the app is gone; the user removes them in System Settings > General > Login Items, so name them in the report. Report "removed N, failed M", what was kept on purpose, and anything macOS refused (app containers and Group Containers need Full Disk Access).

Mention side effects the user would not expect: a credential that another app was reading, a skill that other agents shared, an MCP server entry that will now fail to connect.
