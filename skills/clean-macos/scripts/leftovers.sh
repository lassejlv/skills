#!/bin/bash
# Read-only check for leftovers of uninstalled software on macOS. Deletes nothing.
# Works with the stock /bin/bash on any Mac (Intel or Apple silicon).
# Usage: bash leftovers.sh

[ "$(uname)" = "Darwin" ] || { echo "This script is for macOS only."; exit 1; }

H="$HOME"
short() { case "$1" in "$H"*) printf '~%s' "${1#"$H"}";; *) printf '%s' "$1";; esac; }

echo "===== LAUNCH ITEMS WHOSE PROGRAM IS MISSING ====="
for f in "$H"/Library/LaunchAgents/*.plist /Library/LaunchAgents/*.plist /Library/LaunchDaemons/*.plist; do
  [ -f "$f" ] || continue
  p="$(plutil -extract ProgramArguments.0 raw "$f" 2>/dev/null || plutil -extract Program raw "$f" 2>/dev/null)"
  if [ -z "$p" ]; then echo "NO PROGRAM  $f"
  elif [ ! -e "$p" ]; then echo "MISSING     $f -> $p"
  fi
done
echo "(a plist with no program can still be valid, e.g. socket-activated or managed by a package: check before removing)"

echo; echo "===== PRIVILEGED HELPERS ====="
ls -la /Library/PrivilegedHelperTools 2>/dev/null | sed -n '2,$p'

echo; echo "===== INSTALLED APP BUNDLE IDS ====="
ids="$(for a in /Applications/*.app /Applications/*/*.app "$H"/Applications/*.app; do
  [ -d "$a" ] && defaults read "$a/Contents/Info" CFBundleIdentifier 2>/dev/null
done | sort -u)"
apps="$(ls /Applications "$H/Applications" 2>/dev/null)"
echo "count: $(echo "$ids" | grep -c .)"

echo; echo "===== THIRD-PARTY DATA FOLDERS WITH NO MATCHING INSTALLED APP (>5 MB) ====="
echo "(heuristic: CLI tools and helpers have no app bundle, so treat this as a list to check, not a delete list)"
for base in "$H/Library/Application Support" "$H/Library/Caches" "$H/Library/Containers" "$H/Library/HTTPStorages"; do
  for d in "$base"/*; do
    [ -e "$d" ] || continue
    n="$(basename "$d")"
    case "$n" in com.apple.*|Apple*|.*|CloudDocs|AddressBook|CrashReporter|Knowledge|MobileSync|FileProvider|iCloud*) continue;; esac
    echo "$ids" | grep -qiF "$n" && continue
    echo "$apps" | grep -qiF "$n" && continue
    kb="$(du -sk "$d" 2>/dev/null | cut -f1)"
    [ "${kb:-0}" -gt 5120 ] && printf "%7s  %s  %s\n" "$(du -sh "$d" 2>/dev/null | cut -f1)" "$(stat -f %Sm -t %Y-%m-%d "$d")" "$(short "$d")"
  done
done | sort -rh | head -40

echo; echo "===== DANGLING SYMLINKS IN BIN FOLDERS ====="
find /usr/local/bin /opt/homebrew/bin "$H/.local/bin" "$H/bin" -maxdepth 1 -type l ! -exec test -e {} \; -print 2>/dev/null | head -30

echo; echo "===== NON-APPLE PACKAGE RECEIPTS ====="
pkgutil --pkgs 2>/dev/null | grep -v '^com\.apple\.' | head -40

echo; echo "===== EXTRA PATH ENTRIES ====="
ls /etc/paths.d 2>/dev/null
exit 0
