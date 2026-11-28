#!/bin/bash
# Read-only footprint search for one app or CLI tool on macOS. Deletes nothing.
# Works with the stock /bin/bash on any Mac (Intel or Apple silicon).
#
# Usage: bash find-app-data.sh <name> [more-names-or-bundle-id-fragments ...]
#   bash find-app-data.sh slack
#   bash find-app-data.sh "visual studio code" vscode com.microsoft.VSCode
# Each argument is matched case-insensitively against file and folder names.
# AI coding agent folders (~/.claude*, ~/.codex) are reported as a count only.

[ "$(uname)" = "Darwin" ] || { echo "This script is for macOS only."; exit 1; }
[ $# -ge 1 ] || { echo "usage: $0 <name> [extra-pattern ...]"; exit 1; }

H="$HOME"
V="$(dirname "$(getconf DARWIN_USER_DIR 2>/dev/null)")"
RE="$(printf '%s|' "$@" | sed 's/|$//')"   # extended regex of all patterns
short() { case "$1" in "$H"*) printf '~%s' "${1#"$H"}";; *) printf '%s' "$1";; esac; }
row() { printf "%7s  %s  %s\n" "$(du -sh "$1" 2>/dev/null | cut -f1)" "$(stat -f %Sm -t %Y-%m-%d "$1" 2>/dev/null)" "$(short "$1")"; }

# -iname "*a*" -o -iname "*b*" ...
args=(); for n in "$@"; do [ ${#args[@]} -gt 0 ] && args+=(-o); args+=(-iname "*$n*"); done

echo "===== COMMANDS ====="
for n in "$@"; do
  which -a "$n" 2>/dev/null | while read -r p; do
    if [ -L "$p" ]; then echo "$p -> $(readlink "$p")"; else echo "$p"; fi
  done
done

echo; echo "===== APPS ====="
{ mdfind "kMDItemContentType == 'com.apple.application-bundle'" 2>/dev/null
  ls -d /Applications/*.app /Applications/*/*.app "$H"/Applications/*.app 2>/dev/null; } | grep -iE "$RE" |
while read -r a; do (cd "$a" 2>/dev/null && pwd -P); done | sort -u |   # resolve symlinked folders, drop duplicates
while read -r a; do
  echo "$(du -sh "$a" 2>/dev/null | cut -f1)  $a  ($(defaults read "$a/Contents/Info" CFBundleIdentifier 2>/dev/null)) v$(defaults read "$a/Contents/Info" CFBundleShortVersionString 2>/dev/null)"
done

echo; echo "===== RUNNING ====="
ps -axo pid,comm | grep -iE "$RE" | grep -v -e grep -e find-app-data | cut -c1-150 | head -8

echo; echo "===== FILES AND FOLDERS BY NAME ====="
find "$H" /Applications /Library /opt/homebrew /usr/local /private/tmp /private/var/tmp "$V" /etc/paths.d -xdev \
  \( "${args[@]}" \) -not -path "$H/.claude*" -not -path "$H/.codex/*" \
  -not -path "*/node_modules/*/node_modules/*" -not -path "*/.git/*" -not -path "*.app/Contents/*" \
  -not -path "/Library/Developer/*" -not -path "*/SDKs/*" -prune 2>/dev/null |
  while read -r p; do row "$p"; done | sort -k3 | head -150

echo; echo "===== AI AGENT FOLDERS (count only) ====="
for c in "$H"/.claude* "$H/.codex"; do
  [ -d "$c" ] && echo "$(short "$c"): $(find "$c" \( "${args[@]}" \) 2>/dev/null | wc -l | tr -d ' ') items"
done

echo; echo "===== PREFERENCE DOMAINS ====="
defaults domains 2>/dev/null | tr ',' '\n' | sed 's/^ //' | grep -iE "$RE"

echo; echo "===== LAUNCH ITEMS ====="
grep -rl -iE "$RE" "$H/Library/LaunchAgents" /Library/LaunchAgents /Library/LaunchDaemons 2>/dev/null
ls /Library/PrivilegedHelperTools 2>/dev/null | grep -iE "$RE"
sfltool dumpbtm 2>/dev/null | grep -E '^ +(Identifier|URL|Bundle Identifier): ' | grep -iE "$RE" |
  sed -E 's/^ +/background item /' | sort -u

echo; echo "===== SHELL CONFIG (values hidden) ====="
grep -n -iE "$RE" "$H/.zshrc" "$H/.zprofile" "$H/.zshenv" "$H/.bashrc" "$H/.bash_profile" "$H/.profile" \
  "$H/.config/fish/config.fish" 2>/dev/null | sed -E 's/=.*/=<hidden>/' | cut -c1-140

echo; echo "===== KEYCHAIN (names only) ====="
security dump-keychain 2>/dev/null | grep -iE "\"(svce|acct|labl)\"<blob>=\"[^\"]*($RE)[^\"]*\"" | sort | uniq -c

echo; echo "===== PACKAGE MANAGERS ====="
if command -v brew >/dev/null 2>&1; then
  brew list --formula 2>/dev/null | grep -iE "$RE" | sed 's/^/brew formula: /'
  brew list --cask 2>/dev/null | grep -iE "$RE" | sed 's/^/brew cask: /'
fi
command -v npm >/dev/null 2>&1 && npm ls -g --depth=0 2>/dev/null | grep -iE "$RE" | sed 's/^/npm -g: /'
[ -f "$H/.bun/install/global/package.json" ] && grep -n -iE "$RE" "$H/.bun/install/global/package.json" | sed 's/^/bun -g: /'
command -v cargo >/dev/null 2>&1 && cargo install --list 2>/dev/null | grep -iE -A2 "$RE" | sed 's/^/cargo: /' | head -12
command -v pipx >/dev/null 2>&1 && pipx list --short 2>/dev/null | grep -iE "$RE" | sed 's/^/pipx: /'
command -v uv >/dev/null 2>&1 && uv tool list 2>/dev/null | grep -iE "$RE" | sed 's/^/uv tool: /'
command -v mas >/dev/null 2>&1 && mas list 2>/dev/null | grep -iE "$RE" | sed 's/^/app store: /'
pkgutil --pkgs 2>/dev/null | grep -iE "$RE" | sed 's/^/pkg receipt: /'

echo; echo "===== SYMLINKS POINTING AT IT ====="
find "$H/.local/bin" "$H/bin" /usr/local/bin /opt/homebrew/bin "$H"/.claude*/skills "$H/.agents/skills" -maxdepth 1 -type l 2>/dev/null |
  while read -r l; do
    t="$(readlink "$l")"
    echo "$l $t" | grep -qiE "$RE" && echo "$(short "$l") -> $t"
  done
exit 0
