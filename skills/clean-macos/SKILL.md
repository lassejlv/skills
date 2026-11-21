---
name: clean-macos
description: Deep-clean a Mac safely, dry run first. Scans the whole disk, sorts findings into safe-to-clear, needs-your-call and uninstalled-app leftovers, verifies each item is really unused before deleting, and reports exactly what was freed. Also finds and wipes every trace of a single app or CLI tool (files, caches, preferences, keychain items, launch agents, shell config, package-manager installs). Use this whenever the user wants to clean up, free space on, declutter or audit storage on a Mac, asks why the disk is full or what is taking space, wants caches, logs, build artifacts or old toolchains removed, asks to "find all data from X", "wipe X completely" or "uninstall X and everything it left behind", or needs Full Disk Access or an admin prompt to finish a cleanup, even if they never say "deep clean".
---

# Clean macOS

Free disk space on a Mac without deleting anything the user still needs. The work is mostly investigation: a cleanup that removes 50 GB of caches is worth little if it also removes one signing key or the only build of a project.

## The shape of the job

1. **Scan, read-only.** Never delete in the first round, even if the user sounds impatient. They cannot approve what they have not seen.
2. **Report in tiers** and let the user pick.
3. **Verify, then delete** only the batch that was approved.
4. **Measure and report** what was actually freed, what was held back, and what could not be done.

Approval covers the batch it was given for. "Clean the safe items" does not extend to the next tier, and a new finding inside an approved batch (it turns out to be in use, or irreplaceable) is a reason to hold that one item and say why.

Every Mac is different. Nothing here assumes a particular user, toolset or folder layout: discover what is installed, measure it, and let the sizes and the evidence decide. If the machine is not a Mac (`uname` is not `Darwin`), say so and stop; the locations and commands below do not apply.

## 1. Scan

Run the bundled scripts; they only read. They sit in the `scripts/` folder next to this file, so call them by that folder's full path:

```bash
bash <skill-dir>/scripts/disk-overview.sh     # sizes: home, Library, caches, dev tools, temp, system
bash <skill-dir>/scripts/leftovers.sh         # dead launch items, orphaned data, dangling links, receipts
```

The scripts run on the stock `/bin/bash` of any Mac (Intel or Apple silicon) and use only tools that ship with macOS. Sections for tools that are not installed simply come back empty.

Then drill into whatever is large with `du -hd2 <dir> | sort -rh | head`. Follow the size, not a checklist: the biggest wins are usually one or two things nobody would guess (a build cache, a VM image, a system symbol cache). `references/locations.md` lists where space hides, how to clear each place, and what to leave alone; read it before writing the report.

Note `df -h /System/Volumes/Data` at the start. It is the only honest measure of progress.

If the scan prints "Operation not permitted" for Trash, Mail, Messages or Safari, the terminal lacks Full Disk Access. Say how much is unaccounted for and offer to set it up (see below) rather than guessing.

## 2. Report

Lead with the totals, then tables. Use these tiers:

- **Safe to clear**: regenerates on demand (caches, temp files, logs, stale downloads). Say what the cost is, for example "next builds will be cold".
- **Your call**: re-downloadable but someone may want it (old toolchains, VM images, session history, large apps, global binaries).
- **Leftovers from uninstalled apps**: dead background services, orphaned installs, data without an app.
- **Other findings**: private keys or tokens sitting in Downloads, pending OS updates, space you could not measure.

Give a size and a few words of explanation per row. End by asking which groups to clean. Do not present personal data (Mail, Messages, Photos) or the user's AI agent history as cleanup candidates; report their size only if asked.

Check earlier turns, and any persistent memory or project instructions you have, for standing rules ("never touch X") before listing anything.

## 3. Verify before deleting

Sizes come from the scan; safety comes from this step. For each item in the approved batch, look at it first:

- **Is it running or open?** `pgrep -f`, `lsof +D <dir>`. Do not quit the user's apps to clear a cache; skip the item and tell them. (macOS `pgrep` has no `-E`; use `ps -axo pid,comm | grep -iE`.)
- **Is it really unused?** Access time (`stat -f %Sa`) is reliable on APFS, with one trap: a `brew upgrade` reads every dependent binary, so an access time equal to the last brew run proves nothing. Compare it with the install time (`stat -f %SB`) and with shell history (`grep -c` on `~/.zsh_history`, `~/.bash_history` or the fish history file).
- **Does anything depend on it?** `brew uses --installed`, symlinks pointing at it, project logs from the last few days, toolchain pins. A toolchain used in a build today will simply be downloaded again.
- **Can it be recreated?** A registry package can; a binary built from the user's own source may not be, if the source is gone. `cargo install --list` shows the source path.
- **Whose is it?** A folder written to today belongs to something, even if no installed app matches its name.

When the evidence says "in use" or "irreplaceable", keep it and report why. That is the job working, not a failure to follow instructions. Earlier claims you made in the report are not evidence; if verification contradicts them, say so.

## 4. Delete

Prefer the owning tool's cleanup command over `rm` (`brew uninstall`, `cargo uninstall`, a cache tool's `gc`, a version manager's `clean`); it keeps that tool's records consistent. `references/locations.md` has the command per tool. Preview with the tool's dry-run flag when it has one.

Shell practicalities that otherwise waste turns:

- Run multi-step deletions as a `bash <<'EOF' ... EOF` script with `shopt -s nullglob`. In zsh an unmatched glob aborts the whole command.
- Print one line per path ("removed" or "FAILED") and a final count, and re-check existence after `rm`; `rm -rf` reports success on things macOS silently protects.
- Guard computed paths before using them (`case "$T" in /var/folders/*/T) ;; *) exit 1;; esac`).
- Record `df` before and after each batch.

**Admin rights.** `sudo` cannot prompt inside an agent session. Write the root steps to a script in a temporary folder and run it once:

```bash
osascript -e 'with timeout of 600 seconds' \
  -e 'do shell script "/bin/bash /path/to/root-steps.sh 2>&1" with administrator privileges' \
  -e 'end timeout'
```

This shows the macOS password dialog. Batch all root work into one prompt, and tell the user a dialog is coming. Root does not override System Integrity Protection: paths flagged `restricted` in `ls -lO` (such as `/System/Library/AssetsV2`) cannot be deleted this way, so do not spend a prompt trying.

**Full Disk Access.** The permission belongs to the app that launched the shell, which may be a background helper rather than the visible terminal. Walk the parent chain (`ps -o ppid=,comm= -p <pid>` repeatedly) to find it, then:

```bash
open "x-apple.systempreferences:com.apple.preference.security?Privacy_AllFiles"
open -R "/path/to/That.app"
```

Tell the user to drag the app into the list and restart the terminal. Test with `ls ~/.Trash`. An admin `du` through `osascript` still cannot read privacy-protected folders, so expect some space to stay unexplained.

**When the number does not move.** If `df` barely changes after a large delete, the space is still referenced: a process holds the files open, or they are hard-linked elsewhere (`stat -f %l` shows the link count). Find the other links before reporting the space as freed.

## 5. Report the result

State the space freed from `df`, not from summing sizes. List what was removed, what was held back and why, and what could not be done (protected by macOS, needs a quit, needs admin). Mention consequences the user will notice: cold builds, a re-login, a tool that will re-download a runtime, icons that redraw.

Caches regrow, so a later `df` can be lower than the peak; say that when the user asks for a total. Suggest a restart at the end, once, so system caches rebuild cleanly.

## Wiping one app or tool

For "find everything from X" or "wipe X", read `references/app-wipe.md`. The short version: run `bash <skill-dir>/scripts/find-app-data.sh <name> [bundle-id ...]`, report what was found grouped by what it is, match the scope to the user's words ("its data" keeps the app), then delete, and verify with a second search.

## Things to protect

These deserve a specific confirmation even after a broad "delete it all", because they cannot be recovered and the user may not realise what they are:

- Signing keys, update-signing keys, and keychain items that encrypt user documents.
- Private keys and tokens. When you find them loose (in Downloads, in shell config), suggest moving them, do not print their contents, and redact values in any output you show.
- Source repositories, including on external drives, and builds of the user's own projects with no source on the machine.
- Anything the user has explicitly said to keep.

Do the rest of the batch first, then ask about these in one message with the consequence of each.
