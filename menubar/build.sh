#!/bin/sh
# Сборка значка и установка в ~/Applications/BrainBar.app. Если он был запущен — перезапускает.
set -e
cd "$(dirname "$0")"
BRAIN_BUILD_ROOT="$(cd .. && pwd -P)"
BUILD=build/BrainBar.app
APP="$HOME/Applications/BrainBar.app"

rm -rf "$BUILD"
mkdir -p "$BUILD/Contents/MacOS"
cp Info.plist "$BUILD/Contents/Info.plist"
/usr/bin/python3 - "$BUILD/Contents/Info.plist" "$BRAIN_BUILD_ROOT" "${BRAIN_AGENT_LABEL:-}" <<'PY'
import plistlib, sys
path, brain_dir, agent_label = sys.argv[1:]
with open(path, 'rb') as f:
    info = plistlib.load(f)
info['BrainDirectory'] = brain_dir
if agent_label:
    info['BrainAgentLabel'] = agent_label
with open(path, 'wb') as f:
    plistlib.dump(info, f)
PY
xcrun swiftc -O -swift-version 5 -parse-as-library -module-cache-path "$PWD/build/module-cache" \
    -o "$BUILD/Contents/MacOS/BrainBar" BrainBar.swift MenuViews.swift ModelSettings.swift
codesign --force --sign - "$BUILD"
if [ "${1:-}" = "--build-only" ]; then
    echo "собрано: $PWD/$BUILD"
    exit 0
fi

running=0
pgrep -x BrainBar >/dev/null && running=1 && pkill -x BrainBar
mkdir -p "$HOME/Applications"
rm -rf "$APP"
cp -R "$BUILD" "$APP"
echo "установлено: $APP"
[ "$running" = 1 ] && open "$APP" && echo "перезапущен"
exit 0
