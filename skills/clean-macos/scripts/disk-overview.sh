#!/bin/bash
# Read-only disk usage overview for a macOS cleanup dry run.
# Deletes nothing. Works with the stock /bin/bash on any Mac (Intel or Apple silicon).
# Usage: bash disk-overview.sh

[ "$(uname)" = "Darwin" ] || { echo "This script is for macOS only."; exit 1; }

H="$HOME"
V="$(dirname "$(getconf DARWIN_USER_DIR 2>/dev/null)")"   # per-user /var/folders/xx/yyyy
DATA="/System/Volumes/Data"; [ -d "$DATA" ] || DATA="/"   # pre-Catalina systems have one volume
top() { du -hd1 "$1" 2>/dev/null | sort -rh | head -"${2:-15}"; }
size() { for p in "$@"; do [ -e "$p" ] && du -sh "$p" 2>/dev/null; done; }

echo "===== DISK ====="
sw_vers 2>/dev/null | tr '\n' ' '; echo "| $(uname -m)"
df -h "$DATA" | tail -1
echo "local snapshots: $(tmutil listlocalsnapshots / 2>/dev/null | grep -c 'com.apple')"

echo; echo "===== FULL DISK ACCESS ====="
if ls "$H/.Trash" >/dev/null 2>&1 && ls "$H/Library/Safari" >/dev/null 2>&1; then
  echo "active: Trash, Mail, Messages, Safari etc. are readable"
else
  echo "NOT active: Trash, Mail, Messages, Safari, browser profiles and more are invisible to this scan"
fi

echo; echo "===== HOME (top level) ====="; top "$H" 30
echo; echo "===== ~/Library ====="; top "$H/Library" 15
echo; echo "===== ~/Library/Caches ====="; top "$H/Library/Caches" 20
echo; echo "===== ~/Library/Application Support ====="; top "$H/Library/Application Support" 20
echo; echo "===== ~/Library/Containers + Group Containers ====="
top "$H/Library/Containers" 8; top "$H/Library/Group Containers" 8

echo; echo "===== DEVELOPER CACHES AND TOOLCHAINS ====="
size "$H/.Trash" "$H/Downloads" \
  "$H/Library/Developer/Xcode/DerivedData" "$H/Library/Developer/Xcode/Archives" \
  "$H/Library/Developer/Xcode/iOS DeviceSupport" "$H/Library/Developer/CoreSimulator" \
  "$H/Library/Application Support/MobileSync/Backup" \
  "$H/.npm" "$H/.pnpm-store" "$H/Library/pnpm" "$H/.bun" "$H/.yarn" "$H/Library/Caches/Yarn" \
  "$H/.cache" "$H/.local/share" "$H/.cargo" "$H/.rustup" "$H/go" "$H/Library/Caches/go-build" \
  "$H/.gradle" "$H/.m2" "$H/.cocoapods" "$H/.android" "$H/Library/Android" \
  "$H/.nvm" "$H/.pyenv" "$H/.conda" "$H/miniconda3" "$H/anaconda3" "$H/Library/Caches/pip" \
  "$H/.cache/uv" "$H/.cache/huggingface" "$H/.ollama" "$H/.lmstudio" \
  "$H/.docker" "$H/Library/Containers/com.docker.docker" "$H/.orbstack" "$H/.colima" "$H/.lima" \
  "$H/Library/Caches/Homebrew" "$H/Library/Caches/ms-playwright" "$H/Library/Logs"
echo "-- ~/.cache"; top "$H/.cache" 10
echo "-- ~/.local/share"; top "$H/.local/share" 10
if command -v brew >/dev/null 2>&1; then
  echo "-- Homebrew"; du -sh "$(brew --prefix)" 2>/dev/null; top "$(brew --prefix)/Cellar" 12
fi
command -v docker >/dev/null 2>&1 && { echo "-- Docker"; docker system df 2>/dev/null; }
command -v xcrun >/dev/null 2>&1 && { echo "-- Simulator runtimes"; xcrun simctl runtime list 2>/dev/null | tail -4; }

echo; echo "===== TEMP AND PER-USER SYSTEM CACHE ====="
[ -d "$V" ] && { top "$V/T" 12; top "$V/C" 8; size "$V/X"; }
size /private/tmp /private/var/tmp

echo; echo "===== OUTSIDE HOME ====="
top /Applications 20
size /Library /opt /usr/local /private/var/db/diagnostics /private/var/db/uuidtext /private/var/vm \
     /Library/Caches /Library/Logs /Library/Developer /System/Library/AssetsV2
top /System/Library/AssetsV2 8
echo "(root-only stores such as /System/Library/Caches/com.apple.coresymbolicationd need an admin du)"

echo; echo "===== VERY LARGE FILES (>500 MB) ====="
find "$H" /Applications /opt /usr/local -xdev -type f -size +500M 2>/dev/null | head -40 | while read -r f; do
  printf "%6s  %s\n" "$(du -h "$f" 2>/dev/null | cut -f1)" "$f"
done | sort -rh

echo; echo "===== INSTALLERS LEFT IN HOME ====="
find "$H/Downloads" "$H/Desktop" "$H/Documents" -maxdepth 3 \( -name '*.dmg' -o -name '*.pkg' -o -name '*.iso' \) -size +10M 2>/dev/null |
  while read -r f; do printf "%6s  %s\n" "$(du -h "$f" | cut -f1)" "$f"; done
