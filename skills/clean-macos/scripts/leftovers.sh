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
  case "$p" in
    "") echo "NO PROGRAM  $f";;
    /*) [ -e "$p" ] || echo "MISSING     $f -> $p";;
  esac
done
echo "(a plist with no program can still be valid, e.g. socket-activated or managed by a package: check before removing;"
echo " a bare command name such as 'sh' is looked up on PATH by launchd and is not checked)"

echo; echo "===== BACKGROUND ITEMS WHOSE TARGET IS MISSING (System Settings > General > Login Items) ====="
uid="$(id -u)"
sfltool dumpbtm 2>/dev/null | awk '
  /^ #[0-9]+:/ { if (u != "") print t "\t" i "\t" u; t = i = u = "" }
  /^ +Type: /       { sub(/^ +Type: /, "");       t = $0 }
  /^ +Identifier: / { sub(/^ +Identifier: /, ""); i = $0 }
  /^ +URL: \//      { sub(/^ +URL: /, "");        u = $0 }
  END { if (u != "") print t "\t" i "\t" u }' |
while IFS="$(printf '\t')" read -r t i u; do
  path="$u"; case "$u" in "/Users/$uid/"*) path="$H/${u#"/Users/$uid/"}";; esac
  [ -e "$path" ] || printf "MISSING  %s  %s -> %s\n" "$t" "$i" "$(short "$path")"
done
echo "(these records outlive the app; System Settings > General > Login Items lists them, and 'sfltool resetbtm' clears all of them, so prefer removing the app's own leftovers)"

echo; echo "===== PRIVILEGED HELPERS ====="
ls -la /Library/PrivilegedHelperTools 2>/dev/null | sed -n '2,$p'

echo; echo "===== INSTALLED APPS ====="
# Names a data folder may be keyed by: bundle id, its vendor part (com.brave.Browser -> brave),
# bundle name, executable and file name of every app, plus every running process.
known="$(
  for a in /Applications/*.app /Applications/*/*.app "$H"/Applications/*.app "$H"/Applications/*/*.app; do
    [ -d "$a" ] || continue
    id="$(defaults read "$a/Contents/Info" CFBundleIdentifier 2>/dev/null)"
    echo "$id"; echo "$id" | cut -d. -f2
    defaults read "$a/Contents/Info" CFBundleName 2>/dev/null
    defaults read "$a/Contents/Info" CFBundleExecutable 2>/dev/null
    basename "$a" .app
  done
  ps -axo comm= | sed 's#.*/##'
)"
known="$(echo "$known" | tr '[:upper:]' '[:lower:]' | grep . | sort -u)"
echo "app count: $(ls -d /Applications/*.app /Applications/*/*.app "$H"/Applications/*.app 2>/dev/null | wc -l | tr -d ' ')"
belongs() {
  local n k; n="$(echo "$1" | tr '[:upper:]' '[:lower:]')"
  while read -r k; do
    [ "$n" = "$k" ] && return 0
    [ ${#k} -ge 4 ] && case "$n" in *"$k"*) return 0;; esac
    [ ${#n} -ge 4 ] && case "$k" in *"$n"*) return 0;; esac
  done <<< "$known"
  return 1
}

echo; echo "===== THIRD-PARTY DATA FOLDERS WITH NO MATCHING INSTALLED APP (>5 MB) ====="
echo "(heuristic: CLI tools and helpers have no app bundle, so treat this as a list to check, not a delete list."
echo " RECENT means written in the last 7 days: something still uses it)"
for base in "$H/Library/Application Support" "$H/Library/Caches" "$H/Library/Containers" "$H/Library/HTTPStorages"; do
  for d in "$base"/*; do
    [ -e "$d" ] || continue
    n="$(basename "$d")"
    case "$n" in com.apple.*|Apple*|.*|CloudDocs|AddressBook|CrashReporter|Knowledge|MobileSync|FileProvider|iCloud*|GeoServices|CloudKit) continue;; esac
    belongs "$n" && continue
    kb="$(du -sk "$d" 2>/dev/null | cut -f1)"
    [ "${kb:-0}" -gt 5120 ] || continue
    recent=""; [ -n "$(find "$d" -maxdepth 0 -mtime -7 2>/dev/null)" ] && recent="RECENT"
    printf "%7s  %s  %-6s  %s\n" "$(du -sh "$d" 2>/dev/null | cut -f1)" "$(stat -f %Sm -t %Y-%m-%d "$d")" "$recent" "$(short "$d")"
  done
done | sort -rh | head -40

echo; echo "===== DANGLING SYMLINKS IN BIN FOLDERS ====="
find /usr/local/bin /opt/homebrew/bin "$H/.local/bin" "$H/bin" -maxdepth 1 -type l ! -exec test -e {} \; -print 2>/dev/null | head -30

echo; echo "===== NON-APPLE PACKAGE RECEIPTS ====="
pkgutil --pkgs 2>/dev/null | grep -v '^com\.apple\.' | head -40

echo; echo "===== EXTRA PATH ENTRIES ====="
ls /etc/paths.d 2>/dev/null
exit 0
